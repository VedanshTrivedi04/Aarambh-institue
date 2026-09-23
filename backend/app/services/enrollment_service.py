"""
app/services/enrollment_service.py
----------------------------------
Service layer for student enrollments and batch transfers.

Key invariants (rules.md §6, backend.md §3):
  1. No hard delete:
     Enrollment records are NEVER physically deleted.
     Status transitions: ACTIVE → COMPLETED | DROPPED | TRANSFERRED | CANCELLED.
  2. Batch capacity guard:
     BatchFullError raised if active enrollment count >= batch.capacity.
  3. Duplicate prevention:
     DuplicateEnrollmentError raised if student is already actively enrolled in batch.
  4. Complete transfer audit:
     BatchTransferHistory record is created on every batch move.
     Old enrollment marked TRANSFERRED with end_date; new enrollment created as ACTIVE.
"""

from __future__ import annotations

import uuid
from datetime import date, datetime, timezone

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import (
    BatchFullError,
    DuplicateEnrollmentError,
    NotFoundError,
    ValidationError,
)
from app.core.logging import get_logger
from app.models.academic_structure import Batch
from app.models.enrollment import (
    BatchTransferHistory,
    Enrollment,
    EnrollmentStatus,
)
from app.models.people import StudentProfile
from app.schemas.enrollment import (
    BatchTransferRequest,
    EnrollmentCreate,
    EnrollmentStatusUpdate,
)

logger = get_logger(__name__)


