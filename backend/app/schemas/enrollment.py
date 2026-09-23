"""
app/schemas/enrollment.py
-------------------------
Pydantic v2 schemas for Enrollment and BatchTransferHistory.
"""

from __future__ import annotations

import uuid
from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.enrollment import EnrollmentStatus


class EnrollmentCreate(BaseModel):
    """Payload to enroll a student into a batch."""
    student_id: uuid.UUID
    batch_id: uuid.UUID
    enrollment_date: date | None = None
    remarks: str | None = Field(None, max_length=500)


class EnrollmentStatusUpdate(BaseModel):
    """Payload to update an enrollment's status (COMPLETED, DROPPED, CANCELLED)."""
    status: EnrollmentStatus
    end_date: date | None = None
    remarks: str | None = Field(None, max_length=500)


class BatchTransferRequest(BaseModel):
    """Payload to transfer an enrolled student to another batch."""
    to_batch_id: uuid.UUID
    reason: str = Field(..., min_length=3, max_length=500, description="Reason for transfer")


class EnrollmentRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    student_id: uuid.UUID
    batch_id: uuid.UUID
    institute_id: uuid.UUID | None
    status: EnrollmentStatus
    enrollment_date: date
    end_date: date | None
    enrolled_by: uuid.UUID | None
    remarks: str | None
    created_at: datetime
    updated_at: datetime


class BatchTransferHistoryRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    enrollment_id: uuid.UUID
    student_id: uuid.UUID
    from_batch_id: uuid.UUID
    to_batch_id: uuid.UUID
    reason: str
    transferred_by: uuid.UUID | None
    institute_id: uuid.UUID | None
    created_at: datetime
