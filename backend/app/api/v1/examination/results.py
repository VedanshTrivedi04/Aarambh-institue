"""
app/api/v1/examination/results.py
---------------------------------
Endpoints for marks entry, student scorecards, rankings, and test analytics.

Endpoints:
  - POST  /examination/tests/{id}/marks                         — Bulk marks entry (Teacher/Admin)
  - GET   /examination/tests/{id}/results                       — Batch results list
  - GET   /examination/tests/{id}/analytics                     — Performance overview & top-10 leaderboard
  - GET   /examination/tests/{id}/my-scorecard                  — Student/Parent views own scorecard
  - GET   /examination/tests/{id}/students/{student_id}/scorecard — Teacher/Admin views individual scorecard
"""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import CurrentUser, get_db, require_role
from app.core.exceptions import ForbiddenError, NotFoundError
from app.models.people import ParentProfile, StudentParent, StudentProfile
from app.schemas.common import StandardResponse
from app.schemas.examination import (
    BulkMarksEntryRequest,
    TestAnalytics,
    TestRead,
    TestResultRead,
    TestScorecard,
)
from app.services import examination_service

_STAFF_OR_TEACHER = ("SUPER_ADMIN", "ADMIN", "MANAGEMENT", "TEACHER")

router = APIRouter(
    prefix="/tests",
    tags=["Examinations — Results & Scorecards"],
)


@router.post(
    "/{id}/marks",
    response_model=StandardResponse[list[TestResultRead]],
    status_code=status.HTTP_200_OK,
    dependencies=[require_role(*_STAFF_OR_TEACHER)],
    summary="Record or update marks in bulk for students (auto-computes rank and percentile)",
)
async def record_bulk_marks(
    id: uuid.UUID,
    body: BulkMarksEntryRequest,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    results = await examination_service.record_bulk_marks(
        db=db,
        institute_id=current_user.institute_id,
        evaluator_user_id=current_user.id,
        test_id=id,
        payload=body,
    )
    items = [_format_result_read(r) for r in results]
    return StandardResponse(
        data=items,
        message=f"Successfully evaluated and ranked {len(items)} student results.",
    )


@router.get(
    "/{id}/results",
    response_model=StandardResponse[list[TestResultRead]],
    summary="List all student results for a test",
)
async def list_test_results(
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
    items = [_format_result_read(r) for r in test.results]
    return StandardResponse(data=items)


@router.get(
    "/{id}/analytics",
    response_model=StandardResponse[TestAnalytics],
    summary="Get performance analytics and leaderboard for a test",
)
async def get_test_analytics(
    id: uuid.UUID,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    analytics = await examination_service.get_test_analytics(
        db=db,
        institute_id=current_user.institute_id,
        test_id=id,
    )
    return StandardResponse(data=analytics)


@router.get(
    "/{id}/my-scorecard",
    response_model=StandardResponse[TestScorecard],
    dependencies=[require_role("STUDENT", "PARENT")],
    summary="Student or parent views their own test scorecard",
)
async def get_my_scorecard(
    id: uuid.UUID,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    # Resolve student_id
    if current_user.role == "STUDENT":
        s_stmt = select(StudentProfile.id).where(StudentProfile.user_id == current_user.id)
        student_id = (await db.execute(s_stmt)).scalar_one_or_none()
        if not student_id:
            raise NotFoundError(f"StudentProfile for user {current_user.id} not found")
    elif current_user.role == "PARENT":
        p_stmt = select(ParentProfile.id).where(ParentProfile.user_id == current_user.id)
        parent_id = (await db.execute(p_stmt)).scalar_one_or_none()
        if not parent_id:
            raise NotFoundError(f"ParentProfile for user {current_user.id} not found")
        sp_stmt = select(StudentParent.student_id).where(StudentParent.parent_id == parent_id)
        student_id = (await db.execute(sp_stmt)).scalars().first()
        if not student_id:
            raise NotFoundError(f"StudentParent link for parent {parent_id} not found")

    else:
        raise ForbiddenError("Only students and parents can use this endpoint.")

    data = await examination_service.get_student_scorecard(
        db=db,
        institute_id=current_user.institute_id,
        test_id=id,
        student_id=student_id,
        requester_role=current_user.role,
    )

    t = data["test"]
    r = data["result"]
    scorecard = TestScorecard(
        test=_format_test_read_simple(t),
        result=_format_result_read(r),
        max_marks=data["max_marks"],
        passing_marks=data["passing_marks"],
        is_passed=data["is_passed"],
        class_highest_marks=data["class_highest_marks"],
        class_average_marks=data["class_average_marks"],
    )
    return StandardResponse(data=scorecard)


@router.get(
    "/{id}/students/{student_id}/scorecard",
    response_model=StandardResponse[TestScorecard],
    dependencies=[require_role(*_STAFF_OR_TEACHER)],
    summary="Teacher/Admin views individual student scorecard",
)
async def get_student_scorecard(
    id: uuid.UUID,
    student_id: uuid.UUID,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    data = await examination_service.get_student_scorecard(
        db=db,
        institute_id=current_user.institute_id,
        test_id=id,
        student_id=student_id,
        requester_role=current_user.role,
    )
    t = data["test"]
    r = data["result"]
    scorecard = TestScorecard(
        test=_format_test_read_simple(t),
        result=_format_result_read(r),
        max_marks=data["max_marks"],
        passing_marks=data["passing_marks"],
        is_passed=data["is_passed"],
        class_highest_marks=data["class_highest_marks"],
        class_average_marks=data["class_average_marks"],
    )
    return StandardResponse(data=scorecard)


def _format_result_read(r) -> TestResultRead:
    if isinstance(r, TestResultRead):
        return r
    name = None
    adm_no = None
    roll_no = None
    if getattr(r, "student", None):
        name = f"{r.student.first_name} {r.student.last_name or ''}".strip()
        adm_no = r.student.admission_number
        roll_no = getattr(r.student, "roll_number", None)


    return TestResultRead(
        id=r.id,
        test_id=r.test_id,
        student_id=r.student_id,
        marks_obtained=r.marks_obtained,
        is_absent=r.is_absent,
        percentage=r.percentage,
        percentile=r.percentile,
        rank=r.rank,
        remarks=r.remarks,
        evaluated_by=r.evaluated_by,
        created_at=r.created_at,
        updated_at=r.updated_at,
        student_name=name,
        admission_number=adm_no,
        roll_number=roll_no,
    )


def _format_test_read_simple(t) -> TestRead:
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
