"""
app/models/academic_operations.py
---------------------------------
Academic operations: Timetables, Class Sessions, Session Logs,
Student Attendance tracking, and Teacher Remarks.

Key rules (rules.md §5, §6, backend.md §3):
  - Timetable defines weekly recurring slots.
  - ClassSession represents the concrete calendar class session.
  - Attendance is linked to (class_session_id, enrollment_id) with unique constraint.
  - SessionLog records syllabus progress and homework for a session.
  - StudentRemark records teacher feedback on individual students.
"""

from __future__ import annotations

import enum
import uuid
from datetime import date as Date, datetime

from sqlalchemy import (
    Boolean,
    Date as SADate,
    DateTime,
    Enum,
    ForeignKey,
    Index,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, SoftDeleteMixin, TenantAwareMixin, TimestampMixin
from app.models.academic_structure import DayOfWeek


class ClassSessionStatus(str, enum.Enum):
    SCHEDULED = "SCHEDULED"
    HELD = "HELD"
    CANCELLED = "CANCELLED"
    RESCHEDULED = "RESCHEDULED"


class AttendanceStatus(str, enum.Enum):
    PRESENT = "PRESENT"
    ABSENT = "ABSENT"
    LATE = "LATE"
    EXCUSED = "EXCUSED"


# ─────────────────────────────────────────────────────────────────────────────
# Timetable
# ─────────────────────────────────────────────────────────────────────────────

class Timetable(TenantAwareMixin, TimestampMixin, SoftDeleteMixin, Base):
    """
    Weekly schedule rule for a batch.
    e.g., Batch "10-CBSE-MATH-A" on MON at 17:00-18:30 in Room 101.
    Used by the session generator to populate concrete ClassSessions.
    """

    __tablename__ = "timetables"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    batch_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("batches.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    day_of_week: Mapped[DayOfWeek] = mapped_column(
        Enum(DayOfWeek, name="day_of_week_enum", create_type=False),
        nullable=False,
    )
    start_time: Mapped[str] = mapped_column(String(8), nullable=False)  # "17:00"
    end_time: Mapped[str] = mapped_column(String(8), nullable=False)    # "18:30"
    room: Mapped[str | None] = mapped_column(String(50), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    batch: Mapped["Batch"] = relationship(  # type: ignore[name-defined]
        "Batch", lazy="noload"
    )

    def __repr__(self) -> str:
        return f"<Timetable batch={self.batch_id} day={self.day_of_week} {self.start_time}-{self.end_time}>"


# ─────────────────────────────────────────────────────────────────────────────
# ClassSession
# ─────────────────────────────────────────────────────────────────────────────

class ClassSession(TenantAwareMixin, TimestampMixin, SoftDeleteMixin, Base):
    """
    A concrete calendar class session on a specific date.

    Status transitions:
      SCHEDULED → HELD
      SCHEDULED → CANCELLED
      SCHEDULED → RESCHEDULED (points to new ClassSession via rescheduled_to_session_id)
    """

    __tablename__ = "class_sessions"
    __table_args__ = (
        Index("ix_class_sessions_batch_date", "batch_id", "date"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    batch_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("batches.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    date: Mapped[Date] = mapped_column(SADate, nullable=False, index=True)
    start_time: Mapped[str] = mapped_column(String(8), nullable=False)
    end_time: Mapped[str] = mapped_column(String(8), nullable=False)
    room: Mapped[str | None] = mapped_column(String(50), nullable=True)

    status: Mapped[ClassSessionStatus] = mapped_column(
        Enum(ClassSessionStatus, name="class_session_status_enum"),
        default=ClassSessionStatus.SCHEDULED,
        nullable=False,
        index=True,
    )
    rescheduled_to_session_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("class_sessions.id", ondelete="SET NULL"),
        nullable=True,
    )
    conducted_by: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("teacher_profiles.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    remarks: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Relationships
    batch: Mapped["Batch"] = relationship("Batch", lazy="noload")  # type: ignore[name-defined]
    conducted_by_teacher: Mapped["TeacherProfile"] = relationship(  # type: ignore[name-defined]
        "TeacherProfile", foreign_keys=[conducted_by], lazy="noload"
    )
    session_log: Mapped["SessionLog | None"] = relationship(
        "SessionLog", back_populates="class_session", uselist=False, lazy="noload"
    )
    attendances: Mapped[list["Attendance"]] = relationship(
        "Attendance", back_populates="class_session", lazy="noload"
    )

    def __repr__(self) -> str:
        return f"<ClassSession batch={self.batch_id} date={self.date} status={self.status}>"


# ─────────────────────────────────────────────────────────────────────────────
# SessionLog
# ─────────────────────────────────────────────────────────────────────────────

class SessionLog(TimestampMixin, Base):
    """
    Academic delivery log for a class session.
    Records syllabus progress, topics taught, and homework given.
    """

    __tablename__ = "session_logs"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    class_session_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("class_sessions.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
    )
    topic: Mapped[str] = mapped_column(String(255), nullable=False)
    topics_covered: Mapped[str | None] = mapped_column(Text, nullable=True)
    homework_notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    class_remarks: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_by: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )

    class_session: Mapped["ClassSession"] = relationship(
        "ClassSession", back_populates="session_log", lazy="noload"
    )

    def __repr__(self) -> str:
        return f"<SessionLog session={self.class_session_id} topic={self.topic!r}>"


# ─────────────────────────────────────────────────────────────────────────────
# Attendance
# ─────────────────────────────────────────────────────────────────────────────

class Attendance(Base):
    """
    Student attendance record for a concrete class session.
    Unique constraint on (class_session_id, enrollment_id) enforces one record per student-session.
    """

    __tablename__ = "attendance"
    __table_args__ = (
        UniqueConstraint(
            "class_session_id", "enrollment_id", name="uq_attendance_session_enrollment"
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    class_session_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("class_sessions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    enrollment_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("enrollments.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    status: Mapped[AttendanceStatus] = mapped_column(
        Enum(AttendanceStatus, name="attendance_status_enum"),
        default=AttendanceStatus.PRESENT,
        nullable=False,
        index=True,
    )
    remarks: Mapped[str | None] = mapped_column(String(255), nullable=True)
    marked_by: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    marked_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    # Relationships
    class_session: Mapped["ClassSession"] = relationship(
        "ClassSession", back_populates="attendances", lazy="noload"
    )
    enrollment: Mapped["Enrollment"] = relationship(  # type: ignore[name-defined]
        "Enrollment", lazy="noload"
    )

    def __repr__(self) -> str:
        return f"<Attendance session={self.class_session_id} enrollment={self.enrollment_id} status={self.status}>"


# ─────────────────────────────────────────────────────────────────────────────
# StudentRemark
# ─────────────────────────────────────────────────────────────────────────────

class StudentRemark(TenantAwareMixin, Base):
    """
    Direct teacher observation/remark regarding a student.
    Can optionally be linked to a specific class session.
    `visible_to_parent=True` allows the mobile parent portal to display this note.
    """

    __tablename__ = "student_remarks"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    student_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("student_profiles.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    teacher_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("teacher_profiles.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    class_session_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("class_sessions.id", ondelete="SET NULL"),
        nullable=True,
    )
    body: Mapped[str] = mapped_column(Text, nullable=False)
    visible_to_parent: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False, index=True
    )

    # Relationships
    student: Mapped["StudentProfile"] = relationship(  # type: ignore[name-defined]
        "StudentProfile", lazy="noload"
    )
    teacher: Mapped["TeacherProfile"] = relationship(  # type: ignore[name-defined]
        "TeacherProfile", lazy="noload"
    )

    def __repr__(self) -> str:
        return f"<StudentRemark student={self.student_id} teacher={self.teacher_id}>"
