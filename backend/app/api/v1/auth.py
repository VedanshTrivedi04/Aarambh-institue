"""
app/api/v1/auth.py
------------------
Authentication endpoints.

POST  /api/v1/auth/login           — issue access + refresh tokens
POST  /api/v1/auth/refresh         — rotate refresh token
POST  /api/v1/auth/logout          — revoke current session
POST  /api/v1/auth/logout-all      — revoke all sessions (all devices)
GET   /api/v1/auth/me              — return current user profile
POST  /api/v1/auth/forgot-password — initiate password reset
POST  /api/v1/auth/reset-password  — complete password reset
POST  /api/v1/auth/change-password — change password (authenticated)

Security conventions (rules.md §4):
  - Refresh token travels ONLY in an httpOnly cookie (not in the body).
  - Access token is returned in the response body for the client to hold
    in memory (not localStorage).
  - /login, /refresh, /forgot-password are the endpoints that need
    rate limiting (Slice 12 will add this via middleware/Redis).
"""

from __future__ import annotations

from fastapi import APIRouter, Cookie, Depends, Request, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import CurrentUser, get_db
from app.core.config import get_settings
from app.core.exceptions import UnauthorizedError
from app.core.rate_limit import rate_limit
from app.schemas.auth import (
    ForgotPasswordRequest,
    LoginRequest,
    LogoutAllRequest,
    ResetPasswordRequest,
    TokenResponse,
)
from app.schemas.common import MessageResponse
from app.schemas.user import ChangePasswordRequest, UserRead
from app.services import auth_service, password_service

router = APIRouter(tags=["Auth"])
_REFRESH_COOKIE = "refresh_token"


def _set_refresh_cookie(response: Response, token: str) -> None:
    """Write the refresh token to an httpOnly, Secure, SameSite=Lax cookie."""
    s = get_settings()
    max_age = s.REFRESH_TOKEN_EXPIRE_DAYS * 86400
    response.set_cookie(
        key=_REFRESH_COOKIE,
        value=token,
        httponly=True,
        secure=s.APP_ENV != "dev",   # Secure flag off only in local dev (no HTTPS)
        samesite="lax",
        max_age=max_age,
        path="/api/v1/auth",         # Scoped — cookie not sent to other routes
    )


def _clear_refresh_cookie(response: Response) -> None:
    response.delete_cookie(key=_REFRESH_COOKIE, path="/api/v1/auth")


# ---------------------------------------------------------------------------
# POST /login
# ---------------------------------------------------------------------------

@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Login with email or mobile + password",
    status_code=status.HTTP_200_OK,
    dependencies=[rate_limit(requests_per_minute=10, tier="ip")],
)
async def login(
    body: LoginRequest,
    request: Request,
    response: Response,
    db: AsyncSession = Depends(get_db),
) -> TokenResponse:
    user = await auth_service.authenticate_user(db, body.identifier, body.password)
    access_token, refresh_token, token_response = await auth_service.issue_tokens(
        db, user, request
    )
    await db.commit()
    _set_refresh_cookie(response, refresh_token)
    return token_response


# ---------------------------------------------------------------------------
# POST /refresh
# ---------------------------------------------------------------------------

@router.post(
    "/refresh",
    response_model=TokenResponse,
    summary="Rotate refresh token and issue new access token",
    dependencies=[rate_limit(requests_per_minute=20, tier="ip")],
)
async def refresh(
    request: Request,
    response: Response,
    db: AsyncSession = Depends(get_db),
    # Prefer httpOnly cookie; fall back to body token (for native clients)
    cookie_token: str | None = Cookie(default=None, alias=_REFRESH_COOKIE),
) -> TokenResponse:
    token = cookie_token
    if not token:
        # Try extracting from JSON body (native mobile fallback). Malformed or
        # non-object bodies must yield a 401, not a 500.
        try:
            body = await request.json() if "application/json" in request.headers.get("content-type", "") else {}
        except ValueError:
            body = {}
        token = body.get("refresh_token") if isinstance(body, dict) else None

    if not token:
        raise UnauthorizedError("No refresh token provided")

    access_token, new_refresh_token, token_response = await auth_service.refresh_session(
        db, token, request
    )
    await db.commit()
    _set_refresh_cookie(response, new_refresh_token)
    return token_response


# ---------------------------------------------------------------------------
# POST /logout
# ---------------------------------------------------------------------------

@router.post(
    "/logout",
    response_model=MessageResponse,
    summary="Revoke the current session (logout)",
)
async def logout(
    response: Response,
    db: AsyncSession = Depends(get_db),
    cookie_token: str | None = Cookie(default=None, alias=_REFRESH_COOKIE),
) -> MessageResponse:
    if cookie_token:
        await auth_service.logout(db, cookie_token)
        await db.commit()
    _clear_refresh_cookie(response)
    return MessageResponse(message="Logged out successfully")


# ---------------------------------------------------------------------------
# POST /logout-all
# ---------------------------------------------------------------------------

@router.post(
    "/logout-all",
    response_model=MessageResponse,
    summary="Revoke all active sessions (logout from all devices)",
)
async def logout_all(
    body: LogoutAllRequest,
    response: Response,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
) -> MessageResponse:
    if not body.confirm:
        from app.core.exceptions import ValidationError
        raise ValidationError("confirm must be true", code="CONFIRMATION_REQUIRED")
    count = await auth_service.logout_all(db, current_user.id)
    await db.commit()
    _clear_refresh_cookie(response)
    return MessageResponse(message=f"Logged out from {count} device(s)")


# ---------------------------------------------------------------------------
# GET /me
# ---------------------------------------------------------------------------

@router.get(
    "/me",
    response_model=UserRead,
    summary="Return the current authenticated user's profile",
)
async def me(current_user: CurrentUser) -> UserRead:
    return UserRead.model_validate(current_user)


# ---------------------------------------------------------------------------
# POST /forgot-password
# ---------------------------------------------------------------------------

@router.post(
    "/forgot-password",
    response_model=MessageResponse,
    summary="Request a password reset link/token",
    dependencies=[rate_limit(requests_per_minute=5, tier="ip")],
)
async def forgot_password(
    body: ForgotPasswordRequest,
    db: AsyncSession = Depends(get_db),
) -> MessageResponse:
    # Returns the same message regardless of whether user exists (anti-enumeration)
    await password_service.initiate_password_reset(db, body.identifier)
    await db.commit()
    return MessageResponse(
        message="If an account with that identifier exists, a reset link has been sent."
    )


# ---------------------------------------------------------------------------
# POST /reset-password
# ---------------------------------------------------------------------------

@router.post(
    "/reset-password",
    response_model=MessageResponse,
    summary="Complete password reset using the received token",
)
async def reset_password(
    body: ResetPasswordRequest,
    db: AsyncSession = Depends(get_db),
) -> MessageResponse:
    await password_service.complete_password_reset(db, body.token, body.new_password)
    await db.commit()
    return MessageResponse(message="Password reset successfully. Please log in again.")


# ---------------------------------------------------------------------------
# POST /change-password
# ---------------------------------------------------------------------------

@router.post(
    "/change-password",
    response_model=MessageResponse,
    summary="Change password (authenticated — requires current password)",
)
async def change_password(
    body: ChangePasswordRequest,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
) -> MessageResponse:
    await password_service.change_password(
        db, current_user, body.current_password, body.new_password
    )
    await db.commit()
    return MessageResponse(message="Password changed successfully.")
