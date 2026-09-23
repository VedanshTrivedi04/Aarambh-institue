"use client";

import React, { useState, useEffect } from "react";
import { authFetch } from "@/lib/auth";
import {
  Users,
  Search,
  Plus,
  Phone,
  Clock,
  CheckCircle2,
  BookOpen,
  X,
  Loader2,
  AlertTriangle,
  KeyRound,
} from "lucide-react";

interface TeacherItem {
  id: string;
  first_name: string;
  last_name: string;
  employee_code: string | null;
  qualification: string | null;
  experience_years: number | null;
  personal_phone: string | null;
  personal_email: string | null;
  assigned_batches: string[];
}

interface OnboardResult {
  email: string;
  temp_password: string | null;
}

export default function AdminTeachersPage() {
  const [teachers, setTeachers] = useState<TeacherItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState("");
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [onboardResult, setOnboardResult] = useState<OnboardResult | null>(null);

  const [form, setForm] = useState({
    first_name: "",
    last_name: "",
    qualification: "",
    experience_years: "5",
    personal_phone: "",
    email: "",
  });

  const loadTeachers = async () => {
    setLoading(true);
    const res = await authFetch<{ items: any[] }>("/api/v1/admin/people/teachers?page=1&page_size=50");
    if (res.error) {
      setError(res.error);
      setLoading(false);
      return;
    }
    const items = (res.data as any)?.items || [];

    const batchLists = await Promise.all(
      items.map((t: any) => authFetch<any[]>(`/api/v1/admin/academic/batches?teacher_id=${t.id}`))
    );

    setTeachers(
      items.map((t: any, idx: number) => ({
        id: t.id,
        first_name: t.first_name,
        last_name: t.last_name || "",
        employee_code: t.employee_code,
        qualification: t.qualification,
        experience_years: t.experience_years,
        personal_phone: t.personal_phone,
        personal_email: t.personal_email,
        assigned_batches: ((batchLists[idx].data as any) || []).map((b: any) => b.name),
      }))
    );
    setLoading(false);
  };

  useEffect(() => {
    loadTeachers();
  }, []);

  const handleCreateTeacher = async (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitting(true);
    setError(null);

    const res = await authFetch<{ data: OnboardResult }>("/api/v1/admin/people/teachers/onboard", {
      method: "POST",
      body: JSON.stringify({
        first_name: form.first_name,
        last_name: form.last_name,
        email: form.email,
        qualification: form.qualification || null,
        experience_years: form.experience_years ? Number(form.experience_years) : null,
        personal_phone: form.personal_phone || null,
      }),
    });

    setSubmitting(false);

    if (res.error || !res.data) {
      setError(res.error || "Could not onboard teacher");
      return;
    }

    setOnboardResult((res.data as any).data as OnboardResult);
    setForm({ first_name: "", last_name: "", qualification: "", experience_years: "5", personal_phone: "", email: "" });
    loadTeachers();
  };

  const filtered = teachers.filter((t) => {
    const fullName = `${t.first_name} ${t.last_name}`.toLowerCase();
    return (
      fullName.includes(search.toLowerCase()) ||
      (t.qualification || "").toLowerCase().includes(search.toLowerCase()) ||
      (t.employee_code || "").toLowerCase().includes(search.toLowerCase())
    );
  });

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 text-xs font-bold text-slate-500 mb-1">
            <span>Admin</span>
            <span>/</span>
            <span className="text-[#c22329]">Faculty & Staff</span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-black text-slate-900">
            Teaching Faculty Panel
          </h1>
          <p className="text-xs text-slate-500 mt-0.5">
            Adding a faculty member here creates their login account.
          </p>
        </div>

        <button
          onClick={() => setIsModalOpen(true)}
          className="btn-caramel-gold inline-flex items-center gap-2 px-4 py-2.5 rounded-xl font-bold text-xs shadow-md self-start sm:self-auto cursor-pointer"
        >
          <Plus className="w-4 h-4" />
          <span>+ Add Faculty Member</span>
        </button>
      </div>

      {error && (
        <div className="p-3.5 rounded-2xl bg-red-50 border border-red-200 text-[#c22329] text-xs flex items-center gap-2">
          <AlertTriangle className="w-4 h-4" />
          <span className="font-semibold">{error}</span>
        </div>
      )}

      {/* Search Bar */}
      <div className="bg-white p-4 rounded-2xl border border-slate-200 shadow-sm flex items-center justify-between gap-3">
        <div className="relative w-full sm:w-80">
          <Search className="w-4 h-4 text-slate-400 absolute left-3.5 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            placeholder="Search educator by name, subject, code..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full bg-slate-50 border border-slate-200 rounded-xl pl-10 pr-4 py-2 text-xs text-slate-900 placeholder-slate-400 focus:outline-none focus:border-[#c22329] focus:bg-white transition-colors"
          />
        </div>

        <span className="text-xs text-slate-500 font-bold hidden sm:inline">
          Showing {filtered.length} Active Faculty
        </span>
      </div>

      {/* Faculty Cards Grid */}
      {loading ? (
        <div className="flex items-center justify-center py-16 text-slate-500 gap-2 text-sm font-bold">
          <Loader2 className="w-5 h-5 animate-spin" />
          <span>Loading faculty…</span>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
          {filtered.map((t) => (
            <div
              key={t.id}
              className="bg-white p-6 rounded-3xl border border-slate-200/90 shadow-sm hover:shadow-md transition-all space-y-4 flex flex-col justify-between"
            >
              <div>
                <div className="flex items-start justify-between">
                  <div className="flex items-center gap-3">
                    <div className="w-12 h-12 rounded-2xl bg-amber-50 border border-amber-200 flex items-center justify-center font-black text-lg text-[#c99a5e] shadow-xs">
                      {t.first_name[0]}
                      {t.last_name ? t.last_name[0] : ""}
                    </div>
                    <div>
                      <h3 className="text-base font-bold text-slate-900">
                        {t.first_name} {t.last_name}
                      </h3>
                      {t.employee_code && (
                        <span className="text-[10px] font-mono font-bold text-slate-400">
                          {t.employee_code}
                        </span>
                      )}
                    </div>
                  </div>

                  {t.experience_years != null && (
                    <span className="text-[11px] font-bold px-2.5 py-1 rounded-full bg-amber-50 text-amber-800 border border-amber-200 flex items-center gap-1">
                      <Clock className="w-3 h-3 text-[#c99a5e]" />
                      <span>{t.experience_years} Yrs Exp</span>
                    </span>
                  )}
                </div>

                {t.qualification && (
                  <p className="text-xs text-slate-600 mt-3 font-medium">{t.qualification}</p>
                )}

                {/* Assigned Batches */}
                <div className="mt-4 pt-3 border-t border-slate-100 space-y-1.5">
                  <span className="text-[10px] font-extrabold uppercase tracking-wider text-slate-400">
                    Assigned Batches
                  </span>
                  {t.assigned_batches.length === 0 ? (
                    <p className="text-xs text-slate-400">No batches assigned yet</p>
                  ) : (
                    t.assigned_batches.map((b, idx) => (
                      <div
                        key={idx}
                        className="text-xs text-slate-700 flex items-center gap-1.5 font-medium"
                      >
                        <BookOpen className="w-3.5 h-3.5 text-[#c22329] shrink-0" />
                        <span className="truncate">{b}</span>
                      </div>
                    ))
                  )}
                </div>
              </div>

              {/* Bottom Contact Pill */}
              <div className="pt-3 border-t border-slate-100 flex items-center justify-between text-xs text-slate-500">
                {t.personal_phone ? (
                  <a
                    href={`tel:${t.personal_phone}`}
                    className="text-slate-800 hover:text-[#c22329] font-medium flex items-center gap-1 hover:underline"
                  >
                    <Phone className="w-3 h-3 text-[#c22329]" />
                    <span>{t.personal_phone}</span>
                  </a>
                ) : (
                  <span />
                )}

                <span className="text-[10px] text-emerald-700 font-bold bg-emerald-50 px-2 py-0.5 rounded-full border border-emerald-200 flex items-center gap-1">
                  <CheckCircle2 className="w-3 h-3 text-emerald-600" />
                  <span>Active</span>
                </span>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Add Teacher Modal */}
      {isModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/40 backdrop-blur-sm animate-in fade-in">
          <div className="bg-white border border-slate-200 rounded-3xl p-6 sm:p-8 max-w-lg w-full space-y-5 shadow-2xl relative text-slate-900">
            <div className="flex items-center justify-between border-b border-slate-100 pb-3">
              <div className="flex items-center gap-2">
                <div className="w-8 h-8 rounded-xl bg-amber-50 text-[#c99a5e] border border-amber-200 flex items-center justify-center font-bold">
                  <Users className="w-4 h-4" />
                </div>
                <h3 className="text-lg font-bold text-slate-900">Add Teacher Profile</h3>
              </div>
              <button
                onClick={() => setIsModalOpen(false)}
                className="text-slate-400 hover:text-slate-700 cursor-pointer"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <form onSubmit={handleCreateTeacher} className="space-y-4 text-xs">
              <div className="grid grid-cols-2 gap-3">
                <div className="space-y-1">
                  <label className="font-bold text-slate-700">First Name *</label>
                  <input
                    type="text"
                    required
                    value={form.first_name}
                    onChange={(e) => setForm({ ...form, first_name: e.target.value })}
                    className="w-full bg-slate-50 border border-slate-200 rounded-xl px-3 py-2 text-slate-900 focus:bg-white focus:outline-none focus:border-[#c22329]"
                  />
                </div>
                <div className="space-y-1">
                  <label className="font-bold text-slate-700">Last Name *</label>
                  <input
                    type="text"
                    required
                    value={form.last_name}
                    onChange={(e) => setForm({ ...form, last_name: e.target.value })}
                    className="w-full bg-slate-50 border border-slate-200 rounded-xl px-3 py-2 text-slate-900 focus:bg-white focus:outline-none focus:border-[#c22329]"
                  />
                </div>
              </div>

              <div className="space-y-1">
                <label className="font-bold text-slate-700">Login Email *</label>
                <input
                  type="email"
                  required
                  value={form.email}
                  onChange={(e) => setForm({ ...form, email: e.target.value })}
                  className="w-full bg-slate-50 border border-slate-200 rounded-xl px-3 py-2 text-slate-900 focus:bg-white focus:outline-none focus:border-[#c22329]"
                />
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div className="space-y-1">
                  <label className="font-bold text-slate-700">Highest Qualification</label>
                  <input
                    type="text"
                    value={form.qualification}
                    onChange={(e) => setForm({ ...form, qualification: e.target.value })}
                    placeholder="e.g. M.Sc Physics, B.Ed"
                    className="w-full bg-slate-50 border border-slate-200 rounded-xl px-3 py-2 text-slate-900 focus:bg-white focus:outline-none focus:border-[#c22329]"
                  />
                </div>
                <div className="space-y-1">
                  <label className="font-bold text-slate-700">Experience (Years)</label>
                  <input
                    type="number"
                    value={form.experience_years}
                    onChange={(e) => setForm({ ...form, experience_years: e.target.value })}
                    className="w-full bg-slate-50 border border-slate-200 rounded-xl px-3 py-2 text-slate-900 focus:bg-white focus:outline-none focus:border-[#c22329]"
                  />
                </div>
              </div>

              <div className="space-y-1">
                <label className="font-bold text-slate-700">Mobile Number</label>
                <input
                  type="tel"
                  value={form.personal_phone}
                  onChange={(e) => setForm({ ...form, personal_phone: e.target.value })}
                  className="w-full bg-slate-50 border border-slate-200 rounded-xl px-3 py-2 text-slate-900 focus:bg-white focus:outline-none focus:border-[#c22329]"
                />
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
                  <span>Save Faculty</span>
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Onboarding Success — credentials handoff */}
      {onboardResult && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/40 backdrop-blur-sm animate-in fade-in">
          <div className="bg-white border border-slate-200 rounded-3xl p-6 sm:p-8 max-w-sm w-full space-y-5 shadow-2xl relative text-slate-900">
            <div className="flex items-center gap-2">
              <CheckCircle2 className="w-6 h-6 text-emerald-600" />
              <h3 className="text-lg font-bold text-slate-900">Faculty Onboarded</h3>
            </div>
            <p className="text-xs text-slate-500">
              Share this login securely — the password is shown only once.
            </p>
            <div className="p-3 rounded-xl bg-slate-50 border border-slate-200 flex items-center justify-between text-xs">
              <div>
                <div className="font-bold text-slate-800">{onboardResult.email}</div>
              </div>
              {onboardResult.temp_password && (
                <span className="font-mono font-bold text-[#c22329] flex items-center gap-1">
                  <KeyRound className="w-3 h-3" /> {onboardResult.temp_password}
                </span>
              )}
            </div>
            <button
              onClick={() => {
                setOnboardResult(null);
                setIsModalOpen(false);
              }}
              className="btn-caramel-gold w-full px-5 py-2.5 rounded-xl font-bold shadow-md cursor-pointer"
            >
              Done
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
