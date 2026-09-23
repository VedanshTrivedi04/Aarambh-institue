"""
app/api/v1/analytics/attendance.py
----------------------------------
Attendance status analytics and low attendance alert endpoints.
"""

from __future__ import annotations

import uuid
from datetime import date as Date

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import CurrentUser, get_db, require_role
from app.schemas.analytics import AttendanceAnalyticsResponse
from app.schemas.common import StandardResponse
from app.services import analytics_service

router = APIRouter()


@router.get(
    "/attendance",
    response_model=StandardResponse[AttendanceAnalyticsResponse],
    summary="Attendance breakdown and low-attendance alerts (< 75%)",
    dependencies=[require_role("SUPER_ADMIN", "ADMIN", "TEACHER", "COUNSELLOR")],
)
async def get_attendance_analytics(
    current_user: CurrentUser,
    batch_id: uuid.UUID | None = Query(None, description="Filter by batch ID"),
    start_date: Date | None = Query(None, description="Start date"),
    end_date: Date | None = Query(None, description="End date"),
    db: AsyncSession = Depends(get_db),
):
    data = await analytics_service.get_attendance_analytics(
        db=db,
        institute_id=current_user.institute_id,
        batch_id=batch_id,
        start_date=start_date,
        end_date=end_date,
    )
    return StandardResponse(data=data)
