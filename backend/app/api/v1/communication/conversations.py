"""
app/api/v1/communication/conversations.py
-----------------------------------------
Conversation threads and messaging endpoints.
"""

from __future__ import annotations

import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, Query, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import CurrentUser, get_db
from app.schemas.common import StandardResponse
from app.schemas.communication import (
    ConversationCreate,
    ConversationRead,
    MessageCreate,
    MessageRead,
    ParticipantRead,
)
from app.services import communication_service

router = APIRouter(tags=["Communication - Conversations & Messages"])


def _format_conversation_read(conv, current_user_id: uuid.UUID) -> ConversationRead:
    participants_read = [
        ParticipantRead(
            id=p.id,
            user_id=p.user_id,
            full_name=p.user.email if p.user else None,
            email=p.user.email if p.user else None,
            role_in_conversation=p.role_in_conversation,
            last_read_at=p.last_read_at,
            joined_at=p.joined_at,
        )
        for p in (conv.participants or [])
    ]

    # Calculate unread count for current user
    user_part = next((p for p in (conv.participants or []) if p.user_id == current_user_id), None)
    unread = 0
    last_read = user_part.last_read_at if user_part else None
    if hasattr(conv, "messages") and conv.messages:
        for m in conv.messages:
            if not getattr(m, "is_hidden", False):
                if m.sender_id != current_user_id:
                    if last_read is None or (m.created_at and m.created_at > last_read):
                        unread += 1

    last_msg_read = None
    if hasattr(conv, "messages") and conv.messages:
        visible_msgs = [m for m in conv.messages if not getattr(m, "is_hidden", False)]
        if visible_msgs:
            last_m = visible_msgs[-1]
            last_msg_read = MessageRead(
                id=last_m.id,
                conversation_id=last_m.conversation_id,
                sender_id=last_m.sender_id,
                sender_name=last_m.sender.email if getattr(last_m, "sender", None) else None,
                sender_role=getattr(last_m.sender, "role", None) if getattr(last_m, "sender", None) else None,
                body=last_m.body,
                attachment_id=last_m.attachment_id,
                is_hidden=last_m.is_hidden,
                sent_at=last_m.sent_at,
                created_at=last_m.created_at,
            )

    return ConversationRead(
        id=conv.id,
        institute_id=conv.institute_id,
        type=conv.type,
        batch_id=conv.batch_id,
        title=conv.title,
        created_at=conv.created_at,
        updated_at=conv.updated_at,
        unread_count=unread,
        participants=participants_read,
        last_message=last_msg_read,
    )


@router.post(
    "/conversations",
    response_model=StandardResponse[ConversationRead],
    status_code=status.HTTP_201_CREATED,
    summary="Create or retrieve direct/group conversation thread",
)
async def create_conversation(
    body: ConversationCreate,
    current_user: CurrentUser,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    conv = await communication_service.create_conversation(
        db=db,
        institute_id=current_user.institute_id,
        creator_user=current_user,
        payload=body,
        request=request,
    )
    return StandardResponse(
        data=_format_conversation_read(conv, current_user.id),
        message="Conversation thread ready.",
    )


@router.get(
    "/conversations",
    response_model=StandardResponse[list[ConversationRead]],
    summary="List all conversations for current user",
)
async def list_conversations(
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    convs = await communication_service.list_user_conversations(
        db=db,
        institute_id=current_user.institute_id,
        user_id=current_user.id,
    )
    return StandardResponse(data=[_format_conversation_read(c, current_user.id) for c in convs])


@router.get(
    "/conversations/{id}",
    response_model=StandardResponse[ConversationRead],
    summary="Get conversation details by ID",
)
async def get_conversation(
    id: uuid.UUID,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    conv = await communication_service.get_conversation(
        db=db,
        institute_id=current_user.institute_id,
        conversation_id=id,
        current_user=current_user,
    )
    return StandardResponse(data=_format_conversation_read(conv, current_user.id))


@router.post(
    "/conversations/{id}/messages",
    response_model=StandardResponse[MessageRead],
    status_code=status.HTTP_201_CREATED,
    summary="Send a message into a conversation",
)
async def send_message(
    id: uuid.UUID,
    body: MessageCreate,
    current_user: CurrentUser,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    msg = await communication_service.send_message(
        db=db,
        institute_id=current_user.institute_id,
        conversation_id=id,
        sender_user=current_user,
        payload=body,
        request=request,
    )
    return StandardResponse(
        data=MessageRead(
            id=msg.id,
            conversation_id=msg.conversation_id,
            sender_id=msg.sender_id,
            sender_name=current_user.email,
            sender_role=current_user.role,
            body=msg.body,
            attachment_id=msg.attachment_id,
            is_hidden=msg.is_hidden,
            sent_at=msg.sent_at,
            created_at=msg.created_at,
        ),
        message="Message sent successfully.",
    )


@router.get(
    "/conversations/{id}/messages",
    response_model=StandardResponse[list[MessageRead]],
    summary="Get paginated messages for a conversation",
)
async def list_messages(
    id: uuid.UUID,
    current_user: CurrentUser,
    limit: Annotated[int, Query(ge=1, le=100)] = 50,
    db: AsyncSession = Depends(get_db),
):
    messages = await communication_service.list_conversation_messages(
        db=db,
        institute_id=current_user.institute_id,
        conversation_id=id,
        current_user=current_user,
        limit=limit,
    )
    items = [
        MessageRead(
            id=m.id,
            conversation_id=m.conversation_id,
            sender_id=m.sender_id,
            sender_name=m.sender.email if getattr(m, "sender", None) else None,
            sender_role=m.sender.role if getattr(m, "sender", None) else None,
            body=m.body,
            attachment_id=m.attachment_id,
            is_hidden=m.is_hidden,
            sent_at=m.sent_at,
            created_at=m.created_at,
        )
        for m in messages
    ]
    return StandardResponse(data=items)
