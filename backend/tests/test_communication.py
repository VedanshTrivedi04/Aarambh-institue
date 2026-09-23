"""
tests/test_communication.py
----------------------------
Comprehensive tests for Slice 10: Communication, Notifications & Messaging.

Coverage:
  1. Derived Contact Graph & Boundary Enforcement:
     - Student can only discover and message teachers of their actively enrolled batches.
     - Student cannot message teachers outside their active batches (403 Forbidden).
     - Student can initiate conversation with eligible batch teacher.
  2. Conversation Threading, Messaging & Notifications:
     - Exchanging messages within an authorized conversation.
     - Automatic delivery of in-app Notification to recipients.
     - Unread count watermark tracking (unread -> read).
  3. Audience-Targeted Announcements:
     - Broadcast announcements visible to all institute users.
     - Targeted announcements (by batch_id) strictly visible only to enrolled students.
  4. Parent-Teacher Meeting (PTM) State Machine:
     - Parent requests PTM with child's eligible teacher.
     - Teacher receives in-app notification.
     - Teacher approves / confirms appointment slot.
     - Teacher marks PTM as COMPLETED.
  5. Content Safety, Reporting & Admin Moderation:
     - Conversation participant reports an inappropriate message.
     - Admin reviews moderation queue (status=PENDING).
     - Admin resolves report with action_taken="MESSAGE_HIDDEN".
     - Message is hidden from conversation feed.
     - Emits audit log entry ('moderation.report_resolved').
"""

from __future__ import annotations

import uuid
from datetime import date, datetime, timedelta, timezone

import pytest
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import hash_password
from app.models.academic_structure import (
    AcademicYear,
    Batch,
    Board,
    Course,
    SchoolClass,
    Subject,
)
from app.models.audit import AuditLog
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
from app.models.institute import Institute
from app.models.people import ParentProfile, StudentParent, StudentProfile, TeacherProfile
from app.models.user import User, UserStatus


# ─── Fixtures ────────────────────────────────────────────────────────────────

@pytest.fixture
async def institute(db_session: AsyncSession) -> Institute:
    inst = Institute(id=uuid.uuid4(), name="Comm Test Inst", code=f"COMM_{uuid.uuid4().hex[:6].upper()}", is_active=True)
    db_session.add(inst)
    await db_session.flush()
    return inst


async def _make_user(
    db_session: AsyncSession, institute: Institute, role: str, email: str
) -> tuple[User, str]:
    plain = "Test@1234!"
    user = User(
        id=uuid.uuid4(),
        institute_id=institute.id,
        email=email,
        password_hash=hash_password(plain),
        role=role,
        status=UserStatus.ACTIVE,
        is_active=True,
    )
    db_session.add(user)
    await db_session.flush()
    return user, plain


async def _login(client: AsyncClient, email: str, password: str) -> str:
    resp = await client.post(
        "/api/v1/auth/login",
        json={"identifier": email, "password": password},
    )
    assert resp.status_code == 200, resp.text
    return resp.json()["access_token"]


