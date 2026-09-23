"""
app/services/analytics_service.py
---------------------------------
Business logic for Executive Dashboards, Batch Analytics,
Materialized View Refreshes, Attendance Trends, Financial Metrics,
Student 360° Profile Aggregation, and Data Streaming Exports.
"""

from __future__ import annotations

import csv
import io
import uuid
from datetime import date as Date, datetime, timedelta, timezone
from typing import Any

from sqlalchemy import (
    and_,
    case,
    desc,
    func,
    or_,
    select,
    text,
)
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, selectinload

from app.core.exceptions import ForbiddenError, NotFoundError
from app.core.logging import get_logger
from app.models.academic_operations import (
    Attendance,
    AttendanceStatus,
    ClassSession,
    ClassSessionStatus,
    StudentRemark,
)
from app.models.academic_structure import Batch, SchoolClass
from app.models.enquiry import Enquiry, EnquiryStage
from app.models.enrollment import Enrollment, EnrollmentStatus
from app.models.examination import Test, TestResult, TestStatus
from app.models.finance import FeePlan, Installment, Payment, PaymentMethod, Receipt
from app.models.learning import Homework, HomeworkSubmission
from app.models.people import ParentProfile, StudentParent, StudentProfile, TeacherProfile
from app.models.user import User
from app.schemas.analytics import (
    AttendanceAnalyticsResponse,
    BatchAnalyticsResponse,
    DashboardKPIsResponse,
    ExportType,
    FinancialAnalyticsResponse,
    LowAttendanceAlert,
    MaterializedViewRefreshResponse,
    Student360ProfileResponse,
)

logger = get_logger(__name__)


# ─────────────────────────────────────────────────────────────────────────────
# 1. Executive Dashboard KPIs
# ─────────────────────────────────────────────────────────────────────────────

async def get_executive_dashboard(
    db: AsyncSession,
    *,
    institute_id: uuid.UUID,
) -> DashboardKPIsResponse:
    """Compute executive KPI cards, 7-day attendance trends, and 6-month financial collection metrics."""
    # 1. Counts
    total_students = (
        await db.execute(
            select(func.count(StudentProfile.id)).where(
                StudentProfile.institute_id == institute_id,
                StudentProfile.is_active.is_(True),
                StudentProfile.deleted_at.is_(None),
            )
        )
    ).scalar_one() or 0

    total_batches = (
        await db.execute(
            select(func.count(Batch.id)).where(
                Batch.institute_id == institute_id,
                Batch.is_active.is_(True),
                Batch.deleted_at.is_(None),
            )
        )
    ).scalar_one() or 0

    total_teachers = (
        await db.execute(
            select(func.count(TeacherProfile.id)).where(
                TeacherProfile.institute_id == institute_id,
                TeacherProfile.is_active.is_(True),
                TeacherProfile.deleted_at.is_(None),
            )
        )
    ).scalar_one() or 0

    total_enquiries = (
        await db.execute(
            select(func.count(Enquiry.id)).where(
                Enquiry.institute_id == institute_id,
                Enquiry.stage.notin_([EnquiryStage.ADMISSION, EnquiryStage.NOT_INTERESTED]),
                Enquiry.deleted_at.is_(None),
            )
        )
    ).scalar_one() or 0

    # 2. Financial Metrics
    total_billed = (
        await db.execute(
            select(func.coalesce(func.sum(FeePlan.net_amount), 0.0)).where(
                FeePlan.institute_id == institute_id,
            )
        )
    ).scalar_one() or 0.0

    total_collected = (
        await db.execute(
            select(func.coalesce(func.sum(Payment.amount), 0.0)).where(
                Payment.institute_id == institute_id,
            )
        )
    ).scalar_one() or 0.0

    total_pending = max(0.0, float(total_billed) - float(total_collected))

    # 3. Overall Attendance Rate
    att_stats = (
        await db.execute(
            select(
                func.count(Attendance.id).label("total"),
                func.count(case((Attendance.status == AttendanceStatus.PRESENT, 1))).label("present"),
            )
            .select_from(Attendance)
            .join(ClassSession, ClassSession.id == Attendance.class_session_id)
            .where(ClassSession.institute_id == institute_id)
        )
    ).one()
    total_att, present_att = att_stats[0] or 0, att_stats[1] or 0
    overall_att_rate = round((present_att / total_att * 100.0), 2) if total_att > 0 else 0.0

    # 4. 7-Day Attendance Trend
    today = datetime.now(timezone.utc).date()
    attendance_trends_7d = []
    for i in range(6, -1, -1):
        target_date = today - timedelta(days=i)
        day_stats = (
            await db.execute(
                select(
                    func.count(Attendance.id).label("total"),
                    func.count(case((Attendance.status == AttendanceStatus.PRESENT, 1))).label("present"),
                )
                .select_from(Attendance)
                .join(ClassSession, ClassSession.id == Attendance.class_session_id)
                .where(
                    ClassSession.institute_id == institute_id,
                    ClassSession.date == target_date,
                )
            )
        ).one()
        d_total, d_pres = day_stats[0] or 0, day_stats[1] or 0
        rate = round((d_pres / d_total * 100.0), 2) if d_total > 0 else 0.0
        attendance_trends_7d.append({"date": target_date.isoformat(), "rate": rate, "total_sessions": d_total})

    # 5. 6-Month Fee Collections Trend
    monthly_collections_6m = []
    for m in range(5, -1, -1):
        # approximate month offset
        m_start = (today.replace(day=1) - timedelta(days=m * 30)).replace(day=1)
        next_month = (m_start + timedelta(days=32)).replace(day=1)
        m_start_dt = datetime(m_start.year, m_start.month, m_start.day, tzinfo=timezone.utc)
        next_month_dt = datetime(next_month.year, next_month.month, next_month.day, tzinfo=timezone.utc)
        m_sum = (
            await db.execute(
                select(func.coalesce(func.sum(Payment.amount), 0.0)).where(
                    Payment.institute_id == institute_id,
                    Payment.paid_at >= m_start_dt,
                    Payment.paid_at < next_month_dt,
                )
            )
        ).scalar_one() or 0.0
        monthly_collections_6m.append({"month": m_start.strftime("%Y-%m"), "collected": float(m_sum)})

    return DashboardKPIsResponse(
        total_students=total_students,
        total_batches=total_batches,
        total_teachers=total_teachers,
        total_enquiries_open=total_enquiries,
        total_fees_billed=round(float(total_billed), 2),
        total_fees_collected=round(float(total_collected), 2),
        total_fees_pending=round(float(total_pending), 2),
        overall_attendance_rate=overall_att_rate,
        attendance_trends_7d=attendance_trends_7d,
        monthly_collections_6m=monthly_collections_6m,
    )


