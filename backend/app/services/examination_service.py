"""
app/services/examination_service.py
-----------------------------------
Business logic for examinations, question bank, test assembly, marks entry,
rank/percentile computation, and result publication.

Core rules:
  1. Questions belong to an institute's question bank, scoped by subject & taxonomy.
  2. Tests can be assembled by picking questions from the question bank.
  3. Bulk marks entry automatically computes percentages, competition ranks,
     and statistical percentiles for present students.
  4. Publication Gate: Results and scorecards are hidden from students/parents
     until the test status transitions to PUBLISHED.
  5. Publishing results writes an immutable audit log entry.
"""

from __future__ import annotations

import uuid
from datetime import date as Date, datetime, timezone
from typing import Any

from fastapi import Request
from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.exceptions import (
    ConflictError,
    ForbiddenError,
    NotFoundError,
    ValidationError,
)
from app.core.logging import get_logger
from app.models.academic_structure import Batch, Board, Course, SchoolClass, Subject
from app.models.enrollment import Enrollment, EnrollmentStatus
from app.models.examination import (
    Question,
    QuestionDifficulty,
    QuestionType,
    Test,
    TestQuestion,
    TestResult,
    TestStatus,
    TestType,
)
from app.models.people import StudentProfile
from app.models.user import User
from app.schemas.examination import (
    BulkMarksEntryRequest,
    QuestionCreate,
    QuestionUpdate,
    StudentMarksEntry,
    TestAnalytics,
    TestCreate,
    TestQuestionAssign,
    TestResultRead,
    TestScorecard,
    TestUpdate,
)
from app.services import audit_service

logger = get_logger(__name__)


# ─────────────────────────────────────────────────────────────────────────────
# 1. Question Bank Operations
# ─────────────────────────────────────────────────────────────────────────────

async def create_question(
    db: AsyncSession,
    *,
    institute_id: uuid.UUID,
    user_id: uuid.UUID,
    payload: QuestionCreate,
    branch_id: uuid.UUID | None = None,
) -> Question:
    """Add a new question to the institute question bank."""
    # 1. Validate subject
    subj_stmt = select(Subject).where(
        Subject.id == payload.subject_id,
        Subject.institute_id == institute_id,
        Subject.is_active.is_(True),
    )
    subj = (await db.execute(subj_stmt)).scalar_one_or_none()
    if not subj:
        raise NotFoundError(f"Subject {payload.subject_id} not found")

    # 2. Optional board / class validation
    if payload.board_id:
        b_stmt = select(Board).where(
            Board.id == payload.board_id,
            Board.institute_id == institute_id,
            Board.is_active.is_(True),
        )
        if not (await db.execute(b_stmt)).scalar_one_or_none():
            raise NotFoundError(f"Board {payload.board_id} not found")

    if payload.class_id:
        c_stmt = select(SchoolClass).where(
            SchoolClass.id == payload.class_id,
            SchoolClass.is_active.is_(True),
        )
        if not (await db.execute(c_stmt)).scalar_one_or_none():
            raise NotFoundError(f"Class {payload.class_id} not found")



    question = Question(
        id=uuid.uuid4(),
        institute_id=institute_id,
        branch_id=branch_id,
        board_id=payload.board_id,
        class_id=payload.class_id,
        stream_id=payload.stream_id,
        subject_id=payload.subject_id,
        chapter=payload.chapter,
        topic=payload.topic,
        difficulty=payload.difficulty,
        question_type=payload.question_type,
        body=payload.body,
        options=payload.options,
        correct_answer=payload.correct_answer,
        explanation=payload.explanation,
        default_marks=payload.default_marks,
        created_by=user_id,
    )
    db.add(question)
    await db.flush()
    await db.refresh(question)
    logger.info("Created question", extra={"question_id": str(question.id), "subject_id": str(payload.subject_id)})
    return question


