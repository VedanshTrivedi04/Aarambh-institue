"use client";

import React, { useState } from "react";
import Link from "next/link";
import {
  Users,
  CalendarCheck,
  Award,
  HelpCircle,
  Clock,
  Sparkles,
  ArrowRight,
  CheckCircle2,
  BookOpen,
  FileText,
  AlertCircle,
  Trophy,
  Calendar,
} from "lucide-react";

export default function TeacherDashboardPage() {
  const [activeTab, setActiveTab] = useState<"schedule" | "toppers">("schedule");

  return (
    <div className="space-y-6">
      {/* Educator Greeting Banner */}
      <div className="bg-white p-6 sm:p-7 rounded-3xl border border-slate-200/90 shadow-sm flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-red-50 text-[#c22329] border border-red-200 text-xs font-bold mb-2">
            <Sparkles className="w-3.5 h-3.5 text-[#c99a5e]" />
            <span>Senior Biology & Medical Faculty Desk</span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-black text-slate-900">
            Welcome, Mr. Pankaj Dubey
          </h1>
          <p className="text-xs sm:text-sm text-slate-600 mt-1">
            M.Sc Biology • 30 Years Legacy • Hawa Bangla Campus • All 3 batches operating at full small-batch capacity.
          </p>
        </div>

        <div className="flex flex-wrap items-center gap-2.5">
          <Link
            href="/teacher/attendance"
            className="btn-caramel-gold inline-flex items-center gap-2 px-4 py-2.5 rounded-xl font-bold text-xs shadow-md"
          >
            <CalendarCheck className="w-3.5 h-3.5" />
            <span>Mark Lecture Attendance</span>
          </Link>

          <Link
            href="/teacher/assignments"
            className="inline-flex items-center gap-2 px-4 py-2.5 rounded-xl font-bold text-xs bg-slate-100 hover:bg-slate-200/80 text-slate-700 border border-slate-200 transition-colors"
          >
            <FileText className="w-3.5 h-3.5 text-[#c22329]" />
            <span>Post New DPP / Homework</span>
          </Link>
        </div>
      </div>

      {/* Educator KPI Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Card 1: Active Batches */}
        <div className="bg-white p-5 rounded-3xl border border-slate-200/90 shadow-sm space-y-3">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold text-slate-500">My Batches</span>
            <div className="w-8 h-8 rounded-xl bg-red-50 text-[#c22329] border border-red-200 flex items-center justify-center">
              <BookOpen className="w-4 h-4" />
            </div>
          </div>
          <div className="text-2xl font-black text-slate-900">3 Batches</div>
          <div className="flex items-center gap-1.5 text-[11px] text-emerald-700 font-bold bg-emerald-50 border border-emerald-200/60 px-2 py-0.5 rounded-full w-fit">
            <span>Class 11th, 12th & NEET</span>
          </div>
        </div>

        {/* Card 2: Students Mentored */}
        <div className="bg-white p-5 rounded-3xl border border-slate-200/90 shadow-sm space-y-3">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold text-slate-500">Students Mentored</span>
            <div className="w-8 h-8 rounded-xl bg-blue-50 text-blue-600 border border-blue-200 flex items-center justify-center">
              <Users className="w-4 h-4" />
            </div>
          </div>
          <div className="text-2xl font-black text-slate-900">57 Students</div>
          <div className="flex items-center gap-1.5 text-[11px] text-blue-700 font-bold bg-blue-50 border border-blue-200/60 px-2 py-0.5 rounded-full w-fit">
            <span>Strict Max 20 Limit</span>
          </div>
        </div>

        {/* Card 3: Attendance Rate */}
        <div className="bg-white p-5 rounded-3xl border border-slate-200/90 shadow-sm space-y-3">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold text-slate-500">Today&apos;s Attendance</span>
            <div className="w-8 h-8 rounded-xl bg-emerald-50 text-emerald-600 border border-emerald-200 flex items-center justify-center">
              <CalendarCheck className="w-4 h-4" />
            </div>
          </div>
          <div className="text-2xl font-black text-slate-900">98.1%</div>
          <div className="flex items-center gap-1.5 text-[11px] text-emerald-700 font-bold bg-emerald-50 border border-emerald-200/60 px-2 py-0.5 rounded-full w-fit">
            <CheckCircle2 className="w-3.5 h-3.5" />
            <span>56 of 57 Attending</span>
          </div>
        </div>

        {/* Card 4: Doubts Pending */}
        <div className="bg-white p-5 rounded-3xl border border-slate-200/90 shadow-sm space-y-3">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold text-slate-500">Doubt Tickets</span>
            <div className="w-8 h-8 rounded-xl bg-amber-50 text-[#c99a5e] border border-amber-200 flex items-center justify-center">
              <HelpCircle className="w-4 h-4" />
            </div>
          </div>
          <div className="text-2xl font-black text-slate-900">4 Pending</div>
          <div className="flex items-center gap-1.5 text-[11px] text-amber-800 font-bold bg-amber-50 border border-amber-200/60 px-2 py-0.5 rounded-full w-fit">
            <AlertCircle className="w-3.5 h-3.5" />
            <span>Clinic at 7:30 PM</span>
          </div>
        </div>
      </div>

      {/* Main Grid: Today's Schedule & Toppers Roll */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left Column: Today's Schedule & Lesson Plan (8 cols) */}
        <div className="lg:col-span-8 bg-white rounded-3xl border border-slate-200/90 p-6 space-y-5 shadow-sm">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-base font-bold text-slate-900">
                Today&apos;s Lectures & Lesson Progression
              </h2>
              <p className="text-xs text-slate-500">
                Live timetable for Tuesday, 22 September 2026 • Hawa Bangla Academic Building
              </p>
            </div>
            <span className="text-[10px] font-bold px-2.5 py-1 rounded-full bg-emerald-50 text-emerald-700 border border-emerald-200 flex items-center gap-1">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-ping" />
              <span>Campus Active</span>
            </span>
          </div>

          <div className="space-y-3.5">
            {/* Lecture 1 */}
            <div className="p-4 rounded-2xl bg-slate-50/80 border border-slate-200/80 space-y-3 hover:border-slate-300 transition-colors">
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
                <div className="flex items-center gap-2.5">
                  <span className="px-2.5 py-1 rounded-lg bg-red-50 text-[#c22329] border border-red-200 text-xs font-black">
                    5:00 PM - 6:30 PM
                  </span>
                  <span className="text-xs font-bold text-slate-900">
                    Class 12th Senior Biology (Board + Diagnostic)
                  </span>
                </div>
                <div className="flex items-center gap-2 text-xs">
                  <span className="text-slate-500 font-semibold">Room 201</span>
                  <span className="font-bold text-emerald-700 bg-emerald-50 px-2 py-0.5 rounded border border-emerald-200/60">
                    19 / 20 Enrolled
                  </span>
                </div>
              </div>

              <div className="text-xs text-slate-700 bg-white p-3 rounded-xl border border-slate-200/60 space-y-1">
                <div className="font-bold text-slate-900 flex items-center gap-1.5">
                  <BookOpen className="w-3.5 h-3.5 text-[#c22329]" />
                  <span>Topic: Human Circulatory System — Cardiac Cycle & ECG Waves</span>
                </div>
                <p className="text-slate-500 text-[11px]">
                  Coverage: NCERT Chapter 18 + MP Board numericals + NEET past 10-year MCQs.
                </p>
              </div>

              <div className="flex items-center justify-between pt-1">
                <span className="text-[11px] text-slate-500 font-medium">
                  DPP #14 due for collection
                </span>
                <Link
                  href="/teacher/attendance"
                  className="text-xs font-bold text-[#c22329] hover:underline flex items-center gap-1"
                >
                  <span>Mark Attendance</span>
                  <ArrowRight className="w-3.5 h-3.5" />
                </Link>
              </div>
            </div>

            {/* Lecture 2 */}
            <div className="p-4 rounded-2xl bg-slate-50/80 border border-slate-200/80 space-y-3 hover:border-slate-300 transition-colors">
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
                <div className="flex items-center gap-2.5">
                  <span className="px-2.5 py-1 rounded-lg bg-amber-50 text-amber-800 border border-amber-200 text-xs font-black">
                    6:30 PM - 7:30 PM
                  </span>
                  <span className="text-xs font-bold text-slate-900">
                    NEET Medical Specialist Foundation Batch
                  </span>
                </div>
                <div className="flex items-center gap-2 text-xs">
                  <span className="text-slate-500 font-semibold">Room 201</span>
                  <span className="font-bold text-amber-800 bg-amber-50 px-2 py-0.5 rounded border border-amber-200">
                    20 / 20 Full
                  </span>
                </div>
              </div>

              <div className="text-xs text-slate-700 bg-white p-3 rounded-xl border border-slate-200/60 space-y-1">
                <div className="font-bold text-slate-900 flex items-center gap-1.5">
                  <BookOpen className="w-3.5 h-3.5 text-[#c22329]" />
                  <span>Topic: Principles of Inheritance & Variation — Chromosomal Theory</span>
                </div>
                <p className="text-slate-500 text-[11px]">
                  Coverage: Pedigree charts, Morgan linkage experiments, and high-yield diagram practice.
                </p>
              </div>

              <div className="flex items-center justify-between pt-1">
                <span className="text-[11px] text-slate-500 font-medium">
                  Model Test papers to be handed out
                </span>
                <Link
                  href="/teacher/exams"
                  className="text-xs font-bold text-[#c22329] hover:underline flex items-center gap-1"
                >
                  <span>View Test Registry</span>
                  <ArrowRight className="w-3.5 h-3.5" />
                </Link>
              </div>
            </div>

            {/* Lecture 3 */}
            <div className="p-4 rounded-2xl bg-slate-50/80 border border-slate-200/80 space-y-3 hover:border-slate-300 transition-colors">
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
                <div className="flex items-center gap-2.5">
                  <span className="px-2.5 py-1 rounded-lg bg-blue-50 text-blue-700 border border-blue-200 text-xs font-black">
                    7:30 PM - 8:15 PM
                  </span>
                  <span className="text-xs font-bold text-slate-900">
                    1-on-1 Student Doubt Clearing Clinic
                  </span>
                </div>
                <div className="flex items-center gap-2 text-xs">
                  <span className="text-slate-500 font-semibold">Faculty Room A</span>
                  <span className="font-bold text-blue-700 bg-blue-50 px-2 py-0.5 rounded border border-blue-200/60">
                    4 Students Slotted
                  </span>
                </div>
              </div>

              <p className="text-xs text-slate-600 bg-white p-3 rounded-xl border border-slate-200/60">
                Dedicated personal attention for weak numerical questions and diagram clarification.
              </p>

              <div className="flex items-center justify-between pt-1">
                <span className="text-[11px] text-slate-500 font-medium">
                  Rohit, Monika, Dhruvika & Neha booked
                </span>
                <Link
                  href="/teacher/doubts"
                  className="text-xs font-bold text-[#c22329] hover:underline flex items-center gap-1"
                >
                  <span>Open Doubt Queue</span>
                  <ArrowRight className="w-3.5 h-3.5" />
                </Link>
              </div>
            </div>
          </div>
        </div>

        {/* Right Column: Toppers & Quick Actions (4 cols) */}
        <div className="lg:col-span-4 space-y-5">
          {/* Recent Mock Test Toppers */}
          <div className="bg-white rounded-3xl border border-slate-200/90 p-6 space-y-4 shadow-sm">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <Trophy className="w-4 h-4 text-[#c99a5e]" />
                <h3 className="text-sm font-bold text-slate-900">Biology Mock Toppers</h3>
              </div>
              <span className="text-[10px] font-bold text-slate-500">20 Sep Test</span>
            </div>

            <div className="space-y-3">
              <div className="p-3 rounded-2xl bg-amber-50/60 border border-amber-200/60 flex items-center justify-between">
                <div>
                  <span className="block font-bold text-xs text-slate-900">
                    Prince Yadav
                  </span>
                  <span className="block text-[10px] text-slate-500">
                    Class 12th • Rank 1st
                  </span>
                </div>
                <div className="text-right">
                  <span className="font-mono text-sm font-black text-amber-800">
                    348 / 360
                  </span>
                  <span className="block text-[9px] font-bold text-emerald-700">
                    96.6% A+
                  </span>
                </div>
              </div>

              <div className="p-3 rounded-2xl bg-slate-50 border border-slate-200/80 flex items-center justify-between">
                <div>
                  <span className="block font-bold text-xs text-slate-900">
                    Monika Patidar
                  </span>
                  <span className="block text-[10px] text-slate-500">
                    Class 12th • Rank 2nd
                  </span>
                </div>
                <div className="text-right">
                  <span className="font-mono text-sm font-black text-slate-900">
                    332 / 360
                  </span>
                  <span className="block text-[9px] font-bold text-emerald-700">
                    92.2% A+
                  </span>
                </div>
              </div>

              <div className="p-3 rounded-2xl bg-slate-50 border border-slate-200/80 flex items-center justify-between">
                <div>
                  <span className="block font-bold text-xs text-slate-900">
                    Rohit Garg
                  </span>
                  <span className="block text-[10px] text-slate-500">
                    Class 10th Science • Rank 1st
                  </span>
                </div>
                <div className="text-right">
                  <span className="font-mono text-sm font-black text-slate-900">
                    96 / 100
                  </span>
                  <span className="block text-[9px] font-bold text-emerald-700">
                    96.0% A+
                  </span>
                </div>
              </div>
            </div>

            <Link
              href="/teacher/exams"
              className="block text-center text-xs font-bold text-[#c22329] hover:underline pt-1"
            >
              Enter Marks for Next Test →
            </Link>
          </div>

          {/* Quick Academic Tools */}
          <div className="bg-white rounded-3xl border border-slate-200/90 p-6 space-y-3.5 shadow-sm">
            <h3 className="text-sm font-bold text-slate-900">Quick Faculty Desk</h3>

            <div className="space-y-2">
              <Link
                href="/teacher/batches"
                className="flex items-center justify-between p-3 rounded-xl bg-slate-50 hover:bg-slate-100/80 border border-slate-200/80 text-xs font-bold text-slate-700 transition-colors"
              >
                <div className="flex items-center gap-2.5">
                  <Users className="w-4 h-4 text-[#c22329]" />
                  <span>View Student Roster</span>
                </div>
                <span className="text-[10px] text-slate-500">57 Students</span>
              </Link>

              <Link
                href="/teacher/assignments"
                className="flex items-center justify-between p-3 rounded-xl bg-slate-50 hover:bg-slate-100/80 border border-slate-200/80 text-xs font-bold text-slate-700 transition-colors"
              >
                <div className="flex items-center gap-2.5">
                  <FileText className="w-4 h-4 text-[#c99a5e]" />
                  <span>Assignments & DPPs</span>
                </div>
                <span className="text-[10px] text-slate-500">3 Active</span>
              </Link>

              <Link
                href="/teacher/syllabus"
                className="flex items-center justify-between p-3 rounded-xl bg-slate-50 hover:bg-slate-100/80 border border-slate-200/80 text-xs font-bold text-slate-700 transition-colors"
              >
                <div className="flex items-center gap-2.5">
                  <BookOpen className="w-4 h-4 text-blue-600" />
                  <span>Syllabus Roadmap</span>
                </div>
                <span className="text-[10px] text-slate-500">72% Done</span>
              </Link>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
