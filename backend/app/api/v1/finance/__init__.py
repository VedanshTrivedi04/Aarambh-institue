"""
app/api/v1/finance/__init__.py
------------------------------
Aggregates finance routers: plans, payments, receipts, and student summaries.
"""

from fastapi import APIRouter

from app.api.v1.finance import payments, payments_online, plans, receipts, student, webhooks

router = APIRouter()

router.include_router(plans.router)
router.include_router(payments.router)
router.include_router(payments_online.router)
router.include_router(receipts.router)
router.include_router(student.router)
router.include_router(webhooks.router)

__all__ = ["router"]
