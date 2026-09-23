"""
app/schemas/finance.py
----------------------
Pydantic schemas for Slice 9: Finance & Immutable Ledger.
"""

from __future__ import annotations

import uuid
from datetime import date as Date, datetime
from pydantic import BaseModel, ConfigDict, Field

from app.models.finance import (
    AdjustmentType,
    FeePlanType,
    InstallmentStatus,
    PaymentMethod,
    RazorpayOrderStatus,
)


# ─── Installments & Receipts ──────────────────────────────────────────────────

class InstallmentRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    fee_plan_id: uuid.UUID
    installment_number: int
    amount: float
    due_date: Date
    status: InstallmentStatus
    paid_amount: float
    balance_amount: float = 0.0


class ReceiptRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    payment_id: uuid.UUID
    receipt_number: str
    pdf_storage_key: str | None
    issued_at: datetime
    created_at: datetime


# ─── Payment Adjustments ──────────────────────────────────────────────────────

class PaymentAdjustmentCreate(BaseModel):
    adjustment_type: AdjustmentType
    amount: float = Field(..., gt=0, description="Adjustment amount (positive value)")
    reason: str = Field(..., min_length=3, description="Justification/audit rationale for ledger adjustment")


class PaymentAdjustmentRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    payment_id: uuid.UUID
    adjustment_type: AdjustmentType
    amount: float
    reason: str
    authorized_by: uuid.UUID
    authorized_by_name: str | None = None
    created_at: datetime


# ─── Payments ─────────────────────────────────────────────────────────────────

class PaymentRecordRequest(BaseModel):
    installment_id: uuid.UUID
    amount: float = Field(..., gt=0, description="Amount received")
    payment_method: PaymentMethod
    transaction_reference: str | None = Field(None, description="Bank/UPI/UTR transaction reference")
    idempotency_key: str = Field(..., min_length=8, max_length=255, description="Client idempotency key to prevent duplicate charge")


class PaymentRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    installment_id: uuid.UUID
    amount: float
    payment_method: PaymentMethod
    transaction_reference: str | None
    idempotency_key: str
    paid_at: datetime
    recorded_by: uuid.UUID
    recorded_by_name: str | None = None
    created_at: datetime
    receipt: ReceiptRead | None = None
    adjustments: list[PaymentAdjustmentRead] = []


# ─── Fee Plans ────────────────────────────────────────────────────────────────

class FeePlanCreate(BaseModel):
    enrollment_id: uuid.UUID
    total_amount: float = Field(..., gt=0, description="Gross fee amount before deductions")
    discount_amount: float = Field(0.0, ge=0, description="Management/promotional discount")
    scholarship_amount: float = Field(0.0, ge=0, description="Merit/category scholarship deduction")
    discount_reason: str | None = Field(None, description="Reason for discount or scholarship allocation")
    plan_type: FeePlanType = Field(FeePlanType.LUMP_SUM, description="Lump sum vs Installment schedule")
    installment_count: int = Field(1, ge=1, le=12, description="Number of installments if plan_type is INSTALLMENT")
    first_due_date: Date = Field(..., description="First installment or lump sum due date")


class FeePlanUpdate(BaseModel):
    discount_reason: str | None = None


class FeePlanRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    institute_id: uuid.UUID
    enrollment_id: uuid.UUID
    total_amount: float
    discount_amount: float
    scholarship_amount: float
    net_amount: float
    plan_type: FeePlanType
    discount_reason: str | None
    created_by: uuid.UUID
    created_at: datetime
    updated_at: datetime

    student_name: str | None = None
    student_admission_number: str | None = None
    course_name: str | None = None
    batch_name: str | None = None
    total_paid: float = 0.0
    outstanding_balance: float = 0.0
    installments: list[InstallmentRead] = []


# ─── Student Aggregated Overview ──────────────────────────────────────────────

class StudentFeeSummary(BaseModel):
    student_id: uuid.UUID
    student_name: str
    admission_number: str
    total_fee: float
    total_paid: float
    total_outstanding: float
    plans: list[FeePlanRead] = []
    next_due_installment: InstallmentRead | None = None


# ─── Razorpay Online Payments ──────────────────────────────────────────────────

class RazorpayOrderCreateRequest(BaseModel):
    installment_id: uuid.UUID


class RazorpayOrderCreateResponse(BaseModel):
    """Everything the frontend needs to open Razorpay Checkout."""

    razorpay_order_id: str
    razorpay_key_id: str
    amount: int = Field(..., description="Amount in paise, as required by Razorpay Checkout")
    currency: str = "INR"
    installment_id: uuid.UUID
    name: str = Field(..., description="Institute/business name shown in the checkout modal")
    description: str = Field(..., description="e.g. 'Installment 2 of 3 — Class 10th Fee'")
    prefill_name: str | None = None
    prefill_email: str | None = None
    prefill_contact: str | None = None


class RazorpayVerifyRequest(BaseModel):
    razorpay_order_id: str
    razorpay_payment_id: str
    razorpay_signature: str


class RazorpayOrderStatusRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    razorpay_order_id: str
    status: RazorpayOrderStatus
    amount: float
    installment_id: uuid.UUID
