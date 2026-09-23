"""
app/api/v1/finance/payments.py
------------------------------
Append-only payment recording and adjustment endpoints.
"""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, Request, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import CurrentUser, get_db, require_role
from app.core.exceptions import ForbiddenError
from app.models.people import ParentProfile, StudentParent, StudentProfile
from app.schemas.common import StandardResponse
from app.schemas.finance import (
    PaymentAdjustmentCreate,
    PaymentAdjustmentRead,
    PaymentRead,
    PaymentRecordRequest,
    ReceiptRead,
)
from app.services import finance_service

router = APIRouter(tags=["Finance - Payments & Adjustments"])

_STAFF_OR_ADMIN = ("SUPER_ADMIN", "ADMIN", "COUNSELLOR")
_ADMIN_ONLY = ("SUPER_ADMIN", "ADMIN")


def _format_payment_read(p) -> PaymentRead:
    rcp_read = None
    if p.receipt:
        rcp_read = ReceiptRead(
            id=p.receipt.id,
            payment_id=p.receipt.payment_id,
            receipt_number=p.receipt.receipt_number,
            pdf_storage_key=p.receipt.pdf_storage_key,
            issued_at=p.receipt.issued_at,
            created_at=p.receipt.created_at,
        )

    adjs_read = [
        PaymentAdjustmentRead(
            id=a.id,
            payment_id=a.payment_id,
            adjustment_type=a.adjustment_type,
            amount=a.amount,
            reason=a.reason,
            authorized_by=a.authorized_by,
            authorized_by_name=a.authorizer.email if getattr(a, "authorizer", None) else None,
            created_at=a.created_at,
        )
        for a in (p.adjustments or [])
    ]

    rec_name = p.recorder.email if getattr(p, "recorder", None) else None

    return PaymentRead(
        id=p.id,
        installment_id=p.installment_id,
        amount=p.amount,
        payment_method=p.payment_method,
        transaction_reference=p.transaction_reference,
        idempotency_key=p.idempotency_key,
        paid_at=p.paid_at,
        recorded_by=p.recorded_by,
        recorded_by_name=rec_name,
        created_at=p.created_at,
        receipt=rcp_read,
        adjustments=adjs_read,
    )


@router.post(
    "/payments",
    response_model=StandardResponse[PaymentRead],
    status_code=status.HTTP_201_CREATED,
    dependencies=[require_role(*_STAFF_OR_ADMIN)],
    summary="Record an append-only payment for an installment",
)
async def record_payment(
    body: PaymentRecordRequest,
    current_user: CurrentUser,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    payment = await finance_service.record_payment(
        db=db,
        institute_id=current_user.institute_id,
        recorder_user_id=current_user.id,
        payload=body,
        request=request,
    )
    return StandardResponse(
        data=_format_payment_read(payment),
        message=f"Payment recorded successfully. Receipt #{payment.receipt.receipt_number if payment.receipt else 'N/A'}",
    )


@router.get(
    "/payments/{id}",
    response_model=StandardResponse[PaymentRead],
    summary="Get payment details with receipt and adjustment audit trail",
)
async def get_payment(
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

    payment = await finance_service.get_payment(
        db=db,
        institute_id=current_user.institute_id,
        payment_id=id,
        for_student_or_parent=is_student_or_parent,
        student_id=student_id,
    )
    return StandardResponse(data=_format_payment_read(payment))


@router.post(
    "/payments/{id}/adjustments",
    response_model=StandardResponse[PaymentAdjustmentRead],
    status_code=status.HTTP_201_CREATED,
    dependencies=[require_role(*_ADMIN_ONLY)],
    summary="Record an append-only correction, reversal, or refund on a payment",
)
async def record_payment_adjustment(
    id: uuid.UUID,
    body: PaymentAdjustmentCreate,
    current_user: CurrentUser,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    adj = await finance_service.record_payment_adjustment(
        db=db,
        institute_id=current_user.institute_id,
        authorizer_user_id=current_user.id,
        payment_id=id,
        payload=body,
        request=request,
    )
    read_obj = PaymentAdjustmentRead(
        id=adj.id,
        payment_id=adj.payment_id,
        adjustment_type=adj.adjustment_type,
        amount=adj.amount,
        reason=adj.reason,
        authorized_by=adj.authorized_by,
        authorized_by_name=current_user.email,
        created_at=adj.created_at,
    )
    return StandardResponse(
        data=read_obj,
        message=f"Applied {adj.adjustment_type.value} adjustment of {adj.amount} successfully.",
    )


@router.get(
    "/payments/{id}/adjustments",
    response_model=StandardResponse[list[PaymentAdjustmentRead]],
    dependencies=[require_role(*_ADMIN_ONLY)],
    summary="List adjustments for a payment",
)
async def list_payment_adjustments(
    id: uuid.UUID,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    payment = await finance_service.get_payment(
        db=db,
        institute_id=current_user.institute_id,
        payment_id=id,
    )
    items = [
        PaymentAdjustmentRead(
            id=a.id,
            payment_id=a.payment_id,
            adjustment_type=a.adjustment_type,
            amount=a.amount,
            reason=a.reason,
            authorized_by=a.authorized_by,
            authorized_by_name=a.authorizer.email if getattr(a, "authorizer", None) else None,
            created_at=a.created_at,
        )
        for a in (payment.adjustments or [])
    ]
    return StandardResponse(data=items)
