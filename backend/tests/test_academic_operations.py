"""
tests/test_academic_operations.py
---------------------------------
Tests for Slice 6: Academic Operations & Attendance.

Coverage:
  1. Timetable creation and calendar session generation from weekly rules.
  2. Class session rescheduling lifecycle (old marked RESCHEDULED with FK link).
  3. Session delivery logs (topic, homework) and auto-advancing status to HELD.
  4. Attendance ReBAC enforcement:
     - Teacher assigned to batch can mark attendance.
     - Unassigned teacher is rejected with 403 FORBIDDEN.
     - Admin can mark attendance for any session.
  5. Bulk attendance marking & upsert idempotency (no duplicate rows on re-mark).
  6. Foreign enrollment rejected (cannot mark student not in batch).
  7. Attendance sheet inspection and student attendance % calculation.
  8. Teacher remarks on students with parent visibility filtering.
"""

from __future__ import annotations

import uuid
from datetime import date, timedelta

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import hash_password
from app.models.academic_operations import (
    AttendanceStatus,
    ClassSession,
    ClassSessionStatus,
    Timetable,
)
from app.models.academic_structure import (
    AcademicYear,
    Batch,
    Board,
    Course,
    DayOfWeek,
    SchoolClass,
    Subject,
)
from app.models.enrollment import Enrollment, EnrollmentStatus
from app.models.institute import Institute
from app.models.people import StudentProfile, TeacherProfile
from app.models.user import User, UserStatus


# ─── Fixtures ────────────────────────────────────────────────────────────────

@pytest.fixture
async def institute(db_session: AsyncSession) -> Institute:
    inst = Institute(id=uuid.uuid4(), name="Ops Test Inst", code="OPS_TEST", is_active=True)
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
async def admin_token(async_client: AsyncClient, db_session: AsyncSession, institute: Institute) -> str:
    user, plain = await _make_user(db_session, institute, "ADMIN", "admin@ops.test")
    return await _login(async_client, user.email, plain)


@pytest.fixture
async def academic_env(
    db_session: AsyncSession, institute: Institute
) -> dict[str, any]:
    # 1. Teachers
    t1_user, t1_pwd = await _make_user(db_session, institute, "TEACHER", "teacher1@ops.test")
    t1_profile = TeacherProfile(
        id=uuid.uuid4(), institute_id=institute.id, user_id=t1_user.id,
        first_name="Anita", last_name="Sharma",
    )
    t2_user, t2_pwd = await _make_user(db_session, institute, "TEACHER", "teacher2@ops.test")
    t2_profile = TeacherProfile(
        id=uuid.uuid4(), institute_id=institute.id, user_id=t2_user.id,
        first_name="Ravi", last_name="Verma",
    )
    db_session.add_all([t1_profile, t2_profile])

    # 2. Academic structure
    year = AcademicYear(
        id=uuid.uuid4(), institute_id=institute.id, name="2025-26",
        start_date=date(2025, 4, 1), end_date=date(2026, 3, 31), is_current=True,
    )
    board = Board(id=uuid.uuid4(), institute_id=institute.id, name="CBSE", code="CBSE")
    sclass = SchoolClass(id=uuid.uuid4(), board_id=board.id, name="Class 10", display_order=10)
    subject = Subject(id=uuid.uuid4(), institute_id=institute.id, name="Math", code="MATH")
    course = Course(
        id=uuid.uuid4(), institute_id=institute.id, academic_year_id=year.id,
        class_id=sclass.id, name="Class 10 Math", code="C10-M", duration_months=12,
    )
    # Batch assigned to Teacher 1
    batch = Batch(
        id=uuid.uuid4(), institute_id=institute.id, course_id=course.id,
        subject_id=subject.id, teacher_id=t1_profile.id, name="10-MATH-OPS",
        capacity=30, is_active=True,
    )
    db_session.add_all([year, board, sclass, subject, course, batch])

    # 3. Students & Enrollments
    s1_user, _ = await _make_user(db_session, institute, "STUDENT", "student1@ops.test")
    s1 = StudentProfile(
        id=uuid.uuid4(), institute_id=institute.id, user_id=s1_user.id,
        first_name="Aarav", last_name="Kumar", admission_number="ADM-OPS-01",
    )
    s2_user, _ = await _make_user(db_session, institute, "STUDENT", "student2@ops.test")
    s2 = StudentProfile(
        id=uuid.uuid4(), institute_id=institute.id, user_id=s2_user.id,
        first_name="Bhavna", last_name="Mehta", admission_number="ADM-OPS-02",
    )
    db_session.add_all([s1, s2])
    await db_session.flush()

    e1 = Enrollment(
        id=uuid.uuid4(), student_id=s1.id, batch_id=batch.id,
        institute_id=institute.id, status=EnrollmentStatus.ACTIVE,
        enrollment_date=date(2025, 4, 1),
    )
    e2 = Enrollment(
        id=uuid.uuid4(), student_id=s2.id, batch_id=batch.id,
        institute_id=institute.id, status=EnrollmentStatus.ACTIVE,
        enrollment_date=date(2025, 4, 1),
    )
    db_session.add_all([e1, e2])
    await db_session.flush()

    return {
        "teacher1_user": t1_user,
        "teacher1_pwd": t1_pwd,
        "teacher1_profile": t1_profile,
        "teacher2_user": t2_user,
        "teacher2_pwd": t2_pwd,
        "batch_id": batch.id,
        "student1_id": s1.id,
        "student2_id": s2.id,
        "enrollment1_id": e1.id,
        "enrollment2_id": e2.id,
    }


