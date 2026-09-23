"""
005_academic_operations_attendance — Timetables, Sessions, Logs, Attendance & Remarks.

Creates:
  - timetables
  - class_sessions
  - session_logs
  - attendance
  - student_remarks
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "005"
down_revision = "004"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ── Enums ─────────────────────────────────────────────────────────────
    session_status_enum = postgresql.ENUM(
        "SCHEDULED", "HELD", "CANCELLED", "RESCHEDULED",
        name="class_session_status_enum", create_type=False,
    )
    session_status_enum.create(op.get_bind(), checkfirst=True)

    attendance_status_enum = postgresql.ENUM(
        "PRESENT", "ABSENT", "LATE", "EXCUSED",
        name="attendance_status_enum", create_type=False,
    )
    attendance_status_enum.create(op.get_bind(), checkfirst=True)

    # ── timetables ────────────────────────────────────────────────────────
    op.create_table(
        "timetables",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("institute_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("institutes.id", ondelete="RESTRICT"), nullable=True),
        sa.Column("branch_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("branches.id", ondelete="RESTRICT"), nullable=True),
        sa.Column("batch_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("batches.id", ondelete="CASCADE"), nullable=False),
        sa.Column("day_of_week", sa.Enum("MON", "TUE", "WED", "THU", "FRI", "SAT", "SUN", name="day_of_week_enum"),
                  nullable=False),
        sa.Column("start_time", sa.String(8), nullable=False),
        sa.Column("end_time", sa.String(8), nullable=False),
        sa.Column("room", sa.String(50), nullable=True),
        sa.Column("is_active", sa.Boolean, nullable=False, server_default="true"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_timetables_institute_id", "timetables", ["institute_id"])
    op.create_index("ix_timetables_batch_id", "timetables", ["batch_id"])
    op.create_index("ix_timetables_deleted_at", "timetables", ["deleted_at"])

    # ── class_sessions ────────────────────────────────────────────────────
    op.create_table(
        "class_sessions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("institute_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("institutes.id", ondelete="RESTRICT"), nullable=True),
        sa.Column("branch_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("branches.id", ondelete="RESTRICT"), nullable=True),
        sa.Column("batch_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("batches.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("date", sa.Date, nullable=False),
        sa.Column("start_time", sa.String(8), nullable=False),
        sa.Column("end_time", sa.String(8), nullable=False),
        sa.Column("room", sa.String(50), nullable=True),
        sa.Column("status", sa.Enum("SCHEDULED", "HELD", "CANCELLED", "RESCHEDULED",
                                    name="class_session_status_enum"),
                  nullable=False, server_default="SCHEDULED"),
        sa.Column("rescheduled_to_session_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("class_sessions.id", ondelete="SET NULL"), nullable=True),
        sa.Column("conducted_by", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("teacher_profiles.id", ondelete="SET NULL"), nullable=True),
        sa.Column("remarks", sa.Text, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_class_sessions_institute_id", "class_sessions", ["institute_id"])
    op.create_index("ix_class_sessions_batch_id", "class_sessions", ["batch_id"])
    op.create_index("ix_class_sessions_date", "class_sessions", ["date"])
    op.create_index("ix_class_sessions_status", "class_sessions", ["status"])
    op.create_index("ix_class_sessions_conducted_by", "class_sessions", ["conducted_by"])
    op.create_index("ix_class_sessions_batch_date", "class_sessions", ["batch_id", "date"])
    op.create_index("ix_class_sessions_deleted_at", "class_sessions", ["deleted_at"])

    # ── session_logs ──────────────────────────────────────────────────────
    op.create_table(
        "session_logs",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("class_session_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("class_sessions.id", ondelete="CASCADE"), nullable=False, unique=True),
        sa.Column("topic", sa.String(255), nullable=False),
        sa.Column("topics_covered", sa.Text, nullable=True),
        sa.Column("homework_notes", sa.Text, nullable=True),
        sa.Column("class_remarks", sa.Text, nullable=True),
        sa.Column("created_by", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_session_logs_class_session_id", "session_logs", ["class_session_id"])

    # ── attendance ────────────────────────────────────────────────────────
    op.create_table(
        "attendance",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("class_session_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("class_sessions.id", ondelete="CASCADE"), nullable=False),
        sa.Column("enrollment_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("enrollments.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("status", sa.Enum("PRESENT", "ABSENT", "LATE", "EXCUSED", name="attendance_status_enum"),
                  nullable=False, server_default="PRESENT"),
        sa.Column("remarks", sa.String(255), nullable=True),
        sa.Column("marked_by", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("marked_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint("class_session_id", "enrollment_id", name="uq_attendance_session_enrollment"),
    )
    op.create_index("ix_attendance_class_session_id", "attendance", ["class_session_id"])
    op.create_index("ix_attendance_enrollment_id", "attendance", ["enrollment_id"])
    op.create_index("ix_attendance_status", "attendance", ["status"])

    # ── student_remarks ───────────────────────────────────────────────────
    op.create_table(
        "student_remarks",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("institute_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("institutes.id", ondelete="RESTRICT"), nullable=True),
        sa.Column("branch_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("branches.id", ondelete="RESTRICT"), nullable=True),
        sa.Column("student_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("student_profiles.id", ondelete="CASCADE"), nullable=False),
        sa.Column("teacher_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("teacher_profiles.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("class_session_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("class_sessions.id", ondelete="SET NULL"), nullable=True),
        sa.Column("body", sa.Text, nullable=False),
        sa.Column("visible_to_parent", sa.Boolean, nullable=False, server_default="true"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_student_remarks_institute_id", "student_remarks", ["institute_id"])
    op.create_index("ix_student_remarks_student_id", "student_remarks", ["student_id"])
    op.create_index("ix_student_remarks_teacher_id", "student_remarks", ["teacher_id"])
    op.create_index("ix_student_remarks_created_at", "student_remarks", ["created_at"])


def downgrade() -> None:
    op.drop_table("student_remarks")
    op.drop_table("attendance")
    op.drop_table("session_logs")
    op.drop_table("class_sessions")
    op.drop_table("timetables")

    op.execute("DROP TYPE IF EXISTS attendance_status_enum")
    op.execute("DROP TYPE IF EXISTS class_session_status_enum")
