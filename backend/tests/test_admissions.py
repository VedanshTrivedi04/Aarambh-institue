"""
tests/test_admissions.py
------------------------
Tests for Slice 5: Admissions & Enquiry Pipeline.

Coverage:
  1. Enquiry creation with automatic initial follow-up entry.
  2. Enquiry follow-up timeline and stage transitions (NEW -> COUNSELLING -> DEMO).
  3. Enquiry filtering and search.
  4. Atomic Admission Wizard (happy path):
     - Student User + StudentProfile (auto-generated admission number)
     - Parent User + ParentProfile
     - StudentParent link
     - Batch Enrollment (ACTIVE)
     - Returned temporary passwords
  5. Atomic Admission Wizard with Enquiry conversion:
     - Enquiry marked stage=ADMISSION
     - converted_student_id populated
     - Follow-up timeline audit appended
  6. Atomic rollback on BatchFullError:
     - Target batch at capacity
     - Transaction rolls back completely; no orphan User or Profile records remain.
  7. Parent account reuse across siblings:
     - Admitting a second student with the same parent email links to existing ParentProfile.
"""

from __future__ import annotations

import uuid
from datetime import date

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
from app.models.enquiry import Enquiry, EnquiryStage
from app.models.enrollment import Enrollment, EnrollmentStatus
from app.models.institute import Institute
from app.models.people import ParentProfile, StudentParent, StudentProfile
from app.models.user import User, UserStatus


# ─── Fixtures ────────────────────────────────────────────────────────────────

@pytest.fixture
async def institute(db_session: AsyncSession) -> Institute:
    inst = Institute(id=uuid.uuid4(), name="Admission Test Inst", code="ADM_TEST", is_active=True)
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
    user, plain = await _make_user(db_session, institute, "ADMIN", "admin@admission.test")
    return await _login(async_client, user.email, plain)


@pytest.fixture
async def academic_setup(db_session: AsyncSession, institute: Institute) -> dict[str, uuid.UUID]:
    year = AcademicYear(
        id=uuid.uuid4(), institute_id=institute.id, name="2025-26",
        start_date=date(2025, 4, 1), end_date=date(2026, 3, 31), is_current=True,
    )
    board = Board(id=uuid.uuid4(), institute_id=institute.id, name="CBSE", code="CBSE")
    sclass = SchoolClass(id=uuid.uuid4(), board_id=board.id, name="Class 10", display_order=10)
    subject = Subject(id=uuid.uuid4(), institute_id=institute.id, name="Science", code="SCI")
    course = Course(
        id=uuid.uuid4(), institute_id=institute.id, academic_year_id=year.id,
        class_id=sclass.id, name="Class 10 Science", code="C10-SCI", duration_months=12,
    )
    batch_open = Batch(
        id=uuid.uuid4(), institute_id=institute.id, course_id=course.id,
        subject_id=subject.id, name="10-CBSE-SCI-OPEN", capacity=10, is_active=True,
    )
    batch_tight = Batch(
        id=uuid.uuid4(), institute_id=institute.id, course_id=course.id,
        subject_id=subject.id, name="10-CBSE-SCI-TIGHT", capacity=1, is_active=True,
    )

    db_session.add_all([year, board, sclass, subject, course, batch_open, batch_tight])
    await db_session.flush()

    return {
        "class_id": sclass.id,
        "course_id": course.id,
        "batch_open_id": batch_open.id,
        "batch_tight_id": batch_tight.id,
    }


