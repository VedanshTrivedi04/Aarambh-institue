"""
app/api/v1/finance/plans.py
---------------------------
Fee Plan configuration and retrieval endpoints.
"""

from __future__ import annotations

import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, Request, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import CurrentUser, get_db, require_role
from app.core.exceptions import ForbiddenError, NotFoundError
from app.models.people import ParentProfile, StudentParent, StudentProfile
from app.schemas.common import StandardResponse
from app.schemas.finance import FeePlanCreate, FeePlanRead, InstallmentRead
from app.services import finance_service

router = APIRouter(tags=["Finance - Fee Plans"])

_STAFF_OR_ADMIN = ("SUPER_ADMIN", "ADMIN", "COUNSELLOR")


def _format_fee_plan_read(plan) -> FeePlanRead:
    st_name = None
    adm_no = None
    crs_name = None
    bt_name = None
    if plan.enrollment:
        if plan.enrollment.student:
            st = plan.enrollment.student
            st_name = f"{st.first_name} {st.last_name or ''}".strip()
            adm_no = st.admission_number
        if plan.enrollment.batch:
            bt_name = plan.enrollment.batch.name
            if hasattr(plan.enrollment.batch, "course") and plan.enrollment.batch.course:
                crs_name = plan.enrollment.batch.course.name

    installments_read = [
        InstallmentRead(
            id=i.id,
            fee_plan_id=i.fee_plan_id,
            installment_number=i.installment_number,
            amount=i.amount,
            due_date=i.due_date,
            status=i.status,
            paid_amount=i.paid_amount,
            balance_amount=max(0.0, round(i.amount - i.paid_amount, 2)),
        )
        for i in (plan.installments or [])
    ]

    total_paid = sum(i.paid_amount for i in (plan.installments or []))
    outstanding = max(0.0, round(plan.net_amount - total_paid, 2))

    return FeePlanRead(
        id=plan.id,
        institute_id=plan.institute_id,
        enrollment_id=plan.enrollment_id,
        total_amount=plan.total_amount,
        discount_amount=plan.discount_amount,
        scholarship_amount=plan.scholarship_amount,
        net_amount=plan.net_amount,
        plan_type=plan.plan_type,
        discount_reason=plan.discount_reason,
        created_by=plan.created_by,
        created_at=plan.created_at,
        updated_at=plan.updated_at,
        student_name=st_name,
        student_admission_number=adm_no,
        course_name=crs_name,
        batch_name=bt_name,
        total_paid=round(total_paid, 2),
        outstanding_balance=round(outstanding, 2),
        installments=installments_read,
    )


@router.post(
    "/plans",
    response_model=StandardResponse[FeePlanRead],
    status_code=status.HTTP_201_CREATED,
    dependencies=[require_role(*_STAFF_OR_ADMIN)],
    summary="Create fee plan and installments for an enrollment",
)
async def create_fee_plan(
    body: FeePlanCreate,
    current_user: CurrentUser,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    plan = await finance_service.create_fee_plan(
        db=db,
        institute_id=current_user.institute_id,
        creator_user_id=current_user.id,
        payload=body,
        request=request,
    )
    return StandardResponse(
        data=_format_fee_plan_read(plan),
        message="Fee plan and installments created successfully.",
    )


@router.get(
    "/plans/{id}",
    response_model=StandardResponse[FeePlanRead],
    summary="Get fee plan by ID with installment breakdown",
)
async def get_fee_plan(
    id: uuid.UUID,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    is_student_or_parent = current_user.role in ("STUDENT", "PARENT")
    student_id = None
    if current_user.role == "STUDENT":
        s_stmt = select(StudentProfile.id).where(StudentProfile.user_id == current_user.id)
        student_id = (await db.execute(s_stmt)).scalar_one_or_none()
    elif current_user.role == "PARENT":
        p_stmt = select(ParentProfile.id).where(ParentProfile.user_id == current_user.id)
        parent_id = (await db.execute(p_stmt)).scalar_one_or_none()
        if parent_id:
            sp_stmt = select(StudentParent.student_id).where(StudentParent.parent_id == parent_id)
            student_id = (await db.execute(sp_stmt)).scalars().first()

    plan = await finance_service.get_fee_plan(
        db=db,
        institute_id=current_user.institute_id,
        fee_plan_id=id,
        for_student_or_parent=is_student_or_parent,
        student_id=student_id,
    )
    return StandardResponse(data=_format_fee_plan_read(plan))


@router.get(
    "/enrollments/{enrollment_id}/plan",
    response_model=StandardResponse[FeePlanRead],
    summary="Get active fee plan for an enrollment",
)
async def get_fee_plan_by_enrollment(
    enrollment_id: uuid.UUID,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    is_student_or_parent = current_user.role in ("STUDENT", "PARENT")
    student_id = None
    if current_user.role == "STUDENT":
        s_stmt = select(StudentProfile.id).where(StudentProfile.user_id == current_user.id)
        student_id = (await db.execute(s_stmt)).scalar_one_or_none()
    elif current_user.role == "PARENT":
        p_stmt = select(ParentProfile.id).where(ParentProfile.user_id == current_user.id)
        parent_id = (await db.execute(p_stmt)).scalar_one_or_none()
        if parent_id:
            sp_stmt = select(StudentParent.student_id).where(StudentParent.parent_id == parent_id)
            student_id = (await db.execute(sp_stmt)).scalars().first()

    plan = await finance_service.get_fee_plan_by_enrollment(
        db=db,
        institute_id=current_user.institute_id,
        enrollment_id=enrollment_id,
        for_student_or_parent=is_student_or_parent,
        student_id=student_id,
    )
    return StandardResponse(data=_format_fee_plan_read(plan))
