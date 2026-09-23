"""
app/api/v1/communication/announcements.py
-----------------------------------------
Targeted bulletin and broadcast announcement endpoints.
"""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import CurrentUser, get_db, require_role
from app.schemas.common import StandardResponse
from app.schemas.communication import AnnouncementCreate, AnnouncementRead
from app.services import communication_service

router = APIRouter(tags=["Communication - Announcements"])

_STAFF_OR_TEACHER = ("SUPER_ADMIN", "ADMIN", "TEACHER", "COUNSELLOR")


def _format_announcement_read(ann) -> AnnouncementRead:
    author_name = None
    if getattr(ann, "author", None):
        author_name = ann.author.email

    return AnnouncementRead(
        id=ann.id,
        institute_id=ann.institute_id,
        title=ann.title,
        body=ann.body,
        target_audience=ann.target_audience or {},
        is_pinned=ann.is_pinned,
        published_at=ann.published_at,
        created_by=ann.created_by,
        author_name=author_name,
        created_at=ann.created_at,
    )


@router.post(
    "/announcements",
    response_model=StandardResponse[AnnouncementRead],
    status_code=status.HTTP_201_CREATED,
    dependencies=[require_role(*_STAFF_OR_TEACHER)],
    summary="Publish targeted or broadcast announcement",
)
async def create_announcement(
    body: AnnouncementCreate,
    current_user: CurrentUser,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    ann = await communication_service.create_announcement(
        db=db,
        institute_id=current_user.institute_id,
        creator_user=current_user,
        payload=body,
        request=request,
    )
    return StandardResponse(
        data=_format_announcement_read(ann),
        message="Announcement published successfully.",
    )


@router.get(
    "/announcements",
    response_model=StandardResponse[list[AnnouncementRead]],
    summary="Get announcement feed filtered by user's audience segment",
)
async def list_announcements(
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    announcements = await communication_service.list_announcements(
        db=db,
        institute_id=current_user.institute_id,
        current_user=current_user,
    )
    return StandardResponse(data=[_format_announcement_read(a) for a in announcements])
