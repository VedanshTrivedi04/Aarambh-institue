"""
app/schemas/common.py
---------------------
Shared Pydantic v2 schema building blocks used across all domains.

Provides:
  - PaginationParams  — query-param validator for page/page_size
  - PaginatedResponse — uniform list envelope: {items, total, page, page_size}
  - FilterParams      — base class for search/filter/sort query params
  - StandardResponse  — single-resource wrapper
"""

from __future__ import annotations

from typing import Generic, TypeVar

from fastapi import Query
from pydantic import BaseModel, ConfigDict, field_validator

T = TypeVar("T")


# ---------------------------------------------------------------------------
# Pagination
# ---------------------------------------------------------------------------


class PaginationParams:
    """
    FastAPI dependency for consistent pagination query parameters.

    Usage:
        @router.get("/students")
        async def list_students(pagination: PaginationParams = Depends()):
            offset = (pagination.page - 1) * pagination.page_size
            ...
    """

    def __init__(
        self,
        page: int = Query(default=1, ge=1, description="Page number (1-indexed)"),
        page_size: int = Query(default=20, ge=1, le=100, description="Items per page (max 100)"),
    ) -> None:
        self.page = page
        self.page_size = page_size

    @property
    def offset(self) -> int:
        return (self.page - 1) * self.page_size

    @property
    def limit(self) -> int:
        return self.page_size


class PaginatedResponse(BaseModel, Generic[T]):
    """
    Envelope for every list endpoint.

    Shape:
        {
            "items": [...],
            "total": 142,
            "page": 2,
            "page_size": 20
        }
    """

    model_config = ConfigDict(arbitrary_types_allowed=True)

    items: list[T]
    total: int
    page: int
    page_size: int


# ---------------------------------------------------------------------------
# Filter / sort base (all list endpoints extend this)
# ---------------------------------------------------------------------------


class FilterParams:
    """
    Base class for search/filter/sort query params shared by list endpoints.

    Subclass and add domain-specific filters:

        class StudentFilterParams(FilterParams):
            board_id: UUID | None = Query(None)
            class_id: UUID | None = Query(None)
    """

    def __init__(
        self,
        search: str | None = Query(default=None, description="Full-text search query"),
        sort_by: str | None = Query(default=None, description="Field to sort by"),
        sort_order: str = Query(default="asc", pattern="^(asc|desc)$"),
    ) -> None:
        self.search = search
        self.sort_by = sort_by
        self.sort_order = sort_order


# ---------------------------------------------------------------------------
# Generic response wrappers
# ---------------------------------------------------------------------------


class StandardResponse(BaseModel, Generic[T]):
    """Single-resource response — used for create/update endpoints."""

    data: T
    message: str = "Success"


class MessageResponse(BaseModel):
    """Simple message-only response — used for delete/action endpoints."""

    message: str
