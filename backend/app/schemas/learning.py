"""
app/schemas/learning.py
-----------------------
Pydantic v2 schemas for Learning modules and File attachments:
  - FileAttachment
  - StudyMaterial
  - Homework
  - HomeworkSubmission & Evaluation
"""

from __future__ import annotations

import uuid
from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.learning import MaterialType, SubmissionStatus


# ─── File Attachment ─────────────────────────────────────────────────────────

class FileAttachmentRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    storage_key: str
    file_name: str
    file_size: int
    content_type: str
    uploaded_by: uuid.UUID | None
    created_at: datetime
    download_url: str | None = None


# ─── Study Material ──────────────────────────────────────────────────────────

class StudyMaterialCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    type: MaterialType = MaterialType.NOTES
    description: str | None = None
    target_course_id: uuid.UUID | None = None
    target_batch_id: uuid.UUID | None = None
    attachment_id: uuid.UUID | None = None
    is_published: bool = True


class StudyMaterialUpdate(BaseModel):
    title: str | None = Field(None, min_length=1, max_length=255)
    type: MaterialType | None = None
    description: str | None = None
    target_course_id: uuid.UUID | None = None
    target_batch_id: uuid.UUID | None = None
    attachment_id: uuid.UUID | None = None
    is_published: bool | None = None


class StudyMaterialRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    institute_id: uuid.UUID | None
    title: str
    type: MaterialType
    description: str | None
    target_course_id: uuid.UUID | None
    target_batch_id: uuid.UUID | None
    attachment_id: uuid.UUID | None
    uploaded_by: uuid.UUID | None
    is_published: bool
    created_at: datetime
    updated_at: datetime
    attachment: FileAttachmentRead | None = None


# ─── Homework ────────────────────────────────────────────────────────────────

class HomeworkCreate(BaseModel):
    batch_id: uuid.UUID
    subject_id: uuid.UUID
    title: str = Field(..., min_length=1, max_length=255)
    instructions: str | None = None
    chapter: str | None = Field(None, max_length=100)
    due_date: date
    attachment_id: uuid.UUID | None = None


class HomeworkUpdate(BaseModel):
    title: str | None = Field(None, min_length=1, max_length=255)
    instructions: str | None = None
    chapter: str | None = Field(None, max_length=100)
    due_date: date | None = None
    attachment_id: uuid.UUID | None = None


class HomeworkRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    batch_id: uuid.UUID
    subject_id: uuid.UUID
    title: str
    instructions: str | None
    chapter: str | None
    due_date: date
    attachment_id: uuid.UUID | None
    created_by: uuid.UUID | None
    created_at: datetime
    updated_at: datetime
    attachment: FileAttachmentRead | None = None


# ─── Homework Submission & Grading ───────────────────────────────────────────

class HomeworkSubmissionCreate(BaseModel):
    attachment_id: uuid.UUID | None = None
    submission_text: str | None = None


class HomeworkEvaluationRequest(BaseModel):
    marks: float = Field(..., ge=0)
    max_marks: float | None = Field(None, gt=0)
    teacher_comment: str | None = None
    status: SubmissionStatus = SubmissionStatus.REVIEWED


class HomeworkSubmissionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    homework_id: uuid.UUID
    student_id: uuid.UUID
    attachment_id: uuid.UUID | None
    submission_text: str | None
    status: SubmissionStatus
    marks: float | None
    max_marks: float | None
    teacher_comment: str | None
    submitted_at: datetime
    reviewed_at: datetime | None
    reviewed_by: uuid.UUID | None
    attachment: FileAttachmentRead | None = None
