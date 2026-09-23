"""
app/api/v1/communication/notifications.py
-----------------------------------------
Notification feed, unread counter, and mark-read endpoints.
"""

from __future__ import annotations

import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import CurrentUser, get_db
from app.schemas.common import StandardResponse
from app.schemas.communication import (
    NotificationCountRead,
    NotificationMarkReadRequest,
    NotificationRead,
)
from app.services import communication_service

router = APIRouter(tags=["Communication - Notifications"])


@router.get(
    "/notifications",
    response_model=StandardResponse[list[NotificationRead]],
    summary="List in-app notifications for current user",
)
async def list_notifications(
    current_user: CurrentUser,
    is_read: Annotated[bool | None, Query(description="Filter by read status")] = None,
    limit: Annotated[int, Query(ge=1, le=100)] = 50,
    db: AsyncSession = Depends(get_db),
):
    notifs = await communication_service.list_notifications(
        db=db,
        institute_id=current_user.institute_id,
        user_id=current_user.id,
        is_read=is_read,
        limit=limit,
    )
    items = [
        NotificationRead(
            id=n.id,
            user_id=n.user_id,
            title=n.title,
            body=n.body,
            type=n.type,
            related_entity_type=n.related_entity_type,
            related_entity_id=n.related_entity_id,
            is_read=n.is_read,
            read_at=n.read_at,
            created_at=n.created_at,
        )
        for n in notifs
    ]
    return StandardResponse(data=items)


@router.get(
    "/notifications/unread-count",
    response_model=StandardResponse[NotificationCountRead],
    summary="Get unread notification count for badge rendering",
)
async def get_unread_count(
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    count = await communication_service.get_unread_notification_count(
        db=db,
        institute_id=current_user.institute_id,
        user_id=current_user.id,
    )
    return StandardResponse(data=NotificationCountRead(unread_count=count))


@router.patch(
    "/notifications/{id}/read",
    response_model=StandardResponse[dict],
    summary="Mark single notification as read",
)
async def mark_single_read(
    id: uuid.UUID,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    updated = await communication_service.mark_notifications_as_read(
        db=db,
        institute_id=current_user.institute_id,
        user_id=current_user.id,
        notification_ids=[id],
    )
    return StandardResponse(
        data={"marked_read": updated},
        message="Notification marked as read.",
    )


@router.post(
    "/notifications/mark-all-read",
    response_model=StandardResponse[dict],
    summary="Mark all user notifications as read",
)
async def mark_all_read(
    current_user: CurrentUser,
    body: NotificationMarkReadRequest | None = None,
    db: AsyncSession = Depends(get_db),
):
    n_ids = body.notification_ids if body and body.notification_ids else None
    updated = await communication_service.mark_notifications_as_read(
        db=db,
        institute_id=current_user.institute_id,
        user_id=current_user.id,
        notification_ids=n_ids,
    )
    return StandardResponse(
        data={"marked_read": updated},
        message=f"Marked {updated} notification(s) as read.",
    )
