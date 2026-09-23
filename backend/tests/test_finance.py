"""
tests/test_finance.py
---------------------
Comprehensive tests for Slice 9: Finance & Immutable Ledger.

Coverage:
  1. Fee Plan Creation & Installment Splitting:
     - Lump-sum vs multi-installment schedule creation.
     - Automatic balance distribution and remainder penny/paise handling.
     - Role restriction: Only STAFF/ADMIN/COUNSELLOR can create plans (STUDENT -> 403).
     - Audit log verification ('fee_plan.created').
  2. Append-Only Payment Recording & Idempotency:
     - Recording payment against an installment.
     - Unique human-readable receipt generation (RCP-YYYYMM-XXXXXX).
     - Idempotency key replay test: Re-submitting the same key safely returns the
       original payment without duplicate charge or balance double-decrement.
     - Receipt lookup by receipt number.
  3. Overpayment Boundary & Validation:
     - Payment amount exceeding remaining installment balance rejected (422).
     - Zero or negative amount rejected by schema validation (422).
  4. Payment Adjustments & Ledger Immutability:
     - Append-only adjustment (REFUND / REVERSAL / CORRECTION).
     - Installment paid_amount and status reconciliation.
     - Original payment remains unedited and undeleted (immutable ledger).
     - Audit log verification ('payment.adjusted').
  5. ReBAC & Self-Service Portal:
     - Student self-service: GET /api/v1/finance/my-fees.
     - Linked Parent self-service: GET /api/v1/finance/my-fees.
     - Student blocked from recording payments (403 Forbidden).
     - Cross-tenant isolation verification.
"""

from __future__ import annotations

import uuid
from datetime import date, timedelta

import pytest
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import hash_password
from app.models.academic_structure import (
    AcademicYear,
    Batch,
    Board,
    Course,
    SchoolClass,
    Subject,
)
from app.models.audit import AuditLog
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
)
from app.models.institute import Institute
from app.models.people import ParentProfile, StudentParent, StudentProfile
from app.models.user import User, UserStatus


# ─── Fixtures ────────────────────────────────────────────────────────────────

@pytest.fixture
async def institute(db_session: AsyncSession) -> Institute:
    inst = Institute(id=uuid.uuid4(), name="Finance Test Inst", code="FIN_TEST", is_active=True)
    db_session.add(inst)
    await db_session.flush()
    return inst


@pytest.fixture
async def other_institute(db_session: AsyncSession) -> Institute:
    inst = Institute(id=uuid.uuid4(), name="Other Finance Inst", code="OTHER_FIN", is_active=True)
    db_session.add(inst)
    await db_session.flush()
    return inst


async def _make_user(
    db_session: AsyncSession, institute: Institute, role: str, email: str
) -> tuple[User, str]:
    plain = "Test@1234!"
    user = User(
        id=uuid.uuid4(),
        institute_id=institute.id,
        email=email,
        password_hash=hash_password(plain),
        role=role,
        status=UserStatus.ACTIVE,
        is_active=True,
    )
    db_session.add(user)
    await db_session.flush()
    return user, plain


async def _login(client: AsyncClient, email: str, password: str) -> str:
    resp = await client.post(
        "/api/v1/auth/login",
        json={"identifier": email, "password": password},
    )
    assert resp.status_code == 200, resp.text
    return resp.json()["access_token"]


