"use client";

import React, { useState, useEffect } from "react";
import Link from "next/link";
import { authFetch } from "@/lib/auth";
import {
  Users,
  UserCheck,
  GraduationCap,
  Sparkles,
  ArrowRight,
  Plus,
  Phone,
  CalendarCheck,
  CheckCircle2,
  Loader2,
} from "lucide-react";

interface DashboardKPIs {
  total_students: number;
  total_batches: number;
  total_teachers: number;
  total_enquiries_open: number;
  overall_attendance_rate: number;
}

interface TodaySession {
  id: string;
  batch_id: string;
  start_time: string;
  room: string | null;
  status: string;
  batch_name: string;
  teacher_name: string | null;
}

function todayISO() {
  return new Date().toISOString().slice(0, 10);
}

export default function AdminDashboardPage() {
  const [enquiries, setEnquiries] = useState<any[]>([]);
  const [kpis, setKpis] = useState<DashboardKPIs | null>(null);
  const [todaySessions, setTodaySessions] = useState<TodaySession[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadData() {
      setLoading(true);

      const [enquiryRes, kpiRes, batchRes, teacherRes] = await Promise.all([
        authFetch<{ items: any[] }>("/api/v1/admin/enquiries?page=1&page_size=5"),
        authFetch<{ data: DashboardKPIs }>("/api/v1/analytics/dashboard"),
        authFetch<any[]>("/api/v1/admin/academic/batches"),
        authFetch<{ items: any[] }>("/api/v1/admin/people/teachers?page_size=100"),
      ]);

      setEnquiries((enquiryRes.data as any)?.items || []);
      if (kpiRes.data) setKpis((kpiRes.data as any).data);

      const batches = (batchRes.data as any) || [];
      const teachers = (teacherRes.data as any)?.items || [];
      const teacherNameById = new Map(teachers.map((t: any) => [t.id, `${t.first_name} ${t.last_name || ""}`.trim()]));

      const today = todayISO();
      const sessionRes = await authFetch<{ items: any[] }>(
        `/api/v1/operations/sessions?date_from=${today}&date_to=${today}&page_size=20`
      );
      const sessions = (sessionRes.data as any)?.items || [];
      const batchById = new Map<string, any>(batches.map((b: any) => [b.id, b]));

      setTodaySessions(
        sessions.map((s: any) => {
          const batch = batchById.get(s.batch_id);
          return {
            id: s.id,
            batch_id: s.batch_id,
            start_time: s.start_time,
            room: s.room,
            status: s.status,
            batch_name: batch?.name || "Unknown Batch",
            teacher_name: s.conducted_by ? teacherNameById.get(s.conducted_by) || null : null,
          };
        }).sort((a: TodaySession, b: TodaySession) => a.start_time.localeCompare(b.start_time))
      );

      setLoading(false);
    }
    loadData();
  }, []);

  return (
    <div className="space-y-6">
      {/* Top Greeting & Quick Actions */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 bg-white p-6 sm:p-7 rounded-3xl border border-slate-200/90 shadow-sm">
        <div>
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-red-50 text-[#c22329] border border-red-200 text-xs font-bold mb-2">
            <Sparkles className="w-3.5 h-3.5 text-amber-500" />
            <span>Aarambh Institute Admin Operations</span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-black text-slate-900">
            Welcome, Administrator
          </h1>
        </div>

        <div className="flex flex-wrap items-center gap-2.5">
          <Link
            href="/admin/enquiries"
            className="btn-caramel-gold inline-flex items-center gap-2 px-4 py-2.5 rounded-xl font-bold text-xs shadow-md"
          >
            <Plus className="w-3.5 h-3.5" />
            <span>New Walk-in Enquiry</span>
          </Link>

          <Link
            href="/admin/attendance"
            className="inline-flex items-center gap-2 px-4 py-2.5 rounded-xl font-bold text-xs bg-slate-100 hover:bg-slate-200/80 text-slate-700 border border-slate-200 transition-colors"
          >
            <CalendarCheck className="w-3.5 h-3.5 text-[#c22329]" />
            <span>Mark Attendance</span>
          </Link>
        </div>
      </div>

      {/* KPI Cards */}
      {loading ? (
        <div className="flex items-center justify-center py-10 text-slate-500 gap-2 text-sm font-bold">
          <Loader2 className="w-5 h-5 animate-spin" />
          <span>Loading dashboard…</span>
        </div>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          {/* Card 1: Leads */}
          <div className="bg-white p-5 rounded-3xl border border-slate-200/90 shadow-sm space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-xs font-bold text-slate-500">Open Enquiries</span>
              <div className="w-8 h-8 rounded-xl bg-red-50 text-[#c22329] border border-red-200 flex items-center justify-center">
                <UserCheck className="w-4 h-4" />
              </div>
            </div>
            <div className="text-2xl font-black text-slate-900">{kpis?.total_enquiries_open ?? 0}</div>
          </div>

          {/* Card 2: Active Students */}
          <div className="bg-white p-5 rounded-3xl border border-slate-200/90 shadow-sm space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-xs font-bold text-slate-500">Active Students</span>
              <div className="w-8 h-8 rounded-xl bg-blue-50 text-blue-600 border border-blue-200 flex items-center justify-center">
                <GraduationCap className="w-4 h-4" />
              </div>
            </div>
            <div className="text-2xl font-black text-slate-900">{kpis?.total_students ?? 0}</div>
            <div className="flex items-center gap-1.5 text-[11px] text-blue-700 font-bold bg-blue-50 border border-blue-200/60 px-2 py-0.5 rounded-full w-fit">
              <span>{kpis?.total_batches ?? 0} Batches</span>
            </div>
          </div>

          {/* Card 3: Faculty */}
          <div className="bg-white p-5 rounded-3xl border border-slate-200/90 shadow-sm space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-xs font-bold text-slate-500">Teaching Faculty</span>
              <div className="w-8 h-8 rounded-xl bg-amber-50 text-[#c99a5e] border border-amber-200 flex items-center justify-center">
                <Users className="w-4 h-4" />
              </div>
            </div>
            <div className="text-2xl font-black text-slate-900">{kpis?.total_teachers ?? 0}</div>
          </div>

          {/* Card 4: Attendance */}
          <div className="bg-white p-5 rounded-3xl border border-slate-200/90 shadow-sm space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-xs font-bold text-slate-500">Overall Attendance</span>
              <div className="w-8 h-8 rounded-xl bg-emerald-50 text-emerald-600 border border-emerald-200 flex items-center justify-center">
                <CalendarCheck className="w-4 h-4" />
              </div>
            </div>
            <div className="text-2xl font-black text-slate-900">{(kpis?.overall_attendance_rate ?? 0).toFixed(1)}%</div>
            {(kpis?.overall_attendance_rate ?? 0) >= 90 && (
              <div className="flex items-center gap-1.5 text-[11px] text-emerald-700 font-bold bg-emerald-50 border border-emerald-200/60 px-2 py-0.5 rounded-full w-fit">
                <CheckCircle2 className="w-3.5 h-3.5" />
                <span>High Attendance Rate</span>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Grid: Recent Leads & Batch Schedule */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Recent Enquiries (8 cols) */}
        <div className="lg:col-span-8 bg-white rounded-3xl border border-slate-200/90 p-6 space-y-4 shadow-sm">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-base font-bold text-slate-900">
                Recent Admissions & Website Leads
              </h2>
            </div>
            <Link
              href="/admin/enquiries"
              className="text-xs font-bold text-[#c22329] hover:underline flex items-center gap-1"
            >
              <span>View All CRM</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </Link>
          </div>

          {/* Table */}
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-slate-50 border-b border-slate-200 text-slate-500 uppercase text-[10px] font-extrabold tracking-wider">
                <tr>
                  <th className="py-3 px-3">Student Name</th>
                  <th className="py-3 px-3">Target Class</th>
                  <th className="py-3 px-3">Contact</th>
                  <th className="py-3 px-3">Source</th>
                  <th className="py-3 px-3">Stage</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 font-medium">
                {enquiries.length === 0 && !loading && (
                  <tr>
                    <td colSpan={5} className="py-8 text-center text-slate-400">No enquiries yet.</td>
                  </tr>
                )}
                {enquiries.map((lead) => (
                  <tr key={lead.id} className="hover:bg-slate-50/70 transition-colors">
                    <td className="py-3 px-3">
                      <div className="font-bold text-slate-900">{lead.student_name}</div>
                      <div className="text-[10px] text-slate-500">Parent: {lead.parent_name || "N/A"}</div>
                    </td>
                    <td className="py-3 px-3 text-slate-700">
                      <div className="font-semibold">{lead.target_class}</div>
                    </td>
                    <td className="py-3 px-3">
                      <a
                        href={`tel:${lead.phone}`}
                        className="text-slate-800 hover:text-[#c22329] font-medium hover:underline flex items-center gap-1"
                      >
                        <Phone className="w-3 h-3 text-[#c22329]" />
                        <span>{lead.phone}</span>
                      </a>
                    </td>
                    <td className="py-3 px-3">
                      <span className="px-2 py-0.5 rounded-full bg-slate-100 border border-slate-200 text-[10px] font-bold text-slate-600">
                        {lead.source || "WEBSITE"}
                      </span>
                    </td>
                    <td className="py-3 px-3">
                      <span
                        className={`px-2.5 py-0.5 rounded-full text-[10px] font-extrabold uppercase border ${
                          lead.stage === "NEW"
                            ? "bg-red-50 text-[#c22329] border-red-200"
                            : lead.stage === "DEMO"
                            ? "bg-amber-50 text-amber-800 border-amber-200"
                            : "bg-blue-50 text-blue-700 border-blue-200"
                        }`}
                      >
                        {lead.stage || "NEW"}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* Today's Batch Schedule (4 cols) */}
        <div className="lg:col-span-4 bg-white rounded-3xl border border-slate-200/90 p-6 space-y-4 shadow-sm">
          <div className="flex items-center justify-between">
            <h2 className="text-base font-bold text-slate-900">
              Today&apos;s Sessions
            </h2>
            <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-emerald-50 text-emerald-700 border border-emerald-200">
              Live
            </span>
          </div>

          <div className="space-y-3">
            {todaySessions.length === 0 && !loading && (
              <p className="text-xs text-slate-400 text-center py-6">No sessions scheduled today.</p>
            )}
            {todaySessions.map((s) => (
              <div key={s.id} className="p-3.5 rounded-2xl bg-slate-50/80 border border-slate-200/80 space-y-1.5 hover:bg-slate-100/60 transition-colors">
                <div className="flex items-center justify-between text-xs">
                  <span className="font-bold text-slate-900">{s.batch_name}</span>
                  <span className="text-[10px] font-extrabold text-[#c99a5e] bg-amber-50 px-2 py-0.5 rounded border border-amber-200/60">
                    {s.start_time}
                  </span>
                </div>
                {s.teacher_name && <div className="text-xs text-slate-600">Faculty: {s.teacher_name}</div>}
                <div className="text-[11px] text-slate-500 font-semibold flex items-center justify-between pt-1">
                  <span>{s.room || "Room TBD"}</span>
                  <span className="text-slate-500 font-bold uppercase">{s.status}</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
