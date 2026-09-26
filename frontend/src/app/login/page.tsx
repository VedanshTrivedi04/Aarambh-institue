"use client";

import React, { useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { loginUser, logoutUser, portalForRole } from "@/lib/auth";
import {
  Lock,
  Mail,
  ArrowRight,
  ShieldCheck,
  Eye,
  EyeOff,
  Sparkles,
  Users,
  GraduationCap,
  AlertCircle,
  Loader2,
  ArrowLeft,
  Building,
} from "lucide-react";

export default function LoginPage() {
  const router = useRouter();
  const [roleTab, setRoleTab] = useState<"admin" | "teacher" | "student">("admin");
  const [identifier, setIdentifier] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleRoleChange = (role: "admin" | "teacher" | "student") => {
    setRoleTab(role);
    setError(null);
  };

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    const res = await loginUser(identifier, password);
    setLoading(false);

    if (res.success) {
      const portal = portalForRole(res.user?.role);
      if (portal) {
        router.push(portal);
      } else {
        await logoutUser();
        setError("This account doesn't have access to any portal. Please contact the institute.");
      }
    } else {
      setError(res.error || "Login failed. Please check your credentials.");
    }
  };

  return (
    <div className="min-h-screen bg-[#f8fafd] text-slate-900 flex flex-col justify-between p-4 sm:p-6 lg:p-8 font-['Outfit',sans-serif] selection:bg-[#c99a5e]/30 selection:text-amber-900 relative">
      {/* Subtle Background Glows */}
      <div className="absolute top-10 left-1/4 w-96 h-96 bg-red-500/5 rounded-full blur-3xl pointer-events-none -z-10" />
      <div className="absolute bottom-10 right-1/4 w-96 h-96 bg-amber-500/5 rounded-full blur-3xl pointer-events-none -z-10" />

      {/* Top Bar with Back to Website */}
      <div className="max-w-7xl mx-auto w-full flex items-center justify-between py-2">
        <Link
          href="/"
          className="inline-flex items-center gap-2 text-xs font-bold text-slate-700 hover:text-slate-950 transition-colors bg-white hover:bg-slate-50 px-3.5 py-2 rounded-xl border border-slate-200 shadow-sm"
        >
          <ArrowLeft className="w-3.5 h-3.5 text-[#c22329]" />
          <span>Back To Public Website</span>
        </Link>

        <div className="flex items-center gap-2 text-xs text-[#c99a5e] font-bold bg-amber-50 border border-amber-200/70 px-3 py-1.5 rounded-full shadow-xs">
          <Sparkles className="w-3.5 h-3.5 text-[#c99a5e]" />
          <span>Aarambh Institute ERP v2.0</span>
        </div>
      </div>

      {/* Main Login Card */}
      <div className="max-w-md w-full mx-auto my-8">
        <div className="bg-white border border-slate-200/90 rounded-3xl p-7 sm:p-9 shadow-xl shadow-slate-200/70 relative overflow-hidden">
          {/* Subtle Corner Accents */}
          <div className="absolute top-0 right-0 w-32 h-32 bg-gradient-to-br from-red-500/10 to-transparent rounded-bl-full pointer-events-none" />
          <div className="absolute bottom-0 left-0 w-32 h-32 bg-gradient-to-tr from-amber-500/10 to-transparent rounded-tr-full pointer-events-none" />

          {/* Brand Header */}
          <div className="text-center space-y-3 relative z-10 mb-7">
            <div className="w-14 h-14 mx-auto rounded-2xl bg-white border border-red-200 p-1.5 shadow-md shadow-red-500/10 flex items-center justify-center">
              <div className="text-center">
                <span className="block font-black text-sm text-[#c22329] leading-none">
                  आरंभ
                </span>
                <span className="block font-extrabold text-[8px] text-amber-600 uppercase tracking-tight mt-0.5">
                  ERP
                </span>
              </div>
            </div>

            <div>
              <h1 className="text-2xl font-black text-slate-900 tracking-tight">
                Institutional ERP Portal
              </h1>
              <p className="text-xs text-slate-500 mt-1 flex items-center justify-center gap-1.5 font-medium">
                <Building className="w-3.5 h-3.5 text-[#c99a5e]" />
                <span>Aarambh Institute • Hawa Bangla Campus, Indore</span>
              </p>
            </div>
          </div>

          {/* Role Switcher Tabs */}
          <div className="grid grid-cols-3 gap-1.5 p-1 bg-slate-100/90 rounded-2xl border border-slate-200 mb-6 text-xs font-bold relative z-10">
            <button
              type="button"
              onClick={() => handleRoleChange("admin")}
              className={`py-2 px-2 rounded-xl transition-all flex items-center justify-center gap-1.5 ${
                roleTab === "admin"
                  ? "bg-white text-[#c22329] shadow-sm border border-red-200/80 font-black"
                  : "text-slate-600 hover:text-slate-900"
              }`}
            >
              <ShieldCheck className="w-3.5 h-3.5" />
              <span>Admin</span>
            </button>

            <button
              type="button"
              onClick={() => handleRoleChange("teacher")}
              className={`py-2 px-2 rounded-xl transition-all flex items-center justify-center gap-1.5 ${
                roleTab === "teacher"
                  ? "bg-white text-blue-700 shadow-sm border border-blue-200/80 font-black"
                  : "text-slate-600 hover:text-slate-900"
              }`}
            >
              <Users className="w-3.5 h-3.5" />
              <span>Faculty</span>
            </button>

            <button
              type="button"
              onClick={() => handleRoleChange("student")}
              className={`py-2 px-2 rounded-xl transition-all flex items-center justify-center gap-1.5 ${
                roleTab === "student"
                  ? "bg-white text-amber-800 shadow-sm border border-amber-200/80 font-black"
                  : "text-slate-600 hover:text-slate-900"
              }`}
            >
              <GraduationCap className="w-3.5 h-3.5" />
              <span>Student</span>
            </button>
          </div>

          {/* Error Message */}
          {error && (
            <div className="mb-5 p-3 rounded-xl bg-red-50 border border-red-200 text-red-700 text-xs flex items-start gap-2 animate-in fade-in font-medium">
              <AlertCircle className="w-4 h-4 shrink-0 text-red-600 mt-0.5" />
              <span>{error}</span>
            </div>
          )}

          {/* Form */}
          <form onSubmit={handleLogin} className="space-y-4 relative z-10">
            <div className="space-y-1.5">
              <label className="text-xs font-bold text-slate-700 flex items-center justify-between">
                <span>Email or Mobile Number</span>
                <span className="text-[10px] text-slate-400 font-normal">Primary Login ID</span>
              </label>
              <div className="relative">
                <Mail className="w-4 h-4 text-slate-400 absolute left-3.5 top-1/2 -translate-y-1/2" />
                <input
                  type="text"
                  required
                  value={identifier}
                  onChange={(e) => setIdentifier(e.target.value)}
                  placeholder="admin@aarambhinstitute.com"
                  className="w-full bg-slate-50 border border-slate-200 rounded-xl pl-10 pr-4 py-2.5 text-sm text-slate-900 placeholder-slate-400 focus:bg-white focus:outline-none focus:border-[#c22329] focus:ring-2 focus:ring-red-500/10 transition-all font-medium"
                />
              </div>
            </div>

            <div className="space-y-1.5">
              <label className="text-xs font-bold text-slate-700 flex items-center justify-between">
                <span>Account Password</span>
                <span className="text-[10px] text-slate-400 font-normal">Encrypted</span>
              </label>
              <div className="relative">
                <Lock className="w-4 h-4 text-slate-400 absolute left-3.5 top-1/2 -translate-y-1/2" />
                <input
                  type={showPassword ? "text" : "password"}
                  required
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="••••••••••••"
                  className="w-full bg-slate-50 border border-slate-200 rounded-xl pl-10 pr-10 py-2.5 text-sm text-slate-900 placeholder-slate-400 focus:bg-white focus:outline-none focus:border-[#c22329] focus:ring-2 focus:ring-red-500/10 transition-all font-medium"
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-700"
                >
                  {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                </button>
              </div>
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full py-3 px-4 rounded-xl font-bold text-sm bg-gradient-to-r from-[#c22329] to-red-700 hover:from-red-600 hover:to-red-800 text-white shadow-lg shadow-red-600/25 transition-all flex items-center justify-center gap-2 disabled:opacity-50 cursor-pointer mt-2"
            >
              {loading ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin" />
                  <span>Authenticating...</span>
                </>
              ) : (
                <>
                  <span>Sign In To Workspace</span>
                  <ArrowRight className="w-4 h-4" />
                </>
              )}
            </button>
          </form>
        </div>
      </div>

      {/* Footer Note */}
      <div className="text-center text-xs text-slate-500 py-3 font-medium">
        © 2026 Aarambh Institute, Indore. Developed by Pragyan Innovations.
      </div>
    </div>
  );
}
