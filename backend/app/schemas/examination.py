"""
app/schemas/examination.py
--------------------------
Pydantic v2 schemas for Examinations, Question Bank, Tests & Results:
  - Question bank CRUD & query
  - Test creation, assembly & detail
  - Bulk marks entry & validation
  - Student scorecard, rankings, and test analytics
"""

from __future__ import annotations

import uuid
from datetime import date as Date, datetime, time as Time
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from app.models.examination import (
    QuestionDifficulty,
    QuestionType,
    TestStatus,
    TestType,
)


# ─── Question Schemas ────────────────────────────────────────────────────────

class QuestionCreate(BaseModel):
    subject_id: uuid.UUID
    board_id: uuid.UUID | None = None
    class_id: uuid.UUID | None = None
    stream_id: uuid.UUID | None = None
    chapter: str | None = Field(None, max_length=255)
    topic: str | None = Field(None, max_length=255)
    difficulty: QuestionDifficulty = QuestionDifficulty.MEDIUM
    question_type: QuestionType = QuestionType.SUBJECTIVE
    body: str = Field(..., min_length=1)
    options: list[dict[str, Any]] | None = None
    correct_answer: str | None = None
    explanation: str | None = None
    default_marks: float = Field(1.0, gt=0)


class QuestionUpdate(BaseModel):
    subject_id: uuid.UUID | None = None
    board_id: uuid.UUID | None = None
    class_id: uuid.UUID | None = None
    stream_id: uuid.UUID | None = None
    chapter: str | None = Field(None, max_length=255)
    topic: str | None = Field(None, max_length=255)
    difficulty: QuestionDifficulty | None = None
    question_type: QuestionType | None = None
    body: str | None = Field(None, min_length=1)
    options: list[dict[str, Any]] | None = None
    correct_answer: str | None = None
    explanation: str | None = None
    default_marks: float | None = Field(None, gt=0)


class QuestionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    institute_id: uuid.UUID
    branch_id: uuid.UUID | None
    board_id: uuid.UUID | None
    class_id: uuid.UUID | None
    stream_id: uuid.UUID | None
    subject_id: uuid.UUID
    chapter: str | None
    topic: str | None
    difficulty: QuestionDifficulty
    question_type: QuestionType
    body: str
    options: list[dict[str, Any]] | None
    correct_answer: str | None
    explanation: str | None
    default_marks: float
    created_by: uuid.UUID
    created_at: datetime
    updated_at: datetime

    subject_name: str | None = None
    class_name: str | None = None
    board_name: str | None = None


# ─── Test Question Mapping ───────────────────────────────────────────────────

class TestQuestionAssign(BaseModel):
    question_id: uuid.UUID
    marks: float = Field(..., gt=0)
    display_order: int = Field(1, ge=1)
    section: str | None = Field(None, max_length=50)


class TestQuestionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    test_id: uuid.UUID
    question_id: uuid.UUID
    marks: float
    display_order: int
    section: str | None
    question: QuestionRead | None = None


# ─── Test Schemas ────────────────────────────────────────────────────────────

class TestCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    type: TestType = TestType.CLASS
    date: Date
    start_time: Time | None = None
    duration_minutes: int | None = Field(None, gt=0)
    max_marks: float = Field(..., gt=0)
    passing_marks: float | None = Field(None, ge=0)
    status: TestStatus = TestStatus.DRAFT
    instructions: str | None = None

    course_id: uuid.UUID | None = None
    batch_id: uuid.UUID | None = None
    subject_id: uuid.UUID | None = None

    questions: list[TestQuestionAssign] = []


class TestUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=255)
    type: TestType | None = None
    date: Date | None = None
    start_time: Time | None = None
    duration_minutes: int | None = Field(None, gt=0)
    max_marks: float | None = Field(None, gt=0)
    passing_marks: float | None = Field(None, ge=0)
    status: TestStatus | None = None
    instructions: str | None = None
    course_id: uuid.UUID | None = None
    batch_id: uuid.UUID | None = None
    subject_id: uuid.UUID | None = None


class TestRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    institute_id: uuid.UUID
    branch_id: uuid.UUID | None
    course_id: uuid.UUID | None
    batch_id: uuid.UUID | None
    subject_id: uuid.UUID | None
    name: str
    type: TestType
    date: Date
    start_time: Time | None
    duration_minutes: int | None
    max_marks: float
    passing_marks: float | None
    status: TestStatus
    instructions: str | None
    created_by: uuid.UUID
    published_at: datetime | None
    published_by: uuid.UUID | None
    created_at: datetime
    updated_at: datetime

    course_name: str | None = None
    batch_name: str | None = None
    subject_name: str | None = None
    question_count: int = 0
    evaluated_count: int = 0


class TestDetailRead(TestRead):
    test_questions: list[TestQuestionRead] = []


# ─── Marks Entry & Result Schemas ────────────────────────────────────────────

class StudentMarksEntry(BaseModel):
    student_id: uuid.UUID
    marks_obtained: float | None = Field(None, ge=0)
    is_absent: bool = False
    remarks: str | None = None


class BulkMarksEntryRequest(BaseModel):
    entries: list[StudentMarksEntry] = Field(..., min_length=1)


class TestResultRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    test_id: uuid.UUID
    student_id: uuid.UUID
    marks_obtained: float | None
    is_absent: bool
    percentage: float | None
    percentile: float | None
    rank: int | None
    remarks: str | None
    evaluated_by: uuid.UUID | None
    created_at: datetime
    updated_at: datetime

    student_name: str | None = None
    admission_number: str | None = None
    roll_number: str | None = None


class TestScorecard(BaseModel):
    """Student view of their test result."""
    test: TestRead
    result: TestResultRead
    max_marks: float
    passing_marks: float | None
    is_passed: bool | None
    class_highest_marks: float | None
    class_average_marks: float | None


class TestAnalytics(BaseModel):
    """Aggregate performance report for a test."""
    test_id: uuid.UUID
    test_name: str
    max_marks: float
    total_candidates: int
    present_count: int
    absent_count: int
    highest_marks: float | None
    average_marks: float | None
    lowest_marks: float | None
    pass_percentage: float | None
    leaderboard: list[TestResultRead] = []
