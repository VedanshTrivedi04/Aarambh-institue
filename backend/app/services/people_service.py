"""
app/services/people_service.py
------------------------------
Service layer for domain people profiles:
  - StudentProfile
  - TeacherProfile
  - ParentProfile
  - StaffProfile
  - StudentParent link management

Architecture rules:
  - Profiles are domain records separate from auth identity (User).
  - Every profile is linked to a User via unique user_id.
  - Queries are tenant-isolated by institute_id.
  - Soft-deletes are respected (deleted_at IS NULL).
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime

from sqlalchemy import func, or_, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import (
    ConflictError,
    NotFoundError,
    ValidationError,
)
from app.core.logging import get_logger
from app.models.academic_structure import SchoolClass
from app.models.people import (
    ParentProfile,
    StaffProfile,
    StudentParent,
    StudentProfile,
    TeacherProfile,
)
from app.models.user import User
from app.schemas.people import (
    ParentProfileCreate,
    ParentProfileUpdate,
    StaffProfileCreate,
    StaffProfileUpdate,
    StudentProfileCreate,
    StudentProfileUpdate,
    TeacherOnboardRequest,
    TeacherProfileCreate,
    TeacherProfileUpdate,
)

logger = get_logger(__name__)


class PeopleService:
    """Central service managing all domain person profiles and parent links."""

    # ─────────────────────────────────────────────────────────────────────────
    # StudentProfile
    # ─────────────────────────────────────────────────────────────────────────

    @staticmethod
    async def create_student_profile(
        db: AsyncSession,
        data: StudentProfileCreate,
        institute_id: uuid.UUID | None,
    ) -> StudentProfile:
        # Verify user exists and is not deleted
        user = await db.get(User, data.user_id)
        if not user or user.deleted_at is not None:
            raise NotFoundError(f"User {data.user_id} not found")

        # Check user doesn't already have a StudentProfile
        existing = await db.scalar(
            select(StudentProfile).where(
                StudentProfile.user_id == data.user_id,
                StudentProfile.deleted_at.is_(None),
            )
        )
        if existing:
            raise ConflictError("A student profile already exists for this user")

        # Check unique admission_number within institute if provided
        if data.admission_number and institute_id:
            duplicate_adm = await db.scalar(
                select(StudentProfile).where(
                    StudentProfile.institute_id == institute_id,
                    StudentProfile.admission_number == data.admission_number,
                    StudentProfile.deleted_at.is_(None),
                )
            )
            if duplicate_adm:
                raise ConflictError(f"Admission number '{data.admission_number}' is already assigned")

        # Validate class if provided
        if data.current_class_id:
            cls = await db.get(SchoolClass, data.current_class_id)
            if not cls or cls.deleted_at is not None:
                raise NotFoundError(f"Class {data.current_class_id} not found")

        profile = StudentProfile(
            institute_id=institute_id,
            user_id=data.user_id,
            first_name=data.first_name,
            last_name=data.last_name,
            date_of_birth=data.date_of_birth,
            gender=data.gender,
            blood_group=data.blood_group,
            admission_number=data.admission_number,
            current_class_id=data.current_class_id,
            joining_date=data.joining_date,
            address_line1=data.address_line1,
            address_line2=data.address_line2,
            city=data.city,
            state=data.state,
            pincode=data.pincode,
            emergency_contact_name=data.emergency_contact_name,
            emergency_contact_phone=data.emergency_contact_phone,
        )
        db.add(profile)
        await db.flush()
        await db.refresh(profile)
        logger.info("Created student profile", extra={"profile_id": str(profile.id), "user_id": str(data.user_id)})
        return profile

    @staticmethod
    async def get_student_profile(
        db: AsyncSession,
        profile_id: uuid.UUID,
        institute_id: uuid.UUID | None,
    ) -> StudentProfile:
        query = select(StudentProfile).where(
            StudentProfile.id == profile_id,
            StudentProfile.deleted_at.is_(None),
        )
        if institute_id:
            query = query.where(StudentProfile.institute_id == institute_id)
        profile = await db.scalar(query)
        if not profile:
            raise NotFoundError(f"Student profile {profile_id} not found")
        return profile

    @staticmethod
    async def get_student_by_user_id(
        db: AsyncSession,
        user_id: uuid.UUID,
        institute_id: uuid.UUID | None = None,
    ) -> StudentProfile | None:
        query = select(StudentProfile).where(
            StudentProfile.user_id == user_id,
            StudentProfile.deleted_at.is_(None),
        )
        if institute_id:
            query = query.where(StudentProfile.institute_id == institute_id)
        return await db.scalar(query)

    @staticmethod
    async def update_student_profile(
        db: AsyncSession,
        profile_id: uuid.UUID,
        data: StudentProfileUpdate,
        institute_id: uuid.UUID | None,
    ) -> StudentProfile:
        profile = await PeopleService.get_student_profile(db, profile_id, institute_id)
        update_data = data.model_dump(exclude_unset=True)

        if "current_class_id" in update_data and update_data["current_class_id"] is not None:
            cls = await db.get(SchoolClass, update_data["current_class_id"])
            if not cls or cls.deleted_at is not None:
                raise NotFoundError(f"Class {update_data['current_class_id']} not found")

        for field, value in update_data.items():
            setattr(profile, field, value)

        await db.flush()
        await db.refresh(profile)
        logger.info("Updated student profile", extra={"profile_id": str(profile_id)})
        return profile

    @staticmethod
    async def list_students(
        db: AsyncSession,
        institute_id: uuid.UUID | None,
        class_id: uuid.UUID | None = None,
        search: str | None = None,
        skip: int = 0,
        limit: int = 50,
    ) -> tuple[list[StudentProfile], int]:
        base_query = select(StudentProfile).where(StudentProfile.deleted_at.is_(None))
        if institute_id:
            base_query = base_query.where(StudentProfile.institute_id == institute_id)
        if class_id:
            base_query = base_query.where(StudentProfile.current_class_id == class_id)
        if search:
            term = f"%{search.strip()}%"
            base_query = base_query.where(
                or_(
                    StudentProfile.first_name.ilike(term),
                    StudentProfile.last_name.ilike(term),
                    StudentProfile.admission_number.ilike(term),
                )
            )

        total = await db.scalar(select(func.count()).select_from(base_query.subquery())) or 0
        items = (
            await db.scalars(
                base_query.order_by(StudentProfile.first_name, StudentProfile.last_name)
                .offset(skip)
                .limit(limit)
            )
        ).all()
        return list(items), total

    @staticmethod
    async def soft_delete_student_profile(
        db: AsyncSession,
        profile_id: uuid.UUID,
        institute_id: uuid.UUID | None,
    ) -> None:
        profile = await PeopleService.get_student_profile(db, profile_id, institute_id)
        profile.deleted_at = datetime.now(UTC)
        profile.is_active = False
        await db.flush()
        logger.info("Soft deleted student profile", extra={"profile_id": str(profile_id)})

    # ─────────────────────────────────────────────────────────────────────────
    # TeacherProfile
    # ─────────────────────────────────────────────────────────────────────────

    @staticmethod
    async def create_teacher_profile(
        db: AsyncSession,
        data: TeacherProfileCreate,
        institute_id: uuid.UUID | None,
    ) -> TeacherProfile:
        user = await db.get(User, data.user_id)
        if not user or user.deleted_at is not None:
            raise NotFoundError(f"User {data.user_id} not found")

        existing = await db.scalar(
            select(TeacherProfile).where(
                TeacherProfile.user_id == data.user_id,
                TeacherProfile.deleted_at.is_(None),
            )
        )
        if existing:
            raise ConflictError("A teacher profile already exists for this user")

        if data.employee_code and institute_id:
            duplicate_code = await db.scalar(
                select(TeacherProfile).where(
                    TeacherProfile.institute_id == institute_id,
                    TeacherProfile.employee_code == data.employee_code,
                    TeacherProfile.deleted_at.is_(None),
                )
            )
            if duplicate_code:
                raise ConflictError(f"Employee code '{data.employee_code}' is already assigned")

        profile = TeacherProfile(
            institute_id=institute_id,
            user_id=data.user_id,
            first_name=data.first_name,
            last_name=data.last_name,
            date_of_birth=data.date_of_birth,
            gender=data.gender,
            employee_code=data.employee_code,
            qualification=data.qualification,
            experience_years=data.experience_years,
            joining_date=data.joining_date,
            personal_email=data.personal_email,
            personal_phone=data.personal_phone,
            address=data.address,
        )
        db.add(profile)
        await db.flush()
        await db.refresh(profile)
        logger.info("Created teacher profile", extra={"profile_id": str(profile.id), "user_id": str(data.user_id)})
        return profile

    @staticmethod
    async def onboard_teacher(
        db: AsyncSession,
        data: TeacherOnboardRequest,
        institute_id: uuid.UUID | None,
    ) -> tuple[TeacherProfile, str | None]:
        """
        Atomically creates the TEACHER login account (User) and TeacherProfile.
        Returns (profile, temp_password) — temp_password is None when the
        caller supplied their own password.
        """
        import secrets

        from app.core.security import hash_password
        from app.models.user import UserStatus

        email = data.email.lower().strip()
        existing_user = await db.scalar(select(User).where(User.email == email))
        if existing_user:
            raise ConflictError(f"A user with email '{email}' already exists")

        if data.employee_code and institute_id:
            duplicate_code = await db.scalar(
                select(TeacherProfile).where(
                    TeacherProfile.institute_id == institute_id,
                    TeacherProfile.employee_code == data.employee_code,
                    TeacherProfile.deleted_at.is_(None),
                )
            )
            if duplicate_code:
                raise ConflictError(f"Employee code '{data.employee_code}' is already assigned")

        temp_password: str | None = None
        plain_password = data.password or secrets.token_urlsafe(10)
        if not data.password:
            temp_password = plain_password

        user = User(
            institute_id=institute_id,
            email=email,
            password_hash=hash_password(plain_password),
            role="TEACHER",
            status=UserStatus.ACTIVE,
            is_active=True,
        )
        db.add(user)
        await db.flush()

        profile = TeacherProfile(
            institute_id=institute_id,
            user_id=user.id,
            first_name=data.first_name,
            last_name=data.last_name,
            employee_code=data.employee_code,
            qualification=data.qualification,
            experience_years=data.experience_years,
            personal_email=email,
            personal_phone=data.personal_phone,
        )
        db.add(profile)
        await db.flush()
        await db.refresh(profile)

        logger.info(
            "Onboarded teacher",
            extra={"profile_id": str(profile.id), "user_id": str(user.id)},
        )
        return profile, temp_password

    @staticmethod
    async def get_teacher_profile(
        db: AsyncSession,
        profile_id: uuid.UUID,
        institute_id: uuid.UUID | None,
    ) -> TeacherProfile:
        query = select(TeacherProfile).where(
            TeacherProfile.id == profile_id,
            TeacherProfile.deleted_at.is_(None),
        )
        if institute_id:
            query = query.where(TeacherProfile.institute_id == institute_id)
        profile = await db.scalar(query)
        if not profile:
            raise NotFoundError(f"Teacher profile {profile_id} not found")
        return profile

    @staticmethod
    async def get_teacher_by_user_id(
        db: AsyncSession,
        user_id: uuid.UUID,
        institute_id: uuid.UUID | None = None,
    ) -> TeacherProfile | None:
        query = select(TeacherProfile).where(
            TeacherProfile.user_id == user_id,
            TeacherProfile.deleted_at.is_(None),
        )
        if institute_id:
            query = query.where(TeacherProfile.institute_id == institute_id)
        return await db.scalar(query)

    @staticmethod
    async def update_teacher_profile(
        db: AsyncSession,
        profile_id: uuid.UUID,
        data: TeacherProfileUpdate,
        institute_id: uuid.UUID | None,
    ) -> TeacherProfile:
        profile = await PeopleService.get_teacher_profile(db, profile_id, institute_id)
        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(profile, field, value)
        await db.flush()
        await db.refresh(profile)
        logger.info("Updated teacher profile", extra={"profile_id": str(profile_id)})
        return profile

    @staticmethod
    async def list_teachers(
        db: AsyncSession,
        institute_id: uuid.UUID | None,
        search: str | None = None,
        skip: int = 0,
        limit: int = 50,
    ) -> tuple[list[TeacherProfile], int]:
        base_query = select(TeacherProfile).where(TeacherProfile.deleted_at.is_(None))
        if institute_id:
            base_query = base_query.where(TeacherProfile.institute_id == institute_id)
        if search:
            term = f"%{search.strip()}%"
            base_query = base_query.where(
                or_(
                    TeacherProfile.first_name.ilike(term),
                    TeacherProfile.last_name.ilike(term),
                    TeacherProfile.employee_code.ilike(term),
                )
            )

        total = await db.scalar(select(func.count()).select_from(base_query.subquery())) or 0
        items = (
            await db.scalars(
                base_query.order_by(TeacherProfile.first_name, TeacherProfile.last_name)
                .offset(skip)
                .limit(limit)
            )
        ).all()
        return list(items), total

    @staticmethod
    async def soft_delete_teacher_profile(
        db: AsyncSession,
        profile_id: uuid.UUID,
        institute_id: uuid.UUID | None,
    ) -> None:
        profile = await PeopleService.get_teacher_profile(db, profile_id, institute_id)
        profile.deleted_at = datetime.now(UTC)
        profile.is_active = False
        await db.flush()
        logger.info("Soft deleted teacher profile", extra={"profile_id": str(profile_id)})

    # ─────────────────────────────────────────────────────────────────────────
    # ParentProfile
    # ─────────────────────────────────────────────────────────────────────────

    @staticmethod
    async def create_parent_profile(
        db: AsyncSession,
        data: ParentProfileCreate,
        institute_id: uuid.UUID | None,
    ) -> ParentProfile:
        user = await db.get(User, data.user_id)
        if not user or user.deleted_at is not None:
            raise NotFoundError(f"User {data.user_id} not found")

        existing = await db.scalar(
            select(ParentProfile).where(
                ParentProfile.user_id == data.user_id,
                ParentProfile.deleted_at.is_(None),
            )
        )
        if existing:
            raise ConflictError("A parent profile already exists for this user")

        profile = ParentProfile(
            institute_id=institute_id,
            user_id=data.user_id,
            first_name=data.first_name,
            last_name=data.last_name,
            relation=data.relation,
            occupation=data.occupation,
            annual_income=data.annual_income,
            address=data.address,
        )
        db.add(profile)
        await db.flush()
        await db.refresh(profile)
        logger.info("Created parent profile", extra={"profile_id": str(profile.id), "user_id": str(data.user_id)})
        return profile

    @staticmethod
    async def get_parent_profile(
        db: AsyncSession,
        profile_id: uuid.UUID,
        institute_id: uuid.UUID | None,
    ) -> ParentProfile:
        query = select(ParentProfile).where(
            ParentProfile.id == profile_id,
            ParentProfile.deleted_at.is_(None),
        )
        if institute_id:
            query = query.where(ParentProfile.institute_id == institute_id)
        profile = await db.scalar(query)
        if not profile:
            raise NotFoundError(f"Parent profile {profile_id} not found")
        return profile

    @staticmethod
    async def get_parent_by_user_id(
        db: AsyncSession,
        user_id: uuid.UUID,
        institute_id: uuid.UUID | None = None,
    ) -> ParentProfile | None:
        query = select(ParentProfile).where(
            ParentProfile.user_id == user_id,
            ParentProfile.deleted_at.is_(None),
        )
        if institute_id:
            query = query.where(ParentProfile.institute_id == institute_id)
        return await db.scalar(query)

    @staticmethod
    async def update_parent_profile(
        db: AsyncSession,
        profile_id: uuid.UUID,
        data: ParentProfileUpdate,
        institute_id: uuid.UUID | None,
    ) -> ParentProfile:
        profile = await PeopleService.get_parent_profile(db, profile_id, institute_id)
        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(profile, field, value)
        await db.flush()
        await db.refresh(profile)
        logger.info("Updated parent profile", extra={"profile_id": str(profile_id)})
        return profile

    @staticmethod
    async def list_parents(
        db: AsyncSession,
        institute_id: uuid.UUID | None,
        search: str | None = None,
        skip: int = 0,
        limit: int = 50,
    ) -> tuple[list[ParentProfile], int]:
        base_query = select(ParentProfile).where(ParentProfile.deleted_at.is_(None))
        if institute_id:
            base_query = base_query.where(ParentProfile.institute_id == institute_id)
        if search:
            term = f"%{search.strip()}%"
            base_query = base_query.where(
                or_(
                    ParentProfile.first_name.ilike(term),
                    ParentProfile.last_name.ilike(term),
                )
            )

        total = await db.scalar(select(func.count()).select_from(base_query.subquery())) or 0
        items = (
            await db.scalars(
                base_query.order_by(ParentProfile.first_name, ParentProfile.last_name)
                .offset(skip)
                .limit(limit)
            )
        ).all()
        return list(items), total

    # ─────────────────────────────────────────────────────────────────────────
    # StaffProfile
    # ─────────────────────────────────────────────────────────────────────────

    @staticmethod
    async def create_staff_profile(
        db: AsyncSession,
        data: StaffProfileCreate,
        institute_id: uuid.UUID | None,
    ) -> StaffProfile:
        user = await db.get(User, data.user_id)
        if not user or user.deleted_at is not None:
            raise NotFoundError(f"User {data.user_id} not found")

        existing = await db.scalar(
            select(StaffProfile).where(
                StaffProfile.user_id == data.user_id,
                StaffProfile.deleted_at.is_(None),
            )
        )
        if existing:
            raise ConflictError("A staff profile already exists for this user")

        if data.employee_code and institute_id:
            duplicate_code = await db.scalar(
                select(StaffProfile).where(
                    StaffProfile.institute_id == institute_id,
                    StaffProfile.employee_code == data.employee_code,
                    StaffProfile.deleted_at.is_(None),
                )
            )
            if duplicate_code:
                raise ConflictError(f"Employee code '{data.employee_code}' is already assigned")

        profile = StaffProfile(
            institute_id=institute_id,
            user_id=data.user_id,
            first_name=data.first_name,
            last_name=data.last_name,
            designation=data.designation,
            department=data.department,
            employee_code=data.employee_code,
            joining_date=data.joining_date,
            address=data.address,
        )
        db.add(profile)
        await db.flush()
        await db.refresh(profile)
        logger.info("Created staff profile", extra={"profile_id": str(profile.id), "user_id": str(data.user_id)})
        return profile

    @staticmethod
    async def get_staff_profile(
        db: AsyncSession,
        profile_id: uuid.UUID,
        institute_id: uuid.UUID | None,
    ) -> StaffProfile:
        query = select(StaffProfile).where(
            StaffProfile.id == profile_id,
            StaffProfile.deleted_at.is_(None),
        )
        if institute_id:
            query = query.where(StaffProfile.institute_id == institute_id)
        profile = await db.scalar(query)
        if not profile:
            raise NotFoundError(f"Staff profile {profile_id} not found")
        return profile

    @staticmethod
    async def get_staff_by_user_id(
        db: AsyncSession,
        user_id: uuid.UUID,
        institute_id: uuid.UUID | None = None,
    ) -> StaffProfile | None:
        query = select(StaffProfile).where(
            StaffProfile.user_id == user_id,
            StaffProfile.deleted_at.is_(None),
        )
        if institute_id:
            query = query.where(StaffProfile.institute_id == institute_id)
        return await db.scalar(query)

    @staticmethod
    async def update_staff_profile(
        db: AsyncSession,
        profile_id: uuid.UUID,
        data: StaffProfileUpdate,
        institute_id: uuid.UUID | None,
    ) -> StaffProfile:
        profile = await PeopleService.get_staff_profile(db, profile_id, institute_id)
        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(profile, field, value)
        await db.flush()
        await db.refresh(profile)
        logger.info("Updated staff profile", extra={"profile_id": str(profile_id)})
        return profile

    @staticmethod
    async def list_staff(
        db: AsyncSession,
        institute_id: uuid.UUID | None,
        search: str | None = None,
        skip: int = 0,
        limit: int = 50,
    ) -> tuple[list[StaffProfile], int]:
        base_query = select(StaffProfile).where(StaffProfile.deleted_at.is_(None))
        if institute_id:
            base_query = base_query.where(StaffProfile.institute_id == institute_id)
        if search:
            term = f"%{search.strip()}%"
            base_query = base_query.where(
                or_(
                    StaffProfile.first_name.ilike(term),
                    StaffProfile.last_name.ilike(term),
                    StaffProfile.employee_code.ilike(term),
                )
            )

        total = await db.scalar(select(func.count()).select_from(base_query.subquery())) or 0
        items = (
            await db.scalars(
                base_query.order_by(StaffProfile.first_name, StaffProfile.last_name)
                .offset(skip)
                .limit(limit)
            )
        ).all()
        return list(items), total

    # ─────────────────────────────────────────────────────────────────────────
    # StudentParent Links
    # ─────────────────────────────────────────────────────────────────────────

    @staticmethod
    async def link_parent_to_student(
        db: AsyncSession,
        student_id: uuid.UUID,
        parent_id: uuid.UUID,
        is_primary: bool,
        institute_id: uuid.UUID | None,
    ) -> StudentParent:
        # Validate student and parent exist
        student = await PeopleService.get_student_profile(db, student_id, institute_id)
        parent = await PeopleService.get_parent_profile(db, parent_id, institute_id)

        # Check existing link
        existing = await db.scalar(
            select(StudentParent).where(
                StudentParent.student_id == student.id,
                StudentParent.parent_id == parent.id,
            )
        )
        if existing:
            raise ConflictError("This parent is already linked to this student")

        # If primary, reset existing primary links for this student
        if is_primary:
            await db.execute(
                update(StudentParent)
                .where(StudentParent.student_id == student.id)
                .values(is_primary=False)
            )

        link = StudentParent(
            student_id=student.id,
            parent_id=parent.id,
            is_primary=is_primary,
        )
        db.add(link)
        await db.flush()
        await db.refresh(link)
        logger.info(
            "Linked parent to student",
            extra={"student_id": str(student.id), "parent_id": str(parent.id), "is_primary": is_primary},
        )
        return link

    @staticmethod
    async def unlink_parent_from_student(
        db: AsyncSession,
        student_id: uuid.UUID,
        parent_id: uuid.UUID,
        institute_id: uuid.UUID | None,
    ) -> None:
        await PeopleService.get_student_profile(db, student_id, institute_id)
        link = await db.scalar(
            select(StudentParent).where(
                StudentParent.student_id == student_id,
                StudentParent.parent_id == parent_id,
            )
        )
        if not link:
            raise NotFoundError(f"Link between student {student_id} and parent {parent_id} not found")
        await db.delete(link)
        await db.flush()
        logger.info("Unlinked parent from student", extra={"student_id": str(student_id), "parent_id": str(parent_id)})

    @staticmethod
    async def get_parents_for_student(
        db: AsyncSession,
        student_id: uuid.UUID,
        institute_id: uuid.UUID | None,
    ) -> list[ParentProfile]:
        await PeopleService.get_student_profile(db, student_id, institute_id)
        query = (
            select(ParentProfile)
            .join(StudentParent, StudentParent.parent_id == ParentProfile.id)
            .where(
                StudentParent.student_id == student_id,
                ParentProfile.deleted_at.is_(None),
            )
        )
        return list((await db.scalars(query)).all())

    @staticmethod
    async def get_students_for_parent(
        db: AsyncSession,
        parent_id: uuid.UUID,
        institute_id: uuid.UUID | None,
    ) -> list[StudentProfile]:
        await PeopleService.get_parent_profile(db, parent_id, institute_id)
        query = (
            select(StudentProfile)
            .join(StudentParent, StudentParent.student_id == StudentProfile.id)
            .where(
                StudentParent.parent_id == parent_id,
                StudentProfile.deleted_at.is_(None),
            )
        )
        return list((await db.scalars(query)).all())