async def get_question(
    db: AsyncSession,
    *,
    institute_id: uuid.UUID,
    question_id: uuid.UUID,
) -> Question:
    stmt = (
        select(Question)
        .where(
            Question.id == question_id,
            Question.institute_id == institute_id,
            Question.deleted_at.is_(None),
        )
        .options(
            selectinload(Question.subject),
            selectinload(Question.board),
            selectinload(Question.school_class),
            selectinload(Question.creator),
        )
    )
    q = (await db.execute(stmt)).scalar_one_or_none()
    if not q:
        raise NotFoundError(f"Question {question_id} not found")
    return q


async def list_questions(
    db: AsyncSession,
    *,
    institute_id: uuid.UUID,
    subject_id: uuid.UUID | None = None,
    board_id: uuid.UUID | None = None,
    class_id: uuid.UUID | None = None,
    difficulty: QuestionDifficulty | None = None,
    question_type: QuestionType | None = None,
    chapter: str | None = None,
    search: str | None = None,
    limit: int = 50,
    offset: int = 0,
) -> tuple[list[Question], int]:
    stmt = (
        select(Question)
        .where(
            Question.institute_id == institute_id,
            Question.deleted_at.is_(None),
        )
        .options(
            selectinload(Question.subject),
            selectinload(Question.board),
            selectinload(Question.school_class),
            selectinload(Question.creator),
        )
    )

    if subject_id:
        stmt = stmt.where(Question.subject_id == subject_id)
    if board_id:
        stmt = stmt.where(Question.board_id == board_id)
    if class_id:
        stmt = stmt.where(Question.class_id == class_id)
    if difficulty:
        stmt = stmt.where(Question.difficulty == difficulty)
    if question_type:
        stmt = stmt.where(Question.question_type == question_type)
    if chapter:
        stmt = stmt.where(Question.chapter.ilike(f"%{chapter}%"))
    if search:
        stmt = stmt.where(Question.body.ilike(f"%{search}%"))

    # Total count
    count_stmt = select(func.count()).select_from(stmt.subquery())
    total = (await db.execute(count_stmt)).scalar_one()

    # Ordered pagination
    stmt = stmt.order_by(Question.created_at.desc()).limit(limit).offset(offset)
    questions = (await db.execute(stmt)).scalars().all()
    return list(questions), total


async def update_question(
    db: AsyncSession,
    *,
    institute_id: uuid.UUID,
    question_id: uuid.UUID,
    payload: QuestionUpdate,
) -> Question:
    q = await get_question(db, institute_id=institute_id, question_id=question_id)

    update_data = payload.model_dump(exclude_unset=True)
    for field, val in update_data.items():
        setattr(q, field, val)

    await db.flush()
    await db.refresh(q)
    return q


async def delete_question(
    db: AsyncSession,
    *,
    institute_id: uuid.UUID,
    question_id: uuid.UUID,
) -> None:
    q = await get_question(db, institute_id=institute_id, question_id=question_id)
    q.deleted_at = datetime.now(timezone.utc)
    await db.flush()


# ─────────────────────────────────────────────────────────────────────────────
# 2. Test Management & Assembly
# ─────────────────────────────────────────────────────────────────────────────

async def create_test(
    db: AsyncSession,
    *,
    institute_id: uuid.UUID,
    user_id: uuid.UUID,
    payload: TestCreate,
    branch_id: uuid.UUID | None = None,
) -> Test:
    """Create a new test, optionally linking questions from the bank."""
    # 1. Validate target batch or course if specified
    if payload.batch_id:
        b_stmt = select(Batch).where(
            Batch.id == payload.batch_id,
            Batch.institute_id == institute_id,
            Batch.deleted_at.is_(None),
        )
        if not (await db.execute(b_stmt)).scalar_one_or_none():
            raise NotFoundError(f"Batch {payload.batch_id} not found")

    if payload.course_id:
        c_stmt = select(Course).where(
            Course.id == payload.course_id,
            Course.institute_id == institute_id,
            Course.deleted_at.is_(None),
        )
        if not (await db.execute(c_stmt)).scalar_one_or_none():
            raise NotFoundError(f"Course {payload.course_id} not found")

    if payload.subject_id:
        s_stmt = select(Subject).where(
            Subject.id == payload.subject_id,
            Subject.institute_id == institute_id,
            Subject.is_active.is_(True),
        )
        if not (await db.execute(s_stmt)).scalar_one_or_none():
            raise NotFoundError(f"Subject {payload.subject_id} not found")


    test = Test(
        id=uuid.uuid4(),
        institute_id=institute_id,
        branch_id=branch_id,
        course_id=payload.course_id,
        batch_id=payload.batch_id,
        subject_id=payload.subject_id,
        name=payload.name,
        type=payload.type,
        date=payload.date,
        start_time=payload.start_time,
        duration_minutes=payload.duration_minutes,
        max_marks=payload.max_marks,
        passing_marks=payload.passing_marks,
        status=payload.status,
        instructions=payload.instructions,
        created_by=user_id,
    )
    db.add(test)
    await db.flush()

    # If questions provided in payload, attach them
    if payload.questions:
        await _attach_questions_to_test(db, institute_id=institute_id, test=test, questions=payload.questions)

    await db.refresh(test)
    return await get_test(db, institute_id=institute_id, test_id=test.id)


