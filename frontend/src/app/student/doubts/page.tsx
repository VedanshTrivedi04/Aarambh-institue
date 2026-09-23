"use client";

import React, { useState } from "react";
import {
  HelpCircle,
  MessageCircle,
  Clock,
  CheckCircle2,
  Calendar,
  Send,
  User,
  Users,
  Sparkles,
  MapPin,
  ChevronRight,
  ShieldCheck,
  AlertCircle,
} from "lucide-react";

interface Doubt {
  id: string;
  date: string;
  subject: string;
  faculty: string;
  title: string;
  description: string;
  status: string;
  clinicBooked: boolean;
  clinicTime: string | null;
  reply: string | null;
  repliedAt: string | null;
}

export default function StudentDoubtsPage() {
  const [subject, setSubject] = useState("Biology");
  const [faculty, setFaculty] = useState("Mr. Pankaj Dubey (Head of Biology)");
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [requestClinic, setRequestClinic] = useState(false);
  const [preferredSlot, setPreferredSlot] = useState("Saturday 03:30 PM - 04:30 PM");
  const [submitting, setSubmitting] = useState(false);
  const [toastMessage, setToastMessage] = useState<string | null>(null);

  const [doubts, setDoubts] = useState<Doubt[]>([
    {
      id: "DBT-2026-081",
      date: "21 Sep 2026",
      subject: "Biology",
      faculty: "Mr. Pankaj Dubey (30y Exp)",
      title: "Pedigree Chart: How to differentiate between X-linked recessive vs Autosomal recessive without skipped generations?",
      description: "In DPP-08 question 12, both male and female parents are unaffected, but one male child is affected. Could this be autosomal recessive or strictly X-linked?",
      status: "RESOLVED",
      clinicBooked: true,
      clinicTime: "Attended Saturday 19 Sep (Faculty Cabin A)",
      reply: "Look at the mother's carrier status. In X-linked recessive, if a female child is affected, the father MUST be affected. If fathers are unaffected, but daughters are affected, it is strictly autosomal recessive. I have verified your fair copy.",
      repliedAt: "21 Sep 2026, 06:15 PM",
    },
    {
      id: "DBT-2026-074",
      date: "17 Sep 2026",
      subject: "Physics",
      faculty: "Mrs. Anita Holkar (15y Exp)",
      title: "Lens Maker Formula: What if medium on both sides of convex lens have different refractive indices?",
      description: "Does 1/f = (μ2 - μ1)/R1 - (μ3 - μ2)/R2 apply directly or do we calculate refraction at each curved surface separately?",
      status: "RESOLVED",
      clinicBooked: false,
      clinicTime: null,
      reply: "Always apply the single spherical surface refraction formula: (μ2/v - μ1/u) = (μ2 - μ1)/R for each boundary successively. Never use the standard Lens Maker formula if surrounding media differ on left and right.",
      repliedAt: "18 Sep 2026, 11:20 AM",
    },
    {
      id: "DBT-2026-068",
      date: "14 Sep 2026",
      subject: "Chemistry",
      faculty: "Mr. Ansh Sir (10y Exp)",
      title: "Coordination Compounds: High spin vs Low spin d6 octahedral splitting with weak vs strong field ligands",
      description: "Why does [Fe(H2O)6]2+ have 4 unpaired electrons while [Fe(CN)6]4- is diamagnetic?",
      status: "RESOLVED",
      clinicBooked: false,
      clinicTime: null,
      reply: "Water is a weak field ligand where Crystal Field Splitting Energy (Δo) is less than Pairing Energy (P). Electrons occupy eg orbitals before pairing. Cyanide is a strong field ligand where Δo > P, forcing complete pairing in t2g.",
      repliedAt: "14 Sep 2026, 08:45 PM",
    },
  ]);

  const handleSubmitDoubt = (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitting(true);

    setTimeout(() => {
      setSubmitting(false);
      const newDbt = {
        id: `DBT-2026-0${doubts.length + 82}`,
        date: "Today, 03:45 PM",
        subject,
        faculty,
        title,
        description,
        status: "PENDING_FACULTY",
        clinicBooked: requestClinic,
        clinicTime: requestClinic ? preferredSlot : null,
        reply: null,
        repliedAt: null,
      };

      setDoubts([newDbt, ...doubts]);
      setToastMessage("Doubt submitted! Your educator will respond within 4 hours.");
      setTitle("");
      setDescription("");
      setRequestClinic(false);
      setTimeout(() => setToastMessage(null), 4000);
    }, 700);
  };

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      {/* Toast Alert */}
      {toastMessage && (
        <div className="fixed bottom-6 right-6 z-50 p-4 rounded-2xl bg-slate-900 text-white text-xs font-bold shadow-2xl flex items-center gap-2 animate-in fade-in">
          <CheckCircle2 className="w-4 h-4 text-emerald-400" />
          <span>{toastMessage}</span>
        </div>
      )}

      {/* Header */}
      <div className="bg-white rounded-3xl border border-slate-200/90 p-6 sm:p-8 shadow-sm">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <div className="flex items-center gap-2 mb-1">
              <span className="text-[10px] font-black uppercase tracking-wider px-2 py-0.5 rounded bg-purple-50 text-purple-700 border border-purple-200">
                1-on-1 Academic Support
              </span>
              <span className="text-[10px] font-bold text-slate-500">
                Direct Faculty Access
              </span>
            </div>
            <h1 className="text-2xl font-black text-slate-900 tracking-tight">
              Ask Faculty Doubt & Book Clinic Slot
            </h1>
            <p className="text-xs text-slate-500 mt-1 font-medium">
              Small batch guarantee: No student leaves the institute with unresolved questions
            </p>
          </div>

          <div className="flex items-center gap-3">
            <span className="px-3.5 py-1.5 rounded-full bg-emerald-50 border border-emerald-200 text-xs font-black text-emerald-700 flex items-center gap-1.5">
              <CheckCircle2 className="w-4 h-4 text-emerald-600" />
              <span>3 Clinic Sessions Attended</span>
            </span>
          </div>
        </div>
      </div>

      {/* 2 Column Layout: Form & Doubt History */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Ask Doubt Form (1 Col) */}
        <div className="space-y-6">
          <div className="bg-white rounded-3xl border border-slate-200/90 p-6 shadow-sm space-y-4">
            <div>
              <h2 className="text-sm font-black text-slate-900 uppercase tracking-wider flex items-center gap-2">
                <MessageCircle className="w-4 h-4 text-[#c22329]" />
                <span>Submit New Academic Question</span>
              </h2>
              <p className="text-xs text-slate-500 font-medium mt-0.5">
                Sent straight to educator&apos;s personal ERP desk
              </p>
            </div>

            <form onSubmit={handleSubmitDoubt} className="space-y-3.5 text-xs">
              <div className="space-y-1">
                <label className="font-bold text-slate-700">Subject Stream</label>
                <select
                  value={subject}
                  onChange={(e) => {
                    setSubject(e.target.value);
                    if (e.target.value === "Biology") setFaculty("Mr. Pankaj Dubey (Head of Biology)");
                    else if (e.target.value === "Physics") setFaculty("Mrs. Anita Holkar (15y Exp)");
                    else setFaculty("Mr. Ansh Sir (10y Exp)");
                  }}
                  className="w-full bg-slate-50 border border-slate-200 rounded-xl px-3 py-2 text-slate-900 font-medium focus:bg-white focus:outline-none focus:border-[#c22329]"
                >
                  <option value="Biology">Biology (Botany & Zoology)</option>
                  <option value="Physics">Physics (Mechanics & Optics)</option>
                  <option value="Chemistry">Chemistry (Inorganic & Physical)</option>
                  <option value="Mathematics">Optional Mathematics</option>
                </select>
              </div>

              <div className="space-y-1">
                <label className="font-bold text-slate-700">Assigned Educator</label>
                <input
                  type="text"
                  readOnly
                  value={faculty}
                  className="w-full bg-slate-100 border border-slate-200 rounded-xl px-3 py-2 text-slate-700 font-semibold cursor-not-allowed"
                />
              </div>

              <div className="space-y-1">
                <label className="font-bold text-slate-700">Question Title / Topic</label>
                <input
                  type="text"
                  required
                  value={title}
                  onChange={(e) => setTitle(e.target.value)}
                  placeholder="e.g. Pedigree numerical problem on X-linked traits"
                  className="w-full bg-slate-50 border border-slate-200 rounded-xl px-3 py-2 text-slate-900 font-medium focus:bg-white focus:outline-none focus:border-[#c22329]"
                />
              </div>

              <div className="space-y-1">
                <label className="font-bold text-slate-700">Doubt Description / Numerical Details</label>
                <textarea
                  rows={4}
                  required
                  value={description}
                  onChange={(e) => setDescription(e.target.value)}
                  placeholder="State the concept or equation where you are facing difficulty..."
                  className="w-full bg-slate-50 border border-slate-200 rounded-xl p-3 text-slate-900 font-medium focus:bg-white focus:outline-none focus:border-[#c22329]"
                />
              </div>

              {/* 1-on-1 Clinic Booking Checkbox */}
              <div className="p-3.5 rounded-2xl bg-amber-50/70 border border-amber-200/80 space-y-2">
                <label className="flex items-center gap-2 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={requestClinic}
                    onChange={(e) => setRequestClinic(e.target.checked)}
                    className="w-4 h-4 text-[#c22329] rounded border-slate-300 focus:ring-red-500"
                  />
                  <span className="font-bold text-slate-900 text-xs">
                    Book In-Person 1-on-1 Clinic Slot
                  </span>
                </label>
                {requestClinic && (
                  <div className="space-y-1 animate-in fade-in">
                    <span className="text-[10px] text-slate-500 font-medium block">
                      Select Preferred Consultation Window:
                    </span>
                    <select
                      value={preferredSlot}
                      onChange={(e) => setPreferredSlot(e.target.value)}
                      className="w-full bg-white border border-amber-300 rounded-xl px-2.5 py-1.5 text-slate-900 font-semibold text-xs"
                    >
                      <option>Saturday 03:30 PM - 04:30 PM (Cabin A)</option>
                      <option>Saturday 04:30 PM - 05:30 PM (Cabin A)</option>
                      <option>Wednesday 07:00 PM - 07:45 PM (Post-Class)</option>
                    </select>
                  </div>
                )}
              </div>

              <button
                type="submit"
                disabled={submitting}
                className="w-full py-2.5 px-4 rounded-xl font-bold bg-[#c22329] hover:bg-red-700 text-white transition-all shadow-md flex items-center justify-center gap-2 cursor-pointer disabled:opacity-50"
              >
                <Send className="w-3.5 h-3.5" />
                <span>{submitting ? "Sending to Faculty..." : "Submit Question to Educator"}</span>
              </button>
            </form>
          </div>

          {/* Cabin Location Notice */}
          <div className="p-5 rounded-3xl bg-slate-900 text-white shadow-md space-y-2">
            <h3 className="text-xs font-black text-[#c99a5e] uppercase tracking-wider flex items-center gap-1.5">
              <MapPin className="w-3.5 h-3.5" />
              <span>Campus Doubt Counters</span>
            </h3>
            <p className="text-xs text-slate-300 leading-relaxed font-normal">
              Mr. Pankaj Dubey sits in <strong>Faculty Cabin A (First Floor)</strong> every day from 03:00 PM onwards before batch lectures begin.
            </p>
          </div>
        </div>

        {/* Doubt History & Responses (2 Cols) */}
        <div className="lg:col-span-2 space-y-4">
          <div className="bg-white rounded-3xl border border-slate-200/90 p-6 shadow-sm space-y-4">
            <div className="flex items-center justify-between pb-3 border-b border-slate-100">
              <div>
                <h2 className="text-base font-black text-slate-900 flex items-center gap-2">
                  <HelpCircle className="w-4 h-4 text-[#c22329]" />
                  <span>Doubt Tickets & Educator Responses</span>
                </h2>
                <p className="text-xs text-slate-500 font-medium mt-0.5">
                  Complete discussion trail with teacher evaluations
                </p>
              </div>
              <span className="text-xs font-bold text-slate-500">
                {doubts.length} Question Threads
              </span>
            </div>

            <div className="space-y-4">
              {doubts.map((dbt) => (
                <div
                  key={dbt.id}
                  className="p-5 rounded-2xl border border-slate-200 bg-white hover:border-slate-300 transition-all space-y-3"
                >
                  <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
                    <div className="flex items-center gap-2">
                      <span className="text-[10px] font-mono font-bold px-2 py-0.5 rounded bg-slate-100 text-slate-700 border border-slate-200">
                        {dbt.id}
                      </span>
                      <span
                        className={`text-[10px] font-black uppercase px-2 py-0.5 rounded ${
                          dbt.subject === "Biology"
                            ? "bg-emerald-100 text-emerald-800"
                            : dbt.subject === "Physics"
                            ? "bg-blue-100 text-blue-800"
                            : "bg-red-100 text-red-800"
                        }`}
                      >
                        {dbt.subject}
                      </span>
                      <span className="text-xs font-semibold text-slate-500">
                        Assigned to: <strong className="text-slate-800">{dbt.faculty}</strong>
                      </span>
                    </div>

                    <div className="flex items-center gap-2">
                      {dbt.status === "RESOLVED" ? (
                        <span className="px-2.5 py-0.5 rounded-full bg-emerald-50 text-emerald-700 border border-emerald-200 text-[10px] font-black flex items-center gap-1">
                          <CheckCircle2 className="w-3 h-3" />
                          <span>RESOLVED</span>
                        </span>
                      ) : (
                        <span className="px-2.5 py-0.5 rounded-full bg-amber-50 text-amber-700 border border-amber-200 text-[10px] font-black flex items-center gap-1 animate-pulse">
                          <Clock className="w-3 h-3" />
                          <span>AWAITING REPLY</span>
                        </span>
                      )}
                    </div>
                  </div>

                  <div>
                    <h3 className="text-sm font-bold text-slate-900">{dbt.title}</h3>
                    <p className="text-xs text-slate-600 mt-1 font-normal leading-relaxed">
                      {dbt.description}
                    </p>
                  </div>

                  {/* 1-on-1 Clinic Slot Banner */}
                  {dbt.clinicBooked && (
                    <div className="p-2.5 rounded-xl bg-purple-50 border border-purple-200 text-xs text-purple-900 flex items-center gap-2 font-medium">
                      <Calendar className="w-3.5 h-3.5 text-purple-600" />
                      <span>1-on-1 Clinic Appointment: <strong>{dbt.clinicTime}</strong></span>
                    </div>
                  )}

                  {/* Educator Answer */}
                  {dbt.reply ? (
                    <div className="p-4 rounded-2xl bg-slate-50 border border-slate-200/90 text-xs space-y-1.5">
                      <div className="flex items-center justify-between text-[11px] font-bold text-slate-700">
                        <span className="flex items-center gap-1 text-[#c22329]">
                          <ShieldCheck className="w-3.5 h-3.5 text-[#c22329]" />
                          <span>Official Faculty Explanation ({dbt.faculty})</span>
                        </span>
                        <span className="text-[10px] text-slate-400 font-normal">{dbt.repliedAt}</span>
                      </div>
                      <p className="text-slate-800 leading-relaxed font-normal">
                        {dbt.reply}
                      </p>
                    </div>
                  ) : (
                    <div className="p-3 rounded-xl bg-amber-50/60 border border-amber-200 text-xs text-amber-800 font-medium">
                      Educator is reviewing your question. Written answer or clinic slot will be posted shortly.
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
