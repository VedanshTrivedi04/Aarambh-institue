"""
006_learning_and_storage — File attachments, Study materials, Homework & Submissions.

Creates:
  - file_attachments
  - study_materials
  - homework
  - homework_submissions
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "006"
down_revision = "005"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ── Enums ─────────────────────────────────────────────────────────────
    material_type_enum = postgresql.ENUM(
        "NOTES", "DPP", "WORKSHEET", "VIDEO", "IMPORTANT_QUESTIONS", "REVISION", "OTHER",
        name="material_type_enum", create_type=False,
    )
    material_type_enum.create(op.get_bind(), checkfirst=True)

    submission_status_enum = postgresql.ENUM(
        "SUBMITTED", "LATE", "REVIEWED", "NEEDS_IMPROVEMENT", "RESUBMIT",
        name="submission_status_enum", create_type=False,
    )
    submission_status_enum.create(op.get_bind(), checkfirst=True)

    # ── file_attachments ──────────────────────────────────────────────────
    op.create_table(
        "file_attachments",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("institute_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("institutes.id", ondelete="RESTRICT"), nullable=True),
        sa.Column("branch_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("branches.id", ondelete="RESTRICT"), nullable=True),
        sa.Column("storage_key", sa.String(255), nullable=False, unique=True),
        sa.Column("file_name", sa.String(255), nullable=False),
        sa.Column("file_size", sa.Integer, nullable=False),
        sa.Column("content_type", sa.String(100), nullable=False),
        sa.Column("uploaded_by", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_file_attachments_institute_id", "file_attachments", ["institute_id"])
    op.create_index("ix_file_attachments_storage_key", "file_attachments", ["storage_key"])
    op.create_index("ix_file_attachments_uploaded_by", "file_attachments", ["uploaded_by"])

    # ── study_materials ───────────────────────────────────────────────────
    op.create_table(
        "study_materials",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("institute_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("institutes.id", ondelete="RESTRICT"), nullable=True),
        sa.Column("branch_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("branches.id", ondelete="RESTRICT"), nullable=True),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("type", sa.Enum("NOTES", "DPP", "WORKSHEET", "VIDEO", "IMPORTANT_QUESTIONS",
                                  "REVISION", "OTHER", name="material_type_enum"),
                  nullable=False, server_default="NOTES"),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("target_course_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("courses.id", ondelete="SET NULL"), nullable=True),
        sa.Column("target_batch_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("batches.id", ondelete="SET NULL"), nullable=True),
        sa.Column("attachment_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("file_attachments.id", ondelete="SET NULL"), nullable=True),
        sa.Column("uploaded_by", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("is_published", sa.Boolean, nullable=False, server_default="true"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_study_materials_institute_id", "study_materials", ["institute_id"])
    op.create_index("ix_study_materials_type", "study_materials", ["type"])
    op.create_index("ix_study_materials_target_course_id", "study_materials", ["target_course_id"])
    op.create_index("ix_study_materials_target_batch_id", "study_materials", ["target_batch_id"])
    op.create_index("ix_study_materials_deleted_at", "study_materials", ["deleted_at"])

    # ── homework ──────────────────────────────────────────────────────────
    op.create_table(
        "homework",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("institute_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("institutes.id", ondelete="RESTRICT"), nullable=True),
        sa.Column("branch_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("branches.id", ondelete="RESTRICT"), nullable=True),
        sa.Column("batch_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("batches.id", ondelete="CASCADE"), nullable=False),
        sa.Column("subject_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("subjects.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("instructions", sa.Text, nullable=True),
        sa.Column("chapter", sa.String(100), nullable=True),
        sa.Column("due_date", sa.Date, nullable=False),
        sa.Column("attachment_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("file_attachments.id", ondelete="SET NULL"), nullable=True),
        sa.Column("created_by", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_homework_institute_id", "homework", ["institute_id"])
    op.create_index("ix_homework_batch_id", "homework", ["batch_id"])
    op.create_index("ix_homework_subject_id", "homework", ["subject_id"])
    op.create_index("ix_homework_due_date", "homework", ["due_date"])
    op.create_index("ix_homework_deleted_at", "homework", ["deleted_at"])

    # ── homework_submissions ──────────────────────────────────────────────
    op.create_table(
        "homework_submissions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("homework_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("homework.id", ondelete="CASCADE"), nullable=False),
        sa.Column("student_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("student_profiles.id", ondelete="CASCADE"), nullable=False),
        sa.Column("attachment_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("file_attachments.id", ondelete="SET NULL"), nullable=True),
        sa.Column("submission_text", sa.Text, nullable=True),
        sa.Column("status", sa.Enum("SUBMITTED", "LATE", "REVIEWED", "NEEDS_IMPROVEMENT", "RESUBMIT",
                                    name="submission_status_enum"),
                  nullable=False, server_default="SUBMITTED"),
        sa.Column("marks", sa.Float, nullable=True),
        sa.Column("max_marks", sa.Float, nullable=True),
        sa.Column("teacher_comment", sa.Text, nullable=True),
        sa.Column("submitted_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("reviewed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("reviewed_by", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.UniqueConstraint("homework_id", "student_id", name="uq_homework_student_submission"),
    )
    op.create_index("ix_homework_submissions_homework_id", "homework_submissions", ["homework_id"])
    op.create_index("ix_homework_submissions_student_id", "homework_submissions", ["student_id"])
    op.create_index("ix_homework_submissions_status", "homework_submissions", ["status"])


def downgrade() -> None:
    op.drop_table("homework_submissions")
    op.drop_table("homework")
    op.drop_table("study_materials")
    op.drop_table("file_attachments")

    op.execute("DROP TYPE IF EXISTS submission_status_enum")
    op.execute("DROP TYPE IF EXISTS material_type_enum")
