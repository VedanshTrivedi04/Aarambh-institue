"use client";

import React, { useEffect, useState } from "react";
import { Sparkles, Calendar, Clock, Award, CheckCircle, ArrowRight, Download, Loader2, AlertTriangle } from "lucide-react";
import { submitPublicEnquiry } from "@/lib/api";

interface TestDate {
  date: string;
  time: string;
  mode: string;
}

const FALLBACK_TEST_DATES: TestDate[] = [
  { date: "Sunday, 29th March 2026", time: "10:00 AM - 11:30 AM", mode: "Online & Offline" },
  { date: "Sunday, 5th April 2026", time: "10:00 AM - 11:30 AM", mode: "Online & Offline" },
  { date: "Sunday, 12th April 2026", time: "10:00 AM - 11:30 AM", mode: "Online & Offline" },
];

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";

export default function ScholarshipSection() {
  const [selectedClass, setSelectedClass] = useState<string>("10");
  const [selectedStream, setSelectedStream] = useState<string>("jee");
  const [registered, setRegistered] = useState<boolean>(false);
  const [studentName, setStudentName] = useState<string>("");
  const [studentPhone, setStudentPhone] = useState<string>("");
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [testDates, setTestDates] = useState<TestDate[]>(FALLBACK_TEST_DATES);

  useEffect(() => {
    fetch(`${API_BASE_URL}/api/v1/admin/cms/content/student_corner`, { cache: "no-store" })
      .then((res) => (res.ok ? res.json() : null))
      .then((json) => {
        if (json?.data?.scholarship_tests?.length) {
          setTestDates(json.data.scholarship_tests);
        }
      })
      .catch(() => {});
  }, []);

  const handleRegister = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!studentName || !studentPhone) return;
    setSubmitting(true);
    setError(null);

    const res = await submitPublicEnquiry({
      student_name: studentName,
      parent_name: studentName,
      phone: studentPhone,
      target_class: `Class ${selectedClass}`,
      stream: selectedStream,
      remarks: `A-SAT Scholarship Test registration (Class ${selectedClass}, target: ${selectedStream}).`,
    });

    setSubmitting(false);

    if (!res.success) {
      setError(res.error || "Could not register — please try again or contact us directly.");
      return;
    }

    setRegistered(true);
  };

  return (
    <section id="scholarship" className="relative py-24 bg-white text-slate-900 border-t border-slate-200/80">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-12 items-center">
          {/* Left Column: Information & Test Dates */}
          <div className="lg:col-span-7 space-y-6">
            <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-amber-50 border border-amber-200 text-amber-800 text-xs font-bold uppercase tracking-wider">
              <Sparkles className="w-3.5 h-3.5 text-amber-600" />
              <span>Aarambh Scholarship & Aptitude Test (A-SAT)</span>
            </div>

            <h2 className="text-3xl sm:text-5xl font-black tracking-tight text-slate-900 leading-tight">
              Avail Up To <span className="gradient-text-gold">90% Scholarship</span> <br />
              On 2026 – 2027 Tuition Fees
            </h2>

            <p className="text-sm sm:text-base text-slate-600 leading-relaxed max-w-xl font-normal">
              Financial constraints should never stand between a bright student and premier coaching. A-SAT evaluates your analytical reasoning and rewards merit with massive tuition waivers.
            </p>

            {/* Feature Bullets */}
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 pt-2 text-xs sm:text-sm text-slate-800 font-semibold">
              <div className="flex items-center gap-2.5 p-3.5 rounded-2xl bg-slate-50 border border-slate-200/80">
                <CheckCircle className="w-4 h-4 text-amber-600 flex-shrink-0" />
                <span>Zero Registration Fee (Free Test)</span>
              </div>
              <div className="flex items-center gap-2.5 p-3.5 rounded-2xl bg-slate-50 border border-slate-200/80">
                <CheckCircle className="w-4 h-4 text-blue-600 flex-shrink-0" />
                <span>10-Page In-Depth Aptitude Analysis</span>
              </div>
              <div className="flex items-center gap-2.5 p-3.5 rounded-2xl bg-slate-50 border border-slate-200/80">
                <CheckCircle className="w-4 h-4 text-emerald-600 flex-shrink-0" />
                <span>Online (Home) or Offline (Campus)</span>
              </div>
              <div className="flex items-center gap-2.5 p-3.5 rounded-2xl bg-slate-50 border border-slate-200/80">
                <CheckCircle className="w-4 h-4 text-purple-600 flex-shrink-0" />
                <span>1:1 Counseling with Senior IITian</span>
              </div>
            </div>

            {/* Upcoming Test Dates */}
            <div className="pt-4 space-y-3">
              <h4 className="text-xs font-bold uppercase tracking-wider text-slate-500">
                Upcoming Examination Slots:
              </h4>
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
                {testDates.map((item, idx) => (
                  <div
                    key={idx}
                    className="p-3.5 rounded-2xl bg-slate-50 border border-slate-200 hover:border-blue-300 transition-all text-left space-y-1"
                  >
                    <div className="flex items-center gap-1.5 text-blue-700 text-xs font-bold">
                      <Calendar className="w-3.5 h-3.5" />
                      <span>{item.date}</span>
                    </div>
                    <div className="text-[11px] text-slate-600 flex items-center gap-1 font-medium">
                      <Clock className="w-3 h-3 text-slate-400" />
                      <span>{item.time}</span>
                    </div>
                    <span className="inline-block text-[10px] text-emerald-800 bg-emerald-100 border border-emerald-200 px-2 py-0.5 rounded font-bold">
                      {item.mode}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Right Column: Instant Registration Card */}
          <div className="lg:col-span-5">
            <div className="bg-white p-7 sm:p-8 rounded-3xl border border-slate-200 shadow-xl relative overflow-hidden">
              {!registered ? (
                <form onSubmit={handleRegister} className="space-y-4">
                  <div>
                    <h3 className="text-xl font-bold text-slate-900">
                      Register For Free A-SAT
                    </h3>
                    <p className="text-xs text-slate-500 mt-1 font-medium">
                      Fill details to book test slot & instantly download sample papers
                    </p>
                  </div>

                  <div>
                    <label className="block text-xs font-bold text-slate-700 mb-1">
                      Student Full Name *
                    </label>
                    <input
                      type="text"
                      required
                      value={studentName}
                      onChange={(e) => setStudentName(e.target.value)}
                      placeholder="e.g. Aryan Sharma"
                      className="w-full px-4 py-2.5 rounded-xl bg-slate-50 border border-slate-200 text-slate-900 placeholder-slate-400 text-sm focus:outline-none focus:bg-white focus:border-blue-500 transition-colors font-medium"
                    />
                  </div>

                  <div>
                    <label className="block text-xs font-bold text-slate-700 mb-1">
                      Parent / Student Mobile Number *
                    </label>
                    <input
                      type="tel"
                      required
                      value={studentPhone}
                      onChange={(e) => setStudentPhone(e.target.value)}
                      placeholder="+91 98765 43210"
                      className="w-full px-4 py-2.5 rounded-xl bg-slate-50 border border-slate-200 text-slate-900 placeholder-slate-400 text-sm focus:outline-none focus:bg-white focus:border-blue-500 transition-colors font-medium"
                    />
                  </div>

                  {/* Class selection */}
                  <div>
                    <label className="block text-xs font-bold text-slate-700 mb-1.5">
                      Current Class (Academic 2025-26)
                    </label>
                    <div className="grid grid-cols-5 gap-1.5">
                      {["8", "9", "10", "11", "12+"].map((cls) => (
                        <button
                          type="button"
                          key={cls}
                          onClick={() => setSelectedClass(cls)}
                          className={`py-2 rounded-xl text-xs font-bold transition-all ${
                            selectedClass === cls
                              ? "bg-blue-600 text-white shadow-sm"
                              : "bg-slate-100 text-slate-700 hover:bg-slate-200 border border-slate-200"
                          }`}
                        >
                          Class {cls}
                        </button>
                      ))}
                    </div>
                  </div>

                  {/* Target Stream */}
                  <div>
                    <label className="block text-xs font-bold text-slate-700 mb-1.5">
                      Target Career Goal
                    </label>
                    <div className="grid grid-cols-3 gap-2">
                      {[
                        { id: "jee", label: "JEE (Engg)" },
                        { id: "neet", label: "NEET (Med)" },
                        { id: "found", label: "Foundation" },
                      ].map((stream) => (
                        <button
                          type="button"
                          key={stream.id}
                          onClick={() => setSelectedStream(stream.id)}
                          className={`py-2 rounded-xl text-xs font-bold transition-all ${
                            selectedStream === stream.id
                              ? "bg-amber-500 text-slate-950"
                              : "bg-slate-100 text-slate-700 hover:bg-slate-200 border border-slate-200"
                          }`}
                        >
                          {stream.label}
                        </button>
                      ))}
                    </div>
                  </div>

                  {error && (
                    <p className="text-xs font-semibold text-[#c22329] bg-red-50 border border-red-200 rounded-xl px-3 py-2 flex items-center gap-1.5">
                      <AlertTriangle className="w-3.5 h-3.5 shrink-0" />
                      <span>{error}</span>
                    </p>
                  )}

                  <button
                    type="submit"
                    disabled={submitting}
                    className="w-full py-3.5 rounded-xl text-sm font-bold text-white bg-gradient-to-r from-blue-600 to-indigo-700 hover:from-blue-500 hover:to-blue-600 shadow-lg shadow-blue-600/25 transition-all hover:scale-[1.02] flex items-center justify-center gap-2 mt-2 disabled:opacity-60"
                  >
                    {submitting ? <Loader2 className="w-4 h-4 animate-spin" /> : (
                      <>
                        <span>Claim Free A-SAT Slot & Download Syllabus</span>
                        <ArrowRight className="w-4 h-4" />
                      </>
                    )}
                  </button>

                  <p className="text-[11px] text-center text-slate-500">
                    🔒 No credit card required. Aarambh Institute never shares your data.
                  </p>
                </form>
              ) : (
                <div className="text-center py-6 space-y-4 animate-in fade-in">
                  <div className="w-16 h-16 rounded-full bg-emerald-100 text-emerald-700 flex items-center justify-center mx-auto">
                    <CheckCircle className="w-8 h-8" />
                  </div>
                  <h3 className="text-xl font-bold text-slate-900">
                    Slot Booked Successfully!
                  </h3>
                  <p className="text-xs text-slate-600 leading-relaxed font-medium">
                    Thank you, <strong className="text-slate-900">{studentName}</strong>. Our academic team has sent your test admit card & login credentials to <strong className="text-blue-700">{studentPhone}</strong>.
                  </p>
                  <div className="p-4 rounded-2xl bg-slate-50 border border-slate-200 text-left space-y-2 text-xs">
                    <div className="flex items-center justify-between text-slate-600">
                      <span>Target:</span>
                      <span className="font-bold text-slate-900 uppercase">{selectedStream} — Class {selectedClass}</span>
                    </div>
                    <div className="flex items-center justify-between text-slate-600">
                      <span>Assigned Date:</span>
                      <span className="font-bold text-amber-700">{testDates[0]?.date || "Upcoming Sunday"} ({testDates[0]?.time || "10:00 AM"})</span>
                    </div>
                  </div>
                  <button
                    onClick={() => {
                      alert("Downloading A-SAT Syllabus & Previous Year Sample Question Paper PDF!");
                    }}
                    className="w-full py-3 rounded-xl text-xs font-bold text-slate-800 bg-slate-100 hover:bg-slate-200 border border-slate-200 transition-all flex items-center justify-center gap-2"
                  >
                    <Download className="w-4 h-4 text-blue-600" />
                    <span>Download Official Sample Paper PDF</span>
                  </button>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