@pytest.fixture
async def comm_env(
    db_session: AsyncSession, async_client: AsyncClient, institute: Institute
) -> dict[str, any]:
    # 1. Admin
    admin_u, admin_pwd = await _make_user(db_session, institute, "ADMIN", f"admin_{uuid.uuid4().hex[:4]}@comm.test")
    admin_token = await _login(async_client, admin_u.email, admin_pwd)

    # 2. Teacher 1 (Math Teacher for Batch A)
    t1_u, t1_pwd = await _make_user(db_session, institute, "TEACHER", f"t1_{uuid.uuid4().hex[:4]}@comm.test")
    t1_token = await _login(async_client, t1_u.email, t1_pwd)
    t1_profile = TeacherProfile(
        id=uuid.uuid4(), institute_id=institute.id, user_id=t1_u.id,
        first_name="Amit", last_name="Verma",
    )
    db_session.add(t1_profile)

    # 3. Teacher 2 (Physics Teacher for Batch B)
    t2_u, t2_pwd = await _make_user(db_session, institute, "TEACHER", f"t2_{uuid.uuid4().hex[:4]}@comm.test")
    t2_token = await _login(async_client, t2_u.email, t2_pwd)
    t2_profile = TeacherProfile(
        id=uuid.uuid4(), institute_id=institute.id, user_id=t2_u.id,
        first_name="Pooja", last_name="Nair",
    )
    db_session.add(t2_profile)
    await db_session.flush()

    # 4. Academic Structure
    ay = AcademicYear(
        id=uuid.uuid4(), institute_id=institute.id, name="2025-26",
        start_date=date(2025, 4, 1), end_date=date(2026, 3, 31), is_current=True,
    )
    board = Board(id=uuid.uuid4(), institute_id=institute.id, name="CBSE", code=f"CBSE_{uuid.uuid4().hex[:4]}")
    sclass = SchoolClass(id=uuid.uuid4(), board_id=board.id, name="Class 10", display_order=10)
    sub_math = Subject(id=uuid.uuid4(), institute_id=institute.id, name="Mathematics", code=f"M_{uuid.uuid4().hex[:4]}")
    sub_phy = Subject(id=uuid.uuid4(), institute_id=institute.id, name="Physics", code=f"P_{uuid.uuid4().hex[:4]}")
    db_session.add_all([ay, board, sclass, sub_math, sub_phy])
    await db_session.flush()

    course = Course(
        id=uuid.uuid4(), institute_id=institute.id, academic_year_id=ay.id, class_id=sclass.id,
        name="Foundation 10th", code=f"F10_{uuid.uuid4().hex[:4]}",
    )
    db_session.add(course)
    await db_session.flush()

    # Batch A (Taught by Teacher 1)
    batch_a = Batch(
        id=uuid.uuid4(), institute_id=institute.id, course_id=course.id, subject_id=sub_math.id,
        teacher_id=t1_profile.id, name="Batch 10-A Math", capacity=30,
    )
    # Batch B (Taught by Teacher 2)
    batch_b = Batch(
        id=uuid.uuid4(), institute_id=institute.id, course_id=course.id, subject_id=sub_phy.id,
        teacher_id=t2_profile.id, name="Batch 10-B Physics", capacity=30,
    )
    db_session.add_all([batch_a, batch_b])
    await db_session.flush()

    # 5. Student A (Enrolled only in Batch A)
    s_a_user, s_a_pwd = await _make_user(db_session, institute, "STUDENT", f"st_a_{uuid.uuid4().hex[:4]}@comm.test")
    s_a_token = await _login(async_client, s_a_user.email, s_a_pwd)
    st_a_profile = StudentProfile(
        id=uuid.uuid4(), institute_id=institute.id, user_id=s_a_user.id,
        admission_number=f"ADM-A-{uuid.uuid4().hex[:6].upper()}",
        first_name="Rohan", last_name="Kapoor",
    )
    db_session.add(st_a_profile)
    await db_session.flush()

    enroll_a = Enrollment(
        id=uuid.uuid4(), institute_id=institute.id, student_id=st_a_profile.id,
        batch_id=batch_a.id, enrollment_date=date.today(), status=EnrollmentStatus.ACTIVE,
    )
    db_session.add(enroll_a)

    # 6. Student B (Enrolled only in Batch B)
    s_b_user, s_b_pwd = await _make_user(db_session, institute, "STUDENT", f"st_b_{uuid.uuid4().hex[:4]}@comm.test")
    s_b_token = await _login(async_client, s_b_user.email, s_b_pwd)
    st_b_profile = StudentProfile(
        id=uuid.uuid4(), institute_id=institute.id, user_id=s_b_user.id,
        admission_number=f"ADM-B-{uuid.uuid4().hex[:6].upper()}",
        first_name="Sneha", last_name="Patil",
    )
    db_session.add(st_b_profile)
    await db_session.flush()

    enroll_b = Enrollment(
        id=uuid.uuid4(), institute_id=institute.id, student_id=st_b_profile.id,
        batch_id=batch_b.id, enrollment_date=date.today(), status=EnrollmentStatus.ACTIVE,
    )
    db_session.add(enroll_b)

    # 7. Parent of Student A
    p_a_user, p_a_pwd = await _make_user(db_session, institute, "PARENT", f"parent_a_{uuid.uuid4().hex[:4]}@comm.test")
    p_a_token = await _login(async_client, p_a_user.email, p_a_pwd)
    pt_a_profile = ParentProfile(
        id=uuid.uuid4(), institute_id=institute.id, user_id=p_a_user.id,
        first_name="Vikram", last_name="Kapoor", relation="FATHER",
    )
    db_session.add(pt_a_profile)
    await db_session.flush()

    link_a = StudentParent(
        student_id=st_a_profile.id,
        parent_id=pt_a_profile.id,
        is_primary=True,
    )
    db_session.add(link_a)
    await db_session.flush()

    return {
        "institute": institute,
        "admin_user": admin_u,
        "admin_token": admin_token,
        "t1_user": t1_u,
        "t1_profile": t1_profile,
        "t1_token": t1_token,
        "t2_user": t2_u,
        "t2_profile": t2_profile,
        "t2_token": t2_token,
        "st_a_user": s_a_user,
        "st_a_profile": st_a_profile,
        "st_a_token": s_a_token,
        "st_b_user": s_b_user,
        "st_b_profile": st_b_profile,
        "st_b_token": s_b_token,
        "parent_a_user": p_a_user,
        "parent_a_profile": pt_a_profile,
        "parent_a_token": p_a_token,
        "batch_a": batch_a,
        "batch_b": batch_b,
    }


