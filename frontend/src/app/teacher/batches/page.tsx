"use client";

import React, { useState } from "react";
import {
  Users,
  Search,
  Phone,
  MessageCircle,
  Clock,
  BookOpen,
  Award,
  CheckCircle2,
  AlertCircle,
  Plus,
} from "lucide-react";

interface StudentInBatch {
  id: string;
  admission_number: string;
  student_name: string;
  board: string;
  attendance_pct: number;
  average_score: number;
  grade: string;
  parent_name: string;
  parent_phone: string;
  recent_remark: string;
}

export default function TeacherBatchesPage() {
  const [selectedBatch, setSelectedBatch] = useState<"b1" | "b2" | "b3">("b1");
  const [search, setSearch] = useState("");

  const batches = [
    {
      id: "b1",
      name: "Class 12th Senior Biology (Board + NEET)",
      timings: "5:00 PM - 6:30 PM",
      room: "Room 201",
      enrolled: 19,
      capacity: 20,
      board: "MP Board / CBSE",
    },
    {
      id: "b2",
      name: "NEET Medical Specialist Foundation",
      timings: "6:30 PM - 7:30 PM",
      room: "Room 201",
      enrolled: 20,
      capacity: 20,
      board: "NCERT / Medical Entrance",
    },
    {
      id: "b3",
      name: "Class 11th Senior Biology",
      timings: "4:00 PM - 5:00 PM",
      room: "Room 201",
      enrolled: 18,
      capacity: 20,
      board: "MP Board / CBSE",
    },
  ];

  const studentsList: Record<string, StudentInBatch[]> = {
    b1: [
      {
        id: "s1",
        admission_number: "AAR-2026-001",
        student_name: "Prince Yadav",
        board: "MP Board",
        attendance_pct: 98,
        average_score: 96,
        grade: "A+ (Rank 1st)",
        parent_name: "Sanjay Yadav",
        parent_phone: "9826011122",
        recent_remark: "Excellent in Human Physiology diagrams.",
      },
      {
        id: "s6",
        admission_number: "AAR-2026-006",
        student_name: "Monika Patidar",
        board: "CBSE",
        attendance_pct: 91,
        average_score: 89,
        grade: "Distinction",
        parent_name: "Ramesh Patidar",
        parent_phone: "7909714081",
        recent_remark: "Needs extra practice on plant histology.",
      },
      {
        id: "s3",
        admission_number: "AAR-2026-003",
        student_name: "Payal Sharma",
        board: "MP Board",
        attendance_pct: 94,
        average_score: 91,
        grade: "A+",
        parent_name: "Kishore Sharma",
        parent_phone: "9893077889",
        recent_remark: "Active questioner in class discussions.",
      },
      {
        id: "s4",
        admission_number: "AAR-2026-004",
        student_name: "Neha Yadav",
        board: "MP Board",
        attendance_pct: 92,
        average_score: 85,
        grade: "First Class",
        parent_name: "Satish Yadav",
        parent_phone: "9755012345",
        recent_remark: "Regular submitter of homework DPPs.",
      },
      {
        id: "s5",
        admission_number: "AAR-2026-005",
        student_name: "Nupur Joshi",
        board: "CBSE",
        attendance_pct: 97,
        average_score: 88,
        grade: "Distinction",
        parent_name: "Anil Joshi",
        parent_phone: "8839714081",
        recent_remark: "Strong conceptual clarity in genetics.",
      },
      {
        id: "s8",
        admission_number: "AAR-2026-008",
        student_name: "Yashika Mehta",
        board: "CBSE",
        attendance_pct: 95,
        average_score: 84,
        grade: "First Class",
        parent_name: "Rajesh Mehta",
        parent_phone: "9827055441",
        recent_remark: "Improvement noted in monthly test series.",
      },
    ],
    b2: [
      {
        id: "s1",
        admission_number: "AAR-2026-001",
        student_name: "Prince Yadav",
        board: "NEET Medical",
        attendance_pct: 99,
        average_score: 97,
        grade: "Rank 1st (NEET)",
        parent_name: "Sanjay Yadav",
        parent_phone: "9826011122",
        recent_remark: "Targeting 680+ in NEET 2027.",
      },
      {
        id: "s2",
        admission_number: "AAR-2026-002",
        student_name: "Rohit Garg",
        board: "NEET Medical",
        attendance_pct: 96,
        average_score: 93,
        grade: "Rank 2nd",
        parent_name: "Manoj Garg",
        parent_phone: "9425033445",
        recent_remark: "Very fast calculation speed in genetics.",
      },
      {
        id: "s6",
        admission_number: "AAR-2026-006",
        student_name: "Monika Patidar",
        board: "NEET Medical",
        attendance_pct: 94,
        average_score: 90,
        grade: "Top Tier",
        parent_name: "Ramesh Patidar",
        parent_phone: "7909714081",
        recent_remark: "Attends Friday revision clinic regularly.",
      },
    ],
    b3: [
      {
        id: "s7",
        admission_number: "AAR-2026-007",
        student_name: "Dhruvika Solanki",
        board: "MP Board",
        attendance_pct: 99,
        average_score: 94,
        grade: "A+",
        parent_name: "Gopal Solanki",
        parent_phone: "9406612398",
        recent_remark: "Exemplary notebook presentation.",
      },
      {
        id: "s4",
        admission_number: "AAR-2026-004",
        student_name: "Neha Yadav",
        board: "MP Board",
        attendance_pct: 93,
        average_score: 87,
        grade: "First Class",
        parent_name: "Satish Yadav",
        parent_phone: "9755012345",
        recent_remark: "Punctual and attentive.",
      },
    ],
  };

  const currentBatch = batches.find((b) => b.id === selectedBatch) || batches[0];
  const activeStudents = studentsList[selectedBatch] || [];

  const filteredStudents = activeStudents.filter((s) => {
    const term = search.toLowerCase();
    return (
      s.student_name.toLowerCase().includes(term) ||
      s.admission_number.toLowerCase().includes(term) ||
      s.parent_phone.includes(term)
    );
  });

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 text-xs font-bold text-slate-500 mb-1">
            <span>Faculty</span>
            <span>/</span>
            <span className="text-[#c22329]">My Batches & Students</span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-black text-slate-900">
            Teaching Batches & Student Roster
          </h1>
          <p className="text-xs text-slate-500 mt-0.5">
            Strict 20-student limit policy ensures Mr. Pankaj Dubey gives 1-on-1 mentorship to every student.
          </p>
        </div>

        <div className="flex items-center gap-2">
          <span className="px-3 py-1.5 rounded-xl bg-emerald-50 border border-emerald-200 text-xs font-bold text-emerald-700">
            Strict Max 20 Guaranteed
          </span>
        </div>
      </div>

      {/* Batch Cards Selector */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {batches.map((b) => {
          const isSelected = selectedBatch === b.id;
          const isFull = b.enrolled >= b.capacity;
          const pct = Math.round((b.enrolled / b.capacity) * 100);

          return (
            <button
              key={b.id}
              onClick={() => setSelectedBatch(b.id as any)}
              className={`p-5 rounded-3xl border text-left transition-all space-y-3 cursor-pointer ${
                isSelected
                  ? "bg-white border-[#c22329] ring-2 ring-red-500/15 shadow-md"
                  : "bg-white border-slate-200/90 hover:border-slate-300 shadow-sm"
              }`}
            >
              <div className="flex items-center justify-between">
                <span className="text-[10px] font-black uppercase px-2.5 py-0.5 rounded-md bg-blue-50 text-blue-700 border border-blue-200">
                  {b.board}
                </span>
                <span className="text-xs font-bold text-slate-500">{b.room}</span>
              </div>

              <h3 className="font-bold text-sm text-slate-900 leading-snug">{b.name}</h3>

              <div className="flex items-center gap-1.5 text-xs text-slate-600 font-medium">
                <Clock className="w-3.5 h-3.5 text-[#c99a5e]" />
                <span>{b.timings}</span>
              </div>

              {/* Progress */}
              <div className="pt-2 border-t border-slate-100 space-y-1">
                <div className="flex items-center justify-between text-[11px]">
                  <span className="text-slate-500 font-medium">Batch Capacity</span>
                  <span className={`font-bold ${isFull ? "text-amber-800" : "text-emerald-700"}`}>
                    {b.enrolled} / {b.capacity} {isFull ? "(Full)" : ""}
                  </span>
                </div>
                <div className="w-full bg-slate-100 h-1.5 rounded-full overflow-hidden">
                  <div
                    className={`h-full rounded-full ${isFull ? "bg-amber-500" : "bg-emerald-500"}`}
                    style={{ width: `${pct}%` }}
                  />
                </div>
              </div>
            </button>
          );
        })}
      </div>

      {/* Student Roster Table for Selected Batch */}
      <div className="bg-white rounded-3xl border border-slate-200/90 overflow-hidden shadow-sm space-y-4 p-6">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-slate-100 pb-4">
          <div>
            <span className="text-[10px] font-extrabold text-[#c99a5e] uppercase tracking-wider">
              Enrolled Student Directory
            </span>
            <h2 className="text-lg font-bold text-slate-900 mt-0.5">{currentBatch.name}</h2>
            <p className="text-xs text-slate-500">
              Showing {filteredStudents.length} students • {currentBatch.timings} in {currentBatch.room}
            </p>
          </div>

          <div className="relative w-full sm:w-72">
            <Search className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
            <input
              type="text"
              placeholder="Search student, adm #, phone..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="w-full bg-slate-50 border border-slate-200 rounded-xl pl-9 pr-3 py-2 text-xs text-slate-900 placeholder-slate-400 focus:bg-white focus:outline-none focus:border-[#c22329]"
            />
          </div>
        </div>

        {/* Table */}
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-50 border-b border-slate-200 text-slate-500 uppercase text-[10px] font-extrabold tracking-wider">
              <tr>
                <th className="py-3 px-3">Adm # & Student</th>
                <th className="py-3 px-3">Board Track</th>
                <th className="py-3 px-3">Attendance</th>
                <th className="py-3 px-3">Performance Avg</th>
                <th className="py-3 px-3">Educator Remark</th>
                <th className="py-3 px-3 text-right">Parent Contact</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 font-medium">
              {filteredStudents.map((s) => {
                const cleanPhone = s.parent_phone.replace(/\D/g, "");

                return (
                  <tr key={s.id} className="hover:bg-slate-50/70 transition-colors">
                    <td className="py-3 px-3">
                      <div className="font-mono text-[10px] text-[#c99a5e] font-extrabold">
                        {s.admission_number}
                      </div>
                      <div className="font-bold text-slate-900 text-sm">{s.student_name}</div>
                    </td>
                    <td className="py-3 px-3">
                      <span className="px-2 py-0.5 rounded-full bg-slate-100 border border-slate-200 text-[10px] font-bold text-slate-600">
                        {s.board}
                      </span>
                    </td>
                    <td className="py-3 px-3">
                      <div className="flex items-center gap-1.5">
                        <div className="w-12 bg-slate-100 rounded-full h-1.5 overflow-hidden">
                          <div
                            className="bg-emerald-500 h-full rounded-full"
                            style={{ width: `${s.attendance_pct}%` }}
                          />
                        </div>
                        <span className="font-bold text-emerald-700">{s.attendance_pct}%</span>
                      </div>
                    </td>
                    <td className="py-3 px-3">
                      <span className="font-bold text-slate-900">{s.average_score}%</span>
                      <span className="block text-[10px] text-amber-800 font-bold">{s.grade}</span>
                    </td>
                    <td className="py-3 px-3 text-slate-600 max-w-xs text-[11px] italic">
                      &quot;{s.recent_remark}&quot;
                    </td>
                    <td className="py-3 px-3 text-right">
                      <div className="inline-flex items-center gap-1.5">
                        <a
                          href={`tel:${s.parent_phone}`}
                          title="Call Parent"
                          className="p-1.5 rounded-lg bg-slate-100 text-slate-700 hover:text-[#c22329] hover:bg-red-50 border border-slate-200 transition-colors"
                        >
                          <Phone className="w-3.5 h-3.5" />
                        </a>
                        <a
                          href={`https://wa.me/91${cleanPhone}?text=Hello%20${encodeURIComponent(
                            s.parent_name
                          )}%2C%20this%20is%20Mr.%20Pankaj%20Dubey%20(Biology%20Faculty)%20from%20Aarambh%20Institute%20regarding%20${encodeURIComponent(
                            s.student_name
                          )}.`}
                          target="_blank"
                          rel="noopener noreferrer"
                          title="WhatsApp Parent"
                          className="p-1.5 rounded-lg bg-emerald-50 text-emerald-700 border border-emerald-200 hover:bg-emerald-100 transition-colors"
                        >
                          <MessageCircle className="w-3.5 h-3.5" />
                        </a>
                      </div>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
