"""
tests/test_analytics.py
-----------------------
Comprehensive test suite for Slice 11: Reports & Analytics.

Tests:
  1. Executive Dashboard KPIs & Security:
     - Admin fetches KPI summary cards, trends, financial balances.
     - Non-administrative role is rejected with 403 Forbidden.
  2. Student 360° Comprehensive Profile & ReBAC Protection:
     - Single-trip aggregation of demographics, batch enrollments, attendance %,
       exam results, fee balance, receipts, homework, and teacher remarks.
     - Student A can view own profile (and via /my-360).
     - Verified Parent A can view Student A's profile.
     - Assigned Teacher 1 can view Student A's profile.
     - Student B is rejected with 403 Forbidden when attempting to view Student A.
     - Unassigned Teacher 2 is rejected with 403 Forbidden.
  3. Batch Analytics & Materialized View Refresh:
     - Detailed batch performance metrics (sessions, attendance %, tests, avg score, low attendance count).
     - ReBAC: Teacher assigned to batch can view; unassigned teacher receives 403.
     - Admin triggers POST /analytics/refresh to refresh PostgreSQL Materialized Views.
  4. Financial & Attendance Analytics:
     - Fee collections and payment method breakdown (UPI).
     - Attendance distribution (PRESENT, ABSENT) and low attendance alert (< 75%).
  5. CSV Data Streaming Exports:
     - Streaming CSV download for students roster, fee ledger, attendance, and exam marks.
"""

from __future__ import annotations

import uuid
from datetime import date, datetime, timedelta, timezone

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import hash_password
from app.models.academic_operations import (
    Attendance,
    AttendanceStatus,
    ClassSession,
    ClassSessionStatus,
    StudentRemark,
)
from app.models.academic_structure import (
    AcademicYear,
    Batch,
    Board,
    Course,
    SchoolClass,
    Subject,
)
from app.models.enrollment import Enrollment, EnrollmentStatus
from app.models.examination import (
    Test as ExamTest,
    TestQuestion as ExamTestQuestion,
    TestResult as ExamTestResult,
    TestStatus as ExamTestStatus,
    TestType as ExamTestType,
)
from app.models.finance import (
    FeePlan,
    FeePlanType,
    Installment,
    InstallmentStatus,
    Payment,
    PaymentMethod,
    Receipt,
)
from app.models.institute import Institute
from app.models.learning import Homework, HomeworkSubmission, SubmissionStatus
from app.models.people import ParentProfile, StudentParent, StudentProfile, TeacherProfile
from app.models.user import User, UserStatus


async def _make_user(
    db: AsyncSession,
    institute_id: uuid.UUID,
    role: str,
    email: str,
) -> tuple[User, str]:
    user = User(
        id=uuid.uuid4(),
        institute_id=institute_id,
        email=email,
        password_hash=hash_password("AnalyticsPass123!"),
        role=role,
        status=UserStatus.ACTIVE,
        is_active=True,
        is_verified=True,
    )
    db.add(user)
    await db.flush()
    await db.refresh(user)

    from app.core.security import create_access_token
    token, _, _ = create_access_token(str(user.id), user.role)
    return user, token