# ─────────────────────────────────────────────────────────────────────────────
# 2. Batch Detailed Analytics
# ─────────────────────────────────────────────────────────────────────────────

async def get_batch_analytics(
    db: AsyncSession,
    *,
    institute_id: uuid.UUID,
    batch_id: uuid.UUID,
    current_user: User,
) -> BatchAnalyticsResponse:
    """Fetch analytics for a specific batch, checking ReBAC teacher assignment and falling back to live queries."""
    # 1. Fetch batch
    batch_stmt = (
        select(Batch)
        .where(
            Batch.id == batch_id,
            Batch.institute_id == institute_id,
            Batch.deleted_at.is_(None),
        )
        .options(joinedload(Batch.teacher))
    )
    batch = (await db.execute(batch_stmt)).scalar_one_or_none()
    if not batch:
        raise NotFoundError(f"Batch {batch_id} not found.")

    # 2. ReBAC Guard: Teachers can only view batches they teach
    if current_user.role == "TEACHER":
        t_stmt = select(TeacherProfile.id).where(TeacherProfile.user_id == current_user.id)
        teacher_prof_id = (await db.execute(t_stmt)).scalar_one_or_none()
        if batch.teacher_id != teacher_prof_id:
            raise ForbiddenError("You do not have permission to view analytics for this batch.")

    # 3. Read from Materialized View with fallback
    mv_stmt = text(
        """
        SELECT total_enrolled, total_sessions_conducted, average_attendance_rate, tests_conducted, average_test_score
        FROM mv_batch_performance_summary
        WHERE batch_id = :b_id
        """
    )
    mv_row = (await db.execute(mv_stmt, {"b_id": batch_id})).mappings().first()

    if mv_row:
        total_enrolled = mv_row["total_enrolled"]
        total_sessions = mv_row["total_sessions_conducted"]
        avg_att_rate = float(mv_row["average_attendance_rate"])
        tests_conducted = mv_row["tests_conducted"]
        avg_test_score = float(mv_row["average_test_score"])
    else:
        # Fallback to direct calculation
        total_enrolled = (
            await db.execute(
                select(func.count(Enrollment.id)).where(
                    Enrollment.batch_id == batch_id,
                    Enrollment.status == EnrollmentStatus.ACTIVE,
                )
            )
        ).scalar_one() or 0

        total_sessions = (
            await db.execute(
                select(func.count(ClassSession.id)).where(
                    ClassSession.batch_id == batch_id,
                    ClassSession.status == ClassSessionStatus.HELD,
                    ClassSession.deleted_at.is_(None),
                )
            )
        ).scalar_one() or 0

        att_stats = (
            await db.execute(
                select(
                    func.count(Attendance.id).label("total"),
                    func.count(case((Attendance.status == AttendanceStatus.PRESENT, 1))).label("present"),
                )
                .select_from(Attendance)
                .join(ClassSession, ClassSession.id == Attendance.class_session_id)
                .where(ClassSession.batch_id == batch_id, ClassSession.status == ClassSessionStatus.HELD)
            )
        ).one()
        t_att, p_att = att_stats[0] or 0, att_stats[1] or 0
        avg_att_rate = round((p_att / t_att * 100.0), 2) if t_att > 0 else 0.0

        test_stats = (
            await db.execute(
                select(
                    func.count(Test.id.distinct()).label("tests"),
                    func.coalesce(func.avg(TestResult.percentage), 0.0).label("avg_score"),
                )
                .select_from(Test)
                .outerjoin(TestResult, TestResult.test_id == Test.id)
                .where(Test.batch_id == batch_id, Test.status == TestStatus.PUBLISHED, Test.deleted_at.is_(None))
            )
        ).one()
        tests_conducted = test_stats[0] or 0
        avg_test_score = round(float(test_stats[1] or 0.0), 2)

    # 4. Detailed Test Metrics (Top score, pass rate)
    test_results_stmt = (
        select(
            func.max(TestResult.percentage).label("top_score"),
            func.count(case((TestResult.percentage >= 40.0, 1))).label("passed"),
            func.count(TestResult.id).label("total_results"),
        )
        .select_from(TestResult)
        .join(Test, Test.id == TestResult.test_id)
        .where(Test.batch_id == batch_id, Test.status == TestStatus.PUBLISHED, Test.deleted_at.is_(None))
    )
    tr_row = (await db.execute(test_results_stmt)).one()
    top_score = float(tr_row[0]) if tr_row[0] is not None else None
    passed_count, total_res = tr_row[1] or 0, tr_row[2] or 0
    pass_rate = round((passed_count / total_res * 100.0), 2) if total_res > 0 else None

    # 5. Low Attendance Count in Batch (< 75%)
    subq = (
        select(
            Attendance.enrollment_id,
            func.count(Attendance.id).label("tot"),
            func.count(case((Attendance.status == AttendanceStatus.PRESENT, 1))).label("pres"),
        )
        .join(ClassSession, ClassSession.id == Attendance.class_session_id)
        .where(ClassSession.batch_id == batch_id, ClassSession.status == ClassSessionStatus.HELD)
        .group_by(Attendance.enrollment_id)
        .subquery()
    )
    low_att_count = (
        await db.execute(
            select(func.count(subq.c.enrollment_id)).where(
                (subq.c.pres * 100.0 / subq.c.tot) < 75.0
            )
        )
    ).scalar_one() or 0

    # 6. Homework metrics
    hw_assigned = (
        await db.execute(
            select(func.count(Homework.id)).where(
                Homework.batch_id == batch_id,
                Homework.deleted_at.is_(None),
            )
        )
    ).scalar_one() or 0

    hw_subs = (
        await db.execute(
            select(func.count(HomeworkSubmission.id))
            .join(Homework, Homework.id == HomeworkSubmission.homework_id)
            .where(Homework.batch_id == batch_id, Homework.deleted_at.is_(None))
        )
    ).scalar_one() or 0

    expected_subs = hw_assigned * total_enrolled
    hw_sub_rate = round((hw_subs / expected_subs * 100.0), 2) if expected_subs > 0 else 0.0

    return BatchAnalyticsResponse(
        batch_id=batch.id,
        batch_name=batch.name,
        total_enrolled=total_enrolled,
        capacity=batch.capacity,
        total_sessions_conducted=total_sessions,
        average_attendance_rate=avg_att_rate,
        low_attendance_students_count=low_att_count,
        tests_conducted=tests_conducted,
        average_test_score=avg_test_score,
        top_test_score=top_score,
        pass_rate=pass_rate,
        homework_assigned_count=hw_assigned,
        homework_submission_rate=hw_sub_rate,
    )


