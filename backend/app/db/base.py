"""
app/db/base.py
--------------
SQLAlchemy 2.0 declarative base and shared column mixins.

Mixins provided:
  TimestampMixin    — created_at / updated_at with timezone
  SoftDeleteMixin   — deleted_at nullable; soft-delete convention
  TenantAwareMixin  — institute_id / branch_id for multi-branch support
                      (architecture.md §11 — nullable from day-one)

Every domain model should inherit from `Base` and include the mixins it needs.

Example:
    class Course(TenantAwareMixin, TimestampMixin, SoftDeleteMixin, Base):
        __tablename__ = "courses"
        ...
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime

from sqlalchemy import DateTime, ForeignKey, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """Root declarative base.  All ORM models inherit from this."""

    # Use UUID PKs by default — rules.md §9 (no sequential IDs in public URLs).
    type_annotation_map = {
        uuid.UUID: UUID(as_uuid=True),
    }


# ---------------------------------------------------------------------------
# Mixins
# ---------------------------------------------------------------------------


class TimestampMixin:
    """Adds created_at and updated_at columns to any table."""

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )


class SoftDeleteMixin:
    """
    Soft deletion support.

    deleted_at = None  →  record is active
    deleted_at = <ts>  →  record is archived / soft-deleted

    Rules (rules.md §6, architecture.md §11):
    - Attendance, enrollment, payment, and result records must NEVER be physically deleted.
    - Use `deleted_at IS NULL` filters in every service query for soft-deleted models.
    """

    deleted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        default=None,
        index=True,
    )

    @property
    def is_deleted(self) -> bool:
        return self.deleted_at is not None

    def soft_delete(self) -> None:
        self.deleted_at = datetime.now(UTC)


class TenantAwareMixin:
    """
    Multi-tenant columns — nullable from day one so a single-branch
    Aarambh install works without migration changes later.
    (architecture.md §11, systemdesign.md §2)

    Every service must scope queries by institute_id at the query level.
    Cross-tenant access raises CrossTenantAccessError (exceptions.py).
    """

    # FK defined as a string reference to avoid circular imports.
    institute_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("institutes.id", ondelete="RESTRICT"),
        nullable=True,
        index=True,
    )
    branch_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("branches.id", ondelete="RESTRICT"),
        nullable=True,
        index=True,
    )
