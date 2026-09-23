"use client";

import React from "react";
import { Award, ShieldCheck, Heart, Users, GraduationCap, CheckCircle2 } from "lucide-react";

import { AboutSectionData, InstituteContactInfo } from "@/types/landing";

interface AboutSectionProps {
  about?: AboutSectionData;
  contact?: InstituteContactInfo;
}

export default function AboutSection({ about, contact }: AboutSectionProps) {
  const directorName = about?.director_name || "Shobhna Vyas";
  const directorExp = about?.director_experience || "20 Years Experience";
  const directorQuote =
    about?.director_quote ||
    "As a parent myself, I know what you want: safety, learning, and happiness for your child. At Aarambh Institute, you will get all three. Let's grow together.";
  const paragraphs = about?.paragraphs || [
    "At Aarambh Institute, we believe that the right guidance at the right time can transform a student's academic journey.",
    "Our experienced faculty, well-researched curriculum, and student-centric approach make learning both effective and engaging.",
  ];

  return (
    <section id="about" className="relative py-20 bg-white text-slate-900 border-b border-slate-200/80">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-12 items-center">
          {/* Left: About Text & Director Message */}
          <div className="lg:col-span-7 space-y-6">
            <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-red-50 border border-red-200 text-[#c22329] text-xs font-bold uppercase tracking-wider">
              <Award className="w-3.5 h-3.5" />
              <span>Established {contact?.established_year || 2015} • {contact?.city || "Indore, MP"}</span>
            </div>

            <h2 className="text-3xl sm:text-5xl font-black tracking-tight text-slate-900 leading-tight">
              Transforming Academic Journeys <br />
              <span className="text-[#c22329]">With The Right Guidance</span>
            </h2>

            <p className="text-base text-slate-700 leading-relaxed font-medium">
              At <strong className="text-slate-900">{contact?.name || "Aarambh Institute"}</strong>, we believe that the right guidance at the right time can transform a student&apos;s academic journey. Our experienced faculty, well-researched curriculum, and student-centric approach make learning both effective and engaging.
            </p>

            {/* Founder Message Card */}
            <div className="p-6 rounded-3xl bg-gradient-to-r from-amber-50/70 via-slate-50 to-red-50/50 border border-amber-200/80 shadow-sm relative overflow-hidden">
              <div className="flex items-start gap-4">
                <div className="w-14 h-14 rounded-2xl bg-gradient-to-br from-amber-500 to-[#c22329] text-white flex items-center justify-center font-black text-xl flex-shrink-0 shadow-md">
                  SV
                </div>
                <div className="space-y-2">
                  <div className="flex items-center gap-2">
                    <span className="font-bold text-slate-900 text-base">{directorName}</span>
                    <span className="text-[11px] font-bold px-2 py-0.5 rounded bg-amber-100 text-amber-900">
                      {about?.director_designation || "Founder & Director"} ({directorExp})
                    </span>
                  </div>
                  <p className="text-sm text-slate-700 italic leading-relaxed font-normal">
                    &ldquo;{directorQuote}&rdquo;
                  </p>
                </div>
              </div>
            </div>

            {/* Core Values */}
            <div className="grid grid-cols-3 gap-3 pt-2 text-xs font-bold">
              <div className="flex items-center gap-2 p-3 rounded-2xl bg-slate-50 border border-slate-200">
                <ShieldCheck className="w-4 h-4 text-emerald-600 flex-shrink-0" />
                <span>Child Safety First</span>
              </div>
              <div className="flex items-center gap-2 p-3 rounded-2xl bg-slate-50 border border-slate-200">
                <GraduationCap className="w-4 h-4 text-blue-600 flex-shrink-0" />
                <span>Effective Learning</span>
              </div>
              <div className="flex items-center gap-2 p-3 rounded-2xl bg-slate-50 border border-slate-200">
                <Heart className="w-4 h-4 text-[#c22329] flex-shrink-0" />
                <span>Joyful Environment</span>
              </div>
            </div>
          </div>

          {/* Right: Quick Highlights Grid */}
          <div className="lg:col-span-5">
            <div className="bg-[#f8fafd] p-7 rounded-3xl border border-slate-200 shadow-md space-y-4">
              <div className="flex items-center justify-between border-b border-slate-200 pb-3">
                <span className="text-xs font-bold text-slate-500 uppercase tracking-wider">
                  Institute Milestones
                </span>
                <span className="text-xs font-bold text-[#c22329] bg-red-50 px-2.5 py-0.5 rounded-full border border-red-200">
                  Best Coaching Award 2023
                </span>
              </div>

              <div className="grid grid-cols-2 gap-3.5">
                <div className="p-4 rounded-2xl bg-white border border-slate-200 shadow-sm">
                  <span className="text-2xl sm:text-3xl font-black text-[#c22329]">15+ Yrs</span>
                  <p className="text-xs text-slate-600 font-semibold mt-1">Teaching Experience</p>
                </div>
                <div className="p-4 rounded-2xl bg-white border border-slate-200 shadow-sm">
                  <span className="text-2xl sm:text-3xl font-black text-blue-700">2000+</span>
                  <p className="text-xs text-slate-600 font-semibold mt-1">Students Since 2015</p>
                </div>
                <div className="p-4 rounded-2xl bg-white border border-slate-200 shadow-sm">
                  <span className="text-2xl sm:text-3xl font-black text-emerald-700">98%</span>
                  <p className="text-xs text-slate-600 font-semibold mt-1">Board Result Rate</p>
                </div>
                <div className="p-4 rounded-2xl bg-white border border-slate-200 shadow-sm">
                  <span className="text-2xl sm:text-3xl font-black text-amber-600">12+</span>
                  <p className="text-xs text-slate-600 font-semibold mt-1">Expert Faculty</p>
                </div>
              </div>

              <div className="p-4 rounded-2xl bg-white border border-slate-200 space-y-2 text-xs">
                <div className="flex items-center justify-between text-slate-700">
                  <span className="font-semibold">Classes Covered:</span>
                  <span className="font-bold text-slate-900">4th to 12th & Degrees</span>
                </div>
                <div className="flex items-center justify-between text-slate-700">
                  <span className="font-semibold">Boards:</span>
                  <span className="font-bold text-slate-900">MP Board • CBSE • ICSE</span>
                </div>
                <div className="flex items-center justify-between text-slate-700">
                  <span className="font-semibold">Working Hours:</span>
                  <span className="font-bold text-slate-900">10:00 AM – 8:00 PM</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
