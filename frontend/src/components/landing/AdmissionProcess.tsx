"use client";

import React from "react";
import { PhoneCall, MapPin, FileCheck, CheckCircle2, ArrowRight, Clock, Calendar, MessageCircle } from "lucide-react";

export default function AdmissionProcess() {
  const steps = [
    {
      step: "01",
      title: "Call or WhatsApp For Enquiry",
      desc: "Contact our Indore helpline at 88397-14081 or 79097-14081 to know course details, subjects, and batch slots.",
      icon: PhoneCall,
      color: "bg-red-50 text-[#c22329] border-red-200",
    },
    {
      step: "02",
      title: "Visit For A Free Demo Class",
      desc: "Come to our campus at 8 Shantinath Puri, Hawa Bangla (Near Sai Mandir). Experience our classroom teaching firsthand.",
      icon: MapPin,
      color: "bg-amber-50 text-amber-800 border-amber-200",
    },
    {
      step: "03",
      title: "Fill Form & Submit Documents",
      desc: "Complete the simple admission form. Attach: Previous year marksheet, Student Aadhar Card, and 2 passport photos.",
      icon: FileCheck,
      color: "bg-blue-50 text-blue-700 border-blue-200",
    },
    {
      step: "04",
      title: "Pay Fees & Get Batch Timing",
      desc: "Pay the student-friendly monthly fee and receive your confirmed morning or evening batch schedule.",
      icon: CheckCircle2,
      color: "bg-emerald-50 text-emerald-700 border-emerald-200",
    },
  ];

  return (
    <section id="admissions-process" className="relative py-24 bg-[#f8fafd] text-slate-900 border-b border-slate-200/80">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center max-w-3xl mx-auto space-y-4">
          <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-red-50 border border-red-200 text-[#c22329] text-xs font-bold uppercase tracking-wider">
            <Calendar className="w-3.5 h-3.5" />
            <span>Admission Season: April to June (Open Now)</span>
          </div>

          <h2 className="text-3xl sm:text-5xl font-black tracking-tight text-slate-900">
            Simple 4-Step <br />
            <span className="text-[#c22329]">Admission Process</span>
          </h2>

          <p className="text-sm sm:text-base text-slate-600">
            Joining Aarambh Institute is straightforward and transparent. Follow these 4 easy steps to secure your seat.
          </p>
        </div>

        {/* 4 Steps Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mt-16">
          {steps.map((item, idx) => {
            const Icon = item.icon;
            return (
              <div
                key={idx}
                className="light-card-interactive p-7 rounded-3xl flex flex-col justify-between relative group"
              >
                <div>
                  <div className="flex items-center justify-between mb-5">
                    <span className="font-black text-2xl text-slate-300 group-hover:text-[#c22329] transition-colors">
                      {item.step}
                    </span>
                    <div className={`p-3 rounded-2xl border ${item.color}`}>
                      <Icon className="w-5 h-5" />
                    </div>
                  </div>

                  <h3 className="text-lg font-bold text-slate-900 mb-2 group-hover:text-[#c22329] transition-colors">
                    {item.title}
                  </h3>

                  <p className="text-xs sm:text-sm text-slate-600 leading-relaxed font-normal">
                    {item.desc}
                  </p>
                </div>

                <div className="mt-6 pt-3 border-t border-slate-100 flex items-center text-xs font-bold text-[#c99a5e]">
                  <span>Step {idx + 1} of 4</span>
                </div>
              </div>
            );
          })}
        </div>

        {/* Documents Required Box */}
        <div className="mt-14 p-6 sm:p-8 rounded-3xl bg-white border border-slate-200 max-w-3xl mx-auto shadow-sm">
          <h4 className="font-black text-base text-slate-900 mb-3 flex items-center gap-2">
            <FileCheck className="w-5 h-5 text-blue-600" />
            <span>Documents Required For Admission:</span>
          </h4>
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 text-xs font-semibold text-slate-700">
            <div className="p-3 rounded-xl bg-slate-50 border border-slate-200/70 flex items-center gap-2">
              <CheckCircle2 className="w-4 h-4 text-emerald-600 flex-shrink-0" />
              <span>Previous Year Marksheet</span>
            </div>
            <div className="p-3 rounded-xl bg-slate-50 border border-slate-200/70 flex items-center gap-2">
              <CheckCircle2 className="w-4 h-4 text-emerald-600 flex-shrink-0" />
              <span>Student Aadhar Card</span>
            </div>
            <div className="p-3 rounded-xl bg-slate-50 border border-slate-200/70 flex items-center gap-2">
              <CheckCircle2 className="w-4 h-4 text-emerald-600 flex-shrink-0" />
              <span>2 Passport Size Photos</span>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
