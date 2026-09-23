"""
app/models/examination.py
-------------------------
Examinations, Question Bank, Tests & Results models:
  - Question: Question bank item with taxonomy (board, class, subject), difficulty, type, and options
  - Test: Scheduled/conducted examination for a batch/course
  - TestQuestion: Association mapping questions to tests with marks allocation
  - TestResult: Student marks, attendance (absent), percentile, and rank
"""

from __future__ import annotations

import enum
import uuid
from datetime import date as Date, datetime, time as Time
from typing import TYPE_CHECKING, Any

from sqlalchemy import (
    Boolean,
    Date as SADate,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Integer,
    JSON,
    String,
    Text,
    Time as SATime,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, SoftDeleteMixin, TenantAwareMixin, TimestampMixin

if TYPE_CHECKING:
    from app.models.academic_structure import Batch, Board, Course, SchoolClass, Subject
    from app.models.people import StudentProfile
    from app.models.user import User


class QuestionDifficulty(str, enum.Enum):
    EASY = "EASY"
    MEDIUM = "MEDIUM"
    HARD = "HARD"


class QuestionType(str, enum.Enum):
    OBJECTIVE = "OBJECTIVE"
    SUBJECTIVE = "SUBJECTIVE"


class TestType(str, enum.Enum):
    CLASS = "CLASS"
    CHAPTER = "CHAPTER"
    UNIT = "UNIT"
    MONTHLY = "MONTHLY"
    HALF_YEARLY = "HALF_YEARLY"
    PRE_BOARD = "PRE_BOARD"
    MOCK = "MOCK"
    SPECIAL = "SPECIAL"


class TestStatus(str, enum.Enum):
    DRAFT = "DRAFT"
    SCHEDULED = "SCHEDULED"
    CONDUCTED = "CONDUCTED"
    EVALUATING = "EVALUATING"
    PUBLISHED = "PUBLISHED"


# ─────────────────────────────────────────────────────────────────────────────
# Question
# ─────────────────────────────────────────────────────────────────────────────

class Question(TenantAwareMixin, TimestampMixin, SoftDeleteMixin, Base):
    """
    Reusable question stored in the institute's Question Bank.
    Can be filtered by taxonomy (board, class, stream, subject, chapter, topic, difficulty).
    """
    __tablename__ = "questions"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    board_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("boards.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    class_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("school_classes.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    stream_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("streams.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    subject_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("subjects.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )

    chapter: Mapped[str | None] = mapped_column(String(255), nullable=True, index=True)
    topic: Mapped[str | None] = mapped_column(String(255), nullable=True, index=True)

    difficulty: Mapped[QuestionDifficulty] = mapped_column(
        Enum(QuestionDifficulty), default=QuestionDifficulty.MEDIUM, nullable=False, index=True
    )
    question_type: Mapped[QuestionType] = mapped_column(
        Enum(QuestionType), default=QuestionType.SUBJECTIVE, nullable=False, index=True
    )

    body: Mapped[str] = mapped_column(Text, nullable=False)
    options: Mapped[list[dict[str, Any]] | None] = mapped_column(JSON, nullable=True)
    correct_answer: Mapped[str | None] = mapped_column(Text, nullable=True)
    explanation: Mapped[str | None] = mapped_column(Text, nullable=True)
    default_marks: Mapped[float] = mapped_column(Float, default=1.0, nullable=False)

    created_by: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=False,
    )

    # Relationships
    subject: Mapped["Subject"] = relationship("Subject", lazy="selectin")
    board: Mapped["Board | None"] = relationship("Board", lazy="selectin")
    school_class: Mapped["SchoolClass | None"] = relationship("SchoolClass", lazy="selectin")
    creator: Mapped["User"] = relationship("User", foreign_keys=[created_by], lazy="selectin")
    test_questions: Mapped[list["TestQuestion"]] = relationship(
        "TestQuestion", back_populates="question", cascade="all, delete-orphan"
    )


# ─────────────────────────────────────────────────────────────────────────────
# Test
# ─────────────────────────────────────────────────────────────────────────────

class Test(TenantAwareMixin, TimestampMixin, SoftDeleteMixin, Base):
    """
    An assessment scheduled or conducted for students of a batch, course, or institute.
    Transitions: DRAFT -> SCHEDULED -> CONDUCTED -> EVALUATING -> PUBLISHED.
    """
    __tablename__ = "tests"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    course_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("courses.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    batch_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("batches.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    subject_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("subjects.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    type: Mapped[TestType] = mapped_column(
        Enum(TestType), default=TestType.CLASS, nullable=False, index=True
    )
    date: Mapped[Date] = mapped_column(SADate, nullable=False, index=True)
    start_time: Mapped[Time | None] = mapped_column(SATime, nullable=True)
    duration_minutes: Mapped[int | None] = mapped_column(Integer, nullable=True)

    max_marks: Mapped[float] = mapped_column(Float, nullable=False)
    passing_marks: Mapped[float | None] = mapped_column(Float, nullable=True)

    status: Mapped[TestStatus] = mapped_column(
        Enum(TestStatus), default=TestStatus.DRAFT, nullable=False, index=True
    )
    instructions: Mapped[str | None] = mapped_column(Text, nullable=True)

    created_by: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=False,
    )
    published_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    published_by: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )

    # Relationships
    course: Mapped["Course | None"] = relationship("Course", lazy="selectin")
    batch: Mapped["Batch | None"] = relationship("Batch", lazy="selectin")
    subject: Mapped["Subject | None"] = relationship("Subject", lazy="selectin")
    creator: Mapped["User"] = relationship("User", foreign_keys=[created_by], lazy="selectin")
    publisher: Mapped["User | None"] = relationship("User", foreign_keys=[published_by], lazy="selectin")

    test_questions: Mapped[list["TestQuestion"]] = relationship(
        "TestQuestion",
        back_populates="test",
        cascade="all, delete-orphan",
        order_by="TestQuestion.display_order",
        lazy="selectin",
    )
    results: Mapped[list["TestResult"]] = relationship(
        "TestResult",
        back_populates="test",
        cascade="all, delete-orphan",
        lazy="selectin",
    )


