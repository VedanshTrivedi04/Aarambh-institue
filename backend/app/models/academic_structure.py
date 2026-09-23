"""
app/models/academic_structure.py
---------------------------------
Academic backbone models.  Every feature module (attendance, homework,
exams, fees, chat) ultimately hangs off Enrollment, which itself points
at a Course + Batch pair defined here.

Hierarchy (architecture.md §5, skill.md):
    Board → Class → (Stream, Classes 11-12 only) → Course → Subjects → Batch

Key rules:
  - Stream exists ONLY for Classes 11-12; nullable FK on Course.
  - Course belongs to one AcademicYear — this is how historical data is kept
    separate across years.
  - Batch is the concrete "section" students sit in: one Course, one Subject,
    one Teacher, a schedule, a capacity.
  - CourseSubject is the join table mapping which Subjects make up a Course.
  - Entities must NOT be collapsed: keep Board/Class/Stream/Course/Subject/Batch
    as distinct models (skill.md §2, architecture.md §5).
  - All models carry TenantAwareMixin — every query is scoped by institute_id.
"""

from __future__ import annotations

import enum
import uuid
from datetime import date as Date
from typing import TYPE_CHECKING

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Date as SADate,
    ForeignKey,
    Integer,
    SmallInteger,
    String,
    Text,
    Time,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import ARRAY, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, SoftDeleteMixin, TenantAwareMixin, TimestampMixin

if TYPE_CHECKING:
    from app.models.user import User


# ─────────────────────────────────────────────────────────────────────────────
# AcademicYear
# ─────────────────────────────────────────────────────────────────────────────

