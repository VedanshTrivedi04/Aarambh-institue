"""
app/api/v1/admin/cms.py
-----------------------
Admin endpoints for managing and customizing public website content.
Subdivided page-by-page and stored dynamically in PostgreSQL.
"""

from __future__ import annotations

import datetime
from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.api.deps import CurrentUser, require_role
from app.db.session import get_db
from app.models.cms import SiteContent
from app.schemas.cms import (
    PageContentResponse,
    PageContentUpdate,
    AllSiteContentResponse,
    ResetContentRequest,
)
from app.core.cms_defaults import DEFAULT_SITE_PAGES
from app.core.logging import get_logger

logger = get_logger(__name__)

_ADMIN_ROLES = ("SUPER_ADMIN", "ADMIN", "MANAGEMENT")

router = APIRouter(prefix="/cms", tags=["Admin — Website CMS"])


async def _ensure_cms_table(db: AsyncSession) -> None:
    """Creates the site_contents table if not already created."""
    try:
        from app.db.base import Base
        conn = await db.connection()
        await conn.run_sync(Base.metadata.create_all)
    except Exception as e:
        logger.warning("Auto table verify note: %s", e)


@router.get(
    "/content",
    response_model=AllSiteContentResponse,
    summary="Get all public page configurations for CMS editor",
)
async def get_all_cms_content(db: AsyncSession = Depends(get_db)) -> AllSiteContentResponse:
    """
    Fetches all customizable public pages from the database.
    If any page is missing, it automatically seeds it with canonical default data.
    """
    await _ensure_cms_table(db)

    stmt = select(SiteContent)
    res = await db.execute(stmt)
    records = res.scalars().all()
    existing_map = {r.page_slug: r for r in records}

    latest_updated: datetime.datetime | None = None
    pages_result: dict[str, dict[str, Any]] = {}

    # Seed or return
    needs_commit = False
    for slug, default_data in DEFAULT_SITE_PAGES.items():
        if slug in existing_map:
            row = existing_map[slug]
            pages_result[slug] = row.data
            if row.updated_at and (latest_updated is None or row.updated_at > latest_updated):
                latest_updated = row.updated_at
        else:
            # Seed missing page into database
            new_record = SiteContent(
                page_slug=slug,
                title=slug.replace("_", " ").title(),
                data=default_data,
                updated_by="SYSTEM_DEFAULT",
            )
            db.add(new_record)
            pages_result[slug] = default_data
            needs_commit = True

    if needs_commit:
        await db.commit()

    return AllSiteContentResponse(
        pages=pages_result,
        last_updated=latest_updated or datetime.datetime.now(datetime.timezone.utc),
    )


@router.get(
    "/content/{page_slug}",
    response_model=PageContentResponse,
    summary="Get single page configuration",
)
async def get_page_cms_content(
    page_slug: str,
    db: AsyncSession = Depends(get_db),
) -> PageContentResponse:
    """Fetches configuration for a specific page slug."""
    await _ensure_cms_table(db)

    stmt = select(SiteContent).where(SiteContent.page_slug == page_slug)
    res = await db.execute(stmt)
    record = res.scalar_one_or_none()

    if not record:
        if page_slug in DEFAULT_SITE_PAGES:
            default_data = DEFAULT_SITE_PAGES[page_slug]
            new_record = SiteContent(
                page_slug=page_slug,
                title=page_slug.replace("_", " ").title(),
                data=default_data,
                updated_by="SYSTEM_DEFAULT",
            )
            db.add(new_record)
            await db.commit()
            await db.refresh(new_record)
            return PageContentResponse.model_validate(new_record)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Page slug '{page_slug}' not found.",
        )

    return PageContentResponse.model_validate(record)


@router.put(
    "/content/{page_slug}",
    response_model=PageContentResponse,
    dependencies=[require_role(*_ADMIN_ROLES)],
    summary="Update single page content in database",
)
async def update_page_cms_content(
    page_slug: str,
    payload: PageContentUpdate,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
) -> PageContentResponse:
    """Updates the JSON configuration for a specific public page in PostgreSQL."""
    await _ensure_cms_table(db)

    stmt = select(SiteContent).where(SiteContent.page_slug == page_slug)
    res = await db.execute(stmt)
    record = res.scalar_one_or_none()

    if not record:
        record = SiteContent(
            page_slug=page_slug,
            title=payload.title or page_slug.replace("_", " ").title(),
            description=payload.description,
            data=payload.data,
            updated_by=payload.updated_by or current_user.email,
        )
        db.add(record)
    else:
        if payload.title is not None:
            record.title = payload.title
        if payload.description is not None:
            record.description = payload.description
        record.data = payload.data
        record.updated_by = payload.updated_by or current_user.email

    await db.commit()
    await db.refresh(record)
    logger.info("Admin updated CMS content for page: %s", page_slug)
    return PageContentResponse.model_validate(record)


@router.post(
    "/content/reset",
    dependencies=[require_role(*_ADMIN_ROLES)],
    summary="Reset page(s) to institute canonical defaults",
)
async def reset_cms_content(
    payload: ResetContentRequest,
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """Resets either a specific page slug or all pages back to canonical default data."""
    await _ensure_cms_table(db)

    target_slug = payload.page_slug
    if target_slug:
        if target_slug not in DEFAULT_SITE_PAGES:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Unknown page slug '{target_slug}'",
            )
        stmt = select(SiteContent).where(SiteContent.page_slug == target_slug)
        res = await db.execute(stmt)
        record = res.scalar_one_or_none()
        if record:
            record.data = DEFAULT_SITE_PAGES[target_slug]
            record.updated_by = "ADMIN_RESET"
        else:
            db.add(
                SiteContent(
                    page_slug=target_slug,
                    title=target_slug.replace("_", " ").title(),
                    data=DEFAULT_SITE_PAGES[target_slug],
                    updated_by="ADMIN_RESET",
                )
            )
        await db.commit()
        return {"success": True, "message": f"Reset '{target_slug}' to defaults."}

    # Reset all
    for slug, default_data in DEFAULT_SITE_PAGES.items():
        stmt = select(SiteContent).where(SiteContent.page_slug == slug)
        res = await db.execute(stmt)
        record = res.scalar_one_or_none()
        if record:
            record.data = default_data
            record.updated_by = "ADMIN_RESET_ALL"
        else:
            db.add(
                SiteContent(
                    page_slug=slug,
                    title=slug.replace("_", " ").title(),
                    data=default_data,
                    updated_by="ADMIN_RESET_ALL",
                )
            )
    await db.commit()
    return {"success": True, "message": "All pages reset to defaults."}
