"""
012_site_content_cms — Dynamic website content management system.

Creates:
  - site_contents table (stores public page content subdivided by page_slug as JSONB)
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "012"
down_revision = "011"
branch_labels = None
depends_on = None


def upgrade() -> None:
    conn = op.get_bind()
    insp = sa.inspect(conn)
    tables = insp.get_table_names()

    if "site_contents" not in tables:
        op.create_table(
            "site_contents",
            sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
            sa.Column("page_slug", sa.String(length=50), nullable=False),
            sa.Column("title", sa.String(length=255), nullable=True),
            sa.Column("description", sa.Text(), nullable=True),
            sa.Column("data", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
            sa.Column("updated_by", sa.String(length=150), nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
            sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
            sa.UniqueConstraint("page_slug", name="uq_site_contents_page_slug"),
        )

    # Ensure index exists safely
    try:
        existing_indexes = [idx["name"] for idx in insp.get_indexes("site_contents")]
    except Exception:
        existing_indexes = []

    if "ix_site_contents_page_slug" not in existing_indexes:
        try:
            op.create_index("ix_site_contents_page_slug", "site_contents", ["page_slug"])
        except Exception:
            pass


def downgrade() -> None:
    conn = op.get_bind()
    insp = sa.inspect(conn)
    tables = insp.get_table_names()
    if "site_contents" in tables:
        try:
            existing_indexes = [idx["name"] for idx in insp.get_indexes("site_contents")]
            if "ix_site_contents_page_slug" in existing_indexes:
                op.drop_index("ix_site_contents_page_slug", table_name="site_contents")
        except Exception:
            pass
        op.drop_table("site_contents")
