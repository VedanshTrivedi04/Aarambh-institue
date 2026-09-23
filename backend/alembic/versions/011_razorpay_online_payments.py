"""
011_razorpay_online_payments — Online payment gateway integration.

Adds:
  - payments.razorpay_order_id / razorpay_payment_id / razorpay_signature
  - razorpay_orders table (tracks an Order from creation through settlement)
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "011"
down_revision = "010"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ── payments: online gateway linkage columns ────────────────────────────
    op.add_column("payments", sa.Column("razorpay_order_id", sa.String(length=64), nullable=True))
    op.add_column("payments", sa.Column("razorpay_payment_id", sa.String(length=64), nullable=True))
    op.add_column("payments", sa.Column("razorpay_signature", sa.String(length=255), nullable=True))
    op.create_index("ix_payments_razorpay_order_id", "payments", ["razorpay_order_id"])
    op.create_index("ix_payments_razorpay_payment_id", "payments", ["razorpay_payment_id"])

    # ── razorpay_orders ──────────────────────────────────────────────────────
    razorpay_order_status_enum = postgresql.ENUM(
        "CREATED", "PAID", "FAILED",
        name="razorpay_order_status_enum", create_type=False,
    )
    razorpay_order_status_enum.create(op.get_bind(), checkfirst=True)

    op.create_table(
        "razorpay_orders",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("institute_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("institutes.id", ondelete="RESTRICT"), nullable=True, index=True),
        sa.Column("branch_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("branches.id", ondelete="RESTRICT"), nullable=True, index=True),
        sa.Column("installment_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("installments.id", ondelete="RESTRICT"), nullable=False, index=True),
        sa.Column("razorpay_order_id", sa.String(length=64), unique=True, nullable=False, index=True),
        sa.Column("amount", sa.Float(), nullable=False),
        sa.Column("status", razorpay_order_status_enum, nullable=False, server_default="CREATED", index=True),
        sa.Column("payment_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("payments.id", ondelete="RESTRICT"), nullable=True),
        sa.Column("initiated_by", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("users.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True),
                  server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True),
                  server_default=sa.func.now(), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("razorpay_orders")
    sa.Enum(name="razorpay_order_status_enum").drop(op.get_bind(), checkfirst=True)

    op.drop_index("ix_payments_razorpay_payment_id", table_name="payments")
    op.drop_index("ix_payments_razorpay_order_id", table_name="payments")
    op.drop_column("payments", "razorpay_signature")
    op.drop_column("payments", "razorpay_payment_id")
    op.drop_column("payments", "razorpay_order_id")
