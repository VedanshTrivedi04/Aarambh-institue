"""
app/api/deps.py
---------------
Shared FastAPI dependencies used across all portals and routers.

Provides:
  get_db()            — yields an async DB session (see db/session.py)
  get_current_user()  — decodes JWT, loads User row, enforces is_active
  require_role()      — RBAC route guard (role-level check)

Architecture note (backend.md §3, §5):
  - require_role() is a *route-level* guard only.
  - Services MUST additionally verify resource ownership at the query level
    (ReBAC) — e.g. a teacher can only see their own batches.
  - NEVER rely solely on route guards for data isolation.
"""

from __future__ import annotations

from typing import Annotated
from uuid import UUID

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import AccountInactiveError, ForbiddenError, UnauthorizedError
from app.core.security import decode_token
from app.db.session import get_db

# Import User model lazily to avoid circular imports at module load time.
# The actual model is defined in Slice 2; this deps file is ready for it.

bearer_scheme = HTTPBearer(auto_error=False)

# ---------------------------------------------------------------------------
# DB session dependency — re-exported here for convenient import in routers.
# ---------------------------------------------------------------------------
DbDep = Annotated[AsyncSession, Depends(get_db)]


# ---------------------------------------------------------------------------
# Current user dependency
# ---------------------------------------------------------------------------

async def get_current_user(
    db: DbDep,
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
) -> "User":  # type: ignore[name-defined]  # noqa: F821
    """
    Decode the Bearer JWT and return the authenticated User ORM row.

    Raises:
      UnauthorizedError  — no token / invalid / expired
      AccountInactiveError — user is disabled
    """
    if credentials is None:
        raise UnauthorizedError("Authentication required")

    payload = decode_token(credentials.credentials, expected_type="access")
    user_id: str | None = payload.get("sub")
    if not user_id:
        raise UnauthorizedError("Invalid token payload")

    # Inline import to break circular dependency until Slice 2 creates User model.
    try:
        from app.models.user import User  # noqa: PLC0415
    except ImportError:
        raise UnauthorizedError("User model not yet available")

    result = await db.execute(select(User).where(User.id == UUID(user_id)))
    user: User | None = result.scalar_one_or_none()

    if user is None:
        raise UnauthorizedError("User not found")
    if not user.is_active:
        raise AccountInactiveError("Account is inactive or suspended")

    return user


CurrentUser = Annotated["User", Depends(get_current_user)]  # type: ignore[name-defined]


# ---------------------------------------------------------------------------
# RBAC route guard factory
# ---------------------------------------------------------------------------

def require_role(*allowed_roles: str):
    """
    FastAPI dependency factory for role-based access control.

    Usage:
        @router.get("/admin/students", dependencies=[Depends(require_role("ADMIN"))])

    Or in the function signature:
        async def endpoint(user: CurrentUser = Depends(require_role("ADMIN", "TEACHER"))):

    IMPORTANT: This is a *route-level* check only. Services must additionally
    verify resource ownership (ReBAC) at the query level (backend.md §5).
    """
    async def _guard(current_user: CurrentUser) -> "User":  # type: ignore[name-defined]
        if current_user.role not in allowed_roles:
            raise ForbiddenError(
                f"Access denied: requires one of {allowed_roles}",
                code="FORBIDDEN",
                user_role=current_user.role,
            )
        return current_user

    return Depends(_guard)


# ---------------------------------------------------------------------------
# Tenant context dependency (Slice 2 will populate this fully)
# ---------------------------------------------------------------------------

async def get_tenant_context(current_user: CurrentUser) -> dict:
    """
    Returns the institute_id and branch_id from the current user's profile.
    Used by services to scope all queries within the user's tenant boundary.
    """
    return {
        "institute_id": getattr(current_user, "institute_id", None),
        "branch_id": getattr(current_user, "branch_id", None),
    }

TenantContext = Annotated[dict, Depends(get_tenant_context)]