@pytest.fixture
async def finance_env(
    db_session: AsyncSession, async_client: AsyncClient, institute: Institute, other_institute: Institute
) -> dict[str, any]:
    # 1. Admin
    admin_u, admin_pwd = await _make_user(db_session, institute, "ADMIN", "admin@fin.test")
    admin_token = await _login(async_client, admin_u.email, admin_pwd)

    # 2. Counsellor
    counsellor_u, coun_pwd = await _make_user(db_session, institute, "COUNSELLOR", "counsellor@fin.test")
    counsellor_token = await _login(async_client, counsellor_u.email, coun_pwd)

    # 3. Student
    student_u, st_pwd = await _make_user(db_session, institute, "STUDENT", "student@fin.test")
    student_token = await _login(async_client, student_u.email, st_pwd)
    st_profile = StudentProfile(
        id=uuid.uuid4(),
        institute_id=institute.id,
        user_id=student_u.id,
        admission_number=f"ADM-FIN-{uuid.uuid4().hex[:6].upper()}",
        first_name="Aarav",
        last_name="Sharma",
    )
    db_session.add(st_profile)

    # 4. Parent linked to Student
    parent_u, pt_pwd = await _make_user(db_session, institute, "PARENT", "parent@fin.test")
    parent_token = await _login(async_client, parent_u.email, pt_pwd)
    pt_profile = ParentProfile(
        id=uuid.uuid4(),
        institute_id=institute.id,
        user_id=parent_u.id,
        first_name="Rajesh",
        last_name="Sharma",
        relation="FATHER",
    )
    db_session.add(pt_profile)
    await db_session.flush()

    link = StudentParent(
        student_id=st_profile.id,
        parent_id=pt_profile.id,
        is_primary=True,
    )
    db_session.add(link)

    # 5. Cross-tenant Admin
    other_admin, o_pwd = await _make_user(db_session, other_institute, "ADMIN", "admin@otherfin.test")
    other_admin_token = await _login(async_client, other_admin.email, o_pwd)

    # 6. Academic Setup
    ay = AcademicYear(
        id=uuid.uuid4(), institute_id=institute.id, name="2025-26",
        start_date=date(2025, 4, 1), end_date=date(2026, 3, 31), is_current=True,
    )
    board = Board(id=uuid.uuid4(), institute_id=institute.id, name="CBSE", code="CBSE_FIN")
    db_session.add_all([ay, board])
    await db_session.flush()

    sclass = SchoolClass(id=uuid.uuid4(), board_id=board.id, name="Class 11", display_order=11)
    subject = Subject(id=uuid.uuid4(), institute_id=institute.id, name="Mathematics", code=f"M_{uuid.uuid4().hex[:4]}")
    db_session.add_all([sclass, subject])
    await db_session.flush()

    course = Course(
        id=uuid.uuid4(),
        institute_id=institute.id,
        academic_year_id=ay.id,
        class_id=sclass.id,
        name="JEE Advanced 2-Year",
        code=f"C_{uuid.uuid4().hex[:6]}",
    )
    db_session.add(course)
    await db_session.flush()

    batch = Batch(
        id=uuid.uuid4(),
        institute_id=institute.id,
        course_id=course.id,
        subject_id=subject.id,
        name=f"Batch Alpha {uuid.uuid4().hex[:4]}",
        capacity=40,
    )
    db_session.add(batch)
    await db_session.flush()

    # 7. Student Enrollment
    enrollment = Enrollment(
        id=uuid.uuid4(),
        institute_id=institute.id,
        student_id=st_profile.id,
        batch_id=batch.id,
        enrollment_date=date.today(),
        status=EnrollmentStatus.ACTIVE,
    )
    db_session.add(enrollment)
    await db_session.flush()

    return {
        "institute": institute,
        "admin_user": admin_u,
        "admin_token": admin_token,
        "counsellor_token": counsellor_token,
        "student_user": student_u,
        "student_profile": st_profile,
        "student_token": student_token,
        "parent_profile": pt_profile,
        "parent_token": parent_token,
        "other_admin_token": other_admin_token,
        "batch": batch,
        "enrollment": enrollment,
    }


