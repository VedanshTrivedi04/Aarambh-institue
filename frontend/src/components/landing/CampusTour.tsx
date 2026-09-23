"use client";

import React from "react";
import { Building, Monitor, Library, Wifi, ShieldAlert, Cpu } from "lucide-react";

export default function CampusTour() {
  const facilities = [
    {
      icon: Monitor,
      title: "Smart Hybrid Classrooms",
      desc: "Interactive touch panels, 4K digital blackboard projection, and HD cameras recording every session for anytime replay on Aarambh ERP.",
    },
    {
      icon: Cpu,
      title: "National CBT Testing Lab",
      desc: "100+ dedicated computer terminals replicating the exact NTA JEE/NEET screen layout, exam timer, and virtual keyboard interface.",
    },
    {
      icon: Library,
      title: "Silent AC Reference Library",
      desc: "Open from 7 AM to 10 PM. Stocked with 5,000+ national and international competitive physics, chemistry, maths, and biology journals.",
    },
    {
      icon: Building,
      title: "1:1 Doubt Clearing Counters",
      desc: "Comfortable glass-partitioned breakout zones where students sit directly with teachers to resolve homework questions without hesitation.",
    },
    {
      icon: ShieldAlert,
      title: "Biometric & Campus Security",
      desc: "RFID / Biometric attendance sends instant SMS/app notification to parents upon student arrival and departure, backed by 24x7 CCTV.",
    },
    {
      icon: Wifi,
      title: "Cafeteria & Wellness Hub",
      desc: "Hygienic snacks, purified water stations, and recreational open green spaces designed to relieve study fatigue during long batch hours.",
    },
  ];

  return (
    <section id="facilities" className="relative py-24 bg-white text-slate-900 border-t border-slate-200/80">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center max-w-3xl mx-auto space-y-4">
          <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-blue-50 border border-blue-200 text-blue-700 text-xs font-bold uppercase tracking-wider">
            <Building className="w-3.5 h-3.5" />
            <span>World-Class Infrastructure</span>
          </div>

          <h2 className="text-3xl sm:text-5xl font-black tracking-tight text-slate-900">
            Designed For Deep Focus <br />
            <span className="gradient-text-blue">& Modern Learning</span>
          </h2>

          <p className="text-sm sm:text-base text-slate-600">
            An environment free from distractions, fully equipped with cutting-edge academic technology to give your preparation an unmatched competitive edge.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mt-16">
          {facilities.map((fac, idx) => {
            const Icon = fac.icon;
            return (
              <div
                key={idx}
                className="light-card-interactive p-7 rounded-3xl flex flex-col justify-start group"
              >
                <div className="w-12 h-12 rounded-2xl bg-blue-50 border border-blue-100 flex items-center justify-center text-blue-600 mb-5 group-hover:scale-110 transition-all">
                  <Icon className="w-6 h-6" />
                </div>
                <h3 className="text-xl font-bold text-slate-900 mb-2 group-hover:text-blue-600 transition-colors">
                  {fac.title}
                </h3>
                <p className="text-xs sm:text-sm text-slate-600 leading-relaxed font-normal">
                  {fac.desc}
                </p>
              </div>
            );
          })}
        </div>
      </div>
    </section>
  );
}
