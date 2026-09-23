"""
app/api/v1/communication/moderation.py
--------------------------------------
Content safety reporting and admin moderation endpoints.
"""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, Query, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import CurrentUser, get_db, require_role
from app.models.communication import ReportStatus
from app.schemas.common import StandardResponse
from app.schemas.communication import (
    ReportMessageCreate,
    ReportedMessageRead,
    ResolveReportRequest,
)
from app.services import communication_service

router = APIRouter(tags=["Communication - Safety & Moderation"])

_ADMIN_ONLY = ("SUPER_ADMIN", "ADMIN")


def _format_report_read(rep) -> ReportedMessageRead:
    m_body = None
    s_id = None
    s_name = None
    if getattr(rep, "message", None):
        m_body = rep.message.body
        s_id = rep.message.sender_id
        if getattr(rep.message, "sender", None):
            s_name = rep.message.sender.email

    rep_name = None
    if getattr(rep, "reporter", None):
        rep_name = rep.reporter.email

    res_name = None
    if getattr(rep, "resolver", None):
        res_name = rep.resolver.email

    return ReportedMessageRead(
        id=rep.id,
        institute_id=rep.institute_id,
        message_id=rep.message_id,
        message_body=m_body,
        sender_id=s_id,
        sender_name=s_name,
        reported_by=rep.reported_by,
        reporter_name=rep_name,
        reason=rep.reason,
        status=rep.status,
        resolved_by=rep.resolved_by,
        resolver_name=res_name,
        resolution_notes=rep.resolution_notes,
        action_taken=rep.action_taken,
        resolved_at=rep.resolved_at,
        created_at=rep.created_at,
    )


@router.post(
    "/moderation/reports",
    response_model=StandardResponse[ReportedMessageRead],
    status_code=status.HTTP_201_CREATED,
    summary="Report an inappropriate message for moderation review",
)
async def report_message(
    body: ReportMessageCreate,
    current_user: CurrentUser,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    report = await communication_service.report_message(
        db=db,
        institute_id=current_user.institute_id,
        reporter_user=current_user,
        payload=body,
        request=request,
    )
    return StandardResponse(
        data=_format_report_read(report),
        message="Message report submitted for administrative review.",
    )


@router.get(
    "/moderation/reports",
    response_model=StandardResponse[list[ReportedMessageRead]],
    dependencies=[require_role(*_ADMIN_ONLY)],
    summary="Admin moderation queue for reported messages",
)
async def list_reports(
    current_user: CurrentUser,
    status_filter: ReportStatus | None = Query(None, alias="status"),
    db: AsyncSession = Depends(get_db),
):
    reports = await communication_service.list_reported_messages(
        db=db,
        institute_id=current_user.institute_id,
        status=status_filter,
    )
    return StandardResponse(data=[_format_report_read(r) for r in reports])


@router.patch(
    "/moderation/reports/{id}/resolve",
    response_model=StandardResponse[ReportedMessageRead],
    dependencies=[require_role(*_ADMIN_ONLY)],
    summary="Admin resolves or dismisses a message report",
)
async def resolve_report(
    id: uuid.UUID,
    body: ResolveReportRequest,
    current_user: CurrentUser,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    resolved = await communication_service.resolve_reported_message(
        db=db,
        institute_id=current_user.institute_id,
        admin_user=current_user,
        report_id=id,
        payload=body,
        request=request,
    )
    return StandardResponse(
        data=_format_report_read(resolved),
        message=f"Report marked as {resolved.status.value}. Action: {resolved.action_taken or 'None'}.",
    )
