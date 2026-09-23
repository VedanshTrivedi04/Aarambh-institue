"""
app/schemas/academic_structure.py
----------------------------------
Pydantic v2 schemas for all academic-structure entities.

Separate Create / Update / Read triples for each entity
following the REST resource lifecycle pattern.
"""

from __future__ import annotations

import uuid
from datetime import date
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, model_validator


# ─────────────────────────────────────────────────────────────────────────────
# AcademicYear
# ─────────────────────────────────────────────────────────────────────────────

class AcademicYearCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=20, examples=["2025-26"])
    start_date: date
    end_date: date
    is_current: bool = False

    @model_validator(mode="after")
    def start_before_end(self) -> "AcademicYearCreate":
        if self.start_date >= self.end_date:
            raise ValueError("start_date must be before end_date")
        return self


class AcademicYearUpdate(BaseModel):
    name: str | None = Field(None, min_length=2, max_length=20)
    start_date: date | None = None
    end_date: date | None = None
    is_current: bool | None = None


class AcademicYearRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    institute_id: uuid.UUID | None
    name: str
    start_date: date
    end_date: date
    is_current: bool


# ─────────────────────────────────────────────────────────────────────────────
# Board
# ─────────────────────────────────────────────────────────────────────────────

class BoardCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    code: str = Field(..., min_length=1, max_length=20, pattern=r"^[A-Z0-9_]+$")


class BoardUpdate(BaseModel):
    name: str | None = Field(None, min_length=2, max_length=100)
    is_active: bool | None = None


class BoardRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    institute_id: uuid.UUID | None
    name: str
    code: str
    is_active: bool


# ─────────────────────────────────────────────────────────────────────────────
# SchoolClass
# ─────────────────────────────────────────────────────────────────────────────

class ClassCreate(BaseModel):
    board_id: uuid.UUID
    name: str = Field(..., min_length=1, max_length=20, examples=["Class 10", "Class 12"])
    display_order: int = Field(default=0, ge=0)


class ClassUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=20)
    display_order: int | None = Field(None, ge=0)
    is_active: bool | None = None


class ClassRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    institute_id: uuid.UUID | None
    board_id: uuid.UUID
    name: str
    display_order: int
    is_active: bool


# ─────────────────────────────────────────────────────────────────────────────
# Stream
# ─────────────────────────────────────────────────────────────────────────────

class StreamCreate(BaseModel):
    class_id: uuid.UUID
    name: str = Field(..., min_length=1, max_length=50, examples=["PCM", "Commerce", "Arts"])


class StreamUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=50)
    is_active: bool | None = None


class StreamRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    institute_id: uuid.UUID | None
    class_id: uuid.UUID
    name: str
    is_active: bool


# ─────────────────────────────────────────────────────────────────────────────
# Subject
# ─────────────────────────────────────────────────────────────────────────────

class SubjectCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    code: str = Field(..., min_length=1, max_length=20, pattern=r"^[A-Z0-9_]+$")
    description: str | None = None


class SubjectUpdate(BaseModel):
    name: str | None = Field(None, min_length=2, max_length=100)
    description: str | None = None
    is_active: bool | None = None


class SubjectRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    institute_id: uuid.UUID | None
    name: str
    code: str
    description: str | None
    is_active: bool


# ─────────────────────────────────────────────────────────────────────────────
# Course
# ─────────────────────────────────────────────────────────────────────────────

class CourseCreate(BaseModel):
    academic_year_id: uuid.UUID
    class_id: uuid.UUID
    stream_id: uuid.UUID | None = None
    name: str = Field(..., min_length=2, max_length=255)
    code: str = Field(..., min_length=1, max_length=50, pattern=r"^[A-Z0-9_\-]+$")
    duration_months: int = Field(default=12, ge=1, le=60)
    description: str | None = None
    subject_ids: list[uuid.UUID] = Field(default_factory=list)


class CourseUpdate(BaseModel):
    name: str | None = Field(None, min_length=2, max_length=255)
    description: str | None = None
    duration_months: int | None = Field(None, ge=1, le=60)
    is_active: bool | None = None
    subject_ids: list[uuid.UUID] | None = None  # Full replace of course subjects


class CourseRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    institute_id: uuid.UUID | None
    academic_year_id: uuid.UUID
    class_id: uuid.UUID
    stream_id: uuid.UUID | None
    name: str
    code: str
    duration_months: int
    description: str | None
    is_active: bool


class CourseReadFull(CourseRead):
    """Includes the list of subjects for detail view."""
    subjects: list[SubjectRead] = Field(default_factory=list)


# ─────────────────────────────────────────────────────────────────────────────
# Batch
# ─────────────────────────────────────────────────────────────────────────────

_VALID_DAYS = {"MON", "TUE", "WED", "THU", "FRI", "SAT", "SUN"}


class BatchCreate(BaseModel):
    course_id: uuid.UUID
    subject_id: uuid.UUID
    teacher_id: uuid.UUID | None = None
    name: str = Field(..., min_length=2, max_length=100, examples=["10-CBSE-MATH-A"])
    room: str | None = Field(None, max_length=50)
    capacity: int = Field(default=30, ge=1, le=500)
    start_time: str | None = Field(None, pattern=r"^\d{2}:\d{2}$", examples=["17:00"])
    end_time: str | None = Field(None, pattern=r"^\d{2}:\d{2}$", examples=["18:30"])
    days: list[str] | None = Field(None, examples=[["MON", "WED", "FRI"]])
    start_date: date | None = None

    @model_validator(mode="after")
    def validate_days(self) -> "BatchCreate":
        if self.days:
            invalid = set(self.days) - _VALID_DAYS
            if invalid:
                raise ValueError(f"Invalid day codes: {invalid}. Use MON-SUN.")
        return self


class BatchUpdate(BaseModel):
    teacher_id: uuid.UUID | None = None
    room: str | None = Field(None, max_length=50)
    capacity: int | None = Field(None, ge=1, le=500)
    start_time: str | None = Field(None, pattern=r"^\d{2}:\d{2}$")
    end_time: str | None = Field(None, pattern=r"^\d{2}:\d{2}$")
    days: list[str] | None = None
    start_date: date | None = None
    is_active: bool | None = None


class BatchRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    institute_id: uuid.UUID | None
    course_id: uuid.UUID
    subject_id: uuid.UUID
    teacher_id: uuid.UUID | None
    name: str
    room: str | None
    capacity: int
    start_time: str | None
    end_time: str | None
    days: list[str] | None
    start_date: date | None
    is_active: bool