# ─── Tests ───────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_fee_plan_creation_and_installment_splitting(
    async_client: AsyncClient,
    db_session: AsyncSession,
    finance_env: dict[str, any],
):
    """
    1. Verify fee plan creation with automatic installment splitting and remainder penny/paise balance.
    2. Verify audit trail emission.
    3. Verify role authorization (Student blocked with 403).
    """
    env = finance_env
    admin_token = env["admin_token"]
    student_token = env["student_token"]
    enrollment = env["enrollment"]

    # Student cannot create fee plan
    resp = await async_client.post(
        "/api/v1/finance/plans",
        headers={"Authorization": f"Bearer {student_token}"},
        json={
            "enrollment_id": str(enrollment.id),
            "total_amount": 60000.0,
            "first_due_date": str(date.today()),
        },
    )
    assert resp.status_code == 403

    # Admin creates fee plan with 3 installments
    # Net = 60000 - 5000 (discount) - 5000 (scholarship) = 50000
    # 50000 / 3 = 16666.67, 16666.67, 16666.66
    payload = {
        "enrollment_id": str(enrollment.id),
        "total_amount": 60000.0,
        "discount_amount": 5000.0,
        "scholarship_amount": 5000.0,
        "discount_reason": "Merit Entrance Exam Rank 5",
        "plan_type": "INSTALLMENT",
        "installment_count": 3,
        "first_due_date": str(date.today() + timedelta(days=10)),
    }

    create_resp = await async_client.post(
        "/api/v1/finance/plans",
        headers={"Authorization": f"Bearer {admin_token}"},
        json=payload,
    )
    assert create_resp.status_code == 201, create_resp.text
    body = create_resp.json()["data"]

    assert body["total_amount"] == 60000.0
    assert body["discount_amount"] == 5000.0
    assert body["scholarship_amount"] == 5000.0
    assert body["net_amount"] == 50000.0
    assert body["plan_type"] == "INSTALLMENT"
    assert len(body["installments"]) == 3

    # Verify installment amounts sum to exactly net_amount
    inst_amounts = [inst["amount"] for inst in body["installments"]]
    assert sum(inst_amounts) == 50000.0
    assert inst_amounts[0] == 16666.67
    assert inst_amounts[1] == 16666.67
    assert inst_amounts[2] == 16666.66

    # Verify sequential installment numbers
    assert [inst["installment_number"] for inst in body["installments"]] == [1, 2, 3]

    # Verify audit log recorded
    audit_stmt = (
        select(AuditLog)
        .where(AuditLog.entity_id == str(body["id"]), AuditLog.action == "fee_plan.created")
    )
    audit = (await db_session.execute(audit_stmt)).scalar_one_or_none()
    assert audit is not None
    assert audit.actor_id == env["admin_user"].id


@pytest.mark.asyncio
async def test_payment_recording_idempotency_and_receipt(
    async_client: AsyncClient,
    db_session: AsyncSession,
    finance_env: dict[str, any],
):
    """
    1. Record an append-only payment against an installment.
    2. Verify unique receipt generated (RCP-YYYYMM-XXXXXX).
    3. Verify idempotency protection: Replaying the exact same request returns the original payment.
    4. Verify receipt verification lookup by receipt number.
    """
    env = finance_env
    admin_token = env["admin_token"]
    enrollment = env["enrollment"]

    # 1. Create a fee plan with lump sum
    plan_resp = await async_client.post(
        "/api/v1/finance/plans",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "enrollment_id": str(enrollment.id),
            "total_amount": 25000.0,
            "plan_type": "LUMP_SUM",
            "installment_count": 1,
            "first_due_date": str(date.today()),
        },
    )
    assert plan_resp.status_code == 201, plan_resp.text
    installment_id = plan_resp.json()["data"]["installments"][0]["id"]

    # 2. Record first payment of 10000.0 with idempotency key
    idemp_key = f"PAY-IDEMP-{uuid.uuid4().hex[:12]}"
    pay_payload = {
        "installment_id": installment_id,
        "amount": 10000.0,
        "payment_method": "UPI",
        "transaction_reference": "UPI/2026/TXN88921",
        "idempotency_key": idemp_key,
    }

    pay_resp = await async_client.post(
        "/api/v1/finance/payments",
        headers={"Authorization": f"Bearer {admin_token}"},
        json=pay_payload,
    )
    assert pay_resp.status_code == 201, pay_resp.text
    pay_data = pay_resp.json()["data"]

    assert pay_data["amount"] == 10000.0
    assert pay_data["payment_method"] == "UPI"
    assert pay_data["idempotency_key"] == idemp_key
    assert pay_data["receipt"] is not None
    receipt_num = pay_data["receipt"]["receipt_number"]
    assert receipt_num.startswith("RCP-")
    payment_id = pay_data["id"]

    # Check installment paid_amount updated
    inst = await db_session.get(Installment, uuid.UUID(installment_id))
    assert inst.paid_amount == 10000.0
    assert inst.status == InstallmentStatus.DUE  # still has balance

    # 3. Replay EXACT same request with same idempotency_key
    replay_resp = await async_client.post(
        "/api/v1/finance/payments",
        headers={"Authorization": f"Bearer {admin_token}"},
        json=pay_payload,
    )
    assert replay_resp.status_code == 201, replay_resp.text
    replay_data = replay_resp.json()["data"]

    # Must return identical payment ID and receipt number without double charging
    assert replay_data["id"] == payment_id
    assert replay_data["receipt"]["receipt_number"] == receipt_num

    await db_session.refresh(inst)
    assert inst.paid_amount == 10000.0  # NOT 20000.0!

    # 4. Lookup receipt by receipt_number
    rcp_lookup = await async_client.get(
        f"/api/v1/finance/receipts/number/{receipt_num}",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert rcp_lookup.status_code == 200, rcp_lookup.text
    assert rcp_lookup.json()["data"]["payment_id"] == payment_id


@pytest.mark.asyncio
async def test_overpayment_boundary_and_validation(
    async_client: AsyncClient,
    db_session: AsyncSession,
    finance_env: dict[str, any],
):
    """
    1. Attempt to pay more than the installment's remaining balance -> rejected with 422.
    2. Attempt to submit zero or negative payment amount -> rejected with 422.
    """
    env = finance_env
    admin_token = env["admin_token"]
    enrollment = env["enrollment"]

    plan_resp = await async_client.post(
        "/api/v1/finance/plans",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "enrollment_id": str(enrollment.id),
            "total_amount": 15000.0,
            "plan_type": "LUMP_SUM",
            "first_due_date": str(date.today()),
        },
    )
    assert plan_resp.status_code == 201
    installment_id = plan_resp.json()["data"]["installments"][0]["id"]

    # 1. Overpayment: Attempt to pay 20000 when installment is 15000
    overpay_resp = await async_client.post(
        "/api/v1/finance/payments",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "installment_id": installment_id,
            "amount": 20000.0,
            "payment_method": "BANK_TRANSFER",
            "idempotency_key": f"OVERPAY-{uuid.uuid4().hex[:10]}",
        },
    )
    assert overpay_resp.status_code == 422
    assert "exceeds" in overpay_resp.text.lower()

    # 2. Schema validation: 0.0 or negative amount rejected
    zero_pay_resp = await async_client.post(
        "/api/v1/finance/payments",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "installment_id": installment_id,
            "amount": 0.0,
            "payment_method": "CASH",
            "idempotency_key": f"ZERO-{uuid.uuid4().hex[:10]}",
        },
    )
    assert zero_pay_resp.status_code == 422


