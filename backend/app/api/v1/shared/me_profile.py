"""
app/api/v1/shared/me_profile.py
-------------------------------
Self-view profile endpoints for authenticated users.

Architecture rules:
  - User identity (User) is separate from domain profiles.
  - Endpoints here allow students, teachers, parents, and staff to inspect
    their own personal domain profiles and associated data without admin rights.
"""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import CurrentUser, get_db
from app.core.exceptions import NotFoundError
from app.schemas.common import StandardResponse
from app.schemas.enrollment import EnrollmentRead
from app.schemas.people import (
    ParentProfileRead,
    StaffProfileRead,
    StudentProfileRead,
    TeacherProfileRead,
)
from app.services.enrollment_service import EnrollmentService
from app.services.people_service import PeopleService

router = APIRouter(
    prefix="/me",
    tags=["Shared - My Profile"],
)


@router.get(
    "/profile",
    summary="Get current user's domain profile",
)
async def get_my_profile(
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
) -> StandardResponse[dict[str, Any]]:
    """
    Resolves the domain profile for the currently authenticated user.
    Checks StudentProfile, TeacherProfile, ParentProfile, and StaffProfile.
    """
    # Check student
    student = await PeopleService.get_student_by_user_id(db, current_user.id, current_user.institute_id)
    if student:
        return StandardResponse(
            data={"type": "STUDENT", "profile": StudentProfileRead.model_validate(student).model_dump()}
        )

    # Check teacher
    teacher = await PeopleService.get_teacher_by_user_id(db, current_user.id, current_user.institute_id)
    if teacher:
        return StandardResponse(
            data={"type": "TEACHER", "profile": TeacherProfileRead.model_validate(teacher).model_dump()}
        )

    # Check parent
    parent = await PeopleService.get_parent_by_user_id(db, current_user.id, current_user.institute_id)
    if parent:
        return StandardResponse(
            data={"type": "PARENT", "profile": ParentProfileRead.model_validate(parent).model_dump()}
        )

    # Check staff
    staff = await PeopleService.get_staff_by_user_id(db, current_user.id, current_user.institute_id)
    if staff:
        return StandardResponse(
            data={"type": "STAFF", "profile": StaffProfileRead.model_validate(staff).model_dump()}
        )

    raise NotFoundError("No domain profile found for this user")


@router.get(
    "/enrollments",
    response_model=list[EnrollmentRead],
    summary="Get current student's enrollments",
)
async def get_my_enrollments(
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    student = await PeopleService.get_student_by_user_id(db, current_user.id, current_user.institute_id)
    if not student:
        raise NotFoundError("Student profile not found for current user")

    enrollments, _ = await EnrollmentService.list_enrollments(
        db, institute_id=current_user.institute_id, student_id=student.id
    )
    return [EnrollmentRead.model_validate(e) for e in enrollments]


@router.get(
    "/children",
    response_model=list[StudentProfileRead],
    summary="Get current parent's children",
)
async def get_my_children(
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    parent = await PeopleService.get_parent_by_user_id(db, current_user.id, current_user.institute_id)
    if not parent:
        raise NotFoundError("Parent profile not found for current user")

    students = await PeopleService.get_students_for_parent(db, parent.id, current_user.institute_id)
    return [StudentProfileRead.model_validate(s) for s in students]
