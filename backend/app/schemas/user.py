"""
app/schemas/user.py
-------------------
Pydantic v2 schemas for User read/create/update.
Deliberately lean — password is never returned in any response.
"""

from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field, model_validator

from app.models.user import UserStatus


class UserRead(BaseModel):
    """Safe public representation — no password hash, no session details."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    institute_id: uuid.UUID | None
    email: str | None
    mobile: str | None
    role: str
    status: UserStatus
    is_active: bool
    is_verified: bool
    last_login_at: datetime | None
    created_at: datetime
    updated_at: datetime


class UserCreate(BaseModel):
    """Used internally (e.g. Admission Wizard) — not a public signup endpoint."""

    institute_id: uuid.UUID
    email: EmailStr | None = None
    mobile: str | None = Field(None, min_length=10, max_length=15)
    password: str = Field(..., min_length=8, max_length=128)
    role: str = Field(..., min_length=2, max_length=60)

    @model_validator(mode="after")
    def email_or_mobile_required(self) -> "UserCreate":
        if not self.email and not self.mobile:
            raise ValueError("Either email or mobile must be provided")
        return self


class UserUpdate(BaseModel):
    email: EmailStr | None = None
    mobile: str | None = Field(None, min_length=10, max_length=15)
    status: UserStatus | None = None
    is_active: bool | None = None


class ChangePasswordRequest(BaseModel):
    current_password: str = Field(..., min_length=8)
    new_password: str = Field(..., min_length=8, max_length=128)
