"""
app/api/v1/admin/people.py
--------------------------
Admin endpoints for managing domain profiles:
  - StudentProfile
  - TeacherProfile
  - ParentProfile
  - StaffProfile
  - StudentParent link associations

Guarded by ADMIN / MANAGEMENT roles.
"""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import CurrentUser, get_db, require_role
from app.schemas.common import MessageResponse, PaginatedResponse, StandardResponse
from app.schemas.people import (
    ParentProfileCreate,
    ParentProfileRead,
    ParentProfileUpdate,
    StaffProfileCreate,
    StaffProfileRead,
    StaffProfileUpdate,
    StudentParentLink,
    StudentParentRead,
    StudentProfileCreate,
    StudentProfileRead,
    StudentProfileUpdate,
    TeacherOnboardRequest,
    TeacherOnboardResponse,
    TeacherProfileCreate,
    TeacherProfileRead,
    TeacherProfileUpdate,
)
from app.services.people_service import PeopleService

_ADMIN_ROLES = ("SUPER_ADMIN", "ADMIN", "MANAGEMENT")

router = APIRouter(
    prefix="/people",
    tags=["Admin - People & Profiles"],
    dependencies=[require_role(*_ADMIN_ROLES)],
)


# ─────────────────────────────────────────────────────────────────────────────
# Student Profiles
# ─────────────────────────────────────────────────────────────────────────────

