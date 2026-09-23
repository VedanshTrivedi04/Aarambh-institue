"""
app/services/storage_service.py
-------------------------------
Service layer for file uploads, attachment metadata, and storage lifecycle.
"""

from __future__ import annotations

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundError
from app.core.logging import get_logger
from app.core.storage import get_storage_backend, validate_file
from app.models.learning import FileAttachment

logger = get_logger(__name__)


class StorageService:
    """Manages file storage uploads, retrieval, and attachment rows."""

    @staticmethod
    async def upload_file(
        db: AsyncSession,
        content_bytes: bytes,
        filename: str,
        content_type: str,
        institute_id: uuid.UUID | None,
        uploaded_by: uuid.UUID | None = None,
    ) -> FileAttachment:
        """
        Validates and stores a file, then creates a FileAttachment metadata record.
        """
        validate_file(content_bytes, filename, content_type)

        backend = get_storage_backend()
        storage_key = await backend.save(content_bytes, filename, content_type)

        attachment = FileAttachment(
            institute_id=institute_id,
            storage_key=storage_key,
            file_name=filename,
            file_size=len(content_bytes),
            content_type=content_type,
            uploaded_by=uploaded_by,
        )
        db.add(attachment)
        await db.flush()
        await db.refresh(attachment)

        logger.info(
            "Uploaded file attachment",
            extra={"attachment_id": str(attachment.id), "storage_key": storage_key, "file_name": filename},
        )
        return attachment

    @staticmethod
    async def get_attachment(
        db: AsyncSession,
        attachment_id: uuid.UUID,
        institute_id: uuid.UUID | None,
    ) -> FileAttachment:
        query = select(FileAttachment).where(FileAttachment.id == attachment_id)
        if institute_id:
            query = query.where(FileAttachment.institute_id == institute_id)
        attachment = await db.scalar(query)
        if not attachment:
            raise NotFoundError(f"Attachment {attachment_id} not found")
        return attachment

    @staticmethod
    async def get_attachment_by_key(
        db: AsyncSession,
        storage_key: str,
    ) -> FileAttachment:
        attachment = await db.scalar(
            select(FileAttachment).where(FileAttachment.storage_key == storage_key)
        )
        if not attachment:
            raise NotFoundError(f"Attachment '{storage_key}' not found")
        return attachment

    @staticmethod
    async def download_file(storage_key: str) -> bytes:
        backend = get_storage_backend()
        return await backend.get(storage_key)

    @staticmethod
    async def delete_attachment(
        db: AsyncSession,
        attachment_id: uuid.UUID,
        institute_id: uuid.UUID | None,
    ) -> None:
        attachment = await StorageService.get_attachment(db, attachment_id, institute_id)
        backend = get_storage_backend()
        await backend.delete(attachment.storage_key)
        await db.delete(attachment)
        await db.flush()
        logger.info("Deleted file attachment", extra={"attachment_id": str(attachment_id)})
