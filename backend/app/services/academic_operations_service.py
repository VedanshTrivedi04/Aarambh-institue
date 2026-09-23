"""
app/services/academic_operations_service.py
-------------------------------------------
Service layer for academic operations:
  - Timetables & calendar session generation
  - ClassSessions & session log delivery tracking
  - Attendance Engine with ReBAC authority checks and bulk upsert
  - Student attendance metrics calculation
  - Student remarks (teacher feedback visible to parents)
"""

from __future__ import annotations

import uuid
from datetime import UTC, date, datetime, timedelta

from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.exceptions import (
    ConflictError,
    ForbiddenError,
    NotFoundError,
    ValidationError,
)
from app.core.logging import get_logger
from app.models.academic_operations import (
    Attendance,
    AttendanceStatus,
    ClassSession,
    ClassSessionStatus,
    SessionLog,
    StudentRemark,
    Timetable,
)
from app.models.academic_structure import Batch, DayOfWeek
from app.models.enrollment import Enrollment, EnrollmentStatus
from app.models.people import StudentProfile, TeacherProfile
from app.models.user import User
from app.schemas.academic_operations import (
    AttendanceRecordInput,
    ClassSessionCreate,
    ClassSessionUpdate,
    SessionAttendanceSheetItem,
    SessionLogCreate,
    SessionRescheduleRequest,
    StudentAttendanceSummary,
    StudentRemarkCreate,
    TimetableCreate,
    TimetableUpdate,
)

logger = get_logger(__name__)

_DAY_MAP = {
    0: DayOfWeek.MONDAY,
    1: DayOfWeek.TUESDAY,
    2: DayOfWeek.WEDNESDAY,
    3: DayOfWeek.THURSDAY,
    4: DayOfWeek.FRIDAY,
    5: DayOfWeek.SATURDAY,
    6: DayOfWeek.SUNDAY,
}


