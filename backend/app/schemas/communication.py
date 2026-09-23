"""
app/schemas/communication.py
----------------------------
Pydantic schemas for Slice 10: Communication, Notifications & Messaging.
"""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any
from pydantic import BaseModel, ConfigDict, Field

from app.models.communication import (
    ConversationType,
    NotificationType,
    PTMStatus,
    ReportStatus,
)


# ─── Notifications ───────────────────────────────────────────────────────────

class NotificationRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    user_id: uuid.UUID
    title: str
    body: str
    type: NotificationType
    related_entity_type: str | None = None
    related_entity_id: str | None = None
    is_read: bool
    read_at: datetime | None = None
    created_at: datetime


class NotificationCountRead(BaseModel):
    unread_count: int


class NotificationMarkReadRequest(BaseModel):
    notification_ids: list[uuid.UUID] = Field(default_factory=list, description="IDs to mark as read")


# ─── Derived Contact Discovery ───────────────────────────────────────────────

class EligibleContactRead(BaseModel):
    user_id: uuid.UUID
    profile_id: uuid.UUID
    full_name: str
    role: str
    email: str | None = None
    mobile: str | None = None
    subject_names: list[str] = []
    batch_names: list[str] = []


# ─── Conversations & Messages ─────────────────────────────────────────────────

class ParticipantRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    user_id: uuid.UUID
    full_name: str | None = None
    email: str | None = None
    role_in_conversation: str
    last_read_at: datetime | None = None
    joined_at: datetime


class MessageCreate(BaseModel):
    body: str = Field(..., min_length=1, max_length=5000, description="Text message content")
    attachment_id: uuid.UUID | None = Field(None, description="Optional attached file ID")


class MessageRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    conversation_id: uuid.UUID
    sender_id: uuid.UUID
    sender_name: str | None = None
    sender_role: str | None = None
    body: str
    attachment_id: uuid.UUID | None = None
    is_hidden: bool = False
    sent_at: datetime
    created_at: datetime


class ConversationCreate(BaseModel):
    participant_user_ids: list[uuid.UUID] = Field(
        ..., min_length=1, description="List of participant user IDs to add (excluding caller)"
    )
    type: ConversationType = Field(
        default=ConversationType.DIRECT_STUDENT_TEACHER,
        description="Type of conversation thread",
    )
    batch_id: uuid.UUID | None = Field(None, description="Linked Batch ID if batch group chat")
    title: str | None = Field(None, max_length=255, description="Optional conversation topic / title")


class ConversationRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    institute_id: uuid.UUID
    type: ConversationType
    batch_id: uuid.UUID | None = None
    title: str | None = None
    created_at: datetime
    updated_at: datetime
    unread_count: int = 0
    participants: list[ParticipantRead] = []
    last_message: MessageRead | None = None


# ─── Announcements ────────────────────────────────────────────────────────────

class AnnouncementCreate(BaseModel):
    title: str = Field(..., min_length=3, max_length=255, description="Announcement header")
    body: str = Field(..., min_length=5, description="Detailed bulletin content")
    target_audience: dict[str, Any] = Field(
        default_factory=dict,
        description="Audience filter criteria: board_id, class_id, course_id, batch_id",
    )
    is_pinned: bool = Field(False, description="Pin to top of announcement feed")


class AnnouncementRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    institute_id: uuid.UUID
    title: str
    body: str
    target_audience: dict[str, Any]
    is_pinned: bool
    published_at: datetime
    created_by: uuid.UUID
    author_name: str | None = None
    created_at: datetime


# ─── Parent-Teacher Meetings (PTM) ────────────────────────────────────────────

class PTMRequestCreate(BaseModel):
    student_id: uuid.UUID = Field(..., description="Student profile ID")
    teacher_id: uuid.UUID = Field(..., description="Teacher profile ID")
    reason: str = Field(..., min_length=5, description="Discussion agenda / reason for meeting")
    requested_slot: datetime = Field(..., description="Parent's preferred date and time")


class PTMStatusUpdate(BaseModel):
    status: PTMStatus = Field(..., description="Target status transition")
    confirmed_slot: datetime | None = Field(None, description="Final confirmed date and time (if APPROVED)")
    teacher_notes: str | None = Field(None, description="Teacher remarks or meeting summary")


class PTMRequestRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    institute_id: uuid.UUID
    parent_id: uuid.UUID
    parent_name: str | None = None
    student_id: uuid.UUID
    student_name: str | None = None
    teacher_id: uuid.UUID
    teacher_name: str | None = None
    reason: str
    requested_slot: datetime
    confirmed_slot: datetime | None = None
    teacher_notes: str | None = None
    status: PTMStatus
    created_at: datetime
    updated_at: datetime


# ─── Moderation & Safety ──────────────────────────────────────────────────────

class ReportMessageCreate(BaseModel):
    message_id: uuid.UUID = Field(..., description="Reported message ID")
    reason: str = Field(..., min_length=5, max_length=1000, description="Why this message violates guidelines")


class ResolveReportRequest(BaseModel):
    status: ReportStatus = Field(..., description="RESOLVED or DISMISSED")
    resolution_notes: str = Field(..., min_length=3, description="Admin justification notes")
    action_taken: str = Field(..., description="e.g. MESSAGE_HIDDEN, WARNING_ISSUED, NONE")


class ReportedMessageRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    institute_id: uuid.UUID
    message_id: uuid.UUID
    message_body: str | None = None
    sender_id: uuid.UUID | None = None
    sender_name: str | None = None
    reported_by: uuid.UUID
    reporter_name: str | None = None
    reason: str
    status: ReportStatus
    resolved_by: uuid.UUID | None = None
    resolver_name: str | None = None
    resolution_notes: str | None = None
    action_taken: str | None = None
    resolved_at: datetime | None = None
    created_at: datetime
