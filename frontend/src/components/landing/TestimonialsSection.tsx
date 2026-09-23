"use client";

import React, { useState } from "react";
import { Star, MessageSquare, CheckCircle, Quote } from "lucide-react";

export default function TestimonialsSection() {
  const [filter, setFilter] = useState<"all" | "parent" | "student">("all");

  const reviews = [
    {
      type: "parent",
      name: "Parent of Dhruvika",
      grade: "Class 6th",
      year: "2023",
      rating: 5,
      text: "Aarambh Institute ke teachers bahut dedicated hain. Mere bachche ke marks aur confidence dono mein kaafi improvement hua hai. Hum institute ki teaching aur guidance se bahut santusht hain.",
      badge: "Parent Testimonial",
    },
    {
      type: "student",
      name: "Yashika",
      grade: "Class 7th",
      year: "2024",
      rating: 5,
      text: "Aarambh Institute mein padhai ka environment bahut positive hai. Teachers har topic ko simple aur interesting tareeke se samjhate hain, jis se padhai aasan lagti hai.",
      badge: "Student Review",
    },
    {
      type: "parent",
      name: "Vaishnavi Patel's Parents",
      grade: "Class 10th Board",
      year: "2025",
      rating: 5,
      text: "Regular tests, personal attention aur progress updates ki wajah se humein bachche ki performance ka poora pata rehta hai. Aarambh Institute sach mein students ke future ko lekar serious hai.",
      badge: "Board Parent Review",
    },
    {
      type: "student",
      name: "Rishabh Bhargav",
      grade: "Class 11th (Science)",
      year: "2025",
      rating: 5,
      text: "Yahan mujhe padhai ke saath motivation bhi milta hai. Teachers hamesha support karte hain aur doubts ko turant solve karte hain.",
      badge: "Senior Student",
    },
    {
      type: "student",
      name: "Gourav Sarothiya",
      grade: "Class 10th",
      year: "2024",
      rating: 5,
      text: "Best guidance for academic success! Dedicated teachers and doubt support helped me score great marks in my board exams.",
      badge: "Class 10 Achiever",
    },
  ];

  const filtered = filter === "all" ? reviews : reviews.filter((r) => r.type === filter);

  return (
    <section className="relative py-24 bg-white text-slate-900 border-b border-slate-200/80">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center max-w-3xl mx-auto space-y-4">
          <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-amber-50 border border-amber-200 text-amber-800 text-xs font-bold uppercase tracking-wider">
            <MessageSquare className="w-3.5 h-3.5 text-amber-600" />
            <span>Student & Parent Testimonials</span>
          </div>

          <h2 className="text-3xl sm:text-5xl font-black tracking-tight text-slate-900">
            What Parents & Students <br />
            <span className="text-[#c22329]">Say About Aarambh Institute</span>
          </h2>

          <p className="text-sm sm:text-base text-slate-600">
            Genuine experiences from families in Indore who trusted Aarambh Institute for their child&apos;s education.
          </p>

          <div className="flex items-center justify-center gap-2 pt-4">
            {[
              { id: "all", label: "All Reviews" },
              { id: "parent", label: "Parent Testimonials" },
              { id: "student", label: "Student Feedback" },
            ].map((t) => (
              <button
                key={t.id}
                onClick={() => setFilter(t.id as any)}
                className={`px-4 py-2 rounded-xl text-xs font-bold transition-all ${
                  filter === t.id
                    ? "bg-[#c22329] text-white shadow-sm"
                    : "bg-slate-100 text-slate-700 hover:text-slate-950 border border-slate-200"
                }`}
              >
                {t.label}
              </button>
            ))}
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mt-14">
          {filtered.map((item, idx) => (
            <div
              key={idx}
              className="light-card-interactive p-7 rounded-3xl flex flex-col justify-between"
            >
              <div>
                <div className="flex items-center justify-between mb-4">
                  <div className="flex items-center gap-1 text-amber-500">
                    {[...Array(item.rating)].map((_, i) => (
                      <Star key={i} className="w-4 h-4 fill-amber-400" />
                    ))}
                  </div>
                  <span className="text-[11px] font-bold px-2.5 py-0.5 rounded-full bg-slate-100 text-slate-600 border border-slate-200">
                    {item.badge}
                  </span>
                </div>

                <p className="text-sm text-slate-700 leading-relaxed italic mb-6 font-normal">
                  &ldquo;{item.text}&rdquo;
                </p>
              </div>

              <div className="pt-4 border-t border-slate-100 flex items-center justify-between">
                <div>
                  <h4 className="font-bold text-slate-900 text-sm">{item.name}</h4>
                  <p className="text-xs text-slate-500 mt-0.5 font-medium">
                    {item.grade} ({item.year})
                  </p>
                </div>
                <div className="flex items-center gap-1 text-emerald-700 text-xs font-bold">
                  <CheckCircle className="w-3.5 h-3.5" />
                  <span>Verified</span>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