async def _attach_questions_to_test(
    db: AsyncSession,
    *,
    institute_id: uuid.UUID,
    test: Test,
    questions: list[TestQuestionAssign],
) -> None:
    for q_assign in questions:
        # Check question exists in institute
        q_stmt = select(Question).where(
            Question.id == q_assign.question_id,
            Question.institute_id == institute_id,
            Question.deleted_at.is_(None),
        )
        q = (await db.execute(q_stmt)).scalar_one_or_none()
        if not q:
            raise NotFoundError(f"Question {q_assign.question_id} not found")

        tq = TestQuestion(
            id=uuid.uuid4(),
            test_id=test.id,
            question_id=q.id,
            marks=q_assign.marks,
            display_order=q_assign.display_order,
            section=q_assign.section,
        )
        db.add(tq)
    await db.flush()


async def get_test(
    db: AsyncSession,
    *,
    institute_id: uuid.UUID,
    test_id: uuid.UUID,
    for_student_or_parent: bool = False,
) -> Test:
    stmt = (
        select(Test)
        .where(
            Test.id == test_id,
            Test.institute_id == institute_id,
            Test.deleted_at.is_(None),
        )
        .options(
            selectinload(Test.course),
            selectinload(Test.batch),
            selectinload(Test.subject),
            selectinload(Test.creator),
            selectinload(Test.publisher),
            selectinload(Test.test_questions).selectinload(TestQuestion.question),
            selectinload(Test.results).selectinload(TestResult.student),
        )
    )
    t = (await db.execute(stmt)).scalar_one_or_none()
    if not t:
        raise NotFoundError(f"Test {test_id} not found")

    # Publication gate
    if for_student_or_parent and t.status != TestStatus.PUBLISHED:
        raise ForbiddenError("Test details and results have not been published yet.")

    return t


async def list_tests(
    db: AsyncSession,
    *,
    institute_id: uuid.UUID,
    course_id: uuid.UUID | None = None,
    batch_id: uuid.UUID | None = None,
    subject_id: uuid.UUID | None = None,
    status: TestStatus | None = None,
    type: TestType | None = None,
    date_from: Date | None = None,
    date_to: Date | None = None,
    limit: int = 50,
    offset: int = 0,
    for_student_or_parent: bool = False,
    student_batch_ids: list[uuid.UUID] | None = None,
) -> tuple[list[Test], int]:
    stmt = (
        select(Test)
        .where(
            Test.institute_id == institute_id,
            Test.deleted_at.is_(None),
        )
        .options(
            selectinload(Test.course),
            selectinload(Test.batch),
            selectinload(Test.subject),
            selectinload(Test.creator),
            selectinload(Test.test_questions),
            selectinload(Test.results),
        )
    )

    if for_student_or_parent:
        # Publication gate: student/parent can ONLY see published tests
        stmt = stmt.where(Test.status == TestStatus.PUBLISHED)
        if student_batch_ids is not None:
            stmt = stmt.where(
                (Test.batch_id.in_(student_batch_ids)) | (Test.batch_id.is_(None))
            )
    elif status:
        stmt = stmt.where(Test.status == status)

    if course_id:
        stmt = stmt.where(Test.course_id == course_id)
    if batch_id:
        stmt = stmt.where(Test.batch_id == batch_id)
    if subject_id:
        stmt = stmt.where(Test.subject_id == subject_id)
    if type:
        stmt = stmt.where(Test.type == type)
    if date_from:
        stmt = stmt.where(Test.date >= date_from)
    if date_to:
        stmt = stmt.where(Test.date <= date_to)

    count_stmt = select(func.count()).select_from(stmt.subquery())
    total = (await db.execute(count_stmt)).scalar_one()

    stmt = stmt.order_by(Test.date.desc(), Test.created_at.desc()).limit(limit).offset(offset)
    tests = (await db.execute(stmt)).scalars().all()
    return list(tests), total