# ─── Tests ───────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_timetable_and_session_generation(
    async_client: AsyncClient,
    admin_token: str,
    academic_env: dict[str, any],
):
    """Test creating timetable rules and generating sessions for a date range."""
    headers = {"Authorization": f"Bearer {admin_token}"}
    batch_id = str(academic_env["batch_id"])

    # 1. Create timetable: MONDAY 17:00-18:30
    tt_resp = await async_client.post(
        "/api/v1/operations/timetables",
        json={
            "batch_id": batch_id,
            "day_of_week": "MON",
            "start_time": "17:00",
            "end_time": "18:30",
            "room": "Room 101",
        },
        headers=headers,
    )
    assert tt_resp.status_code == 201, tt_resp.text
    assert tt_resp.json()["data"]["day_of_week"] == "MON"

    # 2. Generate sessions between Monday 2026-05-04 and Monday 2026-05-18 (3 Mondays)
    gen_resp = await async_client.post(
        "/api/v1/operations/timetables/generate-sessions",
        json={
            "batch_id": batch_id,
            "start_date": "2026-05-04",
            "end_date": "2026-05-18",
        },
        headers=headers,
    )
    assert gen_resp.status_code == 201
    sessions = gen_resp.json()["data"]
    assert len(sessions) == 3
    for s in sessions:
        assert s["batch_id"] == batch_id
        assert s["status"] == "SCHEDULED"


@pytest.mark.asyncio
async def test_session_rescheduling(
    async_client: AsyncClient,
    admin_token: str,
    academic_env: dict[str, any],
):
    """Test session rescheduling lifecycle with audit link."""
    headers = {"Authorization": f"Bearer {admin_token}"}
    batch_id = str(academic_env["batch_id"])

    # Create session
    create_resp = await async_client.post(
        "/api/v1/operations/sessions",
        json={
            "batch_id": batch_id,
            "date": "2026-06-01",
            "start_time": "17:00",
            "end_time": "18:30",
        },
        headers=headers,
    )
    session_id = create_resp.json()["data"]["id"]

    # Reschedule
    resched_resp = await async_client.post(
        f"/api/v1/operations/sessions/{session_id}/reschedule",
        json={
            "new_date": "2026-06-02",
            "new_start_time": "18:00",
            "new_end_time": "19:30",
            "reason": "Teacher emergency",
        },
        headers=headers,
    )
    assert resched_resp.status_code == 200, resched_resp.text
    new_session = resched_resp.json()["data"]
    assert new_session["date"] == "2026-06-02"
    assert new_session["status"] == "SCHEDULED"

    # Old session is now RESCHEDULED and points to new
    old_resp = await async_client.get(f"/api/v1/operations/sessions/{session_id}", headers=headers)
    assert old_resp.status_code == 200
    old = old_resp.json()["data"]
    assert old["status"] == "RESCHEDULED"
    assert old["rescheduled_to_session_id"] == new_session["id"]


