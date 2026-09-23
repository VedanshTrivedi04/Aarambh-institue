"use client";

import React, { useState } from "react";
import {
  CreditCard,
  Plus,
  Printer,
  X,
  Loader2,
  Zap,
} from "lucide-react";
import { payInstallmentWithRazorpay } from "@/lib/razorpay";

interface PaymentReceipt {
  id: string;
  receipt_number: string;
  student_name: string;
  class_name: string;
  amount: number;
  payment_mode: "UPI_QR" | "CASH" | "BANK_TRANSFER" | "ONLINE";
  date: string;
  status: "PAID" | "PENDING";
}

export default function AdminFeesPage() {
  const [receipts, setReceipts] = useState<PaymentReceipt[]>([
    {
      id: "rc-1",
      receipt_number: "RCP-2026-084",
      student_name: "Prince Yadav",
      class_name: "Class 12th (Science PCM)",
      amount: 2000,
      payment_mode: "UPI_QR",
      date: "22 Sep 2026",
      status: "PAID",
    },
    {
      id: "rc-2",
      receipt_number: "RCP-2026-083",
      student_name: "Rohit Garg",
      class_name: "Class 10th Board",
      amount: 1000,
      payment_mode: "CASH",
      date: "21 Sep 2026",
      status: "PAID",
    },
    {
      id: "rc-3",
      receipt_number: "RCP-2026-082",
      student_name: "Payal Sharma",
      class_name: "Class 10th Board",
      amount: 1000,
      payment_mode: "UPI_QR",
      date: "20 Sep 2026",
      status: "PAID",
    },
    {
      id: "rc-4",
      receipt_number: "RCP-2026-081",
      student_name: "Dhruvika Solanki",
      class_name: "Class 6th Junior Foundation",
      amount: 800,
      payment_mode: "CASH",
      date: "19 Sep 2026",
      status: "PAID",
    },
    {
      id: "rc-5",
      receipt_number: "RCP-2026-080",
      student_name: "Monika Patidar",
      class_name: "Class 12th PCB",
      amount: 1500,
      payment_mode: "UPI_QR",
      date: "18 Sep 2026",
      status: "PAID",
    },
  ]);

  const [isModalOpen, setIsModalOpen] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [activeReceipt, setActiveReceipt] = useState<PaymentReceipt | null>(null);
  const [payError, setPayError] = useState<string | null>(null);

  const [form, setForm] = useState({
    student_name: "Rohit Garg",
    class_name: "Class 10th",
    amount: "1000",
    payment_mode: "UPI_QR" as "UPI_QR" | "CASH" | "BANK_TRANSFER" | "ONLINE",
    installment_id: "",
  });

  const handleRecordPayment = async (e: React.FormEvent) => {
    e.preventDefault();
    setPayError(null);

    // ONLINE mode collects the payment live via Razorpay Checkout against a
    // real installment — everything else stays as a locally-noted manual entry.
    if (form.payment_mode === "ONLINE") {
      if (!form.installment_id.trim()) {
        setPayError("Enter the installment ID to collect an online payment against.");
        return;
      }
      setSubmitting(true);
      try {
        const payment = await payInstallmentWithRazorpay(form.installment_id.trim());
        const newReceipt: PaymentReceipt = {
          id: payment.id,
          receipt_number: payment.receipt?.receipt_number || payment.id,
          student_name: form.student_name,
          class_name: form.class_name,
          amount: payment.amount,
          payment_mode: "ONLINE",
          date: "Today, Just now",
          status: "PAID",
        };
        setReceipts([newReceipt, ...receipts]);
        setIsModalOpen(false);
      } catch (err: any) {
        setPayError(err?.message || "Online payment could not be completed");
      } finally {
        setSubmitting(false);
      }
      return;
    }

    setSubmitting(true);

    const newReceipt: PaymentReceipt = {
      id: "rc-" + Date.now(),
      receipt_number: `RCP-2026-${String(85 + receipts.length).padStart(3, "0")}`,
      student_name: form.student_name,
      class_name: form.class_name,
      amount: parseFloat(form.amount) || 1000,
      payment_mode: form.payment_mode,
      date: "Today, Just now",
      status: "PAID",
    };

    setReceipts([newReceipt, ...receipts]);
    setSubmitting(false);
    setIsModalOpen(false);
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 text-xs font-bold text-slate-500 mb-1">
            <span>Admin</span>
            <span>/</span>
            <span className="text-[#c22329]">Fees & Billing</span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-black text-slate-900">
            Fee Ledger & Receipts
          </h1>
          <p className="text-xs text-slate-500 mt-0.5">
            Transparent fee collections: Junior batches from ₹800/mo, board & entrance batches, and UPI receipts.
          </p>
        </div>

        <button
          onClick={() => setIsModalOpen(true)}
          className="btn-caramel-gold inline-flex items-center gap-2 px-4 py-2.5 rounded-xl font-bold text-xs shadow-md self-start sm:self-auto cursor-pointer"
        >
          <Plus className="w-4 h-4" />
          <span>+ Record Fee Payment</span>
        </button>
      </div>

      {/* KPI Stats */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <div className="bg-white p-5 rounded-3xl border border-slate-200/90 shadow-sm space-y-2">
          <span className="text-xs font-bold text-slate-500">Total Month Collection</span>
          <div className="text-2xl sm:text-3xl font-black text-emerald-700">
            ₹1,48,600
          </div>
          <p className="text-xs text-slate-500">Across 186 enrolled students</p>
        </div>

        <div className="bg-white p-5 rounded-3xl border border-slate-200/90 shadow-sm space-y-2">
          <span className="text-xs font-bold text-slate-500">Pending Installment Dues</span>
          <div className="text-2xl sm:text-3xl font-black text-amber-700">
            ₹12,400
          </div>
          <p className="text-xs text-slate-500">6 students with partial dues</p>
        </div>

        <div className="bg-white p-5 rounded-3xl border border-slate-200/90 shadow-sm space-y-2">
          <span className="text-xs font-bold text-slate-500">Student-Friendly Base Fee</span>
          <div className="text-2xl sm:text-3xl font-black text-blue-700">
            ₹800 / mo
          </div>
          <p className="text-xs text-slate-500">Class 4th to 8th all-subject foundation</p>
        </div>
      </div>

      {/* Receipts Ledger Table */}
      <div className="bg-white rounded-3xl border border-slate-200/90 overflow-hidden shadow-sm">
        <div className="p-4 border-b border-slate-100 flex items-center justify-between">
          <h2 className="text-sm font-bold text-slate-900">Recent Payment Receipts</h2>
          <span className="text-xs text-slate-500">Showing last 5 receipts</span>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-50 border-b border-slate-200 text-slate-500 uppercase text-[10px] font-extrabold tracking-wider">
              <tr>
                <th className="py-3.5 px-4">Receipt Number</th>
                <th className="py-3.5 px-4">Student & Class</th>
                <th className="py-3.5 px-4">Amount Paid</th>
                <th className="py-3.5 px-4">Payment Mode</th>
                <th className="py-3.5 px-4">Date</th>
                <th className="py-3.5 px-4 text-right">Receipt Print</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 font-medium">
              {receipts.map((rc) => (
                <tr key={rc.id} className="hover:bg-slate-50/70 transition-colors">
                  <td className="py-3.5 px-4 font-mono font-bold text-[#c99a5e]">
                    {rc.receipt_number}
                  </td>
                  <td className="py-3.5 px-4">
                    <div className="font-bold text-slate-900 text-sm">{rc.student_name}</div>
                    <div className="text-[11px] text-slate-500">{rc.class_name}</div>
                  </td>
                  <td className="py-3.5 px-4">
                    <span className="font-mono text-sm font-black text-emerald-700">
                      ₹{rc.amount.toLocaleString("en-IN")}/-
                    </span>
                  </td>
                  <td className="py-3.5 px-4">
                    <span className="px-2 py-0.5 rounded-full bg-slate-100 border border-slate-200 text-[10px] font-bold text-slate-600">
                      {rc.payment_mode}
                    </span>
                  </td>
                  <td className="py-3.5 px-4 text-slate-500">{rc.date}</td>
                  <td className="py-3.5 px-4 text-right">
                    <button
                      onClick={() => setActiveReceipt(rc)}
                      className="inline-flex items-center gap-1.5 text-[11px] font-bold text-slate-700 hover:text-[#c22329] bg-slate-100 hover:bg-red-50 border border-slate-200 px-2.5 py-1.5 rounded-lg transition-colors cursor-pointer"
                    >
                      <Printer className="w-3.5 h-3.5 text-[#c22329]" />
                      <span>Print Slip</span>
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Record Fee Payment Modal */}
      {isModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/40 backdrop-blur-sm animate-in fade-in">
          <div className="bg-white border border-slate-200 rounded-3xl p-6 sm:p-8 max-w-md w-full space-y-5 shadow-2xl relative text-slate-900">
            <div className="flex items-center justify-between border-b border-slate-100 pb-3">
              <div className="flex items-center gap-2">
                <div className="w-8 h-8 rounded-xl bg-emerald-50 text-emerald-700 border border-emerald-200 flex items-center justify-center font-bold">
                  <CreditCard className="w-4 h-4" />
                </div>
                <h3 className="text-lg font-bold text-slate-900">Record Fee Receipt</h3>
              </div>
              <button
                onClick={() => setIsModalOpen(false)}
                className="text-slate-400 hover:text-slate-700 cursor-pointer"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <form onSubmit={handleRecordPayment} className="space-y-4 text-xs">
              <div className="space-y-1">
                <label className="font-bold text-slate-700">Student Name *</label>
                <input
                  type="text"
                  required
                  value={form.student_name}
                  onChange={(e) => setForm({ ...form, student_name: e.target.value })}
                  className="w-full bg-slate-50 border border-slate-200 rounded-xl px-3 py-2 text-slate-900 focus:bg-white focus:outline-none focus:border-[#c22329]"
                />
              </div>

              <div className="space-y-1">
                <label className="font-bold text-slate-700">Class & Course *</label>
                <input
                  type="text"
                  required
                  value={form.class_name}
                  onChange={(e) => setForm({ ...form, class_name: e.target.value })}
                  className="w-full bg-slate-50 border border-slate-200 rounded-xl px-3 py-2 text-slate-900 focus:bg-white focus:outline-none focus:border-[#c22329]"
                />
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div className="space-y-1">
                  <label className="font-bold text-slate-700">Amount (₹) *</label>
                  <input
                    type="number"
                    required
                    disabled={form.payment_mode === "ONLINE"}
                    value={form.amount}
                    onChange={(e) => setForm({ ...form, amount: e.target.value })}
                    className="w-full bg-slate-50 border border-slate-200 rounded-xl px-3 py-2 text-slate-900 font-mono font-bold text-sm focus:bg-white focus:outline-none focus:border-[#c22329] disabled:opacity-50"
                  />
                </div>
                <div className="space-y-1">
                  <label className="font-bold text-slate-700">Payment Mode *</label>
                  <select
                    value={form.payment_mode}
                    onChange={(e) =>
                      setForm({ ...form, payment_mode: e.target.value as any })
                    }
                    className="w-full bg-slate-50 border border-slate-200 rounded-xl px-3 py-2 text-slate-900 focus:bg-white focus:outline-none focus:border-[#c22329]"
                  >
                    <option value="UPI_QR">UPI / QR Code</option>
                    <option value="CASH">Cash Deposit</option>
                    <option value="BANK_TRANSFER">Bank NetBanking</option>
                    <option value="ONLINE">Online (Razorpay Checkout)</option>
                  </select>
                </div>
              </div>

              {form.payment_mode === "ONLINE" && (
                <div className="space-y-1">
                  <label className="font-bold text-slate-700 flex items-center gap-1.5">
                    <Zap className="w-3.5 h-3.5 text-[#c99a5e]" />
                    Installment ID *
                  </label>
                  <input
                    type="text"
                    required
                    placeholder="Paste the installment ID from the student's fee plan"
                    value={form.installment_id}
                    onChange={(e) => setForm({ ...form, installment_id: e.target.value })}
                    className="w-full bg-slate-50 border border-slate-200 rounded-xl px-3 py-2 text-slate-900 font-mono text-[11px] focus:bg-white focus:outline-none focus:border-[#c22329]"
                  />
                  <p className="text-[10px] text-slate-500">
                    The amount is taken from the installment's remaining balance and the Razorpay checkout modal opens on submit.
                  </p>
                </div>
              )}

              {payError && (
                <p className="text-[11px] font-bold text-[#c22329] bg-red-50 border border-red-200 rounded-lg px-3 py-2">
                  {payError}
                </p>
              )}

              <div className="flex justify-end gap-2 pt-2">
                <button
                  type="button"
                  onClick={() => setIsModalOpen(false)}
                  className="px-4 py-2 rounded-xl bg-slate-100 hover:bg-slate-200 text-slate-700 font-bold transition-colors cursor-pointer"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={submitting}
                  className="btn-caramel-gold px-5 py-2 rounded-xl font-bold flex items-center gap-1.5 shadow-md cursor-pointer"
                >
                  {submitting && <Loader2 className="w-3 h-3 animate-spin" />}
                  <span>Generate Receipt</span>
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Printable Receipt Preview Modal */}
      {activeReceipt && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/60 backdrop-blur-sm animate-in fade-in">
          <div className="bg-white text-slate-900 rounded-3xl p-8 max-w-md w-full space-y-6 shadow-2xl relative border border-slate-200">
            {/* Aarambh Receipt Header */}
            <div className="text-center border-b border-slate-100 pb-4">
              <span className="font-black text-xl text-[#c22329]">AARAMBH INSTITUTE</span>
              <p className="text-[11px] text-slate-600 font-semibold mt-1">
                8 Shantinath Puri, Hawa Bangla, Near Sai Mandir, Indore (MP)
              </p>
              <p className="text-[10px] text-slate-500">
                Phone: 88397-14081 | Email: aarambhinstitute09@gmail.com
              </p>
              <div className="inline-block mt-2.5 px-3 py-0.5 rounded-full bg-red-50 text-[#c22329] border border-red-200 font-bold text-xs">
                OFFICIAL FEE RECEIPT
              </div>
            </div>

            <div className="space-y-2 text-xs">
              <div className="flex justify-between py-1 border-b border-slate-100">
                <span className="text-slate-500">Receipt No:</span>
                <span className="font-mono font-bold text-slate-900">{activeReceipt.receipt_number}</span>
              </div>
              <div className="flex justify-between py-1 border-b border-slate-100">
                <span className="text-slate-500">Student Name:</span>
                <span className="font-bold text-slate-900">{activeReceipt.student_name}</span>
              </div>
              <div className="flex justify-between py-1 border-b border-slate-100">
                <span className="text-slate-500">Course / Class:</span>
                <span className="font-medium text-slate-900">{activeReceipt.class_name}</span>
              </div>
              <div className="flex justify-between py-1 border-b border-slate-100">
                <span className="text-slate-500">Payment Mode:</span>
                <span className="font-bold text-slate-800">{activeReceipt.payment_mode}</span>
              </div>
              <div className="flex justify-between py-2 text-sm bg-slate-50 p-2.5 rounded-xl border border-slate-100">
                <span className="font-bold text-slate-700">Amount Received:</span>
                <span className="font-black text-emerald-700">₹{activeReceipt.amount.toLocaleString("en-IN")}/-</span>
              </div>
            </div>

            <div className="text-center text-[10px] text-slate-400 pt-2 border-t border-slate-100">
              Thank you for choosing Aarambh Institute. Step Toward Success!
            </div>

            <div className="flex justify-end gap-2 pt-2">
              <button
                onClick={() => setActiveReceipt(null)}
                className="px-4 py-2 rounded-xl bg-slate-100 hover:bg-slate-200 text-slate-700 text-xs font-bold transition-colors cursor-pointer"
              >
                Close Preview
              </button>
              <button
                onClick={() => window.print()}
                className="btn-caramel-gold px-4 py-2 rounded-xl text-xs font-bold flex items-center gap-1.5 shadow-md cursor-pointer"
              >
                <Printer className="w-3.5 h-3.5" />
                <span>Print Copy</span>
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
