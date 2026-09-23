"""
app/schemas/people.py
---------------------
Pydantic v2 schemas for StudentProfile, TeacherProfile,
ParentProfile, StaffProfile, and StudentParent.

Rule: password is NEVER included in profile schemas.
      Profile schemas are domain-only — use auth schemas for credentials.
"""

from __future__ import annotations

import uuid
from datetime import date

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.models.people import BloodGroup, Gender


# ─── StudentProfile ──────────────────────────────────────────────────────────

class StudentProfileCreate(BaseModel):
    user_id: uuid.UUID
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    date_of_birth: date | None = None
    gender: Gender | None = None
    blood_group: BloodGroup | None = None
    admission_number: str | None = Field(None, max_length=50)
    current_class_id: uuid.UUID | None = None
    joining_date: date | None = None
    address_line1: str | None = None
    address_line2: str | None = None
    city: str | None = None
    state: str | None = None
    pincode: str | None = Field(None, max_length=10)
    emergency_contact_name: str | None = None
    emergency_contact_phone: str | None = Field(None, max_length=20)


class StudentProfileUpdate(BaseModel):
    first_name: str | None = Field(None, min_length=1, max_length=100)
    last_name: str | None = Field(None, min_length=1, max_length=100)
    date_of_birth: date | None = None
    gender: Gender | None = None
    blood_group: BloodGroup | None = None
    current_class_id: uuid.UUID | None = None
    address_line1: str | None = None
    address_line2: str | None = None
    city: str | None = None
    state: str | None = None
    pincode: str | None = Field(None, max_length=10)
    emergency_contact_name: str | None = None
    emergency_contact_phone: str | None = Field(None, max_length=20)
    is_active: bool | None = None


class StudentProfileRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    user_id: uuid.UUID
    institute_id: uuid.UUID | None
    first_name: str
    last_name: str
    full_name: str
    date_of_birth: date | None
    gender: Gender | None
    blood_group: BloodGroup | None
    photo_url: str | None
    admission_number: str | None
    current_class_id: uuid.UUID | None
    joining_date: date | None
    address_line1: str | None
    city: str | None
    state: str | None
    pincode: str | None
    emergency_contact_name: str | None
    emergency_contact_phone: str | None
    is_active: bool


# ─── TeacherProfile ──────────────────────────────────────────────────────────

class TeacherProfileCreate(BaseModel):
    user_id: uuid.UUID
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    date_of_birth: date | None = None
    gender: Gender | None = None
    employee_code: str | None = Field(None, max_length=50)
    qualification: str | None = Field(None, max_length=255)
    experience_years: int | None = Field(None, ge=0, le=60)
    joining_date: date | None = None
    personal_email: str | None = None
    personal_phone: str | None = Field(None, max_length=20)
    address: str | None = None


class TeacherProfileUpdate(BaseModel):
    first_name: str | None = Field(None, min_length=1, max_length=100)
    last_name: str | None = Field(None, min_length=1, max_length=100)
    qualification: str | None = None
    experience_years: int | None = Field(None, ge=0, le=60)
    personal_email: str | None = None


class TeacherOnboardRequest(BaseModel):
    """Creates the TEACHER login account and TeacherProfile atomically."""
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr
    password: str | None = Field(None, min_length=8, description="Leave null to auto-generate")
    employee_code: str | None = Field(None, max_length=50)
    qualification: str | None = Field(None, max_length=255)
    experience_years: int | None = Field(None, ge=0, le=60)
    personal_phone: str | None = Field(None, max_length=20)


class TeacherOnboardResponse(BaseModel):
    teacher_user_id: uuid.UUID
    teacher_profile_id: uuid.UUID
    email: str
    temp_password: str | None = None
    personal_phone: str | None = Field(None, max_length=20)
    address: str | None = None
    is_active: bool | None = None


class TeacherProfileRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    user_id: uuid.UUID
    institute_id: uuid.UUID | None
    first_name: str
    last_name: str
    full_name: str
    gender: Gender | None
    photo_url: str | None
    employee_code: str | None
    qualification: str | None
    experience_years: int | None
    joining_date: date | None
    personal_email: str | None
    personal_phone: str | None
    is_active: bool


# ─── ParentProfile ───────────────────────────────────────────────────────────

class ParentProfileCreate(BaseModel):
    user_id: uuid.UUID
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    relation: str = Field(default="PARENT", max_length=30)
    occupation: str | None = Field(None, max_length=150)
    annual_income: str | None = Field(None, max_length=50)
    address: str | None = None


class ParentProfileUpdate(BaseModel):
    first_name: str | None = Field(None, min_length=1, max_length=100)
    last_name: str | None = Field(None, min_length=1, max_length=100)
    relation: str | None = Field(None, max_length=30)
    occupation: str | None = None
    annual_income: str | None = None
    address: str | None = None
    is_active: bool | None = None


class ParentProfileRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    user_id: uuid.UUID
    institute_id: uuid.UUID | None
    first_name: str
    last_name: str
    full_name: str
    relation: str
    occupation: str | None
    photo_url: str | None
    is_active: bool


# ─── StaffProfile ─────────────────────────────────────────────────────────────

class StaffProfileCreate(BaseModel):
    user_id: uuid.UUID
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    designation: str | None = Field(None, max_length=100)
    department: str | None = Field(None, max_length=100)
    employee_code: str | None = Field(None, max_length=50)
    joining_date: date | None = None
    address: str | None = None


class StaffProfileUpdate(BaseModel):
    first_name: str | None = Field(None, min_length=1, max_length=100)
    last_name: str | None = Field(None, min_length=1, max_length=100)
    designation: str | None = None
    department: str | None = None
    address: str | None = None
    is_active: bool | None = None


class StaffProfileRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    user_id: uuid.UUID
    institute_id: uuid.UUID | None
    first_name: str
    last_name: str
    full_name: str
    designation: str | None
    department: str | None
    employee_code: str | None
    joining_date: date | None
    is_active: bool


# ─── StudentParent ────────────────────────────────────────────────────────────

class StudentParentLink(BaseModel):
    """Request to link a parent profile to a student."""
    parent_id: uuid.UUID
    is_primary: bool = False


class StudentParentRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    student_id: uuid.UUID
    parent_id: uuid.UUID
    is_primary: bool
