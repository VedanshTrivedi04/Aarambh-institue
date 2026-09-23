"""
002_academic_structure — Academic structure schema.

Creates:
  - academic_years
  - boards
  - school_classes
  - streams
  - subjects
  - courses
  - course_subjects
  - batches

REVIEW NOTES:
  - academic_years.is_current has no DB-level unique constraint — uniqueness
    (only one current year per institute) is enforced in the service layer
    (update_academic_year atomically clears others before setting).
  - batches.days uses PostgreSQL TEXT[] (ARRAY) — simpler than a separate
    batch_schedule table for the current load profile; can be normalised later.
  - batches.teacher_id has NO FK constraint yet (teacher_profiles added in
    Slice 4) — added here as a nullable UUID, FK constraint added in Slice 4.
  - course_subjects uses a composite PK instead of a surrogate UUID, per
    codeoptimisation.md §3 (avoid UUIDs on pure join tables).
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "002"
down_revision = "001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ── academic_years ────────────────────────────────────────────────────
    op.create_table(
        "academic_years",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("institute_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("institutes.id", ondelete="RESTRICT"), nullable=True),
        sa.Column("branch_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("branches.id", ondelete="RESTRICT"), nullable=True),
        sa.Column("name", sa.String(20), nullable=False),
        sa.Column("start_date", sa.Date, nullable=False),
        sa.Column("end_date", sa.Date, nullable=False),
        sa.Column("is_current", sa.Boolean, nullable=False, server_default="false"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.UniqueConstraint("institute_id", "name", name="uq_academic_years_institute_name"),
    )
    op.create_index("ix_academic_years_institute_id", "academic_years", ["institute_id"])
    op.create_index("ix_academic_years_deleted_at", "academic_years", ["deleted_at"])

    # ── boards ────────────────────────────────────────────────────────────
    op.create_table(
        "boards",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("institute_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("institutes.id", ondelete="RESTRICT"), nullable=True),
        sa.Column("branch_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("branches.id", ondelete="RESTRICT"), nullable=True),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("code", sa.String(20), nullable=False),
        sa.Column("is_active", sa.Boolean, nullable=False, server_default="true"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint("institute_id", "code", name="uq_boards_institute_code"),
    )
    op.create_index("ix_boards_institute_id", "boards", ["institute_id"])

    # ── school_classes ────────────────────────────────────────────────────
    op.create_table(
        "school_classes",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("institute_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("institutes.id", ondelete="RESTRICT"), nullable=True),
        sa.Column("branch_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("branches.id", ondelete="RESTRICT"), nullable=True),
        sa.Column("board_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("boards.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("name", sa.String(20), nullable=False),
        sa.Column("display_order", sa.SmallInteger, nullable=False, server_default="0"),
        sa.Column("is_active", sa.Boolean, nullable=False, server_default="true"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint("board_id", "name", name="uq_school_classes_board_name"),
    )
    op.create_index("ix_school_classes_board_id", "school_classes", ["board_id"])
    op.create_index("ix_school_classes_institute_id", "school_classes", ["institute_id"])

    # ── streams ───────────────────────────────────────────────────────────
    op.create_table(
        "streams",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("institute_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("institutes.id", ondelete="RESTRICT"), nullable=True),
        sa.Column("branch_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("branches.id", ondelete="RESTRICT"), nullable=True),
        sa.Column("class_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("school_classes.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("name", sa.String(50), nullable=False),
        sa.Column("is_active", sa.Boolean, nullable=False, server_default="true"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint("class_id", "name", name="uq_streams_class_name"),
    )
    op.create_index("ix_streams_class_id", "streams", ["class_id"])

    # ── subjects ──────────────────────────────────────────────────────────
    op.create_table(
        "subjects",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("institute_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("institutes.id", ondelete="RESTRICT"), nullable=True),
        sa.Column("branch_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("branches.id", ondelete="RESTRICT"), nullable=True),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("code", sa.String(20), nullable=False),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("is_active", sa.Boolean, nullable=False, server_default="true"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint("institute_id", "code", name="uq_subjects_institute_code"),
    )
    op.create_index("ix_subjects_institute_id", "subjects", ["institute_id"])

    # ── courses ───────────────────────────────────────────────────────────
    op.create_table(
        "courses",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("institute_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("institutes.id", ondelete="RESTRICT"), nullable=True),
        sa.Column("branch_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("branches.id", ondelete="RESTRICT"), nullable=True),
        sa.Column("academic_year_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("academic_years.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("class_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("school_classes.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("stream_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("streams.id", ondelete="RESTRICT"), nullable=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("code", sa.String(50), nullable=False),
        sa.Column("duration_months", sa.SmallInteger, nullable=False, server_default="12"),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("is_active", sa.Boolean, nullable=False, server_default="true"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.UniqueConstraint(
            "institute_id", "academic_year_id", "code",
            name="uq_courses_institute_year_code"
        ),
    )
    op.create_index("ix_courses_institute_id", "courses", ["institute_id"])
    op.create_index("ix_courses_academic_year_id", "courses", ["academic_year_id"])
    op.create_index("ix_courses_class_id", "courses", ["class_id"])
    op.create_index("ix_courses_deleted_at", "courses", ["deleted_at"])

    # ── course_subjects ───────────────────────────────────────────────────
    op.create_table(
        "course_subjects",
        sa.Column("course_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("courses.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("subject_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("subjects.id", ondelete="RESTRICT"), primary_key=True),
        sa.UniqueConstraint("course_id", "subject_id", name="uq_course_subjects"),
    )

    # ── batches ───────────────────────────────────────────────────────────
    op.create_table(
        "batches",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("institute_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("institutes.id", ondelete="RESTRICT"), nullable=True),
        sa.Column("branch_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("branches.id", ondelete="RESTRICT"), nullable=True),
        sa.Column("course_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("courses.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("subject_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("subjects.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("teacher_id", postgresql.UUID(as_uuid=True), nullable=True),  # FK added Slice 4
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("room", sa.String(50), nullable=True),
        sa.Column("capacity", sa.Integer, nullable=False, server_default="30"),
        sa.Column("start_time", sa.String(8), nullable=True),
        sa.Column("end_time", sa.String(8), nullable=True),
        sa.Column("days", postgresql.ARRAY(sa.String(3)), nullable=True),
        sa.Column("start_date", sa.Date, nullable=True),
        sa.Column("is_active", sa.Boolean, nullable=False, server_default="true"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.UniqueConstraint("institute_id", "name", name="uq_batches_institute_name"),
        sa.CheckConstraint("capacity > 0", name="ck_batches_capacity_positive"),
    )
    op.create_index("ix_batches_institute_id", "batches", ["institute_id"])
    op.create_index("ix_batches_course_id", "batches", ["course_id"])
    op.create_index("ix_batches_subject_id", "batches", ["subject_id"])
    op.create_index("ix_batches_teacher_id", "batches", ["teacher_id"])
    op.create_index("ix_batches_deleted_at", "batches", ["deleted_at"])


def downgrade() -> None:
    op.drop_table("batches")
    op.drop_table("course_subjects")
    op.drop_table("courses")
    op.drop_table("subjects")
    op.drop_table("streams")
    op.drop_table("school_classes")
    op.drop_table("boards")
    op.drop_table("academic_years")
