"""
app/services/learning_service.py
--------------------------------
Service layer for Study Materials, Homework Assignments, and Student Submissions.
"""

from __future__ import annotations

import uuid
from datetime import UTC, date, datetime

from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.exceptions import (
    ConflictError,
    ForbiddenError,
    NotFoundError,
    ValidationError,
)
from app.core.logging import get_logger
from app.models.academic_structure import Batch
from app.models.enrollment import Enrollment, EnrollmentStatus
from app.models.learning import (
    FileAttachment,
    Homework,
    HomeworkSubmission,
    MaterialType,
    StudyMaterial,
    SubmissionStatus,
)
from app.models.people import StudentProfile, TeacherProfile
from app.models.user import User
from app.schemas.learning import (
    HomeworkCreate,
    HomeworkEvaluationRequest,
    HomeworkSubmissionCreate,
    HomeworkUpdate,
    StudyMaterialCreate,
    StudyMaterialUpdate,
)

logger = get_logger(__name__)


class LearningService:
    """Manages course/batch learning materials, assignments, and student submissions."""

    # ─────────────────────────────────────────────────────────────────────────
    # Study Material CRUD
    # ─────────────────────────────────────────────────────────────────────────

    @staticmethod
    async def create_study_material(
        db: AsyncSession,
        data: StudyMaterialCreate,
        institute_id: uuid.UUID | None,
        uploaded_by: uuid.UUID | None = None,
    ) -> StudyMaterial:
        if data.attachment_id:
            att = await db.get(FileAttachment, data.attachment_id)
            if not att:
                raise NotFoundError(f"Attachment {data.attachment_id} not found")

        material = StudyMaterial(
            institute_id=institute_id,
            title=data.title,
            type=data.type,
            description=data.description,
            target_course_id=data.target_course_id,
            target_batch_id=data.target_batch_id,
            attachment_id=data.attachment_id,
            uploaded_by=uploaded_by,
            is_published=data.is_published,
        )
        db.add(material)
        await db.flush()
        await db.refresh(material)
        logger.info("Created study material", extra={"material_id": str(material.id), "title": material.title})
        return material

    @staticmethod
    async def get_study_material(
        db: AsyncSession,
        material_id: uuid.UUID,
        institute_id: uuid.UUID | None,
    ) -> StudyMaterial:
        query = (
            select(StudyMaterial)
            .options(selectinload(StudyMaterial.attachment))
            .where(
                StudyMaterial.id == material_id,
                StudyMaterial.deleted_at.is_(None),
            )
        )
        if institute_id:
            query = query.where(StudyMaterial.institute_id == institute_id)
        material = await db.scalar(query)
        if not material:
            raise NotFoundError(f"Study material {material_id} not found")
        return material

    @staticmethod
    async def update_study_material(
        db: AsyncSession,
        material_id: uuid.UUID,
        data: StudyMaterialUpdate,
        institute_id: uuid.UUID | None,
    ) -> StudyMaterial:
        material = await LearningService.get_study_material(db, material_id, institute_id)
        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(material, field, value)
        await db.flush()
        await db.refresh(material)
        return material

    @staticmethod
    async def list_study_materials(
        db: AsyncSession,
        institute_id: uuid.UUID | None,
        course_id: uuid.UUID | None = None,
        batch_id: uuid.UUID | None = None,
        material_type: MaterialType | None = None,
        published_only: bool = True,
        skip: int = 0,
        limit: int = 50,
    ) -> tuple[list[StudyMaterial], int]:
        base_query = (
            select(StudyMaterial)
            .options(selectinload(StudyMaterial.attachment))
            .where(StudyMaterial.deleted_at.is_(None))
        )
        if institute_id:
            base_query = base_query.where(StudyMaterial.institute_id == institute_id)
        if published_only:
            base_query = base_query.where(StudyMaterial.is_published.is_(True))
        if course_id:
            base_query = base_query.where(
                or_(
                    StudyMaterial.target_course_id == course_id,
                    StudyMaterial.target_course_id.is_(None),
                )
            )
        if batch_id:
            base_query = base_query.where(
                or_(
                    StudyMaterial.target_batch_id == batch_id,
                    StudyMaterial.target_batch_id.is_(None),
                )
            )
        if material_type:
            base_query = base_query.where(StudyMaterial.type == material_type)

        total = await db.scalar(select(func.count()).select_from(base_query.subquery())) or 0
        items = (
            await db.scalars(
                base_query.order_by(StudyMaterial.created_at.desc()).offset(skip).limit(limit)
            )
        ).all()
        return list(items), total

    @staticmethod
    async def soft_delete_study_material(
        db: AsyncSession,
        material_id: uuid.UUID,
        institute_id: uuid.UUID | None,
    ) -> None:
        material = await LearningService.get_study_material(db, material_id, institute_id)
        material.deleted_at = datetime.now(UTC)
        await db.flush()

    # ─────────────────────────────────────────────────────────────────────────
    # Homework CRUD
    # ─────────────────────────────────────────────────────────────────────────

    @staticmethod
    async def create_homework(
        db: AsyncSession,
        data: HomeworkCreate,
        institute_id: uuid.UUID | None,
        created_by: uuid.UUID | None = None,
    ) -> Homework:
        batch = await db.get(Batch, data.batch_id)
        if not batch or batch.deleted_at is not None:
            raise NotFoundError(f"Batch {data.batch_id} not found")

        if data.attachment_id:
            att = await db.get(FileAttachment, data.attachment_id)
            if not att:
                raise NotFoundError(f"Attachment {data.attachment_id} not found")

        hw = Homework(
            institute_id=institute_id,
            batch_id=data.batch_id,
            subject_id=data.subject_id,
            title=data.title,
            instructions=data.instructions,
            chapter=data.chapter,
            due_date=data.due_date,
            attachment_id=data.attachment_id,
            created_by=created_by,
        )
        db.add(hw)
        await db.flush()
        await db.refresh(hw)
        logger.info("Created homework assignment", extra={"homework_id": str(hw.id), "title": hw.title})
        return hw

    @staticmethod
    async def get_homework(
        db: AsyncSession,
        homework_id: uuid.UUID,
        institute_id: uuid.UUID | None,
    ) -> Homework:
        query = (
            select(Homework)
            .options(selectinload(Homework.attachment))
            .where(
                Homework.id == homework_id,
                Homework.deleted_at.is_(None),
            )
        )
        if institute_id:
            query = query.where(Homework.institute_id == institute_id)
        hw = await db.scalar(query)
        if not hw:
            raise NotFoundError(f"Homework {homework_id} not found")
        return hw

    @staticmethod
    async def update_homework(
        db: AsyncSession,
        homework_id: uuid.UUID,
        data: HomeworkUpdate,
        institute_id: uuid.UUID | None,
    ) -> Homework:
        hw = await LearningService.get_homework(db, homework_id, institute_id)
        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(hw, field, value)
        await db.flush()
        await db.refresh(hw)
        return hw

    @staticmethod
    async def list_batch_homework(
        db: AsyncSession,
        batch_id: uuid.UUID,
        institute_id: uuid.UUID | None,
        skip: int = 0,
        limit: int = 50,
    ) -> tuple[list[Homework], int]:
        base_query = (
            select(Homework)
            .options(selectinload(Homework.attachment))
            .where(
                Homework.batch_id == batch_id,
                Homework.deleted_at.is_(None),
            )
        )
        if institute_id:
            base_query = base_query.where(Homework.institute_id == institute_id)

        total = await db.scalar(select(func.count()).select_from(base_query.subquery())) or 0
        items = (
            await db.scalars(
                base_query.order_by(Homework.due_date.desc()).offset(skip).limit(limit)
            )
        ).all()
        return list(items), total

    @staticmethod
    async def soft_delete_homework(
        db: AsyncSession,
        homework_id: uuid.UUID,
        institute_id: uuid.UUID | None,
    ) -> None:
        hw = await LearningService.get_homework(db, homework_id, institute_id)
        hw.deleted_at = datetime.now(UTC)
        await db.flush()

    # ─────────────────────────────────────────────────────────────────────────
    # Homework Submission & Evaluation
    # ─────────────────────────────────────────────────────────────────────────

    @staticmethod
    async def submit_homework(
        db: AsyncSession,
        homework_id: uuid.UUID,
        student_user: User,
        data: HomeworkSubmissionCreate,
    ) -> HomeworkSubmission:
        """Student submits assignment work."""
        hw = await db.get(Homework, homework_id)
        if not hw or hw.deleted_at is not None:
            raise NotFoundError(f"Homework {homework_id} not found")

        student = await db.scalar(
            select(StudentProfile).where(
                StudentProfile.user_id == student_user.id,
                StudentProfile.deleted_at.is_(None),
            )
        )
        if not student:
            raise ForbiddenError("Student profile not found for user")

        # Verify active enrollment in this batch
        enrollment = await db.scalar(
            select(Enrollment).where(
                Enrollment.student_id == student.id,
                Enrollment.batch_id == hw.batch_id,
                Enrollment.status == EnrollmentStatus.ACTIVE,
            )
        )
        if not enrollment:
            raise ForbiddenError("You are not actively enrolled in the batch for this assignment")

        # Check late status
        status = SubmissionStatus.LATE if date.today() > hw.due_date else SubmissionStatus.SUBMITTED

        # Upsert submission
        submission = await db.scalar(
            select(HomeworkSubmission).where(
                HomeworkSubmission.homework_id == homework_id,
                HomeworkSubmission.student_id == student.id,
            )
        )
        now_utc = datetime.now(UTC)

        if submission:
            submission.attachment_id = data.attachment_id
            submission.submission_text = data.submission_text
            submission.status = status
            submission.submitted_at = now_utc
        else:
            submission = HomeworkSubmission(
                homework_id=homework_id,
                student_id=student.id,
                attachment_id=data.attachment_id,
                submission_text=data.submission_text,
                status=status,
                submitted_at=now_utc,
            )
            db.add(submission)

        await db.flush()
        await db.refresh(submission)
        logger.info(
            "Submitted homework",
            extra={"homework_id": str(homework_id), "student_id": str(student.id), "status": status.value},
        )
        return submission

    @staticmethod
    async def evaluate_submission(
        db: AsyncSession,
        submission_id: uuid.UUID,
        evaluation: HomeworkEvaluationRequest,
        reviewer_user: User,
    ) -> HomeworkSubmission:
        """Teacher evaluates and grades student assignment submission."""
        submission = await db.get(HomeworkSubmission, submission_id)
        if not submission:
            raise NotFoundError(f"Submission {submission_id} not found")

        submission.marks = evaluation.marks
        submission.max_marks = evaluation.max_marks
        submission.teacher_comment = evaluation.teacher_comment
        submission.status = evaluation.status
        submission.reviewed_at = datetime.now(UTC)
        submission.reviewed_by = reviewer_user.id

        await db.flush()
        await db.refresh(submission)
        logger.info("Evaluated homework submission", extra={"submission_id": str(submission_id), "marks": evaluation.marks})
        return submission

    @staticmethod
    async def list_homework_submissions(
        db: AsyncSession,
        homework_id: uuid.UUID,
    ) -> list[HomeworkSubmission]:
        query = (
            select(HomeworkSubmission)
            .options(selectinload(HomeworkSubmission.attachment))
            .where(HomeworkSubmission.homework_id == homework_id)
            .order_by(HomeworkSubmission.submitted_at.desc())
        )
        return list((await db.scalars(query)).all())

    @staticmethod
    async def get_student_submission(
        db: AsyncSession,
        homework_id: uuid.UUID,
        student_id: uuid.UUID,
    ) -> HomeworkSubmission | None:
        query = (
            select(HomeworkSubmission)
            .options(selectinload(HomeworkSubmission.attachment))
            .where(
                HomeworkSubmission.homework_id == homework_id,
                HomeworkSubmission.student_id == student_id,
            )
        )
        return await db.scalar(query)
