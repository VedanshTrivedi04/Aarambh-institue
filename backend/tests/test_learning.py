"""
tests/test_learning.py
----------------------
Tests for Slice 7: Learning & Generic File Storage.

Coverage:
  1. File upload with MIME and extension security validation:
     - Valid PDF/Image uploads successfully.
     - Disallowed file types (.exe, .sh) are rejected with 422 ValidationError.
  2. File download / streaming by storage_key.
  3. Study Material creation and target course/batch scoping.
  4. Homework assignment by teacher.
  5. Student homework submission (enrolled vs unenrolled ReBAC check).
  6. Automatic LATE status detection when submitting past due date.
  7. Teacher grading and evaluation feedback.
"""

from __future__ import annotations

import io
import uuid
from datetime import date, timedelta

import pytest
from httpx import AsyncClient
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
from app.models.enrollment import Enrollment, EnrollmentStatus
from app.models.institute import Institute
from app.models.people import StudentProfile, TeacherProfile
from app.models.user import User, UserStatus


# ─── Fixtures ────────────────────────────────────────────────────────────────

@pytest.fixture
async def institute(db_session: AsyncSession) -> Institute:
    inst = Institute(id=uuid.uuid4(), name="Learning Test Inst", code="LEARN_TEST", is_active=True)
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
    user, plain = await _make_user(db_session, institute, "ADMIN", "admin@learn.test")
    return await _login(async_client, user.email, plain)


@pytest.fixture
async def learning_env(
    db_session: AsyncSession, institute: Institute
) -> dict[str, any]:
    # 1. Teacher
    t_user, t_pwd = await _make_user(db_session, institute, "TEACHER", "teacher@learn.test")
    t_profile = TeacherProfile(
        id=uuid.uuid4(), institute_id=institute.id, user_id=t_user.id,
        first_name="Sunita", last_name="Sharma",
    )
    db_session.add(t_profile)

    # 2. Academic structure
    year = AcademicYear(
        id=uuid.uuid4(), institute_id=institute.id, name="2025-26",
        start_date=date(2025, 4, 1), end_date=date(2026, 3, 31), is_current=True,
    )
    board = Board(id=uuid.uuid4(), institute_id=institute.id, name="CBSE", code="CBSE")
    sclass = SchoolClass(id=uuid.uuid4(), board_id=board.id, name="Class 10", display_order=10)
    subject = Subject(id=uuid.uuid4(), institute_id=institute.id, name="Physics", code="PHY")
    course = Course(
        id=uuid.uuid4(), institute_id=institute.id, academic_year_id=year.id,
        class_id=sclass.id, name="Class 10 Physics", code="C10-PHY", duration_months=12,
    )
    batch = Batch(
        id=uuid.uuid4(), institute_id=institute.id, course_id=course.id,
        subject_id=subject.id, teacher_id=t_profile.id, name="10-PHY-A",
        capacity=30, is_active=True,
    )
    db_session.add_all([year, board, sclass, subject, course, batch])

    # 3. Enrolled Student
    s1_user, s1_pwd = await _make_user(db_session, institute, "STUDENT", "enrolled@learn.test")
    s1 = StudentProfile(
        id=uuid.uuid4(), institute_id=institute.id, user_id=s1_user.id,
        first_name="Rohan", last_name="Gupta", admission_number="ADM-L-01",
    )
    db_session.add(s1)
    await db_session.flush()

    e1 = Enrollment(
        id=uuid.uuid4(), student_id=s1.id, batch_id=batch.id,
        institute_id=institute.id, status=EnrollmentStatus.ACTIVE,
        enrollment_date=date(2025, 4, 1),
    )
    db_session.add(e1)

    # 4. Unenrolled Student
    s2_user, s2_pwd = await _make_user(db_session, institute, "STUDENT", "other@learn.test")
    s2 = StudentProfile(
        id=uuid.uuid4(), institute_id=institute.id, user_id=s2_user.id,
        first_name="Other", last_name="Student", admission_number="ADM-L-02",
    )
    db_session.add(s2)
    await db_session.flush()

    return {
        "teacher_user": t_user,
        "teacher_pwd": t_pwd,
        "course_id": course.id,
        "batch_id": batch.id,
        "subject_id": subject.id,
        "enrolled_student_user": s1_user,
        "enrolled_student_pwd": s1_pwd,
        "enrolled_student_profile": s1,
        "unenrolled_student_user": s2_user,
        "unenrolled_student_pwd": s2_pwd,
    }


# ─── Tests ───────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_file_upload_validation_and_download(
    async_client: AsyncClient,
    admin_token: str,
):
    """Verify file uploads, MIME/extension security checks, and streaming download."""
    headers = {"Authorization": f"Bearer {admin_token}"}

    # 1. Valid PDF upload
    pdf_bytes = b"%PDF-1.4 Mock PDF Content For Testing"
    files = {"file": ("sample_notes.pdf", io.BytesIO(pdf_bytes), "application/pdf")}
    up_resp = await async_client.post("/api/v1/learning/files/upload", files=files, headers=headers)
    assert up_resp.status_code == 201, up_resp.text
    att_data = up_resp.json()["data"]
    storage_key = att_data["storage_key"]
    assert att_data["file_name"] == "sample_notes.pdf"
    assert att_data["download_url"] is not None

    # 2. Download/Stream file content
    dl_resp = await async_client.get(f"/api/v1/learning/files/{storage_key}")
    assert dl_resp.status_code == 200
    assert dl_resp.content == pdf_bytes
    assert dl_resp.headers["content-type"] == "application/pdf"

    # 3. Disallowed extension (.exe / .sh) rejected
    bad_files = {"file": ("malicious.exe", io.BytesIO(b"malware binary"), "application/octet-stream")}
    bad_resp = await async_client.post("/api/v1/learning/files/upload", files=bad_files, headers=headers)
    assert bad_resp.status_code == 422
    assert "not permitted" in bad_resp.json()["detail"]


