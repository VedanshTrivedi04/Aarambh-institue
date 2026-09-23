"""
app/api/v1/operations/attendance.py
-----------------------------------
Daily Attendance Engine endpoints.

Endpoints:
  POST /attendance/sessions/{session_id}/mark   — Bulk mark attendance with ReBAC authority check
  GET  /attendance/sessions/{session_id}/sheet  — Get full batch roster with marked statuses
  GET  /attendance/students/{student_id}/stats  — Compute student attendance percentage & breakdown
"""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import CurrentUser, get_db, require_role
from app.schemas.academic_operations import (
    AttendanceBulkMarkRequest,
    SessionAttendanceSheetItem,
    StudentAttendanceSummary,
)
from app.schemas.common import StandardResponse
from app.services.academic_operations_service import AcademicOperationsService

_TEACHER_OR_ADMIN = ("SUPER_ADMIN", "ADMIN", "MANAGEMENT", "TEACHER")

router = APIRouter(
    prefix="/attendance",
    tags=["Operations - Attendance"],
)


@router.post(
    "/sessions/{session_id}/mark",
    response_model=StandardResponse[dict[str, int]],
    status_code=status.HTTP_200_OK,
    dependencies=[require_role(*_TEACHER_OR_ADMIN)],
    summary="Bulk mark or update attendance for a class session",
)
async def bulk_mark_attendance(
    session_id: uuid.UUID,
    body: AttendanceBulkMarkRequest,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    count = await AcademicOperationsService.bulk_mark_attendance(
        db=db,
        session_id=session_id,
        records=body.records,
        current_user=current_user,
    )
    await db.commit()
    return StandardResponse(
        data={"marked_count": count},
        message=f"Attendance recorded for {count} students",
    )


@router.get(
    "/sessions/{session_id}/sheet",
    response_model=list[SessionAttendanceSheetItem],
    dependencies=[require_role(*_TEACHER_OR_ADMIN)],
    summary="Get full attendance roster for a session",
)
async def get_session_attendance_sheet(
    session_id: uuid.UUID,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    sheet = await AcademicOperationsService.get_session_attendance_sheet(
        db=db,
        session_id=session_id,
        institute_id=current_user.institute_id,
    )
    return sheet


@router.get(
    "/students/{student_id}/stats",
    response_model=StandardResponse[StudentAttendanceSummary],
    summary="Compute student attendance percentage and session breakdown",
)
async def get_student_attendance_stats(
    student_id: uuid.UUID,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
    batch_id: uuid.UUID | None = Query(None, description="Filter stats by specific batch"),
):
    summary = await AcademicOperationsService.get_student_attendance_summary(
        db=db,
        student_id=student_id,
        batch_id=batch_id,
        institute_id=current_user.institute_id,
    )
    return StandardResponse(data=summary)
