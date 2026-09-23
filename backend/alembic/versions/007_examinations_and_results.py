"""
007_examinations_and_results — Question bank, Tests, Question mapping & Results.

Creates:
  - questions
  - tests
  - test_questions
  - test_results
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "007"
down_revision = "006"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ── Enums ─────────────────────────────────────────────────────────────
    difficulty_enum = postgresql.ENUM(
        "EASY", "MEDIUM", "HARD",
        name="question_difficulty_enum", create_type=False,
    )
    difficulty_enum.create(op.get_bind(), checkfirst=True)

    question_type_enum = postgresql.ENUM(
        "OBJECTIVE", "SUBJECTIVE",
        name="question_type_enum", create_type=False,
    )
    question_type_enum.create(op.get_bind(), checkfirst=True)

    test_type_enum = postgresql.ENUM(
        "CLASS", "CHAPTER", "UNIT", "MONTHLY", "HALF_YEARLY", "PRE_BOARD", "MOCK", "SPECIAL",
        name="test_type_enum", create_type=False,
    )
    test_type_enum.create(op.get_bind(), checkfirst=True)

    test_status_enum = postgresql.ENUM(
        "DRAFT", "SCHEDULED", "CONDUCTED", "EVALUATING", "PUBLISHED",
        name="test_status_enum", create_type=False,
    )
    test_status_enum.create(op.get_bind(), checkfirst=True)

    # ── questions ─────────────────────────────────────────────────────────
    op.create_table(
        "questions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("institute_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("institutes.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("branch_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("branches.id", ondelete="RESTRICT"), nullable=True),
        sa.Column("board_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("boards.id", ondelete="SET NULL"), nullable=True),
        sa.Column("class_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("school_classes.id", ondelete="SET NULL"), nullable=True),
        sa.Column("stream_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("streams.id", ondelete="SET NULL"), nullable=True),
        sa.Column("subject_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("subjects.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("chapter", sa.String(255), nullable=True),
        sa.Column("topic", sa.String(255), nullable=True),
        sa.Column("difficulty", difficulty_enum, nullable=False, server_default="MEDIUM"),
        sa.Column("question_type", question_type_enum, nullable=False, server_default="SUBJECTIVE"),
        sa.Column("body", sa.Text, nullable=False),
        sa.Column("options", postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column("correct_answer", sa.Text, nullable=True),
        sa.Column("explanation", sa.Text, nullable=True),
        sa.Column("default_marks", sa.Float, nullable=False, server_default="1.0"),
        sa.Column("created_by", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("users.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_questions_institute_id", "questions", ["institute_id"])
    op.create_index("ix_questions_subject_id", "questions", ["subject_id"])
    op.create_index("ix_questions_board_id", "questions", ["board_id"])
    op.create_index("ix_questions_class_id", "questions", ["class_id"])
    op.create_index("ix_questions_difficulty", "questions", ["difficulty"])
    op.create_index("ix_questions_chapter", "questions", ["chapter"])

    # ── tests ─────────────────────────────────────────────────────────────
    op.create_table(
        "tests",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("institute_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("institutes.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("branch_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("branches.id", ondelete="RESTRICT"), nullable=True),
        sa.Column("course_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("courses.id", ondelete="SET NULL"), nullable=True),
        sa.Column("batch_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("batches.id", ondelete="SET NULL"), nullable=True),
        sa.Column("subject_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("subjects.id", ondelete="SET NULL"), nullable=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("type", test_type_enum, nullable=False, server_default="CLASS"),
        sa.Column("date", sa.Date, nullable=False),
        sa.Column("start_time", sa.Time, nullable=True),
        sa.Column("duration_minutes", sa.Integer, nullable=True),
        sa.Column("max_marks", sa.Float, nullable=False),
        sa.Column("passing_marks", sa.Float, nullable=True),
        sa.Column("status", test_status_enum, nullable=False, server_default="DRAFT"),
        sa.Column("instructions", sa.Text, nullable=True),
        sa.Column("created_by", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("users.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("published_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("published_by", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_tests_institute_id", "tests", ["institute_id"])
    op.create_index("ix_tests_batch_id", "tests", ["batch_id"])
    op.create_index("ix_tests_course_id", "tests", ["course_id"])
    op.create_index("ix_tests_date", "tests", ["date"])
    op.create_index("ix_tests_status", "tests", ["status"])

    # ── test_questions ────────────────────────────────────────────────────
    op.create_table(
        "test_questions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("test_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("tests.id", ondelete="CASCADE"), nullable=False),
        sa.Column("question_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("questions.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("marks", sa.Float, nullable=False),
        sa.Column("display_order", sa.Integer, nullable=False, server_default="1"),
        sa.Column("section", sa.String(50), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
        sa.UniqueConstraint("test_id", "question_id", name="uq_test_question"),
    )
    op.create_index("ix_test_questions_test_id", "test_questions", ["test_id"])
    op.create_index("ix_test_questions_question_id", "test_questions", ["question_id"])

    # ── test_results ──────────────────────────────────────────────────────
    op.create_table(
        "test_results",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("test_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("tests.id", ondelete="CASCADE"), nullable=False),
        sa.Column("student_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("student_profiles.id", ondelete="CASCADE"), nullable=False),
        sa.Column("marks_obtained", sa.Float, nullable=True),
        sa.Column("is_absent", sa.Boolean, nullable=False, server_default="false"),
        sa.Column("percentage", sa.Float, nullable=True),
        sa.Column("percentile", sa.Float, nullable=True),
        sa.Column("rank", sa.Integer, nullable=True),
        sa.Column("remarks", sa.Text, nullable=True),
        sa.Column("evaluated_by", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
        sa.UniqueConstraint("test_id", "student_id", name="uq_test_student_result"),
    )
    op.create_index("ix_test_results_test_id", "test_results", ["test_id"])
    op.create_index("ix_test_results_student_id", "test_results", ["student_id"])


def downgrade() -> None:
    op.drop_table("test_results")
    op.drop_table("test_questions")
    op.drop_table("tests")
    op.drop_table("questions")

    op.execute("DROP TYPE IF EXISTS test_status_enum")
    op.execute("DROP TYPE IF EXISTS test_type_enum")
    op.execute("DROP TYPE IF EXISTS question_type_enum")
    op.execute("DROP TYPE IF EXISTS question_difficulty_enum")