class AcademicOperationsService:
    """Core academic delivery and attendance engine."""

    # ─────────────────────────────────────────────────────────────────────────
    # Timetable & Session Generation
    # ─────────────────────────────────────────────────────────────────────────

    @staticmethod
    async def create_timetable(
        db: AsyncSession,
        data: TimetableCreate,
        institute_id: uuid.UUID | None,
    ) -> Timetable:
        batch = await db.get(Batch, data.batch_id)
        if not batch or batch.deleted_at is not None:
            raise NotFoundError(f"Batch {data.batch_id} not found")

        timetable = Timetable(
            institute_id=institute_id,
            batch_id=data.batch_id,
            day_of_week=data.day_of_week,
            start_time=data.start_time,
            end_time=data.end_time,
            room=data.room,
        )
        db.add(timetable)
        await db.flush()
        await db.refresh(timetable)
        logger.info("Created timetable rule", extra={"batch_id": str(data.batch_id), "day": data.day_of_week.value})
        return timetable

    @staticmethod
    async def list_batch_timetables(
        db: AsyncSession,
        batch_id: uuid.UUID,
        institute_id: uuid.UUID | None,
    ) -> list[Timetable]:
        query = select(Timetable).where(
            Timetable.batch_id == batch_id,
            Timetable.deleted_at.is_(None),
            Timetable.is_active.is_(True),
        )
        if institute_id:
            query = query.where(Timetable.institute_id == institute_id)
        return list((await db.scalars(query)).all())

    @staticmethod
    async def generate_sessions_from_timetable(
        db: AsyncSession,
        batch_id: uuid.UUID,
        start_date: date,
        end_date: date,
        institute_id: uuid.UUID | None,
    ) -> list[ClassSession]:
        """Generate concrete ClassSession rows between start_date and end_date based on Timetables."""
        if start_date > end_date:
            raise ValidationError("start_date cannot be after end_date")

        batch = await db.get(Batch, batch_id)
        if not batch or batch.deleted_at is not None:
            raise NotFoundError(f"Batch {batch_id} not found")

        timetables = await AcademicOperationsService.list_batch_timetables(db, batch_id, institute_id)
        if not timetables:
            return []

        # Group by day_of_week
        rules_by_day: dict[DayOfWeek, list[Timetable]] = {}
        for t in timetables:
            rules_by_day.setdefault(t.day_of_week, []).append(t)

        created_sessions: list[ClassSession] = []
        cur = start_date
        while cur <= end_date:
            weekday_enum = _DAY_MAP[cur.weekday()]
            if weekday_enum in rules_by_day:
                for rule in rules_by_day[weekday_enum]:
                    # Check if session already exists for this batch, date, start_time
                    existing = await db.scalar(
                        select(ClassSession).where(
                            ClassSession.batch_id == batch_id,
                            ClassSession.date == cur,
                            ClassSession.start_time == rule.start_time,
                            ClassSession.deleted_at.is_(None),
                        )
                    )
                    if not existing:
                        session = ClassSession(
                            institute_id=institute_id,
                            batch_id=batch_id,
                            date=cur,
                            start_time=rule.start_time,
                            end_time=rule.end_time,
                            room=rule.room,
                            status=ClassSessionStatus.SCHEDULED,
                            conducted_by=batch.teacher_id,
                        )
                        db.add(session)
                        created_sessions.append(session)
            cur += timedelta(days=1)

        await db.flush()
        logger.info(
            "Generated class sessions from timetable",
            extra={"batch_id": str(batch_id), "count": len(created_sessions)},
        )
        return created_sessions

    # ─────────────────────────────────────────────────────────────────────────
    # ClassSession CRUD & Rescheduling
    # ─────────────────────────────────────────────────────────────────────────

    @staticmethod
    async def create_session(
        db: AsyncSession,
        data: ClassSessionCreate,
        institute_id: uuid.UUID | None,
    ) -> ClassSession:
        batch = await db.get(Batch, data.batch_id)
        if not batch or batch.deleted_at is not None:
            raise NotFoundError(f"Batch {data.batch_id} not found")

        session = ClassSession(
            institute_id=institute_id,
            batch_id=data.batch_id,
            date=data.date,
            start_time=data.start_time,
            end_time=data.end_time,
            room=data.room,
            status=ClassSessionStatus.SCHEDULED,
            conducted_by=data.conducted_by or batch.teacher_id,
            remarks=data.remarks,
        )
        db.add(session)
        await db.flush()
        await db.refresh(session)
        return session

    @staticmethod
    async def get_session(
        db: AsyncSession,
        session_id: uuid.UUID,
        institute_id: uuid.UUID | None,
    ) -> ClassSession:
        query = select(ClassSession).where(
            ClassSession.id == session_id,
            ClassSession.deleted_at.is_(None),
        )
        if institute_id:
            query = query.where(ClassSession.institute_id == institute_id)
        session = await db.scalar(query)
        if not session:
            raise NotFoundError(f"Class session {session_id} not found")
        return session

    @staticmethod
    async def update_session(
        db: AsyncSession,
        session_id: uuid.UUID,
        data: ClassSessionUpdate,
        institute_id: uuid.UUID | None,
    ) -> ClassSession:
        session = await AcademicOperationsService.get_session(db, session_id, institute_id)
        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(session, field, value)
        await db.flush()
        await db.refresh(session)
        return session

    @staticmethod
    async def reschedule_session(
        db: AsyncSession,
        session_id: uuid.UUID,
        request: SessionRescheduleRequest,
        institute_id: uuid.UUID | None,
    ) -> tuple[ClassSession, ClassSession]:
        """
        Reschedules an existing class session.
        Marks old session RESCHEDULED with a link to the new session.
        """
        old_session = await AcademicOperationsService.get_session(db, session_id, institute_id)
        if old_session.status in (ClassSessionStatus.HELD, ClassSessionStatus.CANCELLED):
            raise ValidationError(f"Cannot reschedule session with status '{old_session.status.value}'")

        # Create replacement session
        new_session = ClassSession(
            institute_id=old_session.institute_id,
            batch_id=old_session.batch_id,
            date=request.new_date,
            start_time=request.new_start_time,
            end_time=request.new_end_time,
            room=request.new_room or old_session.room,
            status=ClassSessionStatus.SCHEDULED,
            conducted_by=old_session.conducted_by,
            remarks=f"Rescheduled from {old_session.date} {old_session.start_time}. Reason: {request.reason}",
        )
        db.add(new_session)
        await db.flush()

        # Update old session
        old_session.status = ClassSessionStatus.RESCHEDULED
        old_session.rescheduled_to_session_id = new_session.id
        old_session.remarks = f"Rescheduled to {request.new_date} {request.new_start_time}. Reason: {request.reason}"

        await db.flush()
        await db.refresh(old_session)
        await db.refresh(new_session)
        logger.info(
            "Rescheduled class session",
            extra={"old_session_id": str(old_session.id), "new_session_id": str(new_session.id)},
        )
        return old_session, new_session

    @staticmethod
    async def list_sessions(
        db: AsyncSession,
        institute_id: uuid.UUID | None,
        batch_id: uuid.UUID | None = None,
        date_from: date | None = None,
        date_to: date | None = None,
        session_status: ClassSessionStatus | None = None,
        skip: int = 0,
        limit: int = 50,
    ) -> tuple[list[ClassSession], int]:
        base_query = select(ClassSession).where(ClassSession.deleted_at.is_(None))
        if institute_id:
            base_query = base_query.where(ClassSession.institute_id == institute_id)
        if batch_id:
            base_query = base_query.where(ClassSession.batch_id == batch_id)
        if date_from:
            base_query = base_query.where(ClassSession.date >= date_from)
        if date_to:
            base_query = base_query.where(ClassSession.date <= date_to)
        if session_status:
            base_query = base_query.where(ClassSession.status == session_status)

        total = await db.scalar(select(func.count()).select_from(base_query.subquery())) or 0
        items = (
            await db.scalars(
                base_query.order_by(ClassSession.date.desc(), ClassSession.start_time.desc())
                .offset(skip)
                .limit(limit)
            )
        ).all()
        return list(items), total

    # ─────────────────────────────────────────────────────────────────────────
    # SessionLog CRUD
    # ─────────────────────────────────────────────────────────────────────────

    @staticmethod
    async def save_session_log(
        db: AsyncSession,
        session_id: uuid.UUID,
        data: SessionLogCreate,
        institute_id: uuid.UUID | None,
        author_id: uuid.UUID | None = None,
    ) -> SessionLog:
        session = await AcademicOperationsService.get_session(db, session_id, institute_id)

        # Check existing log
        log = await db.scalar(
            select(SessionLog).where(SessionLog.class_session_id == session_id)
        )
        if log:
            log.topic = data.topic
            log.topics_covered = data.topics_covered
            log.homework_notes = data.homework_notes
            log.class_remarks = data.class_remarks
        else:
            log = SessionLog(
                class_session_id=session_id,
                topic=data.topic,
                topics_covered=data.topics_covered,
                homework_notes=data.homework_notes,
                class_remarks=data.class_remarks,
                created_by=author_id,
            )
            db.add(log)

        # Auto-advance session status to HELD if currently SCHEDULED
        if session.status == ClassSessionStatus.SCHEDULED:
            session.status = ClassSessionStatus.HELD

        await db.flush()
        await db.refresh(log)
        logger.info("Saved session log", extra={"session_id": str(session_id), "topic": log.topic})
        return log

    @staticmethod
    async def get_session_log(
        db: AsyncSession,
        session_id: uuid.UUID,
        institute_id: uuid.UUID | None,
    ) -> SessionLog:
        await AcademicOperationsService.get_session(db, session_id, institute_id)
        log = await db.scalar(
            select(SessionLog).where(SessionLog.class_session_id == session_id)
        )
        if not log:
            raise NotFoundError(f"No session log recorded for session {session_id}")
        return log

    # ─────────────────────────────────────────────────────────────────────────
    # Attendance Engine with ReBAC
    # ─────────────────────────────────────────────────────────────────────────

    @staticmethod
    async def verify_attendance_authority(
        db: AsyncSession,
        session: ClassSession,
        current_user: User,
    ) -> None:
        """
        ReBAC check (rules.md §5):
        - ADMIN / SUPER_ADMIN / MANAGEMENT can mark attendance for any session.
        - TEACHER can ONLY mark attendance for sessions where they are assigned to the batch or session.
        """
        if current_user.role in ("SUPER_ADMIN", "ADMIN", "MANAGEMENT"):
            return

        if current_user.role == "TEACHER":
            teacher_profile = await db.scalar(
                select(TeacherProfile).where(
                    TeacherProfile.user_id == current_user.id,
                    TeacherProfile.deleted_at.is_(None),
                )
            )
            if not teacher_profile:
                raise ForbiddenError("Teacher profile not configured for your user account")

            # Check if teacher is assigned to this session or batch
            batch = await db.get(Batch, session.batch_id)
            if session.conducted_by == teacher_profile.id or (batch and batch.teacher_id == teacher_profile.id):
                return
            raise ForbiddenError("You are not authorized to mark attendance for this batch")

        raise ForbiddenError("Insufficient permissions to mark attendance")

    @staticmethod
    async def bulk_mark_attendance(
        db: AsyncSession,
        session_id: uuid.UUID,
        records: list[AttendanceRecordInput],
        current_user: User,
    ) -> int:
        """
        Mark or update attendance for students in a class session.
        Enforces:
          1. ReBAC teacher assignment check.
          2. Enrollment batch membership check.
          3. Upsert behavior (updates existing or inserts new).
          4. Automatically marks ClassSession as HELD.
        """
        session = await AcademicOperationsService.get_session(db, session_id, current_user.institute_id)
        await AcademicOperationsService.verify_attendance_authority(db, session, current_user)

        # Fetch all active enrollments for this session's batch
        valid_enrollments = {
            e.id: e
            for e in (
                await db.scalars(
                    select(Enrollment).where(
                        Enrollment.batch_id == session.batch_id,
                    )
                )
            ).all()
        }

        # Fetch existing attendance rows for this session
        existing_rows = {
            a.enrollment_id: a
            for a in (
                await db.scalars(
                    select(Attendance).where(Attendance.class_session_id == session_id)
                )
            ).all()
        }

        now_utc = datetime.now(UTC)
        count_marked = 0

        for r in records:
            if r.enrollment_id not in valid_enrollments:
                raise ValidationError(
                    f"Enrollment {r.enrollment_id} does not belong to batch {session.batch_id}"
                )

            if r.enrollment_id in existing_rows:
                # Update existing
                row = existing_rows[r.enrollment_id]
                row.status = r.status
                row.remarks = r.remarks
                row.marked_by = current_user.id
                row.marked_at = now_utc
            else:
                # Insert new
                new_row = Attendance(
                    class_session_id=session_id,
                    enrollment_id=r.enrollment_id,
                    status=r.status,
                    remarks=r.remarks,
                    marked_by=current_user.id,
                    marked_at=now_utc,
                )
                db.add(new_row)

            count_marked += 1

        # Advance session to HELD
        if session.status == ClassSessionStatus.SCHEDULED:
            session.status = ClassSessionStatus.HELD

        await db.flush()
        logger.info(
            "Bulk marked attendance",
            extra={"session_id": str(session_id), "count": count_marked},
        )
        return count_marked

    @staticmethod
    async def get_session_attendance_sheet(
        db: AsyncSession,
        session_id: uuid.UUID,
        institute_id: uuid.UUID | None,
    ) -> list[SessionAttendanceSheetItem]:
        """Returns the full roster of enrolled students with their marked status for this session."""
        session = await AcademicOperationsService.get_session(db, session_id, institute_id)

        # Get active enrollments for this batch + student profiles
        query = (
            select(Enrollment, StudentProfile, Attendance)
            .join(StudentProfile, StudentProfile.id == Enrollment.student_id)
            .outerjoin(
                Attendance,
                (Attendance.enrollment_id == Enrollment.id)
                & (Attendance.class_session_id == session_id),
            )
            .where(
                Enrollment.batch_id == session.batch_id,
                Enrollment.status == EnrollmentStatus.ACTIVE,
                StudentProfile.deleted_at.is_(None),
            )
            .order_by(StudentProfile.first_name, StudentProfile.last_name)
        )

        results = (await db.execute(query)).all()
        sheet: list[SessionAttendanceSheetItem] = []
        for enrollment, student, att in results:
            sheet.append(
                SessionAttendanceSheetItem(
                    enrollment_id=enrollment.id,
                    student_id=student.id,
                    student_name=student.full_name,
                    admission_number=student.admission_number,
                    status=att.status if att else None,
                    remarks=att.remarks if att else None,
                )
            )
        return sheet

    @staticmethod
    async def get_student_attendance_summary(
        db: AsyncSession,
        student_id: uuid.UUID,
        batch_id: uuid.UUID | None = None,
        institute_id: uuid.UUID | None = None,
    ) -> StudentAttendanceSummary:
        """Compute aggregated attendance metrics for a student."""
        # Find student's enrollments
        enr_query = select(Enrollment.id).where(Enrollment.student_id == student_id)
        if batch_id:
            enr_query = enr_query.where(Enrollment.batch_id == batch_id)
        if institute_id:
            enr_query = enr_query.where(Enrollment.institute_id == institute_id)
        enrollment_ids = list((await db.scalars(enr_query)).all())

        if not enrollment_ids:
            return StudentAttendanceSummary(
                student_id=student_id,
                batch_id=batch_id,
                total_sessions=0,
                present_count=0,
                absent_count=0,
                late_count=0,
                excused_count=0,
                attendance_percentage=100.0,
            )

        # Query all attendance records for these enrollments
        att_query = select(Attendance.status, func.count(Attendance.id)).where(
            Attendance.enrollment_id.in_(enrollment_ids)
        ).group_by(Attendance.status)

        counts = dict((await db.execute(att_query)).all())
        present = counts.get(AttendanceStatus.PRESENT, 0)
        absent = counts.get(AttendanceStatus.ABSENT, 0)
        late = counts.get(AttendanceStatus.LATE, 0)
        excused = counts.get(AttendanceStatus.EXCUSED, 0)
        total = present + absent + late + excused

        pct = 100.0 if total == 0 else round(((present + (0.5 * late)) / total) * 100, 2)

        return StudentAttendanceSummary(
            student_id=student_id,
            batch_id=batch_id,
            total_sessions=total,
            present_count=present,
            absent_count=absent,
            late_count=late,
            excused_count=excused,
            attendance_percentage=pct,
        )

    # ─────────────────────────────────────────────────────────────────────────
    # Student Remarks
    # ─────────────────────────────────────────────────────────────────────────

    @staticmethod
    async def create_student_remark(
        db: AsyncSession,
        data: StudentRemarkCreate,
        teacher_user: User,
        institute_id: uuid.UUID | None,
    ) -> StudentRemark:
        teacher = await db.scalar(
            select(TeacherProfile).where(
                TeacherProfile.user_id == teacher_user.id,
                TeacherProfile.deleted_at.is_(None),
            )
        )
        if not teacher:
            raise ForbiddenError("Only teachers with a configured profile can write student remarks")

        student = await db.get(StudentProfile, data.student_id)
        if not student or student.deleted_at is not None:
            raise NotFoundError(f"Student profile {data.student_id} not found")

        remark = StudentRemark(
            institute_id=institute_id,
            student_id=data.student_id,
            teacher_id=teacher.id,
            class_session_id=data.class_session_id,
            body=data.body,
            visible_to_parent=data.visible_to_parent,
        )
        db.add(remark)
        await db.flush()
        await db.refresh(remark)
        logger.info("Recorded student remark", extra={"student_id": str(data.student_id), "teacher_id": str(teacher.id)})
        return remark

    @staticmethod
    async def list_student_remarks(
        db: AsyncSession,
        student_id: uuid.UUID,
        parent_view: bool = False,
        institute_id: uuid.UUID | None = None,
    ) -> list[StudentRemark]:
        query = select(StudentRemark).where(StudentRemark.student_id == student_id)
        if institute_id:
            query = query.where(StudentRemark.institute_id == institute_id)
        if parent_view:
            query = query.where(StudentRemark.visible_to_parent.is_(True))
        query = query.order_by(StudentRemark.created_at.desc())
        return list((await db.scalars(query)).all())
