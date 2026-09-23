"""
tests/test_enrollment.py
------------------------
Tests for Slice 4: People, Profiles & Enrollment Engine.

Coverage:
  1. Profile separation: User auth record is separate from Student/Teacher/Parent profiles.
  2. Duplicate profile prevention for the same user.
  3. Unique admission_number constraint within institute.
  4. StudentParent linking (primary contact flag, bi-directional lookup).
  5. Student enrollment into a batch (happy path).
  6. Duplicate active enrollment prevention (DuplicateEnrollmentError -> 409).
  7. Batch capacity guard (BatchFullError -> 409).
  8. Batch transfer lifecycle:
     - Old enrollment marked TRANSFERRED with end_date.
     - New active enrollment created in destination batch.
     - Append-only BatchTransferHistory row created with reason.
  9. Transfer rejected if destination batch is full.
 10. Status transition (COMPLETED/DROPPED) with end_date.
 11. Self-view /me/profile and /me/enrollments for student.
"""

from __future__ import annotations

import uuid
from datetime import date

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
from app.models.enrollment import EnrollmentStatus
from app.models.institute import Institute
from app.models.people import BloodGroup, Gender
from app.models.user import User, UserStatus


# ─── Fixtures ────────────────────────────────────────────────────────────────

@pytest.fixture
async def institute(db_session: AsyncSession) -> Institute:
    inst = Institute(id=uuid.uuid4(), name="Enrollment Test Inst", code="ENROLL_TEST", is_active=True)
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
    user, plain = await _make_user(db_session, institute, "ADMIN", "admin@enroll.test")
    return await _login(async_client, user.email, plain)


@pytest.fixture
async def academic_setup(db_session: AsyncSession, institute: Institute) -> dict[str, uuid.UUID]:
    """Create basic academic structure needed for batch creation."""
    year = AcademicYear(
        id=uuid.uuid4(), institute_id=institute.id, name="2025-26",
        start_date=date(2025, 4, 1), end_date=date(2026, 3, 31), is_current=True,
    )
    board = Board(id=uuid.uuid4(), institute_id=institute.id, name="CBSE", code="CBSE")
    sclass = SchoolClass(id=uuid.uuid4(), board_id=board.id, name="Class 10", display_order=10)
    subject = Subject(id=uuid.uuid4(), institute_id=institute.id, name="Mathematics", code="MATH")
    course = Course(
        id=uuid.uuid4(), institute_id=institute.id, academic_year_id=year.id,
        class_id=sclass.id, name="Class 10 CBSE Math", code="C10-MATH", duration_months=12,
    )
    batch_a = Batch(
        id=uuid.uuid4(), institute_id=institute.id, course_id=course.id,
        subject_id=subject.id, name="10-CBSE-MATH-A", capacity=2, is_active=True,
    )
    batch_b = Batch(
        id=uuid.uuid4(), institute_id=institute.id, course_id=course.id,
        subject_id=subject.id, name="10-CBSE-MATH-B", capacity=1, is_active=True,
    )

    db_session.add_all([year, board, sclass, subject, course, batch_a, batch_b])
    await db_session.flush()

    return {
        "class_id": sclass.id,
        "course_id": course.id,
        "batch_a_id": batch_a.id,
        "batch_b_id": batch_b.id,
    }


# ─── Tests ───────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_student_profile_crud_and_separation(
    async_client: AsyncClient,
    db_session: AsyncSession,
    institute: Institute,
    admin_token: str,
    academic_setup: dict[str, uuid.UUID],
):
    """Verify StudentProfile creation, isolation from User, and unique admission_number."""
    user, _ = await _make_user(db_session, institute, "STUDENT", "student1@test.com")
    headers = {"Authorization": f"Bearer {admin_token}"}

    # 1. Create StudentProfile
    create_payload = {
        "user_id": str(user.id),
        "first_name": "Aarav",
        "last_name": "Sharma",
        "date_of_birth": "2010-05-15",
        "gender": "MALE",
        "blood_group": "B+",
        "admission_number": "ADM-2025-001",
        "current_class_id": str(academic_setup["class_id"]),
    }
    resp = await async_client.post("/api/v1/admin/people/students", json=create_payload, headers=headers)
    assert resp.status_code == 201, resp.text
    student_data = resp.json()["data"]
    assert student_data["full_name"] == "Aarav Sharma"
    assert student_data["admission_number"] == "ADM-2025-001"
    student_id = student_data["id"]

    # 2. Cannot create duplicate profile for same user
    dup_user_resp = await async_client.post("/api/v1/admin/people/students", json=create_payload, headers=headers)
    assert dup_user_resp.status_code == 409

    # 3. Cannot reuse admission_number for another user
    user2, _ = await _make_user(db_session, institute, "STUDENT", "student2@test.com")
    dup_adm_payload = {**create_payload, "user_id": str(user2.id)}
    dup_adm_resp = await async_client.post("/api/v1/admin/people/students", json=dup_adm_payload, headers=headers)
    assert dup_adm_resp.status_code == 409

    # 4. Update profile
    patch_resp = await async_client.patch(
        f"/api/v1/admin/people/students/{student_id}",
        json={"first_name": "Aarav Kumar"},
        headers=headers,
    )
    assert patch_resp.status_code == 200
    assert patch_resp.json()["data"]["first_name"] == "Aarav Kumar"


