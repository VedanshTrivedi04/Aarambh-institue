"""
app/schemas/auth.py
-------------------
Pydantic v2 schemas for the authentication API surface.

Rules (rules.md §4):
  - Tokens are NEVER logged (logging.py sensitive-key redaction).
  - The refresh token is delivered in an httpOnly cookie by the router,
    not in this response body — this keeps it off mobile/JS storage.
  - LoginRequest accepts either email or mobile as the identifier.
"""

from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, Field, model_validator

from app.schemas.user import UserRead


class LoginRequest(BaseModel):
    """
    Accepts email OR mobile as identifier — whichever the user registered with.
    """

    identifier: str = Field(
        ...,
        description="Email address or mobile number",
        examples=["admin@aarambh.in", "9876543210"],
    )
    password: str = Field(..., min_length=1)


class TokenResponse(BaseModel):
    """
    Returned from /login and /refresh.

    access_token — short-lived; stored in memory or a short-lived cookie.
    token_type   — always "bearer".
    expires_in   — seconds until access token expires (for client-side countdown).
    user         — current user snapshot (avoids an extra /me call after login).

    NOTE: The refresh token is set as an httpOnly cookie by the router
    (Set-Cookie header) and is NOT included here, preventing JS access.
    """

    access_token: str
    token_type: str = "bearer"
    expires_in: int          # seconds
    user: UserRead


class RefreshRequest(BaseModel):
    """
    Used when the client sends the refresh token in the request body
    instead of (or in addition to) the httpOnly cookie.
    The router prefers the httpOnly cookie; this is a fallback for
    environments (e.g. native mobile) where cookies are inconvenient.
    """

    refresh_token: str | None = None


class ForgotPasswordRequest(BaseModel):
    identifier: str = Field(..., description="Email or mobile number of the account")


class ResetPasswordRequest(BaseModel):
    token: str = Field(..., description="Reset token received via email/SMS")
    new_password: str = Field(..., min_length=8, max_length=128)


class LogoutAllRequest(BaseModel):
    """Optional — caller can request logout from all devices."""
    confirm: bool = Field(default=False, description="Must be true to proceed")
