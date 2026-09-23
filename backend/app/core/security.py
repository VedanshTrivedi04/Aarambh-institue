"""
app/core/security.py
--------------------
Password hashing (pwdlib / Argon2) and JWT token utilities.

Uses pwdlib with Argon2 as recommended by the FastAPI security docs:
  https://fastapi.tiangolo.com/tutorial/security/oauth2-jwt/

Rules (rules.md §4):
- Password hash strings are NEVER logged or returned in API responses.
- JWT payload is minimal: sub (user UUID), role, jti (token ID), type (access|refresh).
- Access tokens: short-lived (30 min default).
- Refresh tokens: longer-lived (7 days default), stored as a session row.
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime, timedelta
from typing import Literal

import jwt
from pwdlib import PasswordHash

from app.core.config import get_settings
from app.core.exceptions import TokenExpiredError, UnauthorizedError

# ---------------------------------------------------------------------------
# Password hashing
# ---------------------------------------------------------------------------

# PasswordHash.recommended() uses Argon2 under the hood.
# It also supports verify_and_update() for transparent algorithm upgrades.
_pwd_hash = PasswordHash.recommended()


def hash_password(plain: str) -> str:
    """Return an Argon2 hash of the plain-text password."""
    return _pwd_hash.hash(plain)


def verify_password(plain: str, hashed: str) -> tuple[bool, str | None]:
    """
    Verify a plain password against a stored hash.

    Returns:
        (is_valid, updated_hash_or_None)
        If updated_hash is not None, persist the new hash (transparent rehash).
    """
    valid, updated = _pwd_hash.verify_and_update(plain, hashed)
    return valid, updated


# ---------------------------------------------------------------------------
# JWT
# ---------------------------------------------------------------------------

TokenType = Literal["access", "refresh"]


def _settings():
    return get_settings()


def create_token(
    user_id: str,
    role: str,
    token_type: TokenType,
    jti: str | None = None,
) -> tuple[str, str, datetime]:
    """
    Create a signed JWT.

    Returns:
        (encoded_token, jti, expires_at)

    The JTI (JWT ID) uniquely identifies this token instance and is stored
    in the UserSession row so we can revoke it on logout.
    """
    s = _settings()
    now = datetime.now(UTC)

    if jti is None:
        jti = str(uuid.uuid4())

    if token_type == "access":
        expires_delta = timedelta(minutes=s.ACCESS_TOKEN_EXPIRE_MINUTES)
    else:
        expires_delta = timedelta(days=s.REFRESH_TOKEN_EXPIRE_DAYS)

    expires_at = now + expires_delta

    payload = {
        "sub": user_id,          # subject: user UUID as string
        "role": role,            # role slug (e.g. "ADMIN", "TEACHER")
        "type": token_type,
        "jti": jti,
        "iat": now,
        "exp": expires_at,
    }

    encoded = jwt.encode(payload, s.SECRET_KEY, algorithm=s.ALGORITHM)
    return encoded, jti, expires_at


def create_access_token(user_id: str, role: str) -> tuple[str, str, datetime]:
    return create_token(user_id, role, "access")


def create_refresh_token(user_id: str, role: str, jti: str | None = None) -> tuple[str, str, datetime]:
    return create_token(user_id, role, "refresh", jti=jti)


def decode_token(token: str, expected_type: TokenType = "access") -> dict:
    """
    Decode and validate a JWT.

    Raises:
        TokenExpiredError — if the token is past its expiry.
        UnauthorizedError — if the token is malformed or signature is invalid.
    """
    s = _settings()
    try:
        payload = jwt.decode(token, s.SECRET_KEY, algorithms=[s.ALGORITHM])
    except jwt.ExpiredSignatureError:
        raise TokenExpiredError("Token has expired")
    except jwt.PyJWTError:
        raise UnauthorizedError("Invalid token")

    if payload.get("type") != expected_type:
        raise UnauthorizedError(f"Expected {expected_type} token")

    return payload
