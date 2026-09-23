import React from "react";
import Link from "next/link";
import { getLandingData } from "@/lib/api";
import FacultySection from "@/components/landing/FacultySection";
import {
  GraduationCap,
  Users,
  Award,
  Sparkles,
  ArrowRight,
  Clock,
  CheckCircle2,
  BookOpen,
  MessageSquare,
} from "lucide-react";

export const metadata = {
  title: "Faculty Members | Aarambh Institute Indore | Veteran Educators",
  description:
    "Meet the experienced educators of Aarambh Institute in Indore: Mr. Pankaj Dubey (30y Biology), Mr. Jitendra Shindey (30y Commerce), Mrs. Shobhna Vyas (20y Maths/Science), Mr. Vishal Rathore, Mrs. Anita Holkar & more.",
};

export default async function FacultyPage() {
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
            <span className="text-[#c22329]">Faculty</span>
          </div>

          <div className="max-w-3xl space-y-4">
            <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-amber-50 border border-amber-200 text-amber-800 text-xs font-bold uppercase tracking-wider">
              <Users className="w-3.5 h-3.5" />
              <span>Veteran Educators & Subject Heads</span>
            </div>

            <h1 className="text-3xl sm:text-5xl font-black text-slate-900 tracking-tight leading-tight">
              Mentorship By Senior Educators <br />
              <span className="text-[#c22329]">With Up to 30 Years Legacy</span>
            </h1>

            <p className="text-base sm:text-lg text-slate-600 leading-relaxed">
              Great teachers don&apos;t just cover the syllabus — they demystify difficult concepts, instill exam temperament, and turn fearful students into top rankers.
            </p>
          </div>

          {/* Quick Stats Grid */}
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 mt-8">
            <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm flex items-center gap-4">
              <div className="w-12 h-12 rounded-xl bg-red-100 text-[#c22329] flex items-center justify-center font-black text-lg shrink-0">
                30Y
              </div>
              <div>
                <h3 className="text-sm font-bold text-slate-900">Highest Faculty Experience</h3>
                <p className="text-xs text-slate-500">Decades of board pattern mastery</p>
              </div>
            </div>

            <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm flex items-center gap-4">
              <div className="w-12 h-12 rounded-xl bg-blue-100 text-blue-700 flex items-center justify-center font-black text-lg shrink-0">
                100%
              </div>
              <div>
                <h3 className="text-sm font-bold text-slate-900">Dedicated Full-Time Mentors</h3>
                <p className="text-xs text-slate-500">Accessible daily for doubt solving</p>
              </div>
            </div>

            <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm flex items-center gap-4">
              <div className="w-12 h-12 rounded-xl bg-emerald-100 text-emerald-700 flex items-center justify-center font-black text-lg shrink-0">
                20 Max
              </div>
              <div>
                <h3 className="text-sm font-bold text-slate-900">Students Per Faculty Batch</h3>
                <p className="text-xs text-slate-500">Direct 1:1 personal attention</p>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Main Faculty Cards */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-6">
        <FacultySection faculty={data.faculty} />
      </div>

      {/* Teaching Philosophy */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="bg-white rounded-3xl p-8 sm:p-12 border border-slate-200 shadow-sm space-y-8">
          <div className="max-w-2xl space-y-2">
            <span className="text-xs font-bold uppercase tracking-wider text-[#c22329]">
              Academic Methodology
            </span>
            <h2 className="text-2xl sm:text-3xl font-black text-slate-900">
              How Our Faculty Prepares Students For Board Exams
            </h2>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="p-6 rounded-2xl bg-slate-50 border border-slate-100 space-y-3">
              <div className="w-10 h-10 rounded-xl bg-red-100 text-[#c22329] flex items-center justify-center font-bold">
                1
              </div>
              <h3 className="text-base font-bold text-slate-900">Root Concept Clarity</h3>
              <p className="text-xs text-slate-600 leading-relaxed">
                Rather than memorizing standard steps, every formula, theorem, and accounting principle is broken down with practical real-life examples until students gain intuitive understanding.
              </p>
            </div>

            <div className="p-6 rounded-2xl bg-slate-50 border border-slate-100 space-y-3">
              <div className="w-10 h-10 rounded-xl bg-blue-100 text-blue-700 flex items-center justify-center font-bold">
                2
              </div>
              <h3 className="text-base font-bold text-slate-900">Board Answer-Writing Drills</h3>
              <p className="text-xs text-slate-600 leading-relaxed">
                Senior evaluators coach students on presentation, diagram labeling, step marking, and time management for MP Board, CBSE, and ICSE examinations.
              </p>
            </div>

            <div className="p-6 rounded-2xl bg-slate-50 border border-slate-100 space-y-3">
              <div className="w-10 h-10 rounded-xl bg-emerald-100 text-emerald-700 flex items-center justify-center font-bold">
                3
              </div>
              <h3 className="text-base font-bold text-slate-900">Zero Fear & Open Doubts</h3>
              <p className="text-xs text-slate-600 leading-relaxed">
                Our classrooms foster an open, question-friendly environment. Hesitant students receive individual encouragement during daily post-lecture clinics.
              </p>
            </div>
          </div>

          <div className="pt-6 border-t border-slate-100 flex flex-col sm:flex-row items-center justify-between gap-4">
            <div className="flex items-center gap-2 text-sm font-semibold text-slate-700">
              <MessageSquare className="w-4 h-4 text-[#c22329]" />
              <span>Want to consult our faculty regarding your child&apos;s stream or syllabus?</span>
            </div>

            <Link
              href="/admissions"
              className="btn-caramel-gold inline-flex items-center gap-2 px-6 py-2.5 rounded-xl font-bold text-xs shadow-md"
            >
              <span>Book Teacher Counseling Session</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </Link>
          </div>
        </div>
      </section>
    </div>
  );
}
