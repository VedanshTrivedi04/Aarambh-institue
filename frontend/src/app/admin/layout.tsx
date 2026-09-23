"use client";

import React, { useState } from "react";
import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { clearAuthSession } from "@/lib/auth";
import { useAuthGuard } from "@/hooks/useAuthGuard";

const ALLOWED_ROLES = ["SUPER_ADMIN", "ADMIN", "MANAGEMENT", "ACCOUNTANT", "COUNSELLOR"];
import {
  LayoutDashboard,
  UserCheck,
  GraduationCap,
  Users,
  BookOpen,
  CalendarCheck,
  CreditCard,
  Award,
  Bell,
  Search,
  LogOut,
  ExternalLink,
  Menu,
  X,
  Building,
  Sparkles,
  ArrowRight,
  Globe,
} from "lucide-react";

export default function AdminLayout({ children }: { children: React.ReactNode }) {
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
    { label: "Dashboard", href: "/admin", icon: LayoutDashboard },
    { label: "Enquiries & Leads", href: "/admin/enquiries", icon: UserCheck, badge: "CRM" },
    { label: "Students Directory", href: "/admin/students", icon: GraduationCap },
    { label: "Faculty & Staff", href: "/admin/teachers", icon: Users },
    { label: "Batches & Academics", href: "/admin/academic", icon: BookOpen },
    { label: "Attendance Register", href: "/admin/attendance", icon: CalendarCheck },
    { label: "Fees & Billing", href: "/admin/fees", icon: CreditCard },
    { label: "Exams & Results", href: "/admin/exams", icon: Award },
    { label: "Website CMS", href: "/admin/cms", icon: Globe, badge: "NEW" },
  ];

  const isActive = (href: string) => {
    if (href === "/admin") return pathname === "/admin";
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
            <Link href="/admin" className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-2xl bg-white border border-red-200 p-1 flex items-center justify-center shadow-md shadow-red-500/10">
                <div className="text-center">
                  <span className="block font-black text-xs text-[#c22329] leading-none">
                    आरंभ
                  </span>
                  <span className="block font-extrabold text-[7px] text-amber-600 uppercase mt-0.5">
                    ERP
                  </span>
                </div>
              </div>
              <div className="flex flex-col">
                <span className="font-black text-sm tracking-wide text-slate-900 leading-tight">
                  AARAMBH ERP
                </span>
                <span className="text-[10px] text-[#c99a5e] font-bold tracking-wider uppercase">
                  Admin Workspace
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
              Operations & Management
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
                      ? "bg-red-50 text-[#c22329] border border-red-200 font-bold shadow-sm"
                      : "text-slate-600 hover:text-slate-950 hover:bg-slate-100/70"
                  }`}
                >
                  <div className="flex items-center gap-3">
                    <Icon className={`w-4 h-4 shrink-0 ${active ? "text-[#c22329]" : "text-slate-500"}`} />
                    <span>{item.label}</span>
                  </div>
                  {item.badge && (
                    <span className="text-[9px] font-black px-1.5 py-0.5 rounded bg-amber-100 text-amber-800 border border-amber-300">
                      {item.badge}
                    </span>
                  )}
                </Link>
              );
            })}
          </div>
        </div>

        {/* Sidebar Bottom / Quick Access */}
        <div className="p-3 border-t border-slate-200/80 space-y-2 bg-slate-50/50">
          <Link
            href="/"
            target="_blank"
            className="flex items-center justify-between px-3.5 py-2 rounded-xl text-xs font-semibold text-slate-600 hover:text-slate-900 hover:bg-slate-100 transition-colors"
          >
            <div className="flex items-center gap-2">
              <ExternalLink className="w-3.5 h-3.5 text-[#c22329]" />
              <span>Live Website</span>
            </div>
            <span className="text-[10px] text-slate-400 font-bold">Preview</span>
          </Link>

          {/* User Profile Pill */}
          <div className="p-2.5 rounded-2xl bg-white border border-slate-200 shadow-sm flex items-center justify-between">
            <div className="flex items-center gap-2.5 overflow-hidden">
              <div className="w-8 h-8 rounded-xl bg-red-50 text-[#c22329] border border-red-200 flex items-center justify-center font-bold text-xs shrink-0">
                AD
              </div>
              <div className="truncate">
                <span className="block text-xs font-bold text-slate-900 truncate">
                  {user.email.split("@")[0]}
                </span>
                <span className="block text-[10px] text-emerald-700 font-bold uppercase">
                  {user.role}
                </span>
              </div>
            </div>

            <button
              onClick={handleLogout}
              title="Logout"
              className="text-slate-400 hover:text-[#c22329] p-1.5 rounded-lg hover:bg-red-50 transition-colors"
            >
              <LogOut className="w-4 h-4" />
            </button>
          </div>
        </div>
      </aside>

      {/* Main Content Area */}
      <div className="flex-1 md:pl-64 flex flex-col min-h-screen bg-[#f8fafd]">
        {/* Admin Top Navbar */}
        <header className="sticky top-0 z-40 h-16 bg-white/95 backdrop-blur-xl border-b border-slate-200/80 px-4 sm:px-6 flex items-center justify-between shadow-sm">
          <div className="flex items-center gap-3">
            <button
              onClick={() => setSidebarOpen(true)}
              className="md:hidden p-2 rounded-xl bg-slate-100 text-slate-700 hover:text-slate-950 border border-slate-200"
            >
              <Menu className="w-5 h-5" />
            </button>

            {/* Academic Context Badges */}
            <div className="flex items-center gap-2">
              <span className="hidden sm:inline-flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-slate-100 border border-slate-200 text-xs font-bold text-slate-700">
                <Building className="w-3.5 h-3.5 text-[#c99a5e]" />
                <span>Hawa Bangla Campus</span>
              </span>

              <span className="inline-flex items-center gap-1 px-3 py-1.5 rounded-xl bg-blue-50 border border-blue-200 text-xs font-black text-blue-700">
                <span>Session: 2026-27</span>
              </span>
            </div>
          </div>

          {/* Right Header Utilities */}
          <div className="flex items-center gap-3">
            <Link
              href="/admin/enquiries"
              className="hidden lg:flex items-center gap-1.5 px-3.5 py-1.5 rounded-xl bg-red-50 border border-red-200 text-xs font-bold text-[#c22329] hover:bg-red-100 transition-colors"
            >
              <Sparkles className="w-3 h-3 text-amber-500" />
              <span>CRM Enquiries</span>
            </Link>

            <Link
              href="/"
              target="_blank"
              className="hidden sm:inline-flex items-center gap-1.5 text-xs font-bold text-slate-700 hover:text-slate-950 px-3.5 py-1.5 rounded-xl bg-slate-100 hover:bg-slate-200/80 border border-slate-200 transition-colors"
            >
              <ExternalLink className="w-3.5 h-3.5 text-[#c99a5e]" />
              <span>Website</span>
            </Link>

            <button
              onClick={handleLogout}
              className="flex items-center gap-1.5 text-xs font-bold text-[#c22329] hover:text-white px-3.5 py-1.5 rounded-xl bg-red-50 hover:bg-[#c22329] border border-red-200 transition-colors"
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
