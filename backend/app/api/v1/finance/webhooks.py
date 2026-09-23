"""
app/api/v1/finance/webhooks.py
-------------------------------
Server-to-server Razorpay webhook. This is the durable settlement path:
even if a student closes their browser right after paying (so the
client-side /verify call never fires), this endpoint still confirms the
charge and appends the Payment ledger row.

Unauthenticated by design (Razorpay calls it directly) — trust is
established purely via the HMAC signature on the raw request body.
"""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, Header, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ValidationError
from app.core.logging import get_logger
from app.db.session import get_db
from app.services import finance_service, razorpay_service

logger = get_logger("api.finance.webhooks")

router = APIRouter(tags=["Finance - Webhooks"])


@router.post(
    "/webhooks/razorpay",
    status_code=status.HTTP_200_OK,
    summary="Razorpay webhook — durable server-to-server payment confirmation",
)
async def razorpay_webhook(
    request: Request,
    db: AsyncSession = Depends(get_db),
    x_razorpay_signature: str | None = Header(default=None, alias="X-Razorpay-Signature"),
):
    raw_body = await request.body()

    if not x_razorpay_signature or not razorpay_service.verify_webhook_signature(
        raw_body=raw_body, signature_header=x_razorpay_signature
    ):
        raise ValidationError("Invalid Razorpay webhook signature.")

    payload = await request.json()
    event = payload.get("event")

    if event != "payment.captured":
        # Acknowledge and ignore events we don't act on (order.paid, payment.failed, etc.)
        logger.info("Ignored Razorpay webhook event", extra={"event": event})
        return {"status": "ignored", "event": event}

    entity = payload.get("payload", {}).get("payment", {}).get("entity", {})
    razorpay_order_id = entity.get("order_id")
    razorpay_payment_id = entity.get("id")
    notes = entity.get("notes") or {}
    institute_id_raw = notes.get("institute_id")

    if not razorpay_order_id or not razorpay_payment_id or not institute_id_raw:
        logger.warning("Razorpay webhook missing required fields", extra={"payload": payload})
        return {"status": "ignored", "reason": "missing_fields"}

    await finance_service.confirm_razorpay_payment(
        db=db,
        institute_id=uuid.UUID(institute_id_raw),
        razorpay_order_id=razorpay_order_id,
        razorpay_payment_id=razorpay_payment_id,
        razorpay_signature=None,  # already verified at the webhook envelope level
        request=request,
    )
    await db.commit()

    return {"status": "ok"}
