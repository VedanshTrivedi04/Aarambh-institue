"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { authFetch, getCurrentUser, AuthUser } from "@/lib/auth";
import { payInstallmentWithRazorpay } from "@/lib/razorpay";
import {
  CreditCard,
  CheckCircle2,
  Clock,
  AlertTriangle,
  Loader2,
  ShieldCheck,
} from "lucide-react";

interface InstallmentRead {
  id: string;
  installment_number: number;
  amount: number;
  due_date: string;
  status: "UPCOMING" | "DUE" | "PAID" | "OVERDUE";
  paid_amount: number;
  balance_amount: number;
}

interface FeePlanRead {
  id: string;
  net_amount: number;
  course_name?: string | null;
  batch_name?: string | null;
  total_paid: number;
  outstanding_balance: number;
  installments: InstallmentRead[];
}

interface StudentFeeSummary {
  student_id: string;
  student_name: string;
  admission_number: string;
  total_fee: number;
  total_paid: number;
  total_outstanding: number;
  plans: FeePlanRead[];
  next_due_installment: InstallmentRead | null;
}

const STATUS_STYLES: Record<string, string> = {
  PAID: "bg-emerald-50 text-emerald-700 border-emerald-200",
  DUE: "bg-amber-50 text-amber-800 border-amber-200",
  OVERDUE: "bg-red-50 text-[#c22329] border-red-200",
  UPCOMING: "bg-slate-100 text-slate-600 border-slate-200",
};

