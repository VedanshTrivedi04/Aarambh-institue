"""
app/api/v1/operations/sessions.py
---------------------------------
ClassSession scheduling, status transitions, rescheduling, and session logs.

Endpoints:
  POST  /sessions                     — Create ad-hoc session
  GET   /sessions                     — List calendar sessions with filters
  GET   /sessions/{id}                — Get session details
  PATCH /sessions/{id}                — Update session
  POST  /sessions/{id}/reschedule     — Reschedule session (links old to new)
  POST  /sessions/{id}/log            — Save session delivery log (syllabus progress/homework)
  GET   /sessions/{id}/log            — Get session delivery log
"""

from __future__ import annotations

import uuid
from datetime import date

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import CurrentUser, get_db, require_role
from app.models.academic_operations import ClassSessionStatus
from app.schemas.academic_operations import (
    ClassSessionCreate,
    ClassSessionRead,
    ClassSessionUpdate,
    SessionLogCreate,
    SessionLogRead,
    SessionRescheduleRequest,
)
from app.schemas.common import PaginatedResponse, StandardResponse
from app.services.academic_operations_service import AcademicOperationsService

_TEACHER_OR_ADMIN = ("SUPER_ADMIN", "ADMIN", "MANAGEMENT", "TEACHER")

router = APIRouter(
    prefix="/sessions",
    tags=["Operations - Class Sessions"],
)


@router.post(
    "",
    response_model=StandardResponse[ClassSessionRead],
    status_code=status.HTTP_201_CREATED,
    dependencies=[require_role(*_TEACHER_OR_ADMIN)],
    summary="Create an ad-hoc class session",
)
async def create_session(
    body: ClassSessionCreate,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    session = await AcademicOperationsService.create_session(
        db, body, current_user.institute_id
    )
    await db.commit()
    return StandardResponse(
        data=ClassSessionRead.model_validate(session),
        message="Class session scheduled successfully",
    )


@router.get(
    "",
    response_model=PaginatedResponse[ClassSessionRead],
    summary="List class sessions with filters",
)
async def list_sessions(
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
    batch_id: uuid.UUID | None = Query(None, description="Filter by batch ID"),
    date_from: date | None = Query(None, description="Start date (inclusive)"),
    date_to: date | None = Query(None, description="End date (inclusive)"),
    session_status: ClassSessionStatus | None = Query(None, alias="status", description="Filter by status"),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
):
    skip = (page - 1) * page_size
    items, total = await AcademicOperationsService.list_sessions(
        db,
        institute_id=current_user.institute_id,
        batch_id=batch_id,
        date_from=date_from,
        date_to=date_to,
        session_status=session_status,
        skip=skip,
        limit=page_size,
    )
    return PaginatedResponse(
        items=[ClassSessionRead.model_validate(s) for s in items],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get(
    "/{session_id}",
    response_model=StandardResponse[ClassSessionRead],
    summary="Get single class session details",
)
async def get_session(
    session_id: uuid.UUID,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    session = await AcademicOperationsService.get_session(
        db, session_id, current_user.institute_id
    )
    return StandardResponse(data=ClassSessionRead.model_validate(session))


@router.patch(
    "/{session_id}",
    response_model=StandardResponse[ClassSessionRead],
    dependencies=[require_role(*_TEACHER_OR_ADMIN)],
    summary="Update class session details or status",
)
async def update_session(
    session_id: uuid.UUID,
    body: ClassSessionUpdate,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    session = await AcademicOperationsService.update_session(
        db, session_id, body, current_user.institute_id
    )
    await db.commit()
    return StandardResponse(
        data=ClassSessionRead.model_validate(session),
        message="Class session updated",
    )


@router.post(
    "/{session_id}/reschedule",
    response_model=StandardResponse[ClassSessionRead],
    dependencies=[require_role(*_TEACHER_OR_ADMIN)],
    summary="Reschedule a session to a new date/time",
)
async def reschedule_session(
    session_id: uuid.UUID,
    body: SessionRescheduleRequest,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    _old, new_session = await AcademicOperationsService.reschedule_session(
        db, session_id, body, current_user.institute_id, current_user.id
    )
    await db.commit()
    return StandardResponse(
        data=ClassSessionRead.model_validate(new_session),
        message="Session successfully rescheduled",
    )


@router.post(
    "/{session_id}/log",
    response_model=StandardResponse[SessionLogRead],
    dependencies=[require_role(*_TEACHER_OR_ADMIN)],
    summary="Record or update session delivery log (topics covered & homework)",
)
async def save_session_log(
    session_id: uuid.UUID,
    body: SessionLogCreate,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    log = await AcademicOperationsService.save_session_log(
        db, session_id, body, current_user.institute_id, current_user.id
    )
    await db.commit()
    return StandardResponse(
        data=SessionLogRead.model_validate(log),
        message="Session log saved successfully",
    )


@router.get(
    "/{session_id}/log",
    response_model=StandardResponse[SessionLogRead],
    summary="Get session delivery log",
)
async def get_session_log(
    session_id: uuid.UUID,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    log = await AcademicOperationsService.get_session_log(
        db, session_id, current_user.institute_id
    )
    return StandardResponse(data=SessionLogRead.model_validate(log))