@pytest.fixture
async def analytics_env(db_session: AsyncSession) -> dict[str, any]:
    """Sets up an institute with batches, students, attendances, exams, fees, and homework."""
    db = db_session
    inst = Institute(
        id=uuid.uuid4(),
        name="Analytics Test Institute",
        code=f"ANL_{uuid.uuid4().hex[:6].upper()}",
        is_active=True,
    )
    db.add(inst)
    await db.flush()

    # 1. Users
    admin_user, admin_token = await _make_user(db, inst.id, "ADMIN", f"admin_{uuid.uuid4().hex[:6]}@test.com")
    t1_user, t1_token = await _make_user(db, inst.id, "TEACHER", f"t1_{uuid.uuid4().hex[:6]}@test.com")
    t2_user, t2_token = await _make_user(db, inst.id, "TEACHER", f"t2_{uuid.uuid4().hex[:6]}@test.com")
    st_a_user, st_a_token = await _make_user(db, inst.id, "STUDENT", f"sta_{uuid.uuid4().hex[:6]}@test.com")
    st_b_user, st_b_token = await _make_user(db, inst.id, "STUDENT", f"stb_{uuid.uuid4().hex[:6]}@test.com")
    pa_user, pa_token = await _make_user(db, inst.id, "PARENT", f"pa_{uuid.uuid4().hex[:6]}@test.com")

    # 2. Profiles
    t1_prof = TeacherProfile(
        id=uuid.uuid4(), institute_id=inst.id, user_id=t1_user.id,
        first_name="Prof", last_name="Alpha", is_active=True
    )
    t2_prof = TeacherProfile(
        id=uuid.uuid4(), institute_id=inst.id, user_id=t2_user.id,
        first_name="Prof", last_name="Beta", is_active=True
    )
    db.add_all([t1_prof, t2_prof])
    await db.flush()

    st_a_prof = StudentProfile(
        id=uuid.uuid4(), institute_id=inst.id, user_id=st_a_user.id,
        first_name="Aarav", last_name="Sharma", admission_number="ADM-A01",
        date_of_birth=date(2008, 5, 14), is_active=True
    )
    st_b_prof = StudentProfile(
        id=uuid.uuid4(), institute_id=inst.id, user_id=st_b_user.id,
        first_name="Bhavin", last_name="Patel", admission_number="ADM-B02",
        date_of_birth=date(2008, 8, 20), is_active=True
    )
    pa_prof = ParentProfile(
        id=uuid.uuid4(), institute_id=inst.id, user_id=pa_user.id,
        first_name="Ramesh", last_name="Sharma", relation="FATHER", is_active=True
    )
    db.add_all([st_a_prof, st_b_prof, pa_prof])
    await db.flush()

    # Link Parent A -> Student A
    sp = StudentParent(id=uuid.uuid4(), student_id=st_a_prof.id, parent_id=pa_prof.id, is_primary=True)
    db.add(sp)

    # 3. Academic Structure
    ay = AcademicYear(id=uuid.uuid4(), institute_id=inst.id, name="2026-27", start_date=date(2026, 4, 1), end_date=date(2027, 3, 31))
    board = Board(id=uuid.uuid4(), institute_id=inst.id, name="CBSE", code=f"CBSE_{uuid.uuid4().hex[:4]}")
    sclass = SchoolClass(id=uuid.uuid4(), board_id=board.id, name="Class 10", display_order=10)
    sub_phy = Subject(id=uuid.uuid4(), institute_id=inst.id, name="Physics", code=f"P_{uuid.uuid4().hex[:4]}")
    db.add_all([ay, board, sclass, sub_phy])
    await db.flush()

    course = Course(
        id=uuid.uuid4(), institute_id=inst.id, academic_year_id=ay.id, class_id=sclass.id,
        name="Class 10 Science", code=f"C10_{uuid.uuid4().hex[:4]}",
    )
    db.add(course)
    await db.flush()

    batch_a = Batch(
        id=uuid.uuid4(), institute_id=inst.id, course_id=course.id, subject_id=sub_phy.id,
        teacher_id=t1_prof.id, name="Batch 10-A", capacity=30, is_active=True
    )
    db.add(batch_a)
    await db.flush()

    # Enrollments
    enr_a = Enrollment(
        id=uuid.uuid4(), institute_id=inst.id, batch_id=batch_a.id,
        student_id=st_a_prof.id, status=EnrollmentStatus.ACTIVE,
        enrollment_date=date(2026, 4, 15),
    )
    enr_b = Enrollment(
        id=uuid.uuid4(), institute_id=inst.id, batch_id=batch_a.id,
        student_id=st_b_prof.id, status=EnrollmentStatus.ACTIVE,
        enrollment_date=date(2026, 4, 15),
    )
    db.add_all([enr_a, enr_b])
    await db.flush()

    # 4. Class Sessions & Attendance (4 sessions)
    today = datetime.now(timezone.utc).date()
    for i in range(4):
        sess = ClassSession(
            id=uuid.uuid4(), institute_id=inst.id, batch_id=batch_a.id,
            date=today - timedelta(days=i),
            start_time="10:00:00", end_time="11:30:00",
            status=ClassSessionStatus.HELD
        )
        db.add(sess)
        await db.flush()

        # Student A: Present in all 4 sessions (100%)
        db.add(Attendance(
            id=uuid.uuid4(), class_session_id=sess.id,
            enrollment_id=enr_a.id, status=AttendanceStatus.PRESENT
        ))

        # Student B: Present in 1st, Absent in other 3 (25% -> low attendance)
        b_status = AttendanceStatus.PRESENT if i == 0 else AttendanceStatus.ABSENT
        db.add(Attendance(
            id=uuid.uuid4(), class_session_id=sess.id,
            enrollment_id=enr_b.id, status=b_status
        ))

    # 5. Examination (1 published test with results)
    test = ExamTest(
        id=uuid.uuid4(), institute_id=inst.id, batch_id=batch_a.id,
        course_id=course.id, subject_id=sub_phy.id,
        name="Physics Term Test 1", type=ExamTestType.UNIT,
        date=today - timedelta(days=2),
        max_marks=100.0, passing_marks=40.0,
        status=ExamTestStatus.PUBLISHED, created_by=t1_user.id,
    )
    db.add(test)
    await db.flush()

    tr_a = ExamTestResult(
        id=uuid.uuid4(), test_id=test.id, student_id=st_a_prof.id,
        marks_obtained=90.0, percentage=90.0, percentile=100.0, rank=1
    )
    tr_b = ExamTestResult(
        id=uuid.uuid4(), test_id=test.id, student_id=st_b_prof.id,
        marks_obtained=50.0, percentage=50.0, percentile=50.0, rank=2
    )
    db.add_all([tr_a, tr_b])

    # 6. Finance: Fee plan, installment, payment, receipt for Student A
    fp = FeePlan(
        id=uuid.uuid4(), institute_id=inst.id, enrollment_id=enr_a.id,
        plan_type=FeePlanType.INSTALLMENT, total_amount=50000.0,
        net_amount=50000.0, created_by=admin_user.id,
    )
    db.add(fp)
    await db.flush()

    inst1 = Installment(
        id=uuid.uuid4(), institute_id=inst.id, fee_plan_id=fp.id, installment_number=1,
        amount=25000.0, paid_amount=25000.0, due_date=today - timedelta(days=10),
        status=InstallmentStatus.PAID,
    )
    inst2 = Installment(
        id=uuid.uuid4(), institute_id=inst.id, fee_plan_id=fp.id, installment_number=2,
        amount=25000.0, paid_amount=0.0, due_date=today + timedelta(days=30),
        status=InstallmentStatus.DUE,
    )
    db.add_all([inst1, inst2])
    await db.flush()

    pay = Payment(
        id=uuid.uuid4(), institute_id=inst.id,
        installment_id=inst1.id, amount=25000.0,
        payment_method=PaymentMethod.UPI,
        transaction_reference="UPI-REF-001",
        idempotency_key="IDEMP-001",
        recorded_by=admin_user.id,
        paid_at=datetime.now(timezone.utc) - timedelta(days=10),
    )
    db.add(pay)
    await db.flush()

    rcp = Receipt(
        id=uuid.uuid4(), institute_id=inst.id, payment_id=pay.id,
        receipt_number="RCP-202609-000001",
    )
    db.add(rcp)

    # 7. Homework & Remark
    hw = Homework(
        id=uuid.uuid4(), institute_id=inst.id, batch_id=batch_a.id,
        subject_id=sub_phy.id,
        title="Optics Problem Set", instructions="Solve Q1 to Q10",
        due_date=today + timedelta(days=5), created_by=t1_user.id,
    )
    db.add(hw)
    await db.flush()

    hw_sub = HomeworkSubmission(
        id=uuid.uuid4(), homework_id=hw.id, student_id=st_a_prof.id,
        submission_text="Attached solution notes", marks=18.0, max_marks=20.0,
        status=SubmissionStatus.REVIEWED,
    )
    db.add(hw_sub)

    rem = StudentRemark(
        id=uuid.uuid4(), institute_id=inst.id, student_id=st_a_prof.id,
        teacher_id=t1_prof.id, body="Consistent academic diligence and exemplary class participation.",
        visible_to_parent=True,
    )
    db.add(rem)
    await db.flush()

    return {
        "institute": inst,
        "admin_token": admin_token,
        "t1_token": t1_token,
        "t2_token": t2_token,
        "st_a_token": st_a_token,
        "st_b_token": st_b_token,
        "pa_token": pa_token,
        "batch_a": batch_a,
        "student_a": st_a_prof,
        "student_b": st_b_prof,
    }


