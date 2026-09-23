"""
app/schemas/enquiry.py
----------------------
Pydantic v2 schemas for Enquiry and EnquiryFollowUp.
"""

from __future__ import annotations

import uuid
from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.models.enquiry import EnquirySource, EnquiryStage


class EnquiryCreate(BaseModel):
    student_name: str = Field(..., min_length=1, max_length=150)
    student_email: EmailStr | None = None
    student_phone: str | None = Field(None, max_length=20)
    parent_name: str = Field(..., min_length=1, max_length=150)
    parent_email: EmailStr | None = None
    parent_phone: str = Field(..., min_length=5, max_length=20)
    board_id: uuid.UUID | None = None
    class_id: uuid.UUID | None = None
    interested_course_id: uuid.UUID | None = None
    source: EnquirySource = EnquirySource.WALK_IN
    counsellor_id: uuid.UUID | None = None
    follow_up_date: date | None = None
    remarks: str | None = None


class EnquiryUpdate(BaseModel):
    student_name: str | None = Field(None, min_length=1, max_length=150)
    student_email: EmailStr | None = None
    student_phone: str | None = Field(None, max_length=20)
    parent_name: str | None = Field(None, min_length=1, max_length=150)
    parent_email: EmailStr | None = None
    parent_phone: str | None = Field(None, min_length=5, max_length=20)
    board_id: uuid.UUID | None = None
    class_id: uuid.UUID | None = None
    interested_course_id: uuid.UUID | None = None
    source: EnquirySource | None = None
    counsellor_id: uuid.UUID | None = None
    follow_up_date: date | None = None
    remarks: str | None = None


class EnquiryFollowUpCreate(BaseModel):
    notes: str = Field(..., min_length=1, max_length=2000)
    new_stage: EnquiryStage | None = None
    next_follow_up_date: date | None = None


class EnquiryFollowUpRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    enquiry_id: uuid.UUID
    author_id: uuid.UUID | None
    stage_before: EnquiryStage | None
    stage_after: EnquiryStage
    notes: str
    next_follow_up_date: date | None
    created_at: datetime


class EnquiryRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    institute_id: uuid.UUID | None
    student_name: str
    student_email: str | None
    student_phone: str | None
    parent_name: str
    parent_email: str | None
    parent_phone: str
    board_id: uuid.UUID | None
    class_id: uuid.UUID | None
    interested_course_id: uuid.UUID | None
    source: EnquirySource
    stage: EnquiryStage
    counsellor_id: uuid.UUID | None
    follow_up_date: date | None
    remarks: str | None
    converted_student_id: uuid.UUID | None
    converted_at: datetime | None
    created_at: datetime
    updated_at: datetime
