"""
009_communication_and_notifications — In-App Notifications, Conversations, Messages, Announcements, PTM & Moderation.

Creates:
  - notifications
  - conversations
  - conversation_participants
  - messages
  - announcements
  - ptm_requests
  - reported_messages
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "009"
down_revision = "008"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ── Enums ─────────────────────────────────────────────────────────────
    notification_type_enum = postgresql.ENUM(
        "ACADEMIC", "ATTENDANCE", "FEE", "COMMUNICATION", "SYSTEM",
        name="notification_type_enum", create_type=False,
    )
    notification_type_enum.create(op.get_bind(), checkfirst=True)

    conversation_type_enum = postgresql.ENUM(
        "DIRECT_STUDENT_TEACHER", "DIRECT_PARENT_TEACHER", "THREE_WAY", "BATCH_GROUP",
        name="conversation_type_enum", create_type=False,
    )
    conversation_type_enum.create(op.get_bind(), checkfirst=True)

    ptm_status_enum = postgresql.ENUM(
        "REQUESTED", "APPROVED", "REJECTED", "RESCHEDULED", "CONFIRMED", "COMPLETED", "CANCELLED",
        name="ptm_status_enum", create_type=False,
    )
    ptm_status_enum.create(op.get_bind(), checkfirst=True)

    report_status_enum = postgresql.ENUM(
        "PENDING", "RESOLVED", "DISMISSED",
        name="report_status_enum", create_type=False,
    )
    report_status_enum.create(op.get_bind(), checkfirst=True)

    # ── notifications ─────────────────────────────────────────────────────
    op.create_table(
        "notifications",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("institute_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("institutes.id", ondelete="RESTRICT"), nullable=True, index=True),
        sa.Column("branch_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("branches.id", ondelete="RESTRICT"), nullable=True, index=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("title", sa.String(length=200), nullable=False),
        sa.Column("body", sa.Text(), nullable=False),
        sa.Column("type", notification_type_enum, nullable=False, server_default="ACADEMIC", index=True),
        sa.Column("related_entity_type", sa.String(length=50), nullable=True),
        sa.Column("related_entity_id", sa.String(length=100), nullable=True),
        sa.Column("is_read", sa.Boolean(), nullable=False, server_default=sa.text("false"), index=True),
        sa.Column("read_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True),
                  server_default=sa.func.now(), nullable=False, index=True),
    )

    # ── conversations ─────────────────────────────────────────────────────
    op.create_table(
        "conversations",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("institute_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("institutes.id", ondelete="RESTRICT"), nullable=True, index=True),
        sa.Column("branch_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("branches.id", ondelete="RESTRICT"), nullable=True, index=True),
        sa.Column("type", conversation_type_enum, nullable=False, server_default="DIRECT_STUDENT_TEACHER", index=True),
        sa.Column("batch_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("batches.id", ondelete="SET NULL"), nullable=True, index=True),
        sa.Column("title", sa.String(length=255), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True),
                  server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True),
                  server_default=sa.func.now(), nullable=False, index=True),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True, index=True),
    )

    # ── conversation_participants ─────────────────────────────────────────
    op.create_table(
        "conversation_participants",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("conversation_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("conversations.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("role_in_conversation", sa.String(length=50), nullable=False),
        sa.Column("last_read_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("joined_at", sa.DateTime(timezone=True),
                  server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint("conversation_id", "user_id", name="uq_conversation_participant"),
    )

    # ── messages ──────────────────────────────────────────────────────────
    op.create_table(
        "messages",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("conversation_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("conversations.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("sender_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("users.id", ondelete="RESTRICT"), nullable=False, index=True),
        sa.Column("body", sa.Text(), nullable=False),
        sa.Column("attachment_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("file_attachments.id", ondelete="SET NULL"), nullable=True),
        sa.Column("is_hidden", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("sent_at", sa.DateTime(timezone=True),
                  server_default=sa.func.now(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True),
                  server_default=sa.func.now(), nullable=False, index=True),
    )

    # ── announcements ─────────────────────────────────────────────────────
    op.create_table(
        "announcements",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("institute_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("institutes.id", ondelete="RESTRICT"), nullable=True, index=True),
        sa.Column("branch_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("branches.id", ondelete="RESTRICT"), nullable=True, index=True),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("body", sa.Text(), nullable=False),
        sa.Column("target_audience", postgresql.JSONB(astext_type=sa.Text()),
                  nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("is_pinned", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("published_at", sa.DateTime(timezone=True),
                  server_default=sa.func.now(), nullable=False, index=True),
        sa.Column("created_by", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("users.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True),
                  server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True),
                  server_default=sa.func.now(), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True, index=True),
    )

    # ── ptm_requests ──────────────────────────────────────────────────────
    op.create_table(
        "ptm_requests",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("institute_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("institutes.id", ondelete="RESTRICT"), nullable=True, index=True),
        sa.Column("branch_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("branches.id", ondelete="RESTRICT"), nullable=True, index=True),
        sa.Column("parent_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("parent_profiles.id", ondelete="RESTRICT"), nullable=False, index=True),
        sa.Column("student_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("student_profiles.id", ondelete="RESTRICT"), nullable=False, index=True),
        sa.Column("teacher_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("teacher_profiles.id", ondelete="RESTRICT"), nullable=False, index=True),
        sa.Column("reason", sa.Text(), nullable=False),
        sa.Column("requested_slot", sa.DateTime(timezone=True), nullable=False),
        sa.Column("confirmed_slot", sa.DateTime(timezone=True), nullable=True),
        sa.Column("teacher_notes", sa.Text(), nullable=True),
        sa.Column("status", ptm_status_enum, nullable=False, server_default="REQUESTED", index=True),
        sa.Column("created_at", sa.DateTime(timezone=True),
                  server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True),
                  server_default=sa.func.now(), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True, index=True),
    )

    # ── reported_messages ─────────────────────────────────────────────────
    op.create_table(
        "reported_messages",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("institute_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("institutes.id", ondelete="RESTRICT"), nullable=True, index=True),
        sa.Column("branch_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("branches.id", ondelete="RESTRICT"), nullable=True, index=True),
        sa.Column("message_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("messages.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("reported_by", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("users.id", ondelete="RESTRICT"), nullable=False, index=True),
        sa.Column("reason", sa.Text(), nullable=False),
        sa.Column("status", report_status_enum, nullable=False, server_default="PENDING", index=True),
        sa.Column("resolved_by", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("resolution_notes", sa.Text(), nullable=True),
        sa.Column("action_taken", sa.String(length=50), nullable=True),
        sa.Column("resolved_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True),
                  server_default=sa.func.now(), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("reported_messages")
    op.drop_table("ptm_requests")
    op.drop_table("announcements")
    op.drop_table("messages")
    op.drop_table("conversation_participants")
    op.drop_table("conversations")
    op.drop_table("notifications")

    for enum_name in [
        "report_status_enum",
        "ptm_status_enum",
        "conversation_type_enum",
        "notification_type_enum",
    ]:
        sa.Enum(name=enum_name).drop(op.get_bind(), checkfirst=True)
