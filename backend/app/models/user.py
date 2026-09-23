"""
app/models/user.py
------------------
User (authentication identity), UserSession (stateful refresh tokens),
and PasswordReset (password recovery flow).

Key design decisions:
  - User = login credentials + status + lifecycle ONLY.
  - Domain profiles (StudentProfile, TeacherProfile, ParentProfile) live in
    separate models (Slice 4) and have a 1-to-1 FK to User.
  - `role` stores the PRIMARY role slug (e.g. "TEACHER") for fast JWT claims.
    Full permission resolution uses UserRole + RolePermission (role.py).
  - `status` gives finer control than a boolean:
      ACTIVE → can log in and use the app
      INACTIVE → account disabled by admin (e.g. student left institute)
      SUSPENDED → temporarily blocked (e.g. too many failed logins)
      PENDING → account created but email/mobile not yet verified

UserSession (rules.md §4, architectural review §5):
  - Every login creates a UserSession row storing the refresh token JTI.
  - Logout marks the session as revoked (revoked_at = now).
  - "Logout all devices" revokes all active sessions for the user.
  - Refresh token reuse detection: if a revoked JTI is presented again,
    all sessions for that user are immediately revoked (stolen token signal).

PasswordReset:
  - Time-limited, single-use token for the forgot-password flow.
  - Token is stored as a SHA-256 hash — never in plain text.
"""

from __future__ import annotations

import enum
import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    DateTime,
    Enum,
    ForeignKey,
    String,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, SoftDeleteMixin, TimestampMixin

if TYPE_CHECKING:
    from app.models.role import UserRole


class UserStatus(str, enum.Enum):
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    SUSPENDED = "SUSPENDED"
    PENDING = "PENDING"           # awaiting first-time verification


class User(TimestampMixin, SoftDeleteMixin, Base):
    """
    Authentication identity — login credentials and account lifecycle.

    Does NOT contain student/teacher/parent domain data;
    those live in profile models (Slice 4).
    """

    __tablename__ = "users"
    __table_args__ = (
        UniqueConstraint("email", name="uq_users_email"),
        UniqueConstraint("mobile", name="uq_users_mobile"),
        CheckConstraint(
            "email IS NOT NULL OR mobile IS NOT NULL",
            name="ck_users_email_or_mobile",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    # institute_id links this user to a tenant.
    # NULL is only allowed for a super-admin seeded at bootstrap.
    institute_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("institutes.id", ondelete="RESTRICT"),
        nullable=True,
        index=True,
    )

    email: Mapped[str | None] = mapped_column(String(255), nullable=True, index=True)
    mobile: Mapped[str | None] = mapped_column(String(20), nullable=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(500), nullable=False)

    # Primary role slug — stored for fast JWT claim generation.
    # Full RBAC uses UserRole table.
    role: Mapped[str] = mapped_column(String(60), nullable=False, index=True)

    status: Mapped[UserStatus] = mapped_column(
        Enum(UserStatus, name="user_status_enum"),
        default=UserStatus.ACTIVE,
        nullable=False,
        index=True,
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    last_login_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    failed_login_attempts: Mapped[int] = mapped_column(default=0, nullable=False)
    locked_until: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # Relationships
    sessions: Mapped[list["UserSession"]] = relationship(
        "UserSession", back_populates="user", lazy="noload", cascade="all, delete-orphan"
    )
    password_resets: Mapped[list["PasswordReset"]] = relationship(
        "PasswordReset", back_populates="user", lazy="noload", cascade="all, delete-orphan"
    )
    user_roles: Mapped[list["UserRole"]] = relationship(
        "UserRole", back_populates="user", lazy="noload"
    )

    def __repr__(self) -> str:
        return f"<User id={self.id} role={self.role!r} status={self.status}>"


class UserSession(TimestampMixin, Base):
    """
    Tracks active refresh token sessions.

    One row per issued refresh token.
    Revoked on logout; all rows for a user revoked on logout-all-devices.

    `refresh_token_jti` — the JWT ID claim from the refresh token.
    `device_info`       — browser/OS string for display in "active sessions" UI.
    """

    __tablename__ = "user_sessions"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    refresh_token_jti: Mapped[str] = mapped_column(
        String(255), nullable=False, unique=True, index=True
    )
    device_info: Mapped[str | None] = mapped_column(String(500), nullable=True)
    ip_address: Mapped[str | None] = mapped_column(String(45), nullable=True)  # IPv6 max length
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    revoked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    last_used_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    user: Mapped["User"] = relationship("User", back_populates="sessions", lazy="noload")

    @property
    def is_revoked(self) -> bool:
        return self.revoked_at is not None

    @property
    def is_expired(self) -> bool:
        from datetime import UTC
        from datetime import datetime as dt
        return dt.now(UTC) > self.expires_at

    @property
    def is_valid(self) -> bool:
        return not self.is_revoked and not self.is_expired

    def __repr__(self) -> str:
        return f"<UserSession id={self.id} user_id={self.user_id} revoked={self.is_revoked}>"


class PasswordReset(TimestampMixin, Base):
    """
    Single-use, time-limited token for the forgot-password flow.

    The raw token is sent to the user via email/SMS.
    We store only a SHA-256 hash of it — never the plain token.
    On use, `used_at` is set and the token can never be reused.
    """

    __tablename__ = "password_resets"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    token_hash: Mapped[str] = mapped_column(String(64), nullable=False, unique=True)  # SHA-256 hex
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    used_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    user: Mapped["User"] = relationship("User", back_populates="password_resets", lazy="noload")

    @property
    def is_used(self) -> bool:
        return self.used_at is not None

    @property
    def is_expired(self) -> bool:
        from datetime import UTC
        from datetime import datetime as dt
        return dt.now(UTC) > self.expires_at

    @property
    def is_valid(self) -> bool:
        return not self.is_used and not self.is_expired

    def __repr__(self) -> str:
        return f"<PasswordReset id={self.id} user_id={self.user_id} used={self.is_used}>"
