"""
app/services/password_service.py
---------------------------------
Password lifecycle: forgot-password, reset-password, change-password.

Flow:
  1. User calls POST /auth/forgot-password with email or mobile.
  2. We create a PasswordReset row with a hashed one-time token and send
     the raw token to the user via email/SMS (notification layer — Slice 10).
  3. User calls POST /auth/reset-password with the raw token + new password.
  4. We look up the hash, validate it, and update the user's password_hash.
  5. The PasswordReset row is marked used_at = now (single-use enforcement).
  6. All active sessions for the user are revoked (force re-login everywhere).

Security rules:
  - Token stored as SHA-256 hash — never in plain text (rules.md §4).
  - Token expires in 15 minutes (configurable).
  - Token is single-use: used_at is set on first successful reset.
  - All sessions revoked after password reset (security best practice).
"""

from __future__ import annotations

import hashlib
import secrets
import uuid
from datetime import UTC, datetime, timedelta

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundError, ValidationError
from app.core.logging import get_logger
from app.core.security import hash_password, verify_password
from app.models.user import PasswordReset, User, UserStatus
from app.services import auth_service

logger = get_logger(__name__)

_RESET_TOKEN_EXPIRE_MINUTES = 15
_RAW_TOKEN_BYTES = 32   # 256-bit entropy


def _generate_reset_token() -> tuple[str, str]:
    """Return (raw_token, sha256_hex_hash)."""
    raw = secrets.token_urlsafe(_RAW_TOKEN_BYTES)
    token_hash = hashlib.sha256(raw.encode()).hexdigest()
    return raw, token_hash


async def initiate_password_reset(
    db: AsyncSession, identifier: str
) -> str:
    """
    Create a PasswordReset record for the user identified by email or mobile.

    Returns the raw token (caller must deliver this to the user via
    email/SMS — NOT stored in the DB).

    If no user is found, we deliberately return without error to prevent
    user enumeration (same response as success).
    """
    stmt = select(User).where(
        (User.email == identifier) | (User.mobile == identifier),
        User.deleted_at.is_(None),
        User.status == UserStatus.ACTIVE,
    )
    result = await db.execute(stmt)
    user: User | None = result.scalar_one_or_none()

    if user is None:
        logger.info("Password reset: user not found (silent)", identifier=identifier[:4] + "***")
        # Return a fake token so timing is consistent (prevent enumeration)
        return secrets.token_urlsafe(_RAW_TOKEN_BYTES)

    # Invalidate any existing unused resets
    existing_stmt = select(PasswordReset).where(
        PasswordReset.user_id == user.id,
        PasswordReset.used_at.is_(None),
    )
    existing = (await db.execute(existing_stmt)).scalars().all()
    for old in existing:
        old.used_at = datetime.now(UTC)   # mark old tokens as used

    raw_token, token_hash = _generate_reset_token()
    reset = PasswordReset(
        user_id=user.id,
        token_hash=token_hash,
        expires_at=datetime.now(UTC) + timedelta(minutes=_RESET_TOKEN_EXPIRE_MINUTES),
    )
    db.add(reset)

    logger.info("Password reset token created", user_id=str(user.id))
    # ASSUMPTION: Notification delivery (email/SMS) is handled by Slice 10.
    # For now, the raw token is returned to the caller for testing purposes.
    return raw_token


async def complete_password_reset(
    db: AsyncSession, raw_token: str, new_password: str
) -> None:
    """
    Verify the raw token, update password, mark token as used, and
    revoke all sessions (forces re-login on all devices).

    Raises:
      ValidationError — token not found, expired, or already used.
    """
    token_hash = hashlib.sha256(raw_token.encode()).hexdigest()

    stmt = select(PasswordReset).where(PasswordReset.token_hash == token_hash)
    result = await db.execute(stmt)
    reset: PasswordReset | None = result.scalar_one_or_none()

    if reset is None or not reset.is_valid:
        raise ValidationError(
            "Reset token is invalid, expired, or already used",
            code="INVALID_RESET_TOKEN",
        )

    # Load the user
    user_result = await db.execute(select(User).where(User.id == reset.user_id))
    user: User | None = user_result.scalar_one_or_none()
    if user is None:
        raise ValidationError("Associated user account not found", code="USER_NOT_FOUND")

    # Update password
    user.password_hash = hash_password(new_password)
    reset.used_at = datetime.now(UTC)

    # Revoke all sessions (force re-login everywhere)
    await auth_service.logout_all(db, user.id)

    logger.info("Password reset complete — all sessions revoked", user_id=str(user.id))


async def change_password(
    db: AsyncSession,
    user: User,
    current_password: str,
    new_password: str,
) -> None:
    """
    Authenticated password change (user knows their current password).

    Raises:
      ValidationError — current password is wrong.
    """
    valid, _ = verify_password(current_password, user.password_hash)
    if not valid:
        raise ValidationError("Current password is incorrect", code="WRONG_CURRENT_PASSWORD")

    if current_password == new_password:
        raise ValidationError(
            "New password must differ from current password", code="SAME_PASSWORD"
        )

    user.password_hash = hash_password(new_password)
    logger.info("Password changed", user_id=str(user.id))