export default function StudentFeesPage() {
  const router = useRouter();
  const [user, setUser] = useState<AuthUser | null>(null);
  const [summary, setSummary] = useState<StudentFeeSummary | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [payingId, setPayingId] = useState<string | null>(null);
  const [toast, setToast] = useState<{ type: "success" | "error"; text: string } | null>(null);

  const loadSummary = async () => {
    setLoading(true);
    setError(null);
    const res = await authFetch<{ data: StudentFeeSummary }>("/api/v1/finance/my-fees");
    if (res.error) {
      setError(res.error);
    } else if (res.data) {
      setSummary((res.data as any).data ?? (res.data as any));
    }
    setLoading(false);
  };

  useEffect(() => {
    const cu = getCurrentUser();
    if (!cu || (cu.role !== "STUDENT" && cu.role !== "PARENT")) {
      router.push("/login");
      return;
    }
    setUser(cu);
    loadSummary();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const handlePay = async (installmentId: string) => {
    setPayingId(installmentId);
    setToast(null);
    try {
      const payment = await payInstallmentWithRazorpay(installmentId);
      setToast({
        type: "success",
        text: `Payment successful. Receipt #${payment.receipt?.receipt_number ?? payment.id}`,
      });
      await loadSummary();
    } catch (err: any) {
      setToast({ type: "error", text: err?.message || "Payment could not be completed" });
    } finally {
      setPayingId(null);
    }
  };

  return (
    <div className="min-h-screen bg-[#f8fafd] text-slate-900">
      <header className="bg-white border-b border-slate-200/80 px-4 sm:px-6 py-5">
        <div className="max-w-4xl mx-auto flex items-center justify-between">
          <div>
            <div className="flex items-center gap-2 text-xs font-bold text-slate-500 mb-1">
              <Link href="/" className="hover:text-[#c22329]">Home</Link>
              <span>/</span>
              <span className="text-[#c22329]">My Fees</span>
            </div>
            <h1 className="text-xl sm:text-2xl font-black text-slate-900">My Fee Ledger</h1>
          </div>
          {user && (
            <div className="text-right hidden sm:block">
              <div className="text-xs font-bold text-slate-900">{user.first_name} {user.last_name}</div>
              <div className="text-[10px] text-slate-500 uppercase font-bold">{user.role}</div>
            </div>
          )}
        </div>
      </header>

      <main className="max-w-4xl mx-auto px-4 sm:px-6 py-8 space-y-6">
        {toast && (
          <div
            className={`rounded-2xl border px-4 py-3 text-xs font-bold flex items-center gap-2 ${
              toast.type === "success"
                ? "bg-emerald-50 border-emerald-200 text-emerald-800"
                : "bg-red-50 border-red-200 text-[#c22329]"
            }`}
          >
            {toast.type === "success" ? <CheckCircle2 className="w-4 h-4" /> : <AlertTriangle className="w-4 h-4" />}
            <span>{toast.text}</span>
          </div>
        )}

        {loading && (
          <div className="flex items-center justify-center py-20 text-slate-500 gap-2 text-sm font-bold">
            <Loader2 className="w-5 h-5 animate-spin" />
            <span>Loading your fee ledger…</span>
          </div>
        )}

        {!loading && error && (
          <div className="bg-white border border-red-200 rounded-3xl p-6 text-center space-y-2">
            <AlertTriangle className="w-8 h-8 text-[#c22329] mx-auto" />
            <p className="text-sm font-bold text-slate-900">Could not load your fee details</p>
            <p className="text-xs text-slate-500">{error}</p>
          </div>
        )}

        {!loading && summary && (
          <>
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
              <div className="bg-white p-5 rounded-3xl border border-slate-200/90 shadow-sm space-y-1">
                <span className="text-xs font-bold text-slate-500">Total Fee</span>
                <div className="text-2xl font-black text-slate-900">₹{summary.total_fee.toLocaleString("en-IN")}</div>
              </div>
              <div className="bg-white p-5 rounded-3xl border border-slate-200/90 shadow-sm space-y-1">
                <span className="text-xs font-bold text-slate-500">Paid So Far</span>
                <div className="text-2xl font-black text-emerald-700">₹{summary.total_paid.toLocaleString("en-IN")}</div>
              </div>
              <div className="bg-white p-5 rounded-3xl border border-slate-200/90 shadow-sm space-y-1">
                <span className="text-xs font-bold text-slate-500">Outstanding</span>
                <div className="text-2xl font-black text-[#c22329]">₹{summary.total_outstanding.toLocaleString("en-IN")}</div>
              </div>
            </div>

            {summary.plans.length === 0 && (
              <div className="bg-white border border-slate-200 rounded-3xl p-8 text-center text-sm text-slate-500">
                No fee plan has been set up for your enrollment yet. Please contact the office.
              </div>
            )}

            {summary.plans.map((plan) => (
              <div key={plan.id} className="bg-white rounded-3xl border border-slate-200/90 overflow-hidden shadow-sm">
                <div className="p-4 border-b border-slate-100 flex items-center justify-between">
                  <div>
                    <h2 className="text-sm font-bold text-slate-900">
                      {plan.course_name || "Fee Plan"} {plan.batch_name ? `• ${plan.batch_name}` : ""}
                    </h2>
                    <p className="text-xs text-slate-500">
                      Net fee ₹{plan.net_amount.toLocaleString("en-IN")} • Outstanding ₹{plan.outstanding_balance.toLocaleString("en-IN")}
                    </p>
                  </div>
                </div>

                <div className="divide-y divide-slate-100">
                  {plan.installments.map((inst) => (
                    <div key={inst.id} className="p-4 flex flex-col sm:flex-row sm:items-center justify-between gap-3">
                      <div className="flex items-center gap-3">
                        <div className="w-10 h-10 rounded-xl bg-slate-50 border border-slate-200 flex items-center justify-center text-slate-500">
                          {inst.status === "PAID" ? (
                            <CheckCircle2 className="w-4 h-4 text-emerald-600" />
                          ) : (
                            <Clock className="w-4 h-4" />
                          )}
                        </div>
                        <div>
                          <div className="text-sm font-bold text-slate-900">
                            Installment #{inst.installment_number} — ₹{inst.amount.toLocaleString("en-IN")}
                          </div>
                          <div className="text-xs text-slate-500">
                            Due {new Date(inst.due_date).toLocaleDateString("en-IN", { day: "2-digit", month: "short", year: "numeric" })}
                            {inst.status !== "PAID" && ` • Balance ₹${inst.balance_amount.toLocaleString("en-IN")}`}
                          </div>
                        </div>
                      </div>

                      <div className="flex items-center gap-2">
                        <span className={`px-2.5 py-1 rounded-full border text-[10px] font-bold ${STATUS_STYLES[inst.status]}`}>
                          {inst.status}
                        </span>
                        {inst.status !== "PAID" && (
                          <button
                            onClick={() => handlePay(inst.id)}
                            disabled={payingId === inst.id}
                            className="btn-caramel-gold inline-flex items-center gap-1.5 px-4 py-2 rounded-xl text-xs font-bold shadow-md disabled:opacity-60 cursor-pointer"
                          >
                            {payingId === inst.id ? (
                              <Loader2 className="w-3.5 h-3.5 animate-spin" />
                            ) : (
                              <CreditCard className="w-3.5 h-3.5" />
                            )}
                            <span>Pay Now</span>
                          </button>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            ))}

            <div className="flex items-center gap-2 justify-center text-[11px] text-slate-400 font-semibold pt-2">
              <ShieldCheck className="w-3.5 h-3.5" />
              <span>Payments are processed securely via Razorpay. A receipt is generated automatically.</span>
            </div>
          </>
        )}
      </main>
    </div>
  );
}