# ─────────────────────────────────────────────────────────────────────────────
# Test 1: Executive Dashboard KPIs
# ─────────────────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_executive_dashboard_kpis(
    async_client: AsyncClient,
    analytics_env: dict[str, any],
):
    env = analytics_env
    admin_token = env["admin_token"]
    st_a_token = env["st_a_token"]

    # 1. Admin accesses dashboard
    resp = await async_client.get(
        "/api/v1/analytics/dashboard",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert resp.status_code == 200, resp.text
    data = resp.json()["data"]

    assert data["total_students"] >= 2
    assert data["total_batches"] >= 1
    assert data["total_teachers"] >= 2
    assert data["total_fees_billed"] >= 50000.0
    assert data["total_fees_collected"] >= 25000.0
    assert data["total_fees_pending"] >= 25000.0
    assert data["overall_attendance_rate"] > 0.0
    assert len(data["attendance_trends_7d"]) == 7

    # 2. Student is blocked (403 Forbidden)
    student_resp = await async_client.get(
        "/api/v1/analytics/dashboard",
        headers={"Authorization": f"Bearer {st_a_token}"},
    )
    assert student_resp.status_code == 403


# ─────────────────────────────────────────────────────────────────────────────
# Test 2: Student 360° Comprehensive Profile & ReBAC
# ─────────────────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_student_360_profile_aggregation_and_rebac(
    async_client: AsyncClient,
    analytics_env: dict[str, any],
):
    env = analytics_env
    admin_token = env["admin_token"]
    st_a_token = env["st_a_token"]
    st_b_token = env["st_b_token"]
    pa_token = env["pa_token"]
    t1_token = env["t1_token"]
    t2_token = env["t2_token"]
    st_a = env["student_a"]

    # 1. Admin retrieves Student A's full 360° profile
    admin_get = await async_client.get(
        f"/api/v1/analytics/students/{st_a.id}/360",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert admin_get.status_code == 200, admin_get.text
    profile = admin_get.json()["data"]

    # Verify demographics & guardians
    assert profile["student_id"] == str(st_a.id)
    assert profile["first_name"] == "Aarav"
    assert len(profile["guardians"]) >= 1
    assert profile["guardians"][0]["relation"] == "FATHER"

    # Verify batches
    assert len(profile["batches"]) >= 1
    assert profile["batches"][0]["batch_name"] == "Batch 10-A"

    # Verify attendance
    assert profile["total_sessions"] == 4
    assert profile["attended_sessions"] == 4
    assert profile["attendance_percentage"] == 100.0
    assert profile["attendance_badge"] == "EXCELLENT"

    # Verify exams
    assert profile["tests_taken"] == 1
    assert profile["average_test_percentage"] == 90.0
    assert len(profile["scorecards"]) == 1
    assert profile["scorecards"][0]["rank"] == 1

    # Verify finances
    assert profile["fee_plan_total"] == 50000.0
    assert profile["total_paid"] == 25000.0
    assert profile["pending_balance"] == 25000.0
    assert len(profile["receipts"]) == 1

    # Verify homework & remarks
    assert profile["total_homework_assigned"] >= 1
    assert profile["total_submitted"] >= 1
    assert len(profile["remarks"]) >= 1

    # 2. Student A self-view via /my-360
    my_360 = await async_client.get(
        "/api/v1/analytics/my-360",
        headers={"Authorization": f"Bearer {st_a_token}"},
    )
    assert my_360.status_code == 200
    assert my_360.json()["data"]["student_id"] == str(st_a.id)

    # 3. Parent A can view linked Student A
    parent_get = await async_client.get(
        f"/api/v1/analytics/students/{st_a.id}/360",
        headers={"Authorization": f"Bearer {pa_token}"},
    )
    assert parent_get.status_code == 200

    # 4. Assigned Teacher 1 can view Student A
    t1_get = await async_client.get(
        f"/api/v1/analytics/students/{st_a.id}/360",
        headers={"Authorization": f"Bearer {t1_token}"},
    )
    assert t1_get.status_code == 200

    # 5. Unassigned Teacher 2 is rejected with 403 Forbidden
    t2_get = await async_client.get(
        f"/api/v1/analytics/students/{st_a.id}/360",
        headers={"Authorization": f"Bearer {t2_token}"},
    )
    assert t2_get.status_code == 403

    # 6. Student B is rejected when attempting to view Student A (403 Forbidden)
    st_b_get = await async_client.get(
        f"/api/v1/analytics/students/{st_a.id}/360",
        headers={"Authorization": f"Bearer {st_b_token}"},
    )
    assert st_b_get.status_code == 403


# ─────────────────────────────────────────────────────────────────────────────
# Test 3: Batch Detailed Analytics & View Refresh
# ─────────────────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_batch_analytics_and_refresh(
    async_client: AsyncClient,
    analytics_env: dict[str, any],
):
    env = analytics_env
    admin_token = env["admin_token"]
    t1_token = env["t1_token"]
    t2_token = env["t2_token"]
    batch_a = env["batch_a"]

    # 1. Assigned Teacher 1 views Batch A analytics
    b_resp = await async_client.get(
        f"/api/v1/analytics/batches/{batch_a.id}",
        headers={"Authorization": f"Bearer {t1_token}"},
    )
    assert b_resp.status_code == 200, b_resp.text
    b_data = b_resp.json()["data"]

    assert b_data["batch_id"] == str(batch_a.id)
    assert b_data["total_enrolled"] == 2
    assert b_data["total_sessions_conducted"] == 4
    # Student A: 4/4 (100%), Student B: 1/4 (25%) -> Low attendance count == 1
    assert b_data["low_attendance_students_count"] == 1
    assert b_data["tests_conducted"] == 1
    assert b_data["average_test_score"] == 70.0  # (90 + 50) / 2
    assert b_data["top_test_score"] == 90.0
    assert b_data["pass_rate"] == 100.0

    # 2. Unassigned Teacher 2 is rejected
    t2_resp = await async_client.get(
        f"/api/v1/analytics/batches/{batch_a.id}",
        headers={"Authorization": f"Bearer {t2_token}"},
    )
    assert t2_resp.status_code == 403

    # 3. Admin triggers materialized view refresh
    refresh_resp = await async_client.post(
        "/api/v1/analytics/refresh",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert refresh_resp.status_code == 200
    assert "mv_batch_performance_summary" in refresh_resp.json()["data"]["views_refreshed"]


# ─────────────────────────────────────────────────────────────────────────────
# Test 4: Financial & Attendance Analytics
# ─────────────────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_financial_and_attendance_analytics(
    async_client: AsyncClient,
    analytics_env: dict[str, any],
):
    env = analytics_env
    admin_token = env["admin_token"]
    batch_a = env["batch_a"]

    # 1. Financial Analytics
    fin_resp = await async_client.get(
        "/api/v1/analytics/finance",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert fin_resp.status_code == 200, fin_resp.text
    fin_data = fin_resp.json()["data"]

    assert fin_data["total_billed"] >= 50000.0
    assert fin_data["total_collected"] >= 25000.0
    assert fin_data["method_breakdown"].get("UPI", 0.0) >= 25000.0

    # 2. Attendance Analytics
    att_resp = await async_client.get(
        f"/api/v1/analytics/attendance?batch_id={batch_a.id}",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert att_resp.status_code == 200, att_resp.text
    att_data = att_resp.json()["data"]

    assert att_data["total_records"] == 8
    assert att_data["present_count"] == 5
    assert att_data["absent_count"] == 3

    # Low attendance student verification (< 75%)
    low_att = att_data["low_attendance_students"]
    assert len(low_att) == 1
    assert low_att[0]["student_name"] == "Bhavin Patel"
    assert low_att[0]["attendance_percentage"] == 25.0


# ─────────────────────────────────────────────────────────────────────────────
# Test 5: CSV Streaming Data Exports
# ─────────────────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_csv_export_streaming(
    async_client: AsyncClient,
    analytics_env: dict[str, any],
):
    env = analytics_env
    admin_token = env["admin_token"]

    export_types = ["students_roster", "fee_ledger", "attendance_register", "exam_results"]

    for exp_type in export_types:
        resp = await async_client.get(
            f"/api/v1/analytics/export?export_type={exp_type}",
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert resp.status_code == 200, f"Failed for {exp_type}: {resp.text}"
        assert resp.headers["content-type"].startswith("text/csv")
        assert "attachment; filename=" in resp.headers["content-disposition"]
        assert len(resp.text) > 20
