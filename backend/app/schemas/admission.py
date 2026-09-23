"""
app/schemas/admission.py
------------------------
Pydantic schemas for the Atomic Admission Wizard.

Enables full onboarding in one transactional request:
  - Student User + StudentProfile
  - Parent User + ParentProfile
  - StudentParent link
  - Initial Batch Enrollment
  - Optional Enquiry state conversion
"""

from __future__ import annotations

import uuid
from datetime import date

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.models.people import BloodGroup, Gender


class StudentAdmissionPayload(BaseModel):
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr
    password: str | None = Field(None, min_length=8, description="Leave null to auto-generate")
    phone: str | None = Field(None, max_length=20)
    date_of_birth: date | None = None
    gender: Gender | None = None
    blood_group: BloodGroup | None = None
    admission_number: str | None = Field(None, max_length=50, description="Leave null to auto-generate")
    class_id: uuid.UUID | None = None
    address_line1: str | None = None
    city: str | None = None
    state: str | None = None
    pincode: str | None = None


class ParentAdmissionPayload(BaseModel):
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr
    password: str | None = Field(None, min_length=8, description="Leave null to auto-generate")
    phone: str = Field(..., min_length=5, max_length=20)
    relation: str = Field(default="PARENT", max_length=30)
    occupation: str | None = None
    annual_income: str | None = None
    is_primary: bool = True


class BatchAdmissionPayload(BaseModel):
    batch_id: uuid.UUID
    enrollment_date: date | None = None
    remarks: str | None = None


class AdmissionWizardRequest(BaseModel):
    """Complete admission wizard request payload."""
    enquiry_id: uuid.UUID | None = None
    student: StudentAdmissionPayload
    parent: ParentAdmissionPayload
    enrollment: BatchAdmissionPayload


class AdmissionWizardResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    student_user_id: uuid.UUID
    student_profile_id: uuid.UUID
    admission_number: str
    student_email: str
    student_temp_password: str | None = None

    parent_user_id: uuid.UUID
    parent_profile_id: uuid.UUID
    parent_email: str
    parent_temp_password: str | None = None

    enrollment_id: uuid.UUID
    batch_id: uuid.UUID
    enquiry_id: uuid.UUID | None = None
    message: str = "Admission successfully processed"