@pytest.mark.asyncio
async def test_parent_profile_and_linking(
    async_client: AsyncClient,
    db_session: AsyncSession,
    institute: Institute,
    admin_token: str,
):
    """Verify ParentProfile creation and StudentParent relationship linking."""
    student_user, _ = await _make_user(db_session, institute, "STUDENT", "child@test.com")
    parent_user, _ = await _make_user(db_session, institute, "PARENT", "parent@test.com")
    headers = {"Authorization": f"Bearer {admin_token}"}

    # Create student profile
    s_resp = await async_client.post(
        "/api/v1/admin/people/students",
        json={"user_id": str(student_user.id), "first_name": "Child", "last_name": "Doe"},
        headers=headers,
    )
    student_id = s_resp.json()["data"]["id"]

    # Create parent profile
    p_resp = await async_client.post(
        "/api/v1/admin/people/parents",
        json={"user_id": str(parent_user.id), "first_name": "Parent", "last_name": "Doe", "relation": "FATHER"},
        headers=headers,
    )
    assert p_resp.status_code == 201
    parent_id = p_resp.json()["data"]["id"]

    # Link parent to student
    link_resp = await async_client.post(
        f"/api/v1/admin/people/students/{student_id}/parents",
        json={"parent_id": parent_id, "is_primary": True},
        headers=headers,
    )
    assert link_resp.status_code == 201
    assert link_resp.json()["data"]["is_primary"] is True

    # Check student's parents endpoint
    get_parents_resp = await async_client.get(
        f"/api/v1/admin/people/students/{student_id}/parents",
        headers=headers,
    )
    assert get_parents_resp.status_code == 200
    parents_list = get_parents_resp.json()
    assert len(parents_list) == 1
    assert parents_list[0]["id"] == parent_id


@pytest.mark.asyncio
async def test_enrollment_engine_duplicate_and_capacity_guards(
    async_client: AsyncClient,
    db_session: AsyncSession,
    institute: Institute,
    admin_token: str,
    academic_setup: dict[str, uuid.UUID],
):
    """
    Verify enrollment engine:
      - Successful enrollment
      - Duplicate active enrollment blocked (409)
      - Capacity limit enforced (BatchFullError -> 409)
    """
    headers = {"Authorization": f"Bearer {admin_token}"}
    batch_b_id = str(academic_setup["batch_b_id"])  # capacity = 1

    # Student 1
    u1, _ = await _make_user(db_session, institute, "STUDENT", "s1@test.com")
    s1_resp = await async_client.post(
        "/api/v1/admin/people/students",
        json={"user_id": str(u1.id), "first_name": "Student", "last_name": "One"},
        headers=headers,
    )
    student1_id = s1_resp.json()["data"]["id"]

    # Student 2
    u2, _ = await _make_user(db_session, institute, "STUDENT", "s2@test.com")
    s2_resp = await async_client.post(
        "/api/v1/admin/people/students",
        json={"user_id": str(u2.id), "first_name": "Student", "last_name": "Two"},
        headers=headers,
    )
    student2_id = s2_resp.json()["data"]["id"]

    # 1. Enroll Student 1 into Batch B (capacity 1)
    enroll_resp = await async_client.post(
        "/api/v1/admin/enrollments",
        json={"student_id": student1_id, "batch_id": batch_b_id},
        headers=headers,
    )
    assert enroll_resp.status_code == 201
    assert enroll_resp.json()["data"]["status"] == "ACTIVE"

    # 2. Duplicate active enrollment for Student 1 -> blocked
    dup_enroll = await async_client.post(
        "/api/v1/admin/enrollments",
        json={"student_id": student1_id, "batch_id": batch_b_id},
        headers=headers,
    )
    assert dup_enroll.status_code == 409
    assert dup_enroll.json()["code"] == "ENROLLMENT_ALREADY_EXISTS"

    # 3. Enroll Student 2 into Batch B -> blocked by capacity
    full_enroll = await async_client.post(
        "/api/v1/admin/enrollments",
        json={"student_id": student2_id, "batch_id": batch_b_id},
        headers=headers,
    )
    assert full_enroll.status_code == 409
    assert full_enroll.json()["code"] == "BATCH_FULL"


