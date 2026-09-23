"use client";

import React, { useEffect, useState, useCallback } from "react";
import {
  Calendar,
  CheckCircle2,
  Save,
  Loader2,
  AlertTriangle,
} from "lucide-react";
import { authFetch } from "@/lib/auth";

interface Batch {
  id: string;
  name: string;
  start_time: string | null;
  end_time: string | null;
  room: string | null;
}

interface SheetItem {
  enrollment_id: string;
  student_id: string;
  student_name: string;
  admission_number: string | null;
  status: "PRESENT" | "ABSENT" | "LATE" | "EXCUSED" | null;
  remarks: string | null;
}

function todayISO() {
  return new Date().toISOString().slice(0, 10);
}

export default function TeacherAttendancePage() {
  const [date, setDate] = useState(todayISO());
  const [batches, setBatches] = useState<Batch[]>([]);
  const [selectedBatch, setSelectedBatch] = useState<string>("");
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [sheet, setSheet] = useState<SheetItem[]>([]);
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [savedSuccess, setSavedSuccess] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Resolve this teacher's TeacherProfile id, then load only their own batches.
  useEffect(() => {
    (async () => {
      const meRes = await authFetch<{ data: { type: string; profile: { id: string } } }>(
        "/api/v1/me/profile"
      );
      const teacherId = (meRes.data as any)?.data?.profile?.id;
      if (!teacherId) {
        setError("Could not resolve your teacher profile.");
        return;
      }
      const batchRes = await authFetch<Batch[]>(
        `/api/v1/admin/academic/batches?teacher_id=${teacherId}`
      );
      if (batchRes.data) {
        setBatches(batchRes.data as any);
        if ((batchRes.data as any).length > 0) setSelectedBatch((batchRes.data as any)[0].id);
      }
    })();
  }, []);

  const loadRoster = useCallback(async () => {
    if (!selectedBatch) return;
    setLoading(true);
    setError(null);
    setSavedSuccess(false);
    setSheet([]);
    setSessionId(null);

    const listRes = await authFetch<{ items: any[] }>(
      `/api/v1/operations/sessions?batch_id=${selectedBatch}&date_from=${date}&date_to=${date}`
    );
    if (listRes.error) {
      setError(listRes.error);
      setLoading(false);
      return;
    }

    let sid: string | null = (listRes.data as any)?.items?.[0]?.id ?? null;

    if (!sid) {
      const batch = batches.find((b) => b.id === selectedBatch);
      const createRes = await authFetch<{ data: any }>("/api/v1/operations/sessions", {
        method: "POST",
        body: JSON.stringify({
          batch_id: selectedBatch,
          date,
          start_time: batch?.start_time || "16:00",
          end_time: batch?.end_time || "17:00",
          room: batch?.room || null,
        }),
      });
      if (createRes.error || !createRes.data) {
        setError(createRes.error || "Could not schedule a session for this batch/date");
        setLoading(false);
        return;
      }
      sid = (createRes.data as any).data.id;
    }

    setSessionId(sid);

    const sheetRes = await authFetch<SheetItem[]>(`/api/v1/operations/attendance/sessions/${sid}/sheet`);
    if (sheetRes.error) {
      setError(sheetRes.error);
    } else {
      setSheet((sheetRes.data as any) || []);
    }
    setLoading(false);
  }, [selectedBatch, date, batches]);

  useEffect(() => {
    if (selectedBatch && batches.length > 0) loadRoster();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [selectedBatch, date, batches.length]);

  const setStatus = (enrollmentId: string, newStatus: SheetItem["status"]) => {
    setSheet((prev) =>
      prev.map((r) => (r.enrollment_id === enrollmentId ? { ...r, status: newStatus } : r))
    );
    setSavedSuccess(false);
  };

  const markAllPresent = () => {
    setSheet((prev) => prev.map((r) => ({ ...r, status: "PRESENT" })));
    setSavedSuccess(false);
  };

  const handleSave = async () => {
    if (!sessionId) return;
    setSaving(true);
    setError(null);
    const res = await authFetch(`/api/v1/operations/attendance/sessions/${sessionId}/mark`, {
      method: "POST",
      body: JSON.stringify({
        records: sheet.map((r) => ({
          enrollment_id: r.enrollment_id,
          status: r.status || "PRESENT",
          remarks: r.remarks,
        })),
      }),
    });
    setSaving(false);
    if (res.error) {
      setError(res.error);
    } else {
      setSavedSuccess(true);
    }
  };

  const presentCount = sheet.filter((r) => r.status === "PRESENT").length;
  const absentCount = sheet.filter((r) => r.status === "ABSENT").length;
  const lateCount = sheet.filter((r) => r.status === "LATE").length;
  const pct = sheet.length ? Math.round(((presentCount + lateCount) / sheet.length) * 100) : 0;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 text-xs font-bold text-slate-500 mb-1">
            <span>Faculty</span>
            <span>/</span>
            <span className="text-[#c22329]">Daily Attendance</span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-black text-slate-900">
            My Batch Attendance
          </h1>
          <p className="text-xs text-slate-500 mt-0.5">
            Log presence for your own batches — synced directly to the attendance ledger.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={markAllPresent}
            disabled={sheet.length === 0}
            className="px-3.5 py-2 rounded-xl bg-slate-100 hover:bg-slate-200/80 text-xs font-bold text-slate-700 border border-slate-200 transition-colors cursor-pointer disabled:opacity-50"
          >
            Mark All Present
          </button>

          <button
            onClick={handleSave}
            disabled={saving || sheet.length === 0}
            className="btn-caramel-gold inline-flex items-center gap-2 px-5 py-2 rounded-xl font-bold text-xs shadow-md cursor-pointer disabled:opacity-60"
          >
            {saving ? <Loader2 className="w-4 h-4 animate-spin" /> : <Save className="w-4 h-4" />}
            <span>Save Attendance</span>
          </button>
        </div>
      </div>

      {/* Control Bar: Date & Batch Pickers */}
      <div className="bg-white p-5 rounded-3xl border border-slate-200/90 shadow-sm grid grid-cols-1 sm:grid-cols-3 gap-4 items-center">
        <div className="space-y-1">
          <label className="text-xs font-bold text-slate-700">Date of Attendance</label>
          <div className="relative">
            <Calendar className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
            <input
              type="date"
              value={date}
              onChange={(e) => setDate(e.target.value)}
              className="w-full bg-slate-50 border border-slate-200 rounded-xl pl-9 pr-3 py-2 text-xs text-slate-900 focus:bg-white focus:outline-none focus:border-[#c22329]"
            />
          </div>
        </div>

        <div className="space-y-1">
          <label className="text-xs font-bold text-slate-700">My Batch</label>
          <select
            value={selectedBatch}
            onChange={(e) => setSelectedBatch(e.target.value)}
            className="w-full bg-slate-50 border border-slate-200 rounded-xl px-3 py-2 text-xs text-slate-900 focus:bg-white focus:outline-none focus:border-[#c22329]"
          >
            {batches.length === 0 && <option value="">No batches assigned to you</option>}
            {batches.map((b) => (
              <option key={b.id} value={b.id}>
                {b.name} {b.start_time ? `(${b.start_time})` : ""}
              </option>
            ))}
          </select>
        </div>

        <div className="flex items-center justify-between sm:justify-end gap-3 pt-4 sm:pt-0">
          <div className="text-right">
            <span className="block text-[11px] text-slate-500 font-medium">Batch Attendance</span>
            <span className="text-xl font-black text-emerald-700">{pct}%</span>
          </div>
          <div className="flex gap-1.5 text-[10px] font-bold">
            <span className="px-2 py-1 rounded-lg bg-emerald-50 text-emerald-700 border border-emerald-200">
              {presentCount} P
            </span>
            <span className="px-2 py-1 rounded-lg bg-red-50 text-[#c22329] border border-red-200">
              {absentCount} A
            </span>
            <span className="px-2 py-1 rounded-lg bg-amber-50 text-amber-800 border border-amber-200">
              {lateCount} L
            </span>
          </div>
        </div>
      </div>

      {error && (
        <div className="p-3.5 rounded-2xl bg-red-50 border border-red-200 text-[#c22329] text-xs flex items-center gap-2">
          <AlertTriangle className="w-4 h-4" />
          <span className="font-semibold">{error}</span>
        </div>
      )}

      {savedSuccess && (
        <div className="p-3.5 rounded-2xl bg-emerald-50 border border-emerald-200 text-emerald-800 text-xs flex items-center gap-2 animate-in fade-in">
          <CheckCircle2 className="w-4 h-4 text-emerald-600" />
          <span className="font-semibold">Attendance saved successfully.</span>
        </div>
      )}

      {/* Attendance Sheet Table */}
      <div className="bg-white rounded-3xl border border-slate-200/90 overflow-hidden shadow-sm">
        {loading ? (
          <div className="flex items-center justify-center py-16 text-slate-500 gap-2 text-sm font-bold">
            <Loader2 className="w-5 h-5 animate-spin" />
            <span>Loading roster…</span>
          </div>
        ) : sheet.length === 0 ? (
          <div className="py-16 text-center text-sm text-slate-500">
            No enrolled students found for this batch.
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-slate-50 border-b border-slate-200 text-slate-500 uppercase text-[10px] font-extrabold tracking-wider">
                <tr>
                  <th className="py-3.5 px-4">Admission #</th>
                  <th className="py-3.5 px-4">Student Name</th>
                  <th className="py-3.5 px-4">Attendance Status</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 font-medium">
                {sheet.map((r) => (
                  <tr key={r.enrollment_id} className="hover:bg-slate-50/70 transition-colors">
                    <td className="py-3.5 px-4 font-mono text-[11px] text-[#c99a5e] font-extrabold">
                      {r.admission_number || "—"}
                    </td>
                    <td className="py-3.5 px-4">
                      <span className="font-bold text-slate-900 text-sm">{r.student_name}</span>
                    </td>
                    <td className="py-3.5 px-4">
                      <div className="inline-flex items-center p-1 rounded-xl bg-slate-100 border border-slate-200 gap-1">
                        <button
                          type="button"
                          onClick={() => setStatus(r.enrollment_id, "PRESENT")}
                          className={`px-3 py-1 rounded-lg text-xs font-bold transition-all cursor-pointer ${
                            (r.status || "PRESENT") === "PRESENT"
                              ? "bg-emerald-600 text-white shadow-xs"
                              : "text-slate-600 hover:text-slate-900"
                          }`}
                        >
                          Present
                        </button>
                        <button
                          type="button"
                          onClick={() => setStatus(r.enrollment_id, "LATE")}
                          className={`px-3 py-1 rounded-lg text-xs font-bold transition-all cursor-pointer ${
                            r.status === "LATE"
                              ? "bg-amber-600 text-white shadow-xs"
                              : "text-slate-600 hover:text-slate-900"
                          }`}
                        >
                          Late
                        </button>
                        <button
                          type="button"
                          onClick={() => setStatus(r.enrollment_id, "ABSENT")}
                          className={`px-3 py-1 rounded-lg text-xs font-bold transition-all cursor-pointer ${
                            r.status === "ABSENT"
                              ? "bg-[#c22329] text-white shadow-xs"
                              : "text-slate-600 hover:text-slate-900"
                          }`}
                        >
                          Absent
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
