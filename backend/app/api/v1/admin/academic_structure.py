"""
app/api/v1/admin/academic_structure.py
--------------------------------------
Admin CRUD endpoints for academic structure entities.
All routes require ADMIN or MANAGEMENT role.

Endpoints:
  AcademicYear  POST/GET /years          GET/PUT/DELETE /years/{id}
  Board         POST/GET /boards         GET/PUT         /boards/{id}
  Class         POST/GET /classes        GET/PUT         /classes/{id}
  Stream        POST/GET /streams        GET             /streams/{id}
  Subject       POST/GET /subjects       GET/PUT         /subjects/{id}
  Course        POST/GET /courses        GET/PUT/DELETE  /courses/{id}
  Batch         POST/GET /batches        GET/PUT/DELETE  /batches/{id}
"""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import CurrentUser, get_db, require_role
from app.schemas.academic_structure import (
    AcademicYearCreate,
    AcademicYearRead,
    AcademicYearUpdate,
    BatchCreate,
    BatchRead,
    BatchUpdate,
    BoardCreate,
    BoardRead,
    BoardUpdate,
    ClassCreate,
    ClassRead,
    ClassUpdate,
    CourseCreate,
    CourseRead,
    CourseReadFull,
    CourseUpdate,
    StreamCreate,
    StreamRead,
    StreamUpdate,
    SubjectCreate,
    SubjectRead,
    SubjectUpdate,
)
from app.schemas.common import MessageResponse, PaginatedResponse, StandardResponse
from app.services import academic_structure_service as svc

_ADMIN_ROLES = ("SUPER_ADMIN", "ADMIN", "MANAGEMENT")

router = APIRouter()


# ─────────────────────────────────────────────────────────────────────────────
# AcademicYear
# ─────────────────────────────────────────────────────────────────────────────

