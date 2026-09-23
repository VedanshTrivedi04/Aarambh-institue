"""
app/api/v1/api.py
-----------------
Aggregator router for the /api/v1 prefix.
Each domain slice registers its own router here.
"""

from fastapi import APIRouter

from app.api.v1 import health
from app.api.v1 import auth as auth_router_module
from app.api.v1.admin import academic_structure as admin_acad

api_router = APIRouter()

# Health & Public — unauthenticated
api_router.include_router(health.router)
from app.api.v1 import public
api_router.include_router(public.router)

# Slice 2 — Auth & Identity
api_router.include_router(auth_router_module.router, prefix="/auth")

# Slice 3 — Academic Structure (admin)
api_router.include_router(
    admin_acad.router,
    prefix="/admin/academic",
    tags=["Admin — Academic Structure"],
)

# Slice 4 — People, Profiles & Enrollment Engine
from app.api.v1.admin import people as admin_people
from app.api.v1.admin import enrollments as admin_enrollments
from app.api.v1.shared import me_profile

api_router.include_router(admin_people.router, prefix="/admin")
api_router.include_router(admin_enrollments.router, prefix="/admin")
api_router.include_router(me_profile.router)

# Slice 5 — Admissions & Enquiry Pipeline
from app.api.v1.admin import enquiries as admin_enquiries
from app.api.v1.admin import admissions as admin_admissions

api_router.include_router(admin_enquiries.router, prefix="/admin")
api_router.include_router(admin_admissions.router, prefix="/admin")

# Slice 6 — Academic Operations & Attendance
from app.api.v1.operations import attendance as op_attendance
from app.api.v1.operations import remarks as op_remarks
from app.api.v1.operations import sessions as op_sessions
from app.api.v1.operations import timetables as op_timetables

api_router.include_router(op_timetables.router, prefix="/operations")
api_router.include_router(op_sessions.router, prefix="/operations")
api_router.include_router(op_attendance.router, prefix="/operations")
api_router.include_router(op_remarks.router, prefix="/operations")

# Slice 7 — Learning & Generic File Storage
from app.api.v1.learning import files as learning_files
from app.api.v1.learning import homework as learning_homework
from app.api.v1.learning import materials as learning_materials

api_router.include_router(learning_files.router, prefix="/learning")
api_router.include_router(learning_materials.router, prefix="/learning")
api_router.include_router(learning_homework.router, prefix="/learning")

# Slice 8 — Examinations & Question Bank
from app.api.v1.examination import questions as exam_questions
from app.api.v1.examination import tests as exam_tests
from app.api.v1.examination import results as exam_results

api_router.include_router(exam_questions.router, prefix="/examination")
api_router.include_router(exam_tests.router, prefix="/examination")
api_router.include_router(exam_results.router, prefix="/examination")

# Slice 9 — Finance & Immutable Ledger
from app.api.v1.finance import router as finance_router

api_router.include_router(finance_router, prefix="/finance")

# Slice 10 — Communication, Notifications & Messaging
from app.api.v1.communication import router as communication_router

api_router.include_router(communication_router, prefix="/communication")

# Slice 11 — Reports & Analytics
from app.api.v1.analytics import router as analytics_router

api_router.include_router(analytics_router, prefix="/analytics")

# Slice 12 — Admin CMS & Dynamic Website Content
from app.api.v1.admin import cms as admin_cms

api_router.include_router(admin_cms.router, prefix="/admin")