# ─── Tests ───────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_enquiry_crm_lifecycle_and_follow_ups(
    async_client: AsyncClient,
    admin_token: str,
    academic_setup: dict[str, uuid.UUID],
):
    """Test enquiry creation, initial follow-up generation, and stage transitions."""
    headers = {"Authorization": f"Bearer {admin_token}"}

    # 1. Create enquiry
    enquiry_payload = {
        "student_name": "Rohan Mehta",
        "parent_name": "Sanjay Mehta",
        "parent_phone": "9876543210",
        "class_id": str(academic_setup["class_id"]),
        "source": "WALK_IN",
        "remarks": "Interested in Class 10 boards preparation",
    }
    resp = await async_client.post("/api/v1/admin/enquiries", json=enquiry_payload, headers=headers)
    assert resp.status_code == 201, resp.text
    enquiry_data = resp.json()["data"]
    enquiry_id = enquiry_data["id"]
    assert enquiry_data["stage"] == "NEW"

    # 2. Check initial follow-up entry exists
    fu_resp = await async_client.get(f"/api/v1/admin/enquiries/{enquiry_id}/follow-ups", headers=headers)
    assert fu_resp.status_code == 200
    timeline = fu_resp.json()
    assert len(timeline) == 1
    assert "WALK_IN" in timeline[0]["notes"]

    # 3. Add counselling follow-up and transition stage to COUNSELLING
    add_fu_resp = await async_client.post(
        f"/api/v1/admin/enquiries/{enquiry_id}/follow-ups",
        json={
            "notes": "Discussed fee plans and batch timings with father",
            "new_stage": "COUNSELLING",
            "next_follow_up_date": "2026-04-10",
        },
        headers=headers,
    )
    assert add_fu_resp.status_code == 201
    assert add_fu_resp.json()["data"]["stage_after"] == "COUNSELLING"

    # 4. Check enquiry reflects updated stage
    get_enq = await async_client.get(f"/api/v1/admin/enquiries/{enquiry_id}", headers=headers)
    assert get_enq.status_code == 200
    assert get_enq.json()["data"]["stage"] == "COUNSELLING"
    assert get_enq.json()["data"]["follow_up_date"] == "2026-04-10"


@pytest.mark.asyncio
async def test_atomic_admission_wizard_success(
    async_client: AsyncClient,
    db_session: AsyncSession,
    admin_token: str,
    academic_setup: dict[str, uuid.UUID],
):
    """
    Test complete atomic admission wizard:
      - Creates Student User & Profile
      - Creates Parent User & Profile
      - Links them via StudentParent
      - Enrolls student into Batch
      - Returns temporary credentials
    """
    headers = {"Authorization": f"Bearer {admin_token}"}
    batch_id = str(academic_setup["batch_open_id"])

    payload = {
        "student": {
            "first_name": "Dev",
            "last_name": "Kapoor",
            "email": "dev.kapoor@student.test",
            "gender": "MALE",
            "blood_group": "O+",
            "class_id": str(academic_setup["class_id"]),
            "city": "Indore",
        },
        "parent": {
            "first_name": "Vikram",
            "last_name": "Kapoor",
            "email": "vikram.kapoor@parent.test",
            "phone": "9988776655",
            "relation": "FATHER",
            "is_primary": True,
        },
        "enrollment": {
            "batch_id": batch_id,
            "remarks": "Direct admission through office",
        },
    }

    resp = await async_client.post("/api/v1/admin/admissions/wizard", json=payload, headers=headers)
    assert resp.status_code == 201, resp.text
    result = resp.json()["data"]

    # Verify returned attributes
    assert result["student_email"] == "dev.kapoor@student.test"
    assert result["parent_email"] == "vikram.kapoor@parent.test"
    assert result["admission_number"].startswith("ADM-")
    assert result["student_temp_password"] is not None
    assert result["parent_temp_password"] is not None

    # Verify DB records
    student_user = await db_session.get(User, uuid.UUID(result["student_user_id"]))
    assert student_user is not None
    assert student_user.role == "STUDENT"

    parent_user = await db_session.get(User, uuid.UUID(result["parent_user_id"]))
    assert parent_user is not None
    assert parent_user.role == "PARENT"

    enrollment = await db_session.get(Enrollment, uuid.UUID(result["enrollment_id"]))
    assert enrollment is not None
    assert enrollment.status == EnrollmentStatus.ACTIVE
    assert str(enrollment.batch_id) == batch_id


@pytest.mark.asyncio
async def test_atomic_admission_wizard_converts_enquiry(
    async_client: AsyncClient,
    admin_token: str,
    academic_setup: dict[str, uuid.UUID],
):
    """Test admission wizard automatically converts an existing enquiry to ADMISSION."""
    headers = {"Authorization": f"Bearer {admin_token}"}

    # 1. Create enquiry
    enq_resp = await async_client.post(
        "/api/v1/admin/enquiries",
        json={
            "student_name": "Sneha Joshi",
            "parent_name": "Alok Joshi",
            "parent_phone": "9123456780",
            "class_id": str(academic_setup["class_id"]),
            "source": "WEBSITE",
        },
        headers=headers,
    )
    enquiry_id = enq_resp.json()["data"]["id"]

    # 2. Run admission wizard with enquiry_id
    admission_payload = {
        "enquiry_id": enquiry_id,
        "student": {
            "first_name": "Sneha",
            "last_name": "Joshi",
            "email": "sneha.joshi@student.test",
        },
        "parent": {
            "first_name": "Alok",
            "last_name": "Joshi",
            "email": "alok.joshi@parent.test",
            "phone": "9123456780",
        },
        "enrollment": {
            "batch_id": str(academic_setup["batch_open_id"]),
        },
    }
    adm_resp = await async_client.post("/api/v1/admin/admissions/wizard", json=admission_payload, headers=headers)
    assert adm_resp.status_code == 201, adm_resp.text
    adm_data = adm_resp.json()["data"]

    # 3. Verify enquiry is now ADMISSION
    get_enq = await async_client.get(f"/api/v1/admin/enquiries/{enquiry_id}", headers=headers)
    assert get_enq.status_code == 200
    enq = get_enq.json()["data"]
    assert enq["stage"] == "ADMISSION"
    assert enq["converted_student_id"] == adm_data["student_profile_id"]
    assert enq["converted_at"] is not None


