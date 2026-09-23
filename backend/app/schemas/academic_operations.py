"""
app/schemas/academic_operations.py
----------------------------------
Pydantic v2 schemas for Academic Operations:
  - Timetables
  - Class Sessions
  - Session Logs
  - Attendance (bulk marking, attendance sheets, and student attendance stats)
  - Student Remarks
"""

from __future__ import annotations

import uuid
from datetime import date as Date, datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.academic_operations import AttendanceStatus, ClassSessionStatus
from app.models.academic_structure import DayOfWeek


# ─── Timetable Schemas ────────────────────────────────────────────────────────

class TimetableCreate(BaseModel):
    batch_id: uuid.UUID
    day_of_week: DayOfWeek
    start_time: str = Field(..., pattern=r"^\d{2}:\d{2}$", description="e.g. 17:00")
    end_time: str = Field(..., pattern=r"^\d{2}:\d{2}$", description="e.g. 18:30")
    room: str | None = Field(None, max_length=50)


class TimetableUpdate(BaseModel):
    day_of_week: DayOfWeek | None = None
    start_time: str | None = Field(None, pattern=r"^\d{2}:\d{2}$")
    end_time: str | None = Field(None, pattern=r"^\d{2}:\d{2}$")
    room: str | None = Field(None, max_length=50)
    is_active: bool | None = None


class TimetableRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    batch_id: uuid.UUID
    institute_id: uuid.UUID | None
    day_of_week: DayOfWeek
    start_time: str
    end_time: str
    room: str | None
    is_active: bool
    created_at: datetime
    updated_at: datetime


# ─── ClassSession Schemas ─────────────────────────────────────────────────────

class ClassSessionCreate(BaseModel):
    batch_id: uuid.UUID
    date: Date
    start_time: str = Field(..., pattern=r"^\d{2}:\d{2}$")
    end_time: str = Field(..., pattern=r"^\d{2}:\d{2}$")
    room: str | None = Field(None, max_length=50)
    conducted_by: uuid.UUID | None = None
    remarks: str | None = None


class ClassSessionUpdate(BaseModel):
    date: Date | None = None
    start_time: str | None = Field(None, pattern=r"^\d{2}:\d{2}$")
    end_time: str | None = Field(None, pattern=r"^\d{2}:\d{2}$")
    room: str | None = Field(None, max_length=50)
    conducted_by: uuid.UUID | None = None
    status: ClassSessionStatus | None = None
    remarks: str | None = None


class SessionRescheduleRequest(BaseModel):
    new_date: Date
    new_start_time: str = Field(..., pattern=r"^\d{2}:\d{2}$")
    new_end_time: str = Field(..., pattern=r"^\d{2}:\d{2}$")
    new_room: str | None = Field(None, max_length=50)
    reason: str = Field(..., min_length=3, max_length=500)


class SessionGenerateRequest(BaseModel):
    batch_id: uuid.UUID
    start_date: Date
    end_date: Date


class ClassSessionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    batch_id: uuid.UUID
    institute_id: uuid.UUID | None
    date: Date

    start_time: str
    end_time: str
    room: str | None
    status: ClassSessionStatus
    rescheduled_to_session_id: uuid.UUID | None
    conducted_by: uuid.UUID | None
    remarks: str | None
    created_at: datetime
    updated_at: datetime


# ─── SessionLog Schemas ───────────────────────────────────────────────────────

class SessionLogCreate(BaseModel):
    topic: str = Field(..., min_length=1, max_length=255)
    topics_covered: str | None = None
    homework_notes: str | None = None
    class_remarks: str | None = None


class SessionLogRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    class_session_id: uuid.UUID
    topic: str
    topics_covered: str | None
    homework_notes: str | None
    class_remarks: str | None
    created_by: uuid.UUID | None
    created_at: datetime
    updated_at: datetime


# ─── Attendance Schemas ───────────────────────────────────────────────────────

class AttendanceRecordInput(BaseModel):
    enrollment_id: uuid.UUID
    status: AttendanceStatus = AttendanceStatus.PRESENT
    remarks: str | None = Field(None, max_length=255)


class AttendanceBulkMarkRequest(BaseModel):
    records: list[AttendanceRecordInput]


class AttendanceRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    class_session_id: uuid.UUID
    enrollment_id: uuid.UUID
    status: AttendanceStatus
    remarks: str | None
    marked_by: uuid.UUID | None
    marked_at: datetime


class SessionAttendanceSheetItem(BaseModel):
    enrollment_id: uuid.UUID
    student_id: uuid.UUID
    student_name: str
    admission_number: str | None
    status: AttendanceStatus | None
    remarks: str | None


class StudentAttendanceSummary(BaseModel):
    student_id: uuid.UUID
    batch_id: uuid.UUID | None = None
    total_sessions: int
    present_count: int
    absent_count: int
    late_count: int
    excused_count: int
    attendance_percentage: float


# ─── StudentRemark Schemas ───────────────────────────────────────────────────

class StudentRemarkCreate(BaseModel):
    student_id: uuid.UUID
    body: str = Field(..., min_length=1, max_length=2000)
    class_session_id: uuid.UUID | None = None
    visible_to_parent: bool = True


class StudentRemarkRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    student_id: uuid.UUID
    teacher_id: uuid.UUID
    class_session_id: uuid.UUID | None
    body: str
    visible_to_parent: bool
    created_at: datetime