# ─────────────────────────────────────────────────────────────────────────────
# 3. Financial Analytics
# ─────────────────────────────────────────────────────────────────────────────

async def get_financial_analytics(
    db: AsyncSession,
    *,
    institute_id: uuid.UUID,
    start_date: Date | None = None,
    end_date: Date | None = None,
) -> FinancialAnalyticsResponse:
    """Analyze fee collections, overdue installments, and payment method distribution."""
    # Billed
    billed_stmt = select(func.coalesce(func.sum(FeePlan.net_amount), 0.0)).where(
        FeePlan.institute_id == institute_id
    )
    total_billed = float((await db.execute(billed_stmt)).scalar_one() or 0.0)

    # Collected
    pay_stmt = select(func.coalesce(func.sum(Payment.amount), 0.0)).where(
        Payment.institute_id == institute_id
    )
    if start_date:
        start_dt = datetime(start_date.year, start_date.month, start_date.day, tzinfo=timezone.utc)
        pay_stmt = pay_stmt.where(Payment.paid_at >= start_dt)
    if end_date:
        end_dt = datetime(end_date.year, end_date.month, end_date.day, 23, 59, 59, tzinfo=timezone.utc)
        pay_stmt = pay_stmt.where(Payment.paid_at <= end_dt)
    total_collected = float((await db.execute(pay_stmt)).scalar_one() or 0.0)

    # Overdue
    today = datetime.now(timezone.utc).date()
    overdue_stmt = (
        select(func.coalesce(func.sum(Installment.amount - Installment.paid_amount), 0.0))
        .join(FeePlan, FeePlan.id == Installment.fee_plan_id)
        .where(
            FeePlan.institute_id == institute_id,
            Installment.due_date < today,
            Installment.paid_amount < Installment.amount,
        )
    )
    total_overdue = float((await db.execute(overdue_stmt)).scalar_one() or 0.0)

    col_rate = round((total_collected / total_billed * 100.0), 2) if total_billed > 0 else 0.0

    # Breakdown by payment method
    method_stmt = (
        select(Payment.payment_method, func.sum(Payment.amount))
        .where(Payment.institute_id == institute_id)
        .group_by(Payment.payment_method)
    )
    method_rows = (await db.execute(method_stmt)).all()
    method_breakdown = {m.value if hasattr(m, "value") else str(m): round(float(amt), 2) for m, amt in method_rows}

    # Monthly timeline for the last 12 months
    monthly_timeline = []
    for m in range(11, -1, -1):
        m_start = (today.replace(day=1) - timedelta(days=m * 30)).replace(day=1)
        next_month = (m_start + timedelta(days=32)).replace(day=1)
        m_start_dt = datetime(m_start.year, m_start.month, m_start.day, tzinfo=timezone.utc)
        next_month_dt = datetime(next_month.year, next_month.month, next_month.day, tzinfo=timezone.utc)
        m_sum = (
            await db.execute(
                select(func.coalesce(func.sum(Payment.amount), 0.0)).where(
                    Payment.institute_id == institute_id,
                    Payment.paid_at >= m_start_dt,
                    Payment.paid_at < next_month_dt,
                )
            )
        ).scalar_one() or 0.0
        monthly_timeline.append({"month": m_start.strftime("%Y-%m"), "collected": float(m_sum)})

    return FinancialAnalyticsResponse(
        total_billed=round(total_billed, 2),
        total_collected=round(total_collected, 2),
        total_overdue=round(total_overdue, 2),
        collection_rate_percentage=col_rate,
        method_breakdown=method_breakdown,
        monthly_timeline=monthly_timeline,
    )


