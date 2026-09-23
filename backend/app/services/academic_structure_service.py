"""
app/services/academic_structure_service.py
-------------------------------------------
Service layer for all academic-structure entities.

Architecture (backend.md §3):
  - Services receive an AsyncSession and typed domain objects.
  - Services own transaction boundaries (db.begin()) — routers commit.
  - Every query is scoped by institute_id (TenantAwareMixin policy).
  - Cross-tenant access raises CrossTenantAccessError.
  - Domain errors are raised as typed AppException subclasses — never HTTPException.

RBAC at service level:
  - Mutating operations (create/update/delete/activate) require ADMIN or MANAGEMENT role.
  - Read operations are accessible to all authenticated users within the tenant.
  - Services check `actor.institute_id == resource.institute_id` (ReBAC).
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from typing import Any

from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.exceptions import (
    ConflictError,
    CrossTenantAccessError,
    ForbiddenError,
    NotFoundError,
    ValidationError,
)
from app.core.logging import get_logger
from app.models.academic_structure import (
    AcademicYear,
    Batch,
    Board,
    Course,
    CourseSubject,
    SchoolClass,
    Stream,
    Subject,
)
from app.models.user import User
from app.schemas.academic_structure import (
    AcademicYearCreate,
    AcademicYearUpdate,
    BatchCreate,
    BatchUpdate,
    BoardCreate,
    BoardUpdate,
    ClassCreate,
    ClassUpdate,
    CourseCreate,
    CourseUpdate,
    StreamCreate,
    StreamUpdate,
    SubjectCreate,
    SubjectUpdate,
)

logger = get_logger(__name__)

_ADMIN_ROLES = {"SUPER_ADMIN", "ADMIN", "MANAGEMENT"}


def _assert_admin(actor: User) -> None:
    if actor.role not in _ADMIN_ROLES:
        raise ForbiddenError("This action requires ADMIN or MANAGEMENT role")


def _assert_tenant(resource_institute_id: uuid.UUID | None, actor: User) -> None:
    if resource_institute_id and actor.institute_id != resource_institute_id:
        raise CrossTenantAccessError("Access denied: cross-tenant resource")


# ─────────────────────────────────────────────────────────────────────────────
# AcademicYear
# ─────────────────────────────────────────────────────────────────────────────

async def create_academic_year(
    db: AsyncSession, payload: AcademicYearCreate, actor: User
) -> AcademicYear:
    _assert_admin(actor)

    # Unique name within institute
    existing = await db.execute(
        select(AcademicYear).where(
            AcademicYear.institute_id == actor.institute_id,
            AcademicYear.name == payload.name,
            AcademicYear.deleted_at.is_(None),
        )
    )
    if existing.scalar_one_or_none():
        raise ConflictError(f"Academic year '{payload.name}' already exists")

    # If marking as current, unset others first
    if payload.is_current:
        await db.execute(
            update(AcademicYear)
            .where(
                AcademicYear.institute_id == actor.institute_id,
                AcademicYear.is_current.is_(True),
            )
            .values(is_current=False)
        )

    year = AcademicYear(
        institute_id=actor.institute_id,
        **payload.model_dump(),
    )
    db.add(year)
    await db.flush()
    logger.info("AcademicYear created", id=str(year.id), name=year.name)
    return year


async def list_academic_years(db: AsyncSession, actor: User) -> list[AcademicYear]:
    result = await db.execute(
        select(AcademicYear)
        .where(
            AcademicYear.institute_id == actor.institute_id,
            AcademicYear.deleted_at.is_(None),
        )
        .order_by(AcademicYear.start_date.desc())
    )
    return list(result.scalars().all())


async def get_academic_year(db: AsyncSession, year_id: uuid.UUID, actor: User) -> AcademicYear:
    result = await db.execute(
        select(AcademicYear).where(
            AcademicYear.id == year_id,
            AcademicYear.deleted_at.is_(None),
        )
    )
    year = result.scalar_one_or_none()
    if not year:
        raise NotFoundError(f"Academic year {year_id} not found")
    _assert_tenant(year.institute_id, actor)
    return year


async def update_academic_year(
    db: AsyncSession, year_id: uuid.UUID, payload: AcademicYearUpdate, actor: User
) -> AcademicYear:
    _assert_admin(actor)
    year = await get_academic_year(db, year_id, actor)

    if payload.is_current is True:
        await db.execute(
            update(AcademicYear)
            .where(
                AcademicYear.institute_id == actor.institute_id,
                AcademicYear.id != year_id,
            )
            .values(is_current=False)
        )

    for field, value in payload.model_dump(exclude_none=True).items():
        setattr(year, field, value)
    await db.flush()
    return year


async def delete_academic_year(db: AsyncSession, year_id: uuid.UUID, actor: User) -> None:
    _assert_admin(actor)
    year = await get_academic_year(db, year_id, actor)
    year.soft_delete()
    await db.flush()


# ─────────────────────────────────────────────────────────────────────────────
# Board
# ─────────────────────────────────────────────────────────────────────────────

async def create_board(db: AsyncSession, payload: BoardCreate, actor: User) -> Board:
    _assert_admin(actor)
    existing = await db.execute(
        select(Board).where(
            Board.institute_id == actor.institute_id,
            Board.code == payload.code,
        )
    )
    if existing.scalar_one_or_none():
        raise ConflictError(f"Board with code '{payload.code}' already exists")

    board = Board(institute_id=actor.institute_id, **payload.model_dump())
    db.add(board)
    await db.flush()
    return board


async def list_boards(db: AsyncSession, actor: User) -> list[Board]:
    result = await db.execute(
        select(Board).where(
            Board.institute_id == actor.institute_id,
            Board.is_active.is_(True),
        )
    )
    return list(result.scalars().all())


async def get_board(db: AsyncSession, board_id: uuid.UUID, actor: User) -> Board:
    result = await db.execute(select(Board).where(Board.id == board_id))
    board = result.scalar_one_or_none()
    if not board:
        raise NotFoundError(f"Board {board_id} not found")
    _assert_tenant(board.institute_id, actor)
    return board


async def update_board(
    db: AsyncSession, board_id: uuid.UUID, payload: BoardUpdate, actor: User
) -> Board:
    _assert_admin(actor)
    board = await get_board(db, board_id, actor)
    for field, value in payload.model_dump(exclude_none=True).items():
        setattr(board, field, value)
    await db.flush()
    return board


# ─────────────────────────────────────────────────────────────────────────────
# SchoolClass
# ─────────────────────────────────────────────────────────────────────────────

async def create_class(db: AsyncSession, payload: ClassCreate, actor: User) -> SchoolClass:
    _assert_admin(actor)
    board = await get_board(db, payload.board_id, actor)

    existing = await db.execute(
        select(SchoolClass).where(
            SchoolClass.board_id == payload.board_id,
            SchoolClass.name == payload.name,
        )
    )
    if existing.scalar_one_or_none():
        raise ConflictError(f"Class '{payload.name}' already exists for this board")

    cls = SchoolClass(institute_id=actor.institute_id, **payload.model_dump())
    db.add(cls)
    await db.flush()
    return cls


async def list_classes(
    db: AsyncSession, actor: User, board_id: uuid.UUID | None = None
) -> list[SchoolClass]:
    stmt = select(SchoolClass).where(
        SchoolClass.institute_id == actor.institute_id,
        SchoolClass.is_active.is_(True),
    )
    if board_id:
        stmt = stmt.where(SchoolClass.board_id == board_id)
    stmt = stmt.order_by(SchoolClass.display_order)
    result = await db.execute(stmt)
    return list(result.scalars().all())


async def get_class(db: AsyncSession, class_id: uuid.UUID, actor: User) -> SchoolClass:
    result = await db.execute(select(SchoolClass).where(SchoolClass.id == class_id))
    cls = result.scalar_one_or_none()
    if not cls:
        raise NotFoundError(f"Class {class_id} not found")
    _assert_tenant(cls.institute_id, actor)
    return cls


async def update_class(
    db: AsyncSession, class_id: uuid.UUID, payload: ClassUpdate, actor: User
) -> SchoolClass:
    _assert_admin(actor)
    cls = await get_class(db, class_id, actor)
    for field, value in payload.model_dump(exclude_none=True).items():
        setattr(cls, field, value)
    await db.flush()
    return cls


# ─────────────────────────────────────────────────────────────────────────────
# Stream
# ─────────────────────────────────────────────────────────────────────────────

async def create_stream(db: AsyncSession, payload: StreamCreate, actor: User) -> Stream:
    _assert_admin(actor)
    await get_class(db, payload.class_id, actor)  # validates tenant + existence

    existing = await db.execute(
        select(Stream).where(
            Stream.class_id == payload.class_id,
            Stream.name == payload.name,
        )
    )
    if existing.scalar_one_or_none():
        raise ConflictError(f"Stream '{payload.name}' already exists for this class")

    stream = Stream(institute_id=actor.institute_id, **payload.model_dump())
    db.add(stream)
    await db.flush()
    return stream


async def list_streams(
    db: AsyncSession, actor: User, class_id: uuid.UUID | None = None
) -> list[Stream]:
    stmt = select(Stream).where(Stream.institute_id == actor.institute_id)
    if class_id:
        stmt = stmt.where(Stream.class_id == class_id)
    result = await db.execute(stmt)
    return list(result.scalars().all())


async def get_stream(db: AsyncSession, stream_id: uuid.UUID, actor: User) -> Stream:
    result = await db.execute(select(Stream).where(Stream.id == stream_id))
    stream = result.scalar_one_or_none()
    if not stream:
        raise NotFoundError(f"Stream {stream_id} not found")
    _assert_tenant(stream.institute_id, actor)
    return stream


# ─────────────────────────────────────────────────────────────────────────────
# Subject
# ─────────────────────────────────────────────────────────────────────────────

async def create_subject(db: AsyncSession, payload: SubjectCreate, actor: User) -> Subject:
    _assert_admin(actor)
    existing = await db.execute(
        select(Subject).where(
            Subject.institute_id == actor.institute_id,
            Subject.code == payload.code,
        )
    )
    if existing.scalar_one_or_none():
        raise ConflictError(f"Subject with code '{payload.code}' already exists")

    subject = Subject(institute_id=actor.institute_id, **payload.model_dump())
    db.add(subject)
    await db.flush()
    return subject


async def list_subjects(db: AsyncSession, actor: User) -> list[Subject]:
    result = await db.execute(
        select(Subject).where(
            Subject.institute_id == actor.institute_id,
            Subject.is_active.is_(True),
        ).order_by(Subject.name)
    )
    return list(result.scalars().all())


async def get_subject(db: AsyncSession, subject_id: uuid.UUID, actor: User) -> Subject:
    result = await db.execute(select(Subject).where(Subject.id == subject_id))
    sub = result.scalar_one_or_none()
    if not sub:
        raise NotFoundError(f"Subject {subject_id} not found")
    _assert_tenant(sub.institute_id, actor)
    return sub


async def update_subject(
    db: AsyncSession, subject_id: uuid.UUID, payload: SubjectUpdate, actor: User
) -> Subject:
    _assert_admin(actor)
    sub = await get_subject(db, subject_id, actor)
    for field, value in payload.model_dump(exclude_none=True).items():
        setattr(sub, field, value)
    await db.flush()
    return sub


# ─────────────────────────────────────────────────────────────────────────────
# Course
# ─────────────────────────────────────────────────────────────────────────────

async def create_course(db: AsyncSession, payload: CourseCreate, actor: User) -> Course:
    _assert_admin(actor)

    # Validate FK references belong to this tenant
    await get_class(db, payload.class_id, actor)
    if payload.stream_id:
        await get_stream(db, payload.stream_id, actor)

    existing = await db.execute(
        select(Course).where(
            Course.institute_id == actor.institute_id,
            Course.academic_year_id == payload.academic_year_id,
            Course.code == payload.code,
            Course.deleted_at.is_(None),
        )
    )
    if existing.scalar_one_or_none():
        raise ConflictError(f"Course with code '{payload.code}' already exists in this academic year")

    subject_ids = payload.subject_ids
    create_data = payload.model_dump(exclude={"subject_ids"})
    course = Course(institute_id=actor.institute_id, **create_data)
    db.add(course)
    await db.flush()   # get course.id

    # Build CourseSubject rows
    for sid in subject_ids:
        await get_subject(db, sid, actor)  # validate each subject
        cs = CourseSubject(course_id=course.id, subject_id=sid)
        db.add(cs)

    await db.flush()
    logger.info("Course created", id=str(course.id), code=course.code)
    return course


async def list_courses(
    db: AsyncSession,
    actor: User,
    academic_year_id: uuid.UUID | None = None,
    class_id: uuid.UUID | None = None,
) -> list[Course]:
    stmt = select(Course).where(
        Course.institute_id == actor.institute_id,
        Course.deleted_at.is_(None),
    )
    if academic_year_id:
        stmt = stmt.where(Course.academic_year_id == academic_year_id)
    if class_id:
        stmt = stmt.where(Course.class_id == class_id)
    result = await db.execute(stmt.order_by(Course.name))
    return list(result.scalars().all())


async def get_course(db: AsyncSession, course_id: uuid.UUID, actor: User) -> Course:
    result = await db.execute(
        select(Course).where(Course.id == course_id, Course.deleted_at.is_(None))
    )
    course = result.scalar_one_or_none()
    if not course:
        raise NotFoundError(f"Course {course_id} not found")
    _assert_tenant(course.institute_id, actor)
    return course


async def get_course_with_subjects(
    db: AsyncSession, course_id: uuid.UUID, actor: User
) -> tuple[Course, list[Subject]]:
    course = await get_course(db, course_id, actor)
    cs_result = await db.execute(
        select(CourseSubject)
        .where(CourseSubject.course_id == course_id)
        .options(selectinload(CourseSubject.subject))
    )
    subjects = [cs.subject for cs in cs_result.scalars().all()]
    return course, subjects


async def update_course(
    db: AsyncSession, course_id: uuid.UUID, payload: CourseUpdate, actor: User
) -> Course:
    _assert_admin(actor)
    course = await get_course(db, course_id, actor)

    if payload.subject_ids is not None:
        # Replace course subjects entirely
        existing_cs = await db.execute(
            select(CourseSubject).where(CourseSubject.course_id == course_id)
        )
        for cs in existing_cs.scalars().all():
            await db.delete(cs)
        for sid in payload.subject_ids:
            await get_subject(db, sid, actor)
            db.add(CourseSubject(course_id=course_id, subject_id=sid))

    update_data = payload.model_dump(exclude_none=True, exclude={"subject_ids"})
    for field, value in update_data.items():
        setattr(course, field, value)

    await db.flush()
    return course


async def delete_course(db: AsyncSession, course_id: uuid.UUID, actor: User) -> None:
    _assert_admin(actor)
    course = await get_course(db, course_id, actor)
    course.soft_delete()
    await db.flush()


# ─────────────────────────────────────────────────────────────────────────────
# Batch
# ─────────────────────────────────────────────────────────────────────────────

async def create_batch(db: AsyncSession, payload: BatchCreate, actor: User) -> Batch:
    _assert_admin(actor)
    await get_course(db, payload.course_id, actor)
    await get_subject(db, payload.subject_id, actor)

    existing = await db.execute(
        select(Batch).where(
            Batch.institute_id == actor.institute_id,
            Batch.name == payload.name,
            Batch.deleted_at.is_(None),
        )
    )
    if existing.scalar_one_or_none():
        raise ConflictError(f"Batch named '{payload.name}' already exists in this institute")

    batch = Batch(
        institute_id=actor.institute_id,
        branch_id=actor.branch_id,
        **payload.model_dump(),
    )
    db.add(batch)
    await db.flush()
    logger.info("Batch created", id=str(batch.id), name=batch.name)
    return batch


async def list_batches(
    db: AsyncSession,
    actor: User,
    course_id: uuid.UUID | None = None,
    subject_id: uuid.UUID | None = None,
    teacher_id: uuid.UUID | None = None,
) -> list[Batch]:
    stmt = select(Batch).where(
        Batch.institute_id == actor.institute_id,
        Batch.deleted_at.is_(None),
    )
    if course_id:
        stmt = stmt.where(Batch.course_id == course_id)
    if subject_id:
        stmt = stmt.where(Batch.subject_id == subject_id)
    if teacher_id:
        stmt = stmt.where(Batch.teacher_id == teacher_id)
    result = await db.execute(stmt.order_by(Batch.name))
    return list(result.scalars().all())


async def get_batch(db: AsyncSession, batch_id: uuid.UUID, actor: User) -> Batch:
    result = await db.execute(
        select(Batch).where(Batch.id == batch_id, Batch.deleted_at.is_(None))
    )
    batch = result.scalar_one_or_none()
    if not batch:
        raise NotFoundError(f"Batch {batch_id} not found")
    _assert_tenant(batch.institute_id, actor)
    return batch


async def update_batch(
    db: AsyncSession, batch_id: uuid.UUID, payload: BatchUpdate, actor: User
) -> Batch:
    _assert_admin(actor)
    batch = await get_batch(db, batch_id, actor)
    for field, value in payload.model_dump(exclude_none=True).items():
        setattr(batch, field, value)
    await db.flush()
    return batch


async def delete_batch(db: AsyncSession, batch_id: uuid.UUID, actor: User) -> None:
    _assert_admin(actor)
    batch = await get_batch(db, batch_id, actor)
    batch.soft_delete()
    await db.flush()