class EnrollmentService:
    """Core enrollment engine with capacity guards and transfer history audit."""

    @staticmethod
    async def get_active_enrollment_count(
        db: AsyncSession,
        batch_id: uuid.UUID,
    ) -> int:
        """Count how many students currently hold an ACTIVE enrollment in a batch."""
        count = await db.scalar(
            select(func.count(Enrollment.id)).where(
                Enrollment.batch_id == batch_id,
                Enrollment.status == EnrollmentStatus.ACTIVE,
            )
        )
        return count or 0

    @staticmethod
    async def enroll_student(
        db: AsyncSession,
        data: EnrollmentCreate,
        institute_id: uuid.UUID | None,
        enrolled_by: uuid.UUID | None = None,
    ) -> Enrollment:
        """
        Enroll a student into a batch.
        Enforces batch capacity and duplicate active enrollment checks.
        """
        # 1. Verify student exists and is not deleted
        student = await db.scalar(
            select(StudentProfile).where(
                StudentProfile.id == data.student_id,
                StudentProfile.deleted_at.is_(None),
            )
        )
        if not student:
            raise NotFoundError(f"Student profile {data.student_id} not found")

        # 2. Verify batch exists, is active, not deleted
        batch = await db.scalar(
            select(Batch).where(
                Batch.id == data.batch_id,
                Batch.deleted_at.is_(None),
            )
        )
        if not batch:
            raise NotFoundError(f"Batch {data.batch_id} not found")
        if not batch.is_active:
            raise ValidationError(f"Batch '{batch.name}' is inactive and cannot accept enrollments")

        # 3. Check duplicate active enrollment
        existing_active = await db.scalar(
            select(Enrollment).where(
                Enrollment.student_id == data.student_id,
                Enrollment.batch_id == data.batch_id,
                Enrollment.status == EnrollmentStatus.ACTIVE,
            )
        )
        if existing_active:
            raise DuplicateEnrollmentError(
                f"Student is already actively enrolled in batch '{batch.name}'"
            )

        # 4. Check batch capacity
        active_count = await EnrollmentService.get_active_enrollment_count(db, data.batch_id)
        if active_count >= batch.capacity:
            raise BatchFullError(
                f"Batch '{batch.name}' has reached capacity ({active_count}/{batch.capacity})"
            )

        # 5. Create enrollment
        enrollment = Enrollment(
            student_id=data.student_id,
            batch_id=data.batch_id,
            institute_id=institute_id or student.institute_id,
            status=EnrollmentStatus.ACTIVE,
            enrollment_date=data.enrollment_date or date.today(),
            enrolled_by=enrolled_by,
            remarks=data.remarks,
        )
        db.add(enrollment)
        await db.flush()
        await db.refresh(enrollment)
        logger.info(
            "Student enrolled into batch",
            extra={
                "enrollment_id": str(enrollment.id),
                "student_id": str(data.student_id),
                "batch_id": str(data.batch_id),
            },
        )
        return enrollment

    @staticmethod
    async def transfer_student(
        db: AsyncSession,
        enrollment_id: uuid.UUID,
        request: BatchTransferRequest,
        institute_id: uuid.UUID | None,
        transferred_by: uuid.UUID | None = None,
    ) -> tuple[Enrollment, BatchTransferHistory, Enrollment]:
        """
        Transfer student from current batch to another batch.
        Lifecycle:
          - Validates old enrollment is ACTIVE.
          - Validates target batch != old batch, active, not full.
          - Marks old enrollment TRANSFERRED.
          - Appends BatchTransferHistory record.
          - Creates new ACTIVE enrollment in target batch.
        Returns (old_enrollment, transfer_history, new_enrollment).
        """
        # 1. Fetch current enrollment
        old_enrollment = await db.get(Enrollment, enrollment_id)
        if not old_enrollment:
            raise NotFoundError(f"Enrollment {enrollment_id} not found")

        if institute_id and old_enrollment.institute_id and old_enrollment.institute_id != institute_id:
            raise NotFoundError(f"Enrollment {enrollment_id} not found")

        if old_enrollment.status != EnrollmentStatus.ACTIVE:
            raise ValidationError(
                f"Cannot transfer enrollment with status '{old_enrollment.status}'. Only ACTIVE enrollments can be transferred."
            )

        if old_enrollment.batch_id == request.to_batch_id:
            raise ValidationError("Target batch must be different from current batch")

        # 2. Fetch and validate target batch
        target_batch = await db.scalar(
            select(Batch).where(
                Batch.id == request.to_batch_id,
                Batch.deleted_at.is_(None),
            )
        )
        if not target_batch:
            raise NotFoundError(f"Target batch {request.to_batch_id} not found")
        if not target_batch.is_active:
            raise ValidationError(f"Target batch '{target_batch.name}' is inactive")

        # 3. Check duplicate active enrollment in target batch
        existing_in_target = await db.scalar(
            select(Enrollment).where(
                Enrollment.student_id == old_enrollment.student_id,
                Enrollment.batch_id == request.to_batch_id,
                Enrollment.status == EnrollmentStatus.ACTIVE,
            )
        )
        if existing_in_target:
            raise DuplicateEnrollmentError(
                f"Student is already actively enrolled in target batch '{target_batch.name}'"
            )

        # 4. Check target batch capacity
        target_count = await EnrollmentService.get_active_enrollment_count(db, request.to_batch_id)
        if target_count >= target_batch.capacity:
            raise BatchFullError(
                f"Target batch '{target_batch.name}' has reached capacity ({target_count}/{target_batch.capacity})"
            )

        today = date.today()

        # 5. Close old enrollment
        from_batch_id = old_enrollment.batch_id
        old_enrollment.status = EnrollmentStatus.TRANSFERRED
        old_enrollment.end_date = today
        old_enrollment.remarks = (
            f"{old_enrollment.remarks or ''} | Transferred to batch '{target_batch.name}'. Reason: {request.reason}".strip(
                " | "
            )
        )

        # 6. Create transfer history audit record
        history = BatchTransferHistory(
            enrollment_id=old_enrollment.id,
            student_id=old_enrollment.student_id,
            from_batch_id=from_batch_id,
            to_batch_id=request.to_batch_id,
            reason=request.reason,
            transferred_by=transferred_by,
            institute_id=old_enrollment.institute_id,
        )
        db.add(history)

        # 7. Create new active enrollment
        new_enrollment = Enrollment(
            student_id=old_enrollment.student_id,
            batch_id=request.to_batch_id,
            institute_id=old_enrollment.institute_id,
            status=EnrollmentStatus.ACTIVE,
            enrollment_date=today,
            enrolled_by=transferred_by,
            remarks=f"Transferred from previous batch. Reason: {request.reason}",
        )
        db.add(new_enrollment)

        await db.flush()
        await db.refresh(old_enrollment)
        await db.refresh(history)
        await db.refresh(new_enrollment)

        logger.info(
            "Transferred student between batches",
            extra={
                "student_id": str(old_enrollment.student_id),
                "from_batch_id": str(from_batch_id),
                "to_batch_id": str(request.to_batch_id),
                "history_id": str(history.id),
                "new_enrollment_id": str(new_enrollment.id),
            },
        )
        return old_enrollment, history, new_enrollment

    @staticmethod
    async def update_status(
        db: AsyncSession,
        enrollment_id: uuid.UUID,
        update_data: EnrollmentStatusUpdate,
        institute_id: uuid.UUID | None,
    ) -> Enrollment:
        """
        Transition an enrollment's status (COMPLETED, DROPPED, CANCELLED).
        Records are NEVER physically deleted.
        """
        enrollment = await db.get(Enrollment, enrollment_id)
        if not enrollment:
            raise NotFoundError(f"Enrollment {enrollment_id} not found")

        if institute_id and enrollment.institute_id and enrollment.institute_id != institute_id:
            raise NotFoundError(f"Enrollment {enrollment_id} not found")

        enrollment.status = update_data.status
        if update_data.end_date:
            enrollment.end_date = update_data.end_date
        elif update_data.status in (
            EnrollmentStatus.COMPLETED,
            EnrollmentStatus.DROPPED,
            EnrollmentStatus.CANCELLED,
        ):
            enrollment.end_date = date.today()

        if update_data.remarks:
            enrollment.remarks = update_data.remarks

        await db.flush()
        await db.refresh(enrollment)
        logger.info(
            "Updated enrollment status",
            extra={"enrollment_id": str(enrollment_id), "status": str(update_data.status)},
        )
        return enrollment

    @staticmethod
    async def get_enrollment(
        db: AsyncSession,
        enrollment_id: uuid.UUID,
        institute_id: uuid.UUID | None,
    ) -> Enrollment:
        query = select(Enrollment).where(Enrollment.id == enrollment_id)
        if institute_id:
            query = query.where(Enrollment.institute_id == institute_id)
        enrollment = await db.scalar(query)
        if not enrollment:
            raise NotFoundError(f"Enrollment {enrollment_id} not found")
        return enrollment

    @staticmethod
    async def list_enrollments(
        db: AsyncSession,
        institute_id: uuid.UUID | None,
        student_id: uuid.UUID | None = None,
        batch_id: uuid.UUID | None = None,
        status: EnrollmentStatus | None = None,
        skip: int = 0,
        limit: int = 50,
    ) -> tuple[list[Enrollment], int]:
        base_query = select(Enrollment)
        if institute_id:
            base_query = base_query.where(Enrollment.institute_id == institute_id)
        if student_id:
            base_query = base_query.where(Enrollment.student_id == student_id)
        if batch_id:
            base_query = base_query.where(Enrollment.batch_id == batch_id)
        if status:
            base_query = base_query.where(Enrollment.status == status)

        total = await db.scalar(select(func.count()).select_from(base_query.subquery())) or 0
        items = (
            await db.scalars(
                base_query.order_by(Enrollment.created_at.desc()).offset(skip).limit(limit)
            )
        ).all()
        return list(items), total

    @staticmethod
    async def get_transfer_history(
        db: AsyncSession,
        student_id: uuid.UUID | None = None,
        enrollment_id: uuid.UUID | None = None,
        institute_id: uuid.UUID | None = None,
        skip: int = 0,
        limit: int = 50,
    ) -> tuple[list[BatchTransferHistory], int]:
        base_query = select(BatchTransferHistory)
        if institute_id:
            base_query = base_query.where(BatchTransferHistory.institute_id == institute_id)
        if student_id:
            base_query = base_query.where(BatchTransferHistory.student_id == student_id)
        if enrollment_id:
            base_query = base_query.where(BatchTransferHistory.enrollment_id == enrollment_id)

        total = await db.scalar(select(func.count()).select_from(base_query.subquery())) or 0
        items = (
            await db.scalars(
                base_query.order_by(BatchTransferHistory.created_at.desc())
                .offset(skip)
                .limit(limit)
            )
        ).all()
        return list(items), total