# ─────────────────────────────────────────────────────────────────────────────
# 4. Attendance Analytics & Low Attendance Alerts
# ─────────────────────────────────────────────────────────────────────────────

async def get_attendance_analytics(
    db: AsyncSession,
    *,
    institute_id: uuid.UUID,
    batch_id: uuid.UUID | None = None,
    start_date: Date | None = None,
    end_date: Date | None = None,
) -> AttendanceAnalyticsResponse:
    """Analyze status distribution and identify students with < 75% attendance."""
    query = (
        select(
            func.count(Attendance.id).label("total"),
            func.count(case((Attendance.status == AttendanceStatus.PRESENT, 1))).label("present"),
            func.count(case((Attendance.status == AttendanceStatus.ABSENT, 1))).label("absent"),
            func.count(case((Attendance.status == AttendanceStatus.LATE, 1))).label("late"),
            func.count(case((Attendance.status == AttendanceStatus.EXCUSED, 1))).label("excused"),
        )
        .select_from(Attendance)
        .join(ClassSession, ClassSession.id == Attendance.class_session_id)
        .where(ClassSession.institute_id == institute_id)
    )
    if batch_id:
        query = query.where(ClassSession.batch_id == batch_id)
    if start_date:
        query = query.where(ClassSession.date >= start_date)
    if end_date:
        query = query.where(ClassSession.date <= end_date)

    row = (await db.execute(query)).one()
    total = row[0] or 0
    present = row[1] or 0
    absent = row[2] or 0
    late = row[3] or 0
    excused = row[4] or 0

    rate = round(((present + late) / total * 100.0), 2) if total > 0 else 0.0

    # Low attendance student identification (< 75%)
    low_att_stmt = (
        select(
            StudentProfile.id.label("student_id"),
            StudentProfile.first_name,
            StudentProfile.last_name,
            StudentProfile.admission_number,
            Batch.id.label("batch_id"),
            Batch.name.label("batch_name"),
            func.count(Attendance.id).label("total_classes"),
            func.count(case((Attendance.status == AttendanceStatus.PRESENT, 1))).label("attended_classes"),
        )
        .select_from(Attendance)
        .join(ClassSession, ClassSession.id == Attendance.class_session_id)
        .join(Enrollment, Enrollment.id == Attendance.enrollment_id)
        .join(StudentProfile, StudentProfile.id == Enrollment.student_id)
        .join(Batch, Batch.id == ClassSession.batch_id)
        .where(ClassSession.institute_id == institute_id)
    )
    if batch_id:
        low_att_stmt = low_att_stmt.where(ClassSession.batch_id == batch_id)

    low_att_stmt = (
        low_att_stmt.group_by(
            StudentProfile.id,
            StudentProfile.first_name,
            StudentProfile.last_name,
            StudentProfile.admission_number,
            Batch.id,
            Batch.name,
        )
        .having(func.count(Attendance.id) >= 1)
    )

    student_records = (await db.execute(low_att_stmt)).all()
    alerts: list[LowAttendanceAlert] = []
    for s in student_records:
        t_cls = s.total_classes
        att_cls = s.attended_classes
        att_pct = round((att_cls / t_cls * 100.0), 2) if t_cls > 0 else 0.0
        if att_pct < 75.0:
            alerts.append(
                LowAttendanceAlert(
                    student_id=s.student_id,
                    student_name=f"{s.first_name} {s.last_name}",
                    admission_number=s.admission_number,
                    batch_id=s.batch_id,
                    batch_name=s.batch_name,
                    total_classes=t_cls,
                    attended_classes=att_cls,
                    attendance_percentage=att_pct,
                )
            )

    return AttendanceAnalyticsResponse(
        total_records=total,
        present_count=present,
        absent_count=absent,
        late_count=late,
        excused_count=excused,
        attendance_rate_percentage=rate,
        low_attendance_students=alerts,
    )


