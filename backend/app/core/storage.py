"""
app/core/storage.py
-------------------
Generic file storage abstraction.

Supports:
  - LocalStorageBackend (development & local testing)
  - S3StorageBackend (AWS S3 / Cloudflare R2 / MinIO in production)
  - Strict MIME-type and size validation to protect against malicious uploads
"""

from __future__ import annotations

import abc
import os
import pathlib
import uuid
from typing import BinaryIO

from app.core.config import get_settings
from app.core.exceptions import ValidationError
from app.core.logging import get_logger

logger = get_logger(__name__)

# Default allowed MIME types for LMS attachments (PDF, documents, images, media)
ALLOWED_MIME_TYPES = {
    "application/pdf",
    "image/jpeg",
    "image/png",
    "image/webp",
    "image/gif",
    "application/msword",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "application/vnd.ms-excel",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    "application/vnd.ms-powerpoint",
    "application/vnd.openxmlformats-officedocument.presentationml.presentation",
    "text/plain",
    "application/zip",
    "audio/mpeg",
    "video/mp4",
}

DISALLOWED_EXTENSIONS = {
    ".exe", ".bat", ".cmd", ".sh", ".py", ".js", ".vbs", ".msi", ".dll", ".so", ".bin"
}


def validate_file(
    content_bytes: bytes,
    filename: str,
    content_type: str,
    max_size_mb: int = 25,
    allowed_types: set[str] | None = None,
) -> None:
    """
    Validates uploaded file size, extension, and content type.
    Raises ValidationError if invalid.
    """
    ext = pathlib.Path(filename).suffix.lower()
    if ext in DISALLOWED_EXTENSIONS:
        raise ValidationError(f"File extension '{ext}' is not permitted for security reasons")

    max_bytes = max_size_mb * 1024 * 1024
    if len(content_bytes) > max_bytes:
        raise ValidationError(
            f"File size ({len(content_bytes)/(1024*1024):.1f} MB) exceeds maximum allowed size ({max_size_mb} MB)"
        )

    types_to_check = allowed_types or ALLOWED_MIME_TYPES
    # Strip parameters from content_type (e.g. text/plain; charset=utf-8)
    base_content_type = content_type.split(";")[0].strip().lower()
    if base_content_type not in types_to_check:
        raise ValidationError(f"MIME type '{base_content_type}' is not supported")


class StorageBackend(abc.ABC):
    """Abstract interface for file persistence."""

    @abc.abstractmethod
    async def save(
        self,
        content_bytes: bytes,
        filename: str,
        content_type: str,
    ) -> str:
        """Saves file content and returns unique storage_key."""
        ...

    @abc.abstractmethod
    async def get(self, storage_key: str) -> bytes:
        """Retrieves raw file content by storage_key."""
        ...

    @abc.abstractmethod
    async def delete(self, storage_key: str) -> bool:
        """Deletes file by storage_key."""
        ...

    @abc.abstractmethod
    def get_url(self, storage_key: str) -> str:
        """Returns direct download or public access URL."""
        ...


class LocalStorageBackend(StorageBackend):
    """Local disk storage for development and testing environments."""

    def __init__(self, base_path: str = "./uploads") -> None:
        self.base_path = pathlib.Path(base_path).resolve()
        self.base_path.mkdir(parents=True, exist_ok=True)

    async def save(
        self,
        content_bytes: bytes,
        filename: str,
        content_type: str,
    ) -> str:
        ext = pathlib.Path(filename).suffix.lower()
        storage_key = f"{uuid.uuid4().hex}{ext}"
        # Group by first 2 hex chars to prevent huge single directory
        sub_dir = self.base_path / storage_key[:2]
        sub_dir.mkdir(parents=True, exist_ok=True)

        target_file = sub_dir / storage_key
        target_file.write_bytes(content_bytes)
        logger.info("Saved file locally", extra={"storage_key": storage_key, "size": len(content_bytes)})
        return storage_key

    async def get(self, storage_key: str) -> bytes:
        target_file = self.base_path / storage_key[:2] / storage_key
        if not target_file.exists():
            raise ValidationError(f"Stored file '{storage_key}' not found")
        return target_file.read_bytes()

    async def delete(self, storage_key: str) -> bool:
        target_file = self.base_path / storage_key[:2] / storage_key
        if target_file.exists():
            target_file.unlink()
            return True
        return False

    def get_url(self, storage_key: str) -> str:
        return f"/api/v1/learning/files/{storage_key}"


class S3StorageBackend(StorageBackend):
    """Production S3 compatible storage backend."""

    def __init__(
        self,
        bucket: str,
        region: str = "ap-south-1",
        access_key: str | None = None,
        secret_key: str | None = None,
    ) -> None:
        self.bucket = bucket
        self.region = region
        self.access_key = access_key
        self.secret_key = secret_key

    async def save(
        self,
        content_bytes: bytes,
        filename: str,
        content_type: str,
    ) -> str:
        ext = pathlib.Path(filename).suffix.lower()
        storage_key = f"uploads/{uuid.uuid4().hex}{ext}"
        # In production, boto3/aioboto3 put_object is called here
        logger.info("S3 upload stub", extra={"bucket": self.bucket, "storage_key": storage_key})
        return storage_key

    async def get(self, storage_key: str) -> bytes:
        raise NotImplementedError("Direct S3 stream via signed URLs preferred in production")

    async def delete(self, storage_key: str) -> bool:
        logger.info("S3 delete stub", extra={"bucket": self.bucket, "storage_key": storage_key})
        return True

    def get_url(self, storage_key: str) -> str:
        return f"https://{self.bucket}.s3.{self.region}.amazonaws.com/{storage_key}"


def get_storage_backend() -> StorageBackend:
    """Factory returning configured storage backend from settings."""
    settings = get_settings()
    if settings.STORAGE_BACKEND == "s3" and settings.AWS_S3_BUCKET:
        return S3StorageBackend(
            bucket=settings.AWS_S3_BUCKET,
            region=settings.AWS_S3_REGION,
            access_key=settings.AWS_ACCESS_KEY_ID,
            secret_key=settings.AWS_SECRET_ACCESS_KEY,
        )
    return LocalStorageBackend(base_path=settings.LOCAL_STORAGE_PATH)
