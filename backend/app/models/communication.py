"""
app/models/communication.py
----------------------------
Communication, Notifications & Relationship-Based Messaging domain models:
  - Notification: In-app persistent notification for academic/fee/attendance/system events
  - Conversation: Direct or group message thread (scoped by dynamic contact graph or batch)
  - ConversationParticipant: Join table tracking user participation and unread status
  - Message: Immutable message record within a conversation (supports attachments)
  - Announcement: Broadcast bulletin targeted via audience filters (JSONB)
  - PTMRequest: Parent-Teacher Meeting lifecycle booking and confirmation
  - ReportedMessage: Moderation queue for reporting inappropriate or policy-violating messages
"""

from __future__ import annotations

import enum
import uuid
from datetime import datetime, timezone
from typing import TYPE_CHECKING, Any

from sqlalchemy import (
    Boolean,
    DateTime,
    Enum,
    ForeignKey,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, SoftDeleteMixin, TenantAwareMixin, TimestampMixin

if TYPE_CHECKING:
    from app.models.academic_structure import Batch
    from app.models.learning import FileAttachment
    from app.models.people import ParentProfile, StudentProfile, TeacherProfile
    from app.models.user import User


# ─── Enums ───────────────────────────────────────────────────────────────────

class NotificationType(str, enum.Enum):
    ACADEMIC = "ACADEMIC"
    ATTENDANCE = "ATTENDANCE"
    FEE = "FEE"
    COMMUNICATION = "COMMUNICATION"
    SYSTEM = "SYSTEM"


class ConversationType(str, enum.Enum):
    DIRECT_STUDENT_TEACHER = "DIRECT_STUDENT_TEACHER"
    DIRECT_PARENT_TEACHER = "DIRECT_PARENT_TEACHER"
    THREE_WAY = "THREE_WAY"  # Parent, Student, Teacher
    BATCH_GROUP = "BATCH_GROUP"


class PTMStatus(str, enum.Enum):
    REQUESTED = "REQUESTED"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    RESCHEDULED = "RESCHEDULED"
    CONFIRMED = "CONFIRMED"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"


class ReportStatus(str, enum.Enum):
    PENDING = "PENDING"
    RESOLVED = "RESOLVED"
    DISMISSED = "DISMISSED"


# ─── Models ──────────────────────────────────────────────────────────────────

class Notification(TenantAwareMixin, Base):
    """
    In-app notification delivered to a user.
    """

    __tablename__ = "notifications"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    title: Mapped[str] = mapped_column(String(200), nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    type: Mapped[NotificationType] = mapped_column(
        Enum(NotificationType, name="notification_type_enum"),
        nullable=False,
        default=NotificationType.ACADEMIC,
        index=True,
    )
    related_entity_type: Mapped[str | None] = mapped_column(String(50), nullable=True)
    related_entity_id: Mapped[str | None] = mapped_column(String(100), nullable=True)

    is_read: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False, index=True)
    read_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        index=True,
    )

    # Relationships
    user: Mapped[User] = relationship("User", foreign_keys=[user_id], lazy="noload")


