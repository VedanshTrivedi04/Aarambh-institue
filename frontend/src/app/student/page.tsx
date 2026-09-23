"use client";

import React, { useState } from "react";
import Link from "next/link";
import dynamic from "next/dynamic";
import {
  CalendarCheck,
  Award,
  FileText,
  Clock,
  ArrowRight,
  TrendingUp,
  AlertCircle,
  CheckCircle2,
  MapPin,
  HelpCircle,
  CreditCard,
  Download,
  Users,
  Sparkles,
} from "lucide-react";

// Dynamically import the canvas-based ID card (client-only)
const StudentIDCard = dynamic(
  () => import("@/components/student/StudentIDCard"),
  { ssr: false }
);

export default function StudentDashboardPage() {
  const [showIDCard, setShowIDCard] = useState(false);

  const scheduleToday = [
    {
      time: "04:00 PM - 05:00 PM",
      subject: "Physics",
      topic: "Ray Optics & Optical Instruments",
      faculty: "Mrs. Anita Holkar (15y Exp)",
      room: "Room 201 (Air-Conditioned)",
      status: "COMPLETED",
    },
    {
      time: "05:00 PM - 06:15 PM",
      subject: "Biology",
      topic: "Principles of Inheritance & Variation (DPP-08 Discussion)",
      faculty: "Mr. Pankaj Dubey (30y Exp, Bio Head)",
      room: "Room 201 (Air-Conditioned)",
      status: "UPCOMING_NEXT",
    },
    {
      time: "06:30 PM - 07:30 PM",
      subject: "Chemistry",
      topic: "Coordination Compounds: Crystal Field Theory",
      faculty: "Mr. Ansh Sir (10y Exp)",
      room: "Room 201 (Air-Conditioned)",
      status: "UPCOMING",
    },
  ];

  const recentTests = [
    {
      name: "NEET Diagnostic Mock #4",
      date: "18 Sep 2026",
      subject: "Biology (Complete Unit)",
      marks: "348 / 360",
      percent: "96.6%",
      rank: "Rank 1st",
      badge: "TOPPER",
    },
    {
      name: "CBSE / MP Board Periodic Test #2",
      date: "10 Sep 2026",
      subject: "Physics & Chemistry Combo",
      marks: "94 / 100",
      percent: "94.0%",
      rank: "Rank 2nd",
      badge: "DISTINCTION",
    },
    {
      name: "Weekly Speed Drill #12",
      date: "03 Sep 2026",
      subject: "Biology - Molecular Basis",
      marks: "176 / 180",
      percent: "97.7%",
      rank: "Rank 1st",
      badge: "TOPPER",
    },
  ];

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      {/* Welcome Banner */}
      <div className="bg-white rounded-3xl border border-slate-200/90 p-6 sm:p-8 shadow-sm relative overflow-hidden">
        <div className="absolute top-0 right-0 w-80 h-80 bg-gradient-to-br from-red-500/10 via-amber-500/5 to-transparent rounded-bl-full pointer-events-none" />

        <div className="relative z-10 flex flex-col lg:flex-row lg:items-center justify-between gap-6">
          <div className="space-y-2">
            <div className="flex flex-wrap items-center gap-2">
              <span className="text-[10px] font-black uppercase tracking-wider px-2.5 py-1 rounded-full bg-red-50 text-[#c22329] border border-red-200">
                Admitted Batch: 2026-27
              </span>
              <span className="text-[10px] font-black uppercase tracking-wider px-2.5 py-1 rounded-full bg-emerald-50 text-emerald-700 border border-emerald-200 flex items-center gap-1">
                <CheckCircle2 className="w-3 h-3" />
                Active Student
              </span>
              <span className="text-[10px] font-bold text-slate-500">
                Enrollment ID: <strong className="text-slate-800">AAR-2026-001</strong>
              </span>
            </div>

            <h1 className="text-2xl sm:text-3xl font-black text-slate-900 tracking-tight">
              Welcome back, Prince Yadav! 👋
            </h1>

            <p className="text-xs sm:text-sm text-slate-600 max-w-2xl font-normal leading-relaxed">
              Enrolled in <strong className="text-slate-900">Class 12th Senior Biology (Board + NEET)</strong>.
              Your next class with <strong className="text-[#c22329]">Mr. Pankaj Dubey</strong> starts at{" "}
              <strong className="text-slate-900">5:00 PM in Room 201</strong>.
            </p>
          </div>

          {/* Quick Action Buttons */}
          <div className="flex flex-wrap items-center gap-2.5 shrink-0">
            <button
              onClick={() => setShowIDCard(true)}
              className="flex items-center gap-2 px-4 py-2.5 rounded-xl border border-slate-200 bg-slate-50 hover:bg-slate-100 text-xs font-bold text-slate-800 transition-colors shadow-xs cursor-pointer"
            >
              <Download className="w-3.5 h-3.5 text-slate-600" />
              <span>Download Student ID</span>
            </button>

            <Link
              href="/student/doubts"
              className="btn-caramel-gold flex items-center gap-2 px-4 py-2.5 rounded-xl text-xs font-bold shadow-md hover:scale-105 transition-transform"
            >
              <HelpCircle className="w-3.5 h-3.5" />
              <span>Ask A Faculty Doubt</span>
            </Link>
          </div>
        </div>
      </div>

      {/* Student ID Card Modal */}
      {showIDCard && (
        <StudentIDCard onClose={() => setShowIDCard(false)} />
      )}

      {/* 4 Academic KPI Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Attendance */}
        <div className="bg-white rounded-3xl border border-slate-200/90 p-5 shadow-sm hover:shadow-md transition-shadow">
          <div className="flex items-center justify-between mb-3">
            <span className="text-xs font-bold text-slate-500 uppercase tracking-wider">
              Lecture Attendance
            </span>
            <div className="w-8 h-8 rounded-xl bg-emerald-50 text-emerald-600 border border-emerald-200 flex items-center justify-center">
              <CalendarCheck className="w-4 h-4" />
            </div>
          </div>
          <div className="text-2xl font-black text-slate-900">98.2%</div>
          <p className="text-[11px] text-emerald-600 font-bold mt-1 flex items-center gap-1">
            <TrendingUp className="w-3 h-3" />
            <span>56 attended out of 57 held</span>
          </p>
          <div className="mt-3 w-full bg-slate-100 rounded-full h-1.5 overflow-hidden">
            <div className="bg-emerald-500 h-1.5 rounded-full" style={{ width: "98.2%" }} />
          </div>
        </div>

        {/* Batch Rank */}
        <div className="bg-white rounded-3xl border border-slate-200/90 p-5 shadow-sm hover:shadow-md transition-shadow">
          <div className="flex items-center justify-between mb-3">
            <span className="text-xs font-bold text-slate-500 uppercase tracking-wider">
              Batch Standing
            </span>
            <div className="w-8 h-8 rounded-xl bg-amber-50 text-amber-600 border border-amber-200 flex items-center justify-center">
              <Award className="w-4 h-4" />
            </div>
          </div>
          <div className="text-2xl font-black text-slate-900 flex items-center gap-2">
            <span>Rank #1</span>
            <span className="text-xs font-bold px-2 py-0.5 rounded-full bg-amber-100 text-amber-800 border border-amber-300">
              Topper
            </span>
          </div>
          <p className="text-[11px] text-slate-500 font-medium mt-1">
            Out of strict 20 students in batch
          </p>
          <div className="mt-3 flex items-center gap-1 text-[10px] font-bold text-[#c99a5e]">
            <Sparkles className="w-3 h-3" />
            <span>Highest avg test score: 96.1%</span>
          </div>
        </div>

        {/* Pending Assignments */}
        <div className="bg-white rounded-3xl border border-slate-200/90 p-5 shadow-sm hover:shadow-md transition-shadow">
          <div className="flex items-center justify-between mb-3">
            <span className="text-xs font-bold text-slate-500 uppercase tracking-wider">
              Homework & DPPs
            </span>
            <div className="w-8 h-8 rounded-xl bg-red-50 text-[#c22329] border border-red-200 flex items-center justify-center">
              <FileText className="w-4 h-4" />
            </div>
          </div>
          <div className="text-2xl font-black text-slate-900">2 Due</div>
          <p className="text-[11px] text-red-600 font-bold mt-1">
            DPP #8 (Biology) due today 8:00 PM
          </p>
          <div className="mt-3 flex items-center justify-between text-[11px] text-slate-500">
            <span>Completed: 24</span>
            <Link href="/student/assignments" className="text-[#c22329] font-bold hover:underline">
              Submit Now →
            </Link>
          </div>
        </div>

        {/* Next Fee Installment */}
        <div className="bg-white rounded-3xl border border-slate-200/90 p-5 shadow-sm hover:shadow-md transition-shadow">
          <div className="flex items-center justify-between mb-3">
            <span className="text-xs font-bold text-slate-500 uppercase tracking-wider">
              Fee Status
            </span>
            <div className="w-8 h-8 rounded-xl bg-blue-50 text-blue-600 border border-blue-200 flex items-center justify-center">
              <CreditCard className="w-4 h-4" />
            </div>
          </div>
          <div className="text-2xl font-black text-slate-900">₹0 Overdue</div>
          <p className="text-[11px] text-emerald-600 font-bold mt-1">
            All current dues clear
          </p>
          <div className="mt-3 flex items-center justify-between text-[11px] text-slate-500">
            <span>Receipt #RCP-084</span>
            <Link href="/student/fees" className="text-blue-600 font-bold hover:underline">
              View Receipts →
            </Link>
          </div>
        </div>
      </div>

      {/* Main Grid: Today's Schedule & Academic Updates */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Today's Lectures Schedule (2 Cols) */}
        <div className="lg:col-span-2 bg-white rounded-3xl border border-slate-200/90 p-6 shadow-sm space-y-5">
          <div className="flex items-center justify-between pb-3 border-b border-slate-100">
            <div>
              <h2 className="text-base font-black text-slate-900 flex items-center gap-2">
                <Clock className="w-4 h-4 text-[#c22329]" />
                <span>Today's Lecture Schedule</span>
              </h2>
              <p className="text-xs text-slate-500 font-medium mt-0.5">
                Batch 12-BIO • 20 Seats Guaranteed • Hawa Bangla Campus
              </p>
            </div>
            <Link
              href="/student/timetable"
              className="text-xs font-bold text-[#c22329] hover:underline flex items-center gap-1"
            >
              <span>Weekly Timetable</span>
              <ArrowRight className="w-3 h-3" />
            </Link>
          </div>

          <div className="space-y-3">
            {scheduleToday.map((lec, idx) => (
              <div
                key={idx}
                className={`p-4 rounded-2xl border transition-all ${
                  lec.status === "UPCOMING_NEXT"
                    ? "bg-red-50/60 border-red-200 shadow-sm"
                    : lec.status === "COMPLETED"
                    ? "bg-slate-50/60 border-slate-200 opacity-75"
                    : "bg-white border-slate-200"
                }`}
              >
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
                  <div className="flex items-center gap-3">
                    <span className="text-xs font-extrabold text-slate-700 bg-white px-2.5 py-1 rounded-lg border border-slate-200 shadow-xs">
                      {lec.time}
                    </span>
                    <span
                      className={`text-xs font-black uppercase px-2 py-0.5 rounded ${
                        lec.subject === "Biology"
                          ? "bg-emerald-100 text-emerald-800"
                          : lec.subject === "Physics"
                          ? "bg-blue-100 text-blue-800"
                          : "bg-purple-100 text-purple-800"
                      }`}
                    >
                      {lec.subject}
                    </span>
                  </div>

                  <span
                    className={`text-[10px] font-black px-2 py-0.5 rounded-full border self-start sm:self-auto ${
                      lec.status === "UPCOMING_NEXT"
                        ? "bg-red-100 text-red-700 border-red-200 animate-pulse"
                        : lec.status === "COMPLETED"
                        ? "bg-slate-100 text-slate-500 border-slate-200"
                        : "bg-amber-50 text-amber-700 border-amber-200"
                    }`}
                  >
                    {lec.status === "UPCOMING_NEXT"
                      ? "Starting at 5:00 PM"
                      : lec.status === "COMPLETED"
                      ? "Attended (Present)"
                      : "Upcoming"}
                  </span>
                </div>

                <div className="mt-2.5">
                  <h3 className="text-sm font-bold text-slate-900">{lec.topic}</h3>
                  <div className="flex flex-wrap items-center gap-3 mt-1.5 text-xs text-slate-500 font-medium">
                    <span className="flex items-center gap-1 text-slate-700">
                      <Users className="w-3.5 h-3.5 text-slate-400" />
                      {lec.faculty}
                    </span>
                    <span>•</span>
                    <span className="flex items-center gap-1 text-slate-600">
                      <MapPin className="w-3.5 h-3.5 text-[#c99a5e]" />
                      {lec.room}
                    </span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Noticeboard & Direct Faculty Access (1 Col) */}
        <div className="space-y-6">
          {/* Institutional Noticeboard */}
          <div className="bg-white rounded-3xl border border-slate-200/90 p-6 shadow-sm space-y-4">
            <h2 className="text-sm font-black text-slate-900 uppercase tracking-wider flex items-center gap-2">
              <Sparkles className="w-4 h-4 text-[#c99a5e]" />
              <span>Campus Announcements</span>
            </h2>

            <div className="space-y-3">
              <div className="p-3.5 rounded-2xl bg-amber-50/70 border border-amber-200/80 space-y-1">
                <span className="text-[10px] font-black uppercase text-amber-800 bg-amber-100 px-1.5 py-0.5 rounded">
                  Director's Desk
                </span>
                <h4 className="text-xs font-bold text-slate-900 mt-1">
                  Board Pre-Test Simulation #1 Announced
                </h4>
                <p className="text-[11px] text-slate-600 leading-relaxed font-normal">
                  Class 12th Board-pattern subjective examination will be conducted on 28th September. Syllabus available in Doubt Clinic.
                </p>
                <span className="text-[10px] text-slate-400 font-bold block pt-1">
                  By Mrs. Shobhna Vyas (Director)
                </span>
              </div>

              <div className="p-3.5 rounded-2xl bg-slate-50 border border-slate-200 space-y-1">
                <span className="text-[10px] font-black uppercase text-blue-700 bg-blue-50 px-1.5 py-0.5 rounded">
                  Faculty Clinic
                </span>
                <h4 className="text-xs font-bold text-slate-900 mt-1">
                  1-on-1 Biology Doubt Counter Open
                </h4>
                <p className="text-[11px] text-slate-600 leading-relaxed font-normal">
                  Mr. Pankaj Dubey will be available in Faculty Cabin A on Saturday between 3:00 PM and 4:30 PM for Genetics numericals.
                </p>
              </div>
            </div>
          </div>

          {/* Quick Support Card */}
          <div className="p-5 rounded-3xl bg-gradient-to-br from-[#c22329] to-red-800 text-white shadow-md space-y-3">
            <div className="flex items-center gap-2">
              <div className="w-7 h-7 rounded-lg bg-white/20 flex items-center justify-center">
                <HelpCircle className="w-4 h-4 text-white" />
              </div>
              <h3 className="text-sm font-black tracking-tight">Need Academic Help?</h3>
            </div>
            <p className="text-xs text-red-100 font-normal leading-relaxed">
              Stuck on numericals or need leave approval? Reach out directly to your batch counselor or coordinator.
            </p>
            <div className="pt-1 flex gap-2">
              <Link
                href="/student/doubts"
                className="w-full text-center py-2 px-3 rounded-xl bg-white text-[#c22329] hover:bg-slate-50 font-bold text-xs shadow-xs transition-colors"
              >
                Book Doubt Slot
              </Link>
            </div>
          </div>
        </div>
      </div>

      {/* Recent Test Performance Ledger */}
      <div className="bg-white rounded-3xl border border-slate-200/90 p-6 shadow-sm space-y-4">
        <div className="flex items-center justify-between pb-3 border-b border-slate-100">
          <div>
            <h2 className="text-base font-black text-slate-900 flex items-center gap-2">
              <Award className="w-4 h-4 text-[#c99a5e]" />
              <span>Recent Test Scores & Distinction Ledger</span>
            </h2>
            <p className="text-xs text-slate-500 font-medium mt-0.5">
              Weekly Board & NEET Pattern Assessments
            </p>
          </div>
          <Link
            href="/student/results"
            className="text-xs font-bold text-[#c22329] hover:underline flex items-center gap-1"
          >
            <span>Complete Report Card</span>
            <ArrowRight className="w-3 h-3" />
          </Link>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs border-collapse">
            <thead>
              <tr className="bg-slate-50 border-b border-slate-200 text-slate-500 uppercase text-[10px] font-extrabold tracking-wider">
                <th className="py-3 px-4">Test Title & Date</th>
                <th className="py-3 px-4">Subject & Scope</th>
                <th className="py-3 px-4">Marks Obtained</th>
                <th className="py-3 px-4">Percentage</th>
                <th className="py-3 px-4">Batch Rank</th>
                <th className="py-3 px-4 text-right">Certificate</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 font-medium text-slate-700">
              {recentTests.map((test, idx) => (
                <tr key={idx} className="hover:bg-slate-50/70 transition-colors">
                  <td className="py-3.5 px-4 font-bold text-slate-900">
                    <div>{test.name}</div>
                    <div className="text-[10px] text-slate-400 font-normal">{test.date}</div>
                  </td>
                  <td className="py-3.5 px-4 text-slate-600">{test.subject}</td>
                  <td className="py-3.5 px-4 font-black text-slate-900 text-sm">
                    {test.marks}
                  </td>
                  <td className="py-3.5 px-4">
                    <span className="font-bold text-emerald-600">{test.percent}</span>
                  </td>
                  <td className="py-3.5 px-4">
                    <span className="px-2.5 py-1 rounded-full bg-amber-50 text-amber-800 border border-amber-200 text-[10px] font-black inline-flex items-center gap-1">
                      <Sparkles className="w-3 h-3 text-amber-500" />
                      {test.rank}
                    </span>
                  </td>
                  <td className="py-3.5 px-4 text-right">
                    <Link
                      href="/student/results"
                      className="inline-flex items-center gap-1 text-[11px] font-bold text-[#c22329] hover:underline"
                    >
                      <Download className="w-3 h-3" />
                      <span>Report Slip</span>
                    </Link>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
