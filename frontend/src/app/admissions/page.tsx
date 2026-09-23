import React from "react";
import Link from "next/link";
import AdmissionProcess from "@/components/landing/AdmissionProcess";
import AdmissionsForm from "@/components/landing/AdmissionsForm";
import FaqSection from "@/components/landing/FaqSection";
import {
  Calendar,
  CheckCircle2,
  FileCheck2,
  Sparkles,
  PhoneCall,
  Clock,
  ShieldCheck,
  CreditCard,
} from "lucide-react";

export const metadata = {
  title: "Admissions 2026-27 | Book Free Demo Class | Aarambh Institute Indore",
  description:
    "Admissions open for Session 2026-27 at Aarambh Institute Indore. Strict 20 students per batch. Book 2 days free demo classes for Class 4th to 12th & Degree programs.",
};

export default function AdmissionsPage() {
  return (
    <div className="bg-[#f8fafd] text-slate-900 pb-20">
      {/* Page Header */}
      <section className="relative bg-gradient-to-b from-white via-slate-50 to-[#f8fafd] border-b border-slate-200/80 pt-10 pb-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center gap-2 text-xs font-bold text-slate-500 mb-4">
            <Link href="/" className="hover:text-[#c22329] transition-colors">
              Home
            </Link>
            <span>/</span>
            <span className="text-[#c22329]">Admissions</span>
          </div>

          <div className="max-w-3xl space-y-4">
            <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-red-50 border border-red-200 text-[#c22329] text-xs font-bold uppercase tracking-wider">
              <Calendar className="w-3.5 h-3.5" />
              <span>Session 2026-27 Admissions Open</span>
            </div>

            <h1 className="text-3xl sm:text-5xl font-black text-slate-900 tracking-tight leading-tight">
              Join Aarambh Institute <br />
              <span className="text-[#c22329]">With 2 Days Free Trial Class</span>
            </h1>

            <p className="text-base sm:text-lg text-slate-600 leading-relaxed">
              We welcome students from Class 4th to 12th (MP Board, CBSE, ICSE) and Degree programs. Because we strictly limit each batch to 20 students, seats fill up quickly.
            </p>
          </div>

          {/* Key Admission Highlights */}
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 mt-8">
            <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm flex items-center gap-3">
              <div className="w-10 h-10 rounded-xl bg-red-100 text-[#c22329] flex items-center justify-center font-bold">
                <CheckCircle2 className="w-5 h-5" />
              </div>
              <div>
                <h3 className="text-sm font-bold text-slate-900">Zero Admission Fees</h3>
                <p className="text-xs text-slate-500">Only affordable monthly fees</p>
              </div>
            </div>

            <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm flex items-center gap-3">
              <div className="w-10 h-10 rounded-xl bg-blue-100 text-blue-700 flex items-center justify-center font-bold">
                <Clock className="w-5 h-5" />
              </div>
              <div>
                <h3 className="text-sm font-bold text-slate-900">2-Day Free Trial</h3>
                <p className="text-xs text-slate-500">Test the batch before deciding</p>
              </div>
            </div>

            <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm flex items-center gap-3">
              <div className="w-10 h-10 rounded-xl bg-amber-100 text-amber-800 flex items-center justify-center font-bold">
                <ShieldCheck className="w-5 h-5" />
              </div>
              <div>
                <h3 className="text-sm font-bold text-slate-900">Strict 20-Cap Batch</h3>
                <p className="text-xs text-slate-500">No student gets left behind</p>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* 4-Step Admission Flow */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-6">
        <AdmissionProcess />
      </div>

      {/* Document Checklist & Fee Transparency */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
          <div className="bg-white p-8 rounded-3xl border border-slate-200 shadow-sm space-y-4">
            <div className="flex items-center gap-2.5 text-slate-900">
              <FileCheck2 className="w-6 h-6 text-[#c22329]" />
              <h2 className="text-xl font-bold">Documents Required For Admission</h2>
            </div>
            <p className="text-xs text-slate-500">
              Please carry photocopy copies during your campus visit after your demo classes:
            </p>
            <ul className="space-y-2.5 text-xs text-slate-700 pt-2">
              <li className="flex items-start gap-2">
                <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0 mt-0.5" />
                <span>Photocopy of previous class marksheet / term report card</span>
              </li>
              <li className="flex items-start gap-2">
                <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0 mt-0.5" />
                <span>Photocopy of Student&apos;s Aadhar Card (for identity verification)</span>
              </li>
              <li className="flex items-start gap-2">
                <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0 mt-0.5" />
                <span>2 recent passport-size student photographs</span>
              </li>
              <li className="flex items-start gap-2">
                <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0 mt-0.5" />
                <span>Parent/guardian contact number and WhatsApp information</span>
              </li>
            </ul>
          </div>

          <div className="bg-white p-8 rounded-3xl border border-slate-200 shadow-sm space-y-4">
            <div className="flex items-center gap-2.5 text-slate-900">
              <CreditCard className="w-6 h-6 text-blue-700" />
              <h2 className="text-xl font-bold">Transparent & Student-Friendly Fees</h2>
            </div>
            <p className="text-xs text-slate-500">
              At Aarambh, we believe quality guidance should be affordable for every family in Indore:
            </p>
            <ul className="space-y-2.5 text-xs text-slate-700 pt-2">
              <li className="flex items-start gap-2">
                <CheckCircle2 className="w-4 h-4 text-blue-600 shrink-0 mt-0.5" />
                <span><strong>Classes 4th to 8th:</strong> ₹800/- to ₹1,000/- monthly (all subjects included)</span>
              </li>
              <li className="flex items-start gap-2">
                <CheckCircle2 className="w-4 h-4 text-blue-600 shrink-0 mt-0.5" />
                <span><strong>Classes 9th to 12th:</strong> Affordable subject & combo packages with monthly options</span>
              </li>
              <li className="flex items-start gap-2">
                <CheckCircle2 className="w-4 h-4 text-blue-600 shrink-0 mt-0.5" />
                <span><strong>College Degrees:</strong> Semester and subject-wise commerce/degree packages</span>
              </li>
              <li className="flex items-start gap-2">
                <CheckCircle2 className="w-4 h-4 text-blue-600 shrink-0 mt-0.5" />
                <span>No hidden charges for test series or formula booklets</span>
              </li>
            </ul>
          </div>
        </div>
      </section>

      {/* Admissions & Demo Lead Capture Form (Wired to CRM) */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-4">
        <AdmissionsForm />
      </div>

      {/* Frequently Asked Questions */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-10">
        <FaqSection />
      </div>
    </div>
  );
}
