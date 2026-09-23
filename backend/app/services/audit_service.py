"""
app/services/audit_service.py
-----------------------------
Thin helper for writing entries to the audit_logs table.

Import and call from any service that performs a sensitive mutation.
All writes are fire-and-forget within the caller's transaction — if the
main transaction rolls back, the audit entry rolls back with it, which is
the correct behaviour (no phantom audit entry for a failed operation).

Usage:
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
from typing import Any

from fastapi import Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logging import get_logger, request_id_ctx_var
from app.models.audit import AuditLog

logger = get_logger(__name__)


async def log(
    db: AsyncSession,
    *,
    action: str,
    entity_name: str,
    entity_id: str,
    actor: Any = None,                  # User ORM row or None for system events
    old_values: dict | None = None,
    new_values: dict | None = None,
    request: Request | None = None,
    institute_id: uuid.UUID | None = None,
) -> AuditLog:
    """
    Write a single audit log entry within the caller's transaction.

    Parameters
    ----------
    action       : dot-notation event slug, e.g. "fee.payment_recorded"
    entity_name  : table / resource name, e.g. "payments"
    entity_id    : UUID (as str) of the affected row
    actor        : User ORM instance (None → system/scheduler)
    old_values   : snapshot before mutation (None for create events)
    new_values   : snapshot after mutation  (None for delete events)
    request      : FastAPI Request — used to capture IP and user-agent
    institute_id : override if actor is None (e.g. scheduled jobs)
    """
    actor_id = getattr(actor, "id", None)
    actor_role = getattr(actor, "role", None)
    resolved_institute_id = institute_id or getattr(actor, "institute_id", None)

    ip: str | None = None
    ua: str | None = None
    if request is not None:
        forwarded_for = request.headers.get("X-Forwarded-For")
        ip = forwarded_for.split(",")[0].strip() if forwarded_for else request.client.host if request.client else None
        ua = request.headers.get("User-Agent")

    entry = AuditLog(
        institute_id=resolved_institute_id,
        actor_id=actor_id,
        actor_role=actor_role,
        action=action,
        entity_name=entity_name,
        entity_id=entity_id,
        old_values=old_values,
        new_values=new_values,
        ip_address=ip,
        user_agent=ua,
        request_id=request_id_ctx_var.get(""),
    )

    db.add(entry)
    logger.info(
        "Audit event",
        action=action,
        entity=f"{entity_name}/{entity_id}",
        actor_id=str(actor_id) if actor_id else "system",
    )
    return entry
