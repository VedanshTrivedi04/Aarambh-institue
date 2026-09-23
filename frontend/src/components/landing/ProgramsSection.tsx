"use client";

import React, { useState } from "react";
import { BookOpen, Check, ArrowRight, Sparkles, Clock, Calendar, Users, IndianRupee, MessageCircle } from "lucide-react";

import { CourseItem } from "@/types/landing";
import Reveal from "@/components/ui/Reveal";

interface ProgramsSectionProps {
  courses?: CourseItem[];
}

export default function ProgramsSection({ courses: propCourses }: ProgramsSectionProps) {
  const [activeTab, setActiveTab] = useState<string>("all");

  const defaultCourses: CourseItem[] = [
    {
      id: "middle-school",
      category: "school",
      title: "Class 4th to 8th (Middle School)",
      subtitle: "All Subjects Comprehensive Coaching for MP Board, CBSE & ICSE",
      target: "Classes 4th, 5th, 6th, 7th & 8th",
      duration: "1 Academic Year",
      board: "MP Board / CBSE / ICSE",
      timings: "Morning 11:00 AM - 12:30 PM | Evening 5:00 PM - 6:30 PM",
      batch_size: "Strict 20 Students per batch",
      fee: "₹800/- to ₹1,000/- (Monthly)",
      badge: "Junior Foundation",
      badge_color: "bg-blue-50 text-blue-700 border-blue-200",
      features: [
        "All Subjects Covered (Maths, Science, English, Hindi, Social Science)",
        "Weekly Assessment Tests with Parent Progress Reports",
        "Printed Comprehensive Study Material & Practice Worksheets",
        "Daily Dedicated Doubt Clearing & Homework Guidance",
        "Special focus on Handwriting, Reading & Basic Mathematical Speed",
      ],
      popular: true,
    },
    {
      id: "high-school",
      category: "board",
      title: "Class 9th to 12th (Board & Entrance)",
      subtitle: "Science (PCM / PCB) & Commerce Stream Mastery for Board Exams",
      target: "Classes 9th, 10th, 11th & 12th",
      duration: "1 Academic Year",
      board: "MP Board / CBSE / ICSE",
      timings: "Morning 11:00 AM - 1:00 PM | Evening 4:00 PM - 6:00 PM",
      batch_size: "Small Batches (20-30 Students)",
      fee: "Student-Friendly Affordable Fees",
      badge: "Board Result Rankers",
      badge_color: "bg-red-50 text-[#c22329] border-red-200",
      features: [
        "All Core Subjects: Physics, Chemistry, Maths, Biology, Commerce & Accounts",
        "Weekly Topic Tests + Monthly Full Board Model Examination Papers",
        "Previous 10 Years Board Papers analysis and Answer-Writing Drills",
        "Special NEET & JEE Mains Foundation Concepts covered by Expert Mentors",
        "Daily 1:1 Doubt Classes with Senior HODs (15+ to 30 Yrs Experience)",
      ],
      popular: true,
    },
    {
      id: "college-degrees",
      category: "college",
      title: "College Degrees (B.Com, M.Com, BBA, MBA, B.Sc)",
      subtitle: "Specialized Higher Education & Commerce/Management Coaching",
      target: "Undergraduate & Postgraduate Students",
      duration: "Semester / Academic Year",
      board: "University Syllabus Aligned",
      timings: "Flexible Morning & Evening College Batches",
      batch_size: "Personalized Domain Batches",
      fee: "Affordable Package Rates",
      badge: "Higher Education",
      badge_color: "bg-amber-50 text-amber-800 border-amber-200",
      features: [
        "Financial Accounting, Corporate Accounting, Taxation & Costing",
        "Business Studies, Economics, Statistics & Financial Management",
        "Taught by Veteran Commerce Head Mr. Jitendra Shindey (30 Yrs Experience)",
        "University Exam Pattern Model Question Banks & Solved Papers",
        "Concept clearing for Competitive Exams (Bank PO, CA Foundation, CAT)",
      ],
      popular: false,
    },
  ];

  const courses = propCourses && propCourses.length > 0 ? propCourses : defaultCourses;

  const filtered =
    activeTab === "all" ? courses : courses.filter((c) => c.category === activeTab);

  return (
    <section id="programs" className="relative py-24 bg-[#f8fafd] text-slate-900 border-b border-slate-200/80">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <Reveal className="text-center max-w-3xl mx-auto space-y-4">
          <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-red-50 border border-red-200 text-[#c22329] text-xs font-bold uppercase tracking-wider">
            <BookOpen className="w-3.5 h-3.5" />
            <span>Courses & Programs Offered</span>
          </div>

          <h2 className="text-3xl sm:text-5xl font-black tracking-tight text-slate-900">
            Coaching Classes From <br />
            <span className="text-[#c22329]">Class 4th to 12th & Degree Courses</span>
          </h2>

          <p className="text-sm sm:text-base text-slate-600">
            Covering MP Board, CBSE & ICSE curriculums with experienced faculty, small batches, and student-friendly fees in Indore.
          </p>
        </Reveal>

        {/* Tab Filters */}
        <Reveal delay={100} className="flex flex-wrap items-center justify-center gap-2.5 mt-10 mb-12">
          {[
            { id: "all", label: "All Programs" },
            { id: "school", label: "Class 4th to 8th" },
            { id: "board", label: "Class 9th to 12th (Boards)" },
            { id: "college", label: "College (B.Com, BBA, MBA, B.Sc)" },
          ].map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`px-5 py-2.5 rounded-xl text-xs sm:text-sm font-bold transition-all duration-300 ${
                activeTab === tab.id
                  ? "bg-[#c22329] text-white shadow-md shadow-red-500/20 scale-105"
                  : "bg-white text-slate-700 hover:text-slate-950 border border-slate-200 shadow-sm hover:scale-105"
              }`}
            >
              {tab.label}
            </button>
          ))}
        </Reveal>

        {/* Course Cards */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-7">
          {filtered.map((course, idx) => (
            <Reveal key={course.id} delay={idx * 100} direction="up" distance={26}>
            <div
              className={`light-card-interactive hover-lift rounded-3xl p-7 flex flex-col justify-between relative overflow-hidden h-full ${
                course.popular ? "border-amber-300 ring-2 ring-amber-500/10 shadow-lg" : "border-slate-200"
              }`}
            >
              {course.popular && (
                <div className="absolute top-0 right-0 bg-[#c99a5e] text-white font-black text-[10px] tracking-wider uppercase px-4 py-1 rounded-bl-xl shadow-sm">
                  ADMISSION OPEN
                </div>
              )}

              <div>
                <div className="flex items-center gap-2 mb-3">
                  <span className={`text-[11px] font-extrabold px-2.5 py-0.5 rounded-md border ${course.badge_color || (course as any).badgeColor}`}>
                    {course.badge}
                  </span>
                  <span className="text-xs text-slate-500 font-semibold">{course.board}</span>
                </div>

                <h3 className="text-xl sm:text-2xl font-black text-slate-900 group-hover:text-[#c22329] transition-colors leading-snug">
                  {course.title}
                </h3>

                <p className="text-xs sm:text-sm text-slate-600 mt-2 font-normal leading-relaxed">
                  {course.subtitle}
                </p>

                {/* Info Pills */}
                <div className="my-5 p-4 rounded-2xl bg-slate-50 border border-slate-100 space-y-2 text-xs text-slate-700 font-semibold">
                  <div className="flex items-center justify-between">
                    <span className="text-slate-500 font-medium">Batch Timings:</span>
                    <span className="text-slate-900 font-bold">{course.timings}</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-slate-500 font-medium">Batch Size:</span>
                    <span className="text-emerald-700 font-bold">{course.batch_size || (course as any).batchSize}</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-slate-500 font-medium">Fee:</span>
                    <span className="text-[#c22329] font-black">{course.fee}</span>
                  </div>
                </div>

                {/* Features */}
                <div className="space-y-2 mb-6">
                  {course.features.map((feat, idx) => (
                    <div key={idx} className="flex items-start gap-2 text-xs sm:text-sm text-slate-700">
                      <div className="p-0.5 rounded bg-emerald-100 text-emerald-700 mt-0.5 flex-shrink-0">
                        <Check className="w-3.5 h-3.5" />
                      </div>
                      <span className="leading-tight font-medium">{feat}</span>
                    </div>
                  ))}
                </div>
              </div>

              {/* Action */}
              <div className="pt-4 border-t border-slate-100 flex flex-col gap-2">
                <a
                  href="#admissions"
                  className="btn-caramel-gold w-full py-3 rounded-xl text-center text-xs sm:text-sm font-black shadow-md flex items-center justify-center gap-2"
                >
                  <span>Book Free Demo Class</span>
                  <ArrowRight className="w-4 h-4" />
                </a>

                <a
                  href="https://wa.me/918839714081?text=Hello%20Aarambh%20Institute%2C%20I%20want%20to%20enquire%20about%20admissions."
                  target="_blank"
                  rel="noopener noreferrer"
                  className="w-full py-2.5 rounded-xl text-center text-xs font-bold text-emerald-800 bg-emerald-50 hover:bg-emerald-100 border border-emerald-200 transition-all flex items-center justify-center gap-1.5"
                >
                  <MessageCircle className="w-3.5 h-3.5 text-emerald-600" />
                  <span>Enquire on WhatsApp (88397-14081)</span>
                </a>
              </div>
            </div>
            </Reveal>
          ))}
        </div>
      </div>
    </section>
  );
}
