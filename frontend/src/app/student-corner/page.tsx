import React from "react";
import Link from "next/link";
import StudentResources from "@/components/landing/StudentResources";
import ScholarshipSection from "@/components/landing/ScholarshipSection";
import {
  FileText,
  Download,
  Calendar,
  Bell,
  Sparkles,
  HelpCircle,
  ArrowRight,
  BookOpen,
} from "lucide-react";

export const metadata = {
  title: "Student Corner & Study Materials | Aarambh Institute Indore",
  description:
    "Free formula booklets, board model question papers, notices, academic holiday calendar, and scholarship tests for Aarambh Institute students in Indore.",
};

export default function StudentCornerPage() {
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
            <span className="text-[#c22329]">Student Corner</span>
          </div>

          <div className="max-w-3xl space-y-4">
            <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-purple-50 border border-purple-200 text-purple-800 text-xs font-bold uppercase tracking-wider">
              <FileText className="w-3.5 h-3.5" />
              <span>Free Academic Hub & Downloads</span>
            </div>

            <h1 className="text-3xl sm:text-5xl font-black text-slate-900 tracking-tight leading-tight">
              Study Materials, Notices & <br />
              <span className="text-[#c22329]">Academic Resources</span>
            </h1>

            <p className="text-base sm:text-lg text-slate-600 leading-relaxed">
              Access free formula sheets, sample board question papers, live test announcements, academic calendars, and career aptitude assessments.
            </p>
          </div>
        </div>
      </section>

      {/* Main Student Resources Component */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-6">
        <StudentResources />
      </div>

      {/* Aarambh Scholarship Test Section */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-10">
        <ScholarshipSection />
      </div>
    </div>
  );
}
