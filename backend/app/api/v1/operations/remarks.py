"""
app/api/v1/operations/remarks.py
--------------------------------
Teacher remarks on students (visible to parents).

Endpoints:
  POST /remarks                       — Teacher creates remark on a student
  GET  /remarks/student/{student_id}  — View remarks on a student
"""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import CurrentUser, get_db, require_role
from app.schemas.academic_operations import StudentRemarkCreate, StudentRemarkRead
from app.schemas.common import StandardResponse
from app.services.academic_operations_service import AcademicOperationsService

_TEACHER_OR_ADMIN = ("SUPER_ADMIN", "ADMIN", "MANAGEMENT", "TEACHER")

router = APIRouter(
    prefix="/remarks",
    tags=["Operations - Student Remarks"],
)


@router.post(
    "",
    response_model=StandardResponse[StudentRemarkRead],
    status_code=status.HTTP_201_CREATED,
    dependencies=[require_role(*_TEACHER_OR_ADMIN)],
    summary="Create a teacher observation/remark on a student",
)
async def create_student_remark(
    body: StudentRemarkCreate,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    remark = await AcademicOperationsService.create_student_remark(
        db, body, current_user, current_user.institute_id
    )
    await db.commit()
    return StandardResponse(
        data=StudentRemarkRead.model_validate(remark),
        message="Remark recorded successfully",
    )


@router.get(
    "/student/{student_id}",
    response_model=list[StudentRemarkRead],
    summary="List remarks for a student (filtered for parents)",
)
async def list_student_remarks(
    student_id: uuid.UUID,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    parent_view = current_user.role == "PARENT"
    remarks = await AcademicOperationsService.list_student_remarks(
        db, student_id, parent_view=parent_view, institute_id=current_user.institute_id
    )
    return [StudentRemarkRead.model_validate(r) for r in remarks]
