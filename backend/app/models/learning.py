"""
app/models/learning.py
----------------------
Learning & Generic Storage models:
  - FileAttachment: Reusable files in object/local storage
  - StudyMaterial: Notes, DPPs, worksheets, revision guides targeted to courses/batches
  - Homework: Assignments published by teachers
  - HomeworkSubmission: Student assignment submissions, evaluations & feedback
"""

from __future__ import annotations

import enum
import uuid
from datetime import date as Date, datetime

from sqlalchemy import (
    Boolean,
    Date as SADate,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, SoftDeleteMixin, TenantAwareMixin, TimestampMixin


class MaterialType(str, enum.Enum):
    NOTES = "NOTES"
    DPP = "DPP"  # Daily Practice Problems
    WORKSHEET = "WORKSHEET"
    VIDEO = "VIDEO"
    IMPORTANT_QUESTIONS = "IMPORTANT_QUESTIONS"
    REVISION = "REVISION"
    OTHER = "OTHER"


class SubmissionStatus(str, enum.Enum):
    SUBMITTED = "SUBMITTED"
    LATE = "LATE"
    REVIEWED = "REVIEWED"
    NEEDS_IMPROVEMENT = "NEEDS_IMPROVEMENT"
    RESUBMIT = "RESUBMIT"


# ─────────────────────────────────────────────────────────────────────────────
# FileAttachment
# ─────────────────────────────────────────────────────────────────────────────

class FileAttachment(TenantAwareMixin, Base):
    """Metadata record for a stored file."""

    __tablename__ = "file_attachments"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    storage_key: Mapped[str] = mapped_column(String(255), nullable=False, unique=True, index=True)
    file_name: Mapped[str] = mapped_column(String(255), nullable=False)
    file_size: Mapped[int] = mapped_column(Integer, nullable=False)
    content_type: Mapped[str] = mapped_column(String(100), nullable=False)
    uploaded_by: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    def __repr__(self) -> str:
        return f"<FileAttachment id={self.id} file={self.file_name!r}>"


# ─────────────────────────────────────────────────────────────────────────────
# StudyMaterial
# ─────────────────────────────────────────────────────────────────────────────

class StudyMaterial(TenantAwareMixin, TimestampMixin, SoftDeleteMixin, Base):
    """
    Learning materials (notes, practice sheets, question banks).
    Targeted at either a full Course or a specific Batch.
    """

    __tablename__ = "study_materials"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    type: Mapped[MaterialType] = mapped_column(
        Enum(MaterialType, name="material_type_enum"),
        default=MaterialType.NOTES,
        nullable=False,
        index=True,
    )
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    target_course_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("courses.id", ondelete="SET NULL"), nullable=True, index=True
    )
    target_batch_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("batches.id", ondelete="SET NULL"), nullable=True, index=True
    )
    attachment_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("file_attachments.id", ondelete="SET NULL"), nullable=True
    )
    uploaded_by: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    is_published: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # Relationships
    attachment: Mapped["FileAttachment | None"] = relationship("FileAttachment", lazy="noload")

    def __repr__(self) -> str:
        return f"<StudyMaterial id={self.id} title={self.title!r} type={self.type}>"


# ─────────────────────────────────────────────────────────────────────────────
# Homework
# ─────────────────────────────────────────────────────────────────────────────

class Homework(TenantAwareMixin, TimestampMixin, SoftDeleteMixin, Base):
    """Assignments created by teachers for specific batches."""

    __tablename__ = "homework"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    batch_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("batches.id", ondelete="CASCADE"), nullable=False, index=True
    )
    subject_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("subjects.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    instructions: Mapped[str | None] = mapped_column(Text, nullable=True)
    chapter: Mapped[str | None] = mapped_column(String(100), nullable=True)
    due_date: Mapped[Date] = mapped_column(SADate, nullable=False, index=True)
    attachment_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("file_attachments.id", ondelete="SET NULL"), nullable=True
    )
    created_by: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )

    # Relationships
    attachment: Mapped["FileAttachment | None"] = relationship("FileAttachment", lazy="noload")
    submissions: Mapped[list["HomeworkSubmission"]] = relationship(
        "HomeworkSubmission", back_populates="homework", lazy="noload"
    )

    def __repr__(self) -> str:
        return f"<Homework id={self.id} title={self.title!r} batch={self.batch_id}>"


# ─────────────────────────────────────────────────────────────────────────────
# HomeworkSubmission
# ─────────────────────────────────────────────────────────────────────────────

class HomeworkSubmission(Base):
    """
    Student homework submission and grading result.
    One submission record per (homework_id, student_id).
    """

    __tablename__ = "homework_submissions"
    __table_args__ = (
        UniqueConstraint("homework_id", "student_id", name="uq_homework_student_submission"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    homework_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("homework.id", ondelete="CASCADE"), nullable=False, index=True
    )
    student_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("student_profiles.id", ondelete="CASCADE"), nullable=False, index=True
    )
    attachment_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("file_attachments.id", ondelete="SET NULL"), nullable=True
    )
    submission_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[SubmissionStatus] = mapped_column(
        Enum(SubmissionStatus, name="submission_status_enum"),
        default=SubmissionStatus.SUBMITTED,
        nullable=False,
        index=True,
    )
    marks: Mapped[float | None] = mapped_column(Float, nullable=True)
    max_marks: Mapped[float | None] = mapped_column(Float, nullable=True)
    teacher_comment: Mapped[str | None] = mapped_column(Text, nullable=True)
    submitted_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    reviewed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    reviewed_by: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )

    # Relationships
    homework: Mapped["Homework"] = relationship("Homework", back_populates="submissions", lazy="noload")
    student: Mapped["StudentProfile"] = relationship("StudentProfile", lazy="noload")  # type: ignore[name-defined]
    attachment: Mapped["FileAttachment | None"] = relationship("FileAttachment", lazy="noload")

    def __repr__(self) -> str:
        return f"<HomeworkSubmission homework={self.homework_id} student={self.student_id} status={self.status}>"
