"""
app/api/v1/analytics/batches.py
-------------------------------
Batch detailed performance metrics endpoint.
"""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import CurrentUser, get_db, require_role
from app.schemas.analytics import BatchAnalyticsResponse
from app.schemas.common import StandardResponse
from app.services import analytics_service

router = APIRouter()


@router.get(
    "/batches/{batch_id}",
    response_model=StandardResponse[BatchAnalyticsResponse],
    summary="Get detailed performance and attendance metrics for a batch",
    dependencies=[require_role("SUPER_ADMIN", "ADMIN", "TEACHER")],
)
async def get_batch_analytics(
    batch_id: uuid.UUID,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    data = await analytics_service.get_batch_analytics(
        db=db,
        institute_id=current_user.institute_id,
        batch_id=batch_id,
        current_user=current_user,
    )
    return StandardResponse(data=data)