# ─── Tests ───────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_derived_contact_graph_enforcement(
    async_client: AsyncClient,
    comm_env: dict[str, any],
):
    """
    1. Student A queries eligible contacts -> only Teacher 1 is returned (teaching Batch A).
       Teacher 2 (teaching Batch B) is NOT returned.
    2. Student A attempts to initiate a conversation with Teacher 2 -> 403 Forbidden.
    3. Student A initiates a conversation with Teacher 1 -> 201 Created.
    """
    env = comm_env
    s_a_token = env["st_a_token"]
    t1_user = env["t1_user"]
    t2_user = env["t2_user"]

    # 1. Query eligible contacts for Student A
    contacts_resp = await async_client.get(
        "/api/v1/communication/contacts/eligible",
        headers={"Authorization": f"Bearer {s_a_token}"},
    )
    assert contacts_resp.status_code == 200, contacts_resp.text
    contacts = contacts_resp.json()["data"]

    eligible_user_ids = [c["user_id"] for c in contacts]
    assert str(t1_user.id) in eligible_user_ids
    assert str(t2_user.id) not in eligible_user_ids

    # 2. Student A attempts to message unauthorized Teacher 2 -> 403 Forbidden
    forbidden_resp = await async_client.post(
        "/api/v1/communication/conversations",
        headers={"Authorization": f"Bearer {s_a_token}"},
        json={
            "participant_user_ids": [str(t2_user.id)],
            "type": "DIRECT_STUDENT_TEACHER",
            "title": "Unauthorized Chat",
        },
    )
    assert forbidden_resp.status_code == 403, forbidden_resp.text

    # 3. Student A initiates conversation with authorized Teacher 1 -> 201 Created
    allowed_resp = await async_client.post(
        "/api/v1/communication/conversations",
        headers={"Authorization": f"Bearer {s_a_token}"},
        json={
            "participant_user_ids": [str(t1_user.id)],
            "type": "DIRECT_STUDENT_TEACHER",
            "title": "Math Doubt Discussion",
        },
    )
    assert allowed_resp.status_code == 201, allowed_resp.text
    conv_data = allowed_resp.json()["data"]
    assert conv_data["type"] == "DIRECT_STUDENT_TEACHER"
    assert len(conv_data["participants"]) == 2


