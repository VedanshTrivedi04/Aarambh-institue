"""
app/models/cms.py
-----------------
ORM model for dynamic website content management (CMS).
Stores public page configurations in PostgreSQL as JSONB.
"""

from __future__ import annotations

import uuid
from typing import Any

from sqlalchemy import String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.types import JSON
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, TimestampMixin


class SiteContent(TimestampMixin, Base):
    """
    Website page content section storage.
    
    Each record represents one public page or bundle section:
    - 'home'
    - 'about'
    - 'courses'
    - 'faculty'
    - 'results'
    - 'admissions'
    - 'contact'
    - 'student_corner'
    - 'landing_bundle' (full snapshot cache)
    """

    __tablename__ = "site_contents"
    __table_args__ = (
        UniqueConstraint("page_slug", name="uq_site_contents_page_slug"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    page_slug: Mapped[str] = mapped_column(
        String(50), nullable=False, unique=True, index=True
    )
    title: Mapped[str | None] = mapped_column(String(255), nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    
    # Store JSON configuration
    data: Mapped[dict[str, Any]] = mapped_column(
        JSONB().with_variant(JSON, "sqlite"),
        nullable=False,
        default=dict,
    )
    updated_by: Mapped[str | None] = mapped_column(String(150), nullable=True)

    def __repr__(self) -> str:
        return f"<SiteContent id={self.id} page_slug={self.page_slug!r}>"