# ─────────────────────────────────────────────────────────────────────────────
# TestQuestion
# ─────────────────────────────────────────────────────────────────────────────

class TestQuestion(TimestampMixin, Base):
    """
    Mapping table assigning questions to a test with test-specific marks & display ordering.
    """
    __tablename__ = "test_questions"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    test_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("tests.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    question_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("questions.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    marks: Mapped[float] = mapped_column(Float, nullable=False)
    display_order: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    section: Mapped[str | None] = mapped_column(String(50), nullable=True)

    __table_args__ = (
        UniqueConstraint("test_id", "question_id", name="uq_test_question"),
    )

    # Relationships
    test: Mapped["Test"] = relationship("Test", back_populates="test_questions")
    question: Mapped["Question"] = relationship("Question", back_populates="test_questions", lazy="selectin")


# ─────────────────────────────────────────────────────────────────────────────
# TestResult
# ─────────────────────────────────────────────────────────────────────────────

class TestResult(TimestampMixin, Base):
    """
    Evaluation result for a student in a test.
    Stores absolute marks obtained, absent flag, percentile rank, and ranking position.
    """
    __tablename__ = "test_results"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    test_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("tests.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    student_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("student_profiles.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    marks_obtained: Mapped[float | None] = mapped_column(Float, nullable=True)
    is_absent: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    percentage: Mapped[float | None] = mapped_column(Float, nullable=True)
    percentile: Mapped[float | None] = mapped_column(Float, nullable=True)
    rank: Mapped[int | None] = mapped_column(Integer, nullable=True)
    remarks: Mapped[str | None] = mapped_column(Text, nullable=True)

    evaluated_by: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )

    __table_args__ = (
        UniqueConstraint("test_id", "student_id", name="uq_test_student_result"),
    )

    # Relationships
    test: Mapped["Test"] = relationship("Test", back_populates="results")
    student: Mapped["StudentProfile"] = relationship("StudentProfile", lazy="selectin")
    evaluator: Mapped["User | None"] = relationship("User", foreign_keys=[evaluated_by], lazy="selectin")
