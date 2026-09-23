"use client";

import React, { useState } from "react";
import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { clearAuthSession } from "@/lib/auth";
import { useAuthGuard } from "@/hooks/useAuthGuard";
import {
  LayoutDashboard,
  Users,
  CalendarCheck,
  FileText,
  Award,
  HelpCircle,
  BookOpen,
  LogOut,
  ExternalLink,
  Menu,
  X,
  Building,
  Sparkles,
  GraduationCap,
} from "lucide-react";

const ALLOWED_ROLES = ["TEACHER"];

export default function TeacherLayout({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const router = useRouter();
  const { user, checking } = useAuthGuard(ALLOWED_ROLES);
  const [sidebarOpen, setSidebarOpen] = useState(false);

  const handleLogout = () => {
    clearAuthSession();
    router.push("/login");
  };

  if (checking || !user) {
    return (
      <div className="min-h-screen bg-[#f8fafd] flex items-center justify-center">
        <div className="w-8 h-8 border-2 border-[#c22329] border-t-transparent rounded-full animate-spin" />
      </div>
    );
  }

  const navItems = [
    { label: "Dashboard", href: "/teacher", icon: LayoutDashboard },
    { label: "My Batches & Students", href: "/teacher/batches", icon: Users, badge: "Max 20" },
    { label: "Daily Attendance", href: "/teacher/attendance", icon: CalendarCheck },
    { label: "Assignments & Homework", href: "/teacher/assignments", icon: FileText },
    { label: "Test Marks Entry", href: "/teacher/exams", icon: Award },
    { label: "Student Doubts & Clinics", href: "/teacher/doubts", icon: HelpCircle, badge: "4 New" },
    { label: "Syllabus Tracker", href: "/teacher/syllabus", icon: BookOpen },
  ];

  const isActive = (href: string) => {
    if (href === "/teacher") return pathname === "/teacher";
    return pathname.startsWith(href);
  };

  return (
    <div className="min-h-screen bg-[#f8fafd] text-slate-900 flex flex-col md:flex-row font-['Outfit',sans-serif]">
      {/* Sidebar - Desktop & Tablet */}
      <aside
        className={`fixed inset-y-0 left-0 z-50 w-64 bg-white border-r border-slate-200/80 flex flex-col justify-between transition-transform duration-300 md:translate-x-0 ${
          sidebarOpen ? "translate-x-0 shadow-2xl" : "-translate-x-full"
        }`}
      >
        {/* Brand Header */}
        <div>
          <div className="h-16 px-5 border-b border-slate-200/80 flex items-center justify-between">
            <Link href="/teacher" className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-2xl bg-white border border-red-200 p-1 flex items-center justify-center shadow-md shadow-red-500/10">
                <div className="text-center">
                  <span className="block font-black text-xs text-[#c22329] leading-none">
                    आरंभ
                  </span>
                  <span className="block font-extrabold text-[7px] text-amber-600 uppercase mt-0.5">
                    FACULTY
                  </span>
                </div>
              </div>
              <div className="flex flex-col">
                <span className="font-black text-sm tracking-wide text-slate-900 leading-tight">
                  AARAMBH ERP
                </span>
                <span className="text-[10px] text-[#c99a5e] font-bold tracking-wider uppercase">
                  Faculty Workspace
                </span>
              </div>
            </Link>

            <button
              onClick={() => setSidebarOpen(false)}
              className="md:hidden text-slate-400 hover:text-slate-700"
            >
              <X className="w-5 h-5" />
            </button>
          </div>

          {/* Navigation Items */}
          <div className="p-3 space-y-1">
            <div className="px-3 py-2 text-[10px] font-extrabold tracking-wider uppercase text-slate-400">
              Teaching & Academic Desk
            </div>

            {navItems.map((item) => {
              const active = isActive(item.href);
              const Icon = item.icon;
              return (
                <Link
                  key={item.href}
                  href={item.href}
                  onClick={() => setSidebarOpen(false)}
                  className={`flex items-center justify-between px-3.5 py-2.5 rounded-xl text-xs font-semibold transition-all ${
                    active
                      ? "bg-red-50 text-[#c22329] border border-red-200 font-bold shadow-xs"
                      : "text-slate-600 hover:text-slate-950 hover:bg-slate-100/70"
                  }`}
                >
                  <div className="flex items-center gap-3">
                    <Icon className={`w-4 h-4 shrink-0 ${active ? "text-[#c22329]" : "text-slate-500"}`} />
                    <span>{item.label}</span>
                  </div>
                  {item.badge && (
                    <span
                      className={`text-[9px] font-black px-1.5 py-0.5 rounded border ${
                        item.badge.includes("New")
                          ? "bg-red-100 text-red-700 border-red-200"
                          : "bg-emerald-50 text-emerald-700 border-emerald-200"
                      }`}
                    >
                      {item.badge}
                    </span>
                  )}
                </Link>
              );
            })}
          </div>
        </div>

        {/* Sidebar Bottom / Educator Card */}
        <div className="p-3 border-t border-slate-200/80 space-y-2 bg-slate-50/50">
          <Link
            href="/"
            target="_blank"
            className="flex items-center justify-between px-3.5 py-2 rounded-xl text-xs font-semibold text-slate-600 hover:text-slate-900 hover:bg-slate-100 transition-colors"
          >
            <div className="flex items-center gap-2">
              <ExternalLink className="w-3.5 h-3.5 text-[#c22329]" />
              <span>Public Website</span>
            </div>
            <span className="text-[10px] text-slate-400 font-bold">Live</span>
          </Link>

          {/* User Profile Pill */}
          <div className="p-2.5 rounded-2xl bg-white border border-slate-200 shadow-sm flex items-center justify-between">
            <div className="flex items-center gap-2.5 overflow-hidden">
              <div className="w-8 h-8 rounded-xl bg-amber-50 text-[#c99a5e] border border-amber-200 flex items-center justify-center font-bold text-xs shrink-0">
                {(user.first_name?.[0] || user.email[0]).toUpperCase()}
                {(user.last_name?.[0] || "").toUpperCase()}
              </div>
              <div className="truncate">
                <span className="block text-xs font-bold text-slate-900 truncate">
                  {user.first_name ? `${user.first_name} ${user.last_name || ""}`.trim() : user.email}
                </span>
                <span className="block text-[10px] text-emerald-700 font-bold uppercase truncate">
                  Faculty
                </span>
              </div>
            </div>

            <button
              onClick={handleLogout}
              title="Logout"
              className="text-slate-400 hover:text-[#c22329] p-1.5 rounded-lg hover:bg-red-50 transition-colors cursor-pointer"
            >
              <LogOut className="w-4 h-4" />
            </button>
          </div>
        </div>
      </aside>

      {/* Main Content Area */}
      <div className="flex-1 md:pl-64 flex flex-col min-h-screen bg-[#f8fafd]">
        {/* Top Navbar */}
        <header className="sticky top-0 z-40 h-16 bg-white/95 backdrop-blur-xl border-b border-slate-200/80 px-4 sm:px-6 flex items-center justify-between shadow-xs">
          <div className="flex items-center gap-3">
            <button
              onClick={() => setSidebarOpen(true)}
              className="md:hidden p-2 rounded-xl bg-slate-100 text-slate-700 hover:text-slate-950 border border-slate-200 cursor-pointer"
            >
              <Menu className="w-5 h-5" />
            </button>

            {/* Academic Context Badges */}
            <div className="flex items-center gap-2">
              <span className="hidden sm:inline-flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-slate-100 border border-slate-200 text-xs font-bold text-slate-700">
                <Building className="w-3.5 h-3.5 text-[#c99a5e]" />
                <span>Hawa Bangla Campus</span>
              </span>

              <span className="inline-flex items-center gap-1 px-3 py-1.5 rounded-xl bg-red-50 border border-red-200 text-xs font-black text-[#c22329]">
                <GraduationCap className="w-3.5 h-3.5 text-[#c22329]" />
                <span>Senior Faculty Desk</span>
              </span>
            </div>
          </div>

          {/* Right Header Utilities */}
          <div className="flex items-center gap-3">
            <div className="hidden lg:flex items-center gap-2 text-xs font-bold text-slate-600 bg-slate-50 border border-slate-200 px-3 py-1.5 rounded-xl">
              <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
              <span>Next Lecture: 5:00 PM (Room 201)</span>
            </div>

            <button
              onClick={handleLogout}
              className="flex items-center gap-1.5 text-xs font-bold text-[#c22329] hover:text-white px-3.5 py-1.5 rounded-xl bg-red-50 hover:bg-[#c22329] border border-red-200 transition-colors cursor-pointer"
            >
              <LogOut className="w-3.5 h-3.5" />
              <span className="hidden sm:inline">Logout</span>
            </button>
          </div>
        </header>

        {/* Page Body */}
        <main className="flex-1 p-4 sm:p-6 lg:p-8 overflow-x-hidden">
          {children}
        </main>
      </div>
    </div>
  );
}