@pytest.mark.asyncio
async def test_conversation_messaging_and_unread_counter(
    async_client: AsyncClient,
    comm_env: dict[str, any],
):
    """
    1. Student A initiates conversation with Teacher 1.
    2. Student A sends a message.
    3. Teacher 1 receives an in-app notification.
    4. Teacher 1's conversation list shows unread_count >= 1.
    5. Teacher 1 fetches messages -> unread_count resets to 0.
    """
    env = comm_env
    s_a_token = env["st_a_token"]
    t1_token = env["t1_token"]
    t1_user = env["t1_user"]

    # 1. Create conversation
    create_conv = await async_client.post(
        "/api/v1/communication/conversations",
        headers={"Authorization": f"Bearer {s_a_token}"},
        json={
            "participant_user_ids": [str(t1_user.id)],
            "type": "DIRECT_STUDENT_TEACHER",
        },
    )
    assert create_conv.status_code == 201
    conv_id = create_conv.json()["data"]["id"]

    # 2. Student A sends message
    msg_resp = await async_client.post(
        f"/api/v1/communication/conversations/{conv_id}/messages",
        headers={"Authorization": f"Bearer {s_a_token}"},
        json={"body": "Hello Sir, I need clarification on problem #5."},
    )
    assert msg_resp.status_code == 201, msg_resp.text
    msg_data = msg_resp.json()["data"]
    assert msg_data["body"] == "Hello Sir, I need clarification on problem #5."

    # 3. Teacher 1 checks notifications
    notif_resp = await async_client.get(
        "/api/v1/communication/notifications",
        headers={"Authorization": f"Bearer {t1_token}"},
    )
    assert notif_resp.status_code == 200
    notifs = notif_resp.json()["data"]
    assert len(notifs) >= 1
    assert notifs[0]["type"] == "COMMUNICATION"

    # 4. Teacher 1 checks conversation list (should show unread_count >= 1)
    convs_resp = await async_client.get(
        "/api/v1/communication/conversations",
        headers={"Authorization": f"Bearer {t1_token}"},
    )
    assert convs_resp.status_code == 200
    convs = convs_resp.json()["data"]
    target_conv = next(c for c in convs if c["id"] == conv_id)
    assert target_conv["unread_count"] >= 1

    # 5. Teacher 1 reads messages
    fetch_msgs = await async_client.get(
        f"/api/v1/communication/conversations/{conv_id}/messages",
        headers={"Authorization": f"Bearer {t1_token}"},
    )
    assert fetch_msgs.status_code == 200
    assert len(fetch_msgs.json()["data"]) >= 1

    # 6. Verify unread count is now 0 for Teacher 1
    convs_after = await async_client.get(
        "/api/v1/communication/conversations",
        headers={"Authorization": f"Bearer {t1_token}"},
    )
    target_after = next(c for c in convs_after.json()["data"] if c["id"] == conv_id)
    assert target_after["unread_count"] == 0


