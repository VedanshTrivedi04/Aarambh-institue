import React from "react";
import Link from "next/link";
import HeroSimple from "@/components/landing/HeroSimple";
import TrustMetrics from "@/components/landing/TrustMetrics";
import AboutSection from "@/components/landing/AboutSection";
import ProgramsSection from "@/components/landing/ProgramsSection";
import FacultySection from "@/components/landing/FacultySection";
import ResultsSection from "@/components/landing/ResultsSection";
import Reveal from "@/components/ui/Reveal";
import { getLandingData } from "@/lib/api";
import {
  ArrowRight,
  GraduationCap,
  BookOpen,
  Award,
  Users,
  Sparkles,
  CheckCircle2,
  PhoneCall,
  MapPin,
  Calendar,
  FileText,
} from "lucide-react";

export default async function Home() {
  const data = await getLandingData();

  return (
    <div className="flex flex-col space-y-12 sm:space-y-16 pb-16">
      {/* Hero Section */}
      <HeroSimple contact={data.contact} stats={data.stats} />

      {/* Trust & Performance Metrics */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 w-full">
        <TrustMetrics />
      </div>

      {/* Dedicated Portal Section Cards */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 w-full">
        <Reveal className="text-center max-w-3xl mx-auto mb-12 space-y-3">
          <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-red-50 border border-red-200 text-[#c22329] text-xs font-bold uppercase tracking-wider">
            <Sparkles className="w-3.5 h-3.5" />
            <span>Explore Aarambh Institute</span>
          </div>
          <h2 className="text-2xl sm:text-4xl font-black text-slate-900 tracking-tight">
            Comprehensive Learning Ecosystem
          </h2>
          <p className="text-slate-600 text-sm sm:text-base">
            Everything your child needs for academic excellence — from Class 4th foundation to Class 12th board mastery and college degrees.
          </p>
        </Reveal>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {/* Card 1: About Us */}
          <Reveal delay={0}>
          <Link
            href="/about"
            className="light-card-interactive hover-lift p-7 rounded-3xl group flex flex-col justify-between h-full"
          >
            <div>
              <div className="w-12 h-12 rounded-2xl bg-red-50 border border-red-200 flex items-center justify-center text-[#c22329] mb-5 group-hover:scale-110 group-hover:rotate-6 transition-transform">
                <GraduationCap className="w-6 h-6" />
              </div>
              <h3 className="text-xl font-bold text-slate-900 group-hover:text-[#c22329] transition-colors">
                About Aarambh
              </h3>
              <p className="text-xs sm:text-sm text-slate-600 mt-2 leading-relaxed">
                Learn about Director Mrs. Shobhna Vyas (20 Yrs Exp), our founding story since 2015, core values, and the 2023 Best Coaching Institute award.
              </p>
            </div>
            <div className="mt-6 pt-4 border-t border-slate-100 flex items-center gap-2 text-xs font-bold text-[#c22329]">
              <span>Read Director&apos;s Message</span>
              <ArrowRight className="w-3.5 h-3.5 group-hover:translate-x-1 transition-transform" />
            </div>
          </Link>
          </Reveal>

          {/* Card 2: Courses */}
          <Reveal delay={80}>
          <Link
            href="/courses"
            className="light-card-interactive hover-lift p-7 rounded-3xl group flex flex-col justify-between h-full"
          >
            <div>
              <div className="w-12 h-12 rounded-2xl bg-blue-50 border border-blue-200 flex items-center justify-center text-blue-700 mb-5 group-hover:scale-110 group-hover:rotate-6 transition-transform">
                <BookOpen className="w-6 h-6" />
              </div>
              <h3 className="text-xl font-bold text-slate-900 group-hover:text-blue-700 transition-colors">
                Academic Programs & Fees
              </h3>
              <p className="text-xs sm:text-sm text-slate-600 mt-2 leading-relaxed">
                Coaching for Classes 4th to 12th (MP Board, CBSE, ICSE) and Degree programs (B.Com, BBA, MBA). Strict 20-student small batches.
              </p>
            </div>
            <div className="mt-6 pt-4 border-t border-slate-100 flex items-center gap-2 text-xs font-bold text-blue-700">
              <span>View All Courses & Schedules</span>
              <ArrowRight className="w-3.5 h-3.5 group-hover:translate-x-1 transition-transform" />
            </div>
          </Link>
          </Reveal>

          {/* Card 3: Faculty */}
          <Reveal delay={160}>
          <Link
            href="/faculty"
            className="light-card-interactive hover-lift p-7 rounded-3xl group flex flex-col justify-between h-full"
          >
            <div>
              <div className="w-12 h-12 rounded-2xl bg-amber-50 border border-amber-200 flex items-center justify-center text-amber-800 mb-5 group-hover:scale-110 group-hover:rotate-6 transition-transform">
                <Users className="w-6 h-6" />
              </div>
              <h3 className="text-xl font-bold text-slate-900 group-hover:text-amber-800 transition-colors">
                Expert Faculty (Up to 30 Yrs)
              </h3>
              <p className="text-xs sm:text-sm text-slate-600 mt-2 leading-relaxed">
                Meet our veteran faculty panel across Biology, Commerce, Maths, Physics, and Chemistry including Mr. Pankaj Dubey & Mr. Jitendra Shindey.
              </p>
            </div>
            <div className="mt-6 pt-4 border-t border-slate-100 flex items-center gap-2 text-xs font-bold text-amber-800">
              <span>Meet All 7 Educators</span>
              <ArrowRight className="w-3.5 h-3.5 group-hover:translate-x-1 transition-transform" />
            </div>
          </Link>
          </Reveal>

          {/* Card 4: Results & Toppers */}
          <Reveal delay={0}>
          <Link
            href="/results"
            className="light-card-interactive hover-lift p-7 rounded-3xl group flex flex-col justify-between h-full"
          >
            <div>
              <div className="w-12 h-12 rounded-2xl bg-emerald-50 border border-emerald-200 flex items-center justify-center text-emerald-700 mb-5 group-hover:scale-110 group-hover:rotate-6 transition-transform">
                <Award className="w-6 h-6" />
              </div>
              <h3 className="text-xl font-bold text-slate-900 group-hover:text-emerald-700 transition-colors">
                Results & Hall of Fame
              </h3>
              <p className="text-xs sm:text-sm text-slate-600 mt-2 leading-relaxed">
                Celebrating Prince (94% Rank 1st), Rohit Garg (91% Rank 2nd), Payal Sharma (89% Rank 3rd), and our 98% board pass rate.
              </p>
            </div>
            <div className="mt-6 pt-4 border-t border-slate-100 flex items-center gap-2 text-xs font-bold text-emerald-700">
              <span>View Merit Roll & Testimonials</span>
              <ArrowRight className="w-3.5 h-3.5 group-hover:translate-x-1 transition-transform" />
            </div>
          </Link>
          </Reveal>

          {/* Card 5: Student Corner */}
          <Reveal delay={80}>
          <Link
            href="/student-corner"
            className="light-card-interactive hover-lift p-7 rounded-3xl group flex flex-col justify-between h-full"
          >
            <div>
              <div className="w-12 h-12 rounded-2xl bg-purple-50 border border-purple-200 flex items-center justify-center text-purple-700 mb-5 group-hover:scale-110 group-hover:rotate-6 transition-transform">
                <FileText className="w-6 h-6" />
              </div>
              <h3 className="text-xl font-bold text-slate-900 group-hover:text-purple-700 transition-colors">
                Student Corner & Resources
              </h3>
              <p className="text-xs sm:text-sm text-slate-600 mt-2 leading-relaxed">
                Free formula booklets, model question papers, notice board for weekly test series, and 2026 academic holiday schedule.
              </p>
            </div>
            <div className="mt-6 pt-4 border-t border-slate-100 flex items-center gap-2 text-xs font-bold text-purple-700">
              <span>Free Downloads & Notices</span>
              <ArrowRight className="w-3.5 h-3.5 group-hover:translate-x-1 transition-transform" />
            </div>
          </Link>
          </Reveal>

          {/* Card 6: Admissions & Demo */}
          <Reveal delay={160}>
          <Link
            href="/admissions"
            className="light-card-interactive hover-lift p-7 rounded-3xl group flex flex-col justify-between border-amber-300 ring-2 ring-amber-400/20 shadow-md h-full"
          >
            <div>
              <div className="w-12 h-12 rounded-2xl bg-[#c99a5e]/20 border border-amber-300 flex items-center justify-center text-[#996515] mb-5 group-hover:scale-110 group-hover:rotate-6 transition-transform">
                <Calendar className="w-6 h-6" />
              </div>
              <div className="inline-block px-2.5 py-0.5 rounded-full bg-red-100 text-[#c22329] font-black text-[10px] uppercase mb-2">
                Limited Seats (20 / Batch)
              </div>
              <h3 className="text-xl font-bold text-slate-900 group-hover:text-[#c22329] transition-colors">
                Admissions 2026-27
              </h3>
              <p className="text-xs sm:text-sm text-slate-600 mt-2 leading-relaxed">
                Register for a 2-day Free Demo Class. Simple 4-step admission process, transparent fee structure, and scholarship discounts.
              </p>
            </div>
            <div className="mt-6 pt-4 border-t border-slate-100 flex items-center gap-2 text-xs font-black text-[#c22329]">
              <span>Book Free Demo Now</span>
              <ArrowRight className="w-3.5 h-3.5 group-hover:translate-x-1 transition-transform" />
            </div>
          </Link>
          </Reveal>
        </div>
      </section>

      {/* Featured Courses Showcase */}
      <div className="border-t border-slate-200/80 pt-10">
        <ProgramsSection courses={data.courses} />
      </div>

      {/* Faculty Showcase */}
      <div className="border-t border-slate-200/80 pt-10">
        <FacultySection faculty={data.faculty} />
      </div>

      {/* Toppers & Hall of Fame Showcase */}
      <div className="border-t border-slate-200/80 pt-10">
        <ResultsSection />
      </div>

      {/* High-Converting CTA Banner */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 w-full">
        <Reveal>
        <div className="rounded-3xl bg-gradient-to-r from-slate-900 via-[#1c1917] to-slate-900 text-white p-8 sm:p-12 shadow-2xl relative overflow-hidden border border-slate-800">
          {/* Ambient floating glows */}
          <div className="absolute -top-10 -right-10 w-64 h-64 bg-amber-500/10 rounded-full blur-3xl animate-float-slow pointer-events-none" />
          <div className="absolute -bottom-16 -left-10 w-64 h-64 bg-red-500/10 rounded-full blur-3xl animate-float-slower pointer-events-none" />

          <div className="relative z-10 max-w-3xl space-y-4">
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-amber-500/20 text-amber-300 border border-amber-500/30 text-xs font-bold uppercase tracking-wider">
              <Sparkles className="w-3.5 h-3.5 text-amber-400 animate-gentle-bounce" />
              <span>Step Toward Success • New Batch Admissions Open</span>
            </div>

            <h2 className="text-2xl sm:text-4xl font-black tracking-tight text-white leading-tight">
              Give Your Child The Advantage Of <br />
              <span className="text-[#c99a5e]">Personal Mentorship & Small Batches</span>
            </h2>

            <p className="text-slate-300 text-sm sm:text-base leading-relaxed">
              Strict 20-student batches ensure your child never gets lost in a crowd. Experience 2 days of free demo classes with our senior HODs.
            </p>

            <div className="flex flex-wrap items-center gap-4 pt-4">
              <Link
                href="/admissions"
                className="btn-caramel-gold inline-flex items-center gap-2 px-6 py-3.5 rounded-xl font-bold text-sm shadow-xl hover:scale-105 transition-transform"
              >
                <span>Book 2-Day Free Demo Class</span>
                <ArrowRight className="w-4 h-4" />
              </Link>

              <a
                href={`tel:+91${(data.contact?.primary_phone || "8839714081").replace(/\D/g, "")}`}
                className="inline-flex items-center gap-2 px-5 py-3.5 rounded-xl font-bold text-sm bg-white/10 hover:bg-white/20 border border-white/20 text-white transition-colors"
              >
                <PhoneCall className="w-4 h-4 text-emerald-400" />
                <span>Call {data.contact?.primary_phone || "88397-14081"}</span>
              </a>
            </div>
          </div>
        </div>
        </Reveal>
      </section>
    </div>
  );
}
