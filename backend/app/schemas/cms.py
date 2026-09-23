"""
app/schemas/cms.py
------------------
Pydantic schemas for the Admin CMS and Dynamic Website Content.
"""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any
from pydantic import BaseModel, Field


class PageContentResponse(BaseModel):
    id: uuid.UUID | None = None
    page_slug: str
    title: str | None = None
    description: str | None = None
    data: dict[str, Any]
    updated_at: datetime | None = None
    updated_by: str | None = None

    class Config:
        from_attributes = True


class PageContentUpdate(BaseModel):
    title: str | None = Field(None, description="Optional title or label for the section")
    description: str | None = Field(None, description="Optional internal note or description")
    data: dict[str, Any] = Field(..., description="JSON configuration payload for the section")
    updated_by: str | None = Field(None, description="Identifier of the admin who updated the page")


class AllSiteContentResponse(BaseModel):
    pages: dict[str, dict[str, Any]]
    last_updated: datetime | None = None


class ResetContentRequest(BaseModel):
    page_slug: str | None = Field(None, description="Page slug to reset, or omit to reset all pages")
