"""
app/api/v1/admin/enrollments.py
-------------------------------
Admin endpoints for student enrollment and batch transfer management.

Guarded by ADMIN / MANAGEMENT roles.
Enforces capacity constraints, duplicate checks, and transfer audit history.
"""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import CurrentUser, get_db, require_role
from app.models.enrollment import EnrollmentStatus
from app.schemas.common import PaginatedResponse, StandardResponse
from app.schemas.enrollment import (
    BatchTransferHistoryRead,
    BatchTransferRequest,
    EnrollmentCreate,
    EnrollmentRead,
    EnrollmentStatusUpdate,
)
from app.services.enrollment_service import EnrollmentService

_ADMIN_ROLES = ("SUPER_ADMIN", "ADMIN", "MANAGEMENT")

router = APIRouter(
    prefix="/enrollments",
    tags=["Admin - Enrollments"],
    dependencies=[require_role(*_ADMIN_ROLES)],
)


@router.post(
    "",
    response_model=StandardResponse[EnrollmentRead],
    status_code=status.HTTP_201_CREATED,
    summary="Enroll a student into a batch",
)
async def enroll_student(
    body: EnrollmentCreate,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    enrollment = await EnrollmentService.enroll_student(
        db=db,
        data=body,
        institute_id=current_user.institute_id,
        enrolled_by=current_user.id,
    )
    await db.commit()
    return StandardResponse(
        data=EnrollmentRead.model_validate(enrollment),
        message="Student enrolled successfully",
    )


@router.get(
    "",
    response_model=PaginatedResponse[EnrollmentRead],
    summary="List enrollments with optional filtering",
)
async def list_enrollments(
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
    student_id: uuid.UUID | None = Query(None, description="Filter by student ID"),
    batch_id: uuid.UUID | None = Query(None, description="Filter by batch ID"),
    enrollment_status: EnrollmentStatus | None = Query(None, alias="status", description="Filter by status"),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
):
    skip = (page - 1) * page_size
    items, total = await EnrollmentService.list_enrollments(
        db=db,
        institute_id=current_user.institute_id,
        student_id=student_id,
        batch_id=batch_id,
        status=enrollment_status,
        skip=skip,
        limit=page_size,
    )
    return PaginatedResponse(
        items=[EnrollmentRead.model_validate(e) for e in items],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get(
    "/transfers/history",
    response_model=PaginatedResponse[BatchTransferHistoryRead],
    summary="List batch transfer history audit records",
)
async def list_transfer_history(
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
    student_id: uuid.UUID | None = Query(None, description="Filter by student ID"),
    enrollment_id: uuid.UUID | None = Query(None, description="Filter by enrollment ID"),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
):
    skip = (page - 1) * page_size
    items, total = await EnrollmentService.get_transfer_history(
        db=db,
        student_id=student_id,
        enrollment_id=enrollment_id,
        institute_id=current_user.institute_id,
        skip=skip,
        limit=page_size,
    )
    return PaginatedResponse(
        items=[BatchTransferHistoryRead.model_validate(h) for h in items],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get(
    "/{enrollment_id}",
    response_model=StandardResponse[EnrollmentRead],
    summary="Get single enrollment",
)
async def get_enrollment(
    enrollment_id: uuid.UUID,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    enrollment = await EnrollmentService.get_enrollment(
        db=db,
        enrollment_id=enrollment_id,
        institute_id=current_user.institute_id,
    )
    return StandardResponse(data=EnrollmentRead.model_validate(enrollment))


@router.post(
    "/{enrollment_id}/transfer",
    response_model=StandardResponse[EnrollmentRead],
    summary="Transfer student from one batch to another",
)
async def transfer_student(
    enrollment_id: uuid.UUID,
    body: BatchTransferRequest,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    _old, _history, new_enrollment = await EnrollmentService.transfer_student(
        db=db,
        enrollment_id=enrollment_id,
        request=body,
        institute_id=current_user.institute_id,
        transferred_by=current_user.id,
    )
    await db.commit()
    return StandardResponse(
        data=EnrollmentRead.model_validate(new_enrollment),
        message="Student transferred successfully",
    )


@router.patch(
    "/{enrollment_id}/status",
    response_model=StandardResponse[EnrollmentRead],
    summary="Update enrollment status (COMPLETED, DROPPED, CANCELLED)",
)
async def update_status(
    enrollment_id: uuid.UUID,
    body: EnrollmentStatusUpdate,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    enrollment = await EnrollmentService.update_status(
        db=db,
        enrollment_id=enrollment_id,
        update_data=body,
        institute_id=current_user.institute_id,
    )
    await db.commit()
    return StandardResponse(
        data=EnrollmentRead.model_validate(enrollment),
        message="Enrollment status updated",
    )
