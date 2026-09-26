"""
app/services/auth_service.py
-----------------------------
Authentication business logic.

Responsibilities:
  - authenticate_user()   — verify credentials (email/mobile + password)
  - issue_tokens()        — create access + refresh tokens, write UserSession
  - refresh_session()     — rotate refresh token with reuse detection
  - logout()              — revoke a single session by JTI
  - logout_all()          — revoke all active sessions for a user
  - update_last_login()   — stamp last_login_at after successful login

Security rules (rules.md §4, architecture.md §7):
  - Identity is always derived from verified JWT — never trusted from client.
  - Refresh token reuse detection: if a revoked JTI is presented again,
    ALL sessions for that user are immediately revoked (stolen token signal).
  - Failed login attempts are tracked; account is locked after 5 consecutive failures.
  - Passwords are verified with pwdlib verify_and_update() which transparently
    rehashes if the stored hash is outdated.
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime, timedelta
from typing import TYPE_CHECKING

from fastapi import Request
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.exceptions import (
    AccountInactiveError,
    InvalidCredentialsError,
    TokenRevokedError,
    UnauthorizedError,
)
from app.core.logging import get_logger
from app.core.client_ip import get_client_ip
from app.core.security import (
    burn_password_check,
    create_access_token,
    create_refresh_token,
    decode_token,
    verify_password,
)
from app.models.user import PasswordReset, User, UserSession, UserStatus
from app.schemas.auth import TokenResponse
from app.schemas.user import UserRead

if TYPE_CHECKING:
    pass

logger = get_logger(__name__)
_MAX_FAILED_ATTEMPTS = 5
_LOCK_DURATION_MINUTES = 30


async def authenticate_user(
    db: AsyncSession,
    identifier: str,       # email or mobile
    plain_password: str,
) -> User:
    """
    Locate user by email or mobile and verify password.

    Raises:
      InvalidCredentialsError  — wrong credentials (deliberately vague message)
      AccountInactiveError     — account is disabled or suspended
    """
    # Try email first, then mobile
    stmt = select(User).where(
        (User.email == identifier) | (User.mobile == identifier),
        User.deleted_at.is_(None),
    )
    result = await db.execute(stmt)
    user: User | None = result.scalar_one_or_none()

    if user is None:
        # Spend the same hashing time as a real check so timing doesn't reveal
        # whether the account exists.
        burn_password_check(plain_password)
        logger.warning("Login attempt: user not found", identifier_truncated=identifier[:4] + "***")
        raise InvalidCredentialsError("Invalid credentials")

    now = datetime.now(UTC)
    if user.locked_until and now < user.locked_until:
        raise AccountInactiveError(
            "Account temporarily locked due to too many failed login attempts. "
            "Try again later.",
            code="ACCOUNT_LOCKED",
        )
    if user.locked_until and now >= user.locked_until:
        # Lock has expired: start a fresh window instead of re-locking on the next typo.
        user.failed_login_attempts = 0
        user.locked_until = None

    # Verify the password BEFORE revealing anything about the account's status,
    # otherwise "Account is suspended" confirms an account exists to anyone.
    valid, updated_hash = verify_password(plain_password, user.password_hash)
    if not valid:
        await _record_failed_attempt(db, user)
        raise InvalidCredentialsError("Invalid credentials")

    if user.status not in (UserStatus.ACTIVE, UserStatus.PENDING):
        raise AccountInactiveError(f"Account is {user.status.value.lower()}")

    # Transparent rehash — update hash if Argon2 parameters changed
    if updated_hash:
        user.password_hash = updated_hash

    # Reset failed attempts on success
    if user.failed_login_attempts > 0:
        user.failed_login_attempts = 0
        user.locked_until = None

    return user


async def issue_tokens(
    db: AsyncSession,
    user: User,
    request: Request | None = None,
) -> tuple[str, str, TokenResponse]:
    """
    Create access + refresh tokens and write a UserSession row.

    Returns:
      (access_token, refresh_token, TokenResponse)

    The caller (router) sets the refresh token as an httpOnly cookie.
    """
    s = get_settings()
    access_token, access_jti, access_exp = create_access_token(
        user_id=str(user.id), role=user.role
    )
    refresh_jti = str(uuid.uuid4())
    refresh_token, _, refresh_exp = create_refresh_token(
        user_id=str(user.id), role=user.role, jti=refresh_jti
    )

    # Build device/IP metadata
    ip: str | None = None
    ua: str | None = None
    if request:
        ip = get_client_ip(request)
        ua = request.headers.get("User-Agent")

    session = UserSession(
        user_id=user.id,
        refresh_token_jti=refresh_jti,
        device_info=ua,
        ip_address=ip,
        expires_at=refresh_exp,
    )
    db.add(session)

    await _update_last_login(db, user)

    expires_in = int(timedelta(minutes=s.ACCESS_TOKEN_EXPIRE_MINUTES).total_seconds())
    response = TokenResponse(
        access_token=access_token,
        expires_in=expires_in,
        user=UserRead.model_validate(user),
    )
    logger.info("Tokens issued", user_id=str(user.id), role=user.role)
    return access_token, refresh_token, response


async def refresh_session(
    db: AsyncSession,
    refresh_token: str,
    request: Request | None = None,
) -> tuple[str, str, TokenResponse]:
    """
    Validate the refresh token and rotate it.

    Rotation: old JTI is revoked, new access + refresh tokens are issued.
    Reuse detection: if the presented JTI was already revoked, revoke ALL
    sessions for the user immediately (indicates a stolen/replayed token).

    Raises:
      UnauthorizedError  — invalid / malformed token
      TokenRevokedError  — token already revoked
    """
    payload = decode_token(refresh_token, expected_type="refresh")
    jti: str = payload["jti"]
    user_id: str = payload["sub"]

    # Look up the session row
    stmt = select(UserSession).where(UserSession.refresh_token_jti == jti)
    result = await db.execute(stmt)
    session: UserSession | None = result.scalar_one_or_none()

    if session is None:
        raise UnauthorizedError("Refresh token not recognised")

    if session.is_revoked:
        # Reuse of a revoked token → revoke all sessions (theft signal)
        logger.warning(
            "Refresh token reuse detected — revoking all sessions",
            user_id=user_id, jti=jti,
        )
        await _revoke_all_sessions(db, uuid.UUID(user_id))
        raise TokenRevokedError("Refresh token already used. All sessions revoked for security.")

    if session.is_expired:
        raise TokenRevokedError("Refresh token has expired")

    # Revoke this session
    session.revoked_at = datetime.now(UTC)

    # Fetch the user
    user_result = await db.execute(
        select(User).where(User.id == uuid.UUID(user_id), User.deleted_at.is_(None))
    )
    user: User | None = user_result.scalar_one_or_none()
    if user is None or not user.is_active:
        raise UnauthorizedError("User not found or inactive")

    # Issue new tokens
    return await issue_tokens(db, user, request)


async def logout(db: AsyncSession, refresh_token: str) -> None:
    """Revoke a single session by the refresh token JTI."""
    try:
        payload = decode_token(refresh_token, expected_type="refresh")
        jti = payload.get("jti")
    except Exception:
        # Token may be expired but logout should still succeed
        return

    if jti:
        stmt = (
            update(UserSession)
            .where(
                UserSession.refresh_token_jti == jti,
                UserSession.revoked_at.is_(None),
            )
            .values(revoked_at=datetime.now(UTC))
        )
        await db.execute(stmt)
        logger.info("Session revoked (logout)", jti=jti)


async def logout_all(db: AsyncSession, user_id: uuid.UUID) -> int:
    """
    Revoke all active sessions for a user.
    Returns the number of sessions revoked.
    """
    count = await _revoke_all_sessions(db, user_id)
    logger.info("All sessions revoked (logout-all)", user_id=str(user_id), count=count)
    return count


# ─── Private helpers ─────────────────────────────────────────────────────────

async def _update_last_login(db: AsyncSession, user: User) -> None:
    user.last_login_at = datetime.now(UTC)


async def _record_failed_attempt(db: AsyncSession, user: User) -> None:
    user.failed_login_attempts += 1
    if user.failed_login_attempts >= _MAX_FAILED_ATTEMPTS:
        user.locked_until = datetime.now(UTC) + timedelta(minutes=_LOCK_DURATION_MINUTES)
        logger.warning(
            "Account locked due to failed login attempts",
            user_id=str(user.id),
            attempts=user.failed_login_attempts,
        )
    # The caller raises InvalidCredentialsError right after this, and get_db() rolls the
    # session back on any exception — without an explicit commit the counter was never
    # persisted and the lockout could not trigger.
    await db.commit()


async def _revoke_all_sessions(db: AsyncSession, user_id: uuid.UUID) -> int:
    now = datetime.now(UTC)
    stmt = (
        update(UserSession)
        .where(
            UserSession.user_id == user_id,
            UserSession.revoked_at.is_(None),
        )
        .values(revoked_at=now)
        .returning(UserSession.id)
    )
    result = await db.execute(stmt)
    return len(result.fetchall())
