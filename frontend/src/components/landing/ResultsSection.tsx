"use client";

import React, { useState } from "react";
import { Trophy, Award, Star, CheckCircle2, Medal } from "lucide-react";
import Reveal from "@/components/ui/Reveal";
import CountUp from "@/components/ui/CountUp";

export default function ResultsSection() {
  const [filter, setFilter] = useState<string>("all");

  const featuredToppers = [
    {
      name: "Prince",
      grade: "Class 12th",
      board: "MP Board",
      score: "94%",
      marks: "580 / 600",
      rank: "Rank 1st",
      year: "2023",
      subjects: "Maths: 100/100 • Physics: 99/100",
      quote: "Aarambh ne mujhe sahi direction diya aur regular practice sets ki wajah se board exam mein top rank mili.",
      badgeColor: "bg-amber-100 text-amber-900 border-amber-300",
      avatarBg: "bg-amber-50 text-amber-700",
      initials: "PR",
    },
    {
      name: "Rohit Garg",
      grade: "Class 10th",
      board: "MP Board",
      score: "91%",
      marks: "Board Distinction",
      rank: "Rank 2nd",
      year: "2024",
      subjects: "Maths & Physics Topper",
      quote: "Proud to be an Aarambhian! The teachers personally cleared every doubt before the exams.",
      badgeColor: "bg-blue-100 text-blue-900 border-blue-300",
      avatarBg: "bg-blue-50 text-blue-700",
      initials: "RG",
    },
    {
      name: "Payal Sharma",
      grade: "Class 10th",
      board: "MP Board",
      score: "89%",
      marks: "Board Distinction",
      rank: "Rank 3rd",
      year: "2024",
      subjects: "Maths & Chemistry Distinction",
      quote: "Aarambh didn't just teach me, it transformed me. Concepts were made crystal clear.",
      badgeColor: "bg-emerald-100 text-emerald-900 border-emerald-300",
      avatarBg: "bg-emerald-50 text-emerald-700",
      initials: "PS",
    },
  ];

  const allToppers = [
    { name: "Prince", class: "12th", board: "MP Board", score: "94%", year: "2023", highlight: "Rank 1st (Maths 100/100)" },
    { name: "Rohit Garg", class: "10th", board: "MP Board", score: "91%", year: "2024", highlight: "Rank 2nd" },
    { name: "Payal Sharma", class: "10th", board: "MP Board", score: "89%", year: "2024", highlight: "Rank 3rd" },
    { name: "Neha Yadav", class: "10th", board: "MP Board", score: "89%", year: "2023", highlight: "Distinction" },
    { name: "Nupur", class: "10th", board: "CBSE", score: "89%", year: "2023", highlight: "Distinction" },
    { name: "Monika", class: "12th", board: "CBSE", score: "85%", year: "2024", highlight: "Distinction" },
    { name: "Ritika Sarothiya", class: "10th", board: "CBSE", score: "85%", year: "2025", highlight: "Distinction" },
    { name: "Nishtha Jain", class: "10th", board: "MP Board", score: "83%", year: "2025", highlight: "First Division" },
    { name: "Shrishti Yadav", class: "9th", board: "MP Board", score: "A Grade", year: "2025", highlight: "Class Topper" },
    { name: "Vanshika Yadav", class: "7th", board: "MP Board", score: "A Grade", year: "2025", highlight: "Class Topper" },
    { name: "Atharva Choudhary", class: "8th", board: "CBSE", score: "A Grade", year: "2025", highlight: "School Star" },
  ];

  return (
    <section id="results" className="relative py-24 bg-[#f8fafd] text-slate-900 border-b border-slate-200/80">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <Reveal className="text-center max-w-3xl mx-auto space-y-4">
          <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-amber-50 border border-amber-200 text-amber-800 text-xs font-bold uppercase tracking-wider">
            <Trophy className="w-3.5 h-3.5 text-amber-600" />
            <span>Our Hall of Fame & Toppers</span>
          </div>

          <h2 className="text-3xl sm:text-5xl font-black tracking-tight text-slate-900">
            Aarambh Institute <br />
            <span className="text-[#c22329]">Board Examination Achievers</span>
          </h2>

          <p className="text-sm sm:text-base text-slate-600">
            2,000+ successful students since 2015 with an 85% average score and 98.5% highest mark in Class 10 MP Board.
          </p>
        </Reveal>

        {/* Highlight Stats Pill */}
        <Reveal delay={100} className="mt-10 mb-14 p-6 rounded-3xl bg-white border border-slate-200 shadow-md max-w-4xl mx-auto">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-6 text-center divide-y md:divide-y-0 md:divide-x divide-slate-100">
            <div className="pt-2 md:pt-0">
              <CountUp value="98.5%" className="stat-pop inline-block text-3xl sm:text-4xl font-black text-[#c22329]" />
              <p className="text-xs font-bold text-slate-600 mt-1">Highest Board Score</p>
            </div>
            <div className="pt-4 md:pt-0">
              <CountUp value="85%" className="stat-pop inline-block text-3xl sm:text-4xl font-black text-amber-600" />
              <p className="text-xs font-bold text-slate-600 mt-1">Average Student Score</p>
            </div>
            <div className="pt-4 md:pt-0">
              <CountUp value="98%" className="stat-pop inline-block text-3xl sm:text-4xl font-black text-emerald-600" />
              <p className="text-xs font-bold text-slate-600 mt-1">Overall Result Pass Rate</p>
            </div>
            <div className="pt-4 md:pt-0">
              <CountUp value="2,000+" className="stat-pop inline-block text-3xl sm:text-4xl font-black text-blue-700" />
              <p className="text-xs font-bold text-slate-600 mt-1">Students Passed (2015-26)</p>
            </div>
          </div>
        </Reveal>

        {/* Featured Profile Cards (Prince, Rohit, Payal) */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-12">
          {featuredToppers.map((student, idx) => (
            <Reveal key={idx} delay={idx * 100} direction="up" distance={24}>
            <div
              className="light-card-interactive hover-lift p-6 sm:p-7 rounded-3xl flex flex-col justify-between h-full"
            >
              <div>
                <div className="flex items-center justify-between mb-4">
                  <div className="flex items-center gap-3">
                    <div className={`w-12 h-12 rounded-2xl ${student.avatarBg} border border-slate-200 flex items-center justify-center font-black text-lg shadow-sm`}>
                      {student.initials}
                    </div>
                    <div>
                      <h4 className="font-bold text-base text-slate-900">
                        {student.name}
                      </h4>
                      <p className="text-xs text-slate-500 font-medium">
                        {student.grade} • {student.board} ({student.year})
                      </p>
                    </div>
                  </div>

                  <span className={`text-xs font-black px-3 py-1 rounded-full border ${student.badgeColor}`}>
                    {student.rank}
                  </span>
                </div>

                <div className="p-3.5 rounded-2xl bg-slate-50 border border-slate-100 mb-4 space-y-1 text-xs">
                  <div className="flex items-center justify-between">
                    <span className="text-slate-500 font-medium">Board Score:</span>
                    <span className="text-[#c22329] font-black text-sm">{student.score}</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-slate-500 font-medium">Marks / Subject:</span>
                    <span className="text-slate-900 font-bold">{student.subjects}</span>
                  </div>
                </div>

                <div className="relative pl-3 border-l-2 border-amber-400 text-xs text-slate-600 italic leading-relaxed font-normal">
                  &ldquo;{student.quote}&rdquo;
                </div>
              </div>

              <div className="pt-4 mt-4 border-t border-slate-100 flex items-center justify-between text-[11px] text-slate-500 font-medium">
                <span className="flex items-center gap-1 text-emerald-700 font-bold">
                  <CheckCircle2 className="w-3.5 h-3.5" />
                  Verified Aarambh Topper
                </span>
                <span className="text-slate-400">Classroom Batch</span>
              </div>
            </div>
            </Reveal>
          ))}
        </div>

        {/* Complete Toppers Table Grid */}
        <Reveal className="bg-white p-6 sm:p-8 rounded-3xl border border-slate-200 shadow-md">
          <div className="flex items-center justify-between border-b border-slate-100 pb-4 mb-4">
            <h3 className="font-extrabold text-lg text-slate-900 flex items-center gap-2">
              <Medal className="w-5 h-5 text-amber-500" />
              <span>Full Hall of Fame Student Roll</span>
            </h3>
            <span className="text-xs font-semibold text-slate-500">
              MP Board & CBSE Toppers (2023 - 2025)
            </span>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs sm:text-sm">
              <thead>
                <tr className="border-b border-slate-100 text-slate-500 font-bold">
                  <th className="py-2.5 px-3">Student Name</th>
                  <th className="py-2.5 px-3">Class</th>
                  <th className="py-2.5 px-3">Board</th>
                  <th className="py-2.5 px-3">Score / Grade</th>
                  <th className="py-2.5 px-3">Year</th>
                  <th className="py-2.5 px-3">Highlight</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {allToppers.map((t, i) => (
                  <tr key={i} className="hover:bg-slate-50/80 transition-colors font-medium text-slate-700">
                    <td className="py-3 px-3 font-bold text-slate-900">{t.name}</td>
                    <td className="py-3 px-3">{t.class}</td>
                    <td className="py-3 px-3">{t.board}</td>
                    <td className="py-3 px-3 font-black text-[#c22329]">{t.score}</td>
                    <td className="py-3 px-3 text-slate-500">{t.year}</td>
                    <td className="py-3 px-3">
                      <span className="px-2 py-0.5 rounded-full bg-slate-100 text-slate-800 text-xs font-semibold">
                        {t.highlight}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </Reveal>
      </div>
    </section>
  );
}
