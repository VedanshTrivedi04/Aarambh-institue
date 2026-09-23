"""
app/api/v1/analytics/export.py
------------------------------
Data streaming and CSV export endpoint.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, Query, Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import CurrentUser, get_db, require_role
from app.schemas.analytics import ExportType
from app.services import analytics_service

router = APIRouter()


@router.get(
    "/export",
    summary="Export data as CSV for rosters, financial ledger, attendance, or exam results",
    dependencies=[require_role("SUPER_ADMIN", "ADMIN", "COUNSELLOR")],
)
async def export_data(
    current_user: CurrentUser,
    export_type: ExportType = Query(..., description="Type of dataset to export"),
    db: AsyncSession = Depends(get_db),
):
    csv_content, filename = await analytics_service.export_data_csv(
        db=db,
        institute_id=current_user.institute_id,
        export_type=export_type,
    )
    return Response(
        content=csv_content,
        media_type="text/csv",
        headers={
            "Content-Disposition": f"attachment; filename=\"{filename}\"",
            "Cache-Control": "no-cache",
        },
    )
