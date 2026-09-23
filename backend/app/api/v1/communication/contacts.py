"""
app/api/v1/communication/contacts.py
------------------------------------
Derived contact discovery endpoint.
Returns allowable recipients determined by active batch enrollments.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import CurrentUser, get_db
from app.schemas.common import StandardResponse
from app.schemas.communication import EligibleContactRead
from app.services import communication_service

router = APIRouter(tags=["Communication - Contacts"])


@router.get(
    "/contacts/eligible",
    response_model=StandardResponse[list[EligibleContactRead]],
    summary="Get eligible contacts for messaging based on derived enrollment graph",
)
async def get_eligible_contacts(
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    contacts = await communication_service.get_eligible_contacts(
        db=db,
        institute_id=current_user.institute_id,
        current_user=current_user,
    )
    return StandardResponse(data=contacts)
