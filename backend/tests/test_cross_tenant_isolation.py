"""
tests/test_cross_tenant_isolation.py
------------------------------------
Security & Multi-Tenancy test suite for Slice 12: Platform & Production Hardening.

Verifies strict tenant isolation across:
  1. Academic Structure: Tenant B administrator cannot read or mutate Tenant A batches.
  2. People & Profiles: Tenant B administrator cannot view or modify Tenant A student profiles.
  3. Student 360° Profile: Cross-tenant access is rejected with 403/404.
  4. Batch Performance Analytics: Tenant B administrator/teacher cannot access Tenant A metrics.
  5. Data Streaming CSV Exports: Tenant B export never leaks Tenant A student data.
"""

from __future__ import annotations

import uuid
from datetime import date, datetime, timedelta, timezone

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import create_access_token, hash_password
from app.models.academic_structure import AcademicYear, Batch, Board, Course, SchoolClass, Subject
from app.models.enrollment import Enrollment, EnrollmentStatus
from app.models.institute import Institute
from app.models.people import StudentProfile, TeacherProfile
from app.models.user import User, UserStatus


async def _create_tenant_environment(db: AsyncSession, suffix: str) -> dict[str, any]:
    # 1. Institute
    inst = Institute(
        id=uuid.uuid4(),
        name=f"Institute {suffix}",
        code=f"INST_{suffix}_{uuid.uuid4().hex[:4].upper()}",
        is_active=True,
    )
    db.add(inst)
    await db.flush()

    # 2. Admin User
    admin = User(
        id=uuid.uuid4(), institute_id=inst.id,
        email=f"admin_{suffix}_{uuid.uuid4().hex[:6]}@erp.com",
        password_hash=hash_password("Pass123!"),
        role="ADMIN", status=UserStatus.ACTIVE, is_active=True, is_verified=True,
    )
    db.add(admin)
    await db.flush()
    token_admin, _, _ = create_access_token(str(admin.id), admin.role)

    # 3. Student User & Profile
    student_user = User(
        id=uuid.uuid4(), institute_id=inst.id,
        email=f"student_{suffix}_{uuid.uuid4().hex[:6]}@erp.com",
        password_hash=hash_password("Pass123!"),
        role="STUDENT", status=UserStatus.ACTIVE, is_active=True, is_verified=True,
    )
    db.add(student_user)
    await db.flush()
    token_student, _, _ = create_access_token(str(student_user.id), student_user.role)

    student_prof = StudentProfile(
        id=uuid.uuid4(), institute_id=inst.id, user_id=student_user.id,
        first_name=f"StudentFirst_{suffix}", last_name=f"StudentLast_{suffix}",
        admission_number=f"ADM-{suffix}-001", is_active=True,
    )
    db.add(student_prof)
    await db.flush()

    # 4. Teacher User & Profile
    teacher_user = User(
        id=uuid.uuid4(), institute_id=inst.id,
        email=f"teacher_{suffix}_{uuid.uuid4().hex[:6]}@erp.com",
        password_hash=hash_password("Pass123!"),
        role="TEACHER", status=UserStatus.ACTIVE, is_active=True, is_verified=True,
    )
    db.add(teacher_user)
    await db.flush()
    token_teacher, _, _ = create_access_token(str(teacher_user.id), teacher_user.role)

    teacher_prof = TeacherProfile(
        id=uuid.uuid4(), institute_id=inst.id, user_id=teacher_user.id,
        first_name=f"Prof_{suffix}", last_name="Educator", is_active=True,
    )
    db.add(teacher_prof)
    await db.flush()

    # 5. Academic Structure (AY, Board, Class, Subject, Course, Batch)
    ay = AcademicYear(id=uuid.uuid4(), institute_id=inst.id, name=f"AY-{suffix}", start_date=date(2026, 4, 1), end_date=date(2027, 3, 31))
    board = Board(id=uuid.uuid4(), institute_id=inst.id, name=f"Board-{suffix}", code=f"B_{suffix}_{uuid.uuid4().hex[:4]}")
    sclass = SchoolClass(id=uuid.uuid4(), board_id=board.id, name=f"Class 10 {suffix}", display_order=10)
    sub = Subject(id=uuid.uuid4(), institute_id=inst.id, name=f"Subject {suffix}", code=f"S_{suffix}_{uuid.uuid4().hex[:4]}")
    db.add_all([ay, board, sclass, sub])
    await db.flush()

    course = Course(
        id=uuid.uuid4(), institute_id=inst.id, academic_year_id=ay.id, class_id=sclass.id,
        name=f"Course {suffix}", code=f"C_{suffix}_{uuid.uuid4().hex[:4]}",
    )
    db.add(course)
    await db.flush()

    batch = Batch(
        id=uuid.uuid4(), institute_id=inst.id, course_id=course.id, subject_id=sub.id,
        teacher_id=teacher_prof.id, name=f"Batch-{suffix}", capacity=40, is_active=True,
    )
    db.add(batch)
    await db.flush()

    # 6. Enrollment
    enrollment = Enrollment(
        id=uuid.uuid4(), institute_id=inst.id, batch_id=batch.id,
        student_id=student_prof.id, status=EnrollmentStatus.ACTIVE,
        enrollment_date=date(2026, 4, 10),
    )
    db.add(enrollment)
    await db.flush()

    return {
        "institute": inst,
        "admin_user": admin,
        "admin_token": token_admin,
        "student_prof": student_prof,
        "student_token": token_student,
        "teacher_prof": teacher_prof,
        "teacher_token": token_teacher,
        "batch": batch,
        "enrollment": enrollment,
    }


