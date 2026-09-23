"""
app/models/people.py
---------------------
Domain profiles — separate from User (auth identity).

Architecture rules (from user review §1, rules.md §3):
  "User and Student/Teacher/Parent should NOT be the same thing."

  User  → authentication identity (email, password, role, status)
  *Profile → domain-specific data (name, DOB, address, photo, etc.)

  One User has exactly one *Profile of the matching type.
  A Parent can be linked to multiple students via StudentParent join.

Models:
  StudentProfile  — personal/academic info for enrolled students
  TeacherProfile  — qualifications, experience for teachers
  ParentProfile   — guardian contact info
  StaffProfile    — administrative/support staff
  StudentParent   — many-to-many join: student ↔ parent(s)

Key constraints:
  - photo_url is stored as a path/URL — file stored in object storage (Slice 7).
  - `admission_number` is unique per institute — assigned by the Admissions module.
  - `employee_code` is unique per institute for TeacherProfile and StaffProfile.
"""

from __future__ import annotations

import enum
import uuid
from datetime import date as Date
from typing import TYPE_CHECKING

from sqlalchemy import (
    Boolean,
    Date as SADate,
    Enum,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, SoftDeleteMixin, TenantAwareMixin, TimestampMixin

if TYPE_CHECKING:
    from app.models.academic import Enrollment
    from app.models.user import User


class Gender(str, enum.Enum):
    MALE = "MALE"
    FEMALE = "FEMALE"
    OTHER = "OTHER"


class BloodGroup(str, enum.Enum):
    A_POS = "A+"
    A_NEG = "A-"
    B_POS = "B+"
    B_NEG = "B-"
    O_POS = "O+"
    O_NEG = "O-"
    AB_POS = "AB+"
    AB_NEG = "AB-"


# ─────────────────────────────────────────────────────────────────────────────
# StudentProfile
# ─────────────────────────────────────────────────────────────────────────────

class StudentProfile(TenantAwareMixin, TimestampMixin, SoftDeleteMixin, Base):
    """
    Student-specific domain data.

    admission_number — unique per institute; assigned during admission flow (Slice 5).
    current_class_id — denormalised for fast filtering/display (always in sync via service).
    guardian_id      — primary parent/guardian (shortcut to the main StudentParent row).
    """

    __tablename__ = "student_profiles"
    __table_args__ = (
        UniqueConstraint("institute_id", "admission_number",
                         name="uq_student_profiles_institute_admission_number"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=False, unique=True, index=True,
    )

    # Personal info
    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False)
    date_of_birth: Mapped[Date | None] = mapped_column(SADate, nullable=True)
    gender: Mapped[Gender | None] = mapped_column(
        Enum(Gender, name="gender_enum"), nullable=True
    )
    blood_group: Mapped[BloodGroup | None] = mapped_column(
        Enum(BloodGroup, name="blood_group_enum"), nullable=True
    )
    photo_url: Mapped[str | None] = mapped_column(String(500), nullable=True)

    # Academic info
    admission_number: Mapped[str | None] = mapped_column(String(50), nullable=True, index=True)
    current_class_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("school_classes.id", ondelete="SET NULL"),
        nullable=True, index=True,
    )
    joining_date: Mapped[Date | None] = mapped_column(SADate, nullable=True)

    # Address
    address_line1: Mapped[str | None] = mapped_column(String(255), nullable=True)
    address_line2: Mapped[str | None] = mapped_column(String(255), nullable=True)
    city: Mapped[str | None] = mapped_column(String(100), nullable=True)
    state: Mapped[str | None] = mapped_column(String(100), nullable=True)
    pincode: Mapped[str | None] = mapped_column(String(10), nullable=True)

    # Emergency contact
    emergency_contact_name: Mapped[str | None] = mapped_column(String(150), nullable=True)
    emergency_contact_phone: Mapped[str | None] = mapped_column(String(20), nullable=True)

    # Status
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # Relationships
    user: Mapped["User"] = relationship("User", foreign_keys=[user_id], lazy="noload")
    enrollments: Mapped[list["Enrollment"]] = relationship(
        "Enrollment", back_populates="student", lazy="noload"
    )
    student_parents: Mapped[list["StudentParent"]] = relationship(
        "StudentParent", back_populates="student",
        lazy="noload", cascade="all, delete-orphan"
    )

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"

    def __repr__(self) -> str:
        return f"<StudentProfile id={self.id} name={self.full_name!r}>"


# ─────────────────────────────────────────────────────────────────────────────
# TeacherProfile
# ─────────────────────────────────────────────────────────────────────────────

