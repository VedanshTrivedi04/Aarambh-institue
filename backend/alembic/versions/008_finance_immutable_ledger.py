"""
008_finance_immutable_ledger — Fee Plans, Installments, Payments, Adjustments & Receipts.

Creates:
  - fee_plans
  - installments
  - payments
  - payment_adjustments
  - receipts
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "008"
down_revision = "007"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ── Enums ─────────────────────────────────────────────────────────────
    fee_plan_type_enum = postgresql.ENUM(
        "LUMP_SUM", "INSTALLMENT",
        name="fee_plan_type_enum", create_type=False,
    )
    fee_plan_type_enum.create(op.get_bind(), checkfirst=True)

    installment_status_enum = postgresql.ENUM(
        "UPCOMING", "DUE", "PAID", "OVERDUE",
        name="installment_status_enum", create_type=False,
    )
    installment_status_enum.create(op.get_bind(), checkfirst=True)

    payment_method_enum = postgresql.ENUM(
        "CASH", "UPI", "BANK_TRANSFER", "CARD", "ONLINE",
        name="payment_method_enum", create_type=False,
    )
    payment_method_enum.create(op.get_bind(), checkfirst=True)

    adjustment_type_enum = postgresql.ENUM(
        "CORRECTION", "REVERSAL", "REFUND",
        name="adjustment_type_enum", create_type=False,
    )
    adjustment_type_enum.create(op.get_bind(), checkfirst=True)

    # ── fee_plans ─────────────────────────────────────────────────────────
    op.create_table(
        "fee_plans",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("institute_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("institutes.id", ondelete="RESTRICT"), nullable=True, index=True),
        sa.Column("branch_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("branches.id", ondelete="RESTRICT"), nullable=True, index=True),
        sa.Column("enrollment_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("enrollments.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("total_amount", sa.Float(), nullable=False),
        sa.Column("discount_amount", sa.Float(), nullable=False, server_default=sa.text("0.0")),
        sa.Column("scholarship_amount", sa.Float(), nullable=False, server_default=sa.text("0.0")),
        sa.Column("net_amount", sa.Float(), nullable=False),
        sa.Column("plan_type", fee_plan_type_enum, nullable=False, server_default="LUMP_SUM"),
        sa.Column("discount_reason", sa.Text(), nullable=True),
        sa.Column("created_by", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("users.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True),
                  server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True),
                  server_default=sa.func.now(), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True, index=True),
    )

    # ── installments ──────────────────────────────────────────────────────
    op.create_table(
        "installments",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("institute_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("institutes.id", ondelete="RESTRICT"), nullable=True, index=True),
        sa.Column("branch_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("branches.id", ondelete="RESTRICT"), nullable=True, index=True),
        sa.Column("fee_plan_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("fee_plans.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("installment_number", sa.Integer(), nullable=False),
        sa.Column("amount", sa.Float(), nullable=False),
        sa.Column("due_date", sa.Date(), nullable=False, index=True),
        sa.Column("status", installment_status_enum, nullable=False, server_default="UPCOMING", index=True),
        sa.Column("paid_amount", sa.Float(), nullable=False, server_default=sa.text("0.0")),
        sa.Column("created_at", sa.DateTime(timezone=True),
                  server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True),
                  server_default=sa.func.now(), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True, index=True),
        sa.UniqueConstraint("fee_plan_id", "installment_number", name="uq_installment_plan_num"),
    )

    # ── payments ──────────────────────────────────────────────────────────
    op.create_table(
        "payments",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("institute_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("institutes.id", ondelete="RESTRICT"), nullable=True, index=True),
        sa.Column("branch_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("branches.id", ondelete="RESTRICT"), nullable=True, index=True),
        sa.Column("installment_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("installments.id", ondelete="RESTRICT"), nullable=False, index=True),
        sa.Column("amount", sa.Float(), nullable=False),
        sa.Column("payment_method", payment_method_enum, nullable=False),
        sa.Column("transaction_reference", sa.String(length=255), nullable=True),
        sa.Column("idempotency_key", sa.String(length=255), unique=True, nullable=False, index=True),
        sa.Column("paid_at", sa.DateTime(timezone=True),
                  server_default=sa.func.now(), nullable=False),
        sa.Column("recorded_by", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("users.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True),
                  server_default=sa.func.now(), nullable=False),
    )

    # ── payment_adjustments ───────────────────────────────────────────────
    op.create_table(
        "payment_adjustments",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("institute_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("institutes.id", ondelete="RESTRICT"), nullable=True, index=True),
        sa.Column("branch_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("branches.id", ondelete="RESTRICT"), nullable=True, index=True),
        sa.Column("payment_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("payments.id", ondelete="RESTRICT"), nullable=False, index=True),
        sa.Column("adjustment_type", adjustment_type_enum, nullable=False),
        sa.Column("amount", sa.Float(), nullable=False),
        sa.Column("reason", sa.Text(), nullable=False),
        sa.Column("authorized_by", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("users.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True),
                  server_default=sa.func.now(), nullable=False),
    )

    # ── receipts ──────────────────────────────────────────────────────────
    op.create_table(
        "receipts",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("institute_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("institutes.id", ondelete="RESTRICT"), nullable=True, index=True),
        sa.Column("branch_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("branches.id", ondelete="RESTRICT"), nullable=True, index=True),
        sa.Column("payment_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("payments.id", ondelete="RESTRICT"), unique=True, nullable=False, index=True),
        sa.Column("receipt_number", sa.String(length=64), unique=True, nullable=False, index=True),
        sa.Column("pdf_storage_key", sa.String(length=512), nullable=True),
        sa.Column("issued_at", sa.DateTime(timezone=True),
                  server_default=sa.func.now(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True),
                  server_default=sa.func.now(), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("receipts")
    op.drop_table("payment_adjustments")
    op.drop_table("payments")
    op.drop_table("installments")
    op.drop_table("fee_plans")

    for enum_name in [
        "adjustment_type_enum",
        "payment_method_enum",
        "installment_status_enum",
        "fee_plan_type_enum",
    ]:
        sa.Enum(name=enum_name).drop(op.get_bind(), checkfirst=True)
