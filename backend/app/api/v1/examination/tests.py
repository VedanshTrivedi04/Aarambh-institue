"""
app/api/v1/examination/tests.py
-------------------------------
Test management, scheduling, question assignment, and result publishing endpoints.

Endpoints:
  - POST   /examination/tests                    — Create test with optional questions (Teacher/Admin)
  - GET    /examination/tests                    — List tests (students/parents see published only)
  - GET    /examination/tests/{id}               — Get test details with question list
  - PATCH  /examination/tests/{id}               — Update test metadata
  - DELETE /examination/tests/{id}               — Soft-delete test
  - POST   /examination/tests/{id}/questions     — Assign/replace questions in test
  - POST   /examination/tests/{id}/publish       — Publish test results (emits audit log)
"""

from __future__ import annotations

import uuid
from datetime import date as Date

from fastapi import APIRouter, Depends, Query, Request, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import CurrentUser, get_db, require_role
from app.models.enrollment import Enrollment, EnrollmentStatus
from app.models.examination import Test, TestQuestion, TestStatus, TestType
from app.models.people import ParentProfile, StudentParent, StudentProfile
from app.schemas.common import MessageResponse, PaginatedResponse, PaginationParams, StandardResponse
from app.schemas.examination import (
    QuestionRead,
    TestCreate,
    TestDetailRead,
    TestQuestionAssign,
    TestQuestionRead,
    TestRead,
    TestUpdate,
)
from app.services import examination_service

_STAFF_OR_TEACHER = ("SUPER_ADMIN", "ADMIN", "MANAGEMENT", "TEACHER")

router = APIRouter(
    prefix="/tests",
    tags=["Examinations — Tests"],
)


