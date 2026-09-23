"""
app/api/v1/finance/student.py
-----------------------------
Student self-service fee portal & staff student financial summary endpoints.
"""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import CurrentUser, get_db, require_role
from app.api.v1.finance.plans import _format_fee_plan_read
from app.core.exceptions import ForbiddenError, NotFoundError
from app.models.people import ParentProfile, StudentParent, StudentProfile
from app.schemas.common import StandardResponse
from app.schemas.finance import InstallmentRead, StudentFeeSummary
from app.services import finance_service

router = APIRouter(tags=["Finance - Student Ledger"])

_STAFF_OR_ADMIN = ("SUPER_ADMIN", "ADMIN", "COUNSELLOR")


def _format_student_fee_summary(data: dict) -> StudentFeeSummary:
    plans_read = [_format_fee_plan_read(p) for p in data["plans"]]
    next_inst_read = None
    if data.get("next_due_installment"):
        i = data["next_due_installment"]
        next_inst_read = InstallmentRead(
            id=i.id,
            fee_plan_id=i.fee_plan_id,
            installment_number=i.installment_number,
            amount=i.amount,
            due_date=i.due_date,
            status=i.status,
            paid_amount=i.paid_amount,
            balance_amount=max(0.0, round(i.amount - i.paid_amount, 2)),
        )

    return StudentFeeSummary(
        student_id=data["student_id"],
        student_name=data["student_name"],
        admission_number=data["admission_number"],
        total_fee=data["total_fee"],
        total_paid=data["total_paid"],
        total_outstanding=data["total_outstanding"],
        plans=plans_read,
        next_due_installment=next_inst_read,
    )


@router.get(
    "/my-fees",
    response_model=StandardResponse[StudentFeeSummary],
    dependencies=[require_role("STUDENT", "PARENT")],
    summary="Student or parent views their aggregated fee ledger and next due payment",
)
async def get_my_fees(
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    if current_user.role == "STUDENT":
        s_stmt = select(StudentProfile.id).where(StudentProfile.user_id == current_user.id)
        student_id = (await db.execute(s_stmt)).scalar_one_or_none()
        if not student_id:
            raise NotFoundError(f"StudentProfile for user {current_user.id} not found.")
    elif current_user.role == "PARENT":
        p_stmt = select(ParentProfile.id).where(ParentProfile.user_id == current_user.id)
        parent_id = (await db.execute(p_stmt)).scalar_one_or_none()
        if not parent_id:
            raise NotFoundError(f"ParentProfile for user {current_user.id} not found.")
        sp_stmt = select(StudentParent.student_id).where(StudentParent.parent_id == parent_id)
        student_id = (await db.execute(sp_stmt)).scalars().first()
        if not student_id:
            raise NotFoundError(f"No student linked to parent profile {parent_id}.")
    else:
        raise ForbiddenError("Only students and parents can access this endpoint.")

    data = await finance_service.get_student_fee_summary(
        db=db,
        institute_id=current_user.institute_id,
        student_id=student_id,
    )
    return StandardResponse(data=_format_student_fee_summary(data))


@router.get(
    "/students/{student_id}/summary",
    response_model=StandardResponse[StudentFeeSummary],
    dependencies=[require_role(*_STAFF_OR_ADMIN)],
    summary="Admin/Counselor views student fee summary and payment history",
)
async def get_student_fee_summary_by_admin(
    student_id: uuid.UUID,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    data = await finance_service.get_student_fee_summary(
        db=db,
        institute_id=current_user.institute_id,
        student_id=student_id,
    )
    return StandardResponse(data=_format_student_fee_summary(data))