@router.post(
    "/years",
    response_model=StandardResponse[AcademicYearRead],
    status_code=status.HTTP_201_CREATED,
    dependencies=[require_role(*_ADMIN_ROLES)],
    summary="Create a new academic year",
)
async def create_academic_year(
    body: AcademicYearCreate,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    year = await svc.create_academic_year(db, body, current_user)
    await db.commit()
    return StandardResponse(data=AcademicYearRead.model_validate(year), message="Academic year created")


@router.get(
    "/years",
    response_model=list[AcademicYearRead],
    summary="List all academic years for the institute",
)
async def list_academic_years(
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    years = await svc.list_academic_years(db, current_user)
    return [AcademicYearRead.model_validate(y) for y in years]


@router.get(
    "/years/{year_id}",
    response_model=AcademicYearRead,
    summary="Get a single academic year",
)
async def get_academic_year(
    year_id: uuid.UUID,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    year = await svc.get_academic_year(db, year_id, current_user)
    return AcademicYearRead.model_validate(year)


@router.put(
    "/years/{year_id}",
    response_model=AcademicYearRead,
    dependencies=[require_role(*_ADMIN_ROLES)],
    summary="Update an academic year",
)
async def update_academic_year(
    year_id: uuid.UUID,
    body: AcademicYearUpdate,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    year = await svc.update_academic_year(db, year_id, body, current_user)
    await db.commit()
    return AcademicYearRead.model_validate(year)


@router.delete(
    "/years/{year_id}",
    response_model=MessageResponse,
    dependencies=[require_role(*_ADMIN_ROLES)],
    summary="Soft-delete an academic year",
)
async def delete_academic_year(
    year_id: uuid.UUID,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    await svc.delete_academic_year(db, year_id, current_user)
    await db.commit()
    return MessageResponse(message="Academic year archived")


# ─────────────────────────────────────────────────────────────────────────────
# Board
# ─────────────────────────────────────────────────────────────────────────────

@router.post(
    "/boards",
    response_model=StandardResponse[BoardRead],
    status_code=status.HTTP_201_CREATED,
    dependencies=[require_role(*_ADMIN_ROLES)],
    summary="Create a new board",
)
async def create_board(
    body: BoardCreate,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    board = await svc.create_board(db, body, current_user)
    await db.commit()
    return StandardResponse(data=BoardRead.model_validate(board), message="Board created")


@router.get("/boards", response_model=list[BoardRead], summary="List boards")
async def list_boards(current_user: CurrentUser, db: AsyncSession = Depends(get_db)):
    boards = await svc.list_boards(db, current_user)
    return [BoardRead.model_validate(b) for b in boards]


@router.get("/boards/{board_id}", response_model=BoardRead, summary="Get a board")
async def get_board(
    board_id: uuid.UUID, current_user: CurrentUser, db: AsyncSession = Depends(get_db)
):
    return BoardRead.model_validate(await svc.get_board(db, board_id, current_user))


@router.put(
    "/boards/{board_id}",
    response_model=BoardRead,
    dependencies=[require_role(*_ADMIN_ROLES)],
    summary="Update a board",
)
async def update_board(
    board_id: uuid.UUID,
    body: BoardUpdate,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    board = await svc.update_board(db, board_id, body, current_user)
    await db.commit()
    return BoardRead.model_validate(board)


# ─────────────────────────────────────────────────────────────────────────────
# SchoolClass
# ─────────────────────────────────────────────────────────────────────────────

@router.post(
    "/classes",
    response_model=StandardResponse[ClassRead],
    status_code=status.HTTP_201_CREATED,
    dependencies=[require_role(*_ADMIN_ROLES)],
    summary="Create a class",
)
async def create_class(
    body: ClassCreate, current_user: CurrentUser, db: AsyncSession = Depends(get_db)
):
    cls = await svc.create_class(db, body, current_user)
    await db.commit()
    return StandardResponse(data=ClassRead.model_validate(cls), message="Class created")


@router.get("/classes", response_model=list[ClassRead], summary="List classes")
async def list_classes(
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
    board_id: uuid.UUID | None = Query(None),
):
    classes = await svc.list_classes(db, current_user, board_id=board_id)
    return [ClassRead.model_validate(c) for c in classes]


@router.get("/classes/{class_id}", response_model=ClassRead, summary="Get a class")
async def get_class(
    class_id: uuid.UUID, current_user: CurrentUser, db: AsyncSession = Depends(get_db)
):
    return ClassRead.model_validate(await svc.get_class(db, class_id, current_user))


@router.put(
    "/classes/{class_id}",
    response_model=ClassRead,
    dependencies=[require_role(*_ADMIN_ROLES)],
    summary="Update a class",
)
async def update_class(
    class_id: uuid.UUID,
    body: ClassUpdate,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    cls = await svc.update_class(db, class_id, body, current_user)
    await db.commit()
    return ClassRead.model_validate(cls)


# ─────────────────────────────────────────────────────────────────────────────
# Stream
# ─────────────────────────────────────────────────────────────────────────────

@router.post(
    "/streams",
    response_model=StandardResponse[StreamRead],
    status_code=status.HTTP_201_CREATED,
    dependencies=[require_role(*_ADMIN_ROLES)],
    summary="Create a stream (11-12 only)",
)
async def create_stream(
    body: StreamCreate, current_user: CurrentUser, db: AsyncSession = Depends(get_db)
):
    stream = await svc.create_stream(db, body, current_user)
    await db.commit()
    return StandardResponse(data=StreamRead.model_validate(stream), message="Stream created")


@router.get("/streams", response_model=list[StreamRead], summary="List streams")
async def list_streams(
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
    class_id: uuid.UUID | None = Query(None),
):
    streams = await svc.list_streams(db, current_user, class_id=class_id)
    return [StreamRead.model_validate(s) for s in streams]


# ─────────────────────────────────────────────────────────────────────────────
# Subject
# ─────────────────────────────────────────────────────────────────────────────

@router.post(
    "/subjects",
    response_model=StandardResponse[SubjectRead],
    status_code=status.HTTP_201_CREATED,
    dependencies=[require_role(*_ADMIN_ROLES)],
    summary="Create a subject",
)
async def create_subject(
    body: SubjectCreate, current_user: CurrentUser, db: AsyncSession = Depends(get_db)
):
    sub = await svc.create_subject(db, body, current_user)
    await db.commit()
    return StandardResponse(data=SubjectRead.model_validate(sub), message="Subject created")


@router.get("/subjects", response_model=list[SubjectRead], summary="List subjects")
async def list_subjects(current_user: CurrentUser, db: AsyncSession = Depends(get_db)):
    subs = await svc.list_subjects(db, current_user)
    return [SubjectRead.model_validate(s) for s in subs]


@router.get("/subjects/{subject_id}", response_model=SubjectRead, summary="Get a subject")
async def get_subject(
    subject_id: uuid.UUID, current_user: CurrentUser, db: AsyncSession = Depends(get_db)
):
    return SubjectRead.model_validate(await svc.get_subject(db, subject_id, current_user))


@router.put(
    "/subjects/{subject_id}",
    response_model=SubjectRead,
    dependencies=[require_role(*_ADMIN_ROLES)],
    summary="Update a subject",
)
async def update_subject(
    subject_id: uuid.UUID,
    body: SubjectUpdate,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    sub = await svc.update_subject(db, subject_id, body, current_user)
    await db.commit()
    return SubjectRead.model_validate(sub)


# ─────────────────────────────────────────────────────────────────────────────
# Course
# ─────────────────────────────────────────────────────────────────────────────

@router.post(
    "/courses",
    response_model=StandardResponse[CourseRead],
    status_code=status.HTTP_201_CREATED,
    dependencies=[require_role(*_ADMIN_ROLES)],
    summary="Create a course",
)
async def create_course(
    body: CourseCreate, current_user: CurrentUser, db: AsyncSession = Depends(get_db)
):
    course = await svc.create_course(db, body, current_user)
    await db.commit()
    return StandardResponse(data=CourseRead.model_validate(course), message="Course created")


@router.get("/courses", response_model=list[CourseRead], summary="List courses")
async def list_courses(
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
    academic_year_id: uuid.UUID | None = Query(None),
    class_id: uuid.UUID | None = Query(None),
):
    courses = await svc.list_courses(db, current_user, academic_year_id, class_id)
    return [CourseRead.model_validate(c) for c in courses]


@router.get("/courses/{course_id}", response_model=CourseReadFull, summary="Get course with subjects")
async def get_course(
    course_id: uuid.UUID, current_user: CurrentUser, db: AsyncSession = Depends(get_db)
):
    course, subjects = await svc.get_course_with_subjects(db, course_id, current_user)
    data = CourseReadFull.model_validate(course)
    data.subjects = [SubjectRead.model_validate(s) for s in subjects]
    return data


@router.put(
    "/courses/{course_id}",
    response_model=CourseRead,
    dependencies=[require_role(*_ADMIN_ROLES)],
    summary="Update a course",
)
async def update_course(
    course_id: uuid.UUID,
    body: CourseUpdate,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    course = await svc.update_course(db, course_id, body, current_user)
    await db.commit()
    return CourseRead.model_validate(course)


@router.delete(
    "/courses/{course_id}",
    response_model=MessageResponse,
    dependencies=[require_role(*_ADMIN_ROLES)],
    summary="Soft-delete a course",
)
async def delete_course(
    course_id: uuid.UUID, current_user: CurrentUser, db: AsyncSession = Depends(get_db)
):
    await svc.delete_course(db, course_id, current_user)
    await db.commit()
    return MessageResponse(message="Course archived")


# ─────────────────────────────────────────────────────────────────────────────
# Batch
# ─────────────────────────────────────────────────────────────────────────────

@router.post(
    "/batches",
    response_model=StandardResponse[BatchRead],
    status_code=status.HTTP_201_CREATED,
    dependencies=[require_role(*_ADMIN_ROLES)],
    summary="Create a batch",
)
async def create_batch(
    body: BatchCreate, current_user: CurrentUser, db: AsyncSession = Depends(get_db)
):
    batch = await svc.create_batch(db, body, current_user)
    await db.commit()
    return StandardResponse(data=BatchRead.model_validate(batch), message="Batch created")


@router.get("/batches", response_model=list[BatchRead], summary="List batches")
async def list_batches(
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
    course_id: uuid.UUID | None = Query(None),
    subject_id: uuid.UUID | None = Query(None),
    teacher_id: uuid.UUID | None = Query(None),
):
    batches = await svc.list_batches(db, current_user, course_id, subject_id, teacher_id)
    return [BatchRead.model_validate(b) for b in batches]


@router.get("/batches/{batch_id}", response_model=BatchRead, summary="Get a batch")
async def get_batch(
    batch_id: uuid.UUID, current_user: CurrentUser, db: AsyncSession = Depends(get_db)
):
    return BatchRead.model_validate(await svc.get_batch(db, batch_id, current_user))


@router.put(
    "/batches/{batch_id}",
    response_model=BatchRead,
    dependencies=[require_role(*_ADMIN_ROLES)],
    summary="Update a batch",
)
async def update_batch(
    batch_id: uuid.UUID,
    body: BatchUpdate,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    batch = await svc.update_batch(db, batch_id, body, current_user)
    await db.commit()
    return BatchRead.model_validate(batch)


@router.delete(
    "/batches/{batch_id}",
    response_model=MessageResponse,
    dependencies=[require_role(*_ADMIN_ROLES)],
    summary="Soft-delete a batch",
)
async def delete_batch(
    batch_id: uuid.UUID, current_user: CurrentUser, db: AsyncSession = Depends(get_db)
):
    await svc.delete_batch(db, batch_id, current_user)
    await db.commit()
    return MessageResponse(message="Batch archived")