@router.post(
    "",
    response_model=StandardResponse[TestDetailRead],
    status_code=status.HTTP_201_CREATED,
    dependencies=[require_role(*_STAFF_OR_TEACHER)],
    summary="Schedule / Create an examination",
)
async def create_test(
    body: TestCreate,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    test = await examination_service.create_test(
        db=db,
        institute_id=current_user.institute_id,
        user_id=current_user.id,
        payload=body,
        branch_id=getattr(current_user, "branch_id", None),
    )

    return StandardResponse(data=_format_test_detail(test))


@router.get(
    "",
    response_model=PaginatedResponse[TestRead],
    summary="List tests with filtering",
)
async def list_tests(
    course_id: uuid.UUID | None = Query(None),
    batch_id: uuid.UUID | None = Query(None),
    subject_id: uuid.UUID | None = Query(None),
    test_status: TestStatus | None = Query(None, alias="status"),
    test_type: TestType | None = Query(None, alias="type"),
    date_from: Date | None = Query(None),
    date_to: Date | None = Query(None),
    pagination: PaginationParams = Depends(),
    current_user: CurrentUser = None,
    db: AsyncSession = Depends(get_db),
):
    is_student_or_parent = current_user.role in ("STUDENT", "PARENT")
    student_batch_ids = None

    if current_user.role == "STUDENT":
        s_stmt = select(StudentProfile.id).where(StudentProfile.user_id == current_user.id)
        student_profile_id = (await db.execute(s_stmt)).scalar_one_or_none()
        if student_profile_id:
            e_stmt = select(Enrollment.batch_id).where(
                Enrollment.student_id == student_profile_id,
                Enrollment.status == EnrollmentStatus.ACTIVE,
            )
            student_batch_ids = list((await db.execute(e_stmt)).scalars().all())
    elif current_user.role == "PARENT":
        p_stmt = select(ParentProfile.id).where(ParentProfile.user_id == current_user.id)
        parent_profile_id = (await db.execute(p_stmt)).scalar_one_or_none()
        if parent_profile_id:
            sp_stmt = select(StudentParent.student_id).where(StudentParent.parent_id == parent_profile_id)
            linked_student_ids = list((await db.execute(sp_stmt)).scalars().all())
            if linked_student_ids:
                e_stmt = select(Enrollment.batch_id).where(
                    Enrollment.student_id.in_(linked_student_ids),
                    Enrollment.status == EnrollmentStatus.ACTIVE,
                )
                student_batch_ids = list((await db.execute(e_stmt)).scalars().all())

    tests, total = await examination_service.list_tests(
        db=db,
        institute_id=current_user.institute_id,
        course_id=course_id,
        batch_id=batch_id,
        subject_id=subject_id,
        status=test_status,
        type=test_type,
        date_from=date_from,
        date_to=date_to,
        limit=pagination.limit,
        offset=pagination.offset,
        for_student_or_parent=is_student_or_parent,
        student_batch_ids=student_batch_ids,
    )
    items = [_format_test_read(t) for t in tests]
    return PaginatedResponse(
        items=items,
        total=total,
        page=pagination.page,
        page_size=pagination.page_size,
    )


@router.get(
    "/{id}",
    response_model=StandardResponse[TestDetailRead],
    summary="Get test details with question list",
)
async def get_test(
    id: uuid.UUID,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    is_student_or_parent = current_user.role in ("STUDENT", "PARENT")
    test = await examination_service.get_test(
        db=db,
        institute_id=current_user.institute_id,
        test_id=id,
        for_student_or_parent=is_student_or_parent,
    )
    return StandardResponse(data=_format_test_detail(test))


@router.patch(
    "/{id}",
    response_model=StandardResponse[TestDetailRead],
    dependencies=[require_role(*_STAFF_OR_TEACHER)],
    summary="Update test details",
)
async def update_test(
    id: uuid.UUID,
    body: TestUpdate,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    test = await examination_service.update_test(
        db=db,
        institute_id=current_user.institute_id,
        test_id=id,
        payload=body,
    )
    return StandardResponse(data=_format_test_detail(test))


@router.delete(
    "/{id}",
    response_model=MessageResponse,
    dependencies=[require_role(*_STAFF_OR_TEACHER)],
    summary="Soft-delete test",
)
async def delete_test(
    id: uuid.UUID,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    await examination_service.delete_test(
        db=db,
        institute_id=current_user.institute_id,
        test_id=id,
    )
    return MessageResponse(message="Test deleted successfully.")


@router.post(
    "/{id}/questions",
    response_model=StandardResponse[TestDetailRead],
    dependencies=[require_role(*_STAFF_OR_TEACHER)],
    summary="Assign / replace questions for a test",
)
async def assign_questions(
    id: uuid.UUID,
    questions: list[TestQuestionAssign],
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    test = await examination_service.assign_questions(
        db=db,
        institute_id=current_user.institute_id,
        test_id=id,
        questions=questions,
    )
    return StandardResponse(data=_format_test_detail(test))


@router.post(
    "/{id}/publish",
    response_model=StandardResponse[TestDetailRead],
    dependencies=[require_role(*_STAFF_OR_TEACHER)],
    summary="Publish test results and notify students/parents (emits audit log)",
)
async def publish_results(
    id: uuid.UUID,
    request: Request,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    test = await examination_service.publish_test_results(
        db=db,
        institute_id=current_user.institute_id,
        user=current_user,
        test_id=id,
        request=request,
    )
    return StandardResponse(
        data=_format_test_detail(test),
        message="Test results published successfully.",
    )


def _format_test_read(t: Test) -> TestRead:
    return TestRead(
        id=t.id,
        institute_id=t.institute_id,
        branch_id=t.branch_id,
        course_id=t.course_id,
        batch_id=t.batch_id,
        subject_id=t.subject_id,
        name=t.name,
        type=t.type,
        date=t.date,
        start_time=t.start_time,
        duration_minutes=t.duration_minutes,
        max_marks=t.max_marks,
        passing_marks=t.passing_marks,
        status=t.status,
        instructions=t.instructions,
        created_by=t.created_by,
        published_at=t.published_at,
        published_by=t.published_by,
        created_at=t.created_at,
        updated_at=t.updated_at,
        course_name=t.course.name if t.course else None,
        batch_name=t.batch.name if t.batch else None,
        subject_name=t.subject.name if t.subject else None,
        question_count=len(t.test_questions) if t.test_questions else 0,
        evaluated_count=len([r for r in t.results if r.marks_obtained is not None or r.is_absent]) if t.results else 0,
    )


def _format_test_detail(t: Test) -> TestDetailRead:
    base = _format_test_read(t)
    tq_reads = []
    if t.test_questions:
        for tq in t.test_questions:
            q_read = None
            if tq.question:
                q = tq.question
                q_read = QuestionRead(
                    id=q.id,
                    institute_id=q.institute_id,
                    branch_id=q.branch_id,
                    board_id=q.board_id,
                    class_id=q.class_id,
                    stream_id=q.stream_id,
                    subject_id=q.subject_id,
                    chapter=q.chapter,
                    topic=q.topic,
                    difficulty=q.difficulty,
                    question_type=q.question_type,
                    body=q.body,
                    options=q.options,
                    correct_answer=q.correct_answer,
                    explanation=q.explanation,
                    default_marks=q.default_marks,
                    created_by=q.created_by,
                    created_at=q.created_at,
                    updated_at=q.updated_at,
                    subject_name=q.subject.name if q.subject else None,
                    class_name=q.school_class.name if q.school_class else None,
                    board_name=q.board.name if q.board else None,
                )
            tq_reads.append(
                TestQuestionRead(
                    id=tq.id,
                    test_id=tq.test_id,
                    question_id=tq.question_id,
                    marks=tq.marks,
                    display_order=tq.display_order,
                    section=tq.section,
                    question=q_read,
                )
            )

    return TestDetailRead(
        **base.model_dump(),
        test_questions=tq_reads,
    )