@pytest.mark.asyncio
async def test_audience_targeted_announcements(
    async_client: AsyncClient,
    comm_env: dict[str, any],
):
    """
    1. Admin publishes an institute-wide broadcast announcement.
    2. Admin publishes a batch-specific announcement targeted exclusively to Batch A.
    3. Student A (in Batch A) sees both announcements.
    4. Student B (in Batch B) sees only the institute-wide broadcast.
    """
    env = comm_env
    admin_token = env["admin_token"]
    s_a_token = env["st_a_token"]
    s_b_token = env["st_b_token"]
    batch_a = env["batch_a"]

    # 1. Publish Broadcast Announcement
    bcast_resp = await async_client.post(
        "/api/v1/communication/announcements",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "title": "Annual Science Fair",
            "body": "The annual science exhibition will be held on October 15th.",
            "target_audience": {},
            "is_pinned": True,
        },
    )
    assert bcast_resp.status_code == 201

    # 2. Publish Batch A Targeted Announcement
    batch_a_resp = await async_client.post(
        "/api/v1/communication/announcements",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "title": "Batch 10-A Math Workshop",
            "body": "Extra trigonometry practice session this Saturday at 4 PM.",
            "target_audience": {"batch_id": str(batch_a.id)},
            "is_pinned": False,
        },
    )
    assert batch_a_resp.status_code == 201

    # 3. Student A feed: must include both announcements
    feed_a = await async_client.get(
        "/api/v1/communication/announcements",
        headers={"Authorization": f"Bearer {s_a_token}"},
    )
    assert feed_a.status_code == 200
    titles_a = [a["title"] for a in feed_a.json()["data"]]
    assert "Annual Science Fair" in titles_a
    assert "Batch 10-A Math Workshop" in titles_a

    # 4. Student B feed: must NOT include Batch 10-A Math Workshop
    feed_b = await async_client.get(
        "/api/v1/communication/announcements",
        headers={"Authorization": f"Bearer {s_b_token}"},
    )
    assert feed_b.status_code == 200
    titles_b = [a["title"] for a in feed_b.json()["data"]]
    assert "Annual Science Fair" in titles_b
    assert "Batch 10-A Math Workshop" not in titles_b


@pytest.mark.asyncio
async def test_parent_teacher_meeting_lifecycle(
    async_client: AsyncClient,
    comm_env: dict[str, any],
):
    """
    1. Parent requests a PTM with Student A's math teacher (Teacher 1).
    2. Teacher 1 reviews the request and approves it with a confirmed slot.
    3. Teacher 1 completes the PTM appointment.
    4. State machine transitions strictly validated.
    """
    env = comm_env
    p_a_token = env["parent_a_token"]
    t1_token = env["t1_token"]
    st_a_profile = env["st_a_profile"]
    t1_profile = env["t1_profile"]

    # 1. Parent requests PTM
    req_time = (datetime.now(timezone.utc) + timedelta(days=3)).isoformat()
    req_resp = await async_client.post(
        "/api/v1/communication/ptm/requests",
        headers={"Authorization": f"Bearer {p_a_token}"},
        json={
            "student_id": str(st_a_profile.id),
            "teacher_id": str(t1_profile.id),
            "reason": "Discuss recent mid-term marks and study habits",
            "requested_slot": req_time,
        },
    )
    assert req_resp.status_code == 201, req_resp.text
    ptm_id = req_resp.json()["data"]["id"]
    assert req_resp.json()["data"]["status"] == "REQUESTED"

    # 2. Teacher receives in-app notification
    t1_notifs = await async_client.get(
        "/api/v1/communication/notifications",
        headers={"Authorization": f"Bearer {t1_token}"},
    )
    assert t1_notifs.status_code == 200
    assert any("PTM" in n["title"] for n in t1_notifs.json()["data"])

    # 3. Teacher approves PTM with confirmed slot
    conf_time = (datetime.now(timezone.utc) + timedelta(days=3, hours=1)).isoformat()
    approve_resp = await async_client.patch(
        f"/api/v1/communication/ptm/requests/{ptm_id}/status",
        headers={"Authorization": f"Bearer {t1_token}"},
        json={
            "status": "APPROVED",
            "confirmed_slot": conf_time,
            "teacher_notes": "Confirmed for 4:00 PM in Room 204.",
        },
    )
    assert approve_resp.status_code == 200, approve_resp.text
    assert approve_resp.json()["data"]["status"] == "APPROVED"
    assert approve_resp.json()["data"]["teacher_notes"] == "Confirmed for 4:00 PM in Room 204."

    # 4. Teacher marks meeting COMPLETED
    complete_resp = await async_client.patch(
        f"/api/v1/communication/ptm/requests/{ptm_id}/status",
        headers={"Authorization": f"Bearer {t1_token}"},
        json={
            "status": "COMPLETED",
            "teacher_notes": "Productive meeting. Advised 30 mins daily algebra practice.",
        },
    )
    assert complete_resp.status_code == 200
    assert complete_resp.json()["data"]["status"] == "COMPLETED"


