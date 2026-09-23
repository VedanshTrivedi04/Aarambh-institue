"use client";

import React from "react";
import { Users, GraduationCap, Trophy, BookOpen, Heart, IndianRupee, Sparkles, CheckCircle2 } from "lucide-react";

export default function FeaturesSection() {
  const usps = [
    {
      icon: GraduationCap,
      title: "Expert Faculty (Up to 30 Yrs Exp)",
      desc: "Highly qualified and veteran educators who teach with passion, patience, and proven pedagogical mastery.",
      tag: "Veteran Educators",
      iconBg: "bg-red-50 text-[#c22329]",
      borderHover: "hover:border-red-300",
    },
    {
      icon: Users,
      title: "Personalised Attention & Small Batches",
      desc: "Strictly limited batch sizes (max 20 to 35 students) ensuring individual guidance, personal homework reviews, and direct student-teacher interaction.",
      tag: "Small Batches",
      iconBg: "bg-amber-50 text-amber-800",
      borderHover: "hover:border-amber-300",
    },
    {
      icon: Trophy,
      title: "Result Oriented Approach",
      desc: "Consistent record of outstanding results in MP Board, CBSE & ICSE exams with 98.5% highest score and 98% pass rate.",
      tag: "Proven Results",
      iconBg: "bg-blue-50 text-blue-700",
      borderHover: "hover:border-blue-300",
    },
    {
      icon: BookOpen,
      title: "Study Material & Regular Weekly Tests",
      desc: "In-depth chapter notes, practice question sets, and return modules designed for all learning levels, accompanied by weekly tests and timely parent feedback.",
      tag: "Comprehensive Material",
      iconBg: "bg-emerald-50 text-emerald-700",
      borderHover: "hover:border-emerald-300",
    },
    {
      icon: Heart,
      title: "Supportive Learning Environment",
      desc: "Encouraging, positive classroom atmosphere that eliminates exam fear, builds self-confidence, and motivates every student to realize their true potential.",
      tag: "Confidence Building",
      iconBg: "bg-purple-50 text-purple-700",
      borderHover: "hover:border-purple-300",
    },
    {
      icon: IndianRupee,
      title: "Student-Friendly Fee Structure",
      desc: "High-quality coaching made accessible to every family at student-friendly monthly prices (starting at just ₹800 to ₹1000/month).",
      tag: "Affordable Excellence",
      iconBg: "bg-cyan-50 text-cyan-700",
      borderHover: "hover:border-cyan-300",
    },
  ];

  return (
    <section id="why-aarambh" className="relative py-24 bg-white text-slate-900 border-b border-slate-200/80">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="text-center max-w-3xl mx-auto space-y-4">
          <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-red-50 border border-red-200 text-[#c22329] text-xs font-bold uppercase tracking-wider">
            <Sparkles className="w-3.5 h-3.5 text-amber-500" />
            <span>Why Choose Aarambh Institute?</span>
          </div>

          <h2 className="text-3xl sm:text-5xl font-black tracking-tight text-slate-900">
            6 Core Pillars of <br />
            <span className="text-[#c22329]">Academic Excellence</span>
          </h2>

          <p className="text-sm sm:text-base text-slate-600">
            What sets Aarambh apart is our commitment to student happiness, safety, and personal mentorship.
          </p>
        </div>

        {/* 6 Pillars Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mt-16">
          {usps.map((usp, idx) => {
            const Icon = usp.icon;
            return (
              <div
                key={idx}
                className={`light-card-interactive p-7 rounded-3xl border border-slate-200 ${usp.borderHover} transition-all group`}
              >
                <div className="flex items-center justify-between mb-5">
                  <div className={`p-3 rounded-2xl ${usp.iconBg} font-bold group-hover:scale-110 transition-transform`}>
                    <Icon className="w-6 h-6" />
                  </div>
                  <span className="text-[11px] font-bold px-2.5 py-1 rounded-full bg-slate-100 text-slate-600">
                    {usp.tag}
                  </span>
                </div>

                <h3 className="text-xl font-bold text-slate-900 mb-2.5 group-hover:text-[#c22329] transition-colors">
                  {usp.title}
                </h3>

                <p className="text-xs sm:text-sm text-slate-600 leading-relaxed font-normal">
                  {usp.desc}
                </p>
              </div>
            );
          })}
        </div>

        {/* Trust Banner */}
        <div className="mt-14 p-8 rounded-3xl bg-gradient-to-r from-red-50/70 via-white to-amber-50/70 border border-slate-200 max-w-4xl mx-auto shadow-sm">
          <div className="flex flex-col sm:flex-row items-center justify-between gap-6 text-center sm:text-left">
            <div className="space-y-1.5">
              <h4 className="text-xl font-black text-slate-900">
                Join 2,000+ Students Who Stepped Toward Success
              </h4>
              <p className="text-xs sm:text-sm text-slate-600">
                Admissions open for Classes 4th to 12th & Degree Courses at Hawa Bangla, Indore.
              </p>
            </div>

            <a
              href="#admissions"
              className="btn-caramel-gold px-6 py-3 rounded-xl text-xs sm:text-sm font-black shadow-md flex-shrink-0"
            >
              Book 1-Day Free Demo
            </a>
          </div>
        </div>
      </div>
    </section>
  );
}
