"""
app/api/v1/analytics/finance.py
-------------------------------
Financial analytics and payment method distribution endpoint.
"""

from __future__ import annotations

from datetime import date as Date

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import CurrentUser, get_db, require_role
from app.schemas.analytics import FinancialAnalyticsResponse
from app.schemas.common import StandardResponse
from app.services import analytics_service

router = APIRouter()


@router.get(
    "/finance",
    response_model=StandardResponse[FinancialAnalyticsResponse],
    summary="Financial collections, overdue schedule, and method breakdown",
    dependencies=[require_role("SUPER_ADMIN", "ADMIN", "COUNSELLOR")],
)
async def get_financial_analytics(
    current_user: CurrentUser,
    start_date: Date | None = Query(None, description="Filter payments from date"),
    end_date: Date | None = Query(None, description="Filter payments to date"),
    db: AsyncSession = Depends(get_db),
):
    data = await analytics_service.get_financial_analytics(
        db=db,
        institute_id=current_user.institute_id,
        start_date=start_date,
        end_date=end_date,
    )
    return StandardResponse(data=data)