class Conversation(TenantAwareMixin, TimestampMixin, SoftDeleteMixin, Base):
    """
    Message thread between two or more participants.
    Direct conversations are governed by the dynamic derived contact graph.
    Batch group conversations link to an academic Batch.
    """

    __tablename__ = "conversations"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    type: Mapped[ConversationType] = mapped_column(
        Enum(ConversationType, name="conversation_type_enum"),
        nullable=False,
        default=ConversationType.DIRECT_STUDENT_TEACHER,
        index=True,
    )
    batch_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("batches.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    title: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # Relationships
    batch: Mapped[Batch | None] = relationship("Batch", lazy="noload")
    participants: Mapped[list[ConversationParticipant]] = relationship(
        "ConversationParticipant",
        back_populates="conversation",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    messages: Mapped[list[Message]] = relationship(
        "Message",
        back_populates="conversation",
        cascade="all, delete-orphan",
        order_by="Message.created_at",
        lazy="noload",
    )


class ConversationParticipant(Base):
    """
    User membership in a conversation with unread watermark tracking.
    """

    __tablename__ = "conversation_participants"
    __table_args__ = (
        UniqueConstraint("conversation_id", "user_id", name="uq_conversation_participant"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    conversation_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("conversations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    role_in_conversation: Mapped[str] = mapped_column(String(50), nullable=False)
    last_read_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    joined_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    # Relationships
    conversation: Mapped[Conversation] = relationship(
        "Conversation",
        back_populates="participants",
        lazy="noload",
    )
    user: Mapped[User] = relationship("User", foreign_keys=[user_id], lazy="noload")


class Message(Base):
    """
    Single message within a conversation.
    Supports text content and optional file attachment.
    """

    __tablename__ = "messages"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    conversation_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("conversations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    sender_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    body: Mapped[str] = mapped_column(Text, nullable=False)
    attachment_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("file_attachments.id", ondelete="SET NULL"),
        nullable=True,
    )
    is_hidden: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    sent_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        index=True,
    )

    # Relationships
    conversation: Mapped[Conversation] = relationship(
        "Conversation",
        back_populates="messages",
        lazy="noload",
    )
    sender: Mapped[User] = relationship("User", foreign_keys=[sender_id], lazy="noload")
    attachment: Mapped[FileAttachment | None] = relationship("FileAttachment", lazy="noload")


class Announcement(TenantAwareMixin, TimestampMixin, SoftDeleteMixin, Base):
    """
    Targeted bulletin or broadcast announcement.
    Audience is filtered using JSONB matching:
      e.g. {"batch_id": "...", "course_id": "...", "class_id": "...", "board_id": "..."}
      An empty dict {} indicates institute-wide broadcast.
    """

    __tablename__ = "announcements"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    target_audience: Mapped[dict[str, Any]] = mapped_column(JSONB, default=dict, nullable=False)
    is_pinned: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    published_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        index=True,
    )
    created_by: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=False,
    )

    # Relationships
    author: Mapped[User] = relationship("User", foreign_keys=[created_by], lazy="noload")


class PTMRequest(TenantAwareMixin, TimestampMixin, SoftDeleteMixin, Base):
    """
    Parent-Teacher Meeting (PTM) booking request and confirmation.
    """

    __tablename__ = "ptm_requests"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    parent_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("parent_profiles.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    student_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("student_profiles.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    teacher_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("teacher_profiles.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    reason: Mapped[str] = mapped_column(Text, nullable=False)
    requested_slot: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    confirmed_slot: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    teacher_notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[PTMStatus] = mapped_column(
        Enum(PTMStatus, name="ptm_status_enum"),
        default=PTMStatus.REQUESTED,
        nullable=False,
        index=True,
    )

    # Relationships
    parent: Mapped[ParentProfile] = relationship("ParentProfile", foreign_keys=[parent_id], lazy="noload")
    student: Mapped[StudentProfile] = relationship("StudentProfile", foreign_keys=[student_id], lazy="noload")
    teacher: Mapped[TeacherProfile] = relationship("TeacherProfile", foreign_keys=[teacher_id], lazy="noload")


class ReportedMessage(TenantAwareMixin, Base):
    """
    Moderation queue record for abusive/inappropriate messages reported by users.
    """

    __tablename__ = "reported_messages"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    message_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("messages.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    reported_by: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    reason: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[ReportStatus] = mapped_column(
        Enum(ReportStatus, name="report_status_enum"),
        default=ReportStatus.PENDING,
        nullable=False,
        index=True,
    )
    resolved_by: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )
    resolution_notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    action_taken: Mapped[str | None] = mapped_column(String(50), nullable=True)
    resolved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    # Relationships
    message: Mapped[Message] = relationship("Message", foreign_keys=[message_id], lazy="noload")
    reporter: Mapped[User] = relationship("User", foreign_keys=[reported_by], lazy="noload")
    resolver: Mapped[User | None] = relationship("User", foreign_keys=[resolved_by], lazy="noload")
