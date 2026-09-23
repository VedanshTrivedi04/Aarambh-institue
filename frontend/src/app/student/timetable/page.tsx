"use client";

import React, { useEffect, useState } from "react";
import {
  Clock,
  MapPin,
  Users,
  BookOpen,
  Loader2,
  AlertTriangle,
} from "lucide-react";
import { authFetch } from "@/lib/auth";

const DAYS = ["MON", "TUE", "WED", "THU", "FRI", "SAT", "SUN"];
const DAY_LABELS: Record<string, string> = {
  MON: "Monday",
  TUE: "Tuesday",
  WED: "Wednesday",
  THU: "Thursday",
  FRI: "Friday",
  SAT: "Saturday",
  SUN: "Sunday",
};

interface ClassEntry {
  batch_id: string;
  batch_name: string;
  start_time: string | null;
  end_time: string | null;
  room: string | null;
  teacher_name: string | null;
}

export default function StudentTimetablePage() {
  const [selectedDay, setSelectedDay] = useState("MON");
  const [schedule, setSchedule] = useState<Record<string, ClassEntry[]>>({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    (async () => {
      setLoading(true);
      const enrollRes = await authFetch<any[]>("/api/v1/me/enrollments");
      if (enrollRes.error) {
        setError(enrollRes.error);
        setLoading(false);
        return;
      }
      const active = ((enrollRes.data as any) || []).filter((e: any) => e.status === "ACTIVE");

      const batches = await Promise.all(
        active.map((e: any) => authFetch<any>(`/api/v1/admin/academic/batches/${e.batch_id}`))
      );

      const teacherIds = Array.from(
        new Set(batches.map((b) => (b.data as any)?.teacher_id).filter(Boolean))
      );
      const teacherProfiles = await Promise.all(
        teacherIds.map((id) => authFetch<any>(`/api/v1/admin/people/teachers/${id}`))
      );
      const teacherNameById = new Map(
        teacherIds.map((id, idx) => {
          const p = (teacherProfiles[idx].data as any)?.data;
          return [id, p ? `${p.first_name} ${p.last_name || ""}`.trim() : null];
        })
      );

      const map: Record<string, ClassEntry[]> = {};
      for (const b of batches) {
        const batch = b.data as any;
        if (!batch || !batch.days) continue;
        const entry: ClassEntry = {
          batch_id: batch.id,
          batch_name: batch.name,
          start_time: batch.start_time,
          end_time: batch.end_time,
          room: batch.room,
          teacher_name: batch.teacher_id ? teacherNameById.get(batch.teacher_id) || null : null,
        };
        for (const day of batch.days as string[]) {
          if (!map[day]) map[day] = [];
          map[day].push(entry);
        }
      }
      for (const day of Object.keys(map)) {
        map[day].sort((a, b) => (a.start_time || "").localeCompare(b.start_time || ""));
      }
      setSchedule(map);
      const firstDayWithClasses = DAYS.find((d) => map[d]?.length) || "MON";
      setSelectedDay(firstDayWithClasses);
      setLoading(false);
    })();
  }, []);

  const todaysClasses = schedule[selectedDay] || [];

  return (
    <div className="space-y-6 max-w-6xl mx-auto">
      <div className="bg-white rounded-3xl border border-slate-200/90 p-6 sm:p-8 shadow-sm">
        <h1 className="text-2xl font-black text-slate-900 tracking-tight">
          Classes & Weekly Timetable
        </h1>
        <p className="text-xs text-slate-500 mt-1 font-medium">
          Your recurring weekly class schedule across all enrolled batches.
        </p>
      </div>

      {error && (
        <div className="p-3.5 rounded-2xl bg-red-50 border border-red-200 text-[#c22329] text-xs flex items-center gap-2">
          <AlertTriangle className="w-4 h-4" />
          <span className="font-semibold">{error}</span>
        </div>
      )}

      {loading ? (
        <div className="flex items-center justify-center py-16 text-slate-500 gap-2 text-sm font-bold">
          <Loader2 className="w-5 h-5 animate-spin" />
          <span>Loading your timetable…</span>
        </div>
      ) : (
        <>
          {/* Day Selector */}
          <div className="flex gap-2 overflow-x-auto pb-1">
            {DAYS.map((day) => (
              <button
                key={day}
                onClick={() => setSelectedDay(day)}
                className={`px-4 py-2 rounded-xl text-xs font-bold whitespace-nowrap transition-all cursor-pointer border ${
                  selectedDay === day
                    ? "bg-[#c22329] text-white border-[#c22329] shadow-md"
                    : "bg-white text-slate-600 border-slate-200 hover:border-slate-300"
                }`}
              >
                {DAY_LABELS[day]}
                {schedule[day]?.length ? (
                  <span className="ml-1.5 opacity-70">({schedule[day].length})</span>
                ) : null}
              </button>
            ))}
          </div>

          {/* Classes for Selected Day */}
          <div className="bg-white rounded-3xl border border-slate-200/90 p-6 shadow-sm space-y-4">
            <h2 className="text-base font-black text-slate-900 flex items-center gap-2">
              <BookOpen className="w-4 h-4 text-[#c22329]" />
              <span>{DAY_LABELS[selectedDay]}'s Classes</span>
            </h2>

            {todaysClasses.length === 0 ? (
              <div className="py-10 text-center text-sm text-slate-500">
                No classes scheduled on {DAY_LABELS[selectedDay]}.
              </div>
            ) : (
              <div className="space-y-3">
                {todaysClasses.map((c, idx) => (
                  <div key={idx} className="p-4 rounded-2xl border border-slate-200 bg-slate-50/60">
                    <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
                      <span className="text-xs font-extrabold text-slate-700 bg-white px-2.5 py-1 rounded-lg border border-slate-200 shadow-xs inline-flex items-center gap-1.5 w-fit">
                        <Clock className="w-3.5 h-3.5 text-[#c22329]" />
                        {c.start_time} - {c.end_time}
                      </span>
                      <h3 className="text-sm font-bold text-slate-900">{c.batch_name}</h3>
                    </div>
                    <div className="flex flex-wrap items-center gap-3 mt-2 text-xs text-slate-500 font-medium">
                      {c.teacher_name && (
                        <span className="flex items-center gap-1 text-slate-700">
                          <Users className="w-3.5 h-3.5 text-slate-400" />
                          {c.teacher_name}
                        </span>
                      )}
                      {c.room && (
                        <span className="flex items-center gap-1 text-slate-600">
                          <MapPin className="w-3.5 h-3.5 text-[#c99a5e]" />
                          {c.room}
                        </span>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </>
      )}
    </div>
  );
}