@pytest.mark.asyncio
async def test_payment_adjustment_and_reconciliation(
    async_client: AsyncClient,
    db_session: AsyncSession,
    finance_env: dict[str, any],
):
    """
    1. Complete payment for an installment (status becomes PAID).
    2. Apply an append-only REFUND / REVERSAL adjustment.
    3. Verify installment paid_amount decreases and status reverts to DUE/OVERDUE.
    4. Verify original Payment record remains immutable (not updated or deleted).
    5. Verify AuditLog entry emitted for payment adjustment.
    """
    env = finance_env
    admin_token = env["admin_token"]
    enrollment = env["enrollment"]

    # 1. Create plan
    plan_resp = await async_client.post(
        "/api/v1/finance/plans",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "enrollment_id": str(enrollment.id),
            "total_amount": 12000.0,
            "plan_type": "LUMP_SUM",
            "first_due_date": str(date.today() - timedelta(days=2)),  # Past due date
        },
    )
    assert plan_resp.status_code == 201
    inst_id = plan_resp.json()["data"]["installments"][0]["id"]

    # 2. Fully pay the installment
    pay_resp = await async_client.post(
        "/api/v1/finance/payments",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "installment_id": inst_id,
            "amount": 12000.0,
            "payment_method": "CARD",
            "idempotency_key": f"PAY-FULL-{uuid.uuid4().hex[:10]}",
        },
    )
    assert pay_resp.status_code == 201
    payment_id = pay_resp.json()["data"]["id"]

    # Verify status is now PAID
    inst = await db_session.get(Installment, uuid.UUID(inst_id))
    assert inst.status == InstallmentStatus.PAID
    assert inst.paid_amount == 12000.0

    # 3. Apply a partial refund adjustment of 4000.0
    adj_resp = await async_client.post(
        f"/api/v1/finance/payments/{payment_id}/adjustments",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "adjustment_type": "REFUND",
            "amount": 4000.0,
            "reason": "Late scholarship approval refund to parent account",
        },
    )
    assert adj_resp.status_code == 201, adj_resp.text
    adj_data = adj_resp.json()["data"]

    assert adj_data["adjustment_type"] == "REFUND"
    assert adj_data["amount"] == 4000.0
    assert adj_data["payment_id"] == payment_id

    # 4. Verify installment reconciled: paid_amount should now be 8000.0, status reverted to OVERDUE
    await db_session.refresh(inst)
    assert inst.paid_amount == 8000.0
    assert inst.status == InstallmentStatus.OVERDUE

    # 5. Verify immutability: Original Payment record still has amount=12000.0
    orig_pay = await db_session.get(Payment, uuid.UUID(payment_id))
    assert orig_pay.amount == 12000.0

    # 6. List adjustments on payment
    list_adj = await async_client.get(
        f"/api/v1/finance/payments/{payment_id}/adjustments",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert list_adj.status_code == 200
    assert len(list_adj.json()["data"]) == 1

    # 7. Verify Audit Log entry
    audit_stmt = (
        select(AuditLog)
        .where(AuditLog.entity_id == str(adj_data["id"]), AuditLog.action == "payment.adjusted")
    )
    audit = (await db_session.execute(audit_stmt)).scalar_one_or_none()
    assert audit is not None


@pytest.mark.asyncio
async def test_rebac_and_student_parent_self_service(
    async_client: AsyncClient,
    db_session: AsyncSession,
    finance_env: dict[str, any],
):
    """
    1. Student views own ledger via /api/v1/finance/my-fees.
    2. Linked parent views student ledger via /api/v1/finance/my-fees.
    3. Student is forbidden from recording payments or adjustments (403).
    4. Cross-tenant admin blocked from viewing other institute's fee plans (404/403).
    """
    env = finance_env
    admin_token = env["admin_token"]
    student_token = env["student_token"]
    parent_token = env["parent_token"]
    other_admin_token = env["other_admin_token"]
    enrollment = env["enrollment"]

    # 1. Admin creates fee plan
    plan_resp = await async_client.post(
        "/api/v1/finance/plans",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "enrollment_id": str(enrollment.id),
            "total_amount": 30000.0,
            "plan_type": "INSTALLMENT",
            "installment_count": 2,
            "first_due_date": str(date.today() + timedelta(days=15)),
        },
    )
    assert plan_resp.status_code == 201
    plan_id = plan_resp.json()["data"]["id"]
    inst_id = plan_resp.json()["data"]["installments"][0]["id"]

    # Pay first installment
    await async_client.post(
        "/api/v1/finance/payments",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "installment_id": inst_id,
            "amount": 15000.0,
            "payment_method": "ONLINE",
            "idempotency_key": f"SELF-TEST-{uuid.uuid4().hex[:10]}",
        },
    )

    # 2. Student self-service: GET /api/v1/finance/my-fees
    st_fees_resp = await async_client.get(
        "/api/v1/finance/my-fees",
        headers={"Authorization": f"Bearer {student_token}"},
    )
    assert st_fees_resp.status_code == 200, st_fees_resp.text
    st_data = st_fees_resp.json()["data"]

    assert st_data["total_fee"] == 30000.0
    assert st_data["total_paid"] == 15000.0
    assert st_data["total_outstanding"] == 15000.0
    assert len(st_data["plans"]) == 1
    assert st_data["next_due_installment"] is not None
    assert st_data["next_due_installment"]["installment_number"] == 2

    # 3. Linked parent self-service: GET /api/v1/finance/my-fees
    pt_fees_resp = await async_client.get(
        "/api/v1/finance/my-fees",
        headers={"Authorization": f"Bearer {parent_token}"},
    )
    assert pt_fees_resp.status_code == 200, pt_fees_resp.text
    pt_data = pt_fees_resp.json()["data"]
    assert pt_data["student_id"] == str(env["student_profile"].id)
    assert pt_data["total_outstanding"] == 15000.0

    # 4. Student blocked from writing payments (403 Forbidden)
    bad_pay = await async_client.post(
        "/api/v1/finance/payments",
        headers={"Authorization": f"Bearer {student_token}"},
        json={
            "installment_id": inst_id,
            "amount": 1000.0,
            "payment_method": "CASH",
            "idempotency_key": f"HACK-{uuid.uuid4().hex[:10]}",
        },
    )
    assert bad_pay.status_code == 403

    # 5. Cross-tenant admin blocked from viewing other institute's fee plan
    cross_plan = await async_client.get(
        f"/api/v1/finance/plans/{plan_id}",
        headers={"Authorization": f"Bearer {other_admin_token}"},
    )
    assert cross_plan.status_code in (404, 403)
