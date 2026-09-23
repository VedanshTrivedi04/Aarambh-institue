"""
app/models/enrollment.py
-------------------------
Enrollment and BatchTransferHistory models.

Enrollment (rules.md §6):
  - An Enrollment links a StudentProfile to a Batch.
  - Records are NEVER physically deleted — use status transitions instead.
  - Status lifecycle:  ACTIVE → COMPLETED | DROPPED | TRANSFERRED
  - Fees, attendance, and results all reference enrollment_id — deleting an
    enrollment would orphan financial and academic records.

BatchTransferHistory (rules.md §6):
  - Every time a student moves between batches, a history row is created.
  - Append-only — no updates, no deletes.
  - Provides a complete audit trail for "who moved this student, when, and why".

Business rules enforced in enrollment_service.py:
  1. BatchFullError          — batch.capacity reached (active enrollment count ≥ capacity)
  2. DuplicateEnrollmentError — student already has ACTIVE enrollment in this batch
  3. Transfer requires a valid reason and creates both a history row and a new Enrollment.
"""

from __future__ import annotations

import enum
import uuid
from datetime import date as Date, datetime

from typing import TYPE_CHECKING

from sqlalchemy import (
    Boolean,
    Date as SADate,
    DateTime,
    Enum,
    ForeignKey,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.academic_structure import Batch
    from app.models.people import StudentProfile


class EnrollmentStatus(str, enum.Enum):
    ACTIVE = "ACTIVE"
    COMPLETED = "COMPLETED"    # finished the course
    DROPPED = "DROPPED"        # voluntarily left
    TRANSFERRED = "TRANSFERRED" # moved to another batch (history row created)
    CANCELLED = "CANCELLED"    # admission cancelled before first class


class Enrollment(TimestampMixin, Base):
    """
    Active or historical enrollment of a student in a batch.

    NOT soft-deleted — status transitions are used instead.
    `enrollment_date` defaults to today; can be backdated by ADMIN.

    NOTE: A student can have multiple Enrollment rows for the same batch
    only if the previous one was TRANSFERRED/DROPPED (not ACTIVE).
    The UNIQUE constraint enforces this:
      uq_enrollments_student_batch_active — only one ACTIVE per (student, batch).
    This cannot be a simple unique constraint because status varies; the
    service layer enforces it with an explicit query before insert.
    """

    __tablename__ = "enrollments"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    student_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("student_profiles.id", ondelete="RESTRICT"),
        nullable=False, index=True,
    )
    batch_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("batches.id", ondelete="RESTRICT"),
        nullable=False, index=True,
    )
    institute_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("institutes.id", ondelete="RESTRICT"),
        nullable=True, index=True,
    )

    status: Mapped[EnrollmentStatus] = mapped_column(
        Enum(EnrollmentStatus, name="enrollment_status_enum"),
        default=EnrollmentStatus.ACTIVE,
        nullable=False,
        index=True,
    )
    enrollment_date: Mapped[Date] = mapped_column(SADate, nullable=False)
    end_date: Mapped[Date | None] = mapped_column(SADate, nullable=True)

    # Who performed the enrollment action (admin/counsellor user id)
    enrolled_by: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)
    # Drop/cancel/transfer notes
    remarks: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Relationships
    student: Mapped["StudentProfile"] = relationship(  # type: ignore[name-defined]
        "StudentProfile", back_populates="enrollments", lazy="noload"
    )
    batch: Mapped["Batch"] = relationship(
        "Batch", foreign_keys=[batch_id], lazy="noload"
    )
    transfer_history: Mapped[list["BatchTransferHistory"]] = relationship(
        "BatchTransferHistory", back_populates="enrollment",
        lazy="noload", foreign_keys="BatchTransferHistory.enrollment_id",
    )

    def __repr__(self) -> str:
        return f"<Enrollment student={self.student_id} batch={self.batch_id} status={self.status}>"


class BatchTransferHistory(Base):
    """
    Append-only record of every student batch transfer.

    Created whenever enrollment_service.transfer_student() is called.
    Never updated or deleted — it is the audit trail for batch movement.

    from_batch_id → to_batch_id documents the transfer direction.
    reason        is required — admin must provide justification.
    transferred_by is the User who initiated the action.
    """

    __tablename__ = "batch_transfer_history"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    enrollment_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("enrollments.id", ondelete="RESTRICT"),
        nullable=False, index=True,
    )
    student_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("student_profiles.id", ondelete="RESTRICT"),
        nullable=False, index=True,
    )
    from_batch_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("batches.id", ondelete="RESTRICT"),
        nullable=False, index=True,
    )
    to_batch_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("batches.id", ondelete="RESTRICT"),
        nullable=False, index=True,
    )
    reason: Mapped[str] = mapped_column(Text, nullable=False)
    transferred_by: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)
    institute_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), nullable=True, index=True
    )

    # Immutable timestamp — server-side
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False, index=True
    )

    enrollment: Mapped["Enrollment"] = relationship(
        "Enrollment", back_populates="transfer_history",
        lazy="noload", foreign_keys=[enrollment_id],
    )

    def __repr__(self) -> str:
        return (
            f"<BatchTransferHistory student={self.student_id} "
            f"from={self.from_batch_id} to={self.to_batch_id}>"
        )
