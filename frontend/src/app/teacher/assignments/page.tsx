"use client";

import React, { useState } from "react";
import {
  FileText,
  Plus,
  Calendar,
  CheckCircle2,
  Clock,
  Download,
  X,
  Loader2,
  Users,
  Award,
} from "lucide-react";

interface AssignmentItem {
  id: string;
  title: string;
  batch_name: string;
  chapter: string;
  due_date: string;
  total_marks: number;
  submitted_count: number;
  total_count: number;
  status: "ACTIVE" | "EVALUATED";
}

export default function TeacherAssignmentsPage() {
  const [assignments, setAssignments] = useState<AssignmentItem[]>([
    {
      id: "a1",
      title: "DPP #14: Cardiac Cycle & Electrocardiogram (ECG) Interpretation",
      batch_name: "Class 12th Senior Biology",
      chapter: "Chapter 18: Body Fluids & Circulation",
      due_date: "23 Sep 2026",
      total_marks: 25,
      submitted_count: 18,
      total_count: 19,
      status: "ACTIVE",
    },
    {
      id: "a2",
      title: "NEET Special Problem Set: Chromosomal Linkage & Recombination Frequency",
      batch_name: "NEET Medical Specialist Batch",
      chapter: "Principles of Inheritance & Variation",
      due_date: "24 Sep 2026",
      total_marks: 40,
      submitted_count: 20,
      total_count: 20,
      status: "EVALUATED",
    },
    {
      id: "a3",
      title: "Board Numerical Practice: Blood Pressure Regulation & Cardiac Output",
      batch_name: "Class 12th Senior Biology",
      chapter: "Chapter 18: Circulation",
      due_date: "26 Sep 2026",
      total_marks: 20,
      submitted_count: 12,
      total_count: 19,
      status: "ACTIVE",
    },
    {
      id: "a4",
      title: "Class 11th Assignment: Plant Cell Anatomy & Organelles Drawing Sheet",
      batch_name: "Class 11th Senior Biology",
      chapter: "Chapter 8: Cell The Unit of Life",
      due_date: "27 Sep 2026",
      total_marks: 15,
      submitted_count: 15,
      total_count: 18,
      status: "ACTIVE",
    },
  ]);

  const [isModalOpen, setIsModalOpen] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [filterBatch, setFilterBatch] = useState("ALL");

  const [form, setForm] = useState({
    title: "",
    batch_name: "Class 12th Senior Biology",
    chapter: "Chapter 19: Excretory Products & Elimination",
    due_date: "2026-09-28",
    total_marks: "25",
  });

  const handleCreateAssignment = (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitting(true);

    const newA: AssignmentItem = {
      id: "as-" + Date.now(),
      title: form.title,
      batch_name: form.batch_name,
      chapter: form.chapter,
      due_date: form.due_date,
      total_marks: parseInt(form.total_marks) || 25,
      submitted_count: 0,
      total_count: form.batch_name.includes("NEET") ? 20 : 19,
      status: "ACTIVE",
    };

    setAssignments([newA, ...assignments]);
    setSubmitting(false);
    setIsModalOpen(false);
  };

  const filtered = assignments.filter((a) => {
    if (filterBatch === "ALL") return true;
    return a.batch_name === filterBatch;
  });

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 text-xs font-bold text-slate-500 mb-1">
            <span>Faculty</span>
            <span>/</span>
            <span className="text-[#c22329]">Assignments & Homework</span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-black text-slate-900">
            Daily Practice Problems & Homework
          </h1>
          <p className="text-xs text-slate-500 mt-0.5">
            Issue curriculum-aligned DPPs, track student submission rates, and grade board diagram questions.
          </p>
        </div>

        <button
          onClick={() => setIsModalOpen(true)}
          className="btn-caramel-gold inline-flex items-center gap-2 px-4 py-2.5 rounded-xl font-bold text-xs shadow-md self-start sm:self-auto cursor-pointer"
        >
          <Plus className="w-4 h-4" />
          <span>+ Post New Homework / DPP</span>
        </button>
      </div>

      {/* Batch Filter Buttons */}
      <div className="flex flex-wrap items-center gap-2">
        {["ALL", "Class 12th Senior Biology", "NEET Medical Specialist Batch", "Class 11th Senior Biology"].map((b) => (
          <button
            key={b}
            onClick={() => setFilterBatch(b)}
            className={`px-3.5 py-1.5 rounded-xl text-xs font-bold transition-all cursor-pointer ${
              filterBatch === b
                ? "bg-[#c22329] text-white shadow-xs"
                : "bg-white hover:bg-slate-50 text-slate-700 border border-slate-200"
            }`}
          >
            {b}
          </button>
        ))}
      </div>

      {/* Assignments Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
        {filtered.map((a) => {
          const submissionPct = Math.round((a.submitted_count / a.total_count) * 100);
          const isComplete = a.submitted_count >= a.total_count;

          return (
            <div
              key={a.id}
              className="bg-white rounded-3xl border border-slate-200/90 shadow-sm p-6 space-y-4 hover:shadow-md transition-all flex flex-col justify-between"
            >
              <div>
                <div className="flex items-start justify-between">
                  <span className="px-2.5 py-1 rounded-md bg-red-50 text-[#c22329] border border-red-200 text-[10px] font-black uppercase">
                    {a.batch_name}
                  </span>
                  <span
                    className={`text-[10px] font-bold px-2 py-0.5 rounded-full border ${
                      a.status === "EVALUATED"
                        ? "bg-emerald-50 text-emerald-700 border-emerald-200"
                        : "bg-amber-50 text-amber-800 border-amber-200"
                    }`}
                  >
                    {a.status}
                  </span>
                </div>

                <h3 className="text-base font-bold text-slate-900 mt-3 leading-snug">
                  {a.title}
                </h3>
                <p className="text-xs text-slate-500 mt-1 font-medium">{a.chapter}</p>

                <div className="mt-4 p-3 rounded-2xl bg-slate-50 border border-slate-200/80 grid grid-cols-2 gap-2 text-xs">
                  <div className="flex items-center gap-1.5 text-slate-700">
                    <Calendar className="w-3.5 h-3.5 text-[#c99a5e]" />
                    <span>Due: <strong>{a.due_date}</strong></span>
                  </div>
                  <div className="flex items-center gap-1.5 text-slate-700">
                    <Award className="w-3.5 h-3.5 text-blue-600" />
                    <span>Max Marks: <strong>{a.total_marks}</strong></span>
                  </div>
                </div>
              </div>

              {/* Submission Progress */}
              <div className="space-y-2 pt-2 border-t border-slate-100">
                <div className="flex items-center justify-between text-xs">
                  <span className="text-slate-500 font-medium">Submissions Received</span>
                  <span
                    className={`font-black ${
                      isComplete ? "text-emerald-700" : "text-slate-900"
                    }`}
                  >
                    {a.submitted_count} / {a.total_count} Students ({submissionPct}%)
                  </span>
                </div>
                <div className="w-full bg-slate-100 h-2 rounded-full overflow-hidden">
                  <div
                    className={`h-full rounded-full transition-all ${
                      isComplete ? "bg-emerald-500" : "bg-blue-600"
                    }`}
                    style={{ width: `${submissionPct}%` }}
                  />
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {/* Post Assignment Modal */}
      {isModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/40 backdrop-blur-sm animate-in fade-in">
          <div className="bg-white border border-slate-200 rounded-3xl p-6 sm:p-8 max-w-lg w-full space-y-5 shadow-2xl relative text-slate-900">
            <div className="flex items-center justify-between border-b border-slate-100 pb-3">
              <div className="flex items-center gap-2">
                <div className="w-8 h-8 rounded-xl bg-red-50 text-[#c22329] border border-red-200 flex items-center justify-center font-bold">
                  <FileText className="w-4 h-4" />
                </div>
                <h3 className="text-lg font-bold text-slate-900">Post Homework / DPP</h3>
              </div>
              <button
                onClick={() => setIsModalOpen(false)}
                className="text-slate-400 hover:text-slate-700 cursor-pointer"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <form onSubmit={handleCreateAssignment} className="space-y-4 text-xs">
              <div className="space-y-1">
                <label className="font-bold text-slate-700">Assignment / DPP Title *</label>
                <input
                  type="text"
                  required
                  value={form.title}
                  onChange={(e) => setForm({ ...form, title: e.target.value })}
                  placeholder="e.g. DPP #16: Nephron Anatomy & Counter-Current Mechanism"
                  className="w-full bg-slate-50 border border-slate-200 rounded-xl px-3 py-2 text-slate-900 focus:bg-white focus:outline-none focus:border-[#c22329]"
                />
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div className="space-y-1">
                  <label className="font-bold text-slate-700">Target Batch *</label>
                  <select
                    value={form.batch_name}
                    onChange={(e) => setForm({ ...form, batch_name: e.target.value })}
                    className="w-full bg-slate-50 border border-slate-200 rounded-xl px-3 py-2 text-slate-900 focus:bg-white focus:outline-none focus:border-[#c22329]"
                  >
                    <option value="Class 12th Senior Biology">Class 12th Senior Biology</option>
                    <option value="NEET Medical Specialist Batch">NEET Medical Specialist Batch</option>
                    <option value="Class 11th Senior Biology">Class 11th Senior Biology</option>
                  </select>
                </div>
                <div className="space-y-1">
                  <label className="font-bold text-slate-700">Max Marks *</label>
                  <input
                    type="number"
                    required
                    value={form.total_marks}
                    onChange={(e) => setForm({ ...form, total_marks: e.target.value })}
                    className="w-full bg-slate-50 border border-slate-200 rounded-xl px-3 py-2 text-slate-900 font-mono focus:bg-white focus:outline-none focus:border-[#c22329]"
                  />
                </div>
              </div>

              <div className="space-y-1">
                <label className="font-bold text-slate-700">Chapter & Syllabus Topic</label>
                <input
                  type="text"
                  value={form.chapter}
                  onChange={(e) => setForm({ ...form, chapter: e.target.value })}
                  className="w-full bg-slate-50 border border-slate-200 rounded-xl px-3 py-2 text-slate-900 focus:bg-white focus:outline-none focus:border-[#c22329]"
                />
              </div>

              <div className="space-y-1">
                <label className="font-bold text-slate-700">Submission Due Date *</label>
                <input
                  type="date"
                  required
                  value={form.due_date}
                  onChange={(e) => setForm({ ...form, due_date: e.target.value })}
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
                  <span>Publish Assignment</span>
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