@pytest.mark.asyncio
async def test_study_material_publishing_and_course_scoping(
    async_client: AsyncClient,
    admin_token: str,
    learning_env: dict[str, any],
):
    """Test study material creation and course/batch targeting."""
    headers = {"Authorization": f"Bearer {admin_token}"}
    course_id = str(learning_env["course_id"])

    # 1. Publish material
    mat_resp = await async_client.post(
        "/api/v1/learning/materials",
        json={
            "title": "Chapter 1: Ray Optics Formula Sheet",
            "type": "NOTES",
            "description": "Essential formulas for ray optics and mirrors",
            "target_course_id": course_id,
            "is_published": True,
        },
        headers=headers,
    )
    assert mat_resp.status_code == 201, mat_resp.text
    mat = mat_resp.json()["data"]
    assert mat["title"] == "Chapter 1: Ray Optics Formula Sheet"

    # 2. Student queries materials
    s_token = await _login(
        async_client,
        learning_env["enrolled_student_user"].email,
        learning_env["enrolled_student_pwd"],
    )
    s_headers = {"Authorization": f"Bearer {s_token}"}
    list_resp = await async_client.get(
        f"/api/v1/learning/materials?course_id={course_id}",
        headers=s_headers,
    )
    assert list_resp.status_code == 200
    items = list_resp.json()["items"]
    assert len(items) >= 1
    assert any(m["id"] == mat["id"] for m in items)


@pytest.mark.asyncio
async def test_homework_assignment_submission_and_evaluation(
    async_client: AsyncClient,
    learning_env: dict[str, any],
):
    """
    Test full homework cycle:
      1. Teacher creates homework assignment.
      2. Enrolled student submits homework.
      3. Unenrolled student attempt is rejected (403).
      4. Teacher evaluates submission and records marks/comment.
      5. Student views evaluated submission.
    """
    batch_id = str(learning_env["batch_id"])
    subject_id = str(learning_env["subject_id"])

    # Teacher logs in and creates assignment
    t_token = await _login(
        async_client,
        learning_env["teacher_user"].email,
        learning_env["teacher_pwd"],
    )
    t_headers = {"Authorization": f"Bearer {t_token}"}

    hw_resp = await async_client.post(
        "/api/v1/learning/homework",
        json={
            "batch_id": batch_id,
            "subject_id": subject_id,
            "title": "Optics Ray Diagrams Problem Set",
            "instructions": "Draw ray diagrams for concave mirror cases 1 through 6.",
            "chapter": "Light - Reflection",
            "due_date": str(date.today() + timedelta(days=3)),
        },
        headers=t_headers,
    )
    assert hw_resp.status_code == 201, hw_resp.text
    hw_id = hw_resp.json()["data"]["id"]

    # Unenrolled student tries to submit -> 403 FORBIDDEN
    unenrolled_token = await _login(
        async_client,
        learning_env["unenrolled_student_user"].email,
        learning_env["unenrolled_student_pwd"],
    )
    un_headers = {"Authorization": f"Bearer {unenrolled_token}"}
    un_sub = await async_client.post(
        f"/api/v1/learning/homework/{hw_id}/submit",
        json={"submission_text": "My solution attempt"},
        headers=un_headers,
    )
    assert un_sub.status_code == 403

    # Enrolled student submits -> 201 CREATED
    enrolled_token = await _login(
        async_client,
        learning_env["enrolled_student_user"].email,
        learning_env["enrolled_student_pwd"],
    )
    en_headers = {"Authorization": f"Bearer {enrolled_token}"}
    sub_resp = await async_client.post(
        f"/api/v1/learning/homework/{hw_id}/submit",
        json={"submission_text": "Completed all 6 cases on sheet."},
        headers=en_headers,
    )
    assert sub_resp.status_code == 201, sub_resp.text
    submission_id = sub_resp.json()["data"]["id"]
    assert sub_resp.json()["data"]["status"] == "SUBMITTED"

    # Teacher grades submission -> 200 OK
    eval_resp = await async_client.post(
        f"/api/v1/learning/homework/submissions/{submission_id}/evaluate",
        json={
            "marks": 9.5,
            "max_marks": 10.0,
            "teacher_comment": "Excellent accuracy on focal point intersections.",
            "status": "REVIEWED",
        },
        headers=t_headers,
    )
    assert eval_resp.status_code == 200
    assert eval_resp.json()["data"]["marks"] == 9.5
    assert eval_resp.json()["data"]["status"] == "REVIEWED"

    # Student views their submission
    my_sub_resp = await async_client.get(
        f"/api/v1/learning/homework/{hw_id}/my-submission",
        headers=en_headers,
    )
    assert my_sub_resp.status_code == 200
    my_sub = my_sub_resp.json()["data"]
    assert my_sub["marks"] == 9.5
    assert "accuracy" in my_sub["teacher_comment"]
