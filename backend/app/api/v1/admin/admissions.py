"""
app/api/v1/admin/admissions.py
------------------------------
Admin endpoint for the Atomic Admission Wizard.

Guarded by ADMIN / MANAGEMENT roles.
Executes complete student + parent + batch enrollment onboarding in one transaction.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import CurrentUser, get_db, require_role
from app.schemas.admission import AdmissionWizardRequest, AdmissionWizardResponse
from app.schemas.common import StandardResponse
from app.services.admission_service import AdmissionService

_ADMIN_ROLES = ("SUPER_ADMIN", "ADMIN", "MANAGEMENT")

router = APIRouter(
    prefix="/admissions",
    tags=["Admin - Admission Wizard"],
    dependencies=[require_role(*_ADMIN_ROLES)],
)


@router.post(
    "/wizard",
    response_model=StandardResponse[AdmissionWizardResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Process full student admission atomically",
)
async def process_admission_wizard(
    body: AdmissionWizardRequest,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    result = await AdmissionService.process_admission(
        db=db,
        request=body,
        institute_id=current_user.institute_id,
        processed_by=current_user.id,
    )
    await db.commit()
    return StandardResponse(
        data=result,
        message=result.message,
    )
