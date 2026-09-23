import React from "react";
import Link from "next/link";
import { getLandingData } from "@/lib/api";
import ProgramsSection from "@/components/landing/ProgramsSection";
import {
  BookOpen,
  CheckCircle2,
  Clock,
  Users,
  Award,
  Sparkles,
  ArrowRight,
  ShieldCheck,
  FileCheck,
  Phone,
} from "lucide-react";

export const metadata = {
  title: "Courses & Fee Structure | Aarambh Institute Indore | Classes 4th to 12th & Degree",
  description:
    "Explore coaching programs at Aarambh Institute Indore for MP Board, CBSE & ICSE: Middle School 4th-8th (₹800/mo), High School 9th-12th (Science PCM/PCB & Commerce), and College Degrees (B.Com, M.Com, BBA).",
};

export default async function CoursesPage() {
  const data = await getLandingData();

  return (
    <div className="bg-[#f8fafd] text-slate-900 pb-20">
      {/* Page Header */}
      <section className="relative bg-gradient-to-b from-white via-slate-50 to-[#f8fafd] border-b border-slate-200/80 pt-10 pb-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center gap-2 text-xs font-bold text-slate-500 mb-4">
            <Link href="/" className="hover:text-[#c22329] transition-colors">
              Home
            </Link>
            <span>/</span>
            <span className="text-[#c22329]">Courses & Programs</span>
          </div>

          <div className="max-w-3xl space-y-4">
            <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-blue-50 border border-blue-200 text-blue-700 text-xs font-bold uppercase tracking-wider">
              <BookOpen className="w-3.5 h-3.5" />
              <span>Comprehensive Curriculums • MP Board, CBSE & ICSE</span>
            </div>

            <h1 className="text-3xl sm:text-5xl font-black text-slate-900 tracking-tight leading-tight">
              Academic Programs & <br />
              <span className="text-[#c22329]">Student-Friendly Fees</span>
            </h1>

            <p className="text-base sm:text-lg text-slate-600 leading-relaxed">
              Tailored coaching programs designed to give students strong academic foundations, exam confidence, and top board ranks. Taught in small batches of max 20 students.
            </p>
          </div>

          {/* Quick Curriculum Tags */}
          <div className="flex flex-wrap gap-2.5 mt-8">
            <span className="px-3.5 py-1.5 rounded-xl bg-white border border-slate-200 text-xs font-bold text-slate-700 shadow-sm">
              🎯 MP Board State Syllabus
            </span>
            <span className="px-3.5 py-1.5 rounded-xl bg-white border border-slate-200 text-xs font-bold text-slate-700 shadow-sm">
              📘 CBSE NCERT Curriculum
            </span>
            <span className="px-3.5 py-1.5 rounded-xl bg-white border border-slate-200 text-xs font-bold text-slate-700 shadow-sm">
              🔬 ICSE Board Standard
            </span>
            <span className="px-3.5 py-1.5 rounded-xl bg-white border border-slate-200 text-xs font-bold text-slate-700 shadow-sm">
              💼 Commerce & Management Degrees
            </span>
          </div>
        </div>
      </section>

      {/* Main Interactive Programs Section */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-6">
        <ProgramsSection courses={data.courses} />
      </div>

      {/* Program Comparison & Batch Guarantees Table */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="bg-white rounded-3xl p-8 sm:p-10 border border-slate-200 shadow-sm space-y-6">
          <div className="space-y-2">
            <span className="text-xs font-extrabold uppercase tracking-wider text-[#c22329]">
              Standardized Quality
            </span>
            <h2 className="text-2xl sm:text-3xl font-black text-slate-900">
              What Every Aarambh Batch Includes
            </h2>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 pt-4">
            <div className="p-5 rounded-2xl bg-slate-50 border border-slate-100 space-y-2">
              <div className="w-10 h-10 rounded-xl bg-red-100 text-[#c22329] flex items-center justify-center font-bold">
                <Users className="w-5 h-5" />
              </div>
              <h3 className="font-bold text-sm text-slate-900">Strict 20-Student Limit</h3>
              <p className="text-xs text-slate-600 leading-relaxed">
                No overcrowded halls. Every teacher knows every student by name and tracks their daily homework and test performance.
              </p>
            </div>

            <div className="p-5 rounded-2xl bg-slate-50 border border-slate-100 space-y-2">
              <div className="w-10 h-10 rounded-xl bg-blue-100 text-blue-700 flex items-center justify-center font-bold">
                <FileCheck className="w-5 h-5" />
              </div>
              <h3 className="font-bold text-sm text-slate-900">Weekly Assessment Tests</h3>
              <p className="text-xs text-slate-600 leading-relaxed">
                Topic-wise tests every weekend. Evaluated answer copies are shared with parents with targeted suggestions for marks improvement.
              </p>
            </div>

            <div className="p-5 rounded-2xl bg-slate-50 border border-slate-100 space-y-2">
              <div className="w-10 h-10 rounded-xl bg-amber-100 text-amber-800 flex items-center justify-center font-bold">
                <Clock className="w-5 h-5" />
              </div>
              <h3 className="font-bold text-sm text-slate-900">Dedicated Doubt Clinics</h3>
              <p className="text-xs text-slate-600 leading-relaxed">
                Daily evening doubt resolution slots with senior faculty. Zero doubts carry over to the next day.
              </p>
            </div>

            <div className="p-5 rounded-2xl bg-slate-50 border border-slate-100 space-y-2">
              <div className="w-10 h-10 rounded-xl bg-emerald-100 text-emerald-700 flex items-center justify-center font-bold">
                <Award className="w-5 h-5" />
              </div>
              <h3 className="font-bold text-sm text-slate-900">Printed Study Booklets</h3>
              <p className="text-xs text-slate-600 leading-relaxed">
                Concise, high-yield formula sheets, chapter notes, and past 10 years solved board question banks provided to every enrolled student.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Free Demo Banner */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        <div className="rounded-3xl bg-gradient-to-r from-red-900 via-[#991b1b] to-red-950 text-white p-8 sm:p-10 shadow-xl flex flex-col md:flex-row items-center justify-between gap-6">
          <div className="space-y-2 max-w-2xl">
            <span className="text-xs font-bold uppercase tracking-wider text-amber-300">
              Not sure which batch fits best?
            </span>
            <h3 className="text-2xl sm:text-3xl font-black text-white">
              Attend 2 Days Of Free Trial Classes
            </h3>
            <p className="text-xs sm:text-sm text-red-100 leading-relaxed">
              Experience the teaching quality, interact with HODs, and evaluate our batch environment before taking admission.
            </p>
          </div>

          <Link
            href="/admissions"
            className="btn-caramel-gold shrink-0 inline-flex items-center gap-2 px-6 py-3.5 rounded-xl font-bold text-sm shadow-lg hover:scale-105 transition-transform"
          >
            <span>Register For Free Demo</span>
            <ArrowRight className="w-4 h-4" />
          </Link>
        </div>
      </section>
    </div>
  );
}
