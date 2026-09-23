"use client";

import React, { useState } from "react";
import {
  CalendarCheck,
  CheckCircle2,
  XCircle,
  Clock,
  Send,
  AlertCircle,
  FileText,
  User,
  Phone,
  ShieldCheck,
} from "lucide-react";

export default function StudentAttendancePage() {
  const [fromDate, setFromDate] = useState("");
  const [toDate, setToDate] = useState("");
  const [reasonCategory, setReasonCategory] = useState("Medical / Illness");
  const [remarks, setRemarks] = useState("");
  const [parentContact, setParentContact] = useState("8839714081");
  const [submitting, setSubmitting] = useState(false);
  const [submitSuccess, setSubmitSuccess] = useState(false);

  const [leaveHistory, setLeaveHistory] = useState([
    {
      id: "LEV-2026-019",
      dates: "12 Sep 2026",
      days: "1 Day",
      category: "Medical / Illness",
      remarks: "Severe seasonal fever; doctor rest prescribed.",
      status: "APPROVED",
      approvedBy: "Mrs. Shobhna Vyas (Director)",
    },
  ]);

  const recentDays = [
    { date: "22 Sep 2026", day: "Tuesday", status: "PRESENT", inTime: "03:52 PM", lectures: "Physics, Biology, Chemistry", faculty: "Pankaj Dubey verified" },
    { date: "21 Sep 2026", day: "Monday", status: "PRESENT", inTime: "03:55 PM", lectures: "Biology, Chemistry", faculty: "Pankaj Dubey verified" },
    { date: "19 Sep 2026", day: "Saturday", status: "PRESENT", inTime: "03:48 PM", lectures: "Weekly Test & Doubt Clinic", faculty: "Vishal Rathore verified" },
    { date: "18 Sep 2026", day: "Friday", status: "PRESENT", inTime: "03:50 PM", lectures: "Physics, Biology", faculty: "Anita Holkar verified" },
    { date: "17 Sep 2026", day: "Thursday", status: "PRESENT", inTime: "03:55 PM", lectures: "Physics, Chemistry", faculty: "Ansh Sir verified" },
    { date: "16 Sep 2026", day: "Wednesday", status: "PRESENT", inTime: "03:45 PM", lectures: "Biology (2hr Mega Class)", faculty: "Pankaj Dubey verified" },
    { date: "15 Sep 2026", day: "Tuesday", status: "PRESENT", inTime: "03:50 PM", lectures: "Physics, Biology", faculty: "Pankaj Dubey verified" },
    { date: "14 Sep 2026", day: "Monday", status: "PRESENT", inTime: "03:52 PM", lectures: "Chemistry, Biology", faculty: "Ansh Sir verified" },
    { date: "12 Sep 2026", day: "Saturday", status: "EXCUSED_LEAVE", inTime: "--", lectures: "All Classes Missed", faculty: "Medical Leave Approved" },
    { date: "11 Sep 2026", day: "Friday", status: "PRESENT", inTime: "03:49 PM", lectures: "Physics, Biology", faculty: "Anita Holkar verified" },
  ];

  const handleSubmitLeave = (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitting(true);
    setTimeout(() => {
      setSubmitting(false);
      setSubmitSuccess(true);
      const newLeave = {
        id: `LEV-2026-0${leaveHistory.length + 20}`,
        dates: fromDate ? `${fromDate} to ${toDate || fromDate}` : "Upcoming",
        days: "1-2 Days",
        category: reasonCategory,
        remarks: remarks || "Parent authorized leave application.",
        status: "PENDING_APPROVAL",
        approvedBy: "Under Review by Admin Desk",
      };
      setLeaveHistory([newLeave, ...leaveHistory]);
      setRemarks("");
      setTimeout(() => setSubmitSuccess(false), 5000);
    }, 800);
  };

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      {/* Header */}
      <div className="bg-white rounded-3xl border border-slate-200/90 p-6 sm:p-8 shadow-sm">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <div className="flex items-center gap-2 mb-1">
              <span className="text-[10px] font-black uppercase tracking-wider px-2 py-0.5 rounded bg-emerald-50 text-emerald-700 border border-emerald-200">
                Live Attendance Record
              </span>
              <span className="text-[10px] font-bold text-slate-500">
                September 2026 Cycle
              </span>
            </div>
            <h1 className="text-2xl font-black text-slate-900 tracking-tight">
              Attendance & Leave Desk
            </h1>
            <p className="text-xs text-slate-500 mt-1 font-medium">
              Student: <strong className="text-slate-800">Prince Yadav</strong> (Class 12th Bio • Roll 12 • Hawa Bangla Campus)
            </p>
          </div>

          <div className="flex items-center gap-3">
            <div className="text-right">
              <span className="block text-[10px] font-bold text-slate-400 uppercase">
                Attendance Score
              </span>
              <span className="text-2xl font-black text-emerald-600">98.2%</span>
            </div>
            <div className="w-12 h-12 rounded-2xl bg-emerald-50 text-emerald-600 border border-emerald-200 flex items-center justify-center font-bold text-lg">
              <CalendarCheck className="w-6 h-6" />
            </div>
          </div>
        </div>
      </div>

      {/* KPI Stats */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="bg-white rounded-3xl border border-slate-200/90 p-5 shadow-sm">
          <span className="text-xs font-bold text-slate-500 uppercase tracking-wider block">
            Total Lectures Conducted
          </span>
          <div className="text-2xl font-black text-slate-900 mt-1">57 Lectures</div>
          <p className="text-[11px] text-slate-500 mt-1">Class 12th Senior Bio Batch</p>
        </div>

        <div className="bg-white rounded-3xl border border-slate-200/90 p-5 shadow-sm">
          <span className="text-xs font-bold text-emerald-700 uppercase tracking-wider block">
            Lectures Attended
          </span>
          <div className="text-2xl font-black text-emerald-600 mt-1">56 Attended</div>
          <p className="text-[11px] text-emerald-600 font-bold mt-1">98.2% Compliance</p>
        </div>

        <div className="bg-white rounded-3xl border border-slate-200/90 p-5 shadow-sm">
          <span className="text-xs font-bold text-amber-700 uppercase tracking-wider block">
            Authorized Leaves
          </span>
          <div className="text-2xl font-black text-amber-700 mt-1">1 Day</div>
          <p className="text-[11px] text-amber-600 font-medium mt-1">Medical notice approved</p>
        </div>

        <div className="bg-white rounded-3xl border border-slate-200/90 p-5 shadow-sm">
          <span className="text-xs font-bold text-blue-700 uppercase tracking-wider block">
            Late Marks
          </span>
          <div className="text-2xl font-black text-blue-700 mt-1">0 Late</div>
          <p className="text-[11px] text-blue-600 font-bold mt-1">100% On-Time Record</p>
        </div>
      </div>

      {/* 2 Column Layout: Daily Ledger & Leave Form */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Daily Attendance Ledger (2 Cols) */}
        <div className="lg:col-span-2 bg-white rounded-3xl border border-slate-200/90 p-6 shadow-sm space-y-4">
          <div className="flex items-center justify-between pb-3 border-b border-slate-100">
            <div>
              <h2 className="text-base font-black text-slate-900 flex items-center gap-2">
                <CalendarCheck className="w-4 h-4 text-[#c22329]" />
                <span>Daily Roll-Call & Punch Logs</span>
              </h2>
              <p className="text-xs text-slate-500 font-medium mt-0.5">
                Biometric & Faculty Manual Verification Records
              </p>
            </div>
            <span className="text-[10px] font-bold px-2.5 py-1 rounded-full bg-slate-100 text-slate-700">
              Showing Last 10 Sessions
            </span>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs border-collapse">
              <thead>
                <tr className="bg-slate-50 border-b border-slate-200 text-slate-500 uppercase text-[10px] font-extrabold tracking-wider">
                  <th className="py-3 px-4">Date & Day</th>
                  <th className="py-3 px-4">Punch In</th>
                  <th className="py-3 px-4">Lectures Covered</th>
                  <th className="py-3 px-4">Faculty Verified</th>
                  <th className="py-3 px-4 text-right">Status</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 font-medium text-slate-700">
                {recentDays.map((item, idx) => (
                  <tr key={idx} className="hover:bg-slate-50/70 transition-colors">
                    <td className="py-3 px-4 font-bold text-slate-900">
                      <div>{item.date}</div>
                      <div className="text-[10px] text-slate-400 font-normal">{item.day}</div>
                    </td>
                    <td className="py-3 px-4">
                      <span className="font-mono text-slate-600 font-bold">{item.inTime}</span>
                    </td>
                    <td className="py-3 px-4 text-slate-700">{item.lectures}</td>
                    <td className="py-3 px-4 text-[11px] text-slate-500">
                      <span className="inline-flex items-center gap-1 text-emerald-700 font-semibold">
                        <ShieldCheck className="w-3.5 h-3.5" />
                        {item.faculty}
                      </span>
                    </td>
                    <td className="py-3 px-4 text-right">
                      {item.status === "PRESENT" ? (
                        <span className="px-2.5 py-1 rounded-full bg-emerald-50 text-emerald-700 border border-emerald-200 text-[10px] font-black inline-flex items-center gap-1">
                          <CheckCircle2 className="w-3 h-3" />
                          PRESENT
                        </span>
                      ) : (
                        <span className="px-2.5 py-1 rounded-full bg-amber-50 text-amber-800 border border-amber-200 text-[10px] font-black inline-flex items-center gap-1">
                          <AlertCircle className="w-3 h-3" />
                          EXCUSED
                        </span>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* Parent Leave Application Form (1 Col) */}
        <div className="space-y-6">
          <div className="bg-white rounded-3xl border border-slate-200/90 p-6 shadow-sm space-y-4">
            <div>
              <h2 className="text-sm font-black text-slate-900 uppercase tracking-wider flex items-center gap-2">
                <FileText className="w-4 h-4 text-[#c22329]" />
                <span>Submit Leave Application</span>
              </h2>
              <p className="text-xs text-slate-500 font-medium mt-0.5">
                Directly notified to Admin & Batch Head
              </p>
            </div>

            {submitSuccess && (
              <div className="p-3 rounded-2xl bg-emerald-50 border border-emerald-200 text-emerald-800 text-xs flex items-start gap-2">
                <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0 mt-0.5" />
                <span>Leave application submitted successfully. Director will review shortly.</span>
              </div>
            )}

            <form onSubmit={handleSubmitLeave} className="space-y-3.5 text-xs">
              <div className="space-y-1">
                <label className="font-bold text-slate-700">Reason Category</label>
                <select
                  value={reasonCategory}
                  onChange={(e) => setReasonCategory(e.target.value)}
                  className="w-full bg-slate-50 border border-slate-200 rounded-xl px-3 py-2 text-slate-900 font-medium focus:bg-white focus:outline-none focus:border-[#c22329]"
                >
                  <option>Medical / Illness</option>
                  <option>Family Emergency</option>
                  <option>School Examination / Practicals</option>
                  <option>Out of Town Travel</option>
                  <option>Other Pre-Approved Reason</option>
                </select>
              </div>

              <div className="grid grid-cols-2 gap-2">
                <div className="space-y-1">
                  <label className="font-bold text-slate-700">From Date</label>
                  <input
                    type="date"
                    required
                    value={fromDate}
                    onChange={(e) => setFromDate(e.target.value)}
                    className="w-full bg-slate-50 border border-slate-200 rounded-xl px-3 py-2 text-slate-900 font-medium focus:bg-white focus:outline-none focus:border-[#c22329]"
                  />
                </div>
                <div className="space-y-1">
                  <label className="font-bold text-slate-700">To Date</label>
                  <input
                    type="date"
                    required
                    value={toDate}
                    onChange={(e) => setToDate(e.target.value)}
                    className="w-full bg-slate-50 border border-slate-200 rounded-xl px-3 py-2 text-slate-900 font-medium focus:bg-white focus:outline-none focus:border-[#c22329]"
                  />
                </div>
              </div>

              <div className="space-y-1">
                <label className="font-bold text-slate-700">Parent Contact Mobile</label>
                <div className="relative">
                  <Phone className="w-3.5 h-3.5 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
                  <input
                    type="tel"
                    required
                    value={parentContact}
                    onChange={(e) => setParentContact(e.target.value)}
                    className="w-full bg-slate-50 border border-slate-200 rounded-xl pl-9 pr-3 py-2 text-slate-900 font-medium focus:bg-white focus:outline-none focus:border-[#c22329]"
                  />
                </div>
              </div>

              <div className="space-y-1">
                <label className="font-bold text-slate-700">Details / Symptoms / Reason</label>
                <textarea
                  rows={3}
                  required
                  value={remarks}
                  onChange={(e) => setRemarks(e.target.value)}
                  placeholder="State the reason for absence..."
                  className="w-full bg-slate-50 border border-slate-200 rounded-xl p-3 text-slate-900 font-medium focus:bg-white focus:outline-none focus:border-[#c22329]"
                />
              </div>

              <button
                type="submit"
                disabled={submitting}
                className="w-full py-2.5 px-4 rounded-xl font-bold bg-[#c22329] hover:bg-red-700 text-white transition-all shadow-md flex items-center justify-center gap-2 cursor-pointer disabled:opacity-50"
              >
                <Send className="w-3.5 h-3.5" />
                <span>{submitting ? "Submitting..." : "Submit Leave Application"}</span>
              </button>
            </form>
          </div>

          {/* Past Leave Requests History */}
          <div className="bg-white rounded-3xl border border-slate-200/90 p-5 shadow-sm space-y-3">
            <h3 className="text-xs font-black text-slate-900 uppercase tracking-wider">
              Previous Leave Requests
            </h3>
            <div className="space-y-2 text-xs">
              {leaveHistory.map((lh, idx) => (
                <div key={idx} className="p-3 rounded-2xl bg-slate-50 border border-slate-200 space-y-1">
                  <div className="flex items-center justify-between">
                    <span className="font-bold text-slate-900">{lh.dates}</span>
                    <span
                      className={`text-[9px] font-black px-2 py-0.5 rounded-full border ${
                        lh.status === "APPROVED"
                          ? "bg-emerald-50 text-emerald-700 border-emerald-200"
                          : "bg-amber-50 text-amber-700 border-amber-200"
                      }`}
                    >
                      {lh.status}
                    </span>
                  </div>
                  <p className="text-[11px] text-slate-600 font-normal">{lh.remarks}</p>
                  <span className="text-[10px] text-slate-400 font-semibold block pt-0.5">
                    {lh.approvedBy}
                  </span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
