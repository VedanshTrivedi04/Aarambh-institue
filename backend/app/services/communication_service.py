"""
app/services/communication_service.py
-------------------------------------
Business logic for Slice 10: Communication, Notifications & Relationship-Based Messaging.

Key Architecture Invariants:
  1. Derived Contact Graph:
     - Students/Parents cannot message arbitrary teachers. They can only message
       teachers currently assigned to batches the student is actively enrolled in.
     - Teachers can message students enrolled in their assigned batches and their linked parents.
  2. Moderation & Safety:
     - Inappropriate messages can be reported by participants.
     - Admins review and take action (e.g. MESSAGE_HIDDEN, WARNING_ISSUED).
  3. Parent-Teacher Meeting (PTM) State Machine:
     - Parent requests meeting with eligible teacher.
     - Teacher/Admin approves, rejects, reschedules, or completes.
  4. In-App Notifications:
     - Automatic delivery on messages, PTM status transitions, and broadcast bulletins.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any

from fastapi import Request
from sqlalchemy import and_, func, or_, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, selectinload

from app.core.exceptions import (
    ConflictError,
    ForbiddenError,
    NotFoundError,
    ValidationError,
)
from app.core.logging import get_logger
from app.models.academic_structure import Batch, Course, SchoolClass, Subject
from app.models.communication import (
    Announcement,
    Conversation,
    ConversationParticipant,
    ConversationType,
    Message,
    Notification,
    NotificationType,
    PTMRequest,
    PTMStatus,
    ReportStatus,
    ReportedMessage,
)
from app.models.enrollment import Enrollment, EnrollmentStatus
from app.models.people import ParentProfile, StudentParent, StudentProfile, TeacherProfile
from app.models.user import User
from app.schemas.communication import (
    AnnouncementCreate,
    ConversationCreate,
    EligibleContactRead,
    MessageCreate,
    PTMRequestCreate,
    PTMStatusUpdate,
    ReportMessageCreate,
    ResolveReportRequest,
)
from app.services import audit_service

logger = get_logger("services.communication")


# ─────────────────────────────────────────────────────────────────────────────
# 1. Dynamic Derived Contact Graph Engine
# ─────────────────────────────────────────────────────────────────────────────

async def get_eligible_contacts(
    db: AsyncSession,
    *,
    institute_id: uuid.UUID,
    current_user: User,
) -> list[EligibleContactRead]:
    """
    Computes real-time allowable messaging contacts derived from active batch enrollments.
    """
    contacts: dict[uuid.UUID, EligibleContactRead] = {}

    # 1. If Admin / Super Admin: can contact any teacher or student
    if current_user.role in ("SUPER_ADMIN", "ADMIN"):
        t_stmt = (
            select(TeacherProfile)
            .where(TeacherProfile.institute_id == institute_id, TeacherProfile.is_active.is_(True))
            .options(joinedload(TeacherProfile.user))
        )
        for t in (await db.execute(t_stmt)).scalars().all():
            if t.user_id != current_user.id:
                contacts[t.user_id] = EligibleContactRead(
                    user_id=t.user_id,
                    profile_id=t.id,
                    full_name=f"{t.first_name} {t.last_name}",
                    role="TEACHER",
                    email=t.user.email if t.user else None,
                )
        return list(contacts.values())

    # 2. If Student: can message teachers of their actively enrolled batches
    if current_user.role == "STUDENT":
        s_stmt = select(StudentProfile.id).where(StudentProfile.user_id == current_user.id)
        student_id = (await db.execute(s_stmt)).scalar_one_or_none()
        if not student_id:
            return []

        enroll_stmt = (
            select(Enrollment)
            .where(
                Enrollment.student_id == student_id,
                Enrollment.status == EnrollmentStatus.ACTIVE,
            )
            .options(
                joinedload(Enrollment.batch).joinedload(Batch.teacher).joinedload(TeacherProfile.user),
                joinedload(Enrollment.batch).joinedload(Batch.subject),
            )
        )
        enrollments = (await db.execute(enroll_stmt)).scalars().all()

        for e in enrollments:
            if e.batch and e.batch.teacher and e.batch.teacher.user:
                teacher = e.batch.teacher
                t_user = teacher.user
                if t_user.id not in contacts:
                    contacts[t_user.id] = EligibleContactRead(
                        user_id=t_user.id,
                        profile_id=teacher.id,
                        full_name=f"{teacher.first_name} {teacher.last_name}",
                        role="TEACHER",
                        email=t_user.email,
                        subject_names=[e.batch.subject.name] if e.batch.subject else [],
                        batch_names=[e.batch.name],
                    )
                else:
                    if e.batch.subject and e.batch.subject.name not in contacts[t_user.id].subject_names:
                        contacts[t_user.id].subject_names.append(e.batch.subject.name)
                    if e.batch.name not in contacts[t_user.id].batch_names:
                        contacts[t_user.id].batch_names.append(e.batch.name)

        return list(contacts.values())

    # 3. If Parent: can message teachers of their linked children's actively enrolled batches
    if current_user.role == "PARENT":
        p_stmt = select(ParentProfile.id).where(ParentProfile.user_id == current_user.id)
        parent_id = (await db.execute(p_stmt)).scalar_one_or_none()
        if not parent_id:
            return []

        children_stmt = select(StudentParent.student_id).where(StudentParent.parent_id == parent_id)
        student_ids = (await db.execute(children_stmt)).scalars().all()
        if not student_ids:
            return []

        enroll_stmt = (
            select(Enrollment)
            .where(
                Enrollment.student_id.in_(student_ids),
                Enrollment.status == EnrollmentStatus.ACTIVE,
            )
            .options(
                joinedload(Enrollment.batch).joinedload(Batch.teacher).joinedload(TeacherProfile.user),
                joinedload(Enrollment.batch).joinedload(Batch.subject),
            )
        )
        enrollments = (await db.execute(enroll_stmt)).scalars().all()

        for e in enrollments:
            if e.batch and e.batch.teacher and e.batch.teacher.user:
                teacher = e.batch.teacher
                t_user = teacher.user
                if t_user.id not in contacts:
                    contacts[t_user.id] = EligibleContactRead(
                        user_id=t_user.id,
                        profile_id=teacher.id,
                        full_name=f"{teacher.first_name} {teacher.last_name}",
                        role="TEACHER",
                        email=t_user.email,
                        subject_names=[e.batch.subject.name] if e.batch.subject else [],
                        batch_names=[e.batch.name],
                    )
                else:
                    if e.batch.subject and e.batch.subject.name not in contacts[t_user.id].subject_names:
                        contacts[t_user.id].subject_names.append(e.batch.subject.name)
                    if e.batch.name not in contacts[t_user.id].batch_names:
                        contacts[t_user.id].batch_names.append(e.batch.name)

        return list(contacts.values())

    # 4. If Teacher: can message students enrolled in their assigned batches and their linked parents
    if current_user.role == "TEACHER":
        t_stmt = select(TeacherProfile.id).where(TeacherProfile.user_id == current_user.id)
        teacher_id = (await db.execute(t_stmt)).scalar_one_or_none()
        if not teacher_id:
            return []

        batches_stmt = select(Batch.id).where(Batch.teacher_id == teacher_id, Batch.is_active.is_(True))
        batch_ids = (await db.execute(batches_stmt)).scalars().all()
        if not batch_ids:
            return []

        enroll_stmt = (
            select(Enrollment)
            .where(
                Enrollment.batch_id.in_(batch_ids),
                Enrollment.status == EnrollmentStatus.ACTIVE,
            )
            .options(
                joinedload(Enrollment.student).joinedload(StudentProfile.user),
                joinedload(Enrollment.student).selectinload(StudentProfile.student_parents).joinedload(StudentParent.parent).joinedload(ParentProfile.user),
                joinedload(Enrollment.batch),
            )
        )
        enrollments = (await db.execute(enroll_stmt)).scalars().all()

        for e in enrollments:
            if e.student and e.student.user:
                st = e.student
                st_user = st.user
                if st_user.id not in contacts:
                    contacts[st_user.id] = EligibleContactRead(
                        user_id=st_user.id,
                        profile_id=st.id,
                        full_name=f"{st.first_name} {st.last_name or ''}".strip(),
                        role="STUDENT",
                        email=st_user.email,
                        batch_names=[e.batch.name] if e.batch else [],
                    )
                # Also include linked parents
                for sp in (st.student_parents or []):
                    if sp.parent and sp.parent.user:
                        pt = sp.parent
                        pt_user = pt.user
                        if pt_user.id not in contacts:
                            contacts[pt_user.id] = EligibleContactRead(
                                user_id=pt_user.id,
                                profile_id=pt.id,
                                full_name=f"{pt.first_name} {pt.last_name}",
                                role="PARENT",
                                email=pt_user.email,
                                batch_names=[e.batch.name] if e.batch else [],
                            )

        return list(contacts.values())

    return []


async def _assert_can_communicate(
    db: AsyncSession,
    *,
    institute_id: uuid.UUID,
    sender_user: User,
    target_user_ids: list[uuid.UUID],
) -> None:
    """Validate that the sender is authorized to initiate conversations with target users."""
    if sender_user.role in ("SUPER_ADMIN", "ADMIN"):
        return

    eligible = await get_eligible_contacts(db, institute_id=institute_id, current_user=sender_user)
    eligible_ids = {c.user_id for c in eligible}

    for tid in target_user_ids:
        if tid == sender_user.id:
            continue
        if tid not in eligible_ids:
            raise ForbiddenError(
                f"You do not have permission to message user {tid} based on current batch assignments."
            )


# ─────────────────────────────────────────────────────────────────────────────
# 2. In-App Notifications
# ─────────────────────────────────────────────────────────────────────────────

async def create_notification(
    db: AsyncSession,
    *,
    institute_id: uuid.UUID,
    user_id: uuid.UUID,
    title: str,
    body: str,
    type: NotificationType = NotificationType.ACADEMIC,
    related_entity_type: str | None = None,
    related_entity_id: str | None = None,
) -> Notification:
    """Create a persistent in-app notification for a user."""
    notif = Notification(
        institute_id=institute_id,
        user_id=user_id,
        title=title,
        body=body,
        type=type,
        related_entity_type=related_entity_type,
        related_entity_id=related_entity_id,
        is_read=False,
    )
    db.add(notif)
    await db.flush()
    return notif


async def list_notifications(
    db: AsyncSession,
    *,
    institute_id: uuid.UUID,
    user_id: uuid.UUID,
    is_read: bool | None = None,
    limit: int = 50,
) -> list[Notification]:
    """List notifications for a user."""
    stmt = (
        select(Notification)
        .where(
            Notification.user_id == user_id,
            Notification.institute_id == institute_id,
        )
        .order_by(Notification.created_at.desc())
        .limit(limit)
    )
    if is_read is not None:
        stmt = stmt.where(Notification.is_read == is_read)

    return list((await db.execute(stmt)).scalars().all())


async def get_unread_notification_count(
    db: AsyncSession,
    *,
    institute_id: uuid.UUID,
    user_id: uuid.UUID,
) -> int:
    """Count unread notifications for quick badge rendering."""
    stmt = (
        select(func.count(Notification.id))
        .where(
            Notification.user_id == user_id,
            Notification.institute_id == institute_id,
            Notification.is_read.is_(False),
        )
    )
    return (await db.execute(stmt)).scalar_one() or 0


async def mark_notifications_as_read(
    db: AsyncSession,
    *,
    institute_id: uuid.UUID,
    user_id: uuid.UUID,
    notification_ids: list[uuid.UUID] | None = None,
) -> int:
    """Mark specific or all notifications as read."""
    stmt = (
        update(Notification)
        .where(
            Notification.user_id == user_id,
            Notification.institute_id == institute_id,
            Notification.is_read.is_(False),
        )
        .values(is_read=True, read_at=datetime.now(timezone.utc))
    )
    if notification_ids:
        stmt = stmt.where(Notification.id.in_(notification_ids))

    res = await db.execute(stmt)
    return res.rowcount


# ─────────────────────────────────────────────────────────────────────────────
# 3. Conversations & Messages
# ─────────────────────────────────────────────────────────────────────────────

async def create_conversation(
    db: AsyncSession,
    *,
    institute_id: uuid.UUID,
    creator_user: User,
    payload: ConversationCreate,
    request: Request | None = None,
) -> Conversation:
    """Create a new conversation thread after verifying relationship-based contact eligibility."""
    # 1. Check contact graph permission
    await _assert_can_communicate(
        db,
        institute_id=institute_id,
        sender_user=creator_user,
        target_user_ids=payload.participant_user_ids,
    )

    # 2. Check if a direct 1-on-1 conversation already exists between these 2 users
    if payload.type in (ConversationType.DIRECT_STUDENT_TEACHER, ConversationType.DIRECT_PARENT_TEACHER) and len(payload.participant_user_ids) == 1:
        other_user_id = payload.participant_user_ids[0]
        # Find shared 2-person conversation
        existing_stmt = (
            select(Conversation)
            .join(Conversation.participants)
            .where(
                Conversation.institute_id == institute_id,
                Conversation.type == payload.type,
                Conversation.deleted_at.is_(None),
                ConversationParticipant.user_id.in_([creator_user.id, other_user_id]),
            )
            .group_by(Conversation.id)
            .having(func.count(ConversationParticipant.user_id) == 2)
            .options(
                selectinload(Conversation.participants).joinedload(ConversationParticipant.user),
                selectinload(Conversation.messages).joinedload(Message.sender),
            )
        )
        existing = (await db.execute(existing_stmt)).scalar_one_or_none()
        if existing:
            return existing

    # 3. Create conversation
    conv = Conversation(
        institute_id=institute_id,
        type=payload.type,
        batch_id=payload.batch_id,
        title=payload.title,
    )
    db.add(conv)
    await db.flush()

    # 4. Add Creator
    creator_part = ConversationParticipant(
        conversation_id=conv.id,
        user_id=creator_user.id,
        role_in_conversation=creator_user.role,
        last_read_at=datetime.now(timezone.utc),
    )
    db.add(creator_part)

    # 5. Add other participants
    users_stmt = select(User).where(User.id.in_(payload.participant_user_ids), User.institute_id == institute_id)
    other_users = (await db.execute(users_stmt)).scalars().all()
    if len(other_users) != len(set(payload.participant_user_ids)):
        raise NotFoundError("One or more participant users not found in this institute.")

    for u in other_users:
        part = ConversationParticipant(
            conversation_id=conv.id,
            user_id=u.id,
            role_in_conversation=u.role,
        )
        db.add(part)

    await db.flush()
    await db.refresh(conv)

    # 6. Audit log
    await audit_service.log(
        db=db,
        actor=creator_user,
        action="conversation.created",
        entity_name="conversations",
        entity_id=str(conv.id),
        new_values={
            "type": conv.type.value,
            "participants": [str(uid) for uid in payload.participant_user_ids],
            "batch_id": str(conv.batch_id) if conv.batch_id else None,
        },
        request=request,
        institute_id=institute_id,
    )

    return await get_conversation(
        db, institute_id=institute_id, conversation_id=conv.id, current_user=creator_user
    )


async def list_user_conversations(
    db: AsyncSession,
    *,
    institute_id: uuid.UUID,
    user_id: uuid.UUID,
) -> list[Conversation]:
    """Fetch all conversations for a user ordered by last activity."""
    stmt = (
        select(Conversation)
        .join(Conversation.participants)
        .where(
            ConversationParticipant.user_id == user_id,
            Conversation.institute_id == institute_id,
            Conversation.deleted_at.is_(None),
        )
        .options(
            selectinload(Conversation.participants).joinedload(ConversationParticipant.user),
            selectinload(Conversation.batch),
            selectinload(Conversation.messages).joinedload(Message.sender),
        )
        .order_by(Conversation.updated_at.desc())
    )
    return list((await db.execute(stmt)).scalars().all())


async def get_conversation(
    db: AsyncSession,
    *,
    institute_id: uuid.UUID,
    conversation_id: uuid.UUID,
    current_user: User,
) -> Conversation:
    """Fetch conversation by ID, ensuring user is a participant or admin."""
    stmt = (
        select(Conversation)
        .where(
            Conversation.id == conversation_id,
            Conversation.institute_id == institute_id,
            Conversation.deleted_at.is_(None),
        )
        .options(
            selectinload(Conversation.participants).joinedload(ConversationParticipant.user),
            selectinload(Conversation.batch),
            selectinload(Conversation.messages).joinedload(Message.sender),
        )
    )
    conv = (await db.execute(stmt)).scalar_one_or_none()
    if not conv:
        raise NotFoundError(f"Conversation {conversation_id} not found.")

    if current_user.role not in ("SUPER_ADMIN", "ADMIN"):
        is_participant = any(p.user_id == current_user.id for p in conv.participants)
        if not is_participant:
            raise ForbiddenError("You are not a participant in this conversation.")

    return conv


async def send_message(
    db: AsyncSession,
    *,
    institute_id: uuid.UUID,
    conversation_id: uuid.UUID,
    sender_user: User,
    payload: MessageCreate,
    request: Request | None = None,
) -> Message:
    """Send an immutable message into a conversation and push notifications to other participants."""
    conv = await get_conversation(
        db, institute_id=institute_id, conversation_id=conversation_id, current_user=sender_user
    )

    # 1. Create message
    msg = Message(
        conversation_id=conv.id,
        sender_id=sender_user.id,
        body=payload.body,
        attachment_id=payload.attachment_id,
    )
    db.add(msg)

    # 2. Update conversation updated_at
    conv.updated_at = datetime.now(timezone.utc)

    # 3. Update sender's last_read_at
    for p in conv.participants:
        if p.user_id == sender_user.id:
            p.last_read_at = datetime.now(timezone.utc)
            break
    part_stmt = (
        update(ConversationParticipant)
        .where(
            ConversationParticipant.conversation_id == conv.id,
            ConversationParticipant.user_id == sender_user.id,
        )
        .values(last_read_at=datetime.now(timezone.utc))
    )
    await db.execute(part_stmt)
    await db.flush()
    await db.refresh(msg)

    # 4. Notify all other participants in the conversation
    for p in conv.participants:
        if p.user_id != sender_user.id:
            await create_notification(
                db,
                institute_id=institute_id,
                user_id=p.user_id,
                title="New Message",
                body=f"New message from {sender_user.email}: {payload.body[:60]}...",
                type=NotificationType.COMMUNICATION,
                related_entity_type="conversation",
                related_entity_id=str(conv.id),
            )

    logger.info("Message sent", extra={"conversation_id": str(conv.id), "message_id": str(msg.id)})
    return msg


async def list_conversation_messages(
    db: AsyncSession,
    *,
    institute_id: uuid.UUID,
    conversation_id: uuid.UUID,
    current_user: User,
    limit: int = 50,
) -> list[Message]:
    """Fetch paginated messages and mark conversation as read for the caller."""
    conv = await get_conversation(
        db, institute_id=institute_id, conversation_id=conversation_id, current_user=current_user
    )

    # Update caller's last_read_at
    for p in conv.participants:
        if p.user_id == current_user.id:
            p.last_read_at = datetime.now(timezone.utc)
            break
    part_stmt = (
        update(ConversationParticipant)
        .where(
            ConversationParticipant.conversation_id == conv.id,
            ConversationParticipant.user_id == current_user.id,
        )
        .values(last_read_at=datetime.now(timezone.utc))
    )
    await db.execute(part_stmt)
    await db.flush()

    stmt = (
        select(Message)
        .where(
            Message.conversation_id == conv.id,
            Message.is_hidden.is_(False),
        )
        .options(joinedload(Message.sender))
        .order_by(Message.created_at.asc())
        .limit(limit)
    )
    return list((await db.execute(stmt)).scalars().all())


# ─────────────────────────────────────────────────────────────────────────────
# 4. Announcements & Bulletins
# ─────────────────────────────────────────────────────────────────────────────

async def create_announcement(
    db: AsyncSession,
    *,
    institute_id: uuid.UUID,
    creator_user: User,
    payload: AnnouncementCreate,
    request: Request | None = None,
) -> Announcement:
    """Create a targeted announcement or institute-wide broadcast."""
    if creator_user.role not in ("SUPER_ADMIN", "ADMIN", "TEACHER"):
        raise ForbiddenError("Only teachers and administrators can post announcements.")

    ann = Announcement(
        institute_id=institute_id,
        title=payload.title,
        body=payload.body,
        target_audience=payload.target_audience,
        is_pinned=payload.is_pinned,
        created_by=creator_user.id,
    )
    db.add(ann)
    await db.flush()
    await db.refresh(ann)

    # Audit log
    await audit_service.log(
        db=db,
        actor=creator_user,
        action="announcement.created",
        entity_name="announcements",
        entity_id=str(ann.id),
        new_values={
            "title": ann.title,
            "target_audience": ann.target_audience,
            "is_pinned": ann.is_pinned,
        },
        request=request,
        institute_id=institute_id,
    )
    return ann


async def list_announcements(
    db: AsyncSession,
    *,
    institute_id: uuid.UUID,
    current_user: User,
) -> list[Announcement]:
    """
    List announcements applicable to the caller based on audience JSONB targeting:
    - Admin/Staff: all announcements
    - Student/Parent: matches institute-wide ({}) OR student's active batch/course/class
    """
    stmt = (
        select(Announcement)
        .where(
            Announcement.institute_id == institute_id,
            Announcement.deleted_at.is_(None),
        )
        .options(joinedload(Announcement.author))
        .order_by(Announcement.is_pinned.desc(), Announcement.published_at.desc())
    )
    all_announcements = (await db.execute(stmt)).scalars().all()

    if current_user.role in ("SUPER_ADMIN", "ADMIN", "TEACHER"):
        return list(all_announcements)

    # Audience filter resolution for Student / Parent
    user_batch_ids: set[str] = set()
    user_course_ids: set[str] = set()
    user_class_ids: set[str] = set()

    student_id = None
    if current_user.role == "STUDENT":
        s_stmt = select(StudentProfile.id).where(StudentProfile.user_id == current_user.id)
        student_id = (await db.execute(s_stmt)).scalar_one_or_none()
    elif current_user.role == "PARENT":
        p_stmt = select(ParentProfile.id).where(ParentProfile.user_id == current_user.id)
        parent_id = (await db.execute(p_stmt)).scalar_one_or_none()
        if parent_id:
            sp_stmt = select(StudentParent.student_id).where(StudentParent.parent_id == parent_id)
            student_id = (await db.execute(sp_stmt)).scalars().first()

    if student_id:
        e_stmt = (
            select(Enrollment)
            .where(Enrollment.student_id == student_id, Enrollment.status == EnrollmentStatus.ACTIVE)
            .options(joinedload(Enrollment.batch).joinedload(Batch.course))
        )
        for e in (await db.execute(e_stmt)).scalars().all():
            if e.batch:
                user_batch_ids.add(str(e.batch.id))
                if e.batch.course:
                    user_course_ids.add(str(e.batch.course.id))
                    user_class_ids.add(str(e.batch.course.class_id))

    filtered: list[Announcement] = []
    for ann in all_announcements:
        aud = ann.target_audience or {}
        if not aud:
            # Broadcast to everyone
            filtered.append(ann)
            continue

        match = True
        if "batch_id" in aud and str(aud["batch_id"]) not in user_batch_ids:
            match = False
        if "course_id" in aud and str(aud["course_id"]) not in user_course_ids:
            match = False
        if "class_id" in aud and str(aud["class_id"]) not in user_class_ids:
            match = False

        if match:
            filtered.append(ann)

    return filtered


# ─────────────────────────────────────────────────────────────────────────────
# 5. Parent-Teacher Meetings (PTM)
# ─────────────────────────────────────────────────────────────────────────────

async def request_ptm(
    db: AsyncSession,
    *,
    institute_id: uuid.UUID,
    parent_user: User,
    payload: PTMRequestCreate,
    request: Request | None = None,
) -> PTMRequest:
    """Parent requests a PTM session with an eligible teacher."""
    if parent_user.role != "PARENT":
        raise ForbiddenError("Only parents can request PTM appointments.")

    p_stmt = select(ParentProfile).where(ParentProfile.user_id == parent_user.id)
    parent = (await db.execute(p_stmt)).scalar_one_or_none()
    if not parent:
        raise NotFoundError("Parent profile not found.")

    # Verify parent is linked to student
    sp_stmt = select(StudentParent).where(
        StudentParent.parent_id == parent.id,
        StudentParent.student_id == payload.student_id,
    )
    if not (await db.execute(sp_stmt)).scalar_one_or_none():
        raise ForbiddenError("You are not registered as the parent of this student.")

    # Verify teacher exists
    teacher = await db.get(TeacherProfile, payload.teacher_id)
    if not teacher or teacher.institute_id != institute_id:
        raise NotFoundError(f"Teacher {payload.teacher_id} not found in this institute.")

    ptm = PTMRequest(
        institute_id=institute_id,
        parent_id=parent.id,
        student_id=payload.student_id,
        teacher_id=teacher.id,
        reason=payload.reason,
        requested_slot=payload.requested_slot,
        status=PTMStatus.REQUESTED,
    )
    db.add(ptm)
    await db.flush()
    await db.refresh(ptm)

    # Notify teacher
    if teacher.user_id:
        await create_notification(
            db,
            institute_id=institute_id,
            user_id=teacher.user_id,
            title="New PTM Request",
            body=f"PTM requested by {parent.first_name} {parent.last_name}: '{payload.reason}'",
            type=NotificationType.ACADEMIC,
            related_entity_type="ptm_request",
            related_entity_id=str(ptm.id),
        )

    # Audit log
    await audit_service.log(
        db=db,
        actor=parent_user,
        action="ptm.requested",
        entity_name="ptm_requests",
        entity_id=str(ptm.id),
        new_values={
            "parent_id": str(parent.id),
            "teacher_id": str(teacher.id),
            "requested_slot": str(payload.requested_slot),
        },
        request=request,
        institute_id=institute_id,
    )
    return ptm


async def list_ptm_requests(
    db: AsyncSession,
    *,
    institute_id: uuid.UUID,
    current_user: User,
) -> list[PTMRequest]:
    """Fetch PTM requests visible to the current user (Parent, Teacher, or Admin)."""
    stmt = (
        select(PTMRequest)
        .where(PTMRequest.institute_id == institute_id, PTMRequest.deleted_at.is_(None))
        .options(
            joinedload(PTMRequest.parent),
            joinedload(PTMRequest.student),
            joinedload(PTMRequest.teacher),
        )
        .order_by(PTMRequest.created_at.desc())
    )

    if current_user.role == "PARENT":
        p_stmt = select(ParentProfile.id).where(ParentProfile.user_id == current_user.id)
        parent_id = (await db.execute(p_stmt)).scalar_one_or_none()
        stmt = stmt.where(PTMRequest.parent_id == parent_id)
    elif current_user.role == "TEACHER":
        t_stmt = select(TeacherProfile.id).where(TeacherProfile.user_id == current_user.id)
        teacher_id = (await db.execute(t_stmt)).scalar_one_or_none()
        stmt = stmt.where(PTMRequest.teacher_id == teacher_id)

    return list((await db.execute(stmt)).scalars().all())


async def update_ptm_status(
    db: AsyncSession,
    *,
    institute_id: uuid.UUID,
    responder_user: User,
    ptm_id: uuid.UUID,
    payload: PTMStatusUpdate,
    request: Request | None = None,
) -> PTMRequest:
    """Teacher or Admin responds to a PTM request."""
    stmt = (
        select(PTMRequest)
        .where(PTMRequest.id == ptm_id, PTMRequest.institute_id == institute_id)
        .options(
            joinedload(PTMRequest.parent).joinedload(ParentProfile.user),
            joinedload(PTMRequest.teacher),
        )
    )
    ptm = (await db.execute(stmt)).scalar_one_or_none()
    if not ptm:
        raise NotFoundError(f"PTM request {ptm_id} not found.")

    if responder_user.role not in ("SUPER_ADMIN", "ADMIN"):
        if responder_user.role != "TEACHER" or ptm.teacher.user_id != responder_user.id:
            raise ForbiddenError("Only the assigned teacher or an administrator can update this meeting.")

    old_status = ptm.status
    ptm.status = payload.status
    if payload.confirmed_slot:
        ptm.confirmed_slot = payload.confirmed_slot
    if payload.teacher_notes:
        ptm.teacher_notes = payload.teacher_notes

    await db.flush()
    await db.refresh(ptm)

    # Notify parent
    if ptm.parent and ptm.parent.user:
        await create_notification(
            db,
            institute_id=institute_id,
            user_id=ptm.parent.user.id,
            title=f"PTM Request {payload.status.value}",
            body=f"Your PTM appointment status has been updated to {payload.status.value}.",
            type=NotificationType.ACADEMIC,
            related_entity_type="ptm_request",
            related_entity_id=str(ptm.id),
        )

    # Audit log
    await audit_service.log(
        db=db,
        actor=responder_user,
        action="ptm.status_updated",
        entity_name="ptm_requests",
        entity_id=str(ptm.id),
        old_values={"status": old_status.value},
        new_values={
            "status": ptm.status.value,
            "confirmed_slot": str(ptm.confirmed_slot) if ptm.confirmed_slot else None,
        },
        request=request,
        institute_id=institute_id,
    )
    return ptm


# ─────────────────────────────────────────────────────────────────────────────
# 6. Safety & Message Moderation
# ─────────────────────────────────────────────────────────────────────────────

async def report_message(
    db: AsyncSession,
    *,
    institute_id: uuid.UUID,
    reporter_user: User,
    payload: ReportMessageCreate,
    request: Request | None = None,
) -> ReportedMessage:
    """Participant reports an inappropriate message."""
    msg = await db.get(Message, payload.message_id)
    if not msg:
        raise NotFoundError(f"Message {payload.message_id} not found.")

    # Check caller is a participant in the message's conversation
    conv = await get_conversation(
        db, institute_id=institute_id, conversation_id=msg.conversation_id, current_user=reporter_user
    )

    report = ReportedMessage(
        institute_id=institute_id,
        message_id=msg.id,
        reported_by=reporter_user.id,
        reason=payload.reason,
        status=ReportStatus.PENDING,
    )
    db.add(report)
    await db.flush()
    await db.refresh(report)

    # Audit log
    await audit_service.log(
        db=db,
        actor=reporter_user,
        action="message.reported",
        entity_name="reported_messages",
        entity_id=str(report.id),
        new_values={"message_id": str(msg.id), "reason": payload.reason},
        request=request,
        institute_id=institute_id,
    )
    return report


async def list_reported_messages(
    db: AsyncSession,
    *,
    institute_id: uuid.UUID,
    status: ReportStatus | None = None,
) -> list[ReportedMessage]:
    """Admin moderation queue listing."""
    stmt = (
        select(ReportedMessage)
        .where(ReportedMessage.institute_id == institute_id)
        .options(
            joinedload(ReportedMessage.message).joinedload(Message.sender),
            joinedload(ReportedMessage.reporter),
            joinedload(ReportedMessage.resolver),
        )
        .order_by(ReportedMessage.created_at.desc())
    )
    if status:
        stmt = stmt.where(ReportedMessage.status == status)

    return list((await db.execute(stmt)).scalars().all())


async def resolve_reported_message(
    db: AsyncSession,
    *,
    institute_id: uuid.UUID,
    admin_user: User,
    report_id: uuid.UUID,
    payload: ResolveReportRequest,
    request: Request | None = None,
) -> ReportedMessage:
    """Admin resolves a reported message, optionally hiding it from conversation view."""
    stmt = (
        select(ReportedMessage)
        .where(ReportedMessage.id == report_id, ReportedMessage.institute_id == institute_id)
        .options(joinedload(ReportedMessage.message))
    )
    report = (await db.execute(stmt)).scalar_one_or_none()
    if not report:
        raise NotFoundError(f"Report {report_id} not found.")

    report.status = payload.status
    report.resolution_notes = payload.resolution_notes
    report.action_taken = payload.action_taken
    report.resolved_by = admin_user.id
    report.resolved_at = datetime.now(timezone.utc)

    # If action is hiding the message
    if payload.action_taken == "MESSAGE_HIDDEN" and report.message:
        report.message.is_hidden = True

    await db.flush()
    await db.refresh(report)

    # Audit log
    await audit_service.log(
        db=db,
        actor=admin_user,
        action="moderation.report_resolved",
        entity_name="reported_messages",
        entity_id=str(report.id),
        new_values={
            "status": report.status.value,
            "action_taken": report.action_taken,
            "resolution_notes": report.resolution_notes,
        },
        request=request,
        institute_id=institute_id,
    )
    return report