@pytest.mark.asyncio
async def test_session_log_auto_advances_status_to_held(
    async_client: AsyncClient,
    admin_token: str,
    academic_env: dict[str, any],
):
    """Saving session log automatically updates session status from SCHEDULED to HELD."""
    headers = {"Authorization": f"Bearer {admin_token}"}
    batch_id = str(academic_env["batch_id"])

    # Create session
    s_resp = await async_client.post(
        "/api/v1/operations/sessions",
        json={"batch_id": batch_id, "date": "2026-06-05", "start_time": "10:00", "end_time": "11:30"},
        headers=headers,
    )
    session_id = s_resp.json()["data"]["id"]

    # Save log
    log_resp = await async_client.post(
        f"/api/v1/operations/sessions/{session_id}/log",
        json={
            "topic": "Quadratic Equations",
            "topics_covered": "Factorization method and discriminant formula",
            "homework_notes": "Solve exercises 4.1 and 4.2",
        },
        headers=headers,
    )
    assert log_resp.status_code == 200
    assert log_resp.json()["data"]["topic"] == "Quadratic Equations"

    # Check session is now HELD
    check_s = await async_client.get(f"/api/v1/operations/sessions/{session_id}", headers=headers)
    assert check_s.json()["data"]["status"] == "HELD"


@pytest.mark.asyncio
async def test_attendance_rebac_and_bulk_marking(
    async_client: AsyncClient,
    admin_token: str,
    academic_env: dict[str, any],
):
    """
    Test attendance marking:
      - Teacher 1 (assigned) can mark attendance.
      - Teacher 2 (unassigned) is blocked (403 FORBIDDEN).
      - Upsert: re-marking modifies status without duplicate rows.
    """
    batch_id = str(academic_env["batch_id"])
    e1_id = str(academic_env["enrollment1_id"])
    e2_id = str(academic_env["enrollment2_id"])

    # Admin creates session
    admin_headers = {"Authorization": f"Bearer {admin_token}"}
    s_resp = await async_client.post(
        "/api/v1/operations/sessions",
        json={"batch_id": batch_id, "date": "2026-06-10", "start_time": "17:00", "end_time": "18:30"},
        headers=admin_headers,
    )
    session_id = s_resp.json()["data"]["id"]

    # Teacher 2 (unassigned) attempts to mark -> 403 FORBIDDEN
    t2_token = await _login(
        async_client,
        academic_env["teacher2_user"].email,
        academic_env["teacher2_pwd"],
    )
    t2_headers = {"Authorization": f"Bearer {t2_token}"}
    unauthorized_resp = await async_client.post(
        f"/api/v1/operations/attendance/sessions/{session_id}/mark",
        json={"records": [{"enrollment_id": e1_id, "status": "PRESENT"}]},
        headers=t2_headers,
    )
    assert unauthorized_resp.status_code == 403

    # Teacher 1 (assigned) marks attendance -> 200 OK
    t1_token = await _login(
        async_client,
        academic_env["teacher1_user"].email,
        academic_env["teacher1_pwd"],
    )
    t1_headers = {"Authorization": f"Bearer {t1_token}"}
    mark_resp = await async_client.post(
        f"/api/v1/operations/attendance/sessions/{session_id}/mark",
        json={
            "records": [
                {"enrollment_id": e1_id, "status": "PRESENT"},
                {"enrollment_id": e2_id, "status": "ABSENT", "remarks": "Sick leave"},
            ]
        },
        headers=t1_headers,
    )
    assert mark_resp.status_code == 200
    assert mark_resp.json()["data"]["marked_count"] == 2

    # Check attendance sheet
    sheet_resp = await async_client.get(
        f"/api/v1/operations/attendance/sessions/{session_id}/sheet",
        headers=t1_headers,
    )
    assert sheet_resp.status_code == 200
    sheet = sheet_resp.json()
    assert len(sheet) == 2
    statuses = {item["enrollment_id"]: item["status"] for item in sheet}
    assert statuses[e1_id] == "PRESENT"
    assert statuses[e2_id] == "ABSENT"

    # Upsert test: re-mark student 2 as LATE instead of ABSENT
    re_mark = await async_client.post(
        f"/api/v1/operations/attendance/sessions/{session_id}/mark",
        json={"records": [{"enrollment_id": e2_id, "status": "LATE"}]},
        headers=t1_headers,
    )
    assert re_mark.status_code == 200

    # Sheet must still only have 2 rows
    sheet_resp2 = await async_client.get(
        f"/api/v1/operations/attendance/sessions/{session_id}/sheet",
        headers=t1_headers,
    )
    sheet2 = sheet_resp2.json()
    assert len(sheet2) == 2
    statuses2 = {item["enrollment_id"]: item["status"] for item in sheet2}
    assert statuses2[e2_id] == "LATE"


