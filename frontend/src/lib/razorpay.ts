"use client";

import { authFetch } from "@/lib/auth";

// ---------------------------------------------------------------------------
// Types mirroring backend/app/schemas/finance.py
// ---------------------------------------------------------------------------

export interface RazorpayOrderCreateResponse {
  razorpay_order_id: string;
  razorpay_key_id: string;
  amount: number; // paise
  currency: string;
  installment_id: string;
  name: string;
  description: string;
  prefill_name?: string | null;
  prefill_email?: string | null;
  prefill_contact?: string | null;
}

export interface PaymentRead {
  id: string;
  installment_id: string;
  amount: number;
  payment_method: string;
  transaction_reference: string | null;
  paid_at: string;
  receipt?: { receipt_number: string } | null;
}

declare global {
  interface Window {
    Razorpay?: any;
  }
}

let scriptLoadPromise: Promise<void> | null = null;

/** Loads the Razorpay Checkout script once and caches the in-flight promise. */
function loadRazorpayScript(): Promise<void> {
  if (typeof window === "undefined") return Promise.reject(new Error("No window"));
  if (window.Razorpay) return Promise.resolve();
  if (scriptLoadPromise) return scriptLoadPromise;

  scriptLoadPromise = new Promise((resolve, reject) => {
    const script = document.createElement("script");
    script.src = "https://checkout.razorpay.com/v1/checkout.js";
    script.async = true;
    script.onload = () => resolve();
    script.onerror = () => reject(new Error("Failed to load Razorpay checkout script"));
    document.body.appendChild(script);
  });

  return scriptLoadPromise;
}

/** Creates a Razorpay order for the given installment via the backend. */
export async function createRazorpayOrder(
  installmentId: string
): Promise<{ data?: RazorpayOrderCreateResponse; error?: string }> {
  const res = await authFetch<RazorpayOrderCreateResponse>("/api/v1/finance/payments/razorpay/orders", {
    method: "POST",
    body: JSON.stringify({ installment_id: installmentId }),
  });
  if (res.error || !res.data) return { error: res.error || "Could not create payment order" };
  return { data: res.data };
}

/** Verifies a completed Razorpay checkout against the backend ledger. */
export async function verifyRazorpayPayment(payload: {
  razorpay_order_id: string;
  razorpay_payment_id: string;
  razorpay_signature: string;
}): Promise<{ data?: PaymentRead; error?: string }> {
  const res = await authFetch<PaymentRead>("/api/v1/finance/payments/razorpay/verify", {
    method: "POST",
    body: JSON.stringify(payload),
  });
  if (res.error || !res.data) return { error: res.error || "Payment verification failed" };
  return { data: res.data };
}

/**
 * End-to-end flow: create order -> open Razorpay Checkout -> verify on success.
 * Resolves with the recorded PaymentRead, or rejects with a human-readable message.
 */
export async function payInstallmentWithRazorpay(installmentId: string): Promise<PaymentRead> {
  const { data: order, error: orderError } = await createRazorpayOrder(installmentId);
  if (orderError || !order) throw new Error(orderError || "Could not start payment");

  await loadRazorpayScript();

  return new Promise<PaymentRead>((resolve, reject) => {
    const rzp = new window.Razorpay!({
      key: order.razorpay_key_id,
      amount: order.amount,
      currency: order.currency,
      name: order.name,
      description: order.description,
      order_id: order.razorpay_order_id,
      prefill: {
        name: order.prefill_name || undefined,
        email: order.prefill_email || undefined,
        contact: order.prefill_contact || undefined,
      },
      theme: { color: "#c22329" },
      handler: async (response: {
        razorpay_order_id: string;
        razorpay_payment_id: string;
        razorpay_signature: string;
      }) => {
        const { data: payment, error } = await verifyRazorpayPayment(response);
        if (error || !payment) {
          reject(new Error(error || "Payment succeeded but verification failed. Contact the office with your payment ID."));
          return;
        }
        resolve(payment);
      },
      modal: {
        ondismiss: () => reject(new Error("Payment cancelled")),
      },
    });
    rzp.on("payment.failed", (resp: any) => {
      reject(new Error(resp?.error?.description || "Payment failed"));
    });
    rzp.open();
  });
}