@pytest.fixture
async def multi_tenant_env(db_session: AsyncSession) -> dict[str, any]:
    tenant_a = await _create_tenant_environment(db_session, "ALPHA")
    tenant_b = await _create_tenant_environment(db_session, "BETA")
    return {"tenant_a": tenant_a, "tenant_b": tenant_b}


# ─────────────────────────────────────────────────────────────────────────────
# Test 1: Academic Structure Cross-Tenant Isolation
# ─────────────────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_cross_tenant_academic_structure_isolation(
    async_client: AsyncClient,
    multi_tenant_env: dict[str, any],
):
    a = multi_tenant_env["tenant_a"]
    b = multi_tenant_env["tenant_b"]

    batch_a_id = a["batch"].id
    token_b = b["admin_token"]

    # 1. Admin B attempts to fetch Batch A
    resp_get = await async_client.get(
        f"/api/v1/admin/academic/batches/{batch_a_id}",
        headers={"Authorization": f"Bearer {token_b}"},
    )
    assert resp_get.status_code in (403, 404), resp_get.text

    # 2. Admin B attempts to update Batch A
    resp_put = await async_client.put(
        f"/api/v1/admin/academic/batches/{batch_a_id}",
        headers={"Authorization": f"Bearer {token_b}"},
        json={"name": "Hacked Batch Name"},
    )
    assert resp_put.status_code in (403, 404), resp_put.text


# ─────────────────────────────────────────────────────────────────────────────
# Test 2: Student Profile Cross-Tenant Isolation
# ─────────────────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_cross_tenant_student_profile_isolation(
    async_client: AsyncClient,
    multi_tenant_env: dict[str, any],
):
    a = multi_tenant_env["tenant_a"]
    b = multi_tenant_env["tenant_b"]

    student_a_id = a["student_prof"].id
    token_b = b["admin_token"]

    # Admin B attempts to fetch Student A profile
    resp_get = await async_client.get(
        f"/api/v1/admin/students/{student_a_id}",
        headers={"Authorization": f"Bearer {token_b}"},
    )
    assert resp_get.status_code in (403, 404), resp_get.text

    # Admin B attempts to update Student A profile
    resp_patch = await async_client.patch(
        f"/api/v1/admin/students/{student_a_id}",
        headers={"Authorization": f"Bearer {token_b}"},
        json={"first_name": "TamperedName"},
    )
    assert resp_patch.status_code in (403, 404), resp_patch.text


# ─────────────────────────────────────────────────────────────────────────────
# Test 3: Student 360° Profile Cross-Tenant Isolation
# ─────────────────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_cross_tenant_student_360_isolation(
    async_client: AsyncClient,
    multi_tenant_env: dict[str, any],
):
    a = multi_tenant_env["tenant_a"]
    b = multi_tenant_env["tenant_b"]

    student_a_id = a["student_prof"].id
    token_admin_b = b["admin_token"]
    token_student_b = b["student_token"]

    # 1. Admin B attempts to retrieve Student A's 360 profile
    resp_admin = await async_client.get(
        f"/api/v1/analytics/students/{student_a_id}/360",
        headers={"Authorization": f"Bearer {token_admin_b}"},
    )
    assert resp_admin.status_code in (403, 404), resp_admin.text

    # 2. Student B attempts to retrieve Student A's 360 profile
    resp_student = await async_client.get(
        f"/api/v1/analytics/students/{student_a_id}/360",
        headers={"Authorization": f"Bearer {token_student_b}"},
    )
    assert resp_student.status_code in (403, 404), resp_student.text


# ─────────────────────────────────────────────────────────────────────────────
# Test 4: Batch Analytics Cross-Tenant Isolation
# ─────────────────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_cross_tenant_batch_analytics_isolation(
    async_client: AsyncClient,
    multi_tenant_env: dict[str, any],
):
    a = multi_tenant_env["tenant_a"]
    b = multi_tenant_env["tenant_b"]

    batch_a_id = a["batch"].id
    token_admin_b = b["admin_token"]
    token_teacher_b = b["teacher_token"]

    # 1. Admin B attempts to view Batch A analytics
    resp_admin = await async_client.get(
        f"/api/v1/analytics/batches/{batch_a_id}",
        headers={"Authorization": f"Bearer {token_admin_b}"},
    )
    assert resp_admin.status_code in (403, 404), resp_admin.text

    # 2. Teacher B attempts to view Batch A analytics
    resp_teacher = await async_client.get(
        f"/api/v1/analytics/batches/{batch_a_id}",
        headers={"Authorization": f"Bearer {token_teacher_b}"},
    )
    assert resp_teacher.status_code in (403, 404), resp_teacher.text


# ─────────────────────────────────────────────────────────────────────────────
# Test 5: CSV Streaming Data Export Isolation
# ─────────────────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_cross_tenant_csv_export_isolation(
    async_client: AsyncClient,
    multi_tenant_env: dict[str, any],
):
    a = multi_tenant_env["tenant_a"]
    b = multi_tenant_env["tenant_b"]

    token_b = b["admin_token"]
    student_a_first = a["student_prof"].first_name
    student_b_first = b["student_prof"].first_name

    # Admin B exports student roster
    resp = await async_client.get(
        "/api/v1/analytics/export?export_type=students_roster",
        headers={"Authorization": f"Bearer {token_b}"},
    )
    assert resp.status_code == 200
    csv_content = resp.text

    # Tenant B data MUST be present
    assert student_b_first in csv_content
    # Tenant A data MUST NEVER be leaked in Tenant B export
    assert student_a_first not in csv_content
