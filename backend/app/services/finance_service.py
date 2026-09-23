"""
app/services/finance_service.py
-------------------------------
Business logic for Slice 9: Finance & Immutable Ledger.

Core Invariants (spec §10, rules.md §6):
  1. Append-only ledger: Payments and Receipts are NEVER updated or deleted in place.
  2. Corrections are recorded as new PaymentAdjustment records (CORRECTION, REVERSAL, REFUND).
  3. Strict server-side fee and balance verification: client amount cannot exceed remaining balance.
  4. Idempotency: Duplicate payment requests with identical idempotency_key safely return the existing payment.
  5. Audit logging for fee plans, payments, adjustments, and receipts.
"""

from __future__ import annotations

import uuid
from datetime import date as Date, datetime, timezone
from typing import Any

from fastapi import Request
from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, selectinload

from app.core.exceptions import (
    ConflictError,
    ForbiddenError,
    NotFoundError,
    ValidationError,
)
from app.core.logging import get_logger
from app.models.enrollment import Enrollment, EnrollmentStatus
from app.models.finance import (
    AdjustmentType,
    FeePlan,
    FeePlanType,
    Installment,
    InstallmentStatus,
    Payment,
    PaymentAdjustment,
    PaymentMethod,
    Receipt,
    RazorpayOrder,
    RazorpayOrderStatus,
)
from app.models.people import StudentProfile
from app.models.user import User
from app.schemas.finance import (
    FeePlanCreate,
    FeePlanUpdate,
    PaymentAdjustmentCreate,
    PaymentRecordRequest,
    RazorpayOrderCreateRequest,
)
from app.services import audit_service, razorpay_service

logger = get_logger("services.finance")


