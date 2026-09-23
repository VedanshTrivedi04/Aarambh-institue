"""
app/models/institute.py
-----------------------
Institute and Branch ORM models.

An Institute is the root tenant — every piece of data in the system belongs
to exactly one institute (architecture.md §11, systemdesign.md §2).

A Branch is a physical location under an institute.
  Institute ─┬─ Main Branch
             ├─ Vijay Nagar Branch
             └─ Rau Branch

Both tables are multi-branch-aware from day one, meaning even a single-branch
install will have one Institute and one Branch row, and `institute_id` /
`branch_id` on all other models resolve correctly without schema changes later.
"""

from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, CheckConstraint, ForeignKey, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, SoftDeleteMixin, TimestampMixin

if TYPE_CHECKING:
    from app.models.user import User


class Institute(TimestampMixin, SoftDeleteMixin, Base):
    """
    Root tenant entity.

    Rules:
      - `code` is the short unique identifier used in URLs, seed scripts, and
        E2E test fixtures (e.g. "AARAMBH").
      - `deleted_at` signals archiving — all related data is preserved
        (SoftDeleteMixin, rules.md §6).
    """

    __tablename__ = "institutes"
    __table_args__ = (
        UniqueConstraint("code", name="uq_institutes_code"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    code: Mapped[str] = mapped_column(String(50), nullable=False)
    logo_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    address: Mapped[str | None] = mapped_column(Text, nullable=True)
    contact_email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    contact_phone: Mapped[str | None] = mapped_column(String(20), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # Relationships
    branches: Mapped[list["Branch"]] = relationship(
        "Branch", back_populates="institute", lazy="noload"
    )

    def __repr__(self) -> str:
        return f"<Institute id={self.id} code={self.code!r}>"


class Branch(TimestampMixin, SoftDeleteMixin, Base):
    """
    Physical location / branch under an institute.

    `is_main_branch=True` marks the primary branch created during institute
    setup — used as the default when branch_id is not explicitly specified.
    """

    __tablename__ = "branches"
    __table_args__ = (
        UniqueConstraint("institute_id", "code", name="uq_branches_institute_code"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    institute_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("institutes.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    code: Mapped[str] = mapped_column(String(50), nullable=False)
    address: Mapped[str | None] = mapped_column(Text, nullable=True)
    contact_number: Mapped[str | None] = mapped_column(String(20), nullable=True)
    is_main_branch: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # Relationships
    institute: Mapped["Institute"] = relationship(
        "Institute", back_populates="branches", lazy="noload"
    )

    def __repr__(self) -> str:
        return f"<Branch id={self.id} code={self.code!r} institute_id={self.institute_id}>"
