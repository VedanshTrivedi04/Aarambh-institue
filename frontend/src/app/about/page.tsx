import React from "react";
import Link from "next/link";
import { getLandingData } from "@/lib/api";
import {
  GraduationCap,
  Award,
  ShieldCheck,
  Heart,
  BookOpen,
  Users,
  CheckCircle2,
  ArrowRight,
  Sparkles,
  MapPin,
  Calendar,
  Building,
} from "lucide-react";

export const metadata = {
  title: "About Us | Aarambh Institute Indore | Director Shobhna Vyas",
  description:
    "Founded in 2015 by Mrs. Shobhna Vyas, Aarambh Institute in Hawa Bangla Indore provides student-centric coaching with strict 20-student batches for Classes 4th to 12th & Degree programs.",
};

export default async function AboutPage() {
  const data = await getLandingData();
  const { about, contact, stats } = data;

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
            <span className="text-[#c22329]">About Us</span>
          </div>

          <div className="max-w-3xl space-y-4">
            <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-red-50 border border-red-200 text-[#c22329] text-xs font-bold uppercase tracking-wider">
              <GraduationCap className="w-3.5 h-3.5" />
              <span>Step Toward Success • Since 2015</span>
            </div>

            <h1 className="text-3xl sm:text-5xl font-black text-slate-900 tracking-tight leading-tight">
              Empowering Students With <br />
              <span className="text-[#c22329]">Values, Safety & Excellence</span>
            </h1>

            <p className="text-base sm:text-lg text-slate-600 leading-relaxed">
              At Aarambh Institute, we believe that the right guidance at the right time transforms a student&apos;s academic journey. Located in Hawa Bangla, Indore, we combine veteran teaching legacy with personalized student care.
            </p>
          </div>

          {/* Quick Stat Pill Grid */}
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 mt-10">
            <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm">
              <div className="text-2xl sm:text-3xl font-black text-[#c22329]">
                {stats.years_experience}
              </div>
              <div className="text-xs font-semibold text-slate-500 mt-1">
                Teaching Legacy
              </div>
            </div>
            <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm">
              <div className="text-2xl sm:text-3xl font-black text-blue-700">
                {stats.total_students}
              </div>
              <div className="text-xs font-semibold text-slate-500 mt-1">
                Students Guided
              </div>
            </div>
            <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm">
              <div className="text-2xl sm:text-3xl font-black text-amber-600">
                {stats.highest_board_score}
              </div>
              <div className="text-xs font-semibold text-slate-500 mt-1">
                Highest Board Result
              </div>
            </div>
            <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm">
              <div className="text-2xl sm:text-3xl font-black text-emerald-700">
                {stats.batch_size_limit}
              </div>
              <div className="text-xs font-semibold text-slate-500 mt-1">
                Strict Max Batch Size
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Director's Desk */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
        <div className="bg-white rounded-3xl p-8 sm:p-12 border border-slate-200 shadow-sm grid grid-cols-1 lg:grid-cols-12 gap-8 items-center">
          <div className="lg:col-span-4 flex flex-col items-center text-center">
            <div className="w-32 h-32 rounded-3xl bg-red-50 border-2 border-red-200 flex items-center justify-center font-black text-4xl text-[#c22329] shadow-inner mb-4">
              SV
            </div>
            <h2 className="text-2xl font-black text-slate-900">
              {about.director_name}
            </h2>
            <p className="text-sm font-bold text-[#c22329] mt-0.5">
              {about.director_designation}
            </p>
            <span className="inline-block mt-2 px-3 py-1 rounded-full bg-slate-100 text-slate-700 text-xs font-semibold border border-slate-200">
              {about.director_experience}
            </span>
          </div>

          <div className="lg:col-span-8 space-y-5 border-t lg:border-t-0 lg:border-l border-slate-200 pt-6 lg:pt-0 lg:pl-8">
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-md bg-amber-50 border border-amber-200 text-amber-800 text-xs font-bold">
              <Sparkles className="w-3.5 h-3.5" />
              <span>Director&apos;s Message To Parents & Students</span>
            </div>

            <blockquote className="text-lg sm:text-xl font-medium text-slate-800 italic leading-relaxed">
              &ldquo;{about.director_quote}&rdquo;
            </blockquote>

            <div className="space-y-3 text-sm text-slate-600 leading-relaxed pt-2">
              {about.paragraphs.map((p, idx) => (
                <p key={idx}>{p}</p>
              ))}
              <p>
                Every child has innate potential. Our responsibility as educators is not to impose rote memorization, but to ignite curiosity, build unbreakable fundamentals, and provide a secure environment where questions are welcomed without fear.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Core Values & Pillars */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        <div className="text-center max-w-3xl mx-auto mb-12 space-y-3">
          <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-blue-50 border border-blue-200 text-blue-700 text-xs font-bold uppercase tracking-wider">
            <ShieldCheck className="w-3.5 h-3.5" />
            <span>Our Guiding Principles</span>
          </div>
          <h2 className="text-2xl sm:text-4xl font-black text-slate-900 tracking-tight">
            Why Families In Indore Trust Aarambh
          </h2>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="bg-white p-7 rounded-3xl border border-slate-200 shadow-sm space-y-3">
            <div className="w-12 h-12 rounded-2xl bg-red-50 border border-red-200 flex items-center justify-center text-[#c22329]">
              <ShieldCheck className="w-6 h-6" />
            </div>
            <h3 className="text-lg font-bold text-slate-900">Child Safety First</h3>
            <p className="text-xs sm:text-sm text-slate-600 leading-relaxed">
              A secure, encouraging, and monitored learning atmosphere. Parents receive continuous updates on attendance, conduct, and academic growth.
            </p>
          </div>

          <div className="bg-white p-7 rounded-3xl border border-slate-200 shadow-sm space-y-3">
            <div className="w-12 h-12 rounded-2xl bg-blue-50 border border-blue-200 flex items-center justify-center text-blue-700">
              <BookOpen className="w-6 h-6" />
            </div>
            <h3 className="text-lg font-bold text-slate-900">Effective Learning</h3>
            <p className="text-xs sm:text-sm text-slate-600 leading-relaxed">
              Proven concept-building, weekly assessment cycles, and personalized doubt sessions led by teachers with up to 30 years experience.
            </p>
          </div>

          <div className="bg-white p-7 rounded-3xl border border-slate-200 shadow-sm space-y-3">
            <div className="w-12 h-12 rounded-2xl bg-amber-50 border border-amber-200 flex items-center justify-center text-amber-800">
              <Heart className="w-6 h-6" />
            </div>
            <h3 className="text-lg font-bold text-slate-900">Joyful Environment</h3>
            <p className="text-xs sm:text-sm text-slate-600 leading-relaxed">
              Education with values and zero fear. We mentor students to build confidence, time management, and resilience for competitive exams.
            </p>
          </div>
        </div>
      </section>

      {/* Recognition Award */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="bg-gradient-to-r from-amber-50 via-white to-amber-50 border border-amber-200 rounded-3xl p-8 sm:p-10 flex flex-col md:flex-row items-center justify-between gap-6 shadow-sm">
          <div className="flex items-center gap-4">
            <div className="w-14 h-14 rounded-2xl bg-amber-100 border border-amber-300 flex items-center justify-center text-amber-800 shrink-0">
              <Award className="w-7 h-7" />
            </div>
            <div>
              <span className="text-xs font-bold uppercase tracking-wider text-amber-800">
                Institutional Accolade
              </span>
              <h3 className="text-xl sm:text-2xl font-black text-slate-900 mt-0.5">
                {about.award_title}
              </h3>
              <p className="text-xs sm:text-sm text-slate-600 mt-1">
                Awarded for outstanding contribution to board examination results and student welfare in Indore.
              </p>
            </div>
          </div>

          <Link
            href="/admissions"
            className="btn-caramel-gold shrink-0 inline-flex items-center gap-2 px-6 py-3 rounded-xl font-bold text-xs sm:text-sm shadow-md"
          >
            <span>Experience Our Classes</span>
            <ArrowRight className="w-4 h-4" />
          </Link>
        </div>
      </section>

      {/* Campus Details */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        <div className="bg-white p-8 rounded-3xl border border-slate-200 shadow-sm grid grid-cols-1 md:grid-cols-2 gap-8 items-center">
          <div className="space-y-4">
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-md bg-slate-100 text-slate-800 text-xs font-bold">
              <Building className="w-3.5 h-3.5 text-[#c22329]" />
              <span>Campus & Classrooms</span>
            </div>
            <h3 className="text-2xl font-black text-slate-900">
              Conveniently Located At Hawa Bangla, Indore
            </h3>
            <p className="text-sm text-slate-600 leading-relaxed">
              Our campus is located at <strong>{contact.full_address}</strong>. Designed for focused study, it features ventilated small-batch classrooms, dedicated doubt clinic corners, and comfortable seating with parent waiting lounges.
            </p>
            <div className="flex flex-wrap gap-4 pt-2">
              <Link
                href="/contact"
                className="inline-flex items-center gap-2 text-xs font-bold text-[#c22329] hover:underline"
              >
                <span>Get Campus Directions & Hours</span>
                <ArrowRight className="w-3.5 h-3.5" />
              </Link>
            </div>
          </div>

          <div className="space-y-3 bg-slate-50 p-6 rounded-2xl border border-slate-100 text-xs font-medium text-slate-700">
            <div className="flex items-center gap-2 text-slate-900 font-bold">
              <CheckCircle2 className="w-4 h-4 text-emerald-600" />
              <span>Strict batch size cap (maximum 20 students per batch)</span>
            </div>
            <div className="flex items-center gap-2 text-slate-900 font-bold">
              <CheckCircle2 className="w-4 h-4 text-emerald-600" />
              <span>Separate batches for Morning & Evening timings</span>
            </div>
            <div className="flex items-center gap-2 text-slate-900 font-bold">
              <CheckCircle2 className="w-4 h-4 text-emerald-600" />
              <span>CCTV monitored learning environment for student safety</span>
            </div>
            <div className="flex items-center gap-2 text-slate-900 font-bold">
              <CheckCircle2 className="w-4 h-4 text-emerald-600" />
              <span>Daily parent interaction and doubt resolution clinics</span>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
}
