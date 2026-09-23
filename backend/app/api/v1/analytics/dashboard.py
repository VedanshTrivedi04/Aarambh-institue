"""
app/api/v1/analytics/dashboard.py
---------------------------------
Executive KPI dashboard and materialized view refresh trigger.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import CurrentUser, get_db, require_role
from app.core.cache import cache_service
from app.core.rate_limit import rate_limit
from app.schemas.analytics import DashboardKPIsResponse, MaterializedViewRefreshResponse
from app.schemas.common import StandardResponse
from app.services import analytics_service

router = APIRouter()


@router.get(
    "/dashboard",
    response_model=StandardResponse[DashboardKPIsResponse],
    summary="Executive KPI dashboard summary",
    dependencies=[require_role("SUPER_ADMIN", "ADMIN", "COUNSELLOR", "RECEPTIONIST")],
)
async def get_executive_dashboard(
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    cache_key = cache_service.build_key(current_user.institute_id, "analytics", "dashboard")
    cached_data = await cache_service.get(cache_key)
    if cached_data is not None:
        return StandardResponse(data=DashboardKPIsResponse.model_validate(cached_data))

    data = await analytics_service.get_executive_dashboard(
        db=db,
        institute_id=current_user.institute_id,
    )
    await cache_service.set(cache_key, data.model_dump(mode="json"), ttl_seconds=60)
    return StandardResponse(data=data)


@router.post(
    "/refresh",
    response_model=StandardResponse[MaterializedViewRefreshResponse],
    status_code=status.HTTP_200_OK,
    summary="Trigger PostgreSQL Materialized View refresh",
    dependencies=[
        require_role("SUPER_ADMIN", "ADMIN"),
        rate_limit(requests_per_minute=20, tier="tenant"),
    ],
)
async def refresh_views(
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    res = await analytics_service.refresh_materialized_views(
        db=db,
        institute_id=current_user.institute_id,
    )
    await cache_service.invalidate_tenant_namespace(current_user.institute_id, "analytics")
    return StandardResponse(data=res, message="Materialized views refreshed.")