# ─────────────────────────────────────────────────────────────────────────────
# 5. Student 360° Comprehensive Profile
# ─────────────────────────────────────────────────────────────────────────────

async def get_student_360_profile(
    db: AsyncSession,
    *,
    institute_id: uuid.UUID,
    student_id: uuid.UUID,
    current_user: User,
) -> Student360ProfileResponse:
    """
    Construct a complete 360° view of a student combining demographics, enrollments,
    attendance, exam results, fee ledger, homework submissions, and teacher remarks.
    Strictly enforced via ReBAC.
    """
    # 1. Fetch student profile with parents and enrollments
    stmt = (
        select(StudentProfile)
        .where(
            StudentProfile.id == student_id,
            StudentProfile.institute_id == institute_id,
            StudentProfile.deleted_at.is_(None),
        )
        .options(
            selectinload(StudentProfile.student_parents)
            .joinedload(StudentParent.parent)
            .joinedload(ParentProfile.user),
            selectinload(StudentProfile.enrollments)
            .joinedload(Enrollment.batch)
            .joinedload(Batch.course),
            selectinload(StudentProfile.enrollments)
            .joinedload(Enrollment.batch)
            .joinedload(Batch.teacher)
            .joinedload(TeacherProfile.user),
        )
    )
    student = (await db.execute(stmt)).scalar_one_or_none()
    if not student:
        raise NotFoundError(f"Student {student_id} not found.")

    # 2. Strict ReBAC Authorization Check
    authorized = False
    if current_user.role in ("SUPER_ADMIN", "ADMIN", "COUNSELLOR", "RECEPTIONIST"):
        authorized = True
    elif current_user.role == "STUDENT":
        authorized = student.user_id == current_user.id
    elif current_user.role == "PARENT":
        authorized = any(
            sp.parent and sp.parent.user_id == current_user.id
            for sp in student.student_parents
        )
    elif current_user.role == "TEACHER":
        authorized = any(
            e.status == EnrollmentStatus.ACTIVE
            and e.batch
            and e.batch.teacher
            and e.batch.teacher.user_id == current_user.id
            for e in student.enrollments
        )

    if not authorized:
        raise ForbiddenError("You do not have permission to access this student's 360° profile.")

    # 3. Class Name lookup if assigned
    current_class_name = None
    if student.current_class_id:
        c_stmt = select(SchoolClass.name).where(SchoolClass.id == student.current_class_id)
        current_class_name = (await db.execute(c_stmt)).scalar_one_or_none()

    # 4. Guardians information
    guardians = [
        {
            "name": f"{sp.parent.first_name} {sp.parent.last_name}",
            "relation": sp.parent.relation,
            "occupation": sp.parent.occupation,
            "email": sp.parent.user.email if sp.parent.user else None,
            "mobile": sp.parent.user.mobile if sp.parent.user else None,
            "is_primary": sp.is_primary,
        }
        for sp in student.student_parents
        if sp.parent
    ]

    # 5. Batches summary
    active_enrollments = [e for e in student.enrollments if e.status == EnrollmentStatus.ACTIVE]
    batches_data = [
        {
            "batch_id": e.batch.id,
            "batch_name": e.batch.name,
            "batch_code": getattr(e.batch, "code", getattr(e.batch, "name", "")),
            "course_name": e.batch.course.name if e.batch.course else None,
            "teacher_name": f"{e.batch.teacher.first_name} {e.batch.teacher.last_name}" if e.batch.teacher else None,
            "enrolled_at": e.enrollment_date.isoformat() if e.enrollment_date else None,
        }
        for e in active_enrollments
        if e.batch
    ]

    enrollment_ids = [e.id for e in student.enrollments]

    # 6. Attendance Profile
    total_sessions = 0
    attended_sessions = 0
    attendance_pct = 0.0
    if enrollment_ids:
        att_row = (
            await db.execute(
                select(
                    func.count(Attendance.id).label("total"),
                    func.count(
                        case((Attendance.status.in_([AttendanceStatus.PRESENT, AttendanceStatus.LATE]), 1))
                    ).label("attended"),
                ).where(Attendance.enrollment_id.in_(enrollment_ids))
            )
        ).one()
        total_sessions = att_row[0] or 0
        attended_sessions = att_row[1] or 0
        attendance_pct = round((attended_sessions / total_sessions * 100.0), 2) if total_sessions > 0 else 0.0

    if attendance_pct >= 90.0:
        badge = "EXCELLENT"
    elif attendance_pct >= 75.0:
        badge = "GOOD"
    elif attendance_pct >= 60.0:
        badge = "WARNING"
    else:
        badge = "CRITICAL"

    # 7. Examination Results & GPA
    test_results_stmt = (
        select(TestResult)
        .where(TestResult.student_id == student.id)
        .options(joinedload(TestResult.test))
        .order_by(TestResult.created_at.desc())
    )
    test_results = (await db.execute(test_results_stmt)).scalars().all()
    tests_taken = len(test_results)
    avg_test_pct = (
        round(sum(tr.percentage or 0.0 for tr in test_results) / tests_taken, 2)
        if tests_taken > 0
        else 0.0
    )
    scorecards = [
        {
            "test_id": tr.test_id,
            "test_title": tr.test.name if tr.test else "Test",
            "test_type": tr.test.type.value if tr.test else None,
            "marks_obtained": tr.marks_obtained,
            "total_marks": tr.test.max_marks if tr.test else None,
            "percentage": tr.percentage,
            "percentile": tr.percentile,
            "rank": tr.rank,
            "is_absent": tr.is_absent,
            "remarks": tr.remarks,
        }
        for tr in test_results
    ]

    # 8. Financial Ledger
    fee_plan_total = 0.0
    total_paid = 0.0
    installments_data = []
    receipts_data = []
    if enrollment_ids:
        fp_stmt = (
            select(FeePlan)
            .where(FeePlan.enrollment_id.in_(enrollment_ids))
            .options(selectinload(FeePlan.installments))
        )
        fee_plans = (await db.execute(fp_stmt)).scalars().all()
        for fp in fee_plans:
            fee_plan_total += float(fp.net_amount)
            for inst in fp.installments:
                total_paid += float(inst.paid_amount)
                installments_data.append(
                    {
                        "installment_number": inst.installment_number,
                        "milestone_name": f"Installment {inst.installment_number}",
                        "amount": float(inst.amount),
                        "paid_amount": float(inst.paid_amount),
                        "due_date": inst.due_date.isoformat(),
                        "status": inst.status.value,
                    }
                )

        fee_plan_ids = [fp.id for fp in fee_plans]
        if fee_plan_ids:
            rec_stmt = (
                select(Receipt, Payment)
                .join(Payment, Payment.id == Receipt.payment_id)
                .join(Installment, Installment.id == Payment.installment_id)
                .where(Installment.fee_plan_id.in_(fee_plan_ids))
                .order_by(Receipt.issued_at.desc())
            )
            receipt_rows = (await db.execute(rec_stmt)).all()
            for r, p in receipt_rows:
                rec_amount = float(p.amount)
                receipts_data.append(
                    {
                        "receipt_number": r.receipt_number,
                        "amount": rec_amount,
                        "payment_method": p.payment_method.value if p.payment_method else None,
                        "issued_at": r.issued_at.isoformat(),
                    }
                )

    pending_balance = max(0.0, fee_plan_total - total_paid)

    # 9. Homework & Submissions
    hw_batch_ids = [e.batch_id for e in active_enrollments if e.batch_id]
    total_hw_assigned = 0
    total_hw_submitted = 0
    avg_hw_marks = None
    if hw_batch_ids:
        total_hw_assigned = (
            await db.execute(
                select(func.count(Homework.id)).where(
                    Homework.batch_id.in_(hw_batch_ids),
                    Homework.deleted_at.is_(None),
                )
            )
        ).scalar_one() or 0

        sub_stmt = select(HomeworkSubmission).where(HomeworkSubmission.student_id == student.id)
        submissions = (await db.execute(sub_stmt)).scalars().all()
        total_hw_submitted = len(submissions)
        graded_marks = [s.marks for s in submissions if s.marks is not None]
        if graded_marks:
            avg_hw_marks = round(sum(graded_marks) / len(graded_marks), 2)

    hw_rate = (
        round((total_hw_submitted / total_hw_assigned * 100.0), 2)
        if total_hw_assigned > 0
        else 0.0
    )

    # 10. Teacher Remarks
    remarks_stmt = (
        select(StudentRemark)
        .where(StudentRemark.student_id == student.id)
        .options(joinedload(StudentRemark.teacher))
        .order_by(StudentRemark.created_at.desc())
    )
    remarks_list = (await db.execute(remarks_stmt)).scalars().all()
    remarks_data = [
        {
            "remark": rm.body,
            "category": "OBSERVATION",
            "author_name": f"{rm.teacher.first_name} {rm.teacher.last_name}" if rm.teacher else "Teacher",
            "date": rm.created_at.isoformat(),
        }
        for rm in remarks_list
    ]

    return Student360ProfileResponse(
        student_id=student.id,
        user_id=student.user_id,
        first_name=student.first_name,
        last_name=student.last_name,
        full_name=student.full_name,
        admission_number=student.admission_number,
        date_of_birth=student.date_of_birth,
        gender=student.gender.value if student.gender else None,
        photo_url=student.photo_url,
        joining_date=student.joining_date,
        current_class_name=current_class_name,
        guardians=guardians,
        batches=batches_data,
        total_sessions=total_sessions,
        attended_sessions=attended_sessions,
        attendance_percentage=attendance_pct,
        attendance_badge=badge,
        tests_taken=tests_taken,
        average_test_percentage=avg_test_pct,
        scorecards=scorecards,
        fee_plan_total=round(fee_plan_total, 2),
        total_paid=round(total_paid, 2),
        pending_balance=round(pending_balance, 2),
        installments=installments_data,
        receipts=receipts_data,
        total_homework_assigned=total_hw_assigned,
        total_submitted=total_hw_submitted,
        homework_completion_rate=hw_rate,
        average_homework_marks=avg_hw_marks,
        remarks=remarks_data,
    )


