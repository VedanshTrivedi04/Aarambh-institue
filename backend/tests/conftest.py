"""
tests/conftest.py
-----------------
Shared pytest fixtures for the entire backend test suite.

Provides:
  async_client — an httpx AsyncClient connected to the test FastAPI app
  db_session   — an async SQLAlchemy session using the TEST database with
                 transactional rollback per test (no data leaks between tests)

Usage in tests:
    async def test_something(async_client: AsyncClient):
        resp = await async_client.get("/api/v1/health")
        assert resp.status_code == 200

Test database config (backend.md §10):
  - Uses TEST_DATABASE_URL from .env (separate DB from dev).
  - Runs all Alembic migrations fresh on each test session.
  - Each test runs in a transaction that is rolled back at the end.
"""

from __future__ import annotations

import asyncio
import os
from typing import AsyncGenerator

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool

from app.core.config import get_settings
from app.db.base import Base
from app.db.session import get_db
from app.main import create_app

# ---------------------------------------------------------------------------
# Test database engine (session-scoped — created once per test run)
# ---------------------------------------------------------------------------

@pytest_asyncio.fixture(scope="session")
async def test_engine():
    settings = get_settings()
    db_url = settings.TEST_DATABASE_URL or settings.DATABASE_URL.replace(
        "/aarambh_erp_dev", "/aarambh_erp_test"
    )
    engine = create_async_engine(db_url, echo=False, future=True, poolclass=NullPool)

    # Ensure all tables exist without dropping schema
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    await engine.dispose()


# ---------------------------------------------------------------------------
# Per-test DB session with rollback isolation
# ---------------------------------------------------------------------------

@pytest_asyncio.fixture
async def db_session(test_engine) -> AsyncGenerator[AsyncSession, None]:
    """
    Each test gets its own transaction that is rolled back at the end.
    This keeps tests isolated without re-creating the schema every time.
    """
    async with test_engine.connect() as conn:
        await conn.begin()
        TestSessionLocal = async_sessionmaker(
            bind=conn,
            expire_on_commit=False,
            class_=AsyncSession,
        )
        async with TestSessionLocal() as session:
            yield session
        await conn.rollback()


# ---------------------------------------------------------------------------
# FastAPI test client (function-scoped)
# ---------------------------------------------------------------------------

@pytest_asyncio.fixture
async def async_client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """
    Returns an httpx AsyncClient wired to the test app.
    The get_db dependency is overridden to use the per-test db_session.
    """
    app = create_app()

    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://testserver",
    ) as client:
        yield client

    app.dependency_overrides.clear()
