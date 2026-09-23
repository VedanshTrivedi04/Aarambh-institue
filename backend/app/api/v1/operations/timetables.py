"""
app/api/v1/operations/timetables.py
-----------------------------------
Timetable management and concrete session generation.

Endpoints:
  POST /timetables                    — Create weekly timetable rule
  GET  /timetables/batch/{batch_id}   — List timetable rules for a batch
  POST /timetables/generate-sessions  — Populate concrete ClassSessions from timetable rules
"""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import CurrentUser, get_db, require_role
from app.schemas.academic_operations import (
    ClassSessionRead,
    SessionGenerateRequest,
    TimetableCreate,
    TimetableRead,
)
from app.schemas.common import StandardResponse
from app.services.academic_operations_service import AcademicOperationsService

_ADMIN_ROLES = ("SUPER_ADMIN", "ADMIN", "MANAGEMENT")

router = APIRouter(
    prefix="/timetables",
    tags=["Operations - Timetables"],
)


@router.post(
    "",
    response_model=StandardResponse[TimetableRead],
    status_code=status.HTTP_201_CREATED,
    dependencies=[require_role(*_ADMIN_ROLES)],
    summary="Create a weekly recurring timetable slot",
)
async def create_timetable(
    body: TimetableCreate,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    timetable = await AcademicOperationsService.create_timetable(
        db, body, current_user.institute_id
    )
    await db.commit()
    return StandardResponse(
        data=TimetableRead.model_validate(timetable),
        message="Timetable rule created successfully",
    )


@router.get(
    "/batch/{batch_id}",
    response_model=list[TimetableRead],
    summary="List active timetable rules for a batch",
)
async def list_batch_timetables(
    batch_id: uuid.UUID,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    timetables = await AcademicOperationsService.list_batch_timetables(
        db, batch_id, current_user.institute_id
    )
    return [TimetableRead.model_validate(t) for t in timetables]


@router.post(
    "/generate-sessions",
    response_model=StandardResponse[list[ClassSessionRead]],
    status_code=status.HTTP_201_CREATED,
    dependencies=[require_role(*_ADMIN_ROLES)],
    summary="Generate calendar sessions between date range from timetable rules",
)
async def generate_sessions(
    body: SessionGenerateRequest,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    sessions = await AcademicOperationsService.generate_sessions_from_timetable(
        db,
        batch_id=body.batch_id,
        start_date=body.start_date,
        end_date=body.end_date,
        institute_id=current_user.institute_id,
    )
    await db.commit()
    return StandardResponse(
        data=[ClassSessionRead.model_validate(s) for s in sessions],
        message=f"Generated {len(sessions)} class sessions successfully",
    )
