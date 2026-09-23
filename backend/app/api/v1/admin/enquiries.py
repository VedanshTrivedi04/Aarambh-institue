"""
app/api/v1/admin/enquiries.py
-----------------------------
Admin CRM endpoints for managing enquiries and follow-ups.

Guarded by ADMIN / MANAGEMENT roles.
"""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import CurrentUser, get_db, require_role
from app.models.enquiry import EnquiryStage
from app.schemas.common import MessageResponse, PaginatedResponse, StandardResponse
from app.schemas.enquiry import (
    EnquiryCreate,
    EnquiryFollowUpCreate,
    EnquiryFollowUpRead,
    EnquiryRead,
    EnquiryUpdate,
)
from app.services.enquiry_service import EnquiryService

_ADMIN_ROLES = ("SUPER_ADMIN", "ADMIN", "MANAGEMENT")

router = APIRouter(
    prefix="/enquiries",
    tags=["Admin - Enquiry CRM"],
    dependencies=[require_role(*_ADMIN_ROLES)],
)


@router.post(
    "",
    response_model=StandardResponse[EnquiryRead],
    status_code=status.HTTP_201_CREATED,
    summary="Log a new enquiry",
)
async def create_enquiry(
    body: EnquiryCreate,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    enquiry = await EnquiryService.create_enquiry(
        db, body, current_user.institute_id, author_id=current_user.id
    )
    await db.commit()
    return StandardResponse(
        data=EnquiryRead.model_validate(enquiry),
        message="Enquiry logged successfully",
    )


@router.get(
    "",
    response_model=PaginatedResponse[EnquiryRead],
    summary="List enquiries with filters",
)
async def list_enquiries(
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
    stage: EnquiryStage | None = Query(None, description="Filter by stage"),
    counsellor_id: uuid.UUID | None = Query(None, description="Filter by counsellor"),
    search: str | None = Query(None, description="Search by student/parent name or phone"),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
):
    skip = (page - 1) * page_size
    items, total = await EnquiryService.list_enquiries(
        db,
        institute_id=current_user.institute_id,
        stage=stage,
        counsellor_id=counsellor_id,
        search=search,
        skip=skip,
        limit=page_size,
    )
    return PaginatedResponse(
        items=[EnquiryRead.model_validate(e) for e in items],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get(
    "/{enquiry_id}",
    response_model=StandardResponse[EnquiryRead],
    summary="Get single enquiry details",
)
async def get_enquiry(
    enquiry_id: uuid.UUID,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    enquiry = await EnquiryService.get_enquiry(
        db, enquiry_id, current_user.institute_id
    )
    return StandardResponse(data=EnquiryRead.model_validate(enquiry))


@router.patch(
    "/{enquiry_id}",
    response_model=StandardResponse[EnquiryRead],
    summary="Update enquiry details",
)
async def update_enquiry(
    enquiry_id: uuid.UUID,
    body: EnquiryUpdate,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    enquiry = await EnquiryService.update_enquiry(
        db, enquiry_id, body, current_user.institute_id
    )
    await db.commit()
    return StandardResponse(
        data=EnquiryRead.model_validate(enquiry),
        message="Enquiry updated",
    )


@router.delete(
    "/{enquiry_id}",
    response_model=MessageResponse,
    summary="Soft-delete an enquiry",
)
async def delete_enquiry(
    enquiry_id: uuid.UUID,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    await EnquiryService.soft_delete_enquiry(
        db, enquiry_id, current_user.institute_id
    )
    await db.commit()
    return MessageResponse(message="Enquiry deleted")


@router.post(
    "/{enquiry_id}/follow-ups",
    response_model=StandardResponse[EnquiryFollowUpRead],
    status_code=status.HTTP_201_CREATED,
    summary="Add a follow-up note or update pipeline stage",
)
async def add_follow_up(
    enquiry_id: uuid.UUID,
    body: EnquiryFollowUpCreate,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    follow_up = await EnquiryService.add_follow_up(
        db,
        enquiry_id=enquiry_id,
        data=body,
        author_id=current_user.id,
        institute_id=current_user.institute_id,
    )
    await db.commit()
    return StandardResponse(
        data=EnquiryFollowUpRead.model_validate(follow_up),
        message="Follow-up recorded successfully",
    )


@router.get(
    "/{enquiry_id}/follow-ups",
    response_model=list[EnquiryFollowUpRead],
    summary="Get full follow-up timeline for an enquiry",
)
async def list_follow_ups(
    enquiry_id: uuid.UUID,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    follow_ups = await EnquiryService.list_follow_ups(
        db, enquiry_id, current_user.institute_id
    )
    return [EnquiryFollowUpRead.model_validate(f) for f in follow_ups]
