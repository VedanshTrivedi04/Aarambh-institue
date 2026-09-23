"""
app/api/v1/analytics/student_360.py
-----------------------------------
Student 360° Comprehensive Profile endpoints with ReBAC verification.
"""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import CurrentUser, get_db, require_role
from app.core.exceptions import NotFoundError
from app.models.people import StudentProfile
from app.schemas.analytics import Student360ProfileResponse
from app.schemas.common import StandardResponse
from app.services import analytics_service

router = APIRouter()


@router.get(
    "/students/{student_id}/360",
    response_model=StandardResponse[Student360ProfileResponse],
    summary="Fetch comprehensive 360° profile of a student (ReBAC protected)",
    dependencies=[require_role("SUPER_ADMIN", "ADMIN", "TEACHER", "COUNSELLOR", "STUDENT", "PARENT")],
)
async def get_student_360(
    student_id: uuid.UUID,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    data = await analytics_service.get_student_360_profile(
        db=db,
        institute_id=current_user.institute_id,
        student_id=student_id,
        current_user=current_user,
    )
    return StandardResponse(data=data)


@router.get(
    "/my-360",
    response_model=StandardResponse[Student360ProfileResponse],
    summary="Convenience endpoint for student to view their own 360° profile",
    dependencies=[require_role("STUDENT")],
)
async def get_my_360(
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    s_stmt = select(StudentProfile.id).where(StudentProfile.user_id == current_user.id)
    student_id = (await db.execute(s_stmt)).scalar_one_or_none()
    if not student_id:
        raise NotFoundError("Student profile not found for current user.")

    data = await analytics_service.get_student_360_profile(
        db=db,
        institute_id=current_user.institute_id,
        student_id=student_id,
        current_user=current_user,
    )
    return StandardResponse(data=data)
