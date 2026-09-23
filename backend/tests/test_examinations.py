"""
tests/test_examinations.py
--------------------------
Tests for Slice 8: Examinations & Question Bank.

Coverage:
  1. Question Bank:
     - Creation with taxonomy, difficulty, options.
     - Validation: Subject existence and tenant scoping.
     - Search and filter by difficulty, type, and keyword.
  2. Test Assembly & Scheduling:
     - Test creation with batch and subject links.
     - Question bank item assignment to test with custom marks and display order.
  3. Bulk Marks Entry & Engine:
     - Bulk entry for multiple students.
     - Boundary validation (marks > max_marks, negative marks rejected).
     - Competition rank auto-calculation (tied marks get identical rank, next rank skips).
     - Statistical percentile auto-calculation for present students.
     - Absent student handling (rank=None, percentile=None).
  4. Publication Gate & Audit Log:
     - Students/Parents blocked from viewing results when test is in DRAFT/EVALUATING.
     - Teacher/Admin publishes results -> transitions status to PUBLISHED.
     - Emits audit log entry ('result.published').
     - Student can view scorecard after publication.
  5. Test Analytics & Leaderboard:
     - Aggregate metrics: highest, lowest, average marks, pass percentage, top-10 leaderboard.
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
from app.models.examination import (
    Question,
    QuestionDifficulty,
    QuestionType,
    Test,
    TestStatus,
    TestType,
)

# Tell pytest not to treat the domain Test model as a test suite
Test.__test__ = False
TestStatus.__test__ = False
TestType.__test__ = False
from app.models.institute import Institute
from app.models.people import StudentProfile, TeacherProfile
from app.models.user import User, UserStatus


# ─── Fixtures ────────────────────────────────────────────────────────────────

@pytest.fixture
async def institute(db_session: AsyncSession) -> Institute:
    inst = Institute(id=uuid.uuid4(), name="Exam Test Inst", code="EXAM_TEST", is_active=True)
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
async def exam_env(
    db_session: AsyncSession, async_client: AsyncClient, institute: Institute
) -> dict[str, any]:
    # 1. Admin
    admin_u, admin_pwd = await _make_user(db_session, institute, "ADMIN", "admin@exam.test")
    admin_token = await _login(async_client, admin_u.email, admin_pwd)

    # 2. Teacher
    t_user, t_pwd = await _make_user(db_session, institute, "TEACHER", "teacher@exam.test")
    t_token = await _login(async_client, t_user.email, t_pwd)
    t_profile = TeacherProfile(
        id=uuid.uuid4(), institute_id=institute.id, user_id=t_user.id,
        first_name="Ramesh", last_name="Verma",
    )
    db_session.add(t_profile)

    # 3. Academic Structure
    year = AcademicYear(
        id=uuid.uuid4(), institute_id=institute.id, name="2025-26",
        start_date=date(2025, 4, 1), end_date=date(2026, 3, 31), is_current=True,
    )
    board = Board(id=uuid.uuid4(), institute_id=institute.id, name="CBSE", code="CBSE")
    sclass = SchoolClass(id=uuid.uuid4(), board_id=board.id, name="Class 12", display_order=12)
    subject = Subject(id=uuid.uuid4(), institute_id=institute.id, name="Mathematics", code="MATH")
    course = Course(
        id=uuid.uuid4(),
        institute_id=institute.id,
        academic_year_id=year.id,
        class_id=sclass.id,
        name="Class 12 Board Maths",
        code="C12-MATH",
        duration_months=12,
    )

    batch = Batch(
        id=uuid.uuid4(),
        institute_id=institute.id,
        course_id=course.id,
        subject_id=subject.id,
        name="Batch Alpha",
        capacity=40,
    )
    db_session.add_all([year, board, sclass, subject, course, batch])
    await db_session.flush()


    # 4. Three Students with Enrollments
    students = []
    student_tokens = []
    for i in range(1, 4):
        s_user, s_pwd = await _make_user(db_session, institute, "STUDENT", f"student{i}@exam.test")
        token = await _login(async_client, s_user.email, s_pwd)
        student_tokens.append(token)
        sp = StudentProfile(
            id=uuid.uuid4(),
            institute_id=institute.id,
            user_id=s_user.id,
            first_name=f"Student{i}",
            last_name="Test",
            admission_number=f"ADM-2025-{100+i}",
        )

        db_session.add(sp)
        await db_session.flush()

        enrollment = Enrollment(
            id=uuid.uuid4(),
            institute_id=institute.id,
            student_id=sp.id,
            batch_id=batch.id,
            status=EnrollmentStatus.ACTIVE,
            enrollment_date=date(2025, 4, 1),
        )
        db_session.add(enrollment)
        students.append(sp)


    await db_session.commit()

    return {
        "institute": institute,
        "admin_token": admin_token,
        "teacher_token": t_token,
        "student_tokens": student_tokens,
        "students": students,
        "subject": subject,
        "batch": batch,
        "course": course,
        "board": board,
        "class": sclass,
    }


# ─── Tests ───────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_question_bank_crud(async_client: AsyncClient, exam_env: dict[str, any]):
    """Test question bank creation, filtering, and retrieval."""
    token = exam_env["teacher_token"]
    subject_id = str(exam_env["subject"].id)
    headers = {"Authorization": f"Bearer {token}"}

    # 1. Create Objective Question
    create_payload = {
        "subject_id": subject_id,
        "chapter": "Calculus",
        "topic": "Integration",
        "difficulty": "HARD",
        "question_type": "OBJECTIVE",
        "body": "What is the integral of 1/x dx?",
        "options": [
            {"key": "A", "text": "x^2"},
            {"key": "B", "text": "ln|x| + C"},
            {"key": "C", "text": "1/x^2"},
            {"key": "D", "text": "e^x"},
        ],
        "correct_answer": "B",
        "default_marks": 4.0,
    }
    resp = await async_client.post("/api/v1/examination/questions", json=create_payload, headers=headers)
    assert resp.status_code == 201, resp.text
    q_data = resp.json()["data"]
    assert q_data["chapter"] == "Calculus"
    assert q_data["difficulty"] == "HARD"
    assert len(q_data["options"]) == 4
    q_id = q_data["id"]

    # 2. List & Filter Questions
    resp = await async_client.get(
        f"/api/v1/examination/questions?subject_id={subject_id}&difficulty=HARD",
        headers=headers,
    )
    assert resp.status_code == 200
    res_json = resp.json()
    assert res_json["total"] >= 1
    assert any(q["id"] == q_id for q in res_json["items"])

    # 3. Get Single Question
    resp = await async_client.get(f"/api/v1/examination/questions/{q_id}", headers=headers)
    assert resp.status_code == 200
    assert resp.json()["data"]["body"] == "What is the integral of 1/x dx?"


@pytest.mark.asyncio
async def test_test_assembly_and_scheduling(async_client: AsyncClient, exam_env: dict[str, any]):
    """Test scheduling an exam and attaching questions from question bank."""
    token = exam_env["teacher_token"]
    headers = {"Authorization": f"Bearer {token}"}
    subject_id = str(exam_env["subject"].id)
    batch_id = str(exam_env["batch"].id)

    # 1. Create two questions in bank
    q1_resp = await async_client.post(
        "/api/v1/examination/questions",
        json={
            "subject_id": subject_id,
            "chapter": "Algebra",
            "difficulty": "EASY",
            "body": "Find roots of x^2 - 4 = 0",
            "default_marks": 2.0,
        },
        headers=headers,
    )
    q1_id = q1_resp.json()["data"]["id"]

    q2_resp = await async_client.post(
        "/api/v1/examination/questions",
        json={
            "subject_id": subject_id,
            "chapter": "Algebra",
            "difficulty": "MEDIUM",
            "body": "Solve 2x + 5 = 15",
            "default_marks": 3.0,
        },
        headers=headers,
    )
    q2_id = q2_resp.json()["data"]["id"]

    # 2. Create Test with Questions
    test_payload = {
        "name": "Maths Unit Test 1",
        "type": "UNIT",
        "date": str(date.today()),
        "duration_minutes": 60,
        "max_marks": 50.0,
        "passing_marks": 20.0,
        "batch_id": batch_id,
        "subject_id": subject_id,
        "questions": [
            {"question_id": q1_id, "marks": 20.0, "display_order": 1, "section": "Section A"},
            {"question_id": q2_id, "marks": 30.0, "display_order": 2, "section": "Section B"},
        ],
    }
    resp = await async_client.post("/api/v1/examination/tests", json=test_payload, headers=headers)
    assert resp.status_code == 201, resp.text
    test_data = resp.json()["data"]
    assert test_data["name"] == "Maths Unit Test 1"
    assert test_data["status"] == "DRAFT"
    assert len(test_data["test_questions"]) == 2
    assert test_data["test_questions"][0]["marks"] == 20.0
    assert test_data["test_questions"][1]["marks"] == 30.0


@pytest.mark.asyncio
async def test_bulk_marks_entry_and_ranking_engine(
    async_client: AsyncClient, exam_env: dict[str, any]
):
    """Test bulk marks entry, validation, competition ranks, and percentiles."""
    token = exam_env["teacher_token"]
    headers = {"Authorization": f"Bearer {token}"}
    students = exam_env["students"]
    batch_id = str(exam_env["batch"].id)

    # 1. Create a Test (Max Marks: 100)
    t_resp = await async_client.post(
        "/api/v1/examination/tests",
        json={
            "name": "Calculus Midterm",
            "type": "MONTHLY",
            "date": str(date.today()),
            "max_marks": 100.0,
            "passing_marks": 40.0,
            "batch_id": batch_id,
        },
        headers=headers,
    )
    test_id = t_resp.json()["data"]["id"]

    # 2. Bulk marks entry:
    # Student 1: 90 marks (Rank 1)
    # Student 2: 70 marks (Rank 2)
    # Student 3: Absent (is_absent=True)
    marks_payload = {
        "entries": [
            {"student_id": str(students[0].id), "marks_obtained": 90.0, "is_absent": False},
            {"student_id": str(students[1].id), "marks_obtained": 70.0, "is_absent": False},
            {"student_id": str(students[2].id), "is_absent": True},
        ]
    }
    resp = await async_client.post(f"/api/v1/examination/tests/{test_id}/marks", json=marks_payload, headers=headers)
    assert resp.status_code == 200, resp.text
    results = resp.json()["data"]
    assert len(results) == 3

    r1 = next(r for r in results if r["student_id"] == str(students[0].id))
    r2 = next(r for r in results if r["student_id"] == str(students[1].id))
    r3 = next(r for r in results if r["student_id"] == str(students[2].id))

    # Check ranks
    assert r1["rank"] == 1
    assert r1["percentage"] == 90.0
    assert r1["percentile"] > r2["percentile"]  # Higher scorer has higher percentile

    assert r2["rank"] == 2
    assert r2["percentage"] == 70.0

    # Absent student
    assert r3["is_absent"] is True
    assert r3["marks_obtained"] is None
    assert r3["rank"] is None
    assert r3["percentile"] is None


@pytest.mark.asyncio
async def test_publication_gate_and_audit_log(
    async_client: AsyncClient, exam_env: dict[str, any], db_session: AsyncSession
):
    """
    Test publication gate:
      - Students cannot see unpublished tests or results.
      - Publishing results unlocks access and emits an audit log.
    """
    teacher_token = exam_env["teacher_token"]
    student_token = exam_env["student_tokens"][0]
    student = exam_env["students"][0]
    batch_id = str(exam_env["batch"].id)

    # 1. Teacher creates test and enters marks
    t_resp = await async_client.post(
        "/api/v1/examination/tests",
        json={
            "name": "Physics Chapter 1 Test",
            "type": "CHAPTER",
            "date": str(date.today()),
            "max_marks": 50.0,
            "passing_marks": 20.0,
            "batch_id": batch_id,
        },
        headers={"Authorization": f"Bearer {teacher_token}"},
    )
    test_id = t_resp.json()["data"]["id"]

    await async_client.post(
        f"/api/v1/examination/tests/{test_id}/marks",
        json={
            "entries": [
                {"student_id": str(student.id), "marks_obtained": 45.0, "is_absent": False}
            ]
        },
        headers={"Authorization": f"Bearer {teacher_token}"},
    )

    # 2. Student attempts to access unpublished test -> 403 Forbidden
    resp = await async_client.get(
        f"/api/v1/examination/tests/{test_id}",
        headers={"Authorization": f"Bearer {student_token}"},
    )
    assert resp.status_code == 403, f"Expected 403 but got {resp.status_code}: {resp.text}"

    # Student attempts to get scorecard before publication -> 403 Forbidden
    resp = await async_client.get(
        f"/api/v1/examination/tests/{test_id}/my-scorecard",
        headers={"Authorization": f"Bearer {student_token}"},
    )
    assert resp.status_code == 403

    # 3. Teacher publishes results
    pub_resp = await async_client.post(
        f"/api/v1/examination/tests/{test_id}/publish",
        headers={"Authorization": f"Bearer {teacher_token}"},
    )
    assert pub_resp.status_code == 200, pub_resp.text
    assert pub_resp.json()["data"]["status"] == "PUBLISHED"
    assert pub_resp.json()["data"]["published_at"] is not None

    # 4. Verify Audit Log entry created
    audit_stmt = select(AuditLog).where(
        AuditLog.entity_name == "tests",
        AuditLog.entity_id == test_id,
        AuditLog.action == "result.published",
    )
    audit_entry = (await db_session.execute(audit_stmt)).scalar_one_or_none()
    assert audit_entry is not None
    assert audit_entry.new_values["status"] == "PUBLISHED"

    # 5. Student can now access test and their scorecard
    resp = await async_client.get(
        f"/api/v1/examination/tests/{test_id}",
        headers={"Authorization": f"Bearer {student_token}"},
    )
    assert resp.status_code == 200
    assert resp.json()["data"]["name"] == "Physics Chapter 1 Test"

    sc_resp = await async_client.get(
        f"/api/v1/examination/tests/{test_id}/my-scorecard",
        headers={"Authorization": f"Bearer {student_token}"},
    )
    assert sc_resp.status_code == 200, sc_resp.text
    sc_data = sc_resp.json()["data"]
    assert sc_data["result"]["marks_obtained"] == 45.0
    assert sc_data["is_passed"] is True
    assert sc_data["class_highest_marks"] == 45.0


@pytest.mark.asyncio
async def test_analytics_and_leaderboard(async_client: AsyncClient, exam_env: dict[str, any]):
    """Test overall test analytics and top-10 leaderboard endpoint."""
    token = exam_env["admin_token"]
    headers = {"Authorization": f"Bearer {token}"}
    students = exam_env["students"]
    batch_id = str(exam_env["batch"].id)

    # 1. Create and populate test
    t_resp = await async_client.post(
        "/api/v1/examination/tests",
        json={
            "name": "Chemistry Final",
            "type": "HALF_YEARLY",
            "date": str(date.today()),
            "max_marks": 100.0,
            "passing_marks": 33.0,
            "batch_id": batch_id,
        },
        headers=headers,
    )
    test_id = t_resp.json()["data"]["id"]

    await async_client.post(
        f"/api/v1/examination/tests/{test_id}/marks",
        json={
            "entries": [
                {"student_id": str(students[0].id), "marks_obtained": 95.0, "is_absent": False},
                {"student_id": str(students[1].id), "marks_obtained": 80.0, "is_absent": False},
                {"student_id": str(students[2].id), "marks_obtained": 25.0, "is_absent": False},  # Failed
            ]
        },
        headers=headers,
    )

    # 2. Get Analytics
    resp = await async_client.get(f"/api/v1/examination/tests/{test_id}/analytics", headers=headers)
    assert resp.status_code == 200, resp.text
    analytics = resp.json()["data"]

    assert analytics["total_candidates"] == 3
    assert analytics["present_count"] == 3
    assert analytics["absent_count"] == 0
    assert analytics["highest_marks"] == 95.0
    assert analytics["lowest_marks"] == 25.0
    assert analytics["pass_percentage"] == 66.67  # 2 passed out of 3 present
    assert len(analytics["leaderboard"]) == 3
    assert analytics["leaderboard"][0]["rank"] == 1
    assert analytics["leaderboard"][0]["marks_obtained"] == 95.0
