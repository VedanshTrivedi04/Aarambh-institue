"""
app/api/v1/learning/materials.py
--------------------------------
Study Materials endpoints (Notes, DPPs, Worksheets, Revision guides).

Endpoints:
  POST   /materials           — Publish new study material (Teacher/Admin)
  GET    /materials           — List study materials (filterable by course, batch, type)
  GET    /materials/{id}      — Get single study material with attachment
  PATCH  /materials/{id}      — Update study material
  DELETE /materials/{id}      — Soft-delete study material
"""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import CurrentUser, get_db, require_role
from app.models.learning import MaterialType
from app.schemas.common import MessageResponse, PaginatedResponse, StandardResponse
from app.schemas.learning import (
    StudyMaterialCreate,
    StudyMaterialRead,
    StudyMaterialUpdate,
)
from app.services.learning_service import LearningService

_STAFF_OR_TEACHER = ("SUPER_ADMIN", "ADMIN", "MANAGEMENT", "TEACHER")

router = APIRouter(
    prefix="/materials",
    tags=["Learning - Study Materials"],
)


@router.post(
    "",
    response_model=StandardResponse[StudyMaterialRead],
    status_code=status.HTTP_201_CREATED,
    dependencies=[require_role(*_STAFF_OR_TEACHER)],
    summary="Publish new study material",
)
async def create_study_material(
    body: StudyMaterialCreate,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    material = await LearningService.create_study_material(
        db, body, current_user.institute_id, uploaded_by=current_user.id
    )
    await db.commit()
    return StandardResponse(
        data=StudyMaterialRead.model_validate(material),
        message="Study material published successfully",
    )


@router.get(
    "",
    response_model=PaginatedResponse[StudyMaterialRead],
    summary="List study materials with course/batch filters",
)
async def list_study_materials(
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
    course_id: uuid.UUID | None = Query(None, description="Filter by course"),
    batch_id: uuid.UUID | None = Query(None, description="Filter by batch"),
    material_type: MaterialType | None = Query(None, alias="type", description="Filter by material type"),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
):
    skip = (page - 1) * page_size
    # If caller is student/parent, only show published
    published_only = current_user.role in ("STUDENT", "PARENT")
    items, total = await LearningService.list_study_materials(
        db,
        institute_id=current_user.institute_id,
        course_id=course_id,
        batch_id=batch_id,
        material_type=material_type,
        published_only=published_only,
        skip=skip,
        limit=page_size,
    )
    return PaginatedResponse(
        items=[StudyMaterialRead.model_validate(m) for m in items],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get(
    "/{material_id}",
    response_model=StandardResponse[StudyMaterialRead],
    summary="Get single study material details",
)
async def get_study_material(
    material_id: uuid.UUID,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    material = await LearningService.get_study_material(
        db, material_id, current_user.institute_id
    )
    return StandardResponse(data=StudyMaterialRead.model_validate(material))


@router.patch(
    "/{material_id}",
    response_model=StandardResponse[StudyMaterialRead],
    dependencies=[require_role(*_STAFF_OR_TEACHER)],
    summary="Update study material details",
)
async def update_study_material(
    material_id: uuid.UUID,
    body: StudyMaterialUpdate,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    material = await LearningService.update_study_material(
        db, material_id, body, current_user.institute_id
    )
    await db.commit()
    return StandardResponse(
        data=StudyMaterialRead.model_validate(material),
        message="Study material updated",
    )


@router.delete(
    "/{material_id}",
    response_model=MessageResponse,
    dependencies=[require_role(*_STAFF_OR_TEACHER)],
    summary="Soft-delete study material",
)
async def delete_study_material(
    material_id: uuid.UUID,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    await LearningService.soft_delete_study_material(
        db, material_id, current_user.institute_id
    )
    await db.commit()
    return MessageResponse(message="Study material deleted")
