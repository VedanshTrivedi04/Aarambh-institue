"""
app/models/enquiry.py
---------------------
Enquiry pipeline and follow-up models for coaching/school CRM.

Enquiry stages lifecycle:
  NEW → CONTACTED → COUNSELLING → DEMO → INTERESTED → ADMISSION
                                                     ↘ NOT_INTERESTED
                                                     ↘ FOLLOW_UP_LATER

Enquiry (rules.md §5, §6):
  - Tracks incoming prospective students and parents.
  - Assigned to a counsellor (User).
  - Converted atomically to StudentProfile + ParentProfile + Enrollment via Admission Wizard.
  - Retains full follow-up history via EnquiryFollowUp (append-only).
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
    ForeignKey,
    String,
    Text,
    func,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, SoftDeleteMixin, TenantAwareMixin, TimestampMixin


class EnquirySource(str, enum.Enum):
    WALK_IN = "WALK_IN"
    WEBSITE = "WEBSITE"
    REFERRAL = "REFERRAL"
    PHONE = "PHONE"
    SOCIAL_MEDIA = "SOCIAL_MEDIA"
    DIRECT = "DIRECT"
    OTHER = "OTHER"


class EnquiryStage(str, enum.Enum):
    NEW = "NEW"
    CONTACTED = "CONTACTED"
    COUNSELLING = "COUNSELLING"
    DEMO = "DEMO"
    INTERESTED = "INTERESTED"
    ADMISSION = "ADMISSION"
    NOT_INTERESTED = "NOT_INTERESTED"
    FOLLOW_UP_LATER = "FOLLOW_UP_LATER"


class Enquiry(TenantAwareMixin, TimestampMixin, SoftDeleteMixin, Base):
    """
    Prospective student enquiry record.

    Managed by counsellors and front desk.
    When stage transitions to ADMISSION via admission wizard,
    `converted_student_id` and `converted_at` are populated.
    """

    __tablename__ = "enquiries"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Student details
    student_name: Mapped[str] = mapped_column(String(150), nullable=False)
    student_email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    student_phone: Mapped[str | None] = mapped_column(String(20), nullable=True)

    # Parent/Guardian details
    parent_name: Mapped[str] = mapped_column(String(150), nullable=False)
    parent_email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    parent_phone: Mapped[str] = mapped_column(String(20), nullable=False)

    # Academic interest
    board_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("boards.id", ondelete="SET NULL"), nullable=True, index=True
    )
    class_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("school_classes.id", ondelete="SET NULL"), nullable=True, index=True
    )
    interested_course_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("courses.id", ondelete="SET NULL"), nullable=True, index=True
    )

    # Lead attribution & pipeline state
    source: Mapped[EnquirySource] = mapped_column(
        Enum(EnquirySource, name="enquiry_source_enum"),
        default=EnquirySource.WALK_IN,
        nullable=False,
    )
    stage: Mapped[EnquiryStage] = mapped_column(
        Enum(EnquiryStage, name="enquiry_stage_enum"),
        default=EnquiryStage.NEW,
        nullable=False,
        index=True,
    )
    counsellor_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True
    )
    follow_up_date: Mapped[Date | None] = mapped_column(SADate, nullable=True, index=True)
    remarks: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Conversion record
    converted_student_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("student_profiles.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    converted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # Relationships
    follow_ups: Mapped[list["EnquiryFollowUp"]] = relationship(
        "EnquiryFollowUp", back_populates="enquiry",
        lazy="noload", cascade="all, delete-orphan",
        order_by="desc(EnquiryFollowUp.created_at)",
    )

    def __repr__(self) -> str:
        return f"<Enquiry id={self.id} student={self.student_name!r} stage={self.stage}>"


class EnquiryFollowUp(Base):
    """
    Append-only follow-up log for an enquiry.
    Tracks every call, meeting, demo session, or stage transition.
    """

    __tablename__ = "enquiry_follow_ups"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    enquiry_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("enquiries.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    author_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    stage_before: Mapped[EnquiryStage | None] = mapped_column(
        Enum(EnquiryStage, name="enquiry_stage_enum", create_type=False), nullable=True
    )
    stage_after: Mapped[EnquiryStage] = mapped_column(
        Enum(EnquiryStage, name="enquiry_stage_enum", create_type=False), nullable=False
    )
    notes: Mapped[str] = mapped_column(Text, nullable=False)
    next_follow_up_date: Mapped[Date | None] = mapped_column(SADate, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False, index=True
    )

    enquiry: Mapped["Enquiry"] = relationship(
        "Enquiry", back_populates="follow_ups", lazy="noload"
    )

    def __repr__(self) -> str:
        return f"<EnquiryFollowUp enquiry={self.enquiry_id} stage={self.stage_after}>"