async def update_test(
    db: AsyncSession,
    *,
    institute_id: uuid.UUID,
    test_id: uuid.UUID,
    payload: TestUpdate,
) -> Test:
    test = await get_test(db, institute_id=institute_id, test_id=test_id)

    update_data = payload.model_dump(exclude_unset=True)
    for field, val in update_data.items():
        setattr(test, field, val)

    await db.flush()
    await db.refresh(test)
    return test


async def delete_test(
    db: AsyncSession,
    *,
    institute_id: uuid.UUID,
    test_id: uuid.UUID,
) -> None:
    test = await get_test(db, institute_id=institute_id, test_id=test_id)
    test.deleted_at = datetime.now(timezone.utc)
    await db.flush()


async def assign_questions(
    db: AsyncSession,
    *,
    institute_id: uuid.UUID,
    test_id: uuid.UUID,
    questions: list[TestQuestionAssign],
) -> Test:
    test = await get_test(db, institute_id=institute_id, test_id=test_id)

    # Remove existing questions
    for existing_q in list(test.test_questions):
        await db.delete(existing_q)
    await db.flush()

    # Attach new questions
    await _attach_questions_to_test(db, institute_id=institute_id, test=test, questions=questions)
    await db.refresh(test)
    return await get_test(db, institute_id=institute_id, test_id=test.id)


# ─────────────────────────────────────────────────────────────────────────────
# 3. Marks Entry & Rank/Percentile Computation Engine
# ─────────────────────────────────────────────────────────────────────────────

async def record_bulk_marks(
    db: AsyncSession,
    *,
    institute_id: uuid.UUID,
    evaluator_user_id: uuid.UUID,
    test_id: uuid.UUID,
    payload: BulkMarksEntryRequest,
) -> list[TestResult]:
    """
    Record or update marks for a batch of students taking a test.
    Automatically:
      1. Validates marks boundaries (0 <= marks <= max_marks).
      2. Computes percentage = (marks / max_marks) * 100.
      3. Recomputes competition ranks and statistical percentiles across all present candidates.
      4. Auto-advances test status to EVALUATING if it was SCHEDULED/CONDUCTED.
    """
    test = await get_test(db, institute_id=institute_id, test_id=test_id)

    if test.status == TestStatus.DRAFT:
        # Auto advance or allow
        test.status = TestStatus.EVALUATING
    elif test.status in (TestStatus.SCHEDULED, TestStatus.CONDUCTED):
        test.status = TestStatus.EVALUATING

    # 1. Upsert student results
    student_ids = [e.student_id for e in payload.entries]

    # Verify all students belong to the institute
    students_stmt = select(StudentProfile).where(
        StudentProfile.id.in_(student_ids),
        StudentProfile.institute_id == institute_id,
        StudentProfile.deleted_at.is_(None),
    )
    valid_students = {s.id: s for s in (await db.execute(students_stmt)).scalars().all()}

    existing_results_stmt = select(TestResult).where(
        TestResult.test_id == test_id,
        TestResult.student_id.in_(student_ids),
    )
    existing_map = {r.student_id: r for r in (await db.execute(existing_results_stmt)).scalars().all()}

    for entry in payload.entries:
        if entry.student_id not in valid_students:
            raise NotFoundError(f"StudentProfile {entry.student_id} not found")

        if not entry.is_absent:
            if entry.marks_obtained is None:
                raise ValidationError("marks_obtained is required when student is not absent.")
            if entry.marks_obtained < 0:
                raise ValidationError(f"Marks obtained cannot be negative: {entry.marks_obtained}")
            if entry.marks_obtained > test.max_marks:
                raise ValidationError(
                    f"Marks obtained ({entry.marks_obtained}) cannot exceed test max marks ({test.max_marks})."
                )
            pct = round((entry.marks_obtained / test.max_marks) * 100.0, 2)
            marks_val = entry.marks_obtained
        else:
            pct = None
            marks_val = None

        if entry.student_id in existing_map:
            res = existing_map[entry.student_id]
            res.marks_obtained = marks_val
            res.is_absent = entry.is_absent
            res.percentage = pct
            res.remarks = entry.remarks
            res.evaluated_by = evaluator_user_id
        else:
            res = TestResult(
                id=uuid.uuid4(),
                test_id=test_id,
                student_id=entry.student_id,
                marks_obtained=marks_val,
                is_absent=entry.is_absent,
                percentage=pct,
                remarks=entry.remarks,
                evaluated_by=evaluator_user_id,
            )
            db.add(res)

    await db.flush()

    # 2. Recompute ranks & percentiles across ALL results for this test
    await _recalculate_ranks_and_percentiles(db, test_id=test_id)

    # Return refreshed results for this test
    res_stmt = (
        select(TestResult)
        .where(TestResult.test_id == test_id)
        .options(selectinload(TestResult.student), selectinload(TestResult.evaluator))
        .order_by(TestResult.rank.asc().nulls_last(), TestResult.created_at.asc())
    )
    refreshed_results = (await db.execute(res_stmt)).scalars().all()
    return list(refreshed_results)


