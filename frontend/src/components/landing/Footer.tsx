"use client";

import React from "react";
import { usePathname } from "next/navigation";
import { Phone, Mail, MapPin, ExternalLink, ArrowUp, Clock, MessageCircle } from "lucide-react";

import { InstituteContactInfo } from "@/types/landing";
import Reveal from "@/components/ui/Reveal";

interface FooterProps {
  contact?: InstituteContactInfo;
}

export default function Footer({ contact }: FooterProps) {
  const pathname = usePathname();

  if (
    pathname?.startsWith("/admin") ||
    pathname?.startsWith("/teacher") ||
    pathname?.startsWith("/student") ||
    pathname?.startsWith("/login")
  ) {
    return null;
  }
  const address = contact?.full_address || "8 Shantinath Puri, Hawa Bangla, Near Sai Mandir, Indore, Madhya Pradesh";
  const primaryPhone = contact?.primary_phone || "88397-14081";
  const secondaryPhone = contact?.secondary_phone || "79097-14081";
  const email = contact?.email || "aarambhinstitute09@gmail.com";
  const workingHours = contact?.working_hours || "10:00 AM to 8:00 PM (Monday to Saturday)";
  const mapsUrl = contact?.google_maps_url || "https://maps.app.goo.gl/T2m2g9b8tjVMCDqL9";
  const tagline = contact?.footer_tagline || "Education with values. Learning with joy.";

  const scrollToTop = () => {
    window.scrollTo({ top: 0, behavior: "smooth" });
  };

  return (
    <footer id="contact" className="relative bg-[#0b1329] text-slate-300 text-sm border-t border-slate-800 pt-16 pb-12">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-10 pb-12 border-b border-slate-800">
          {/* Brand Col */}
          <Reveal delay={0} className="lg:col-span-2 space-y-4">
            <div className="flex items-center gap-3">
              <div className="w-11 h-11 rounded-2xl bg-white p-1 shadow-md flex items-center justify-center">
                <div className="text-center">
                  <span className="block font-black text-xs text-[#c22329] leading-none">
                    आरंभ
                  </span>
                  <span className="block font-extrabold text-[8px] text-amber-600 uppercase mt-0.5">
                    AARAMBH
                  </span>
                </div>
              </div>
              <div className="flex flex-col">
                <div className="flex items-center gap-1.5">
                  <span className="font-black tracking-wider text-xl text-white">
                    AARAMBH
                  </span>
                  <span className="text-[10px] font-extrabold px-1.5 py-0.5 rounded bg-red-500/20 text-red-400 border border-red-500/30">
                    INSTITUTE
                  </span>
                </div>
                <span className="text-[10px] text-amber-400 tracking-wider uppercase font-bold">
                  Step Toward Success • Est. 2015
                </span>
              </div>
            </div>

            <p className="text-xs text-slate-400 leading-relaxed max-w-sm font-normal">
              Premier coaching institute in Indore for Classes 4th to 12th (MP Board, CBSE, ICSE) and College Degrees (B.Com, M.Com, BBA, MBA, B.Sc). Small batches, experienced teachers, and affordable fees.
            </p>

            <p className="text-xs text-amber-300 italic font-semibold">
              &ldquo;{tagline}&rdquo;
            </p>

            {/* Direct Contact Info */}
            <div className="flex flex-col gap-2.5 pt-2 text-xs">
              <div className="flex items-start gap-2.5 text-slate-300">
                <MapPin className="w-4 h-4 text-[#c22329] mt-0.5 flex-shrink-0" />
                <div>
                  <span className="font-semibold text-white">Campus Address:</span>
                  <p className="text-slate-400">{address}</p>
                  <a
                    href={mapsUrl}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-cyan-400 hover:underline inline-flex items-center gap-1 font-bold mt-0.5"
                  >
                    <span>View on Google Maps</span>
                    <ExternalLink className="w-3 h-3" />
                  </a>
                </div>
              </div>

              <div className="flex items-center gap-2.5 text-slate-300">
                <Phone className="w-4 h-4 text-amber-400 flex-shrink-0" />
                <div>
                  <span className="font-semibold text-white">Helpline: </span>
                  <a href={`tel:+91${primaryPhone.replace(/\D/g, '')}`} className="hover:text-white transition-colors">{primaryPhone}</a>
                  <span className="mx-1 text-slate-500">/</span>
                  <a href={`tel:+91${secondaryPhone.replace(/\D/g, '')}`} className="hover:text-white transition-colors">{secondaryPhone}</a>
                </div>
              </div>

              <div className="flex items-center gap-2.5 text-slate-300">
                <Mail className="w-4 h-4 text-cyan-400 flex-shrink-0" />
                <a href={`mailto:${email}`} className="hover:text-white transition-colors">
                  {email}
                </a>
              </div>

              <div className="flex items-center gap-2.5 text-slate-300">
                <Clock className="w-4 h-4 text-emerald-400 flex-shrink-0" />
                <span>Working Hours: {workingHours}</span>
              </div>
            </div>
          </Reveal>

          {/* Quick Courses */}
          <Reveal delay={80} className="space-y-3">
            <h4 className="text-xs font-bold uppercase tracking-wider text-white">
              Courses Offered
            </h4>
            <ul className="space-y-2 text-xs">
              <li>
                <a href="/courses#middle-school" className="hover:text-amber-400 transition-colors">
                  Class 4th to 8th (All Subjects)
                </a>
              </li>
              <li>
                <a href="/courses#high-school" className="hover:text-amber-400 transition-colors">
                  Class 9th & 10th (MP Board / CBSE)
                </a>
              </li>
              <li>
                <a href="/courses#high-school" className="hover:text-amber-400 transition-colors">
                  Class 11th & 12th Science (PCM/PCB)
                </a>
              </li>
              <li>
                <a href="/courses#college-degrees" className="hover:text-amber-400 transition-colors">
                  Class 11th & 12th Commerce
                </a>
              </li>
              <li>
                <a href="/courses#college-degrees" className="hover:text-amber-400 transition-colors">
                  B.Com & M.Com Degree Coaching
                </a>
              </li>
              <li>
                <a href="/courses#college-degrees" className="hover:text-amber-400 transition-colors">
                  BBA, MBA & B.Sc Subjects
                </a>
              </li>
            </ul>
          </Reveal>

          {/* Quick Links */}
          <Reveal delay={160} className="space-y-3">
            <h4 className="text-xs font-bold uppercase tracking-wider text-white">
              Explore Aarambh
            </h4>
            <ul className="space-y-2 text-xs">
              <li>
                <a href="/about" className="hover:text-amber-400 transition-colors">
                  About Institute (Est. 2015)
                </a>
              </li>
              <li>
                <a href="/courses" className="hover:text-amber-400 transition-colors">
                  Academic Programs & Fees
                </a>
              </li>
              <li>
                <a href="/results" className="hover:text-amber-400 transition-colors">
                  Hall of Fame (Toppers & Results)
                </a>
              </li>
              <li>
                <a href="/faculty" className="hover:text-amber-400 transition-colors">
                  Faculty (Up to 30 Yrs Exp)
                </a>
              </li>
              <li>
                <a href="/student-corner" className="hover:text-amber-400 transition-colors">
                  Student Corner & Resources
                </a>
              </li>
              <li>
                <a href="/admissions" className="hover:text-amber-400 transition-colors">
                  Book Free Demo Class
                </a>
              </li>
              <li>
                <a href="/contact" className="hover:text-amber-400 transition-colors">
                  Campus Address & Directions
                </a>
              </li>
            </ul>
          </Reveal>

          {/* Aarambh Portals & Resources */}
          <Reveal delay={240} className="space-y-3">
            <h4 className="text-xs font-bold uppercase tracking-wider text-cyan-400 flex items-center gap-1">
              <span>Student & Parent ERP</span>
              <ExternalLink className="w-3 h-3" />
            </h4>
            <p className="text-[11px] text-slate-400">
              Integrated portal for attendance, test marks, and homework:
            </p>
            <ul className="space-y-2 text-xs">
              <li>
                <a href="/login?role=parent" className="hover:text-cyan-300 transition-colors flex items-center gap-1">
                  <span>Parent Portal</span>
                  <span className="text-[10px] text-slate-500">(Attendance & Marks)</span>
                </a>
              </li>
              <li>
                <a href="/login?role=student" className="hover:text-cyan-300 transition-colors flex items-center gap-1">
                  <span>Student Portal</span>
                  <span className="text-[10px] text-slate-500">(Online Tests & Notes)</span>
                </a>
              </li>
              <li>
                <a href="/login?role=teacher" className="hover:text-cyan-300 transition-colors flex items-center gap-1">
                  <span>Teacher Portal</span>
                  <span className="text-[10px] text-slate-500">(Batch Management)</span>
                </a>
              </li>
              <li>
                <a href="/login?role=admin" className="hover:text-cyan-300 transition-colors flex items-center gap-1">
                  <span>Admin Portal</span>
                  <span className="text-[10px] text-slate-500">(Admissions)</span>
                </a>
              </li>
            </ul>

            <div className="pt-2">
              <a
                href="https://wa.me/918839714081"
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-emerald-500/20 text-emerald-400 border border-emerald-500/30 text-xs font-bold hover:bg-emerald-500/30 transition-colors"
              >
                <MessageCircle className="w-3.5 h-3.5" />
                <span>WhatsApp: 88397-14081</span>
              </a>
            </div>
          </Reveal>
        </div>

        {/* Bottom copyright */}
        <div className="pt-8 flex flex-col sm:flex-row items-center justify-between gap-4 text-xs text-slate-500">
          <div className="flex flex-col sm:flex-row items-center sm:items-start gap-1 sm:gap-2 text-center sm:text-left">
            <span>
              © {new Date().getFullYear()} Aarambh Institute®. All Rights Reserved. 8 Shantinath Puri, Hawa Bangla, Indore.
            </span>
            <span className="hidden sm:inline text-slate-600">•</span>
            <span className="text-slate-400 font-medium">
              Developed by <span className="text-slate-200 font-semibold hover:text-white transition-colors">Pragyan Innovations</span>
            </span>
          </div>

          <div className="flex items-center gap-6">
            <a href="#" className="hover:text-slate-300 transition-colors">aarambhinstitute.com</a>
            <a href="https://maps.app.goo.gl/T2m2g9b8tjVMCDqL9" target="_blank" rel="noopener noreferrer" className="hover:text-slate-300 transition-colors">Google Maps</a>
            <button
              onClick={scrollToTop}
              className="group p-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-300 hover:text-white transition-all hover:-translate-y-1 flex items-center gap-1"
              title="Back to Top"
            >
              <ArrowUp className="w-4 h-4 transition-transform group-hover:-translate-y-0.5" />
              <span>Top</span>
            </button>
          </div>
        </div>
      </div>
    </footer>
  );
}
