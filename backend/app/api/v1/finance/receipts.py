"""
app/api/v1/finance/receipts.py
------------------------------
Receipt verification and lookup endpoints.
"""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import CurrentUser, get_db
from app.core.exceptions import ForbiddenError
from app.models.people import ParentProfile, StudentParent, StudentProfile
from app.schemas.common import StandardResponse
from app.schemas.finance import ReceiptRead
from app.services import finance_service

router = APIRouter(tags=["Finance - Receipts"])


@router.get(
    "/receipts/number/{receipt_number}",
    response_model=StandardResponse[ReceiptRead],
    summary="Lookup receipt by receipt number",
)
async def get_receipt_by_number(
    receipt_number: str,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    is_student_or_parent = current_user.role in ("STUDENT", "PARENT")
    student_id = None
    if current_user.role == "STUDENT":
        s_stmt = select(StudentProfile.id).where(StudentProfile.user_id == current_user.id)
        student_id = (await db.execute(s_stmt)).scalar_one_or_none()
    elif current_user.role == "PARENT":
        p_stmt = select(ParentProfile.id).where(ParentProfile.user_id == current_user.id)
        parent_id = (await db.execute(p_stmt)).scalar_one_or_none()
        if parent_id:
            sp_stmt = select(StudentParent.student_id).where(StudentParent.parent_id == parent_id)
            student_id = (await db.execute(sp_stmt)).scalars().first()

    rcp = await finance_service.get_receipt_by_number(
        db=db,
        institute_id=current_user.institute_id,
        receipt_number=receipt_number,
        for_student_or_parent=is_student_or_parent,
        student_id=student_id,
    )
    return StandardResponse(
        data=ReceiptRead(
            id=rcp.id,
            payment_id=rcp.payment_id,
            receipt_number=rcp.receipt_number,
            pdf_storage_key=rcp.pdf_storage_key,
            issued_at=rcp.issued_at,
            created_at=rcp.created_at,
        )
    )
