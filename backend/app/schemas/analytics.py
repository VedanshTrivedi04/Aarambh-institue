"""
app/schemas/analytics.py
------------------------
Pydantic v2 schemas for Executive Dashboards, Batch Analytics,
Attendance Alerts, Financial Aggregates, and the comprehensive Student 360° Profile.
"""

from __future__ import annotations

import enum
import uuid
from datetime import date as Date, datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class ExportFormat(str, enum.Enum):
    CSV = "csv"
    JSON = "json"


class ExportType(str, enum.Enum):
    STUDENTS_ROSTER = "students_roster"
    FEE_LEDGER = "fee_ledger"
    ATTENDANCE_REGISTER = "attendance_register"
    EXAM_RESULTS = "exam_results"


# ─── Executive Dashboard ───────────────────────────────────────────────────────

class DashboardKPIsResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    total_students: int = 0
    total_batches: int = 0
    total_teachers: int = 0
    total_enquiries_open: int = 0

    total_fees_billed: float = 0.0
    total_fees_collected: float = 0.0
    total_fees_pending: float = 0.0

    overall_attendance_rate: float = 0.0
    attendance_trends_7d: list[dict[str, Any]] = Field(default_factory=list)
    monthly_collections_6m: list[dict[str, Any]] = Field(default_factory=list)


# ─── Batch Analytics ──────────────────────────────────────────────────────────

class BatchAnalyticsResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    batch_id: uuid.UUID
    batch_name: str
    total_enrolled: int = 0
    capacity: int | None = None
    total_sessions_conducted: int = 0
    average_attendance_rate: float = 0.0
    low_attendance_students_count: int = 0

    tests_conducted: int = 0
    average_test_score: float = 0.0
    top_test_score: float | None = None
    pass_rate: float | None = None

    homework_assigned_count: int = 0
    homework_submission_rate: float = 0.0


# ─── Financial Analytics ──────────────────────────────────────────────────────

class FinancialAnalyticsResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    total_billed: float = 0.0
    total_collected: float = 0.0
    total_overdue: float = 0.0
    collection_rate_percentage: float = 0.0
    method_breakdown: dict[str, float] = Field(default_factory=dict)
    monthly_timeline: list[dict[str, Any]] = Field(default_factory=list)


# ─── Attendance Analytics & Alerts ─────────────────────────────────────────────

class LowAttendanceAlert(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    student_id: uuid.UUID
    student_name: str
    admission_number: str | None = None
    batch_id: uuid.UUID
    batch_name: str
    total_classes: int = 0
    attended_classes: int = 0
    attendance_percentage: float = 0.0


class AttendanceAnalyticsResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    total_records: int = 0
    present_count: int = 0
    absent_count: int = 0
    late_count: int = 0
    excused_count: int = 0
    attendance_rate_percentage: float = 0.0
    low_attendance_students: list[LowAttendanceAlert] = Field(default_factory=list)


# ─── Student 360° Comprehensive Profile ───────────────────────────────────────

class Student360ProfileResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    # Core demographics & enrollment
    student_id: uuid.UUID
    user_id: uuid.UUID
    first_name: str
    last_name: str
    full_name: str
    admission_number: str | None = None
    date_of_birth: Date | None = None
    gender: str | None = None
    photo_url: str | None = None
    joining_date: Date | None = None
    current_class_name: str | None = None
    guardians: list[dict[str, Any]] = Field(default_factory=list)

    # Active academic batches
    batches: list[dict[str, Any]] = Field(default_factory=list)

    # Attendance profile
    total_sessions: int = 0
    attended_sessions: int = 0
    attendance_percentage: float = 0.0
    attendance_badge: str = "GOOD"  # EXCELLENT, GOOD, WARNING, CRITICAL

    # Examination performance
    tests_taken: int = 0
    average_test_percentage: float = 0.0
    scorecards: list[dict[str, Any]] = Field(default_factory=list)

    # Financial ledger status
    fee_plan_total: float = 0.0
    total_paid: float = 0.0
    pending_balance: float = 0.0
    installments: list[dict[str, Any]] = Field(default_factory=list)
    receipts: list[dict[str, Any]] = Field(default_factory=list)

    # Homework & assignments
    total_homework_assigned: int = 0
    total_submitted: int = 0
    homework_completion_rate: float = 0.0
    average_homework_marks: float | None = None

    # Teacher observations
    remarks: list[dict[str, Any]] = Field(default_factory=list)


# ─── View Refresh ─────────────────────────────────────────────────────────────

class MaterializedViewRefreshResponse(BaseModel):
    refreshed_at: datetime
    views_refreshed: list[str]
    message: str = "Materialized views refreshed successfully."
