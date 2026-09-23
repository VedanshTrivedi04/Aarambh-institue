"""
app/models/__init__.py
----------------------
Central model registry for Alembic autogenerate.
Import order: dependencies first.
"""

# ── Slice 2: Tenancy, Identity, RBAC & Audit ──────────────────────────────
from app.models.institute import Branch, Institute  # noqa: F401
from app.models.role import Permission, Role, RolePermission, UserRole  # noqa: F401
from app.models.user import PasswordReset, User, UserSession  # noqa: F401
from app.models.audit import AuditLog  # noqa: F401

# ── Slice 3: Academic Structure ────────────────────────────────────────────
from app.models.academic_structure import (  # noqa: F401
    AcademicYear,
    Batch,
    Board,
    Course,
    CourseSubject,
    SchoolClass,
    Stream,
    Subject,
)

# ── Slice 4: People, Profiles & Enrollment ────────────────────────────────
from app.models.people import (  # noqa: F401
    ParentProfile,
    StaffProfile,
    StudentParent,
    StudentProfile,
    TeacherProfile,
)
from app.models.enrollment import (  # noqa: F401
    BatchTransferHistory,
    Enrollment,
)

# ── Slice 5: Admissions & Enquiry Pipeline ────────────────────────────────
from app.models.enquiry import (  # noqa: F401
    Enquiry,
    EnquiryFollowUp,
)

# ── Slice 6: Academic Operations & Attendance ─────────────────────────────
from app.models.academic_operations import (  # noqa: F401
    Attendance,
    ClassSession,
    SessionLog,
    StudentRemark,
    Timetable,
)

# ── Slice 7: Learning & Generic File Storage ──────────────────────────────
from app.models.learning import (  # noqa: F401
    FileAttachment,
    Homework,
    HomeworkSubmission,
    StudyMaterial,
)
# ── Slice 8: Examinations & Question Bank ─────────────────────────────────
from app.models.examination import (  # noqa: F401
    Question,
    QuestionDifficulty,
    QuestionType,
    Test,
    TestQuestion,
    TestResult,
    TestStatus,
    TestType,
)

# ── Slice 9: Finance & Immutable Ledger ───────────────────────────────────
from app.models.finance import (  # noqa: F401
    AdjustmentType,
    FeePlan,
    FeePlanType,
    Installment,
    InstallmentStatus,
    Payment,
    PaymentAdjustment,
    PaymentMethod,
    Receipt,
)

# ── Slice 10: Communication & Messaging ───────────────────────────────────
from app.models.communication import (  # noqa: F401
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

# ── Slice 12: Dynamic Website CMS ──────────────────────────────────────────
from app.models.cms import SiteContent  # noqa: F401