class TeacherProfile(TenantAwareMixin, TimestampMixin, SoftDeleteMixin, Base):
    """
    Teacher/faculty domain data.

    employee_code is unique per institute — assigned by HR/Admin.
    subjects_expertise stores a simple list of subject codes for display (not FK).
    """

    __tablename__ = "teacher_profiles"
    __table_args__ = (
        UniqueConstraint("institute_id", "employee_code",
                         name="uq_teacher_profiles_institute_employee_code"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=False, unique=True, index=True,
    )

    # Personal info
    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False)
    date_of_birth: Mapped[Date | None] = mapped_column(SADate, nullable=True)
    gender: Mapped[Gender | None] = mapped_column(
        Enum(Gender, name="gender_enum", create_type=False), nullable=True
    )
    photo_url: Mapped[str | None] = mapped_column(String(500), nullable=True)

    # Professional info
    employee_code: Mapped[str | None] = mapped_column(String(50), nullable=True, index=True)
    qualification: Mapped[str | None] = mapped_column(String(255), nullable=True)
    experience_years: Mapped[int | None] = mapped_column(Integer, nullable=True)
    joining_date: Mapped[Date | None] = mapped_column(SADate, nullable=True)

    # Contact
    personal_email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    personal_phone: Mapped[str | None] = mapped_column(String(20), nullable=True)
    address: Mapped[str | None] = mapped_column(Text, nullable=True)

    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # Relationships
    user: Mapped["User"] = relationship("User", foreign_keys=[user_id], lazy="noload")

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"

    def __repr__(self) -> str:
        return f"<TeacherProfile id={self.id} name={self.full_name!r}>"


# ─────────────────────────────────────────────────────────────────────────────
# ParentProfile
# ─────────────────────────────────────────────────────────────────────────────

class ParentProfile(TenantAwareMixin, TimestampMixin, SoftDeleteMixin, Base):
    """
    Guardian/parent domain data.
    A parent can have multiple children across the same institute.
    """

    __tablename__ = "parent_profiles"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=False, unique=True, index=True,
    )

    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False)
    relation: Mapped[str] = mapped_column(
        String(30), nullable=False, default="PARENT"
    )  # "FATHER", "MOTHER", "GUARDIAN"
    occupation: Mapped[str | None] = mapped_column(String(150), nullable=True)
    annual_income: Mapped[str | None] = mapped_column(String(50), nullable=True)
    photo_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    address: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # Relationships
    user: Mapped["User"] = relationship("User", foreign_keys=[user_id], lazy="noload")
    student_parents: Mapped[list["StudentParent"]] = relationship(
        "StudentParent", back_populates="parent",
        lazy="noload", cascade="all, delete-orphan"
    )

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"

    def __repr__(self) -> str:
        return f"<ParentProfile id={self.id} name={self.full_name!r}>"


# ─────────────────────────────────────────────────────────────────────────────
# StaffProfile
# ─────────────────────────────────────────────────────────────────────────────

class StaffProfile(TenantAwareMixin, TimestampMixin, SoftDeleteMixin, Base):
    """
    Administrative/support staff (Receptionist, Accountant, Coordinator, etc.)
    Separate from TeacherProfile so permissions can differ.
    """

    __tablename__ = "staff_profiles"
    __table_args__ = (
        UniqueConstraint("institute_id", "employee_code",
                         name="uq_staff_profiles_institute_employee_code"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=False, unique=True, index=True,
    )

    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False)
    designation: Mapped[str | None] = mapped_column(String(100), nullable=True)
    department: Mapped[str | None] = mapped_column(String(100), nullable=True)
    employee_code: Mapped[str | None] = mapped_column(String(50), nullable=True, index=True)
    joining_date: Mapped[Date | None] = mapped_column(SADate, nullable=True)
    photo_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    address: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # Relationships
    user: Mapped["User"] = relationship("User", foreign_keys=[user_id], lazy="noload")

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"

    def __repr__(self) -> str:
        return f"<StaffProfile id={self.id} name={self.full_name!r}>"


# ─────────────────────────────────────────────────────────────────────────────
# StudentParent  (join table)
# ─────────────────────────────────────────────────────────────────────────────

class StudentParent(TimestampMixin, Base):
    """
    Links a StudentProfile to one or more ParentProfiles.

    is_primary=True identifies the primary contact for fee notices, SMS, etc.
    Only one row per (student, parent) pair is allowed.
    """

    __tablename__ = "student_parents"
    __table_args__ = (
        UniqueConstraint("student_id", "parent_id", name="uq_student_parents"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    student_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("student_profiles.id", ondelete="CASCADE"),
        nullable=False, index=True,
    )
    parent_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("parent_profiles.id", ondelete="CASCADE"),
        nullable=False, index=True,
    )
    is_primary: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    student: Mapped["StudentProfile"] = relationship(
        "StudentProfile", back_populates="student_parents", lazy="noload"
    )
    parent: Mapped["ParentProfile"] = relationship(
        "ParentProfile", back_populates="student_parents", lazy="noload"
    )

    def __repr__(self) -> str:
        return f"<StudentParent student={self.student_id} parent={self.parent_id} primary={self.is_primary}>"
