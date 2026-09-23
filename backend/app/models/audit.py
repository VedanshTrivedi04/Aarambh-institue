"""
app/models/audit.py
-------------------
Immutable audit log for all sensitive mutations in the system.

Audit entries are written for (backend.md §14):
  - Fee / payment edits or corrections
  - Result publishing
  - Admin overrides of student / enrollment data
  - Role assignments and changes
  - Batch transfers
  - Account status changes (suspend, reactivate)
  - Any action where "who changed what, when" has compliance value

Design:
  - Rows are NEVER updated or deleted — it's an append-only event log.
  - `old_values` / `new_values` stored as JSONB for flexibility.
  - `entity_name` + `entity_id` identifies the affected record.
  - `actor_id` is NULL only for system-generated events (e.g. scheduled jobs).

Usage (via audit_service.py):
    await audit_service.log(
        db=db,
        actor=current_user,
        action="result.published",
        entity_name="tests",
        entity_id=str(test.id),
        new_values={"status": "PUBLISHED"},
        request=request,
    )
"""

from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class AuditLog(Base):
    """
    Append-only audit event log.

    No TimestampMixin (we don't want an `updated_at` on an immutable record).
    No SoftDeleteMixin — audit rows are permanent.
    """

    __tablename__ = "audit_logs"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )

    # Tenant scope
    institute_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("institutes.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    # Who performed the action (NULL = automated/system)
    actor_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    actor_role: Mapped[str | None] = mapped_column(String(60), nullable=True)

    # What happened
    action: Mapped[str] = mapped_column(
        String(100), nullable=False, index=True
    )  # e.g. "result.published", "fee.payment_recorded", "enrollment.batch_transferred"

    # Which record was affected
    entity_name: Mapped[str] = mapped_column(
        String(100), nullable=False, index=True
    )  # table name, e.g. "tests", "payments", "enrollments"
    entity_id: Mapped[str] = mapped_column(
        String(100), nullable=False, index=True
    )  # UUID as string for flexibility

    # Before/after state (JSONB — nullable for simple events)
    old_values: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    new_values: Mapped[dict | None] = mapped_column(JSONB, nullable=True)

    # Request context
    ip_address: Mapped[str | None] = mapped_column(String(45), nullable=True)
    request_id: Mapped[str | None] = mapped_column(String(100), nullable=True)
    user_agent: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Timestamp — server-side to prevent client clock manipulation
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False, index=True
    )

    def __repr__(self) -> str:
        return (
            f"<AuditLog action={self.action!r} entity={self.entity_name}/{self.entity_id}"
            f" actor={self.actor_id}>"
        )
