"""
app/api/v1/finance/payments_online.py
--------------------------------------
Razorpay checkout endpoints: order creation + client-side verification.

Students/parents can pay their own outstanding installments online;
staff can also trigger an order (e.g. to show a QR/checkout on their own
screen for a walk-in student paying by card/UPI instead of cash).

The webhook (server-to-server, unauthenticated but signature-verified) lives
in app/api/v1/finance/webhooks.py and is the durable source of truth —
this router's /verify endpoint is a fast-path for immediate UI feedback.
"""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, Request, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import CurrentUser, get_db, require_role
from app.core.config import get_settings
from app.models.people import ParentProfile, StudentParent, StudentProfile
from app.schemas.common import StandardResponse
from app.schemas.finance import (
    PaymentRead,
    RazorpayOrderCreateRequest,
    RazorpayOrderCreateResponse,
    RazorpayVerifyRequest,
)
from app.services import finance_service

router = APIRouter(tags=["Finance - Razorpay Online Payments"])

_ONLINE_PAYERS = ("STUDENT", "PARENT", "SUPER_ADMIN", "ADMIN", "COUNSELLOR")


async def _resolve_own_student_id(current_user, db: AsyncSession) -> uuid.UUID | None:
    """Returns the student_id to enforce ownership for, or None for staff callers."""
    if current_user.role == "STUDENT":
        s_stmt = select(StudentProfile.id).where(StudentProfile.user_id == current_user.id)
        return (await db.execute(s_stmt)).scalar_one_or_none()
    if current_user.role == "PARENT":
        p_stmt = select(ParentProfile.id).where(ParentProfile.user_id == current_user.id)
        parent_id = (await db.execute(p_stmt)).scalar_one_or_none()
        if not parent_id:
            return None
        sp_stmt = select(StudentParent.student_id).where(StudentParent.parent_id == parent_id)
        return (await db.execute(sp_stmt)).scalars().first()
    return None  # staff — no ownership restriction


@router.post(
    "/payments/razorpay/orders",
    response_model=StandardResponse[RazorpayOrderCreateResponse],
    status_code=status.HTTP_201_CREATED,
    dependencies=[require_role(*_ONLINE_PAYERS)],
    summary="Create a Razorpay Order for an installment's remaining balance",
)
async def create_razorpay_order(
    body: RazorpayOrderCreateRequest,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    student_id = await _resolve_own_student_id(current_user, db)

    razorpay_order, installment = await finance_service.create_razorpay_order(
        db=db,
        institute_id=current_user.institute_id,
        initiator_user_id=current_user.id,
        payload=body,
        student_id=student_id,
    )

    settings = get_settings()
    return StandardResponse(
        data=RazorpayOrderCreateResponse(
            razorpay_order_id=razorpay_order.razorpay_order_id,
            razorpay_key_id=settings.RAZORPAY_KEY_ID or "",
            amount=round(razorpay_order.amount * 100),
            currency="INR",
            installment_id=installment.id,
            name=settings.APP_NAME,
            description=f"Installment #{installment.installment_number} fee payment",
            prefill_name=current_user.email,
            prefill_email=current_user.email,
            prefill_contact=getattr(current_user, "mobile", None),
        )
    )


@router.post(
    "/payments/razorpay/verify",
    response_model=StandardResponse[PaymentRead],
    dependencies=[require_role(*_ONLINE_PAYERS)],
    summary="Verify a completed Razorpay checkout and append the payment to the ledger",
)
async def verify_razorpay_payment(
    body: RazorpayVerifyRequest,
    current_user: CurrentUser,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    payment = await finance_service.confirm_razorpay_payment(
        db=db,
        institute_id=current_user.institute_id,
        razorpay_order_id=body.razorpay_order_id,
        razorpay_payment_id=body.razorpay_payment_id,
        razorpay_signature=body.razorpay_signature,
        request=request,
    )

    from app.api.v1.finance.payments import _format_payment_read

    return StandardResponse(
        data=_format_payment_read(payment),
        message=f"Payment verified. Receipt #{payment.receipt.receipt_number if payment.receipt else 'N/A'}",
    )