@pytest.mark.asyncio
async def test_message_reporting_and_moderation(
    async_client: AsyncClient,
    db_session: AsyncSession,
    comm_env: dict[str, any],
):
    """
    1. Student A sends a message in a conversation with Teacher 1.
    2. Teacher 1 reports the message as abusive / guideline violation.
    3. Admin checks moderation queue and inspects pending reports.
    4. Admin resolves the report with action_taken="MESSAGE_HIDDEN".
    5. The hidden message no longer appears in conversation message history.
    6. Audit log entry 'moderation.report_resolved' is verified.
    """
    env = comm_env
    admin_token = env["admin_token"]
    s_a_token = env["st_a_token"]
    t1_token = env["t1_token"]
    t1_user = env["t1_user"]

    # 1. Create conversation & send message
    create_conv = await async_client.post(
        "/api/v1/communication/conversations",
        headers={"Authorization": f"Bearer {s_a_token}"},
        json={
            "participant_user_ids": [str(t1_user.id)],
            "type": "DIRECT_STUDENT_TEACHER",
        },
    )
    assert create_conv.status_code == 201
    conv_id = create_conv.json()["data"]["id"]

    msg_resp = await async_client.post(
        f"/api/v1/communication/conversations/{conv_id}/messages",
        headers={"Authorization": f"Bearer {s_a_token}"},
        json={"body": "Inappropriate or spam message content to be reported."},
    )
    assert msg_resp.status_code == 201
    msg_id = msg_resp.json()["data"]["id"]

    # 2. Teacher 1 reports the message
    rep_resp = await async_client.post(
        "/api/v1/communication/moderation/reports",
        headers={"Authorization": f"Bearer {t1_token}"},
        json={
            "message_id": msg_id,
            "reason": "Unsolicited promotional content violation",
        },
    )
    assert rep_resp.status_code == 201, rep_resp.text
    rep_id = rep_resp.json()["data"]["id"]
    assert rep_resp.json()["data"]["status"] == "PENDING"

    # 3. Admin lists moderation queue
    queue_resp = await async_client.get(
        "/api/v1/communication/moderation/reports?status=PENDING",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert queue_resp.status_code == 200
    reports = queue_resp.json()["data"]
    assert any(r["id"] == rep_id for r in reports)

    # 4. Admin resolves the report and hides the message
    resolve_resp = await async_client.patch(
        f"/api/v1/communication/moderation/reports/{rep_id}/resolve",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "status": "RESOLVED",
            "action_taken": "MESSAGE_HIDDEN",
            "resolution_notes": "Confirmed spam; message hidden from conversation.",
        },
    )
    assert resolve_resp.status_code == 200, resolve_resp.text
    assert resolve_resp.json()["data"]["status"] == "RESOLVED"
    assert resolve_resp.json()["data"]["action_taken"] == "MESSAGE_HIDDEN"

    # 5. Verify message is hidden from conversation feed
    feed_resp = await async_client.get(
        f"/api/v1/communication/conversations/{conv_id}/messages",
        headers={"Authorization": f"Bearer {t1_token}"},
    )
    assert feed_resp.status_code == 200
    active_msg_ids = [m["id"] for m in feed_resp.json()["data"]]
    assert msg_id not in active_msg_ids

    # 6. Verify audit log entry
    audit_stmt = (
        select(AuditLog)
        .where(
            AuditLog.entity_id == str(rep_id),
            AuditLog.action == "moderation.report_resolved",
        )
    )
    audit = (await db_session.execute(audit_stmt)).scalar_one_or_none()
    assert audit is not None
    assert audit.actor_id == env["admin_user"].id