async def _recalculate_ranks_and_percentiles(db: AsyncSession, *, test_id: uuid.UUID) -> None:
    """
    Standard competition ranking (1224) and statistical percentile calculation
    across all present examinees.
    Formula for percentile:
      P = ((count(score < S) + 0.5 * count(score == S)) / total_present) * 100
    """
    stmt = (
        select(TestResult)
        .where(TestResult.test_id == test_id)
    )
    all_results = (await db.execute(stmt)).scalars().all()

    present_results = [r for r in all_results if not r.is_absent and r.marks_obtained is not None]
    absent_results = [r for r in all_results if r.is_absent or r.marks_obtained is None]

    # Clear absent ranks & percentiles
    for r in absent_results:
        r.rank = None
        r.percentile = None

    if not present_results:
        await db.flush()
        return

    # Sort descending by marks_obtained
    present_results.sort(key=lambda x: x.marks_obtained, reverse=True)
    total_present = len(present_results)

    # 1. Competition Ranking
    current_rank = 1
    for i, res in enumerate(present_results):
        if i > 0 and res.marks_obtained == present_results[i - 1].marks_obtained:
            # Same marks as previous student -> same rank
            res.rank = present_results[i - 1].rank
        else:
            res.rank = i + 1

    # 2. Percentile Distribution
    for res in present_results:
        strictly_less = sum(1 for r in present_results if r.marks_obtained < res.marks_obtained)
        equal_score = sum(1 for r in present_results if r.marks_obtained == res.marks_obtained)
        res.percentile = round(((strictly_less + 0.5 * equal_score) / total_present) * 100.0, 2)

    await db.flush()


# ─────────────────────────────────────────────────────────────────────────────
# 4. Publication Gate & Audit Log
# ─────────────────────────────────────────────────────────────────────────────

async def publish_test_results(
    db: AsyncSession,
    *,
    institute_id: uuid.UUID,
    user: User,
    test_id: uuid.UUID,
    request: Request | None = None,
) -> Test:
    """
    Publish test results, unlocking visibility for students and parents.
    Emits an audit log entry.
    """
    test = await get_test(db, institute_id=institute_id, test_id=test_id)

    if not test.results:
        raise ValidationError("Cannot publish test results: no marks or student records entered yet.")

    old_status = test.status
    now = datetime.now(timezone.utc)
    test.status = TestStatus.PUBLISHED
    test.published_at = now
    test.published_by = user.id

    # Emit audit log
    await audit_service.log(
        db=db,
        actor=user,
        action="result.published",
        entity_name="tests",
        entity_id=str(test.id),
        old_values={"status": old_status.value},
        new_values={
            "status": TestStatus.PUBLISHED.value,
            "test_name": test.name,
            "total_candidates": len(test.results),
            "published_at": now.isoformat(),
        },
        request=request,
        institute_id=institute_id,
    )

    await db.flush()
    await db.refresh(test)
    logger.info("Published test results", extra={"test_id": str(test.id), "published_by": str(user.id)})
    return test


