"""
app/services/enquiry_service.py
-------------------------------
Service layer for CRM enquiries and follow-ups.

Key invariants:
  - Scoped by institute_id (multi-tenant).
  - Every stage change or touchpoint appends to EnquiryFollowUp.
  - Soft deletes are respected (deleted_at IS NULL).
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime

from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundError, ValidationError
from app.core.logging import get_logger
from app.models.enquiry import Enquiry, EnquiryFollowUp, EnquiryStage
from app.schemas.enquiry import EnquiryCreate, EnquiryFollowUpCreate, EnquiryUpdate

logger = get_logger(__name__)


class EnquiryService:
    """Manages enquiry lifecycle and follow-up timeline."""

    @staticmethod
    async def create_enquiry(
        db: AsyncSession,
        data: EnquiryCreate,
        institute_id: uuid.UUID | None,
        author_id: uuid.UUID | None = None,
    ) -> Enquiry:
        enquiry = Enquiry(
            institute_id=institute_id,
            student_name=data.student_name,
            student_email=data.student_email,
            student_phone=data.student_phone,
            parent_name=data.parent_name,
            parent_email=data.parent_email,
            parent_phone=data.parent_phone,
            board_id=data.board_id,
            class_id=data.class_id,
            interested_course_id=data.interested_course_id,
            source=data.source,
            stage=EnquiryStage.NEW,
            counsellor_id=data.counsellor_id or author_id,
            follow_up_date=data.follow_up_date,
            remarks=data.remarks,
        )
        db.add(enquiry)
        await db.flush()

        # Add initial timeline entry
        initial_note = EnquiryFollowUp(
            enquiry_id=enquiry.id,
            author_id=author_id,
            stage_before=None,
            stage_after=EnquiryStage.NEW,
            notes=f"Enquiry created via {data.source.value}. {data.remarks or ''}".strip(),
            next_follow_up_date=data.follow_up_date,
        )
        db.add(initial_note)
        await db.flush()
        await db.refresh(enquiry)

        logger.info("Created enquiry", extra={"enquiry_id": str(enquiry.id), "student": enquiry.student_name})
        return enquiry

    @staticmethod
    async def get_enquiry(
        db: AsyncSession,
        enquiry_id: uuid.UUID,
        institute_id: uuid.UUID | None,
    ) -> Enquiry:
        query = select(Enquiry).where(
            Enquiry.id == enquiry_id,
            Enquiry.deleted_at.is_(None),
        )
        if institute_id:
            query = query.where(Enquiry.institute_id == institute_id)
        enquiry = await db.scalar(query)
        if not enquiry:
            raise NotFoundError(f"Enquiry {enquiry_id} not found")
        return enquiry

    @staticmethod
    async def update_enquiry(
        db: AsyncSession,
        enquiry_id: uuid.UUID,
        data: EnquiryUpdate,
        institute_id: uuid.UUID | None,
    ) -> Enquiry:
        enquiry = await EnquiryService.get_enquiry(db, enquiry_id, institute_id)
        update_data = data.model_dump(exclude_unset=True)

        for field, value in update_data.items():
            setattr(enquiry, field, value)

        await db.flush()
        await db.refresh(enquiry)
        logger.info("Updated enquiry", extra={"enquiry_id": str(enquiry_id)})
        return enquiry

    @staticmethod
    async def add_follow_up(
        db: AsyncSession,
        enquiry_id: uuid.UUID,
        data: EnquiryFollowUpCreate,
        author_id: uuid.UUID | None,
        institute_id: uuid.UUID | None,
    ) -> EnquiryFollowUp:
        enquiry = await EnquiryService.get_enquiry(db, enquiry_id, institute_id)

        stage_before = enquiry.stage
        stage_after = data.new_stage or enquiry.stage

        # Update enquiry status & follow up date
        enquiry.stage = stage_after
        if data.next_follow_up_date:
            enquiry.follow_up_date = data.next_follow_up_date

        follow_up = EnquiryFollowUp(
            enquiry_id=enquiry.id,
            author_id=author_id,
            stage_before=stage_before,
            stage_after=stage_after,
            notes=data.notes,
            next_follow_up_date=data.next_follow_up_date,
        )
        db.add(follow_up)
        await db.flush()
        await db.refresh(follow_up)

        logger.info(
            "Added enquiry follow-up",
            extra={
                "enquiry_id": str(enquiry_id),
                "stage_before": stage_before.value,
                "stage_after": stage_after.value,
            },
        )
        return follow_up

    @staticmethod
    async def list_enquiries(
        db: AsyncSession,
        institute_id: uuid.UUID | None,
        stage: EnquiryStage | None = None,
        counsellor_id: uuid.UUID | None = None,
        search: str | None = None,
        skip: int = 0,
        limit: int = 50,
    ) -> tuple[list[Enquiry], int]:
        base_query = select(Enquiry).where(Enquiry.deleted_at.is_(None))
        if institute_id:
            base_query = base_query.where(Enquiry.institute_id == institute_id)
        if stage:
            base_query = base_query.where(Enquiry.stage == stage)
        if counsellor_id:
            base_query = base_query.where(Enquiry.counsellor_id == counsellor_id)
        if search:
            term = f"%{search.strip()}%"
            base_query = base_query.where(
                or_(
                    Enquiry.student_name.ilike(term),
                    Enquiry.parent_name.ilike(term),
                    Enquiry.student_phone.ilike(term),
                    Enquiry.parent_phone.ilike(term),
                )
            )

        total = await db.scalar(select(func.count()).select_from(base_query.subquery())) or 0
        items = (
            await db.scalars(
                base_query.order_by(Enquiry.created_at.desc()).offset(skip).limit(limit)
            )
        ).all()
        return list(items), total

    @staticmethod
    async def list_follow_ups(
        db: AsyncSession,
        enquiry_id: uuid.UUID,
        institute_id: uuid.UUID | None,
    ) -> list[EnquiryFollowUp]:
        await EnquiryService.get_enquiry(db, enquiry_id, institute_id)
        query = (
            select(EnquiryFollowUp)
            .where(EnquiryFollowUp.enquiry_id == enquiry_id)
            .order_by(EnquiryFollowUp.created_at.desc())
        )
        return list((await db.scalars(query)).all())

    @staticmethod
    async def soft_delete_enquiry(
        db: AsyncSession,
        enquiry_id: uuid.UUID,
        institute_id: uuid.UUID | None,
    ) -> None:
        enquiry = await EnquiryService.get_enquiry(db, enquiry_id, institute_id)
        enquiry.deleted_at = datetime.now(UTC)
        await db.flush()
        logger.info("Soft deleted enquiry", extra={"enquiry_id": str(enquiry_id)})