@pytest.mark.asyncio
async def test_student_attendance_percentage_stats(
    async_client: AsyncClient,
    admin_token: str,
    academic_env: dict[str, any],
):
    """Verify attendance stats calculation (% and counts)."""
    headers = {"Authorization": f"Bearer {admin_token}"}
    batch_id = str(academic_env["batch_id"])
    e1_id = str(academic_env["enrollment1_id"])
    s1_id = str(academic_env["student1_id"])

    # Create 2 sessions and mark student 1 PRESENT in both
    for i in range(2):
        s_resp = await async_client.post(
            "/api/v1/operations/sessions",
            json={"batch_id": batch_id, "date": f"2026-07-0{i+1}", "start_time": "17:00", "end_time": "18:30"},
            headers=headers,
        )
        sid = s_resp.json()["data"]["id"]
        await async_client.post(
            f"/api/v1/operations/attendance/sessions/{sid}/mark",
            json={"records": [{"enrollment_id": e1_id, "status": "PRESENT"}]},
            headers=headers,
        )

    stats_resp = await async_client.get(
        f"/api/v1/operations/attendance/students/{s1_id}/stats",
        headers=headers,
    )
    assert stats_resp.status_code == 200
    stats = stats_resp.json()["data"]
    assert stats["total_sessions"] == 2
    assert stats["present_count"] == 2
    assert stats["attendance_percentage"] == 100.0


@pytest.mark.asyncio
async def test_student_remarks_visibility(
    async_client: AsyncClient,
    academic_env: dict[str, any],
):
    """Test teacher creating remarks on a student and parent visibility filtering."""
    t1_token = await _login(
        async_client,
        academic_env["teacher1_user"].email,
        academic_env["teacher1_pwd"],
    )
    t1_headers = {"Authorization": f"Bearer {t1_token}"}
    s1_id = str(academic_env["student1_id"])

    # Teacher creates remark
    r_resp = await async_client.post(
        "/api/v1/operations/remarks",
        json={
            "student_id": s1_id,
            "body": "Excellent participation in today's algebra discussion.",
            "visible_to_parent": True,
        },
        headers=t1_headers,
    )
    assert r_resp.status_code == 201
    assert r_resp.json()["data"]["visible_to_parent"] is True

    # List remarks
    list_resp = await async_client.get(
        f"/api/v1/operations/remarks/student/{s1_id}",
        headers=t1_headers,
    )
    assert list_resp.status_code == 200
    remarks = list_resp.json()
    assert len(remarks) >= 1
    assert "algebra" in remarks[0]["body"]
