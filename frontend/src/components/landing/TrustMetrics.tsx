"use client";

import React from "react";
import { Users, Award, GraduationCap, Building2, TrendingUp, ShieldCheck } from "lucide-react";
import Reveal from "@/components/ui/Reveal";
import CountUp from "@/components/ui/CountUp";

export default function TrustMetrics() {
  const metrics = [
    {
      icon: GraduationCap,
      value: "15+ Yrs",
      label: "Teaching Legacy",
      detail: "Established 2015 in Indore",
      color: "from-red-600 to-amber-600",
      iconBg: "bg-red-50 text-[#c22329]",
    },
    {
      icon: Users,
      value: "2,000+",
      label: "Students Mentored",
      detail: "Across MP Board, CBSE & ICSE",
      color: "from-blue-600 to-indigo-600",
      iconBg: "bg-blue-50 text-blue-600",
    },
    {
      icon: Award,
      value: "98.5%",
      label: "Highest Board Score",
      detail: "Class 10 MP Board Topper",
      color: "from-amber-600 to-orange-600",
      iconBg: "bg-amber-50 text-amber-600",
    },
    {
      icon: TrendingUp,
      value: "98%",
      label: "Board Result Rate",
      detail: "85% avg student score",
      color: "from-emerald-600 to-teal-600",
      iconBg: "bg-emerald-50 text-emerald-600",
    },
    {
      icon: Building2,
      value: "12+",
      label: "Expert Faculty",
      detail: "Up to 30 years experience",
      color: "from-purple-600 to-indigo-600",
      iconBg: "bg-purple-50 text-purple-600",
    },
    {
      icon: ShieldCheck,
      value: "Class 4–12",
      label: "School & Degree",
      detail: "B.Com, M.Com, BBA, MBA, B.Sc",
      color: "from-cyan-600 to-blue-700",
      iconBg: "bg-cyan-50 text-cyan-600",
    },
  ];

  return (
    <section className="relative py-12 bg-white border-y border-slate-200/80">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
          {metrics.map((item, index) => {
            const Icon = item.icon;
            return (
              <Reveal key={index} delay={index * 70} direction="up" distance={20}>
                <div className="light-card-interactive hover-lift p-5 rounded-2xl flex flex-col justify-between group h-full">
                  <div className="flex items-center gap-2 mb-3">
                    <div className={`p-2.5 rounded-xl ${item.iconBg} group-hover:scale-110 group-hover:-rotate-6 transition-transform`}>
                      <Icon className="w-5 h-5" />
                    </div>
                  </div>
                  <div>
                    <CountUp
                      value={item.value}
                      className={`stat-pop inline-block text-2xl sm:text-3xl font-black bg-gradient-to-r ${item.color} bg-clip-text text-transparent`}
                    />
                    <div className="text-sm font-bold text-slate-900 mt-1">
                      {item.label}
                    </div>
                    <div className="text-[11px] text-slate-500 mt-0.5 leading-tight">
                      {item.detail}
                    </div>
                  </div>
                </div>
              </Reveal>
            );
          })}
        </div>
      </div>
    </section>
  );
}
