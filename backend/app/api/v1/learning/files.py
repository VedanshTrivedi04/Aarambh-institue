"""
app/api/v1/learning/files.py
----------------------------
Endpoints for generic file uploads, streaming downloads, and attachment metadata.

Endpoints:
  POST /files/upload            — Upload attachment (with MIME and size validation)
  GET  /files/{storage_key}     — Stream/download file content
  GET  /files/info/{attachment_id} — Get attachment metadata
"""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, File, Response, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import CurrentUser, get_db, require_role
from app.core.storage import get_storage_backend
from app.schemas.common import StandardResponse
from app.schemas.learning import FileAttachmentRead
from app.services.storage_service import StorageService

router = APIRouter(
    prefix="/files",
    tags=["Learning - Files & Attachments"],
)


@router.post(
    "/upload",
    response_model=StandardResponse[FileAttachmentRead],
    status_code=status.HTTP_201_CREATED,
    summary="Upload a file attachment (PDF, image, document, media)",
)
async def upload_file(
    file: UploadFile = File(...),
    current_user: CurrentUser = None,
    db: AsyncSession = Depends(get_db),
):
    content = await file.read()
    filename = file.filename or "unnamed_file"
    content_type = file.content_type or "application/octet-stream"

    attachment = await StorageService.upload_file(
        db=db,
        content_bytes=content,
        filename=filename,
        content_type=content_type,
        institute_id=current_user.institute_id if current_user else None,
        uploaded_by=current_user.id if current_user else None,
    )
    await db.commit()

    backend = get_storage_backend()
    res = FileAttachmentRead.model_validate(attachment)
    res.download_url = backend.get_url(attachment.storage_key)
    return StandardResponse(data=res, message="File uploaded successfully")


@router.get(
    "/{storage_key}",
    summary="Download or stream stored file content",
)
async def download_file(
    storage_key: str,
    db: AsyncSession = Depends(get_db),
):
    attachment = await StorageService.get_attachment_by_key(db, storage_key)
    content = await StorageService.download_file(storage_key)

    return Response(
        content=content,
        media_type=attachment.content_type,
        headers={"Content-Disposition": f'inline; filename="{attachment.file_name}"'},
    )


@router.get(
    "/info/{attachment_id}",
    response_model=StandardResponse[FileAttachmentRead],
    summary="Get attachment metadata",
)
async def get_attachment_info(
    attachment_id: uuid.UUID,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    attachment = await StorageService.get_attachment(
        db, attachment_id, current_user.institute_id
    )
    backend = get_storage_backend()
    res = FileAttachmentRead.model_validate(attachment)
    res.download_url = backend.get_url(attachment.storage_key)
    return StandardResponse(data=res)
