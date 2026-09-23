"""
app/api/v1/communication/__init__.py
------------------------------------
Aggregates communication sub-routers: notifications, contacts, conversations, announcements, PTM, moderation.
"""

from fastapi import APIRouter

from app.api.v1.communication import (
    announcements,
    contacts,
    conversations,
    moderation,
    notifications,
    ptm,
)

router = APIRouter()

router.include_router(notifications.router)
router.include_router(contacts.router)
router.include_router(conversations.router)
router.include_router(announcements.router)
router.include_router(ptm.router)
router.include_router(moderation.router)

__all__ = ["router"]
