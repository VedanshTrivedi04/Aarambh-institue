"use client";

import React, { useState, useEffect } from "react";
import { authFetch } from "@/lib/auth";
import {
  GraduationCap,
  Search,
  Plus,
  Phone,
  X,
  Loader2,
  AlertTriangle,
  CheckCircle2,
  KeyRound,
} from "lucide-react";

interface StudentItem {
  id: string;
  admission_number: string | null;
  first_name: string;
  last_name: string;
  current_class_id: string | null;
  emergency_contact_name: string | null;
  emergency_contact_phone: string | null;
  is_active: boolean;
}

interface ClassOption {
  id: string;
  name: string;
}

interface Batch {
  id: string;
  name: string;
}

interface WizardResult {
  admission_number: string;
  student_email: string;
  student_temp_password: string | null;
  parent_email: string;
  parent_temp_password: string | null;
}

export default function AdminStudentsPage() {
  const [students, setStudents] = useState<StudentItem[]>([]);
  const [classes, setClasses] = useState<ClassOption[]>([]);
  const [batches, setBatches] = useState<Batch[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState("");
  const [classFilter, setClassFilter] = useState("ALL");
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [wizardResult, setWizardResult] = useState<WizardResult | null>(null);

  const [form, setForm] = useState({
    student_first_name: "",
    student_last_name: "",
    student_email: "",
    class_id: "",
    parent_first_name: "",
    parent_last_name: "",
    parent_email: "",
    parent_phone: "",
    batch_id: "",
  });

  const classNameById = new Map(classes.map((c) => [c.id, c.name]));

  const loadStudents = async () => {
    setLoading(true);
    const res = await authFetch<{ items: StudentItem[] }>("/api/v1/admin/people/students?page=1&page_size=50");
    if (res.data) {
      setStudents((res.data as any).items || []);
    } else if (res.error) {
      setError(res.error);
    }
    setLoading(false);
  };

  useEffect(() => {
    loadStudents();
    authFetch<ClassOption[]>("/api/v1/admin/academic/classes").then((res) => {
      if (res.data) setClasses(res.data as any);
    });
    authFetch<Batch[]>("/api/v1/admin/academic/batches").then((res) => {
      if (res.data) setBatches(res.data as any);
    });
  }, []);

  const handleCreateStudent = async (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitting(true);
    setError(null);

    const res = await authFetch<{ data: WizardResult }>("/api/v1/admin/admissions/wizard", {
      method: "POST",
      body: JSON.stringify({
        student: {
          first_name: form.student_first_name,
          last_name: form.student_last_name,
          email: form.student_email,
          class_id: form.class_id || null,
        },
        parent: {
          first_name: form.parent_first_name,
          last_name: form.parent_last_name,
          email: form.parent_email,
          phone: form.parent_phone,
        },
        enrollment: {
          batch_id: form.batch_id,
        },
      }),
    });

    setSubmitting(false);

    if (res.error || !res.data) {
      setError(res.error || "Could not enroll student");
      return;
    }

    setWizardResult((res.data as any).data as WizardResult);
    setForm({
      student_first_name: "",
      student_last_name: "",
      student_email: "",
      class_id: "",
      parent_first_name: "",
      parent_last_name: "",
      parent_email: "",
      parent_phone: "",
      batch_id: "",
    });
    loadStudents();
  };

  const filtered = students.filter((s) => {
    const fullName = `${s.first_name} ${s.last_name}`.toLowerCase();
    const matchSearch =
      fullName.includes(search.toLowerCase()) ||
      (s.admission_number || "").toLowerCase().includes(search.toLowerCase()) ||
      (s.emergency_contact_phone || "").includes(search);
    const matchClass = classFilter === "ALL" || s.current_class_id === classFilter;
    return matchSearch && matchClass;
  });

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 text-xs font-bold text-slate-500 mb-1">
            <span>Admin</span>
            <span>/</span>
            <span className="text-[#c22329]">Students Directory</span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-black text-slate-900">
            Enrolled Students Register
          </h1>
          <p className="text-xs text-slate-500 mt-0.5">
            Active students across the institute — enrolling here creates the student's login account and links a parent.
          </p>
        </div>

        <button
          onClick={() => setIsModalOpen(true)}
          className="btn-caramel-gold inline-flex items-center gap-2 px-4 py-2.5 rounded-xl font-bold text-xs shadow-md self-start sm:self-auto cursor-pointer"
        >
          <Plus className="w-4 h-4" />
          <span>+ Enroll New Student</span>
        </button>
      </div>

      {error && (
        <div className="p-3.5 rounded-2xl bg-red-50 border border-red-200 text-[#c22329] text-xs flex items-center gap-2">
          <AlertTriangle className="w-4 h-4" />
          <span className="font-semibold">{error}</span>
        </div>
      )}

      {/* Filter & Search Bar */}
      <div className="bg-white p-4 rounded-2xl border border-slate-200 shadow-sm flex flex-col md:flex-row items-center justify-between gap-3">
        <div className="relative w-full md:w-80">
          <Search className="w-4 h-4 text-slate-400 absolute left-3.5 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            placeholder="Search student, admission #, phone..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full bg-slate-50 border border-slate-200 rounded-xl pl-10 pr-4 py-2 text-xs text-slate-900 placeholder-slate-400 focus:outline-none focus:border-[#c22329] focus:bg-white transition-colors"
          />
        </div>

        <div className="flex flex-wrap items-center gap-1.5 w-full md:w-auto">
          <button
            onClick={() => setClassFilter("ALL")}
            className={`px-3 py-1.5 rounded-xl text-[11px] font-bold transition-all cursor-pointer ${
              classFilter === "ALL" ? "bg-[#c22329] text-white shadow-xs" : "bg-slate-100 hover:bg-slate-200/80 text-slate-600"
            }`}
          >
            ALL
          </button>
          {classes.map((c) => (
            <button
              key={c.id}
              onClick={() => setClassFilter(c.id)}
              className={`px-3 py-1.5 rounded-xl text-[11px] font-bold transition-all cursor-pointer ${
                classFilter === c.id ? "bg-[#c22329] text-white shadow-xs" : "bg-slate-100 hover:bg-slate-200/80 text-slate-600"
              }`}
            >
              {c.name}
            </button>
          ))}
        </div>
      </div>

      {/* Students Table */}
      <div className="bg-white rounded-3xl border border-slate-200/90 overflow-hidden shadow-sm">
        {loading ? (
          <div className="flex items-center justify-center py-16 text-slate-500 gap-2 text-sm font-bold">
            <Loader2 className="w-5 h-5 animate-spin" />
            <span>Loading students…</span>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-slate-50 border-b border-slate-200 text-slate-500 uppercase text-[10px] font-extrabold tracking-wider">
                <tr>
                  <th className="py-3.5 px-4">Adm # & Student</th>
                  <th className="py-3.5 px-4">Class</th>
                  <th className="py-3.5 px-4">Guardian Contact</th>
                  <th className="py-3.5 px-4">Status</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 font-medium">
                {filtered.map((s) => (
                  <tr key={s.id} className="hover:bg-slate-50/70 transition-colors">
                    <td className="py-3.5 px-4">
                      <div className="font-mono text-[10px] text-[#c99a5e] font-extrabold">
                        {s.admission_number || "—"}
                      </div>
                      <div className="font-bold text-slate-900 text-sm">
                        {s.first_name} {s.last_name}
                      </div>
                    </td>
                    <td className="py-3.5 px-4">
                      <div className="font-semibold text-slate-800">
                        {s.current_class_id ? classNameById.get(s.current_class_id) || "—" : "—"}
                      </div>
                    </td>
                    <td className="py-3.5 px-4">
                      <div className="text-slate-800 font-medium">{s.emergency_contact_name || "—"}</div>
                      {s.emergency_contact_phone && (
                        <a
                          href={`tel:${s.emergency_contact_phone}`}
                          className="text-slate-600 hover:text-[#c22329] text-[11px] flex items-center gap-1 font-semibold mt-0.5"
                        >
                          <Phone className="w-3 h-3 text-[#c22329]" />
                          <span>{s.emergency_contact_phone}</span>
                        </a>
                      )}
                    </td>
                    <td className="py-3.5 px-4">
                      <span
                        className={`px-2.5 py-0.5 rounded-full text-[10px] font-black uppercase border ${
                          s.is_active
                            ? "bg-emerald-50 text-emerald-700 border-emerald-200"
                            : "bg-slate-100 text-slate-500 border-slate-200"
                        }`}
                      >
                        {s.is_active ? "Active" : "Inactive"}
                      </span>
                    </td>
                  </tr>
                ))}
                {filtered.length === 0 && (
                  <tr>
                    <td colSpan={4} className="py-10 text-center text-slate-500">No students found.</td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Enroll Student Modal */}
      {isModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/40 backdrop-blur-sm animate-in fade-in">
          <div className="bg-white border border-slate-200 rounded-3xl p-6 sm:p-8 max-w-lg w-full space-y-5 shadow-2xl relative text-slate-900 max-h-[90vh] overflow-y-auto">
            <div className="flex items-center justify-between border-b border-slate-100 pb-3">
              <div className="flex items-center gap-2">
                <div className="w-8 h-8 rounded-xl bg-red-50 text-[#c22329] border border-red-200 flex items-center justify-center font-bold">
                  <GraduationCap className="w-4 h-4" />
                </div>
                <h3 className="text-lg font-bold text-slate-900">Enroll New Student</h3>
              </div>
              <button
                onClick={() => setIsModalOpen(false)}
                className="text-slate-400 hover:text-slate-700 cursor-pointer"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <form onSubmit={handleCreateStudent} className="space-y-4 text-xs">
              <p className="text-[11px] font-bold text-slate-500 uppercase tracking-wider">Student Details</p>
              <div className="grid grid-cols-2 gap-3">
                <div className="space-y-1">
                  <label className="font-bold text-slate-700">First Name *</label>
                  <input
                    type="text" required
                    value={form.student_first_name}
                    onChange={(e) => setForm({ ...form, student_first_name: e.target.value })}
                    className="w-full bg-slate-50 border border-slate-200 rounded-xl px-3 py-2 text-slate-900 focus:bg-white focus:outline-none focus:border-[#c22329]"
                  />
                </div>
                <div className="space-y-1">
                  <label className="font-bold text-slate-700">Last Name *</label>
                  <input
                    type="text" required
                    value={form.student_last_name}
                    onChange={(e) => setForm({ ...form, student_last_name: e.target.value })}
                    className="w-full bg-slate-50 border border-slate-200 rounded-xl px-3 py-2 text-slate-900 focus:bg-white focus:outline-none focus:border-[#c22329]"
                  />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div className="space-y-1">
                  <label className="font-bold text-slate-700">Student Email *</label>
                  <input
                    type="email" required
                    value={form.student_email}
                    onChange={(e) => setForm({ ...form, student_email: e.target.value })}
                    className="w-full bg-slate-50 border border-slate-200 rounded-xl px-3 py-2 text-slate-900 focus:bg-white focus:outline-none focus:border-[#c22329]"
                  />
                </div>
                <div className="space-y-1">
                  <label className="font-bold text-slate-700">Class</label>
                  <select
                    value={form.class_id}
                    onChange={(e) => setForm({ ...form, class_id: e.target.value })}
                    className="w-full bg-slate-50 border border-slate-200 rounded-xl px-3 py-2 text-slate-900 focus:bg-white focus:outline-none focus:border-[#c22329]"
                  >
                    <option value="">Select class</option>
                    {classes.map((c) => (
                      <option key={c.id} value={c.id}>{c.name}</option>
                    ))}
                  </select>
                </div>
              </div>

              <p className="text-[11px] font-bold text-slate-500 uppercase tracking-wider pt-2">Parent / Guardian Details</p>
              <div className="grid grid-cols-2 gap-3">
                <div className="space-y-1">
                  <label className="font-bold text-slate-700">First Name *</label>
                  <input
                    type="text" required
                    value={form.parent_first_name}
                    onChange={(e) => setForm({ ...form, parent_first_name: e.target.value })}
                    className="w-full bg-slate-50 border border-slate-200 rounded-xl px-3 py-2 text-slate-900 focus:bg-white focus:outline-none focus:border-[#c22329]"
                  />
                </div>
                <div className="space-y-1">
                  <label className="font-bold text-slate-700">Last Name *</label>
                  <input
                    type="text" required
                    value={form.parent_last_name}
                    onChange={(e) => setForm({ ...form, parent_last_name: e.target.value })}
                    className="w-full bg-slate-50 border border-slate-200 rounded-xl px-3 py-2 text-slate-900 focus:bg-white focus:outline-none focus:border-[#c22329]"
                  />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div className="space-y-1">
                  <label className="font-bold text-slate-700">Parent Email *</label>
                  <input
                    type="email" required
                    value={form.parent_email}
                    onChange={(e) => setForm({ ...form, parent_email: e.target.value })}
                    className="w-full bg-slate-50 border border-slate-200 rounded-xl px-3 py-2 text-slate-900 focus:bg-white focus:outline-none focus:border-[#c22329]"
                  />
                </div>
                <div className="space-y-1">
                  <label className="font-bold text-slate-700">Parent Mobile *</label>
                  <input
                    type="tel" required
                    value={form.parent_phone}
                    onChange={(e) => setForm({ ...form, parent_phone: e.target.value })}
                    className="w-full bg-slate-50 border border-slate-200 rounded-xl px-3 py-2 text-slate-900 focus:bg-white focus:outline-none focus:border-[#c22329]"
                  />
                </div>
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
                  <span>Enroll Student</span>
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Wizard Success — credentials handoff */}
      {wizardResult && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/40 backdrop-blur-sm animate-in fade-in">
          <div className="bg-white border border-slate-200 rounded-3xl p-6 sm:p-8 max-w-md w-full space-y-5 shadow-2xl relative text-slate-900">
            <div className="flex items-center gap-2">
              <CheckCircle2 className="w-6 h-6 text-emerald-600" />
              <h3 className="text-lg font-bold text-slate-900">Student Enrolled</h3>
            </div>
            <p className="text-xs text-slate-500">
              Admission number <strong className="font-mono text-[#c99a5e]">{wizardResult.admission_number}</strong> generated. Share these login credentials securely — they are shown only once.
            </p>

            <div className="space-y-2 text-xs">
              <div className="p-3 rounded-xl bg-slate-50 border border-slate-200 flex items-center justify-between">
                <div>
                  <div className="font-bold text-slate-800">Student Login</div>
                  <div className="text-slate-500">{wizardResult.student_email}</div>
                </div>
                {wizardResult.student_temp_password && (
                  <span className="font-mono font-bold text-[#c22329] flex items-center gap-1">
                    <KeyRound className="w-3 h-3" /> {wizardResult.student_temp_password}
                  </span>
                )}
              </div>
              <div className="p-3 rounded-xl bg-slate-50 border border-slate-200 flex items-center justify-between">
                <div>
                  <div className="font-bold text-slate-800">Parent Login</div>
                  <div className="text-slate-500">{wizardResult.parent_email}</div>
                </div>
                {wizardResult.parent_temp_password && (
                  <span className="font-mono font-bold text-[#c22329] flex items-center gap-1">
                    <KeyRound className="w-3 h-3" /> {wizardResult.parent_temp_password}
                  </span>
                )}
              </div>
            </div>

            <button
              onClick={() => {
                setWizardResult(null);
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