@router.post(
    "/students",
    response_model=StandardResponse[StudentProfileRead],
    status_code=status.HTTP_201_CREATED,
    summary="Create student domain profile",
)
async def create_student(
    body: StudentProfileCreate,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    profile = await PeopleService.create_student_profile(
        db, body, current_user.institute_id
    )
    await db.commit()
    return StandardResponse(
        data=StudentProfileRead.model_validate(profile),
        message="Student profile created successfully",
    )


@router.get(
    "/students",
    response_model=PaginatedResponse[StudentProfileRead],
    summary="List students with optional search and class filter",
)
async def list_students(
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
    class_id: uuid.UUID | None = Query(None, description="Filter by school class ID"),
    search: str | None = Query(None, description="Search by name or admission number"),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
):
    skip = (page - 1) * page_size
    items, total = await PeopleService.list_students(
        db, current_user.institute_id, class_id=class_id, search=search, skip=skip, limit=page_size
    )
    return PaginatedResponse(
        items=[StudentProfileRead.model_validate(p) for p in items],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get(
    "/students/{profile_id}",
    response_model=StandardResponse[StudentProfileRead],
    summary="Get single student profile",
)
async def get_student(
    profile_id: uuid.UUID,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    profile = await PeopleService.get_student_profile(
        db, profile_id, current_user.institute_id
    )
    return StandardResponse(data=StudentProfileRead.model_validate(profile))


@router.patch(
    "/students/{profile_id}",
    response_model=StandardResponse[StudentProfileRead],
    summary="Update student profile",
)
async def update_student(
    profile_id: uuid.UUID,
    body: StudentProfileUpdate,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    profile = await PeopleService.update_student_profile(
        db, profile_id, body, current_user.institute_id
    )
    await db.commit()
    return StandardResponse(
        data=StudentProfileRead.model_validate(profile),
        message="Student profile updated",
    )


@router.delete(
    "/students/{profile_id}",
    response_model=MessageResponse,
    summary="Soft-delete student profile",
)
async def delete_student(
    profile_id: uuid.UUID,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    await PeopleService.soft_delete_student_profile(
        db, profile_id, current_user.institute_id
    )
    await db.commit()
    return MessageResponse(message="Student profile deleted")


# ─────────────────────────────────────────────────────────────────────────────
# Teacher Profiles
# ─────────────────────────────────────────────────────────────────────────────

@router.post(
    "/teachers/onboard",
    response_model=StandardResponse[TeacherOnboardResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Create a TEACHER login account and profile atomically",
)
async def onboard_teacher(
    body: TeacherOnboardRequest,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    profile, temp_password = await PeopleService.onboard_teacher(
        db, body, current_user.institute_id
    )
    await db.commit()
    return StandardResponse(
        data=TeacherOnboardResponse(
            teacher_user_id=profile.user_id,
            teacher_profile_id=profile.id,
            email=profile.personal_email or "",
            temp_password=temp_password,
        ),
        message="Teacher onboarded successfully",
    )


@router.post(
    "/teachers",
    response_model=StandardResponse[TeacherProfileRead],
    status_code=status.HTTP_201_CREATED,
    summary="Create teacher domain profile",
)
async def create_teacher(
    body: TeacherProfileCreate,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    profile = await PeopleService.create_teacher_profile(
        db, body, current_user.institute_id
    )
    await db.commit()
    return StandardResponse(
        data=TeacherProfileRead.model_validate(profile),
        message="Teacher profile created successfully",
    )


@router.get(
    "/teachers",
    response_model=PaginatedResponse[TeacherProfileRead],
    summary="List teachers",
)
async def list_teachers(
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
    search: str | None = Query(None, description="Search by name or employee code"),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
):
    skip = (page - 1) * page_size
    items, total = await PeopleService.list_teachers(
        db, current_user.institute_id, search=search, skip=skip, limit=page_size
    )
    return PaginatedResponse(
        items=[TeacherProfileRead.model_validate(p) for p in items],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get(
    "/teachers/{profile_id}",
    response_model=StandardResponse[TeacherProfileRead],
    summary="Get single teacher profile",
)
async def get_teacher(
    profile_id: uuid.UUID,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    profile = await PeopleService.get_teacher_profile(
        db, profile_id, current_user.institute_id
    )
    return StandardResponse(data=TeacherProfileRead.model_validate(profile))


@router.patch(
    "/teachers/{profile_id}",
    response_model=StandardResponse[TeacherProfileRead],
    summary="Update teacher profile",
)
async def update_teacher(
    profile_id: uuid.UUID,
    body: TeacherProfileUpdate,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    profile = await PeopleService.update_teacher_profile(
        db, profile_id, body, current_user.institute_id
    )
    await db.commit()
    return StandardResponse(
        data=TeacherProfileRead.model_validate(profile),
        message="Teacher profile updated",
    )


@router.delete(
    "/teachers/{profile_id}",
    response_model=MessageResponse,
    summary="Soft-delete teacher profile",
)
async def delete_teacher(
    profile_id: uuid.UUID,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    await PeopleService.soft_delete_teacher_profile(
        db, profile_id, current_user.institute_id
    )
    await db.commit()
    return MessageResponse(message="Teacher profile deleted")


# ─────────────────────────────────────────────────────────────────────────────
# Parent Profiles & Links
# ─────────────────────────────────────────────────────────────────────────────

@router.post(
    "/parents",
    response_model=StandardResponse[ParentProfileRead],
    status_code=status.HTTP_201_CREATED,
    summary="Create parent domain profile",
)
async def create_parent(
    body: ParentProfileCreate,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    profile = await PeopleService.create_parent_profile(
        db, body, current_user.institute_id
    )
    await db.commit()
    return StandardResponse(
        data=ParentProfileRead.model_validate(profile),
        message="Parent profile created successfully",
    )


@router.get(
    "/parents",
    response_model=PaginatedResponse[ParentProfileRead],
    summary="List parent profiles",
)
async def list_parents(
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
    search: str | None = Query(None, description="Search by name"),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
):
    skip = (page - 1) * page_size
    items, total = await PeopleService.list_parents(
        db, current_user.institute_id, search=search, skip=skip, limit=page_size
    )
    return PaginatedResponse(
        items=[ParentProfileRead.model_validate(p) for p in items],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get(
    "/parents/{profile_id}",
    response_model=StandardResponse[ParentProfileRead],
    summary="Get single parent profile",
)
async def get_parent(
    profile_id: uuid.UUID,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    profile = await PeopleService.get_parent_profile(
        db, profile_id, current_user.institute_id
    )
    return StandardResponse(data=ParentProfileRead.model_validate(profile))


@router.patch(
    "/parents/{profile_id}",
    response_model=StandardResponse[ParentProfileRead],
    summary="Update parent profile",
)
async def update_parent(
    profile_id: uuid.UUID,
    body: ParentProfileUpdate,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    profile = await PeopleService.update_parent_profile(
        db, profile_id, body, current_user.institute_id
    )
    await db.commit()
    return StandardResponse(
        data=ParentProfileRead.model_validate(profile),
        message="Parent profile updated",
    )


@router.post(
    "/students/{student_id}/parents",
    response_model=StandardResponse[StudentParentRead],
    status_code=status.HTTP_201_CREATED,
    summary="Link a parent to a student",
)
async def link_parent(
    student_id: uuid.UUID,
    body: StudentParentLink,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    link = await PeopleService.link_parent_to_student(
        db, student_id, body.parent_id, body.is_primary, current_user.institute_id
    )
    await db.commit()
    return StandardResponse(
        data=StudentParentRead.model_validate(link),
        message="Parent linked to student successfully",
    )


@router.delete(
    "/students/{student_id}/parents/{parent_id}",
    response_model=MessageResponse,
    summary="Unlink a parent from a student",
)
async def unlink_parent(
    student_id: uuid.UUID,
    parent_id: uuid.UUID,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    await PeopleService.unlink_parent_from_student(
        db, student_id, parent_id, current_user.institute_id
    )
    await db.commit()
    return MessageResponse(message="Parent unlinked from student")


@router.get(
    "/students/{student_id}/parents",
    response_model=list[ParentProfileRead],
    summary="Get parents associated with a student",
)
async def get_student_parents(
    student_id: uuid.UUID,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    parents = await PeopleService.get_parents_for_student(
        db, student_id, current_user.institute_id
    )
    return [ParentProfileRead.model_validate(p) for p in parents]


@router.get(
    "/parents/{parent_id}/students",
    response_model=list[StudentProfileRead],
    summary="Get students associated with a parent",
)
async def get_parent_students(
    parent_id: uuid.UUID,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    students = await PeopleService.get_students_for_parent(
        db, parent_id, current_user.institute_id
    )
    return [StudentProfileRead.model_validate(s) for s in students]


# ─────────────────────────────────────────────────────────────────────────────
# Staff Profiles
# ─────────────────────────────────────────────────────────────────────────────

@router.post(
    "/staff",
    response_model=StandardResponse[StaffProfileRead],
    status_code=status.HTTP_201_CREATED,
    summary="Create staff domain profile",
)
async def create_staff(
    body: StaffProfileCreate,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    profile = await PeopleService.create_staff_profile(
        db, body, current_user.institute_id
    )
    await db.commit()
    return StandardResponse(
        data=StaffProfileRead.model_validate(profile),
        message="Staff profile created successfully",
    )


@router.get(
    "/staff",
    response_model=PaginatedResponse[StaffProfileRead],
    summary="List staff profiles",
)
async def list_staff(
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
    search: str | None = Query(None, description="Search by name or employee code"),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
):
    skip = (page - 1) * page_size
    items, total = await PeopleService.list_staff(
        db, current_user.institute_id, search=search, skip=skip, limit=page_size
    )
    return PaginatedResponse(
        items=[StaffProfileRead.model_validate(p) for p in items],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get(
    "/staff/{profile_id}",
    response_model=StandardResponse[StaffProfileRead],
    summary="Get single staff profile",
)
async def get_staff(
    profile_id: uuid.UUID,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    profile = await PeopleService.get_staff_profile(
        db, profile_id, current_user.institute_id
    )
    return StandardResponse(data=StaffProfileRead.model_validate(profile))


@router.patch(
    "/staff/{profile_id}",
    response_model=StandardResponse[StaffProfileRead],
    summary="Update staff profile",
)
async def update_staff(
    profile_id: uuid.UUID,
    body: StaffProfileUpdate,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    profile = await PeopleService.update_staff_profile(
        db, profile_id, body, current_user.institute_id
    )
    await db.commit()
    return StandardResponse(
        data=StaffProfileRead.model_validate(profile),
        message="Staff profile updated",
    )


@router.delete(
    "/staff/{profile_id}",
    response_model=MessageResponse,
    summary="Soft-delete staff profile",
)
async def delete_staff(
    profile_id: uuid.UUID,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    await PeopleService.soft_delete_staff_profile(
        db, profile_id, current_user.institute_id
    )
    await db.commit()
    return MessageResponse(message="Staff profile deleted")
