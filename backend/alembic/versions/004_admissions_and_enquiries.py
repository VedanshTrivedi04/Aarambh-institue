"""
004_admissions_and_enquiries — Enquiries CRM and Admission Pipeline.

Creates:
  - enquiries
  - enquiry_follow_ups
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "004"
down_revision = "003"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ── Enums ─────────────────────────────────────────────────────────────
    source_enum = postgresql.ENUM(
        "WALK_IN", "WEBSITE", "REFERRAL", "PHONE", "SOCIAL_MEDIA", "DIRECT", "OTHER",
        name="enquiry_source_enum", create_type=False,
    )
    source_enum.create(op.get_bind(), checkfirst=True)

    stage_enum = postgresql.ENUM(
        "NEW", "CONTACTED", "COUNSELLING", "DEMO", "INTERESTED",
        "ADMISSION", "NOT_INTERESTED", "FOLLOW_UP_LATER",
        name="enquiry_stage_enum", create_type=False,
    )
    stage_enum.create(op.get_bind(), checkfirst=True)

    # ── enquiries ─────────────────────────────────────────────────────────
    op.create_table(
        "enquiries",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("institute_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("institutes.id", ondelete="RESTRICT"), nullable=True),
        sa.Column("branch_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("branches.id", ondelete="RESTRICT"), nullable=True),
        sa.Column("student_name", sa.String(150), nullable=False),
        sa.Column("student_email", sa.String(255), nullable=True),
        sa.Column("student_phone", sa.String(20), nullable=True),
        sa.Column("parent_name", sa.String(150), nullable=False),
        sa.Column("parent_email", sa.String(255), nullable=True),
        sa.Column("parent_phone", sa.String(20), nullable=False),
        sa.Column("board_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("boards.id", ondelete="SET NULL"), nullable=True),
        sa.Column("class_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("school_classes.id", ondelete="SET NULL"), nullable=True),
        sa.Column("interested_course_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("courses.id", ondelete="SET NULL"), nullable=True),
        sa.Column("source", sa.Enum("WALK_IN", "WEBSITE", "REFERRAL", "PHONE", "SOCIAL_MEDIA", "DIRECT", "OTHER",
                                    name="enquiry_source_enum"), nullable=False, server_default="WALK_IN"),
        sa.Column("stage", sa.Enum("NEW", "CONTACTED", "COUNSELLING", "DEMO", "INTERESTED", "ADMISSION",
                                   "NOT_INTERESTED", "FOLLOW_UP_LATER", name="enquiry_stage_enum"),
                  nullable=False, server_default="NEW"),
        sa.Column("counsellor_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("follow_up_date", sa.Date, nullable=True),
        sa.Column("remarks", sa.Text, nullable=True),
        sa.Column("converted_student_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("student_profiles.id", ondelete="SET NULL"), nullable=True),
        sa.Column("converted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_enquiries_institute_id", "enquiries", ["institute_id"])
    op.create_index("ix_enquiries_stage", "enquiries", ["stage"])
    op.create_index("ix_enquiries_counsellor_id", "enquiries", ["counsellor_id"])
    op.create_index("ix_enquiries_follow_up_date", "enquiries", ["follow_up_date"])
    op.create_index("ix_enquiries_converted_student_id", "enquiries", ["converted_student_id"])
    op.create_index("ix_enquiries_deleted_at", "enquiries", ["deleted_at"])

    # ── enquiry_follow_ups ────────────────────────────────────────────────
    op.create_table(
        "enquiry_follow_ups",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("enquiry_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("enquiries.id", ondelete="CASCADE"), nullable=False),
        sa.Column("author_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("stage_before", sa.Enum("NEW", "CONTACTED", "COUNSELLING", "DEMO", "INTERESTED",
                                          "ADMISSION", "NOT_INTERESTED", "FOLLOW_UP_LATER",
                                          name="enquiry_stage_enum", create_type=False), nullable=True),
        sa.Column("stage_after", sa.Enum("NEW", "CONTACTED", "COUNSELLING", "DEMO", "INTERESTED",
                                         "ADMISSION", "NOT_INTERESTED", "FOLLOW_UP_LATER",
                                         name="enquiry_stage_enum", create_type=False), nullable=False),
        sa.Column("notes", sa.Text, nullable=False),
        sa.Column("next_follow_up_date", sa.Date, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_enquiry_follow_ups_enquiry_id", "enquiry_follow_ups", ["enquiry_id"])
    op.create_index("ix_enquiry_follow_ups_created_at", "enquiry_follow_ups", ["created_at"])


def downgrade() -> None:
    op.drop_table("enquiry_follow_ups")
    op.drop_table("enquiries")

    op.execute("DROP TYPE IF EXISTS enquiry_stage_enum")
    op.execute("DROP TYPE IF EXISTS enquiry_source_enum")