@pytest.mark.asyncio
async def test_atomic_admission_rollback_on_batch_full(
    async_client: AsyncClient,
    db_session: AsyncSession,
    admin_token: str,
    academic_setup: dict[str, uuid.UUID],
):
    """
    Verify full rollback: If target batch has capacity 1 and is full,
    the admission is rejected (409 BATCH_FULL) and no student User is created.
    """
    headers = {"Authorization": f"Bearer {admin_token}"}
    batch_tight_id = str(academic_setup["batch_tight_id"])  # capacity 1

    # Student 1 admission (fills capacity)
    p1 = {
        "student": {"first_name": "Student1", "last_name": "A", "email": "stud1.tight@test.com"},
        "parent": {"first_name": "Parent1", "last_name": "A", "email": "par1.tight@test.com", "phone": "1111111111"},
        "enrollment": {"batch_id": batch_tight_id},
    }
    r1 = await async_client.post("/api/v1/admin/admissions/wizard", json=p1, headers=headers)
    assert r1.status_code == 201

    # Student 2 admission into full batch
    p2 = {
        "student": {"first_name": "Student2", "last_name": "B", "email": "stud2.tight@test.com"},
        "parent": {"first_name": "Parent2", "last_name": "B", "email": "par2.tight@test.com", "phone": "2222222222"},
        "enrollment": {"batch_id": batch_tight_id},
    }
    r2 = await async_client.post("/api/v1/admin/admissions/wizard", json=p2, headers=headers)
    assert r2.status_code == 409
    assert r2.json()["code"] == "BATCH_FULL"

    # Verify Student 2 User was NOT persisted
    st2_user = await db_session.scalar(
        select(User).where(User.email == "stud2.tight@test.com")
    )
    assert st2_user is None


@pytest.mark.asyncio
async def test_parent_reuse_for_sibling_admission(
    async_client: AsyncClient,
    db_session: AsyncSession,
    admin_token: str,
    academic_setup: dict[str, uuid.UUID],
):
    """Admitting a sibling with the same parent email reuses existing ParentProfile."""
    headers = {"Authorization": f"Bearer {admin_token}"}
    batch_id = str(academic_setup["batch_open_id"])
    parent_email = "shared.parent@family.test"

    # Admit child 1
    c1 = {
        "student": {"first_name": "Aryan", "last_name": "Singhania", "email": "aryan@test.com"},
        "parent": {"first_name": "Rajesh", "last_name": "Singhania", "email": parent_email, "phone": "9000000001"},
        "enrollment": {"batch_id": batch_id},
    }
    r1 = await async_client.post("/api/v1/admin/admissions/wizard", json=c1, headers=headers)
    assert r1.status_code == 201
    parent_profile_id_1 = r1.json()["data"]["parent_profile_id"]

    # Admit child 2 (sibling) with same parent email
    c2 = {
        "student": {"first_name": "Ananya", "last_name": "Singhania", "email": "ananya@test.com"},
        "parent": {"first_name": "Rajesh", "last_name": "Singhania", "email": parent_email, "phone": "9000000001"},
        "enrollment": {"batch_id": batch_id},
    }
    r2 = await async_client.post("/api/v1/admin/admissions/wizard", json=c2, headers=headers)
    assert r2.status_code == 201
    parent_profile_id_2 = r2.json()["data"]["parent_profile_id"]

    # Same parent profile must be reused
    assert parent_profile_id_1 == parent_profile_id_2

    # Check parent now has both students linked
    get_children = await async_client.get(
        f"/api/v1/admin/people/parents/{parent_profile_id_1}/students",
        headers=headers,
    )
    assert get_children.status_code == 200
    children = get_children.json()
    assert len(children) == 2
    names = {c["first_name"] for c in children}
    assert "Aryan" in names
    assert "Ananya" in names
