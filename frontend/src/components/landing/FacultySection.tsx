"use client";

import React from "react";
import { GraduationCap, Award, BookOpen, CheckCircle2, Clock } from "lucide-react";

import { FacultyMember } from "@/types/landing";
import Reveal from "@/components/ui/Reveal";

interface FacultySectionProps {
  faculty?: FacultyMember[];
}

export default function FacultySection({ faculty: propFaculty }: FacultySectionProps) {
  const defaultTeachers: FacultyMember[] = [
    {
      name: "Mr. Pankaj Dubey",
      subject: "Biology",
      experience: "30 Years Experience",
      highlight: "Senior Biology Expert • PMT/NEET & Board Specialist",
      specialty: "Botany, Zoology & Medical Foundation",
      initials: "PD",
      avatar_bg: "bg-emerald-100 text-emerald-800 border-emerald-200",
      subject_badge: "bg-emerald-50 text-emerald-800 border-emerald-200",
    },
    {
      name: "Mr. Jitendra Shindey",
      subject: "Commerce & Accountancy",
      experience: "30 Years Experience",
      highlight: "Senior Commerce Mentor • 11th-12th, B.Com & M.Com",
      specialty: "Financial Accounting, Tax & Corporate Laws",
      initials: "JS",
      avatar_bg: "bg-blue-100 text-blue-800 border-blue-200",
      subject_badge: "bg-blue-50 text-blue-800 border-blue-200",
    },
    {
      name: "Mrs. Shobhna Vyas",
      subject: "Maths & Science (Founder)",
      experience: "20 Years Experience",
      highlight: "Founder & Academic Director, Aarambh Institute",
      specialty: "Conceptual Mathematics & Science for 4th to 10th",
      initials: "SV",
      avatar_bg: "bg-red-100 text-[#c22329] border-red-200",
      subject_badge: "bg-red-50 text-[#c22329] border-red-200",
    },
    {
      name: "Mr. Vishal Rathore",
      subject: "Mathematics",
      experience: "15 Years Experience",
      highlight: "Senior Mathematics Specialist for Board Exams",
      specialty: "Algebra, Calculus & Trigonometry Mastery",
      initials: "VR",
      avatar_bg: "bg-amber-100 text-amber-800 border-amber-200",
      subject_badge: "bg-amber-50 text-amber-800 border-amber-200",
    },
    {
      name: "Mrs. Anita Holkar",
      subject: "Physics",
      experience: "15 Years Experience",
      highlight: "Physics Senior Educator for MP Board & CBSE",
      specialty: "Mechanics, Electricity, Optics & Numerical Clarity",
      initials: "AH",
      avatar_bg: "bg-cyan-100 text-cyan-800 border-cyan-200",
      subject_badge: "bg-cyan-50 text-cyan-800 border-cyan-200",
    },
    {
      name: "Mr. Ansh Sir",
      subject: "Chemistry, Biology, Physics",
      experience: "5 Years Experience",
      highlight: "NEET + JEE Mains Category Specialist",
      specialty: "Competitive Speed Techniques & Problem Solving",
      initials: "AS",
      avatar_bg: "bg-purple-100 text-purple-800 border-purple-200",
      subject_badge: "bg-purple-50 text-purple-800 border-purple-200",
    },
    {
      name: "Miss Darshna Panchal",
      subject: "Business Studies & Economics",
      experience: "2 Years Experience",
      highlight: "Teaching & Institutional Management Expertise",
      specialty: "Business Management, Micro & Macro Economics",
      initials: "DP",
      avatar_bg: "bg-rose-100 text-rose-800 border-rose-200",
      subject_badge: "bg-rose-50 text-rose-800 border-rose-200",
    },
  ];

  const teachers = propFaculty && propFaculty.length > 0 ? propFaculty : defaultTeachers;

  return (
    <section id="faculty" className="relative py-24 bg-white text-slate-900 border-b border-slate-200/80">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <Reveal className="text-center max-w-3xl mx-auto space-y-4">
          <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-red-50 border border-red-200 text-[#c22329] text-xs font-bold uppercase tracking-wider">
            <GraduationCap className="w-3.5 h-3.5" />
            <span>Our Experienced Educators</span>
          </div>

          <h2 className="text-3xl sm:text-5xl font-black tracking-tight text-slate-900">
            Meet Our Expert <br />
            <span className="text-[#c22329]">Teaching Faculty</span>
          </h2>

          <p className="text-sm sm:text-base text-slate-600">
            Learn from veteran educators with up to 30 years of dedicated teaching legacy across Science, Maths, Commerce & Humanities.
          </p>
        </Reveal>

        {/* Teachers Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6 mt-16">
          {teachers.map((t, idx) => (
            <Reveal key={idx} delay={(idx % 4) * 90} direction="up" distance={22}>
            <div
              className="light-card-interactive hover-lift p-6 rounded-3xl flex flex-col justify-between group h-full"
            >
              <div>
                <div className="flex items-center justify-between mb-4">
                  <div className={`w-14 h-14 rounded-2xl border ${t.avatar_bg || (t as any).avatarBg} flex items-center justify-center font-black text-xl shadow-sm group-hover:scale-105 transition-transform`}>
                    {t.initials}
                  </div>
                  <span className="text-[11px] font-bold px-2.5 py-1 rounded-full bg-slate-100 border border-slate-200 text-slate-700 flex items-center gap-1">
                    <Clock className="w-3 h-3 text-amber-600" />
                    <span>{t.experience}</span>
                  </span>
                </div>

                <span className={`text-[11px] font-extrabold px-2.5 py-0.5 rounded-md border inline-block mb-2 ${t.subject_badge || (t as any).subjectBadge}`}>
                  {t.subject}
                </span>

                <h3 className="text-xl font-bold text-slate-900 group-hover:text-[#c22329] transition-colors">
                  {t.name}
                </h3>

                <p className="text-xs text-slate-600 mt-1 font-semibold leading-snug">
                  {t.highlight}
                </p>

                <div className="mt-4 pt-3 border-t border-slate-100 text-xs text-slate-500">
                  <span className="font-semibold text-slate-700">Specialty: </span>
                  <span>{t.specialty}</span>
                </div>
              </div>

              <div className="mt-4 pt-3 border-t border-slate-100 flex items-center gap-1.5 text-[11px] text-emerald-700 font-bold">
                <CheckCircle2 className="w-3.5 h-3.5" />
                <span>Small Batch Faculty</span>
              </div>
            </div>
            </Reveal>
          ))}
        </div>
      </div>
    </section>
  );
}
