"use client";

import React, { useState } from "react";
import {
  HelpCircle,
  Clock,
  CheckCircle2,
  Calendar,
  MessageCircle,
  X,
  Loader2,
  BookOpen,
} from "lucide-react";

interface DoubtTicket {
  id: string;
  student_name: string;
  admission_number: string;
  batch: string;
  chapter: string;
  question: string;
  priority: "HIGH" | "MEDIUM" | "NORMAL";
  status: "PENDING" | "SCHEDULED" | "RESOLVED";
  submitted_at: string;
  clinic_time?: string;
  teacher_reply?: string;
}

export default function TeacherDoubtsPage() {
  const [doubts, setDoubts] = useState<DoubtTicket[]>([
    {
      id: "d1",
      student_name: "Monika Patidar",
      admission_number: "AAR-2026-006",
      batch: "Class 12th Senior Biology",
      chapter: "Chapter 18: Body Fluids & Circulation",
      question: "Sir, I am getting confused between the P-wave and T-wave repolarization in ECG questions. Can you explain the depolarization sequence again?",
      priority: "HIGH",
      status: "PENDING",
      submitted_at: "Today, 1:15 PM",
    },
    {
      id: "d2",
      student_name: "Rohit Garg",
      admission_number: "AAR-2026-002",
      batch: "NEET Medical Specialist Batch",
      chapter: "Principles of Inheritance",
      question: "In Morgan's dihybrid cross with Drosophila, why did the yellow body and white eye genes show only 1.3% recombination?",
      priority: "HIGH",
      status: "SCHEDULED",
      submitted_at: "Yesterday, 6:00 PM",
      clinic_time: "Today at 7:30 PM (Faculty Room A)",
    },
    {
      id: "d3",
      student_name: "Neha Yadav",
      admission_number: "AAR-2026-004",
      batch: "Class 12th Senior Biology",
      chapter: "Human Physiology",
      question: "In NCERT Figure 18.2, what is the exact difference between the tricuspid and bicuspid valve chordae tendineae attachments?",
      priority: "MEDIUM",
      status: "PENDING",
      submitted_at: "21 Sep, 8:30 PM",
    },
    {
      id: "d4",
      student_name: "Prince Yadav",
      admission_number: "AAR-2026-001",
      batch: "NEET Medical Specialist Batch",
      chapter: "Genetics Numericals",
      question: "Cleared in class regarding ABO blood group codominance. Notebook verified.",
      priority: "NORMAL",
      status: "RESOLVED",
      submitted_at: "20 Sep, 4:00 PM",
      teacher_reply: "Explained using multiple allele Punnett square. Concept fully clear.",
    },
  ]);

  const [filterStatus, setFilterStatus] = useState<string>("ALL");
  const [activeTicket, setActiveTicket] = useState<DoubtTicket | null>(null);
  const [replyText, setReplyText] = useState("");
  const [clinicSlot, setClinicSlot] = useState("Today at 7:30 PM (Faculty Room A)");
  const [submitting, setSubmitting] = useState(false);

  const handleResolve = (id: string) => {
    setSubmitting(true);
    setTimeout(() => {
      setDoubts((prev) =>
        prev.map((d) =>
          d.id === id
            ? {
                ...d,
                status: "RESOLVED",
                teacher_reply: replyText || "Doubt addressed and verified during lecture clinic.",
              }
            : d
        )
      );
      setSubmitting(false);
      setActiveTicket(null);
      setReplyText("");
    }, 400);
  };

  const handleScheduleClinic = (id: string) => {
    setDoubts((prev) =>
      prev.map((d) =>
        d.id === id
          ? {
              ...d,
              status: "SCHEDULED",
              clinic_time: clinicSlot,
            }
          : d
      )
    );
    setActiveTicket(null);
  };

  const filtered = doubts.filter((d) => {
    if (filterStatus === "ALL") return true;
    return d.status === filterStatus;
  });

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 text-xs font-bold text-slate-500 mb-1">
            <span>Faculty</span>
            <span>/</span>
            <span className="text-[#c22329]">Student Doubts & Revision</span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-black text-slate-900">
            Student Doubt Tickets & 1-on-1 Clinics
          </h1>
          <p className="text-xs text-slate-500 mt-0.5">
            Aarambh personal attention guarantee: every student question receives written guidance or a dedicated 1-on-1 cabin slot.
          </p>
        </div>

        <div className="flex items-center gap-2">
          <span className="px-3 py-1.5 rounded-xl bg-amber-50 border border-amber-200 text-xs font-bold text-amber-800">
            Next Clinic: Today 7:30 PM
          </span>
        </div>
      </div>

      {/* Filter Tabs */}
      <div className="flex items-center gap-2">
        {["ALL", "PENDING", "SCHEDULED", "RESOLVED"].map((st) => (
          <button
            key={st}
            onClick={() => setFilterStatus(st)}
            className={`px-3.5 py-1.5 rounded-xl text-xs font-bold transition-all cursor-pointer ${
              filterStatus === st
                ? "bg-[#c22329] text-white shadow-xs"
                : "bg-white hover:bg-slate-50 text-slate-700 border border-slate-200"
            }`}
          >
            {st}
          </button>
        ))}
      </div>

      {/* Doubts Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
        {filtered.map((d) => (
          <div
            key={d.id}
            className="bg-white rounded-3xl border border-slate-200/90 shadow-sm p-6 space-y-4 hover:shadow-md transition-all flex flex-col justify-between"
          >
            <div>
              <div className="flex items-start justify-between">
                <div>
                  <h3 className="text-base font-bold text-slate-900">{d.student_name}</h3>
                  <span className="text-[10px] font-mono text-slate-500 font-bold">
                    {d.admission_number} • {d.batch}
                  </span>
                </div>

                <div className="flex items-center gap-1.5">
                  <span
                    className={`text-[10px] font-black uppercase px-2.5 py-0.5 rounded-md border ${
                      d.priority === "HIGH"
                        ? "bg-red-50 text-[#c22329] border-red-200"
                        : "bg-amber-50 text-amber-800 border-amber-200"
                    }`}
                  >
                    {d.priority} Priority
                  </span>

                  <span
                    className={`text-[10px] font-bold px-2 py-0.5 rounded-full border ${
                      d.status === "RESOLVED"
                        ? "bg-emerald-50 text-emerald-700 border-emerald-200"
                        : d.status === "SCHEDULED"
                        ? "bg-blue-50 text-blue-700 border-blue-200"
                        : "bg-amber-50 text-amber-800 border-amber-200"
                    }`}
                  >
                    {d.status}
                  </span>
                </div>
              </div>

              <div className="mt-3 text-xs font-bold text-slate-700 flex items-center gap-1.5">
                <BookOpen className="w-3.5 h-3.5 text-[#c22329]" />
                <span>{d.chapter}</span>
              </div>

              <div className="mt-2.5 p-3.5 rounded-2xl bg-slate-50 border border-slate-200/80 text-xs text-slate-800 leading-relaxed font-medium">
                &quot;{d.question}&quot;
              </div>

              {d.clinic_time && (
                <div className="mt-2.5 p-2.5 rounded-xl bg-blue-50 border border-blue-200 text-xs font-semibold text-blue-800 flex items-center gap-2">
                  <Clock className="w-3.5 h-3.5 text-blue-600 shrink-0" />
                  <span>Clinic Slot: {d.clinic_time}</span>
                </div>
              )}

              {d.teacher_reply && (
                <div className="mt-2.5 p-2.5 rounded-xl bg-emerald-50 border border-emerald-200 text-xs text-emerald-800">
                  <span className="font-bold block">Pankaj Sir Resolution:</span>
                  <span>{d.teacher_reply}</span>
                </div>
              )}
            </div>

            {/* Bottom Actions */}
            <div className="pt-3 border-t border-slate-100 flex items-center justify-between text-xs">
              <span className="text-slate-400 text-[11px] font-medium">{d.submitted_at}</span>

              {d.status !== "RESOLVED" && (
                <button
                  onClick={() => setActiveTicket(d)}
                  className="btn-caramel-gold px-3.5 py-1.5 rounded-xl text-xs font-bold shadow-xs cursor-pointer"
                >
                  Resolve or Schedule
                </button>
              )}
            </div>
          </div>
        ))}
      </div>

      {/* Resolution & Schedule Modal */}
      {activeTicket && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/40 backdrop-blur-sm animate-in fade-in">
          <div className="bg-white border border-slate-200 rounded-3xl p-6 sm:p-8 max-w-lg w-full space-y-5 shadow-2xl relative text-slate-900">
            <div className="flex items-center justify-between border-b border-slate-100 pb-3">
              <div className="flex items-center gap-2">
                <div className="w-8 h-8 rounded-xl bg-red-50 text-[#c22329] border border-red-200 flex items-center justify-center font-bold">
                  <HelpCircle className="w-4 h-4" />
                </div>
                <h3 className="text-lg font-bold text-slate-900">
                  Address Doubt for {activeTicket.student_name}
                </h3>
              </div>
              <button
                onClick={() => setActiveTicket(null)}
                className="text-slate-400 hover:text-slate-700 cursor-pointer"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <div className="text-xs space-y-1">
              <span className="font-bold text-slate-500">Student Question:</span>
              <p className="p-3 rounded-xl bg-slate-50 border border-slate-200 text-slate-800 italic">
                &quot;{activeTicket.question}&quot;
              </p>
            </div>

            <div className="space-y-4 text-xs">
              <div className="space-y-1">
                <label className="font-bold text-slate-700">Option A: Schedule 1-on-1 Cabin Clinic Slot</label>
                <input
                  type="text"
                  value={clinicSlot}
                  onChange={(e) => setClinicSlot(e.target.value)}
                  className="w-full bg-slate-50 border border-slate-200 rounded-xl px-3 py-2 text-slate-900 focus:bg-white focus:outline-none focus:border-[#c22329]"
                />
                <button
                  type="button"
                  onClick={() => handleScheduleClinic(activeTicket.id)}
                  className="mt-1.5 px-3 py-1.5 rounded-lg bg-blue-50 text-blue-700 border border-blue-200 font-bold hover:bg-blue-100 transition-colors cursor-pointer"
                >
                  Confirm Clinic Slot
                </button>
              </div>

              <div className="space-y-1 pt-2 border-t border-slate-100">
                <label className="font-bold text-slate-700">Option B: Written Clarification & Mark Resolved</label>
                <textarea
                  rows={3}
                  value={replyText}
                  onChange={(e) => setReplyText(e.target.value)}
                  placeholder="Explain formula, concept, or reference NCERT page number..."
                  className="w-full bg-slate-50 border border-slate-200 rounded-xl px-3 py-2 text-slate-900 focus:bg-white focus:outline-none focus:border-[#c22329]"
                />
              </div>

              <div className="flex justify-end gap-2 pt-2">
                <button
                  type="button"
                  onClick={() => setActiveTicket(null)}
                  className="px-4 py-2 rounded-xl bg-slate-100 hover:bg-slate-200 text-slate-700 font-bold transition-colors cursor-pointer"
                >
                  Close
                </button>
                <button
                  type="button"
                  onClick={() => handleResolve(activeTicket.id)}
                  disabled={submitting}
                  className="btn-caramel-gold px-5 py-2 rounded-xl font-bold flex items-center gap-1.5 shadow-md cursor-pointer"
                >
                  {submitting && <Loader2 className="w-3 h-3 animate-spin" />}
                  <span>Mark Doubt Resolved</span>
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
