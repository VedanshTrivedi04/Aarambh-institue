"use client";

import React, { useState } from "react";
import {
  BookOpen,
  CheckCircle2,
  Clock,
  Calendar,
  Sparkles,
  TrendingUp,
} from "lucide-react";

interface SyllabusChapter {
  id: string;
  chapter_number: number;
  title: string;
  unit: string;
  weightage: string;
  status: "COMPLETED" | "IN_PROGRESS" | "UPCOMING";
  completed_date?: string;
  board_coverage: "MP Board & CBSE" | "NEET High-Yield" | "Foundation";
  test_conducted?: string;
}

export default function TeacherSyllabusPage() {
  const [selectedTrack, setSelectedTrack] = useState<"c12_bio" | "neet_bio">("c12_bio");

  const [chapters, setChapters] = useState<SyllabusChapter[]>([
    {
      id: "ch-1",
      chapter_number: 1,
      title: "Sexual Reproduction in Flowering Plants",
      unit: "Unit VI: Reproduction",
      weightage: "7 Marks",
      status: "COMPLETED",
      completed_date: "15 Aug 2026",
      board_coverage: "MP Board & CBSE",
      test_conducted: "Unit Mock #1 (Avg 91%)",
    },
    {
      id: "ch-2",
      chapter_number: 2,
      title: "Human Reproduction & Reproductive Health",
      unit: "Unit VI: Reproduction",
      weightage: "8 Marks",
      status: "COMPLETED",
      completed_date: "28 Aug 2026",
      board_coverage: "MP Board & CBSE",
      test_conducted: "Unit Mock #2 (Avg 89%)",
    },
    {
      id: "ch-3",
      chapter_number: 3,
      title: "Principles of Inheritance & Variation (Genetics I)",
      unit: "Unit VII: Genetics & Evolution",
      weightage: "10 Marks",
      status: "COMPLETED",
      completed_date: "12 Sep 2026",
      board_coverage: "MP Board & CBSE",
      test_conducted: "Genetics Test (Avg 93%)",
    },
    {
      id: "ch-4",
      chapter_number: 4,
      title: "Molecular Basis of Inheritance (DNA & Replication)",
      unit: "Unit VII: Genetics & Evolution",
      weightage: "10 Marks",
      status: "COMPLETED",
      completed_date: "18 Sep 2026",
      board_coverage: "MP Board & CBSE",
      test_conducted: "Molecular Biology Test",
    },
    {
      id: "ch-5",
      chapter_number: 5,
      title: "Body Fluids & Circulation (Heart, ECG & Blood)",
      unit: "Unit V: Human Physiology Special",
      weightage: "8 Marks",
      status: "IN_PROGRESS",
      board_coverage: "MP Board & CBSE",
      test_conducted: "Mock Test Scheduled for 24 Sep",
    },
    {
      id: "ch-6",
      chapter_number: 6,
      title: "Excretory Products and their Elimination",
      unit: "Unit V: Human Physiology Special",
      weightage: "6 Marks",
      status: "UPCOMING",
      board_coverage: "MP Board & CBSE",
    },
    {
      id: "ch-7",
      chapter_number: 7,
      title: "Neural Control and Coordination (Brain & Reflex)",
      unit: "Unit V: Human Physiology Special",
      weightage: "7 Marks",
      status: "UPCOMING",
      board_coverage: "MP Board & CBSE",
    },
    {
      id: "ch-8",
      chapter_number: 8,
      title: "Biotechnology: Principles and Processes",
      unit: "Unit IX: Biotechnology",
      weightage: "9 Marks",
      status: "UPCOMING",
      board_coverage: "MP Board & CBSE",
    },
  ]);

  const toggleStatus = (id: string) => {
    setChapters((prev) =>
      prev.map((c) => {
        if (c.id === id) {
          const nextStatus =
            c.status === "COMPLETED"
              ? "IN_PROGRESS"
              : c.status === "IN_PROGRESS"
              ? "COMPLETED"
              : "IN_PROGRESS";
          return {
            ...c,
            status: nextStatus,
            completed_date: nextStatus === "COMPLETED" ? "Today" : c.completed_date,
          };
        }
        return c;
      })
    );
  };

  const completedCount = chapters.filter((c) => c.status === "COMPLETED").length;
  const inProgressCount = chapters.filter((c) => c.status === "IN_PROGRESS").length;
  const overallPct = Math.round((completedCount / chapters.length) * 100);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 text-xs font-bold text-slate-500 mb-1">
            <span>Faculty</span>
            <span>/</span>
            <span className="text-[#c22329]">Syllabus & Curriculum</span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-black text-slate-900">
            Curriculum Tracker & Board Roadmap
          </h1>
          <p className="text-xs text-slate-500 mt-0.5">
            Chapter completion schedule aligned with MP Board, CBSE & NEET 2026-27 timelines.
          </p>
        </div>

        <div className="flex items-center gap-2">
          <span className="px-3.5 py-1.5 rounded-xl bg-emerald-50 border border-emerald-200 text-xs font-bold text-emerald-700 flex items-center gap-1.5">
            <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600" />
            <span>Curriculum Ahead of Schedule</span>
          </span>
        </div>
      </div>

      {/* KPI Progress Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <div className="bg-white p-5 rounded-3xl border border-slate-200/90 shadow-sm space-y-2">
          <span className="text-xs font-bold text-slate-500">Overall Coverage</span>
          <div className="text-2xl sm:text-3xl font-black text-emerald-700">
            {overallPct}% Completed
          </div>
          <div className="w-full bg-slate-100 h-2 rounded-full overflow-hidden mt-2">
            <div
              className="bg-emerald-500 h-full rounded-full transition-all"
              style={{ width: `${overallPct}%` }}
            />
          </div>
        </div>

        <div className="bg-white p-5 rounded-3xl border border-slate-200/90 shadow-sm space-y-2">
          <span className="text-xs font-bold text-slate-500">Completed & Tested</span>
          <div className="text-2xl sm:text-3xl font-black text-slate-900">
            {completedCount} Chapters
          </div>
          <p className="text-xs text-slate-500">Full model question papers evaluated</p>
        </div>

        <div className="bg-white p-5 rounded-3xl border border-slate-200/90 shadow-sm space-y-2">
          <span className="text-xs font-bold text-slate-500">Currently in Lecture</span>
          <div className="text-2xl sm:text-3xl font-black text-[#c22329]">
            Chapter 18 (Circulation)
          </div>
          <p className="text-xs text-slate-500">Target completion: 26 September</p>
        </div>
      </div>

      {/* Chapters Table */}
      <div className="bg-white rounded-3xl border border-slate-200/90 overflow-hidden shadow-sm space-y-4 p-6">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-slate-100 pb-4">
          <div>
            <span className="text-[10px] font-extrabold text-[#c99a5e] uppercase tracking-wider">
              Class 12th Senior Biology Unit Breakdown
            </span>
            <h2 className="text-lg font-bold text-slate-900 mt-0.5">NCERT & MP Board Core Syllabus</h2>
            <p className="text-xs text-slate-500">
              Session 2026-27 • Instructed by Mr. Pankaj Dubey (30 Yrs Exp)
            </p>
          </div>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-50 border-b border-slate-200 text-slate-500 uppercase text-[10px] font-extrabold tracking-wider">
              <tr>
                <th className="py-3.5 px-4">Ch #</th>
                <th className="py-3.5 px-4">Chapter Title & Unit</th>
                <th className="py-3.5 px-4">Board Weightage</th>
                <th className="py-3.5 px-4">Completion Status</th>
                <th className="py-3.5 px-4">Mock Test Milestone</th>
                <th className="py-3.5 px-4 text-right">Quick Update</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 font-medium">
              {chapters.map((ch) => (
                <tr key={ch.id} className="hover:bg-slate-50/70 transition-colors">
                  <td className="py-3.5 px-4 font-mono font-bold text-slate-400">
                    Ch {ch.chapter_number}
                  </td>
                  <td className="py-3.5 px-4">
                    <div className="font-bold text-slate-900 text-sm">{ch.title}</div>
                    <div className="text-[10px] text-slate-500">{ch.unit}</div>
                  </td>
                  <td className="py-3.5 px-4">
                    <span className="font-bold text-[#c99a5e] bg-amber-50 px-2 py-0.5 rounded border border-amber-200/60">
                      {ch.weightage}
                    </span>
                  </td>
                  <td className="py-3.5 px-4">
                    <span
                      className={`px-2.5 py-0.5 rounded-full text-[10px] font-black uppercase border ${
                        ch.status === "COMPLETED"
                          ? "bg-emerald-50 text-emerald-700 border-emerald-200"
                          : ch.status === "IN_PROGRESS"
                          ? "bg-red-50 text-[#c22329] border-red-200"
                          : "bg-slate-100 text-slate-600 border-slate-200"
                      }`}
                    >
                      {ch.status}
                    </span>
                    {ch.completed_date && (
                      <span className="block text-[10px] text-slate-400 mt-0.5">
                        Finished on {ch.completed_date}
                      </span>
                    )}
                  </td>
                  <td className="py-3.5 px-4 text-slate-700">
                    {ch.test_conducted ? (
                      <span className="flex items-center gap-1 text-[11px] font-semibold text-slate-800">
                        <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600 shrink-0" />
                        <span>{ch.test_conducted}</span>
                      </span>
                    ) : (
                      <span className="text-slate-400 italic text-[11px]">Pending chapter completion</span>
                    )}
                  </td>
                  <td className="py-3.5 px-4 text-right">
                    <button
                      onClick={() => toggleStatus(ch.id)}
                      className="px-2.5 py-1 rounded-lg bg-slate-100 hover:bg-slate-200 text-slate-700 font-bold text-[11px] transition-colors cursor-pointer"
                    >
                      Toggle Status
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
