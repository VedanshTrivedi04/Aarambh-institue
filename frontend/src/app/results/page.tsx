import React from "react";
import Link from "next/link";
import { getLandingData } from "@/lib/api";
import ResultsSection from "@/components/landing/ResultsSection";
import TestimonialsSection from "@/components/landing/TestimonialsSection";
import {
  Award,
  Trophy,
  Star,
  CheckCircle2,
  Sparkles,
  ArrowRight,
  TrendingUp,
  GraduationCap,
} from "lucide-react";

export const metadata = {
  title: "Results & Toppers | Aarambh Institute Indore | Board Rankers",
  description:
    "Explore the board examination results and Hall of Fame of Aarambh Institute, Indore. Prince (94% Class 12th 1st Rank), Rohit Garg (91%), Payal Sharma (89%) and 98% overall board pass rate.",
};

export default async function ResultsPage() {
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
            <span className="text-[#c22329]">Results & Toppers</span>
          </div>

          <div className="max-w-3xl space-y-4">
            <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-emerald-50 border border-emerald-200 text-emerald-800 text-xs font-bold uppercase tracking-wider">
              <Trophy className="w-3.5 h-3.5 text-amber-500" />
              <span>Proven Track Record • 2015 to 2026</span>
            </div>

            <h1 className="text-3xl sm:text-5xl font-black text-slate-900 tracking-tight leading-tight">
              Aarambh Hall of Fame & <br />
              <span className="text-[#c22329]">Board Exam Rankers</span>
            </h1>

            <p className="text-base sm:text-lg text-slate-600 leading-relaxed">
              Real hard work, rigorous weekly mock tests, and personal attention produce extraordinary results year after year in MP Board, CBSE, and ICSE examinations.
            </p>
          </div>

          {/* Quick Metrics Bar */}
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 mt-10">
            <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm">
              <div className="text-3xl font-black text-[#c22329]">98.5%</div>
              <div className="text-xs font-semibold text-slate-500 mt-1">
                Highest Board Score
              </div>
            </div>
            <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm">
              <div className="text-3xl font-black text-emerald-700">98%</div>
              <div className="text-xs font-semibold text-slate-500 mt-1">
                Overall Board Pass Rate
              </div>
            </div>
            <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm">
              <div className="text-3xl font-black text-blue-700">85%+</div>
              <div className="text-xs font-semibold text-slate-500 mt-1">
                Average Batch Score
              </div>
            </div>
            <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm">
              <div className="text-3xl font-black text-amber-600">2,000+</div>
              <div className="text-xs font-semibold text-slate-500 mt-1">
                Alumni Across Indore
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Main Results Section (Interactive Toppers + Roll) */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-6">
        <ResultsSection />
      </div>

      {/* Testimonials from Students & Parents */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-8">
        <TestimonialsSection />
      </div>

      {/* Enroll For Top Ranks CTA */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10">
        <div className="rounded-3xl bg-gradient-to-r from-slate-900 via-slate-800 to-slate-900 text-white p-8 sm:p-12 border border-slate-700 flex flex-col md:flex-row items-center justify-between gap-6 shadow-xl">
          <div className="space-y-2 max-w-2xl">
            <span className="text-xs font-bold uppercase tracking-wider text-amber-400">
              Your child could be our next board topper
            </span>
            <h3 className="text-2xl sm:text-3xl font-black text-white">
              Join Aarambh&apos;s High-Performance Batch
            </h3>
            <p className="text-xs sm:text-sm text-slate-300 leading-relaxed">
              With only 20 students per batch, our teachers ensure that every student masters difficult concepts and scores distinction in their board exams.
            </p>
          </div>

          <Link
            href="/admissions"
            className="btn-caramel-gold shrink-0 inline-flex items-center gap-2 px-6 py-3.5 rounded-xl font-bold text-sm shadow-md hover:scale-105 transition-transform"
          >
            <span>Book Free Demo Class</span>
            <ArrowRight className="w-4 h-4" />
          </Link>
        </div>
      </section>
    </div>
  );
}
