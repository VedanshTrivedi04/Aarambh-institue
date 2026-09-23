"""
app/schemas/institute.py
------------------------
Pydantic v2 schemas for Institute and Branch CRUD.
"""

from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field


# ─── Institute ───────────────────────────────────────────────────────────────

class InstituteCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=255)
    code: str = Field(..., min_length=2, max_length=50, pattern=r"^[A-Z0-9_]+$")
    address: str | None = None
    contact_email: EmailStr | None = None
    contact_phone: str | None = Field(None, max_length=20)


class InstituteUpdate(BaseModel):
    name: str | None = Field(None, min_length=2, max_length=255)
    address: str | None = None
    logo_url: str | None = None
    contact_email: EmailStr | None = None
    contact_phone: str | None = Field(None, max_length=20)
    is_active: bool | None = None


class InstituteRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    code: str
    logo_url: str | None
    address: str | None
    contact_email: str | None
    contact_phone: str | None
    is_active: bool
    created_at: datetime
    updated_at: datetime


# ─── Branch ──────────────────────────────────────────────────────────────────

class BranchCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=255)
    code: str = Field(..., min_length=2, max_length=50, pattern=r"^[A-Z0-9_]+$")
    address: str | None = None
    contact_number: str | None = Field(None, max_length=20)
    is_main_branch: bool = False


class BranchUpdate(BaseModel):
    name: str | None = Field(None, min_length=2, max_length=255)
    address: str | None = None
    contact_number: str | None = Field(None, max_length=20)
    is_active: bool | None = None


class BranchRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    institute_id: uuid.UUID
    name: str
    code: str
    address: str | None
    contact_number: str | None
    is_main_branch: bool
    is_active: bool
    created_at: datetime
