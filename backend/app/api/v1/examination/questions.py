"""
app/api/v1/examination/questions.py
-----------------------------------
Question Bank endpoints for Aarambh ERP:
  - POST   /examination/questions       — Create question (Teacher/Admin)
  - GET    /examination/questions       — Filter & search questions
  - GET    /examination/questions/{id}  — View question detail
  - PATCH  /examination/questions/{id}  — Update question
  - DELETE /examination/questions/{id}  — Soft-delete question
"""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import CurrentUser, get_db, require_role
from app.models.examination import QuestionDifficulty, QuestionType
from app.schemas.common import MessageResponse, PaginatedResponse, PaginationParams, StandardResponse
from app.schemas.examination import QuestionCreate, QuestionRead, QuestionUpdate
from app.services import examination_service

_STAFF_OR_TEACHER = ("SUPER_ADMIN", "ADMIN", "MANAGEMENT", "TEACHER")

router = APIRouter(
    prefix="/questions",
    tags=["Examinations — Question Bank"],
)


@router.post(
    "",
    response_model=StandardResponse[QuestionRead],
    status_code=status.HTTP_201_CREATED,
    dependencies=[require_role(*_STAFF_OR_TEACHER)],
    summary="Add question to the question bank",
)
async def create_question(
    body: QuestionCreate,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    question = await examination_service.create_question(
        db=db,
        institute_id=current_user.institute_id,
        user_id=current_user.id,
        payload=body,
        branch_id=getattr(current_user, "branch_id", None),
    )

    return StandardResponse(data=_format_question_read(question))


@router.get(
    "",
    response_model=PaginatedResponse[QuestionRead],
    dependencies=[require_role(*_STAFF_OR_TEACHER)],
    summary="List and filter question bank items",
)
async def list_questions(
    subject_id: uuid.UUID | None = Query(None),
    board_id: uuid.UUID | None = Query(None),
    class_id: uuid.UUID | None = Query(None),
    difficulty: QuestionDifficulty | None = Query(None),
    question_type: QuestionType | None = Query(None),
    chapter: str | None = Query(None),
    search: str | None = Query(None),
    pagination: PaginationParams = Depends(),
    current_user: CurrentUser = None,
    db: AsyncSession = Depends(get_db),
):
    questions, total = await examination_service.list_questions(
        db=db,
        institute_id=current_user.institute_id,
        subject_id=subject_id,
        board_id=board_id,
        class_id=class_id,
        difficulty=difficulty,
        question_type=question_type,
        chapter=chapter,
        search=search,
        limit=pagination.limit,
        offset=pagination.offset,
    )
    items = [_format_question_read(q) for q in questions]
    return PaginatedResponse(
        items=items,
        total=total,
        page=pagination.page,
        page_size=pagination.page_size,
    )


@router.get(
    "/{id}",
    response_model=StandardResponse[QuestionRead],
    dependencies=[require_role(*_STAFF_OR_TEACHER)],
    summary="Get question detail",
)
async def get_question(
    id: uuid.UUID,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    question = await examination_service.get_question(
        db=db,
        institute_id=current_user.institute_id,
        question_id=id,
    )
    return StandardResponse(data=_format_question_read(question))


@router.patch(
    "/{id}",
    response_model=StandardResponse[QuestionRead],
    dependencies=[require_role(*_STAFF_OR_TEACHER)],
    summary="Update question in the question bank",
)
async def update_question(
    id: uuid.UUID,
    body: QuestionUpdate,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    question = await examination_service.update_question(
        db=db,
        institute_id=current_user.institute_id,
        question_id=id,
        payload=body,
    )
    return StandardResponse(data=_format_question_read(question))


@router.delete(
    "/{id}",
    response_model=MessageResponse,
    dependencies=[require_role(*_STAFF_OR_TEACHER)],
    summary="Soft-delete question from the bank",
)
async def delete_question(
    id: uuid.UUID,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    await examination_service.delete_question(
        db=db,
        institute_id=current_user.institute_id,
        question_id=id,
    )
    return MessageResponse(message="Question deleted successfully.")


def _format_question_read(q) -> QuestionRead:
    return QuestionRead(
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
