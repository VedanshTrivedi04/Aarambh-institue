"""
app/api/v1/communication/ptm.py
-------------------------------
Parent-Teacher Meeting (PTM) booking and lifecycle endpoints.
"""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import CurrentUser, get_db, require_role
from app.schemas.common import StandardResponse
from app.schemas.communication import (
    PTMRequestCreate,
    PTMRequestRead,
    PTMStatusUpdate,
)
from app.services import communication_service

router = APIRouter(tags=["Communication - PTM Requests"])


def _format_ptm_read(ptm) -> PTMRequestRead:
    p_name = None
    if getattr(ptm, "parent", None):
        p_name = f"{ptm.parent.first_name} {ptm.parent.last_name}"

    s_name = None
    if getattr(ptm, "student", None):
        s_name = f"{ptm.student.first_name} {ptm.student.last_name or ''}".strip()

    t_name = None
    if getattr(ptm, "teacher", None):
        t_name = f"{ptm.teacher.first_name} {ptm.teacher.last_name}"

    return PTMRequestRead(
        id=ptm.id,
        institute_id=ptm.institute_id,
        parent_id=ptm.parent_id,
        parent_name=p_name,
        student_id=ptm.student_id,
        student_name=s_name,
        teacher_id=ptm.teacher_id,
        teacher_name=t_name,
        reason=ptm.reason,
        requested_slot=ptm.requested_slot,
        confirmed_slot=ptm.confirmed_slot,
        teacher_notes=ptm.teacher_notes,
        status=ptm.status,
        created_at=ptm.created_at,
        updated_at=ptm.updated_at,
    )


@router.post(
    "/ptm/requests",
    response_model=StandardResponse[PTMRequestRead],
    status_code=status.HTTP_201_CREATED,
    dependencies=[require_role("PARENT")],
    summary="Parent requests a Parent-Teacher Meeting",
)
async def request_ptm(
    body: PTMRequestCreate,
    current_user: CurrentUser,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    ptm = await communication_service.request_ptm(
        db=db,
        institute_id=current_user.institute_id,
        parent_user=current_user,
        payload=body,
        request=request,
    )
    return StandardResponse(
        data=_format_ptm_read(ptm),
        message="PTM request submitted to teacher successfully.",
    )


@router.get(
    "/ptm/requests",
    response_model=StandardResponse[list[PTMRequestRead]],
    summary="List PTM requests visible to caller",
)
async def list_ptm_requests(
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    items = await communication_service.list_ptm_requests(
        db=db,
        institute_id=current_user.institute_id,
        current_user=current_user,
    )
    return StandardResponse(data=[_format_ptm_read(p) for p in items])


@router.patch(
    "/ptm/requests/{id}/status",
    response_model=StandardResponse[PTMRequestRead],
    summary="Teacher or Admin updates PTM status (approve, reject, reschedule, complete)",
)
async def update_ptm_status(
    id: uuid.UUID,
    body: PTMStatusUpdate,
    current_user: CurrentUser,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    ptm = await communication_service.update_ptm_status(
        db=db,
        institute_id=current_user.institute_id,
        responder_user=current_user,
        ptm_id=id,
        payload=body,
        request=request,
    )
    return StandardResponse(
        data=_format_ptm_read(ptm),
        message=f"PTM appointment status updated to {ptm.status.value}.",
    )