def _add_months(d: Date, months: int) -> Date:
    """Helper to add whole calendar months to a date without external dependencies."""
    month = d.month - 1 + months
    year = d.year + month // 12
    month = month % 12 + 1
    # Day clamping for shorter months
    is_leap = year % 4 == 0 and not (year % 100 == 0 and year % 400 != 0)
    days_in_month = [31, 29 if is_leap else 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    day = min(d.day, days_in_month[month - 1])
    return Date(year, month, day)


# ─────────────────────────────────────────────────────────────────────────────
# 1. Fee Plans
# ─────────────────────────────────────────────────────────────────────────────

async def create_fee_plan(
    db: AsyncSession,
    *,
    institute_id: uuid.UUID,
    creator_user_id: uuid.UUID,
    payload: FeePlanCreate,
    request: Request | None = None,
) -> FeePlan:
    """
    Create a fee plan and automatically generate installment milestones.
    """
    # 1. Validate Enrollment
    e_stmt = (
        select(Enrollment)
        .where(
            Enrollment.id == payload.enrollment_id,
            Enrollment.institute_id == institute_id,
        )
        .options(selectinload(Enrollment.student), selectinload(Enrollment.batch))
    )
    enrollment = (await db.execute(e_stmt)).scalar_one_or_none()
    if not enrollment:
        raise NotFoundError(f"Enrollment {payload.enrollment_id} not found in this institute.")
    if enrollment.status == EnrollmentStatus.CANCELLED:
        raise ValidationError("Cannot create a fee plan for a cancelled enrollment.")

    # 2. Check for existing active fee plan on this enrollment
    existing_stmt = select(FeePlan).where(
        FeePlan.enrollment_id == payload.enrollment_id,
        FeePlan.deleted_at.is_(None),
    )
    existing_plan = (await db.execute(existing_stmt)).scalar_one_or_none()
    if existing_plan:
        raise ConflictError(f"An active fee plan ({existing_plan.id}) already exists for this enrollment.")

    # 3. Compute net amount
    net_amount = round(payload.total_amount - payload.discount_amount - payload.scholarship_amount, 2)
    if net_amount <= 0:
        raise ValidationError(f"Net fee amount ({net_amount}) must be greater than 0 after discounts and scholarships.")

    # 4. Construct FeePlan
    fee_branch_id = getattr(enrollment, "branch_id", None)
    fee_plan = FeePlan(
        institute_id=institute_id,
        branch_id=fee_branch_id,
        enrollment_id=enrollment.id,
        total_amount=payload.total_amount,
        discount_amount=payload.discount_amount,
        scholarship_amount=payload.scholarship_amount,
        net_amount=net_amount,
        plan_type=payload.plan_type,
        discount_reason=payload.discount_reason,
        created_by=creator_user_id,
    )
    db.add(fee_plan)
    await db.flush()

    # 5. Generate Installments
    installments_to_add: list[Installment] = []
    if payload.plan_type == FeePlanType.LUMP_SUM or payload.installment_count == 1:
        inst = Installment(
            institute_id=institute_id,
            branch_id=fee_branch_id,
            fee_plan_id=fee_plan.id,
            installment_number=1,
            amount=net_amount,
            due_date=payload.first_due_date,
            status=InstallmentStatus.UPCOMING if payload.first_due_date >= Date.today() else InstallmentStatus.DUE,
            paid_amount=0.0,
        )
        installments_to_add.append(inst)
    else:
        count = payload.installment_count
        base_amount = round(net_amount / count, 2)
        # Remainder is placed in the final installment to ensure sum == net_amount exactly
        remainder = round(net_amount - (base_amount * (count - 1)), 2)

        for i in range(1, count + 1):
            amount = base_amount if i < count else remainder
            due = _add_months(payload.first_due_date, i - 1)
            inst = Installment(
                institute_id=institute_id,
                branch_id=fee_branch_id,
                fee_plan_id=fee_plan.id,
                installment_number=i,
                amount=amount,
                due_date=due,
                status=InstallmentStatus.UPCOMING if due >= Date.today() else InstallmentStatus.DUE,
                paid_amount=0.0,
            )
            installments_to_add.append(inst)

    db.add_all(installments_to_add)
    await db.flush()
    await db.refresh(fee_plan)

    # 6. Audit Log
    creator = await db.get(User, creator_user_id)
    if creator:
        await audit_service.log(
            db=db,
            actor=creator,
            action="fee_plan.created",
            entity_name="fee_plans",
            entity_id=str(fee_plan.id),
            old_values=None,
            new_values={
                "enrollment_id": str(enrollment.id),
                "net_amount": net_amount,
                "plan_type": payload.plan_type.value,
                "installment_count": len(installments_to_add),
            },
            request=request,
            institute_id=institute_id,
        )

    logger.info("Created fee plan", extra={"fee_plan_id": str(fee_plan.id), "enrollment_id": str(enrollment.id)})
    return fee_plan


async def get_fee_plan(
    db: AsyncSession,
    *,
    institute_id: uuid.UUID,
    fee_plan_id: uuid.UUID,
    for_student_or_parent: bool = False,
    student_id: uuid.UUID | None = None,
) -> FeePlan:
    """Fetch fee plan with all installments and payments."""
    stmt = (
        select(FeePlan)
        .where(
            FeePlan.id == fee_plan_id,
            FeePlan.institute_id == institute_id,
            FeePlan.deleted_at.is_(None),
        )
        .options(
            selectinload(FeePlan.enrollment).selectinload(Enrollment.student),
            selectinload(FeePlan.enrollment).selectinload(Enrollment.batch),
            selectinload(FeePlan.creator),
            selectinload(FeePlan.installments).selectinload(Installment.payments).selectinload(Payment.receipt),
            selectinload(FeePlan.installments).selectinload(Installment.payments).selectinload(Payment.adjustments),
        )
    )
    plan = (await db.execute(stmt)).scalar_one_or_none()
    if not plan:
        raise NotFoundError(f"FeePlan {fee_plan_id} not found.")

    if for_student_or_parent:
        if student_id and plan.enrollment.student_id != student_id:
            raise ForbiddenError("You do not have permission to view this fee plan.")

    return plan


async def get_fee_plan_by_enrollment(
    db: AsyncSession,
    *,
    institute_id: uuid.UUID,
    enrollment_id: uuid.UUID,
    for_student_or_parent: bool = False,
    student_id: uuid.UUID | None = None,
) -> FeePlan:
    """Fetch active fee plan for an enrollment."""
    stmt = (
        select(FeePlan)
        .where(
            FeePlan.enrollment_id == enrollment_id,
            FeePlan.institute_id == institute_id,
            FeePlan.deleted_at.is_(None),
        )
        .options(
            selectinload(FeePlan.enrollment).selectinload(Enrollment.student),
            selectinload(FeePlan.enrollment).selectinload(Enrollment.batch),
            selectinload(FeePlan.creator),
            selectinload(FeePlan.installments).selectinload(Installment.payments).selectinload(Payment.receipt),
            selectinload(FeePlan.installments).selectinload(Installment.payments).selectinload(Payment.adjustments),
        )
    )
    plan = (await db.execute(stmt)).scalar_one_or_none()
    if not plan:
        raise NotFoundError(f"No active fee plan found for enrollment {enrollment_id}.")

    if for_student_or_parent:
        if student_id and plan.enrollment.student_id != student_id:
            raise ForbiddenError("You do not have permission to view this fee plan.")

    return plan


# ─────────────────────────────────────────────────────────────────────────────
# 2. Payments (Append-Only)
# ─────────────────────────────────────────────────────────────────────────────

async def record_payment(
    db: AsyncSession,
    *,
    institute_id: uuid.UUID,
    recorder_user_id: uuid.UUID,
    payload: PaymentRecordRequest,
    request: Request | None = None,
) -> Payment:
    """
    Record an append-only payment for an installment with idempotency protection.
    """
    # 1. Idempotency Check: if idempotency_key matches, return existing payment
    existing_stmt = (
        select(Payment)
        .where(
            Payment.idempotency_key == payload.idempotency_key,
            Payment.institute_id == institute_id,
        )
        .options(
            selectinload(Payment.installment),
            selectinload(Payment.receipt),
            selectinload(Payment.adjustments),
            selectinload(Payment.recorder),
        )
    )
    existing_payment = (await db.execute(existing_stmt)).scalar_one_or_none()
    if existing_payment:
        logger.info(
            "Idempotent payment replay detected",
            extra={"payment_id": str(existing_payment.id), "idempotency_key": payload.idempotency_key},
        )
        return existing_payment

    # 2. Load Installment
    inst_stmt = (
        select(Installment)
        .where(
            Installment.id == payload.installment_id,
            Installment.institute_id == institute_id,
            Installment.deleted_at.is_(None),
        )
        .options(selectinload(Installment.fee_plan).selectinload(FeePlan.enrollment))
    )
    installment = (await db.execute(inst_stmt)).scalar_one_or_none()
    if not installment:
        raise NotFoundError(f"Installment {payload.installment_id} not found.")

    if installment.status == InstallmentStatus.PAID:
        raise ConflictError(f"Installment {installment.installment_number} has already been fully paid.")

    remaining_balance = round(installment.amount - installment.paid_amount, 2)
    if round(payload.amount, 2) > remaining_balance:
        raise ValidationError(
            f"Payment amount ({payload.amount}) exceeds remaining installment balance ({remaining_balance})."
        )

    # 3. Create Append-Only Payment
    payment = Payment(
        institute_id=institute_id,
        branch_id=installment.branch_id,
        installment_id=installment.id,
        amount=round(payload.amount, 2),
        payment_method=payload.payment_method,
        transaction_reference=payload.transaction_reference,
        idempotency_key=payload.idempotency_key,
        paid_at=datetime.now(timezone.utc),
        recorded_by=recorder_user_id,
    )
    db.add(payment)
    await db.flush()

    # 4. Update Installment status and paid_amount
    new_paid = round(installment.paid_amount + payment.amount, 2)
    installment.paid_amount = new_paid
    if new_paid >= installment.amount:
        installment.status = InstallmentStatus.PAID
    else:
        installment.status = InstallmentStatus.DUE if installment.due_date <= Date.today() else InstallmentStatus.UPCOMING

    # 5. Issue Receipt
    receipt_num = f"RCP-{datetime.now(timezone.utc).strftime('%Y%m')}-{uuid.uuid4().hex[:6].upper()}"
    receipt = Receipt(
        institute_id=institute_id,
        branch_id=installment.branch_id,
        payment_id=payment.id,
        receipt_number=receipt_num,
        issued_at=datetime.now(timezone.utc),
    )
    db.add(receipt)
    await db.flush()

    # Refresh payment with relationships
    await db.refresh(payment)
    await db.refresh(receipt)

    # 6. Audit Trail
    recorder = await db.get(User, recorder_user_id)
    if recorder:
        await audit_service.log(
            db=db,
            actor=recorder,
            action="payment.recorded",
            entity_name="payments",
            entity_id=str(payment.id),
            old_values=None,
            new_values={
                "installment_id": str(installment.id),
                "amount": payment.amount,
                "payment_method": payment.payment_method.value,
                "receipt_number": receipt_num,
            },
            request=request,
            institute_id=institute_id,
        )

    logger.info(
        "Recorded payment",
        extra={"payment_id": str(payment.id), "receipt_number": receipt_num, "amount": payment.amount},
    )
    return payment


async def get_payment(
    db: AsyncSession,
    *,
    institute_id: uuid.UUID,
    payment_id: uuid.UUID,
    for_student_or_parent: bool = False,
    student_id: uuid.UUID | None = None,
) -> Payment:
    """Fetch payment details with receipt, adjustments, and installment links."""
    stmt = (
        select(Payment)
        .where(Payment.id == payment_id, Payment.institute_id == institute_id)
        .options(
            selectinload(Payment.receipt),
            selectinload(Payment.adjustments).selectinload(PaymentAdjustment.authorizer),
            joinedload(Payment.installment).joinedload(Installment.fee_plan).joinedload(FeePlan.enrollment),
            joinedload(Payment.recorder),
        )
    )
    payment = (await db.execute(stmt)).scalar_one_or_none()
    if not payment:
        raise NotFoundError(f"Payment {payment_id} not found.")

    if for_student_or_parent:
        inst = payment.installment or await db.get(Installment, payment.installment_id)
        if student_id and inst and inst.fee_plan and inst.fee_plan.enrollment.student_id != student_id:
            raise ForbiddenError("You do not have permission to view this payment.")

    return payment


# ─────────────────────────────────────────────────────────────────────────────
# 3. Payment Adjustments (Append-Only Ledger Corrections)
# ─────────────────────────────────────────────────────────────────────────────

async def record_payment_adjustment(
    db: AsyncSession,
    *,
    institute_id: uuid.UUID,
    authorizer_user_id: uuid.UUID,
    payment_id: uuid.UUID,
    payload: PaymentAdjustmentCreate,
    request: Request | None = None,
) -> PaymentAdjustment:
    """
    Record an append-only correction/reversal/refund for a payment.
    Updates the installment paid amount and reverses status if required.
    """
    payment = await get_payment(db, institute_id=institute_id, payment_id=payment_id)

    # Compute total adjustments previously applied
    prev_adjusted = sum(a.amount for a in payment.adjustments)
    remaining_payable = round(payment.amount - prev_adjusted, 2)
    if round(payload.amount, 2) > remaining_payable:
        raise ValidationError(
            f"Adjustment amount ({payload.amount}) exceeds remaining unadjusted payment amount ({remaining_payable})."
        )

    # Record Adjustment
    adj = PaymentAdjustment(
        institute_id=institute_id,
        branch_id=payment.branch_id,
        payment_id=payment.id,
        adjustment_type=payload.adjustment_type,
        amount=round(payload.amount, 2),
        reason=payload.reason,
        authorized_by=authorizer_user_id,
    )
    db.add(adj)
    await db.flush()

    # Reconcile Installment balance
    installment = payment.installment
    if not installment:
        installment = await db.get(Installment, payment.installment_id)
    if not installment:
        raise NotFoundError(f"Installment {payment.installment_id} not found.")

    new_paid = max(0.0, round(installment.paid_amount - payload.amount, 2))
    installment.paid_amount = new_paid
    if new_paid < installment.amount:
        installment.status = (
            InstallmentStatus.OVERDUE if installment.due_date < Date.today() else InstallmentStatus.DUE
        )

    await db.flush()
    await db.refresh(adj)

    # Audit Trail
    authorizer = await db.get(User, authorizer_user_id)
    if authorizer:
        await audit_service.log(
            db=db,
            actor=authorizer,
            action="payment.adjusted",
            entity_name="payment_adjustments",
            entity_id=str(adj.id),
            old_values={"payment_amount": payment.amount, "installment_paid": installment.paid_amount + payload.amount},
            new_values={
                "payment_id": str(payment.id),
                "adjustment_type": payload.adjustment_type.value,
                "adjusted_amount": payload.amount,
                "new_installment_paid": new_paid,
            },
            request=request,
            institute_id=institute_id,
        )

    logger.info(
        "Applied payment adjustment",
        extra={"adjustment_id": str(adj.id), "payment_id": str(payment.id), "type": payload.adjustment_type.value},
    )
    return adj


# ─────────────────────────────────────────────────────────────────────────────
# 4. Receipts & Student Fee Summary
# ─────────────────────────────────────────────────────────────────────────────

async def get_receipt_by_number(
    db: AsyncSession,
    *,
    institute_id: uuid.UUID,
    receipt_number: str,
    for_student_or_parent: bool = False,
    student_id: uuid.UUID | None = None,
) -> Receipt:
    """Fetch receipt by its human-readable receipt number."""
    stmt = (
        select(Receipt)
        .where(Receipt.receipt_number == receipt_number, Receipt.institute_id == institute_id)
        .options(
            selectinload(Receipt.payment).selectinload(Payment.installment).selectinload(Installment.fee_plan).selectinload(FeePlan.enrollment),
            selectinload(Receipt.payment).selectinload(Payment.recorder),
        )
    )
    receipt = (await db.execute(stmt)).scalar_one_or_none()
    if not receipt:
        raise NotFoundError(f"Receipt '{receipt_number}' not found.")

    if for_student_or_parent:
        if student_id and receipt.payment.installment.fee_plan.enrollment.student_id != student_id:
            raise ForbiddenError("You do not have permission to view this receipt.")

    return receipt


async def get_student_fee_summary(
    db: AsyncSession,
    *,
    institute_id: uuid.UUID,
    student_id: uuid.UUID,
) -> dict[str, Any]:
    """Compute aggregate student financial summary across all active enrollments."""
    # 1. Fetch Student Profile
    s_stmt = select(StudentProfile).where(
        StudentProfile.id == student_id,
        StudentProfile.institute_id == institute_id,
    )
    student = (await db.execute(s_stmt)).scalar_one_or_none()
    if not student:
        raise NotFoundError(f"Student {student_id} not found.")

    # 2. Fetch all enrollments with fee plans
    e_stmt = (
        select(Enrollment)
        .where(
            Enrollment.student_id == student_id,
            Enrollment.institute_id == institute_id,
            Enrollment.status != EnrollmentStatus.CANCELLED,
        )
        .options(
            selectinload(Enrollment.batch),
            selectinload(Enrollment.batch),
        )
    )
    enrollments = (await db.execute(e_stmt)).scalars().all()
    enrollment_ids = [e.id for e in enrollments]

    plans_stmt = (
        select(FeePlan)
        .where(
            FeePlan.enrollment_id.in_(enrollment_ids),
            FeePlan.institute_id == institute_id,
            FeePlan.deleted_at.is_(None),
        )
        .options(
            selectinload(FeePlan.enrollment).selectinload(Enrollment.student),
            selectinload(FeePlan.enrollment).selectinload(Enrollment.batch),
            selectinload(FeePlan.installments).selectinload(Installment.payments),
        )
    )
    plans = (await db.execute(plans_stmt)).scalars().all() if enrollment_ids else []

    total_fee = sum(p.net_amount for p in plans)
    total_paid = sum(inst.paid_amount for p in plans for inst in p.installments)
    total_outstanding = max(0.0, round(total_fee - total_paid, 2))

    # Find earliest upcoming or due installment with balance
    unpaid_installments = [
        inst for p in plans for inst in p.installments if inst.status != InstallmentStatus.PAID and inst.amount > inst.paid_amount
    ]
    unpaid_installments.sort(key=lambda x: x.due_date)
    next_due = unpaid_installments[0] if unpaid_installments else None

    student_name = f"{student.first_name} {student.last_name or ''}".strip()

    return {
        "student_id": student.id,
        "student_name": student_name,
        "admission_number": student.admission_number,
        "total_fee": round(total_fee, 2),
        "total_paid": round(total_paid, 2),
        "total_outstanding": round(total_outstanding, 2),
        "plans": plans,
        "next_due_installment": next_due,
    }


# ─────────────────────────────────────────────────────────────────────────────
# 5. Razorpay Online Payments
# ─────────────────────────────────────────────────────────────────────────────

async def _load_installment_for_online_payment(
    db: AsyncSession,
    *,
    institute_id: uuid.UUID,
    installment_id: uuid.UUID,
    student_id: uuid.UUID | None,
) -> Installment:
    """
    Load an installment and enforce ownership when a student/parent is paying
    their own fee (student_id given). Staff callers pass student_id=None.
    """
    inst_stmt = (
        select(Installment)
        .where(
            Installment.id == installment_id,
            Installment.institute_id == institute_id,
            Installment.deleted_at.is_(None),
        )
        .options(selectinload(Installment.fee_plan).selectinload(FeePlan.enrollment))
    )
    installment = (await db.execute(inst_stmt)).scalar_one_or_none()
    if not installment:
        raise NotFoundError(f"Installment {installment_id} not found.")

    if student_id is not None:
        enrollment = installment.fee_plan.enrollment if installment.fee_plan else None
        if not enrollment or enrollment.student_id != student_id:
            raise ForbiddenError("You do not have permission to pay this installment.")

    if installment.status == InstallmentStatus.PAID:
        raise ConflictError(f"Installment {installment.installment_number} has already been fully paid.")

    return installment


async def create_razorpay_order(
    db: AsyncSession,
    *,
    institute_id: uuid.UUID,
    initiator_user_id: uuid.UUID,
    payload: RazorpayOrderCreateRequest,
    student_id: uuid.UUID | None,
) -> tuple[RazorpayOrder, Installment]:
    """
    Create a Razorpay Order for the remaining balance of an installment.
    The amount is always computed server-side — never trust a client-supplied amount.
    """
    installment = await _load_installment_for_online_payment(
        db, institute_id=institute_id, installment_id=payload.installment_id, student_id=student_id
    )

    remaining_balance = round(installment.amount - installment.paid_amount, 2)
    if remaining_balance <= 0:
        raise ValidationError("This installment has no remaining balance to pay.")

    order = razorpay_service.create_order(
        amount_rupees=remaining_balance,
        receipt=f"inst-{installment.id}",
        notes={
            "institute_id": str(institute_id),
            "installment_id": str(installment.id),
            "fee_plan_id": str(installment.fee_plan_id),
        },
    )

    razorpay_order = RazorpayOrder(
        institute_id=institute_id,
        branch_id=installment.branch_id,
        installment_id=installment.id,
        razorpay_order_id=order["id"],
        amount=remaining_balance,
        status=RazorpayOrderStatus.CREATED,
        initiated_by=initiator_user_id,
    )
    db.add(razorpay_order)
    await db.flush()
    await db.refresh(razorpay_order)

    logger.info(
        "Created Razorpay order for installment",
        extra={"razorpay_order_id": order["id"], "installment_id": str(installment.id), "amount": remaining_balance},
    )
    return razorpay_order, installment


async def confirm_razorpay_payment(
    db: AsyncSession,
    *,
    institute_id: uuid.UUID,
    razorpay_order_id: str,
    razorpay_payment_id: str,
    razorpay_signature: str | None,
    request: Request | None = None,
) -> Payment:
    """
    Settle a Razorpay order into the append-only Payment ledger.
    Idempotent: safe to call twice for the same razorpay_payment_id (e.g. once
    from the client-side /verify call and once from the webhook) — the second
    call just returns the already-recorded payment.
    """
    ro_stmt = select(RazorpayOrder).where(
        RazorpayOrder.razorpay_order_id == razorpay_order_id,
        RazorpayOrder.institute_id == institute_id,
    )
    razorpay_order = (await db.execute(ro_stmt)).scalar_one_or_none()
    if not razorpay_order:
        raise NotFoundError(f"Razorpay order {razorpay_order_id} not found.")

    if razorpay_order.status == RazorpayOrderStatus.PAID and razorpay_order.payment_id:
        existing = await db.get(
            Payment,
            razorpay_order.payment_id,
            options=[
                selectinload(Payment.receipt),
                selectinload(Payment.adjustments),
                selectinload(Payment.recorder),
            ],
        )
        if existing:
            logger.info(
                "Razorpay order already settled — returning existing payment",
                extra={"razorpay_order_id": razorpay_order_id, "payment_id": str(existing.id)},
            )
            return existing

    if razorpay_signature is not None:
        valid = razorpay_service.verify_checkout_signature(
            razorpay_order_id=razorpay_order_id,
            razorpay_payment_id=razorpay_payment_id,
            razorpay_signature=razorpay_signature,
        )
        if not valid:
            razorpay_order.status = RazorpayOrderStatus.FAILED
            await db.flush()
            raise ValidationError("Razorpay signature verification failed.")

    installment = await db.get(Installment, razorpay_order.installment_id)
    if not installment:
        raise NotFoundError(f"Installment {razorpay_order.installment_id} not found.")
    if installment.status == InstallmentStatus.PAID:
        raise ConflictError(f"Installment {installment.installment_number} has already been fully paid.")

    payment_req = PaymentRecordRequest(
        installment_id=installment.id,
        amount=razorpay_order.amount,
        payment_method=PaymentMethod.ONLINE,
        transaction_reference=razorpay_payment_id,
        idempotency_key=f"razorpay:{razorpay_payment_id}",
    )
    payment = await record_payment(
        db=db,
        institute_id=institute_id,
        recorder_user_id=razorpay_order.initiated_by,
        payload=payment_req,
        request=request,
    )
    payment.razorpay_order_id = razorpay_order_id
    payment.razorpay_payment_id = razorpay_payment_id
    payment.razorpay_signature = razorpay_signature

    razorpay_order.status = RazorpayOrderStatus.PAID
    razorpay_order.payment_id = payment.id
    await db.flush()
    await db.refresh(payment)

    logger.info(
        "Settled Razorpay payment",
        extra={"razorpay_order_id": razorpay_order_id, "payment_id": str(payment.id)},
    )
    return payment