# ─────────────────────────────────────────────────────────────────────────────
# 5. Scorecards & Analytics
# ─────────────────────────────────────────────────────────────────────────────

async def get_student_scorecard(
    db: AsyncSession,
    *,
    institute_id: uuid.UUID,
    test_id: uuid.UUID,
    student_id: uuid.UUID,
    requester_role: str,
) -> dict[str, Any]:
    """Fetch student performance report card for a test."""
    is_student_or_parent = requester_role in ("STUDENT", "PARENT")
    test = await get_test(
        db,
        institute_id=institute_id,
        test_id=test_id,
        for_student_or_parent=is_student_or_parent,
    )

    # Fetch result
    stmt = (
        select(TestResult)
        .where(TestResult.test_id == test_id, TestResult.student_id == student_id)
        .options(selectinload(TestResult.student))
    )
    result = (await db.execute(stmt)).scalar_one_or_none()
    if not result:
        raise NotFoundError(f"TestResult for test {test_id} and student {student_id} not found")

    # Compute batch stats
    present_marks = [r.marks_obtained for r in test.results if not r.is_absent and r.marks_obtained is not None]
    highest = max(present_marks) if present_marks else None
    avg = round(sum(present_marks) / len(present_marks), 2) if present_marks else None

    is_passed = None
    if test.passing_marks is not None and result.marks_obtained is not None:
        is_passed = result.marks_obtained >= test.passing_marks

    return {
        "test": test,
        "result": result,
        "max_marks": test.max_marks,
        "passing_marks": test.passing_marks,
        "is_passed": is_passed,
        "class_highest_marks": highest,
        "class_average_marks": avg,
    }


async def get_test_analytics(
    db: AsyncSession,
    *,
    institute_id: uuid.UUID,
    test_id: uuid.UUID,
) -> TestAnalytics:
    """Compute aggregate analytics and leaderboard for a test."""
    test = await get_test(db, institute_id=institute_id, test_id=test_id)

    total_candidates = len(test.results)
    present_results = [r for r in test.results if not r.is_absent and r.marks_obtained is not None]
    absent_count = len([r for r in test.results if r.is_absent])
    present_count = len(present_results)

    scores = [r.marks_obtained for r in present_results]
    highest = max(scores) if scores else None
    lowest = min(scores) if scores else None
    avg = round(sum(scores) / len(scores), 2) if scores else None

    pass_pct = None
    if test.passing_marks is not None and present_count > 0:
        passed_count = sum(1 for s in scores if s >= test.passing_marks)
        pass_pct = round((passed_count / present_count) * 100.0, 2)

    # Leaderboard (Top 10)
    sorted_present = sorted(present_results, key=lambda x: (x.rank or 999999, -(x.marks_obtained or 0)))
    top_10 = sorted_present[:10]

    leaderboard_items = []
    for r in top_10:
        name = None
        adm_no = None
        roll_no = None
        if getattr(r, "student", None):
            name = f"{r.student.first_name} {r.student.last_name or ''}".strip()
            adm_no = r.student.admission_number
            roll_no = getattr(r.student, "roll_number", None)
        leaderboard_items.append(
            TestResultRead(
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
        )

    return TestAnalytics(
        test_id=test.id,
        test_name=test.name,
        max_marks=test.max_marks,
        total_candidates=total_candidates,
        present_count=present_count,
        absent_count=absent_count,
        highest_marks=highest,
        average_marks=avg,
        lowest_marks=lowest,
        pass_percentage=pass_pct,
        leaderboard=leaderboard_items,
    )
