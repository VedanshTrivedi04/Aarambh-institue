"""
app/models/role.py
------------------
Dynamic RBAC: Role, Permission, RolePermission, UserRole.

Design rationale (from architectural review):
  - Four hard-coded role strings (ADMIN/TEACHER/STUDENT/PARENT) are NOT enough.
  - The ERP needs: Super Admin, Management, Accountant, Counsellor, Receptionist,
    Coordinator, Teacher, Student, Parent, etc.
  - Authorization must be permission-based, not role-name-based, so we can give
    Accountant fee permissions without giving academic permissions.

Structure:
  Role ──< RolePermission >── Permission
    │
  UserRole ── User  (a user can hold multiple roles, optionally scoped to a branch)

System roles (seeded at startup):
  SUPER_ADMIN, ADMIN, MANAGEMENT, ACCOUNTANT, COUNSELLOR,
  RECEPTIONIST, COORDINATOR, TEACHER, STUDENT, PARENT

Permissions are slugs grouped by module:
  e.g.  "students.view", "students.create", "fees.record_payment",
        "attendance.mark", "results.publish"
"""

from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, ForeignKey, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.user import User


class Permission(TimestampMixin, Base):
    """
    A single granular action within a module.

    slug examples:
      "students.view"       "students.create"    "students.delete"
      "fees.view"           "fees.record_payment"
      "attendance.mark"     "results.publish"
      "chat.send"           "announcements.create"
    """

    __tablename__ = "permissions"
    __table_args__ = (UniqueConstraint("slug", name="uq_permissions_slug"),)

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    slug: Mapped[str] = mapped_column(String(100), nullable=False)  # e.g. "fees.record_payment"
    name: Mapped[str] = mapped_column(String(150), nullable=False)  # Human label
    module: Mapped[str] = mapped_column(String(60), nullable=False, index=True)  # "fees"
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    role_permissions: Mapped[list["RolePermission"]] = relationship(
        "RolePermission", back_populates="permission", lazy="noload"
    )

    def __repr__(self) -> str:
        return f"<Permission slug={self.slug!r}>"


class Role(TimestampMixin, Base):
    """
    A named group of permissions, scoped to an institute.

    `is_system_role=True` — seeded roles that cannot be deleted.
    `is_system_role=False` — custom roles created by institute admin.
    """

    __tablename__ = "roles"
    __table_args__ = (
        UniqueConstraint("institute_id", "slug", name="uq_roles_institute_slug"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    institute_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("institutes.id", ondelete="CASCADE"),
        nullable=True,    # NULL = global system role (available to all institutes)
        index=True,
    )
    slug: Mapped[str] = mapped_column(String(60), nullable=False)   # e.g. "TEACHER"
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_system_role: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    role_permissions: Mapped[list["RolePermission"]] = relationship(
        "RolePermission", back_populates="role", lazy="noload"
    )
    user_roles: Mapped[list["UserRole"]] = relationship(
        "UserRole", back_populates="role", lazy="noload"
    )

    def __repr__(self) -> str:
        return f"<Role slug={self.slug!r} institute_id={self.institute_id}>"


class RolePermission(Base):
    """Many-to-many join: Role ↔ Permission."""

    __tablename__ = "role_permissions"
    __table_args__ = (
        UniqueConstraint("role_id", "permission_id", name="uq_role_permissions"),
    )

    role_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("roles.id", ondelete="CASCADE"),
        primary_key=True,
    )
    permission_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("permissions.id", ondelete="CASCADE"),
        primary_key=True,
    )

    role: Mapped["Role"] = relationship("Role", back_populates="role_permissions", lazy="noload")
    permission: Mapped["Permission"] = relationship(
        "Permission", back_populates="role_permissions", lazy="noload"
    )


class UserRole(TimestampMixin, Base):
    """
    Assigns a Role to a User, optionally scoped to a specific branch.

    A user can hold multiple roles:
      e.g. TEACHER in Main Branch + COORDINATOR in Vijay Nagar Branch.

    `branch_id=None` means the role applies to ALL branches of the institute.
    """

    __tablename__ = "user_roles"
    __table_args__ = (
        UniqueConstraint("user_id", "role_id", "branch_id", name="uq_user_roles"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    role_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("roles.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    branch_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("branches.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )
    granted_by: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), nullable=True
    )

    user: Mapped["User"] = relationship("User", back_populates="user_roles", lazy="noload")
    role: Mapped["Role"] = relationship("Role", back_populates="user_roles", lazy="noload")

    def __repr__(self) -> str:
        return f"<UserRole user_id={self.user_id} role_id={self.role_id}>"
