"""
alembic/env.py
--------------
Async Alembic migration runner.

Alembic itself doesn't expose an async API — but it can run migrations using
an async SQLAlchemy engine by wrapping the sync migration in asyncio.run().
See: https://alembic.sqlalchemy.org/en/latest/cookbook.html#using-asyncio-with-alembic

Migration policy (backend.md §11):
  - Every migration is reviewed manually before committing — never blindly
    trust autogenerate output.
  - Naming: YYYYMMDD_HHMM_<descriptive_slug>.py (set in alembic.ini).
  - One migration per PR — reviewed alongside the model change.
  - Never hand-edit the schema directly in staging or production.
"""

from __future__ import annotations

import asyncio
from logging.config import fileConfig

from alembic import context
from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config

# ---------------------------------------------------------------------------
# Import the declarative Base so Alembic can auto-detect model changes.
# ALL domain models must be imported here (or transitively via app/models/__init__.py)
# so that their metadata is registered with Base.metadata before autogenerate runs.
# ---------------------------------------------------------------------------
from app.db.base import Base  # noqa: F401
import app.models  # noqa: F401 — registers all ORM models with Base.metadata

# ---------------------------------------------------------------------------
# Alembic Config object (gives access to alembic.ini values)
# ---------------------------------------------------------------------------
config = context.config

# Inject DATABASE_URL from pydantic-settings so we never hard-code it here.
from app.core.config import get_settings as _get_settings

_settings = _get_settings()
config.set_main_option("sqlalchemy.url", _settings.DATABASE_URL)

# Set up Python logging from the alembic.ini [loggers] section.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


# ---------------------------------------------------------------------------
# Offline migrations (no live DB connection — generates SQL script)
# ---------------------------------------------------------------------------


def run_migrations_offline() -> None:
    """Generate SQL without a live DB connection."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
        compare_server_default=True,
    )
    with context.begin_transaction():
        context.run_migrations()


# ---------------------------------------------------------------------------
# Online migrations (async runner)
# ---------------------------------------------------------------------------


def do_run_migrations(connection: Connection) -> None:
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        compare_type=True,
        compare_server_default=True,
    )
    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    """Create an async engine and run migrations inside a sync wrapper."""
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,  # NullPool is correct for migration scripts
    )
    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)
    await connectable.dispose()


def run_migrations_online() -> None:
    asyncio.run(run_async_migrations())


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
