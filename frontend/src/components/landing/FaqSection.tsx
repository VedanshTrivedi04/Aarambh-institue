"use client";

import React, { useState } from "react";
import { HelpCircle, ChevronDown } from "lucide-react";

export default function FaqSection() {
  const [openIndex, setOpenIndex] = useState<number | null>(0);

  const faqs = [
    {
      q: "What is the batch size at Aarambh Institute?",
      a: "Unlike crowded coaching classes with 60-100 students, Aarambh Institute maintains a strict cap of only 20 students per batch. This allows teachers to give personalized attention to every student, check daily classwork, and resolve individual doubts.",
    },
    {
      q: "Who teaches the classes — senior faculty or assistants?",
      a: "100% of our classes and doubt sessions are taken directly by our senior expert educators having between 15 to 30 years of teaching experience, including Founder Mrs. Shobhna Vyas (20 yrs), Mr. Pankaj Dubey (30 yrs), and Mr. Jitendra Shindey (30 yrs).",
    },
    {
      q: "Which boards and classes are taught at the Hawa Bangla campus?",
      a: "We coach students from Class 4th to 12th covering MP Board, CBSE, and ICSE curriculums. We also offer specialized degree coaching for B.Com, M.Com, BBA, MBA, and B.Sc subjects.",
    },
    {
      q: "What is the fee structure at Aarambh Institute?",
      a: "We believe quality education must be student-friendly and affordable. Junior classes (4th to 8th) have a monthly fee of ₹800 to ₹1,000/-. High school and senior classes have highly competitive, transparent fee structures with flexible installment options.",
    },
    {
      q: "Can I attend a free demo class before taking admission?",
      a: "Yes! Every student is entitled to attend free demo classes to experience our teaching methodology, interact with teachers, and see the classroom environment before finalizing admission.",
    },
    {
      q: "What documents are required for admission?",
      a: "To complete the admission process, please bring a copy of the previous year's marksheet, student's Aadhar Card, and 2 passport-size photographs to our campus at 8 Shantinath Puri, Hawa Bangla (Near Sai Mandir), Indore.",
    },
  ];

  return (
    <section className="relative py-24 bg-[#f8fafc] text-slate-900 border-t border-slate-200/80">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center space-y-4 mb-14">
          <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-blue-50 border border-blue-200 text-blue-700 text-xs font-bold uppercase tracking-wider">
            <HelpCircle className="w-3.5 h-3.5" />
            <span>Frequently Asked Questions</span>
          </div>

          <h2 className="text-3xl sm:text-5xl font-black tracking-tight text-slate-900">
            Everything You Need <br />
            <span className="gradient-text-blue">To Know Before Enrolling</span>
          </h2>

          <p className="text-sm sm:text-base text-slate-600">
            Have questions? We are here to help parents and students make an informed decision.
          </p>
        </div>

        {/* Accordion */}
        <div className="space-y-4">
          {faqs.map((faq, idx) => {
            const isOpen = openIndex === idx;
            return (
              <div
                key={idx}
                className="bg-white rounded-2xl border border-slate-200 shadow-sm overflow-hidden transition-all hover:border-blue-300"
              >
                <button
                  onClick={() => setOpenIndex(isOpen ? null : idx)}
                  className="w-full p-5 sm:p-6 text-left flex items-center justify-between gap-4 hover:bg-slate-50 transition-colors"
                >
                  <span className="font-bold text-base sm:text-lg text-slate-900">
                    {faq.q}
                  </span>
                  <div
                    className={`p-1.5 rounded-full bg-slate-100 text-slate-600 flex-shrink-0 transition-transform duration-300 ${
                      isOpen ? "rotate-180 text-blue-600 bg-blue-50 border border-blue-200" : ""
                    }`}
                  >
                    <ChevronDown className="w-4 h-4" />
                  </div>
                </button>

                {isOpen && (
                  <div className="px-5 sm:px-6 pb-6 pt-1 text-sm text-slate-600 leading-relaxed border-t border-slate-100 font-normal animate-in fade-in duration-200">
                    {faq.a}
                  </div>
                )}
              </div>
            );
          })}
        </div>
      </div>
    </section>
  );
}
