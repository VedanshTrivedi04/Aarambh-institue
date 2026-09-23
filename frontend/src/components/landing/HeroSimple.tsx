"use client";

import React, { useRef } from "react";
import {
  ArrowRight,
  Sparkles,
  Award,
  Users,
  CheckCircle2,
  Calendar,
  Phone,
  BookOpen,
  GraduationCap,
  ShieldCheck,
  Star,
  MapPin,
  MessageCircle,
} from "lucide-react";

import { InstituteContactInfo, HeroStats } from "@/types/landing";
import CountUp from "@/components/ui/CountUp";

interface HeroSimpleProps {
  contact?: InstituteContactInfo;
  stats?: HeroStats;
}

export default function HeroSimple({ contact, stats }: HeroSimpleProps) {
  const cardRef = useRef<HTMLDivElement | null>(null);

  const handleCardMouseMove = (e: React.MouseEvent<HTMLDivElement>) => {
    const el = cardRef.current;
    if (!el) return;
    const rect = el.getBoundingClientRect();
    const x = (e.clientX - rect.left) / rect.width - 0.5;
    const y = (e.clientY - rect.top) / rect.height - 0.5;
    el.style.transform = `perspective(900px) rotateX(${y * -6}deg) rotateY(${x * 6}deg) translateY(-4px)`;
  };

  const handleCardMouseLeave = () => {
    const el = cardRef.current;
    if (!el) return;
    el.style.transform = "perspective(900px) rotateX(0deg) rotateY(0deg) translateY(0)";
  };

  const primaryPhone = contact?.primary_phone || "88397-14081";
  const secondaryPhone = contact?.secondary_phone || "79097-14081";
  const city = contact?.city || "Hawa Bangla, Indore";
  const yearsExp = stats?.years_experience || "15+ Yrs";
  const totalStudents = stats?.total_students || "2,000+";
  const highestScore = stats?.highest_board_score || "98.5%";
  const facultyCount = stats?.faculty_count || "12+";

  return (
    <section className="relative pt-28 pb-20 sm:pt-36 sm:pb-24 bg-gradient-to-b from-blue-50/40 via-white to-[#f8fafd] border-b border-slate-200/80 overflow-hidden">
      {/* Decorative ambient background glows (pure CSS, zero images/videos) */}
      <div className="absolute top-0 left-1/2 -translate-x-1/2 w-full max-w-7xl h-96 bg-gradient-to-br from-blue-200/20 via-amber-100/20 to-red-100/15 blur-3xl -z-10 pointer-events-none" />
      <div className="absolute top-10 -right-10 w-72 h-72 bg-amber-200/25 rounded-full blur-3xl -z-10 pointer-events-none animate-float-slow" />
      <div className="absolute bottom-0 -left-16 w-72 h-72 bg-red-200/20 rounded-full blur-3xl -z-10 pointer-events-none animate-float-slower" />

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-12 lg:gap-8 items-center">
          {/* Left Hero Content */}
          <div className="lg:col-span-7 space-y-6 text-left">
            {/* Top Pill Badges */}
            <div className="flex flex-wrap items-center gap-2 animate-fade-in-up">
              <div className="inline-flex items-center gap-1.5 px-3.5 py-1 rounded-full bg-red-50 border border-red-200 text-[#c22329] text-xs font-black uppercase tracking-wider">
                <span className="w-2 h-2 rounded-full bg-[#c22329] animate-pulse" />
                <span>Admissions Open 2026-27</span>
              </div>

              <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-amber-50 border border-amber-200 text-amber-900 text-xs font-bold">
                <MapPin className="w-3.5 h-3.5 text-amber-600" />
                <span>Hawa Bangla, Indore</span>
              </div>
            </div>

            {/* Main Headline from Client Form */}
            <h1
              className="text-4xl sm:text-6xl font-black tracking-tight text-slate-900 leading-[1.12] animate-fade-in-up"
              style={{ animationDelay: "80ms" }}
            >
              Excel in Boards with{" "}
              <span className="text-[#c22329]">Expert Guidance</span>
            </h1>

            {/* Sub-heading */}
            <p
              className="text-base sm:text-xl text-slate-700 leading-relaxed font-medium max-w-2xl animate-fade-in-up"
              style={{ animationDelay: "160ms" }}
            >
              15 Years of trusted coaching for <strong className="text-slate-900">Class 4th to 12th</strong> &amp; <strong className="text-slate-900">Degree Courses</strong> (MP Board, CBSE &amp; ICSE). Small batches of 20 students, personalized attention, and proven 98.5% top results.
            </p>

            {/* Bullet Highlights */}
            <div
              className="grid grid-cols-1 sm:grid-cols-2 gap-2.5 pt-2 text-xs sm:text-sm font-semibold text-slate-700 animate-fade-in-up"
              style={{ animationDelay: "240ms" }}
            >
              <div className="flex items-center gap-2">
                <CheckCircle2 className="w-4 h-4 text-emerald-600 flex-shrink-0" />
                <span>Strict 20 Students per Batch</span>
              </div>
              <div className="flex items-center gap-2">
                <CheckCircle2 className="w-4 h-4 text-emerald-600 flex-shrink-0" />
                <span>Weekly Tests &amp; Instant Doubt Clearing</span>
              </div>
              <div className="flex items-center gap-2">
                <CheckCircle2 className="w-4 h-4 text-emerald-600 flex-shrink-0" />
                <span>Expert Faculty (Up to 30 Yrs Experience)</span>
              </div>
              <div className="flex items-center gap-2">
                <CheckCircle2 className="w-4 h-4 text-emerald-600 flex-shrink-0" />
                <span>Student-Friendly Affordable Fees (From ₹800/mo)</span>
              </div>
            </div>

            {/* CTAs */}
            <div
              className="pt-3 flex flex-wrap items-center gap-3.5 animate-fade-in-up"
              style={{ animationDelay: "320ms" }}
            >
              <a
                href="#admissions"
                className="btn-caramel-gold px-7 py-3.5 rounded-xl font-black text-sm text-white shadow-lg flex items-center gap-2 hover:scale-105 transition-all"
              >
                <span>Join Free Demo Class</span>
                <ArrowRight className="w-4 h-4" />
              </a>

              <a
                href="#programs"
                className="px-6 py-3.5 rounded-xl font-bold text-sm text-slate-800 bg-white hover:bg-slate-50 border border-slate-200 shadow-sm transition-all flex items-center gap-2 hover:border-slate-300 hover:-translate-y-0.5"
              >
                <BookOpen className="w-4 h-4 text-blue-600" />
                <span>View Courses</span>
              </a>

              <a
                href="https://wa.me/918839714081?text=Hello%20Aarambh%20Institute%2C%20I%20want%20to%20know%20more%20about%20admissions."
                target="_blank"
                rel="noopener noreferrer"
                className="px-4 py-3.5 rounded-xl font-bold text-sm text-emerald-700 bg-emerald-50 hover:bg-emerald-100 border border-emerald-200 transition-colors flex items-center gap-1.5 hover:-translate-y-0.5"
                title="Direct WhatsApp Helpline"
              >
                <MessageCircle className="w-4 h-4 text-emerald-600" />
                <span>WhatsApp</span>
              </a>
            </div>

            {/* Helpline quick dial */}
            <div
              className="pt-2 flex items-center gap-2 text-xs text-slate-600 animate-fade-in-up"
              style={{ animationDelay: "380ms" }}
            >
              <Phone className="w-3.5 h-3.5 text-[#c22329]" />
              <span>Direct Admissions Helpline:</span>
              <a href={`tel:+91${primaryPhone.replace(/\D/g, '')}`} className="font-bold text-slate-900 hover:text-[#c22329] transition-colors">
                {primaryPhone}
              </a>
              <span className="text-slate-400">/</span>
              <a href={`tel:+91${secondaryPhone.replace(/\D/g, '')}`} className="font-bold text-slate-900 hover:text-[#c22329] transition-colors">
                {secondaryPhone}
              </a>
            </div>
          </div>

          {/* Right Hero Simple Card Overview */}
          <div className="lg:col-span-5 animate-fade-in-up" style={{ animationDelay: "200ms" }}>
            <div
              ref={cardRef}
              onMouseMove={handleCardMouseMove}
              onMouseLeave={handleCardMouseLeave}
              className="bg-white rounded-3xl border border-slate-200/90 p-6 sm:p-8 shadow-xl shadow-slate-200/40 space-y-5 relative transition-transform duration-200 ease-out will-change-transform"
              style={{ transformStyle: "preserve-3d" }}
            >
              {/* Card Header */}
              <div className="flex items-center justify-between border-b border-slate-100 pb-4">
                <div className="flex items-center gap-3">
                  <div className="w-12 h-12 rounded-2xl bg-gradient-to-br from-red-500 to-[#c22329] text-white flex items-center justify-center font-black text-sm shadow-md">
                    आरंभ
                  </div>
                  <div>
                    <h3 className="font-black text-lg text-slate-900 leading-tight">
                      Aarambh Institute
                    </h3>
                    <p className="text-xs text-amber-700 font-bold uppercase tracking-wide">
                      Step Toward Success
                    </p>
                  </div>
                </div>

                <span className="px-2.5 py-1 rounded-full bg-emerald-50 text-emerald-700 text-xs font-bold border border-emerald-200">
                  Est. 2015
                </span>
              </div>

              {/* Quick Academic Programs Overview */}
              <div className="space-y-2.5">
                <p className="text-xs font-bold text-slate-500 uppercase tracking-wider">
                  Batches Available:
                </p>

                <div className="p-3.5 rounded-2xl bg-slate-50 border border-slate-200/80 flex items-center justify-between hover:bg-slate-100/80 transition-colors">
                  <div>
                    <h4 className="font-bold text-sm text-slate-900">Class 4th to 8th</h4>
                    <p className="text-xs text-slate-500">All Subjects • Strict 20 per batch</p>
                  </div>
                  <span className="text-xs font-black text-[#c22329] bg-red-50 px-2.5 py-1 rounded-lg border border-red-200">
                    ₹800 - ₹1,000/mo
                  </span>
                </div>

                <div className="p-3.5 rounded-2xl bg-slate-50 border border-slate-200/80 flex items-center justify-between hover:bg-slate-100/80 transition-colors">
                  <div>
                    <h4 className="font-bold text-sm text-slate-900">Class 9th to 12th</h4>
                    <p className="text-xs text-slate-500">Science (PCM/PCB) &amp; Commerce</p>
                  </div>
                  <span className="text-xs font-bold text-blue-700 bg-blue-50 px-2.5 py-1 rounded-lg border border-blue-200">
                    Board Result Focus
                  </span>
                </div>

                <div className="p-3.5 rounded-2xl bg-slate-50 border border-slate-200/80 flex items-center justify-between hover:bg-slate-100/80 transition-colors">
                  <div>
                    <h4 className="font-bold text-sm text-slate-900">College Degrees</h4>
                    <p className="text-xs text-slate-500">B.Com, M.Com, BBA, MBA, B.Sc</p>
                  </div>
                  <span className="text-xs font-bold text-amber-800 bg-amber-50 px-2.5 py-1 rounded-lg border border-amber-200">
                    Domain Coaching
                  </span>
                </div>
              </div>

              {/* Free Demo Prompt */}
              <div className="p-4 rounded-2xl bg-gradient-to-r from-amber-50 to-orange-50 border border-amber-200 text-xs text-slate-800 space-y-1">
                <div className="flex items-center gap-1.5 font-bold text-amber-900">
                  <Sparkles className="w-4 h-4 text-amber-600" />
                  <span>Free 2-Day Trial Classes</span>
                </div>
                <p className="text-slate-600">
                  Visit our Hawa Bangla campus to experience teaching by senior educators before finalizing admission.
                </p>
              </div>

              {/* Action Button inside card */}
              <a
                href="#admissions"
                className="w-full py-3 rounded-xl bg-slate-900 hover:bg-[#c22329] text-white text-xs font-black transition-colors flex items-center justify-center gap-2"
              >
                <span>Book Free Demo Slot</span>
                <ArrowRight className="w-3.5 h-3.5" />
              </a>
            </div>
          </div>
        </div>

        {/* 4 Key Stats Bar Below Hero */}
        <div className="mt-16 pt-8 border-t border-slate-200/80 grid grid-cols-2 md:grid-cols-4 gap-6 text-center">
          <div className="space-y-1 animate-fade-in-up" style={{ animationDelay: "420ms" }}>
            <CountUp value={yearsExp} className="stat-pop inline-block text-3xl sm:text-4xl font-black text-[#c22329]" />
            <p className="text-xs sm:text-sm font-bold text-slate-700">Teaching Legacy</p>
            <p className="text-[11px] text-slate-500">Founded in {contact?.established_year || 2015}, Indore</p>
          </div>

          <div className="space-y-1 animate-fade-in-up" style={{ animationDelay: "470ms" }}>
            <CountUp value={totalStudents} className="stat-pop inline-block text-3xl sm:text-4xl font-black text-amber-600" />
            <p className="text-xs sm:text-sm font-bold text-slate-700">Successful Students</p>
            <p className="text-[11px] text-slate-500">Consistent Top Scores</p>
          </div>

          <div className="space-y-1 animate-fade-in-up" style={{ animationDelay: "520ms" }}>
            <CountUp value={highestScore} className="stat-pop inline-block text-3xl sm:text-4xl font-black text-emerald-600" />
            <p className="text-xs sm:text-sm font-bold text-slate-700">Highest Board Result</p>
            <p className="text-[11px] text-slate-500">Class 10 MP Board</p>
          </div>

          <div className="space-y-1 animate-fade-in-up" style={{ animationDelay: "570ms" }}>
            <CountUp value={facultyCount} className="stat-pop inline-block text-3xl sm:text-4xl font-black text-blue-700" />
            <p className="text-xs sm:text-sm font-bold text-slate-700">Expert Faculty</p>
            <p className="text-[11px] text-slate-500">Up to 30 Yrs Experience</p>
          </div>
        </div>
      </div>
    </section>
  );
}