# ─────────────────────────────────────────────────────────────────────────────
# 6. Data Export CSV Generator
# ─────────────────────────────────────────────────────────────────────────────

async def export_data_csv(
    db: AsyncSession,
    *,
    institute_id: uuid.UUID,
    export_type: ExportType,
    filters: dict[str, Any] | None = None,
) -> tuple[str, str]:
    """Stream CSV formatted data for rosters, fee ledger, attendance, and exam marks."""
    filters = filters or {}
    output = io.StringIO()
    writer = csv.writer(output)

    if export_type == ExportType.STUDENTS_ROSTER:
        filename = f"students_roster_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}.csv"
        writer.writerow(["Student ID", "Admission Number", "First Name", "Last Name", "Gender", "DOB", "Joining Date", "Active"])
        stmt = (
            select(StudentProfile)
            .where(StudentProfile.institute_id == institute_id, StudentProfile.deleted_at.is_(None))
            .order_by(StudentProfile.last_name, StudentProfile.first_name)
        )
        students = (await db.execute(stmt)).scalars().all()
        for s in students:
            writer.writerow([
                str(s.id),
                s.admission_number or "",
                s.first_name,
                s.last_name,
                s.gender.value if s.gender else "",
                s.date_of_birth.isoformat() if s.date_of_birth else "",
                s.joining_date.isoformat() if s.joining_date else "",
                "YES" if s.is_active else "NO",
            ])

    elif export_type == ExportType.FEE_LEDGER:
        filename = f"fee_ledger_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}.csv"
        writer.writerow(["Fee Plan ID", "Student Name", "Admission No", "Plan Type", "Net Amount", "Total Paid", "Pending Balance"])
        stmt = (
            select(FeePlan)
            .where(FeePlan.institute_id == institute_id)
            .options(
                joinedload(FeePlan.enrollment).joinedload(Enrollment.student),
                selectinload(FeePlan.installments),
            )
        )
        plans = (await db.execute(stmt)).scalars().all()
        for p in plans:
            st = p.enrollment.student if p.enrollment else None
            paid = sum(inst.paid_amount for inst in p.installments)
            writer.writerow([
                str(p.id),
                st.full_name if st else "N/A",
                st.admission_number if st else "",
                p.plan_type.value,
                f"{p.net_amount:.2f}",
                f"{paid:.2f}",
                f"{(p.net_amount - paid):.2f}",
            ])

    elif export_type == ExportType.ATTENDANCE_REGISTER:
        filename = f"attendance_register_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}.csv"
        writer.writerow(["Session Date", "Batch Name", "Student Name", "Admission No", "Status", "Remarks"])
        stmt = (
            select(Attendance)
            .join(ClassSession, ClassSession.id == Attendance.class_session_id)
            .join(Enrollment, Enrollment.id == Attendance.enrollment_id)
            .join(StudentProfile, StudentProfile.id == Enrollment.student_id)
            .join(Batch, Batch.id == ClassSession.batch_id)
            .where(ClassSession.institute_id == institute_id)
            .options(
                joinedload(Attendance.class_session).joinedload(ClassSession.batch),
                joinedload(Attendance.enrollment).joinedload(Enrollment.student),
            )
            .order_by(ClassSession.date.desc())
            .limit(1000)
        )
        records = (await db.execute(stmt)).scalars().all()
        for att in records:
            writer.writerow([
                att.class_session.date.isoformat() if att.class_session else "",
                att.class_session.batch.name if att.class_session and att.class_session.batch else "",
                att.enrollment.student.full_name if att.enrollment and att.enrollment.student else "",
                att.enrollment.student.admission_number if att.enrollment and att.enrollment.student else "",
                att.status.value,
                att.remarks or "",
            ])

    elif export_type == ExportType.EXAM_RESULTS:
        filename = f"exam_results_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}.csv"
        writer.writerow(["Test Title", "Student Name", "Admission No", "Marks Obtained", "Total Marks", "Percentage", "Percentile", "Rank"])
        stmt = (
            select(TestResult)
            .join(Test, Test.id == TestResult.test_id)
            .join(StudentProfile, StudentProfile.id == TestResult.student_id)
            .where(Test.institute_id == institute_id, Test.deleted_at.is_(None))
            .options(joinedload(TestResult.test), joinedload(TestResult.student))
            .order_by(Test.created_at.desc())
            .limit(1000)
        )
        results = (await db.execute(stmt)).scalars().all()
        for tr in results:
            writer.writerow([
                tr.test.name if tr.test else "",
                tr.student.full_name if tr.student else "",
                tr.student.admission_number if tr.student else "",
                tr.marks_obtained if tr.marks_obtained is not None else "ABSENT",
                tr.test.max_marks if tr.test else "",
                f"{tr.percentage:.2f}" if tr.percentage is not None else "",
                f"{tr.percentile:.2f}" if tr.percentile is not None else "",
                tr.rank or "",
            ])

    return output.getvalue(), filename


# ─────────────────────────────────────────────────────────────────────────────
# 7. Materialized View Refresh
# ─────────────────────────────────────────────────────────────────────────────

async def refresh_materialized_views(
    db: AsyncSession,
    *,
    institute_id: uuid.UUID,
) -> MaterializedViewRefreshResponse:
    """Trigger background refresh of PostgreSQL materialized views."""
    await db.execute(text("REFRESH MATERIALIZED VIEW CONCURRENTLY mv_batch_performance_summary"))
    logger.info("Materialized views refreshed", extra={"institute_id": str(institute_id)})
    return MaterializedViewRefreshResponse(
        refreshed_at=datetime.now(timezone.utc),
        views_refreshed=["mv_batch_performance_summary"],
    )
