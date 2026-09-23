"use client";

import React, { useState } from "react";
import { Phone, Mail, MapPin, CheckCircle, ArrowRight, Sparkles, ShieldCheck, MessageCircle, Loader2 } from "lucide-react";
import { submitPublicEnquiry } from "@/lib/api";

export default function AdmissionsForm() {
  const [submitted, setSubmitted] = useState<boolean>(false);
  const [isSubmitting, setIsSubmitting] = useState<boolean>(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);
  const [formData, setFormData] = useState({
    name: "",
    parentName: "",
    phone: "",
    email: "",
    grade: "10",
    board: "mpboard",
    stream: "all",
  });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!formData.name || !formData.phone) return;
    setIsSubmitting(true);
    setErrorMsg(null);

    const res = await submitPublicEnquiry({
      student_name: formData.name,
      parent_name: formData.parentName || `${formData.name}'s Parent`,
      phone: formData.phone,
      email: formData.email || undefined,
      target_class: `Class ${formData.grade}`,
      stream: formData.stream,
      remarks: `Board: ${formData.board.toUpperCase()} | Free Demo Booking from Website`,
    });

    setIsSubmitting(false);
    if (res.success) {
      setSubmitted(true);
    } else {
      setErrorMsg(res.error || "Could not submit your enquiry. Please try again or contact us via WhatsApp.");
    }
  };

  return (
    <section id="admissions" className="relative py-24 bg-[#f8fafd] text-slate-900 border-b border-slate-200/80">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="bg-white rounded-3xl p-8 sm:p-12 border border-slate-200 shadow-xl relative overflow-hidden">
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-10 items-center">
            {/* Left Col: Offer details */}
            <div className="lg:col-span-6 space-y-6">
              <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-red-50 border border-red-200 text-[#c22329] text-xs font-bold uppercase tracking-wider">
                <Sparkles className="w-3.5 h-3.5 text-amber-500" />
                <span>Admission Season: April to June 2026</span>
              </div>

              <h2 className="text-3xl sm:text-5xl font-black tracking-tight text-slate-900 leading-tight">
                Join Aarambh Institute <br />
                <span className="text-[#c22329]">For A Free Demo Class</span>
              </h2>

              <p className="text-sm sm:text-base text-slate-600 leading-relaxed font-normal">
                Visit our Hawa Bangla, Indore institute. Meet Director Mrs. Shobhna Vyas and our senior faculty, attend actual classes, and experience our individual attention.
              </p>

              <div className="space-y-3 pt-2">
                <div className="flex items-center gap-3 text-sm text-slate-800 font-semibold">
                  <div className="p-1 rounded-lg bg-emerald-100 text-emerald-700">
                    <CheckCircle className="w-4 h-4" />
                  </div>
                  <span>100% Free Demo Session with Subject Teachers</span>
                </div>
                <div className="flex items-center gap-3 text-sm text-slate-800 font-semibold">
                  <div className="p-1 rounded-lg bg-emerald-100 text-emerald-700">
                    <CheckCircle className="w-4 h-4" />
                  </div>
                  <span>Student-Friendly Monthly Fees (₹800 - ₹1000/mo)</span>
                </div>
                <div className="flex items-center gap-3 text-sm text-slate-800 font-semibold">
                  <div className="p-1 rounded-lg bg-emerald-100 text-emerald-700">
                    <CheckCircle className="w-4 h-4" />
                  </div>
                  <span>Morning & Evening Batches for School/College Routine</span>
                </div>
              </div>

              <div className="pt-4 border-t border-slate-100 space-y-2 text-xs text-slate-600">
                <div className="flex items-center gap-2 font-bold text-slate-900">
                  <MapPin className="w-4 h-4 text-[#c22329] flex-shrink-0" />
                  <span>8 Shantinath Puri, Hawa Bangla, Near Sai Mandir, Indore (MP)</span>
                </div>
                <div className="flex items-center gap-2 font-bold text-slate-900">
                  <Phone className="w-4 h-4 text-blue-600 flex-shrink-0" />
                  <span>Helpline: 88397-14081 / 79097-14081</span>
                </div>
              </div>
            </div>

            {/* Right Col: Interactive Lead Capture Form */}
            <div className="lg:col-span-6">
              {!submitted ? (
                <form
                  onSubmit={handleSubmit}
                  className="bg-[#f8fafd] p-6 sm:p-8 rounded-3xl border border-slate-200 shadow-md space-y-4"
                >
                  <h3 className="text-xl font-bold text-slate-900 mb-1">
                    Book Free Demo Class
                  </h3>
                  <p className="text-xs text-slate-500 mb-4 font-medium">
                    Submit to confirm demo seat. Our team will contact you within 2 hours.
                  </p>

                  <div className="space-y-3.5">
                    <div>
                      <label className="block text-xs font-bold text-slate-700 mb-1">
                        Student Full Name *
                      </label>
                      <input
                        type="text"
                        required
                        placeholder="e.g. Aryan Sharma"
                        value={formData.name}
                        onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                        className="w-full px-4 py-2.5 rounded-xl bg-white border border-slate-200 text-slate-900 placeholder-slate-400 text-sm focus:outline-none focus:border-[#c22329] font-medium"
                      />
                    </div>

                    <div>
                      <label className="block text-xs font-bold text-slate-700 mb-1">
                        Parent / Student Mobile Number *
                      </label>
                      <input
                        type="tel"
                        required
                        placeholder="+91 88397-14081"
                        value={formData.phone}
                        onChange={(e) => setFormData({ ...formData, phone: e.target.value })}
                        className="w-full px-4 py-2.5 rounded-xl bg-white border border-slate-200 text-slate-900 placeholder-slate-400 text-sm focus:outline-none focus:border-[#c22329] font-medium"
                      />
                    </div>

                    <div className="grid grid-cols-2 gap-3">
                      <div>
                        <label className="block text-xs font-bold text-slate-700 mb-1">
                          Class / Degree
                        </label>
                        <select
                          value={formData.grade}
                          onChange={(e) => setFormData({ ...formData, grade: e.target.value })}
                          className="w-full px-4 py-2.5 rounded-xl bg-white border border-slate-200 text-slate-900 text-sm focus:outline-none focus:border-[#c22329] font-medium"
                        >
                          <option value="4-8">Class 4th to 8th</option>
                          <option value="9">Class 9th</option>
                          <option value="10">Class 10th (Board)</option>
                          <option value="11">Class 11th</option>
                          <option value="12">Class 12th (Board)</option>
                          <option value="bcom">B.Com</option>
                          <option value="mcom">M.Com</option>
                          <option value="bba-mba">BBA / MBA</option>
                          <option value="bsc">B.Sc</option>
                        </select>
                      </div>

                      <div>
                        <label className="block text-xs font-bold text-slate-700 mb-1">
                          Board / Univ
                        </label>
                        <select
                          value={formData.board}
                          onChange={(e) => setFormData({ ...formData, board: e.target.value })}
                          className="w-full px-4 py-2.5 rounded-xl bg-white border border-slate-200 text-slate-900 text-sm focus:outline-none focus:border-[#c22329] font-medium"
                        >
                          <option value="mpboard">MP Board</option>
                          <option value="cbse">CBSE</option>
                          <option value="icse">ICSE</option>
                          <option value="university">University Degree</option>
                        </select>
                      </div>
                    </div>
                  </div>

                  {errorMsg && (
                    <p className="text-xs font-semibold text-[#c22329] bg-red-50 border border-red-200 rounded-xl px-3 py-2">
                      {errorMsg}
                    </p>
                  )}

                  <button
                    type="submit"
                    disabled={isSubmitting}
                    className="btn-caramel-gold w-full py-3.5 mt-2 rounded-xl text-sm font-black shadow-md flex items-center justify-center gap-2 disabled:opacity-60 transition-all cursor-pointer"
                  >
                    <span>{isSubmitting ? "Reserving Demo Seat..." : "Confirm Free Demo Seat"}</span>
                    {isSubmitting ? (
                      <Loader2 className="w-4 h-4 animate-spin" />
                    ) : (
                      <ArrowRight className="w-4 h-4" />
                    )}
                  </button>

                  <a
                    href={`https://wa.me/918839714081?text=Hello%20Aarambh%20Institute%2C%20I%20want%20to%20book%20a%20free%20demo%20class%20for%20my%20child.`}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="w-full py-2.5 rounded-xl text-xs font-bold text-emerald-800 bg-emerald-50 hover:bg-emerald-100 border border-emerald-200 transition-all flex items-center justify-center gap-1.5"
                  >
                    <MessageCircle className="w-4 h-4 text-emerald-600" />
                    <span>Or Book Instantly On WhatsApp (88397-14081)</span>
                  </a>
                </form>
              ) : (
                <div className="bg-[#f8fafd] p-8 rounded-3xl border border-emerald-300 text-center space-y-4 shadow-sm animate-in fade-in">
                  <div className="w-16 h-16 rounded-full bg-emerald-100 text-emerald-700 flex items-center justify-center mx-auto">
                    <CheckCircle className="w-8 h-8" />
                  </div>
                  <h3 className="text-2xl font-black text-slate-900">
                    Demo Seat Reserved!
                  </h3>
                  <p className="text-sm text-slate-600 max-w-md mx-auto leading-relaxed">
                    Thank you, <strong className="text-slate-900">{formData.name}</strong>. Our director / academic counselor will call <strong className="text-[#c22329]">{formData.phone}</strong> shortly to confirm your batch time at Hawa Bangla, Indore.
                  </p>
                  <div className="p-4 rounded-2xl bg-white border border-slate-200 text-left text-xs space-y-2 max-w-sm mx-auto">
                    <div className="flex justify-between text-slate-600">
                      <span>Course:</span>
                      <span className="font-bold text-slate-900 uppercase">Class {formData.grade} ({formData.board})</span>
                    </div>
                    <div className="flex justify-between text-slate-600">
                      <span>Campus:</span>
                      <span className="font-bold text-[#c22329]">Hawa Bangla, Near Sai Mandir</span>
                    </div>
                  </div>
                  <button
                    onClick={() => setSubmitted(false)}
                    className="text-xs text-[#c22329] hover:underline mt-2 font-bold"
                  >
                    Book for another student
                  </button>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
