"""
app/core/queue.py
-----------------
Asynchronous background task dispatcher for non-blocking operations:
  - Cache invalidation
  - In-app notification fanout
  - Audit log emission
  - Materialized view refreshes
"""

from __future__ import annotations

import asyncio
import uuid
from typing import Any, Callable, Coroutine

from fastapi import BackgroundTasks

from app.core.cache import cache_service
from app.core.logging import get_logger

logger = get_logger(__name__)


class TaskQueueService:
    """
    Standardized background task dispatcher supporting FastAPI BackgroundTasks
    and asyncio event-loop scheduling.
    """

    def enqueue(
        self,
        coro_or_func: Callable[..., Coroutine[Any, Any, Any] | Any],
        *args: Any,
        background_tasks: BackgroundTasks | None = None,
        **kwargs: Any,
    ) -> None:
        """Enqueue task via FastAPI BackgroundTasks if provided, else asyncio.create_task."""
        if background_tasks:
            background_tasks.add_task(coro_or_func, *args, **kwargs)
        else:
            asyncio.create_task(self._safe_execute(coro_or_func, *args, **kwargs))

    async def _safe_execute(
        self,
        coro_or_func: Callable[..., Coroutine[Any, Any, Any] | Any],
        *args: Any,
        **kwargs: Any,
    ) -> None:
        """Execute and catch unexpected exceptions so background crashes don't bring down server."""
        try:
            res = coro_or_func(*args, **kwargs)
            if asyncio.iscoroutine(res):
                await res
        except Exception as exc:
            logger.exception("Background task execution failed", error=str(exc))

    def invalidate_cache(
        self,
        tenant_id: uuid.UUID | str,
        namespace: str,
        background_tasks: BackgroundTasks | None = None,
    ) -> None:
        """Offload cache invalidation for a tenant namespace."""
        self.enqueue(
            cache_service.invalidate_tenant_namespace,
            tenant_id,
            namespace,
            background_tasks=background_tasks,
        )

    def refresh_views(
        self,
        institute_id: uuid.UUID,
        background_tasks: BackgroundTasks | None = None,
    ) -> None:
        """Schedule background materialized view refresh."""
        async def _refresh():
            from app.db.session import async_engine
            from sqlalchemy import text
            try:
                async with async_engine.begin() as conn:
                    await conn.execute(text("REFRESH MATERIALIZED VIEW CONCURRENTLY mv_batch_performance_summary"))
                logger.info("Background materialized view refresh complete", institute_id=str(institute_id))
            except Exception as exc:
                logger.warning("Background view refresh failed", institute_id=str(institute_id), error=str(exc))

        self.enqueue(_refresh, background_tasks=background_tasks)


task_queue = TaskQueueService()
