"""
app/api/v1/learning/homework.py
-------------------------------
Homework assignments, student submissions, and teacher evaluation endpoints.

Endpoints:
  POST /homework                                  — Create homework assignment (Teacher/Admin)
  GET  /homework/batch/{batch_id}                 — List homework assignments for a batch
  GET  /homework/{id}                             — Get homework assignment details
  PATCH /homework/{id}                            — Update homework
  DELETE /homework/{id}                           — Soft-delete homework
  POST /homework/{id}/submit                      — Student submits homework
  GET  /homework/{id}/my-submission               — Student views their submission
  GET  /homework/{id}/submissions                 — Teacher views all student submissions
  POST /homework/submissions/{id}/evaluate        — Teacher grades submission
"""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import CurrentUser, get_db, require_role
from app.core.exceptions import ForbiddenError, NotFoundError
from app.models.people import StudentProfile
from app.schemas.common import MessageResponse, PaginatedResponse, StandardResponse
from app.schemas.learning import (
    HomeworkCreate,
    HomeworkEvaluationRequest,
    HomeworkRead,
    HomeworkSubmissionCreate,
    HomeworkSubmissionRead,
    HomeworkUpdate,
)
from app.services.learning_service import LearningService
from app.services.people_service import PeopleService

_STAFF_OR_TEACHER = ("SUPER_ADMIN", "ADMIN", "MANAGEMENT", "TEACHER")

router = APIRouter(
    prefix="/homework",
    tags=["Learning - Homework"],
)


@router.post(
    "",
    response_model=StandardResponse[HomeworkRead],
    status_code=status.HTTP_201_CREATED,
    dependencies=[require_role(*_STAFF_OR_TEACHER)],
    summary="Assign new homework to a batch",
)
async def create_homework(
    body: HomeworkCreate,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    hw = await LearningService.create_homework(
        db, body, current_user.institute_id, created_by=current_user.id
    )
    await db.commit()
    return StandardResponse(
        data=HomeworkRead.model_validate(hw),
        message="Homework assigned successfully",
    )


@router.get(
    "/batch/{batch_id}",
    response_model=PaginatedResponse[HomeworkRead],
    summary="List homework assignments for a batch",
)
async def list_batch_homework(
    batch_id: uuid.UUID,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
):
    skip = (page - 1) * page_size
    items, total = await LearningService.list_batch_homework(
        db, batch_id, current_user.institute_id, skip=skip, limit=page_size
    )
    return PaginatedResponse(
        items=[HomeworkRead.model_validate(h) for h in items],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get(
    "/{homework_id}",
    response_model=StandardResponse[HomeworkRead],
    summary="Get single homework assignment details",
)
async def get_homework(
    homework_id: uuid.UUID,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    hw = await LearningService.get_homework(
        db, homework_id, current_user.institute_id
    )
    return StandardResponse(data=HomeworkRead.model_validate(hw))


@router.patch(
    "/{homework_id}",
    response_model=StandardResponse[HomeworkRead],
    dependencies=[require_role(*_STAFF_OR_TEACHER)],
    summary="Update homework assignment",
)
async def update_homework(
    homework_id: uuid.UUID,
    body: HomeworkUpdate,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    hw = await LearningService.update_homework(
        db, homework_id, body, current_user.institute_id
    )
    await db.commit()
    return StandardResponse(
        data=HomeworkRead.model_validate(hw),
        message="Homework updated",
    )


@router.delete(
    "/{homework_id}",
    response_model=MessageResponse,
    dependencies=[require_role(*_STAFF_OR_TEACHER)],
    summary="Soft-delete homework assignment",
)
async def delete_homework(
    homework_id: uuid.UUID,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    await LearningService.soft_delete_homework(
        db, homework_id, current_user.institute_id
    )
    await db.commit()
    return MessageResponse(message="Homework deleted")


# ─── Student Submission Endpoints ─────────────────────────────────────────────

@router.post(
    "/{homework_id}/submit",
    response_model=StandardResponse[HomeworkSubmissionRead],
    status_code=status.HTTP_201_CREATED,
    dependencies=[require_role("STUDENT")],
    summary="Student submits their homework work",
)
async def submit_homework(
    homework_id: uuid.UUID,
    body: HomeworkSubmissionCreate,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    submission = await LearningService.submit_homework(
        db, homework_id, current_user, body
    )
    await db.commit()
    return StandardResponse(
        data=HomeworkSubmissionRead.model_validate(submission),
        message="Homework submitted successfully",
    )


@router.get(
    "/{homework_id}/my-submission",
    response_model=StandardResponse[HomeworkSubmissionRead],
    dependencies=[require_role("STUDENT")],
    summary="Student views their own homework submission",
)
async def get_my_submission(
    homework_id: uuid.UUID,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    student = await PeopleService.get_student_by_user_id(db, current_user.id, current_user.institute_id)
    if not student:
        raise NotFoundError("Student profile not found")

    submission = await LearningService.get_student_submission(db, homework_id, student.id)
    if not submission:
        raise NotFoundError("No submission found for this homework")
    return StandardResponse(data=HomeworkSubmissionRead.model_validate(submission))


@router.get(
    "/{homework_id}/submissions",
    response_model=list[HomeworkSubmissionRead],
    dependencies=[require_role(*_STAFF_OR_TEACHER)],
    summary="Teacher/Admin views all student submissions for an assignment",
)
async def list_homework_submissions(
    homework_id: uuid.UUID,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    await LearningService.get_homework(db, homework_id, current_user.institute_id)
    submissions = await LearningService.list_homework_submissions(db, homework_id)
    return [HomeworkSubmissionRead.model_validate(s) for s in submissions]


@router.post(
    "/submissions/{submission_id}/evaluate",
    response_model=StandardResponse[HomeworkSubmissionRead],
    dependencies=[require_role(*_STAFF_OR_TEACHER)],
    summary="Teacher grades and gives feedback on a student submission",
)
async def evaluate_submission(
    submission_id: uuid.UUID,
    body: HomeworkEvaluationRequest,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    submission = await LearningService.evaluate_submission(
        db, submission_id, body, current_user
    )
    await db.commit()
    return StandardResponse(
        data=HomeworkSubmissionRead.model_validate(submission),
        message="Submission evaluated successfully",
    )
