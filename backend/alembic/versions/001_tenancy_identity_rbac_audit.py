"""
001_tenancy_identity_rbac_audit — Initial schema migration.

Creates:
  - institutes
  - branches
  - permissions
  - roles
  - role_permissions
  - users  (with status enum)
  - user_roles
  - user_sessions
  - password_resets
  - audit_logs

REVIEW NOTES (migration policy — backend.md §11):
  - All FK constraints use RESTRICT on business-critical references to prevent
    accidental orphan data.
  - CASCADE is used only where child data is always owned by the parent
    (sessions → user, password_resets → user).
  - UUID primary keys throughout (rules.md §9 — no sequential IDs in public URLs).
  - JSONB used for audit_logs.old_values / new_values for schema flexibility.
  - Composite indexes and unique constraints match the access patterns in
    codeoptimisation.md and systemdesign.md §6.

Revision IDs
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ── institutes ────────────────────────────────────────────────────────
    op.create_table(
        "institutes",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("code", sa.String(50), nullable=False),
        sa.Column("logo_url", sa.String(500), nullable=True),
        sa.Column("address", sa.Text, nullable=True),
        sa.Column("contact_email", sa.String(255), nullable=True),
        sa.Column("contact_phone", sa.String(20), nullable=True),
        sa.Column("is_active", sa.Boolean, nullable=False, server_default="true"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.UniqueConstraint("code", name="uq_institutes_code"),
    )
    op.create_index("ix_institutes_deleted_at", "institutes", ["deleted_at"])

    # ── branches ──────────────────────────────────────────────────────────
    op.create_table(
        "branches",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("institute_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("institutes.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("code", sa.String(50), nullable=False),
        sa.Column("address", sa.Text, nullable=True),
        sa.Column("contact_number", sa.String(20), nullable=True),
        sa.Column("is_main_branch", sa.Boolean, nullable=False, server_default="false"),
        sa.Column("is_active", sa.Boolean, nullable=False, server_default="true"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.UniqueConstraint("institute_id", "code", name="uq_branches_institute_code"),
    )
    op.create_index("ix_branches_institute_id", "branches", ["institute_id"])
    op.create_index("ix_branches_deleted_at", "branches", ["deleted_at"])

    # ── permissions ───────────────────────────────────────────────────────
    op.create_table(
        "permissions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("slug", sa.String(100), nullable=False),
        sa.Column("name", sa.String(150), nullable=False),
        sa.Column("module", sa.String(60), nullable=False),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint("slug", name="uq_permissions_slug"),
    )
    op.create_index("ix_permissions_module", "permissions", ["module"])

    # ── roles ─────────────────────────────────────────────────────────────
    op.create_table(
        "roles",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("institute_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("institutes.id", ondelete="CASCADE"), nullable=True),
        sa.Column("slug", sa.String(60), nullable=False),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("is_system_role", sa.Boolean, nullable=False, server_default="false"),
        sa.Column("is_active", sa.Boolean, nullable=False, server_default="true"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint("institute_id", "slug", name="uq_roles_institute_slug"),
    )
    op.create_index("ix_roles_institute_id", "roles", ["institute_id"])

    # ── role_permissions ──────────────────────────────────────────────────
    op.create_table(
        "role_permissions",
        sa.Column("role_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("roles.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("permission_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("permissions.id", ondelete="CASCADE"), primary_key=True),
        sa.UniqueConstraint("role_id", "permission_id", name="uq_role_permissions"),
    )

    # ── user_status enum ──────────────────────────────────────────────────
    op.execute("CREATE TYPE user_status_enum AS ENUM ('ACTIVE','INACTIVE','SUSPENDED','PENDING')")

    # ── users ─────────────────────────────────────────────────────────────
    op.create_table(
        "users",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("institute_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("institutes.id", ondelete="RESTRICT"), nullable=True),
        sa.Column("email", sa.String(255), nullable=True),
        sa.Column("mobile", sa.String(20), nullable=True),
        sa.Column("password_hash", sa.String(500), nullable=False),
        sa.Column("role", sa.String(60), nullable=False),
        sa.Column("status", postgresql.ENUM(
            "ACTIVE", "INACTIVE", "SUSPENDED", "PENDING",
            name="user_status_enum", create_type=False
        ), nullable=False, server_default="ACTIVE"),
        sa.Column("is_active", sa.Boolean, nullable=False, server_default="true"),
        sa.Column("is_verified", sa.Boolean, nullable=False, server_default="false"),
        sa.Column("last_login_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("failed_login_attempts", sa.Integer, nullable=False, server_default="0"),
        sa.Column("locked_until", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.UniqueConstraint("email", name="uq_users_email"),
        sa.UniqueConstraint("mobile", name="uq_users_mobile"),
        sa.CheckConstraint("email IS NOT NULL OR mobile IS NOT NULL", name="ck_users_email_or_mobile"),
    )
    op.create_index("ix_users_institute_id", "users", ["institute_id"])
    op.create_index("ix_users_email", "users", ["email"])
    op.create_index("ix_users_mobile", "users", ["mobile"])
    op.create_index("ix_users_role", "users", ["role"])
    op.create_index("ix_users_status", "users", ["status"])
    op.create_index("ix_users_deleted_at", "users", ["deleted_at"])

    # ── user_roles ────────────────────────────────────────────────────────
    op.create_table(
        "user_roles",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("role_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("roles.id", ondelete="CASCADE"), nullable=False),
        sa.Column("branch_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("branches.id", ondelete="CASCADE"), nullable=True),
        sa.Column("granted_by", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint("user_id", "role_id", "branch_id", name="uq_user_roles"),
    )
    op.create_index("ix_user_roles_user_id", "user_roles", ["user_id"])
    op.create_index("ix_user_roles_role_id", "user_roles", ["role_id"])
    op.create_index("ix_user_roles_branch_id", "user_roles", ["branch_id"])

    # ── user_sessions ─────────────────────────────────────────────────────
    op.create_table(
        "user_sessions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("refresh_token_jti", sa.String(255), nullable=False, unique=True),
        sa.Column("device_info", sa.String(500), nullable=True),
        sa.Column("ip_address", sa.String(45), nullable=True),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("revoked_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_used_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_user_sessions_user_id", "user_sessions", ["user_id"])
    op.create_index("ix_user_sessions_refresh_token_jti", "user_sessions", ["refresh_token_jti"])

    # ── password_resets ───────────────────────────────────────────────────
    op.create_table(
        "password_resets",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("token_hash", sa.String(64), nullable=False, unique=True),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("used_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_password_resets_user_id", "password_resets", ["user_id"])

    # ── audit_logs ────────────────────────────────────────────────────────
    op.create_table(
        "audit_logs",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("institute_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("institutes.id", ondelete="SET NULL"), nullable=True),
        sa.Column("actor_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("actor_role", sa.String(60), nullable=True),
        sa.Column("action", sa.String(100), nullable=False),
        sa.Column("entity_name", sa.String(100), nullable=False),
        sa.Column("entity_id", sa.String(100), nullable=False),
        sa.Column("old_values", postgresql.JSONB, nullable=True),
        sa.Column("new_values", postgresql.JSONB, nullable=True),
        sa.Column("ip_address", sa.String(45), nullable=True),
        sa.Column("request_id", sa.String(100), nullable=True),
        sa.Column("user_agent", sa.Text, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_audit_logs_institute_id", "audit_logs", ["institute_id"])
    op.create_index("ix_audit_logs_actor_id", "audit_logs", ["actor_id"])
    op.create_index("ix_audit_logs_action", "audit_logs", ["action"])
    op.create_index("ix_audit_logs_entity_name", "audit_logs", ["entity_name"])
    op.create_index("ix_audit_logs_entity_id", "audit_logs", ["entity_id"])
    op.create_index("ix_audit_logs_created_at", "audit_logs", ["created_at"])


def downgrade() -> None:
    op.drop_table("audit_logs")
    op.drop_table("password_resets")
    op.drop_table("user_sessions")
    op.drop_table("user_roles")
    op.drop_table("users")
    op.execute("DROP TYPE IF EXISTS user_status_enum")
    op.drop_table("role_permissions")
    op.drop_table("roles")
    op.drop_table("permissions")
    op.drop_table("branches")
    op.drop_table("institutes")
