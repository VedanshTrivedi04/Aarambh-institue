"use client";

import React, { useState, useEffect } from "react";
import { authFetch } from "@/lib/auth";
import {
  BookOpen,
  Plus,
  Users,
  Clock,
  X,
  Loader2,
  AlertTriangle,
} from "lucide-react";

interface BatchItem {
  id: string;
  name: string;
  room: string | null;
  start_time: string | null;
  end_time: string | null;
  days: string[] | null;
  capacity: number;
  course_name: string | null;
  teacher_name: string | null;
}

interface Course {
  id: string;
  name: string;
}

interface Subject {
  id: string;
  name: string;
}

interface Teacher {
  id: string;
  first_name: string;
  last_name: string;
}

const DAY_OPTIONS = ["MON", "TUE", "WED", "THU", "FRI", "SAT"];

export default function AdminAcademicPage() {
  const [batches, setBatches] = useState<BatchItem[]>([]);
  const [courses, setCourses] = useState<Course[]>([]);
  const [subjects, setSubjects] = useState<Subject[]>([]);
  const [teachers, setTeachers] = useState<Teacher[]>([]);
  const [loading, setLoading] = useState(true);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const [form, setForm] = useState({
    name: "",
    course_id: "",
    subject_id: "",
    teacher_id: "",
    room: "",
    capacity: "20",
    start_time: "16:00",
    end_time: "17:30",
    days: ["MON", "WED", "FRI"] as string[],
  });

  const courseNameById = new Map(courses.map((c) => [c.id, c.name]));
  const teacherNameById = new Map(teachers.map((t) => [t.id, `${t.first_name} ${t.last_name}`.trim()]));

  const loadBatches = async () => {
    setLoading(true);
    const res = await authFetch<any[]>("/api/v1/admin/academic/batches");
    if (res.error) {
      setError(res.error);
      setLoading(false);
      return;
    }
    setBatches(
      ((res.data as any) || []).map((b: any) => ({
        id: b.id,
        name: b.name,
        room: b.room,
        start_time: b.start_time,
        end_time: b.end_time,
        days: b.days,
        capacity: b.capacity,
        course_name: courseNameById.get(b.course_id) || null,
        teacher_name: b.teacher_id ? teacherNameById.get(b.teacher_id) || null : null,
      }))
    );
    setLoading(false);
  };

  useEffect(() => {
    (async () => {
      const [courseRes, subjectRes, teacherRes] = await Promise.all([
        authFetch<Course[]>("/api/v1/admin/academic/courses"),
        authFetch<Subject[]>("/api/v1/admin/academic/subjects"),
        authFetch<{ items: Teacher[] }>("/api/v1/admin/people/teachers?page_size=100"),
      ]);
      if (courseRes.data) setCourses(courseRes.data as any);
      if (subjectRes.data) setSubjects(subjectRes.data as any);
      if (teacherRes.data) setTeachers((teacherRes.data as any).items || []);
    })();
  }, []);

  useEffect(() => {
    if (courses.length > 0 || teachers.length > 0) loadBatches();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [courses.length, teachers.length]);

  const toggleDay = (day: string) => {
    setForm((f) => ({
      ...f,
      days: f.days.includes(day) ? f.days.filter((d) => d !== day) : [...f.days, day],
    }));
  };

  const handleCreateBatch = async (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitting(true);
    setError(null);

    const res = await authFetch<{ data: any }>("/api/v1/admin/academic/batches", {
      method: "POST",
      body: JSON.stringify({
        course_id: form.course_id,
        subject_id: form.subject_id,
        teacher_id: form.teacher_id || null,
        name: form.name,
        room: form.room || null,
        capacity: Number(form.capacity) || 20,
        start_time: form.start_time,
        end_time: form.end_time,
        days: form.days,
      }),
    });

    setSubmitting(false);

    if (res.error || !res.data) {
      setError(res.error || "Could not create batch");
      return;
    }

    setIsModalOpen(false);
    setForm({
      name: "", course_id: "", subject_id: "", teacher_id: "", room: "",
      capacity: "20", start_time: "16:00", end_time: "17:30", days: ["MON", "WED", "FRI"],
    });
    loadBatches();
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 text-xs font-bold text-slate-500 mb-1">
            <span>Admin</span>
            <span>/</span>
            <span className="text-[#c22329]">Batches & Academics</span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-black text-slate-900">
            Academic Batches & Room Schedule
          </h1>
        </div>

        <button
          onClick={() => setIsModalOpen(true)}
          disabled={courses.length === 0 || subjects.length === 0}
          className="btn-caramel-gold inline-flex items-center gap-2 px-4 py-2.5 rounded-xl font-bold text-xs shadow-md self-start sm:self-auto cursor-pointer disabled:opacity-50"
        >
          <Plus className="w-4 h-4" />
          <span>+ Create New Batch</span>
        </button>
      </div>

      {error && (
        <div className="p-3.5 rounded-2xl bg-red-50 border border-red-200 text-[#c22329] text-xs flex items-center gap-2">
          <AlertTriangle className="w-4 h-4" />
          <span className="font-semibold">{error}</span>
        </div>
      )}

      {/* Batches Grid */}
      {loading ? (
        <div className="flex items-center justify-center py-16 text-slate-500 gap-2 text-sm font-bold">
          <Loader2 className="w-5 h-5 animate-spin" />
          <span>Loading batches…</span>
        </div>
      ) : batches.length === 0 ? (
        <div className="bg-white border border-slate-200 rounded-3xl p-8 text-center text-sm text-slate-500">
          No batches created yet.
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
          {batches.map((b) => (
            <div
              key={b.id}
              className="bg-white p-6 rounded-3xl border border-slate-200/90 shadow-sm flex flex-col justify-between hover:shadow-md transition-all space-y-4"
            >
              <div>
                <div className="flex items-start justify-between">
                  <span className="text-[10px] font-extrabold uppercase px-2.5 py-1 rounded-md bg-blue-50 text-blue-700 border border-blue-200">
                    {b.course_name || "Course"}
                  </span>
                  {b.room && <span className="text-xs font-bold text-slate-500">{b.room}</span>}
                </div>

                <h3 className="text-base font-bold text-slate-900 mt-3 leading-snug">
                  {b.name}
                </h3>

                <div className="mt-4 space-y-2 text-xs text-slate-700 bg-slate-50 p-3.5 rounded-2xl border border-slate-200/80">
                  <div className="flex items-center gap-2">
                    <Clock className="w-3.5 h-3.5 text-[#c99a5e] shrink-0" />
                    <span className="font-medium">
                      {b.days?.join(", ") || "—"} • {b.start_time || "—"} - {b.end_time || "—"}
                    </span>
                  </div>
                  {b.teacher_name && (
                    <div className="flex items-center gap-2">
                      <Users className="w-3.5 h-3.5 text-blue-600 shrink-0" />
                      <span className="truncate font-medium">{b.teacher_name}</span>
                    </div>
                  )}
                </div>
              </div>

              <div className="pt-2 text-xs text-slate-500 font-medium">
                Capacity: <span className="font-bold text-slate-800">{b.capacity} students</span>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Create Batch Modal */}
      {isModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/40 backdrop-blur-sm animate-in fade-in">
          <div className="bg-white border border-slate-200 rounded-3xl p-6 sm:p-8 max-w-lg w-full space-y-5 shadow-2xl relative text-slate-900 max-h-[90vh] overflow-y-auto">
            <div className="flex items-center justify-between border-b border-slate-100 pb-3">
              <div className="flex items-center gap-2">
                <div className="w-8 h-8 rounded-xl bg-red-50 text-[#c22329] border border-red-200 flex items-center justify-center font-bold">
                  <BookOpen className="w-4 h-4" />
                </div>
                <h3 className="text-lg font-bold text-slate-900">Create Batch</h3>
              </div>
              <button
                onClick={() => setIsModalOpen(false)}
                className="text-slate-400 hover:text-slate-700 cursor-pointer"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <form onSubmit={handleCreateBatch} className="space-y-4 text-xs">
              <div className="space-y-1">
                <label className="font-bold text-slate-700">Batch Title *</label>
                <input
                  type="text"
                  required
                  value={form.name}
                  onChange={(e) => setForm({ ...form, name: e.target.value })}
                  placeholder="e.g. 10-CBSE-MATH-A"
                  className="w-full bg-slate-50 border border-slate-200 rounded-xl px-3 py-2 text-slate-900 focus:bg-white focus:outline-none focus:border-[#c22329]"
                />
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div className="space-y-1">
                  <label className="font-bold text-slate-700">Course *</label>
                  <select
                    required
                    value={form.course_id}
                    onChange={(e) => setForm({ ...form, course_id: e.target.value })}
                    className="w-full bg-slate-50 border border-slate-200 rounded-xl px-3 py-2 text-slate-900 focus:bg-white focus:outline-none focus:border-[#c22329]"
                  >
                    <option value="">Select course</option>
                    {courses.map((c) => (
                      <option key={c.id} value={c.id}>{c.name}</option>
                    ))}
                  </select>
                </div>
                <div className="space-y-1">
                  <label className="font-bold text-slate-700">Subject *</label>
                  <select
                    required
                    value={form.subject_id}
                    onChange={(e) => setForm({ ...form, subject_id: e.target.value })}
                    className="w-full bg-slate-50 border border-slate-200 rounded-xl px-3 py-2 text-slate-900 focus:bg-white focus:outline-none focus:border-[#c22329]"
                  >
                    <option value="">Select subject</option>
                    {subjects.map((s) => (
                      <option key={s.id} value={s.id}>{s.name}</option>
                    ))}
                  </select>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div className="space-y-1">
                  <label className="font-bold text-slate-700">Teacher</label>
                  <select
                    value={form.teacher_id}
                    onChange={(e) => setForm({ ...form, teacher_id: e.target.value })}
                    className="w-full bg-slate-50 border border-slate-200 rounded-xl px-3 py-2 text-slate-900 focus:bg-white focus:outline-none focus:border-[#c22329]"
                  >
                    <option value="">Unassigned</option>
                    {teachers.map((t) => (
                      <option key={t.id} value={t.id}>{t.first_name} {t.last_name}</option>
                    ))}
                  </select>
                </div>
                <div className="space-y-1">
                  <label className="font-bold text-slate-700">Classroom</label>
                  <input
                    type="text"
                    value={form.room}
                    onChange={(e) => setForm({ ...form, room: e.target.value })}
                    className="w-full bg-slate-50 border border-slate-200 rounded-xl px-3 py-2 text-slate-900 focus:bg-white focus:outline-none focus:border-[#c22329]"
                  />
                </div>
              </div>

              <div className="grid grid-cols-3 gap-3">
                <div className="space-y-1">
                  <label className="font-bold text-slate-700">Start Time *</label>
                  <input
                    type="time"
                    required
                    value={form.start_time}
                    onChange={(e) => setForm({ ...form, start_time: e.target.value })}
                    className="w-full bg-slate-50 border border-slate-200 rounded-xl px-3 py-2 text-slate-900 focus:bg-white focus:outline-none focus:border-[#c22329]"
                  />
                </div>
                <div className="space-y-1">
                  <label className="font-bold text-slate-700">End Time *</label>
                  <input
                    type="time"
                    required
                    value={form.end_time}
                    onChange={(e) => setForm({ ...form, end_time: e.target.value })}
                    className="w-full bg-slate-50 border border-slate-200 rounded-xl px-3 py-2 text-slate-900 focus:bg-white focus:outline-none focus:border-[#c22329]"
                  />
                </div>
                <div className="space-y-1">
                  <label className="font-bold text-slate-700">Capacity</label>
                  <input
                    type="number"
                    value={form.capacity}
                    onChange={(e) => setForm({ ...form, capacity: e.target.value })}
                    className="w-full bg-slate-50 border border-slate-200 rounded-xl px-3 py-2 text-slate-900 font-mono focus:bg-white focus:outline-none focus:border-[#c22329]"
                  />
                </div>
              </div>

              <div className="space-y-1">
                <label className="font-bold text-slate-700">Days *</label>
                <div className="flex flex-wrap gap-1.5">
                  {DAY_OPTIONS.map((day) => (
                    <button
                      key={day}
                      type="button"
                      onClick={() => toggleDay(day)}
                      className={`px-3 py-1.5 rounded-lg text-[11px] font-bold border cursor-pointer transition-all ${
                        form.days.includes(day)
                          ? "bg-[#c22329] text-white border-[#c22329]"
                          : "bg-slate-50 text-slate-600 border-slate-200 hover:border-slate-300"
                      }`}
                    >
                      {day}
                    </button>
                  ))}
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
                  disabled={submitting || form.days.length === 0}
                  className="btn-caramel-gold px-5 py-2 rounded-xl font-bold flex items-center gap-1.5 shadow-md cursor-pointer disabled:opacity-60"
                >
                  {submitting && <Loader2 className="w-3 h-3 animate-spin" />}
                  <span>Save Batch</span>
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