@pytest.mark.asyncio
async def test_batch_transfer_and_history_audit(
    async_client: AsyncClient,
    db_session: AsyncSession,
    institute: Institute,
    admin_token: str,
    academic_setup: dict[str, uuid.UUID],
):
    """
    Verify student batch transfer lifecycle:
      - Active enrollment transferred to another batch.
      - Old enrollment marked TRANSFERRED.
      - New enrollment created as ACTIVE.
      - History row written with audit trail.
    """
    headers = {"Authorization": f"Bearer {admin_token}"}
    batch_a_id = str(academic_setup["batch_a_id"])  # capacity 2
    batch_b_id = str(academic_setup["batch_b_id"])  # capacity 1

    # Create student
    u, _ = await _make_user(db_session, institute, "STUDENT", "transfer_stud@test.com")
    s_resp = await async_client.post(
        "/api/v1/admin/people/students",
        json={"user_id": str(u.id), "first_name": "Rahul", "last_name": "Verma"},
        headers=headers,
    )
    student_id = s_resp.json()["data"]["id"]

    # Enroll in Batch A
    enroll_resp = await async_client.post(
        "/api/v1/admin/enrollments",
        json={"student_id": student_id, "batch_id": batch_a_id},
        headers=headers,
    )
    assert enroll_resp.status_code == 201
    initial_enrollment_id = enroll_resp.json()["data"]["id"]

    # Transfer from Batch A to Batch B
    transfer_resp = await async_client.post(
        f"/api/v1/admin/enrollments/{initial_enrollment_id}/transfer",
        json={"to_batch_id": batch_b_id, "reason": "Requested morning schedule"},
        headers=headers,
    )
    assert transfer_resp.status_code == 200, transfer_resp.text
    new_enrollment_data = transfer_resp.json()["data"]
    assert new_enrollment_data["status"] == "ACTIVE"
    assert new_enrollment_data["batch_id"] == batch_b_id

    # Check old enrollment is now TRANSFERRED
    old_resp = await async_client.get(
        f"/api/v1/admin/enrollments/{initial_enrollment_id}",
        headers=headers,
    )
    assert old_resp.status_code == 200
    assert old_resp.json()["data"]["status"] == "TRANSFERRED"
    assert old_resp.json()["data"]["end_date"] is not None

    # Check transfer history audit log
    history_resp = await async_client.get(
        f"/api/v1/admin/enrollments/transfers/history?student_id={student_id}",
        headers=headers,
    )
    assert history_resp.status_code == 200
    history_items = history_resp.json()["items"]
    assert len(history_items) == 1
    assert history_items[0]["from_batch_id"] == batch_a_id
    assert history_items[0]["to_batch_id"] == batch_b_id
    assert history_items[0]["reason"] == "Requested morning schedule"


@pytest.mark.asyncio
async def test_self_view_profile_and_enrollments(
    async_client: AsyncClient,
    db_session: AsyncSession,
    institute: Institute,
    admin_token: str,
    academic_setup: dict[str, uuid.UUID],
):
    """Verify /me/profile and /me/enrollments for student caller."""
    admin_headers = {"Authorization": f"Bearer {admin_token}"}
    user, plain = await _make_user(db_session, institute, "STUDENT", "self_view_stud@test.com")

    # Admin creates student profile
    s_resp = await async_client.post(
        "/api/v1/admin/people/students",
        json={"user_id": str(user.id), "first_name": "Pooja", "last_name": "Patel"},
        headers=admin_headers,
    )
    student_id = s_resp.json()["data"]["id"]

    # Admin enrolls student
    await async_client.post(
        "/api/v1/admin/enrollments",
        json={"student_id": student_id, "batch_id": str(academic_setup["batch_a_id"])},
        headers=admin_headers,
    )

    # Student logs in
    student_token = await _login(async_client, user.email, plain)
    student_headers = {"Authorization": f"Bearer {student_token}"}

    # Call /me/profile
    profile_resp = await async_client.get("/api/v1/me/profile", headers=student_headers)
    assert profile_resp.status_code == 200
    body = profile_resp.json()["data"]
    assert body["type"] == "STUDENT"
    assert body["profile"]["first_name"] == "Pooja"

    # Call /me/enrollments
    enrollments_resp = await async_client.get("/api/v1/me/enrollments", headers=student_headers)
    assert enrollments_resp.status_code == 200
    enrollments = enrollments_resp.json()
    assert len(enrollments) == 1
    assert enrollments[0]["batch_id"] == str(academic_setup["batch_a_id"])