class AcademicYear(TenantAwareMixin, TimestampMixin, SoftDeleteMixin, Base):
    """
    e.g. "2025-26", "2026-27".

    is_current=True marks the active year used as default in the UI.
    Only one row per institute should have is_current=True at a time
    — enforced by the service layer before toggling.
    """

    __tablename__ = "academic_years"
    __table_args__ = (
        UniqueConstraint("institute_id", "name", name="uq_academic_years_institute_name"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(20), nullable=False)        # "2025-26"
    start_date: Mapped[Date] = mapped_column(SADate, nullable=False)
    end_date: Mapped[Date] = mapped_column(SADate, nullable=False)
    is_current: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    courses: Mapped[list["Course"]] = relationship("Course", back_populates="academic_year", lazy="noload")

    def __repr__(self) -> str:
        return f"<AcademicYear {self.name} institute={self.institute_id}>"


# ─────────────────────────────────────────────────────────────────────────────
# Board
# ─────────────────────────────────────────────────────────────────────────────

class Board(TenantAwareMixin, TimestampMixin, Base):
    """
    Examination board — CBSE, MP Board, ICSE, etc.
    Scoped to institute so custom boards can be created per institute.
    """

    __tablename__ = "boards"
    __table_args__ = (
        UniqueConstraint("institute_id", "code", name="uq_boards_institute_code"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    code: Mapped[str] = mapped_column(String(20), nullable=False)   # "CBSE", "MPBOARD", "ICSE"
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    classes: Mapped[list["Class"]] = relationship("Class", back_populates="board", lazy="noload")

    def __repr__(self) -> str:
        return f"<Board code={self.code!r}>"


# ─────────────────────────────────────────────────────────────────────────────
# Class  (renamed to SchoolClass to avoid shadowing Python built-in)
# ─────────────────────────────────────────────────────────────────────────────

class SchoolClass(TenantAwareMixin, TimestampMixin, Base):
    """
    Grade level — Class 8 through Class 12.
    Belongs to a Board.  display_order drives the sort in the UI.
    """

    __tablename__ = "school_classes"
    __table_args__ = (
        UniqueConstraint("board_id", "name", name="uq_school_classes_board_name"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    board_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("boards.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String(20), nullable=False)        # "Class 8", "Class 12"
    display_order: Mapped[int] = mapped_column(SmallInteger, default=0, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    board: Mapped["Board"] = relationship("Board", back_populates="classes", lazy="noload")
    streams: Mapped[list["Stream"]] = relationship("Stream", back_populates="school_class", lazy="noload")
    courses: Mapped[list["Course"]] = relationship("Course", back_populates="school_class", lazy="noload")

    def __repr__(self) -> str:
        return f"<SchoolClass {self.name!r} board={self.board_id}>"


# Fix back-ref on Board
Board.classes = relationship("SchoolClass", back_populates="board", lazy="noload")  # type: ignore[assignment]


# ─────────────────────────────────────────────────────────────────────────────
# Stream  (Classes 11-12 only)
# ─────────────────────────────────────────────────────────────────────────────

class Stream(TenantAwareMixin, TimestampMixin, Base):
    """
    Academic stream — PCM, PCB, Commerce, Arts.
    Exists only for Classes 11-12.  Course.stream_id is nullable for 8-10.
    """

    __tablename__ = "streams"
    __table_args__ = (
        UniqueConstraint("class_id", "name", name="uq_streams_class_name"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    class_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("school_classes.id", ondelete="RESTRICT"),
        nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String(50), nullable=False)        # "PCM", "Commerce"
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    school_class: Mapped["SchoolClass"] = relationship(
        "SchoolClass", back_populates="streams", lazy="noload"
    )
    courses: Mapped[list["Course"]] = relationship("Course", back_populates="stream", lazy="noload")

    def __repr__(self) -> str:
        return f"<Stream {self.name!r} class={self.class_id}>"


# ─────────────────────────────────────────────────────────────────────────────
# Subject
# ─────────────────────────────────────────────────────────────────────────────

class Subject(TenantAwareMixin, TimestampMixin, Base):
    """
    A teachable subject — Mathematics, Physics, Chemistry, English, etc.
    Shared across boards/classes; the CourseSubject join narrows scope.
    """

    __tablename__ = "subjects"
    __table_args__ = (
        UniqueConstraint("institute_id", "code", name="uq_subjects_institute_code"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    code: Mapped[str] = mapped_column(String(20), nullable=False)       # "MATH", "PHY", "ENG"
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    course_subjects: Mapped[list["CourseSubject"]] = relationship(
        "CourseSubject", back_populates="subject", lazy="noload"
    )
    batches: Mapped[list["Batch"]] = relationship("Batch", back_populates="subject", lazy="noload")

    def __repr__(self) -> str:
        return f"<Subject code={self.code!r}>"


# ─────────────────────────────────────────────────────────────────────────────
# Course
# ─────────────────────────────────────────────────────────────────────────────

class Course(TenantAwareMixin, TimestampMixin, SoftDeleteMixin, Base):
    """
    A teaching programme offered in a given academic year.
    e.g. "Class 10 CBSE Complete 2025-26" or "Class 12 PCM 2025-26".

    stream_id is nullable (only set for Classes 11-12).
    code must be unique within (institute, academic_year) — service enforces this.
    """

    __tablename__ = "courses"
    __table_args__ = (
        UniqueConstraint(
            "institute_id", "academic_year_id", "code",
            name="uq_courses_institute_year_code"
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    academic_year_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("academic_years.id", ondelete="RESTRICT"),
        nullable=False, index=True
    )
    class_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("school_classes.id", ondelete="RESTRICT"),
        nullable=False, index=True
    )
    stream_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("streams.id", ondelete="RESTRICT"),
        nullable=True, index=True
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    code: Mapped[str] = mapped_column(String(50), nullable=False)
    duration_months: Mapped[int] = mapped_column(SmallInteger, nullable=False, default=12)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # Relationships
    academic_year: Mapped["AcademicYear"] = relationship(
        "AcademicYear", back_populates="courses", lazy="noload"
    )
    school_class: Mapped["SchoolClass"] = relationship(
        "SchoolClass", back_populates="courses", lazy="noload"
    )
    stream: Mapped["Stream | None"] = relationship(
        "Stream", back_populates="courses", lazy="noload"
    )
    course_subjects: Mapped[list["CourseSubject"]] = relationship(
        "CourseSubject", back_populates="course", lazy="noload", cascade="all, delete-orphan"
    )
    batches: Mapped[list["Batch"]] = relationship(
        "Batch", back_populates="course", lazy="noload"
    )

    def __repr__(self) -> str:
        return f"<Course code={self.code!r} year={self.academic_year_id}>"


# ─────────────────────────────────────────────────────────────────────────────
# CourseSubject  (join table)
# ─────────────────────────────────────────────────────────────────────────────

class CourseSubject(Base):
    """
    Which subjects make up a course.
    e.g. "Class 10 CBSE Complete" includes Math, Science, English, SST, Hindi.
    """

    __tablename__ = "course_subjects"
    __table_args__ = (
        UniqueConstraint("course_id", "subject_id", name="uq_course_subjects"),
    )

    course_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("courses.id", ondelete="CASCADE"), primary_key=True
    )
    subject_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("subjects.id", ondelete="RESTRICT"), primary_key=True
    )

    course: Mapped["Course"] = relationship("Course", back_populates="course_subjects", lazy="noload")
    subject: Mapped["Subject"] = relationship("Subject", back_populates="course_subjects", lazy="noload")


# ─────────────────────────────────────────────────────────────────────────────
# Batch
# ─────────────────────────────────────────────────────────────────────────────

class DayOfWeek(str, enum.Enum):
    MONDAY = "MON"
    TUESDAY = "TUE"
    WEDNESDAY = "WED"
    THURSDAY = "THU"
    FRIDAY = "FRI"
    SATURDAY = "SAT"
    SUNDAY = "SUN"


class Batch(TenantAwareMixin, TimestampMixin, SoftDeleteMixin, Base):
    """
    A concrete section — the actual group of students that meets.

    One Course can have multiple Batches (e.g. morning + evening sections).
    A Batch is tied to one Subject and one Teacher (a teacher teaches one
    subject per batch — multi-subject teachers have multiple Batch rows).

    Naming convention: "10-CBSE-MATH-A" (from the spec examples).

    capacity — maximum students; enrollment service enforces this (BatchFullError).
    days     — stored as a PostgreSQL TEXT[] array of DayOfWeek enum values.
    """

    __tablename__ = "batches"
    __table_args__ = (
        UniqueConstraint("institute_id", "name", name="uq_batches_institute_name"),
        CheckConstraint("capacity > 0", name="ck_batches_capacity_positive"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    course_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("courses.id", ondelete="RESTRICT"),
        nullable=False, index=True
    )
    subject_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("subjects.id", ondelete="RESTRICT"),
        nullable=False, index=True
    )
    teacher_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("teacher_profiles.id", ondelete="SET NULL"),
        nullable=True, index=True,
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False)     # "10-CBSE-MATH-A"
    room: Mapped[str | None] = mapped_column(String(50), nullable=True)
    capacity: Mapped[int] = mapped_column(Integer, nullable=False, default=30)
    start_time: Mapped[str | None] = mapped_column(String(8), nullable=True)  # "17:00"
    end_time: Mapped[str | None] = mapped_column(String(8), nullable=True)    # "18:30"
    days: Mapped[list[str] | None] = mapped_column(ARRAY(String(3)), nullable=True)
    start_date: Mapped[Date | None] = mapped_column(SADate, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # Relationships
    course: Mapped["Course"] = relationship("Course", back_populates="batches", lazy="noload")
    subject: Mapped["Subject"] = relationship("Subject", back_populates="batches", lazy="noload")
    teacher: Mapped["TeacherProfile | None"] = relationship(  # type: ignore[name-defined]
        "TeacherProfile", foreign_keys=[teacher_id], lazy="noload"
    )

    def __repr__(self) -> str:
        return f"<Batch name={self.name!r} course={self.course_id}>"
