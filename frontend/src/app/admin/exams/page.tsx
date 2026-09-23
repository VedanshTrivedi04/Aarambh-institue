"use client";

import React, { useEffect, useState, useCallback } from "react";
import {
  Award,
  Plus,
  Trophy,
  X,
  Loader2,
  AlertTriangle,
  CheckCircle2,
} from "lucide-react";
import { authFetch } from "@/lib/auth";

interface Batch {
  id: string;
  name: string;
}

interface TestRead {
  id: string;
  name: string;
  batch_id: string | null;
  batch_name: string | null;
  subject_name: string | null;
  date: string;
  max_marks: number;
  passing_marks: number | null;
  status: string;
  evaluated_count: number;
}

interface ResultRow {
  student_id: string;
  student_name: string;
  admission_number: string | null;
  marks_obtained: number | null;
  is_absent: boolean;
  percentage: number | null;
  rank: number | null;
}

export default function AdminExamsPage() {
  const [batches, setBatches] = useState<Batch[]>([]);
  const [tests, setTests] = useState<TestRead[]>([]);
  const [selectedTestId, setSelectedTestId] = useState<string | null>(null);
  const [roster, setRoster] = useState<ResultRow[]>([]);
  const [loadingTests, setLoadingTests] = useState(false);
  const [loadingRoster, setLoadingRoster] = useState(false);
  const [saving, setSaving] = useState(false);
  const [saved, setSaved] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const [isModalOpen, setIsModalOpen] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [form, setForm] = useState({
    name: "",
    batch_id: "",
    date: new Date().toISOString().slice(0, 10),
    max_marks: "100",
    passing_marks: "35",
  });

  const selectedTest = tests.find((t) => t.id === selectedTestId) || null;

  const loadTests = useCallback(async () => {
    setLoadingTests(true);
    const res = await authFetch<{ items: TestRead[] }>("/api/v1/examination/tests?page_size=50");
    if (res.data) {
      const items = (res.data as any).items as TestRead[];
      setTests(items);
      if (items.length > 0 && !selectedTestId) setSelectedTestId(items[0].id);
    } else if (res.error) {
      setError(res.error);
    }
    setLoadingTests(false);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  useEffect(() => {
    authFetch<Batch[]>("/api/v1/admin/academic/batches").then((res) => {
      if (res.data) setBatches(res.data as any);
    });
    loadTests();
  }, [loadTests]);

  const loadRoster = useCallback(async (test: TestRead) => {
    if (!test.batch_id) {
      setRoster([]);
      return;
    }
    setLoadingRoster(true);
    setError(null);
    setSaved(false);

    const [enrollRes, resultsRes] = await Promise.all([
      authFetch<{ items: any[] }>(`/api/v1/admin/enrollments?batch_id=${test.batch_id}&status=ACTIVE&page_size=100`),
      authFetch<{ data: ResultRow[] }>(`/api/v1/examination/tests/${test.id}/results`),
    ]);

    if (enrollRes.error) {
      setError(enrollRes.error);
      setLoadingRoster(false);
      return;
    }

    const enrollments = (enrollRes.data as any)?.items || [];
    const existingResults: ResultRow[] = ((resultsRes.data as any)?.data || []) as ResultRow[];
    const resultByStudent = new Map(existingResults.map((r) => [r.student_id, r]));

    const profiles = await Promise.all(
      enrollments.map((e: any) => authFetch<{ data: any }>(`/api/v1/admin/people/students/${e.student_id}`))
    );

    const rows: ResultRow[] = enrollments.map((e: any, idx: number) => {
      const profile = (profiles[idx].data as any)?.data;
      const existing = resultByStudent.get(e.student_id);
      return {
        student_id: e.student_id,
        student_name: profile ? `${profile.first_name} ${profile.last_name || ""}`.trim() : e.student_id,
        admission_number: profile?.admission_number || null,
        marks_obtained: existing?.marks_obtained ?? null,
        is_absent: existing?.is_absent ?? false,
        percentage: existing?.percentage ?? null,
        rank: existing?.rank ?? null,
      };
    });

    setRoster(rows);
    setLoadingRoster(false);
  }, []);

  useEffect(() => {
    if (selectedTest) loadRoster(selectedTest);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [selectedTestId]);

  const setMarks = (studentId: string, marks: string) => {
    setRoster((prev) =>
      prev.map((r) =>
        r.student_id === studentId
          ? { ...r, marks_obtained: marks === "" ? null : Number(marks), is_absent: false }
          : r
      )
    );
    setSaved(false);
  };

  const toggleAbsent = (studentId: string) => {
    setRoster((prev) =>
      prev.map((r) =>
        r.student_id === studentId ? { ...r, is_absent: !r.is_absent, marks_obtained: null } : r
      )
    );
    setSaved(false);
  };

  const handleSaveMarks = async () => {
    if (!selectedTest) return;
    setSaving(true);
    setError(null);
    const res = await authFetch<{ data: ResultRow[] }>(`/api/v1/examination/tests/${selectedTest.id}/marks`, {
      method: "POST",
      body: JSON.stringify({
        entries: roster.map((r) => ({
          student_id: r.student_id,
          marks_obtained: r.is_absent ? null : r.marks_obtained,
          is_absent: r.is_absent,
        })),
      }),
    });
    setSaving(false);
    if (res.error) {
      setError(res.error);
      return;
    }
    const updated = (res.data as any)?.data as ResultRow[];
    if (updated) {
      setRoster((prev) =>
        prev.map((r) => {
          const u = updated.find((x) => x.student_id === r.student_id);
          return u ? { ...r, percentage: u.percentage, rank: u.rank } : r;
        })
      );
    }
    setSaved(true);
    loadTests();
  };

  const handleCreateTest = async (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitting(true);
    setError(null);
    const res = await authFetch<{ data: TestRead }>("/api/v1/examination/tests", {
      method: "POST",
      body: JSON.stringify({
        name: form.name,
        batch_id: form.batch_id || null,
        date: form.date,
        max_marks: Number(form.max_marks) || 100,
        passing_marks: form.passing_marks ? Number(form.passing_marks) : null,
      }),
    });
    setSubmitting(false);
    if (res.error) {
      setError(res.error);
      return;
    }
    const created = (res.data as any)?.data as TestRead;
    setTests([created, ...tests]);
    setSelectedTestId(created.id);
    setIsModalOpen(false);
    setForm({ name: "", batch_id: "", date: new Date().toISOString().slice(0, 10), max_marks: "100", passing_marks: "35" });
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 text-xs font-bold text-slate-500 mb-1">
            <span>Admin</span>
            <span>/</span>
            <span className="text-[#c22329]">Exams & Results</span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-black text-slate-900">
            Examinations & Marks Ledger
          </h1>
          <p className="text-xs text-slate-500 mt-0.5">
            Schedule tests and enter marks — ranks and percentiles are computed automatically on save.
          </p>
        </div>

        <button
          onClick={() => setIsModalOpen(true)}
          className="btn-caramel-gold inline-flex items-center gap-2 px-4 py-2.5 rounded-xl font-bold text-xs shadow-md self-start sm:self-auto cursor-pointer"
        >
          <Plus className="w-4 h-4" />
          <span>+ Schedule Test</span>
        </button>
      </div>

      {error && (
        <div className="p-3.5 rounded-2xl bg-red-50 border border-red-200 text-[#c22329] text-xs flex items-center gap-2">
          <AlertTriangle className="w-4 h-4" />
          <span className="font-semibold">{error}</span>
        </div>
      )}

      {/* Tests Selector Cards */}
      {loadingTests ? (
        <div className="flex items-center justify-center py-10 text-slate-500 gap-2 text-sm font-bold">
          <Loader2 className="w-5 h-5 animate-spin" />
          <span>Loading tests…</span>
        </div>
      ) : tests.length === 0 ? (
        <div className="bg-white border border-slate-200 rounded-3xl p-8 text-center text-sm text-slate-500">
          No tests scheduled yet. Click "+ Schedule Test" to create one.
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {tests.map((t) => {
            const isSelected = selectedTestId === t.id;
            return (
              <button
                key={t.id}
                onClick={() => setSelectedTestId(t.id)}
                className={`p-5 rounded-3xl border text-left transition-all space-y-3 cursor-pointer ${
                  isSelected
                    ? "bg-white border-[#c22329] ring-2 ring-red-500/15 shadow-md"
                    : "bg-white border-slate-200/90 hover:border-slate-300 shadow-sm"
                }`}
              >
                <div className="flex items-center justify-between">
                  <span className="text-[10px] font-black uppercase px-2.5 py-0.5 rounded-md bg-red-50 text-[#c22329] border border-red-200">
                    {t.batch_name || "Unassigned"}
                  </span>
                  <span className="text-xs font-bold text-slate-500">{t.date}</span>
                </div>

                <h3 className="font-bold text-sm text-slate-900 leading-snug">{t.name}</h3>

                <div className="pt-2 border-t border-slate-100 flex items-center justify-between text-xs">
                  <span className="text-slate-500">Max Marks: {t.max_marks}</span>
                  <span className="text-[#c99a5e] font-extrabold">{t.evaluated_count} evaluated</span>
                </div>
              </button>
            );
          })}
        </div>
      )}

      {/* Marks Sheet for Selected Test */}
      {selectedTest && (
        <div className="bg-white rounded-3xl border border-slate-200/90 overflow-hidden shadow-sm space-y-4 p-6">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-slate-100 pb-4">
            <div>
              <span className="text-[10px] font-extrabold text-[#c99a5e] uppercase tracking-wider">
                Evaluating Test Sheet
              </span>
              <h2 className="text-lg font-bold text-slate-900 mt-0.5">{selectedTest.name}</h2>
              <p className="text-xs text-slate-500">
                {selectedTest.batch_name || "Unassigned batch"} • Conducted on {selectedTest.date} • Max {selectedTest.max_marks}
              </p>
            </div>

            <button
              onClick={handleSaveMarks}
              disabled={saving || roster.length === 0}
              className="btn-caramel-gold inline-flex items-center gap-2 px-5 py-2 rounded-xl font-bold text-xs shadow-md cursor-pointer disabled:opacity-60"
            >
              {saving ? <Loader2 className="w-4 h-4 animate-spin" /> : <Award className="w-4 h-4" />}
              <span>Save Marks Ledger</span>
            </button>
          </div>

          {saved && (
            <div className="p-3 rounded-2xl bg-emerald-50 border border-emerald-200 text-emerald-800 text-xs flex items-center gap-2">
              <CheckCircle2 className="w-4 h-4 text-emerald-600" />
              <span className="font-semibold">Marks saved — ranks and percentiles recomputed.</span>
            </div>
          )}

          {loadingRoster ? (
            <div className="flex items-center justify-center py-10 text-slate-500 gap-2 text-sm font-bold">
              <Loader2 className="w-5 h-5 animate-spin" />
              <span>Loading roster…</span>
            </div>
          ) : roster.length === 0 ? (
            <div className="py-10 text-center text-sm text-slate-500">
              No enrolled students found for this test's batch.
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs">
                <thead className="bg-slate-50 border-b border-slate-200 text-slate-500 uppercase text-[10px] font-extrabold tracking-wider">
                  <tr>
                    <th className="py-3 px-3">Student Name</th>
                    <th className="py-3 px-3">Marks Obtained</th>
                    <th className="py-3 px-3">Percentage</th>
                    <th className="py-3 px-3">Absent</th>
                    <th className="py-3 px-3 text-right">Rank</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100 font-medium">
                  {roster.map((r) => (
                    <tr key={r.student_id} className="hover:bg-slate-50/70 transition-colors">
                      <td className="py-3 px-3">
                        <span className="font-bold text-slate-900 text-sm">{r.student_name}</span>
                        {r.admission_number && (
                          <span className="block text-[10px] text-slate-400 font-mono">{r.admission_number}</span>
                        )}
                      </td>
                      <td className="py-3 px-3">
                        <input
                          type="number"
                          min={0}
                          max={selectedTest.max_marks}
                          disabled={r.is_absent}
                          value={r.marks_obtained ?? ""}
                          onChange={(e) => setMarks(r.student_id, e.target.value)}
                          className="w-20 bg-slate-50 border border-slate-200 rounded-lg px-2 py-1 font-mono font-bold text-slate-900 focus:bg-white focus:outline-none focus:border-[#c22329] disabled:opacity-50"
                        />
                        <span className="text-slate-400 ml-1">/ {selectedTest.max_marks}</span>
                      </td>
                      <td className="py-3 px-3">
                        {r.percentage != null ? (
                          <span className="font-bold text-slate-700">{r.percentage.toFixed(1)}%</span>
                        ) : (
                          <span className="text-slate-300">—</span>
                        )}
                      </td>
                      <td className="py-3 px-3">
                        <input
                          type="checkbox"
                          checked={r.is_absent}
                          onChange={() => toggleAbsent(r.student_id)}
                          className="w-4 h-4 accent-[#c22329] cursor-pointer"
                        />
                      </td>
                      <td className="py-3 px-3 text-right">
                        {r.rank ? (
                          <span className="px-3 py-1 rounded-full bg-amber-50 text-amber-800 border border-amber-200 font-black text-xs inline-flex items-center gap-1 shadow-xs">
                            <Trophy className="w-3.5 h-3.5 text-[#c99a5e]" />
                            <span>Rank {r.rank}</span>
                          </span>
                        ) : (
                          <span className="text-slate-400 text-xs font-medium">—</span>
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      )}

      {/* Schedule Test Modal */}
      {isModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/40 backdrop-blur-sm animate-in fade-in">
          <div className="bg-white border border-slate-200 rounded-3xl p-6 sm:p-8 max-w-lg w-full space-y-5 shadow-2xl relative text-slate-900">
            <div className="flex items-center justify-between border-b border-slate-100 pb-3">
              <div className="flex items-center gap-2">
                <div className="w-8 h-8 rounded-xl bg-red-50 text-[#c22329] border border-red-200 flex items-center justify-center font-bold">
                  <Award className="w-4 h-4" />
                </div>
                <h3 className="text-lg font-bold text-slate-900">Schedule Test</h3>
              </div>
              <button
                onClick={() => setIsModalOpen(false)}
                className="text-slate-400 hover:text-slate-700 cursor-pointer"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <form onSubmit={handleCreateTest} className="space-y-4 text-xs">
              <div className="space-y-1">
                <label className="font-bold text-slate-700">Test Title *</label>
                <input
                  type="text"
                  required
                  value={form.name}
                  onChange={(e) => setForm({ ...form, name: e.target.value })}
                  placeholder="e.g. Weekly Board Model Test #3"
                  className="w-full bg-slate-50 border border-slate-200 rounded-xl px-3 py-2 text-slate-900 focus:bg-white focus:outline-none focus:border-[#c22329]"
                />
              </div>

              <div className="space-y-1">
                <label className="font-bold text-slate-700">Batch *</label>
                <select
                  required
                  value={form.batch_id}
                  onChange={(e) => setForm({ ...form, batch_id: e.target.value })}
                  className="w-full bg-slate-50 border border-slate-200 rounded-xl px-3 py-2 text-slate-900 focus:bg-white focus:outline-none focus:border-[#c22329]"
                >
                  <option value="">Select a batch</option>
                  {batches.map((b) => (
                    <option key={b.id} value={b.id}>{b.name}</option>
                  ))}
                </select>
              </div>

              <div className="grid grid-cols-3 gap-3">
                <div className="space-y-1">
                  <label className="font-bold text-slate-700">Date *</label>
                  <input
                    type="date"
                    required
                    value={form.date}
                    onChange={(e) => setForm({ ...form, date: e.target.value })}
                    className="w-full bg-slate-50 border border-slate-200 rounded-xl px-3 py-2 text-slate-900 focus:bg-white focus:outline-none focus:border-[#c22329]"
                  />
                </div>
                <div className="space-y-1">
                  <label className="font-bold text-slate-700">Max Marks *</label>
                  <input
                    type="number"
                    required
                    value={form.max_marks}
                    onChange={(e) => setForm({ ...form, max_marks: e.target.value })}
                    className="w-full bg-slate-50 border border-slate-200 rounded-xl px-3 py-2 text-slate-900 font-mono focus:bg-white focus:outline-none focus:border-[#c22329]"
                  />
                </div>
                <div className="space-y-1">
                  <label className="font-bold text-slate-700">Passing Marks</label>
                  <input
                    type="number"
                    value={form.passing_marks}
                    onChange={(e) => setForm({ ...form, passing_marks: e.target.value })}
                    className="w-full bg-slate-50 border border-slate-200 rounded-xl px-3 py-2 text-slate-900 font-mono focus:bg-white focus:outline-none focus:border-[#c22329]"
                  />
                </div>
              </div>

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
                  <span>Schedule Test</span>
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
