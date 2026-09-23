"""
app/models/finance.py
---------------------
Finance & Immutable Ledger domain models:
  - FeePlan: High-level fee schedule linked to an Enrollment (lump-sum or installments)
  - Installment: Individual milestone payment due date and amount
  - Payment: Append-only financial transaction record (never updated or deleted in place)
  - PaymentAdjustment: Append-only correction/reversal/refund record for an existing payment
  - Receipt: Generated receipt with unique sequential/human-readable numbering
"""

from __future__ import annotations

import enum
import uuid
from datetime import date as Date, datetime, timezone
from typing import TYPE_CHECKING

from sqlalchemy import (
    Date as SADate,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, SoftDeleteMixin, TenantAwareMixin, TimestampMixin

if TYPE_CHECKING:
    from app.models.enrollment import Enrollment
    from app.models.user import User


class FeePlanType(str, enum.Enum):
    LUMP_SUM = "LUMP_SUM"
    INSTALLMENT = "INSTALLMENT"


class InstallmentStatus(str, enum.Enum):
    UPCOMING = "UPCOMING"
    DUE = "DUE"
    PAID = "PAID"
    OVERDUE = "OVERDUE"


class PaymentMethod(str, enum.Enum):
    CASH = "CASH"
    UPI = "UPI"
    BANK_TRANSFER = "BANK_TRANSFER"
    CARD = "CARD"
    ONLINE = "ONLINE"


class RazorpayOrderStatus(str, enum.Enum):
    CREATED = "CREATED"
    PAID = "PAID"
    FAILED = "FAILED"


class AdjustmentType(str, enum.Enum):
    CORRECTION = "CORRECTION"
    REVERSAL = "REVERSAL"
    REFUND = "REFUND"


class FeePlan(TimestampMixin, SoftDeleteMixin, TenantAwareMixin, Base):
    """
    Agreed fee schedule for a student's enrollment in a course/batch.
    Contains discount and scholarship deductions, net amount, and links to installments.
    """

    __tablename__ = "fee_plans"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    enrollment_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("enrollments.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    total_amount: Mapped[float] = mapped_column(Float, nullable=False)
    discount_amount: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    scholarship_amount: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    net_amount: Mapped[float] = mapped_column(Float, nullable=False)
    plan_type: Mapped[FeePlanType] = mapped_column(
        Enum(FeePlanType, name="fee_plan_type_enum"),
        nullable=False,
        default=FeePlanType.LUMP_SUM,
    )
    discount_reason: Mapped[str | None] = mapped_column(Text, nullable=True)

    created_by: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=False,
    )

    # Relationships
    enrollment: Mapped[Enrollment] = relationship("Enrollment", lazy="noload")
    creator: Mapped[User] = relationship("User", foreign_keys=[created_by], lazy="noload")
    installments: Mapped[list[Installment]] = relationship(
        "Installment",
        back_populates="fee_plan",
        cascade="all, delete-orphan",
        order_by="Installment.installment_number",
        lazy="selectin",
    )


class Installment(TimestampMixin, SoftDeleteMixin, TenantAwareMixin, Base):
    """
    Scheduled milestone payment within a FeePlan.
    """

    __tablename__ = "installments"
    __table_args__ = (
        UniqueConstraint("fee_plan_id", "installment_number", name="uq_installment_plan_num"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    fee_plan_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("fee_plans.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    installment_number: Mapped[int] = mapped_column(Integer, nullable=False)
    amount: Mapped[float] = mapped_column(Float, nullable=False)
    due_date: Mapped[Date] = mapped_column(SADate, nullable=False, index=True)
    status: Mapped[InstallmentStatus] = mapped_column(
        Enum(InstallmentStatus, name="installment_status_enum"),
        default=InstallmentStatus.UPCOMING,
        nullable=False,
        index=True,
    )
    paid_amount: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)

    # Relationships
    fee_plan: Mapped[FeePlan] = relationship("FeePlan", back_populates="installments", lazy="noload")
    payments: Mapped[list[Payment]] = relationship(
        "Payment",
        back_populates="installment",
        order_by="Payment.created_at",
        lazy="selectin",
    )


class Payment(TenantAwareMixin, Base):
    """
    Append-only ledger entry representing funds received for an installment.
    Strictly NO in-place edits and NO soft-deletes.
    Corrections are performed via PaymentAdjustment records.
    """

    __tablename__ = "payments"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    installment_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("installments.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )

    amount: Mapped[float] = mapped_column(Float, nullable=False)
    payment_method: Mapped[PaymentMethod] = mapped_column(
        Enum(PaymentMethod, name="payment_method_enum"),
        nullable=False,
    )
    transaction_reference: Mapped[str | None] = mapped_column(String(255), nullable=True)
    idempotency_key: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    razorpay_order_id: Mapped[str | None] = mapped_column(String(64), nullable=True, index=True)
    razorpay_payment_id: Mapped[str | None] = mapped_column(String(64), nullable=True, index=True)
    razorpay_signature: Mapped[str | None] = mapped_column(String(255), nullable=True)
    paid_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    recorded_by: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Relationships
    installment: Mapped[Installment] = relationship("Installment", back_populates="payments", lazy="noload")
    recorder: Mapped[User] = relationship("User", foreign_keys=[recorded_by], lazy="noload")
    adjustments: Mapped[list[PaymentAdjustment]] = relationship(
        "PaymentAdjustment",
        back_populates="payment",
        order_by="PaymentAdjustment.created_at",
        lazy="selectin",
    )
    receipt: Mapped[Receipt | None] = relationship(
        "Receipt",
        back_populates="payment",
        uselist=False,
        lazy="selectin",
    )


class PaymentAdjustment(TenantAwareMixin, Base):
    """
    Append-only ledger adjustment record (correction, reversal, or refund) applied to a Payment.
    """

    __tablename__ = "payment_adjustments"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    payment_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("payments.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )

    adjustment_type: Mapped[AdjustmentType] = mapped_column(
        Enum(AdjustmentType, name="adjustment_type_enum"),
        nullable=False,
    )
    amount: Mapped[float] = mapped_column(Float, nullable=False)
    reason: Mapped[str] = mapped_column(Text, nullable=False)
    authorized_by: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Relationships
    payment: Mapped[Payment] = relationship("Payment", back_populates="adjustments", lazy="noload")
    authorizer: Mapped[User] = relationship("User", foreign_keys=[authorized_by], lazy="noload")


class Receipt(TenantAwareMixin, Base):
    """
    Generated receipt for a payment with unique receipt numbering.
    """

    __tablename__ = "receipts"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    payment_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("payments.id", ondelete="RESTRICT"),
        unique=True,
        nullable=False,
        index=True,
    )
    receipt_number: Mapped[str] = mapped_column(String(64), unique=True, nullable=False, index=True)
    pdf_storage_key: Mapped[str | None] = mapped_column(String(512), nullable=True)
    issued_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Relationships
    payment: Mapped[Payment] = relationship("Payment", back_populates="receipt", lazy="noload")


class RazorpayOrder(TenantAwareMixin, Base):
    """
    Tracks a Razorpay Order created for an installment, from creation through
    settlement. This exists because a Razorpay Order is created *before* any
    money has moved — the eventual Payment ledger row is only appended once
    the checkout signature (or the webhook) confirms the charge succeeded.
    """

    __tablename__ = "razorpay_orders"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    installment_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("installments.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    razorpay_order_id: Mapped[str] = mapped_column(String(64), unique=True, nullable=False, index=True)
    amount: Mapped[float] = mapped_column(Float, nullable=False)
    status: Mapped[RazorpayOrderStatus] = mapped_column(
        Enum(RazorpayOrderStatus, name="razorpay_order_status_enum"),
        default=RazorpayOrderStatus.CREATED,
        nullable=False,
        index=True,
    )
    payment_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("payments.id", ondelete="RESTRICT"),
        nullable=True,
    )
    initiated_by: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Relationships
    installment: Mapped[Installment] = relationship("Installment", lazy="noload")
    payment: Mapped[Payment | None] = relationship("Payment", lazy="noload")
