"""
app/services/admission_service.py
---------------------------------
Atomic Admission Wizard service.

Orchestrates multi-entity onboarding in a single atomic transaction:
  1. Student User + StudentProfile (with auto-generated admission number if needed)
  2. Parent User + ParentProfile (reusing existing parent by email if already registered)
  3. StudentParent association (with primary contact flag)
  4. Batch Enrollment (enforcing capacity guard and duplicate prevention)
  5. Enquiry conversion (marking stage = ADMISSION and logging timeline follow-up)
"""

from __future__ import annotations

import secrets
import uuid
from datetime import UTC, date, datetime

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import (
    BatchFullError,
    ConflictError,
    NotFoundError,
    ValidationError,
)
from app.core.logging import get_logger
from app.core.security import hash_password
from app.models.academic_structure import Batch
from app.models.enquiry import Enquiry, EnquiryFollowUp, EnquiryStage
from app.models.enrollment import Enrollment, EnrollmentStatus
from app.models.people import ParentProfile, StudentParent, StudentProfile
from app.models.user import User, UserStatus
from app.schemas.admission import AdmissionWizardRequest, AdmissionWizardResponse
from app.services.enrollment_service import EnrollmentService

logger = get_logger(__name__)


class AdmissionService:
    """Atomic multi-entity admission engine."""

    @staticmethod
    async def _generate_admission_number(
        db: AsyncSession, institute_id: uuid.UUID | None
    ) -> str:
        """Generate next sequence admission number for the institute (e.g. ADM-2025-0001)."""
        year_str = datetime.now(UTC).strftime("%Y")
        count_query = select(func.count(StudentProfile.id))
        if institute_id:
            count_query = count_query.where(StudentProfile.institute_id == institute_id)
        current_count = (await db.scalar(count_query)) or 0
        seq = current_count + 1

        # Double check uniqueness loop
        while True:
            candidate = f"ADM-{year_str}-{seq:04d}"
            exists_query = select(StudentProfile).where(
                StudentProfile.admission_number == candidate,
            )
            if institute_id:
                exists_query = exists_query.where(StudentProfile.institute_id == institute_id)
            if not await db.scalar(exists_query):
                return candidate
            seq += 1

    @staticmethod
    async def process_admission(
        db: AsyncSession,
        request: AdmissionWizardRequest,
        institute_id: uuid.UUID | None,
        processed_by: uuid.UUID | None = None,
    ) -> AdmissionWizardResponse:
        """
        Execute atomic admission workflow.
        Guarantees that all entities are created or all fail together.
        """
        # ── 1. Validate Target Batch & Pre-check Capacity ───────────────────
        batch = await db.scalar(
            select(Batch).where(
                Batch.id == request.enrollment.batch_id,
                Batch.deleted_at.is_(None),
            )
        )
        if not batch:
            raise NotFoundError(f"Batch {request.enrollment.batch_id} not found")
        if not batch.is_active:
            raise ValidationError(f"Batch '{batch.name}' is inactive and cannot accept new admissions")

        active_count = await EnrollmentService.get_active_enrollment_count(db, batch.id)
        if active_count >= batch.capacity:
            raise BatchFullError(
                f"Batch '{batch.name}' has reached capacity ({active_count}/{batch.capacity})"
            )

        # ── 2. Check Student User Uniqueness ────────────────────────────────
        existing_student_user = await db.scalar(
            select(User).where(
                User.email == request.student.email.lower().strip(),
                User.deleted_at.is_(None),
            )
        )
        if existing_student_user:
            raise ConflictError(f"A user with email '{request.student.email}' already exists")

        # ── 3. Handle Parent User & Profile ──────────────────────────────────
        parent_temp_password: str | None = None
        existing_parent_user = await db.scalar(
            select(User).where(
                User.email == request.parent.email.lower().strip(),
                User.deleted_at.is_(None),
            )
        )

        if existing_parent_user:
            # Reusing existing parent account
            parent_user = existing_parent_user
            parent_profile = await db.scalar(
                select(ParentProfile).where(
                    ParentProfile.user_id == parent_user.id,
                    ParentProfile.deleted_at.is_(None),
                )
            )
            if not parent_profile:
                # Create profile for existing user
                parent_profile = ParentProfile(
                    institute_id=institute_id,
                    user_id=parent_user.id,
                    first_name=request.parent.first_name,
                    last_name=request.parent.last_name,
                    relation=request.parent.relation,
                    occupation=request.parent.occupation,
                    annual_income=request.parent.annual_income,
                )
                db.add(parent_profile)
                await db.flush()
        else:
            # Create new parent User + ParentProfile
            parent_plain_pwd = request.parent.password or secrets.token_urlsafe(10)
            if not request.parent.password:
                parent_temp_password = parent_plain_pwd

            parent_user = User(
                institute_id=institute_id,
                email=request.parent.email.lower().strip(),
                password_hash=hash_password(parent_plain_pwd),
                role="PARENT",
                status=UserStatus.ACTIVE,
                is_active=True,
            )
            db.add(parent_user)
            await db.flush()

            parent_profile = ParentProfile(
                institute_id=institute_id,
                user_id=parent_user.id,
                first_name=request.parent.first_name,
                last_name=request.parent.last_name,
                relation=request.parent.relation,
                occupation=request.parent.occupation,
                annual_income=request.parent.annual_income,
            )
            db.add(parent_profile)
            await db.flush()

        # ── 4. Create Student User & Profile ─────────────────────────────────
        student_temp_password: str | None = None
        student_plain_pwd = request.student.password or secrets.token_urlsafe(10)
        if not request.student.password:
            student_temp_password = student_plain_pwd

        student_user = User(
            institute_id=institute_id,
            email=request.student.email.lower().strip(),
            password_hash=hash_password(student_plain_pwd),
            role="STUDENT",
            status=UserStatus.ACTIVE,
            is_active=True,
        )
        db.add(student_user)
        await db.flush()

        # Determine admission number
        admission_number = request.student.admission_number
        if not admission_number:
            admission_number = await AdmissionService._generate_admission_number(db, institute_id)
        else:
            # Verify custom admission number uniqueness in institute
            if institute_id:
                dup_adm = await db.scalar(
                    select(StudentProfile).where(
                        StudentProfile.institute_id == institute_id,
                        StudentProfile.admission_number == admission_number,
                        StudentProfile.deleted_at.is_(None),
                    )
                )
                if dup_adm:
                    raise ConflictError(f"Admission number '{admission_number}' is already assigned")

        student_profile = StudentProfile(
            institute_id=institute_id,
            user_id=student_user.id,
            first_name=request.student.first_name,
            last_name=request.student.last_name,
            date_of_birth=request.student.date_of_birth,
            gender=request.student.gender,
            blood_group=request.student.blood_group,
            admission_number=admission_number,
            current_class_id=request.student.class_id,
            joining_date=request.enrollment.enrollment_date or date.today(),
            address_line1=request.student.address_line1,
            city=request.student.city,
            state=request.student.state,
            pincode=request.student.pincode,
            emergency_contact_name=f"{request.parent.first_name} {request.parent.last_name}",
            emergency_contact_phone=request.parent.phone,
        )
        db.add(student_profile)
        await db.flush()

        # ── 5. Create StudentParent Link ─────────────────────────────────────
        student_parent_link = StudentParent(
            student_id=student_profile.id,
            parent_id=parent_profile.id,
            is_primary=request.parent.is_primary,
        )
        db.add(student_parent_link)
        await db.flush()

        # ── 6. Create Enrollment ─────────────────────────────────────────────
        enrollment = Enrollment(
            student_id=student_profile.id,
            batch_id=batch.id,
            institute_id=institute_id,
            status=EnrollmentStatus.ACTIVE,
            enrollment_date=request.enrollment.enrollment_date or date.today(),
            enrolled_by=processed_by,
            remarks=request.enrollment.remarks or f"Admitted into {batch.name}",
        )
        db.add(enrollment)
        await db.flush()

        # ── 7. Convert Enquiry If Provided ───────────────────────────────────
        if request.enquiry_id:
            enquiry = await db.scalar(
                select(Enquiry).where(
                    Enquiry.id == request.enquiry_id,
                    Enquiry.deleted_at.is_(None),
                )
            )
            if enquiry:
                stage_before = enquiry.stage
                enquiry.stage = EnquiryStage.ADMISSION
                enquiry.converted_student_id = student_profile.id
                enquiry.converted_at = datetime.now(UTC)

                follow_up = EnquiryFollowUp(
                    enquiry_id=enquiry.id,
                    author_id=processed_by,
                    stage_before=stage_before,
                    stage_after=EnquiryStage.ADMISSION,
                    notes=(
                        f"Converted to admission. Admission No: {admission_number}, "
                        f"Batch: {batch.name}."
                    ),
                    next_follow_up_date=None,
                )
                db.add(follow_up)
                await db.flush()

        logger.info(
            "Atomic admission completed successfully",
            extra={
                "student_id": str(student_profile.id),
                "admission_number": admission_number,
                "batch_id": str(batch.id),
                "enrollment_id": str(enrollment.id),
            },
        )

        return AdmissionWizardResponse(
            student_user_id=student_user.id,
            student_profile_id=student_profile.id,
            admission_number=admission_number,
            student_email=student_user.email,
            student_temp_password=student_temp_password,
            parent_user_id=parent_user.id,
            parent_profile_id=parent_profile.id,
            parent_email=parent_user.email,
            parent_temp_password=parent_temp_password,
            enrollment_id=enrollment.id,
            batch_id=batch.id,
            enquiry_id=request.enquiry_id,
            message=f"Student {student_profile.full_name} successfully admitted with No. {admission_number}",
        )
