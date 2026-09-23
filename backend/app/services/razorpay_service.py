"""
app/services/razorpay_service.py
---------------------------------
Thin wrapper around the Razorpay SDK: Order creation, checkout-signature
verification, and webhook-signature verification.

No business/ledger logic lives here — that stays in finance_service, which
calls into this module only for the parts that talk to Razorpay itself.
"""

from __future__ import annotations

import hashlib
import hmac
from typing import Any

import razorpay

from app.core.config import get_settings
from app.core.exceptions import AppException, ValidationError
from app.core.logging import get_logger

logger = get_logger("services.razorpay")


class RazorpayNotConfiguredError(AppException):
    status_code = 503
    code = "RAZORPAY_NOT_CONFIGURED"


def _client() -> razorpay.Client:
    settings = get_settings()
    if not settings.RAZORPAY_KEY_ID or not settings.RAZORPAY_KEY_SECRET:
        raise RazorpayNotConfiguredError(
            "Razorpay is not configured. Set RAZORPAY_KEY_ID and RAZORPAY_KEY_SECRET."
        )
    return razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))


def rupees_to_paise(amount: float) -> int:
    """Razorpay amounts are always in the smallest currency unit (paise for INR)."""
    return int(round(amount * 100))


def create_order(*, amount_rupees: float, receipt: str, notes: dict[str, str]) -> dict[str, Any]:
    """
    Create a Razorpay Order. Returns the raw Razorpay order dict
    (contains `id`, `amount`, `currency`, `status`, ...).
    """
    client = _client()
    payload = {
        "amount": rupees_to_paise(amount_rupees),
        "currency": "INR",
        "receipt": receipt,
        "notes": notes,
        "payment_capture": 1,  # auto-capture on successful charge
    }
    try:
        order = client.order.create(data=payload)
    except razorpay.errors.BadRequestError as exc:
        raise ValidationError(f"Razorpay rejected the order request: {exc}") from exc
    logger.info("Created Razorpay order", extra={"razorpay_order_id": order.get("id"), "amount": payload["amount"]})
    return order


def verify_checkout_signature(
    *, razorpay_order_id: str, razorpay_payment_id: str, razorpay_signature: str
) -> bool:
    """
    Verify the signature Razorpay Checkout returns to the browser after a
    successful charge (HMAC-SHA256 of "order_id|payment_id" using the key secret).
    """
    settings = get_settings()
    if not settings.RAZORPAY_KEY_SECRET:
        raise RazorpayNotConfiguredError("Razorpay is not configured.")

    payload = f"{razorpay_order_id}|{razorpay_payment_id}".encode()
    expected = hmac.new(settings.RAZORPAY_KEY_SECRET.encode(), payload, hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, razorpay_signature)


def verify_webhook_signature(*, raw_body: bytes, signature_header: str) -> bool:
    """
    Verify the `X-Razorpay-Signature` header on an incoming webhook request
    against the raw request body, using the dashboard-configured webhook secret.
    """
    settings = get_settings()
    if not settings.RAZORPAY_WEBHOOK_SECRET:
        raise RazorpayNotConfiguredError("RAZORPAY_WEBHOOK_SECRET is not configured.")

    expected = hmac.new(settings.RAZORPAY_WEBHOOK_SECRET.encode(), raw_body, hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, signature_header)
