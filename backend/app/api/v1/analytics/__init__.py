"""
app/api/v1/analytics/__init__.py
--------------------------------
Aggregate router for all Reports & Analytics endpoints.
"""

from __future__ import annotations

from fastapi import APIRouter

from app.api.v1.analytics.attendance import router as attendance_router
from app.api.v1.analytics.batches import router as batches_router
from app.api.v1.analytics.dashboard import router as dashboard_router
from app.api.v1.analytics.export import router as export_router
from app.api.v1.analytics.finance import router as finance_router
from app.api.v1.analytics.student_360 import router as student_360_router

router = APIRouter(tags=["Reports & Analytics"])

router.include_router(dashboard_router)
router.include_router(batches_router)
router.include_router(finance_router)
router.include_router(attendance_router)
router.include_router(student_360_router)
router.include_router(export_router)
