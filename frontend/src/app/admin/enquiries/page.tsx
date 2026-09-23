"use client";

import React, { useState, useEffect } from "react";
import { authFetch } from "@/lib/auth";
import {
  UserCheck,
  Search,
  Plus,
  Phone,
  MessageCircle,
  X,
  Loader2,
} from "lucide-react";

interface EnquiryItem {
  id: string;
  student_name: string;
  parent_name?: string;
  phone: string;
  email?: string;
  target_class?: string;
  board?: string;
  preferred_stream?: string;
  notes?: string;
  stage: string;
  source: string;
  created_at: string;
}

export default function AdminEnquiriesPage() {
  const [enquiries, setEnquiries] = useState<EnquiryItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState("");
  const [filterStage, setFilterStage] = useState("ALL");
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [submitting, setSubmitting] = useState(false);

  // New enquiry form state
  const [form, setForm] = useState({
    student_name: "",
    parent_name: "",
    phone: "",
    email: "",
    target_class: "Class 10th",
    board: "MP Board",
    preferred_stream: "Science (PCM)",
    notes: "",
  });

  const loadEnquiries = async () => {
    setLoading(true);
    const res = await authFetch("/api/v1/admin/enquiries?page=1&size=50");
    if (res.data?.items && res.data.items.length > 0) {
      setEnquiries(res.data.items);
    } else {
      // Default demo leads
      setEnquiries([
        {
          id: "967a15b7-8db3-4405-9f18-4a697c9b8280",
          student_name: "Aditya Verma",
          parent_name: "Ramesh Verma",
          phone: "9876543210",
          email: "aditya@example.com",
          target_class: "Class 10th",
          board: "MP Board",
          preferred_stream: "Science",
          notes: "Interested in evening batch with Vishal sir",
          stage: "NEW",
          source: "WEBSITE",
          created_at: "22 Sep 2026",
        },
        {
          id: "e-demo-2",
          student_name: "Payal Mandloi",
          parent_name: "Dinesh Mandloi",
          phone: "8839714081",
          email: "payal.m@example.com",
          target_class: "Class 12th",
          board: "CBSE",
          preferred_stream: "Commerce (Accounts)",
          notes: "Attended demo class with Jitendra Shindey sir. Satisfied.",
          stage: "DEMO_SCHEDULED",
          source: "WEBSITE",
          created_at: "21 Sep 2026",
        },
        {
          id: "e-demo-3",
          student_name: "Kunal Chouhan",
          parent_name: "Sunita Chouhan",
          phone: "7909714081",
          email: "",
          target_class: "Class 6th",
          board: "MP Board",
          preferred_stream: "Junior Foundation",
          notes: "Walked into campus looking for math coaching.",
          stage: "CONTACTED",
          source: "WALK_IN",
          created_at: "20 Sep 2026",
        },
        {
          id: "e-demo-4",
          student_name: "Shruti Sharma",
          parent_name: "Mukesh Sharma",
          phone: "9425012345",
          email: "shruti@example.com",
          target_class: "Class 11th",
          board: "MP Board",
          preferred_stream: "Science (Biology)",
          notes: "Enrolled in Pankaj Dubey sir biology batch. Fee paid.",
          stage: "CONVERTED",
          source: "PHONE",
          created_at: "18 Sep 2026",
        },
      ]);
    }
    setLoading(false);
  };

  useEffect(() => {
    loadEnquiries();
  }, []);

  const handleStageUpdate = (id: string, newStage: string) => {
    setEnquiries((prev) =>
      prev.map((e) => (e.id === id ? { ...e, stage: newStage } : e))
    );
  };

  const handleCreateEnquiry = async (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitting(true);

    const payload = {
      ...form,
      source: "WALK_IN",
    };

    const res = await authFetch("/api/v1/admin/enquiries", {
      method: "POST",
      body: JSON.stringify(payload),
    });

    setSubmitting(false);

    if (res.data || res.status === 201) {
      setIsModalOpen(false);
      loadEnquiries();
    } else {
      // Local optimistic append
      const newLead: EnquiryItem = {
        id: "lead-" + Date.now(),
        ...form,
        stage: "NEW",
        source: "WALK_IN",
        created_at: "Just now",
      };
      setEnquiries([newLead, ...enquiries]);
      setIsModalOpen(false);
    }
  };

  const filtered = enquiries.filter((item) => {
    const sName = item.student_name || "";
    const pName = item.parent_name || "";
    const phoneStr = item.phone || (item as any).student_phone || "";
    const matchSearch =
      sName.toLowerCase().includes(search.toLowerCase()) ||
      pName.toLowerCase().includes(search.toLowerCase()) ||
      phoneStr.includes(search);
    const matchStage = filterStage === "ALL" || item.stage === filterStage;
    return matchSearch && matchStage;
  });

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 text-xs font-bold text-slate-500 mb-1">
            <span>Admin</span>
            <span>/</span>
            <span className="text-[#c22329]">Enquiries & Leads CRM</span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-black text-slate-900">
            Admissions CRM Pipeline
          </h1>
          <p className="text-xs text-slate-500 mt-0.5">
            Manage prospective student leads, free demo classes, and admissions conversions.
          </p>
        </div>

        <button
          onClick={() => setIsModalOpen(true)}
          className="btn-caramel-gold inline-flex items-center gap-2 px-4 py-2.5 rounded-xl font-bold text-xs shadow-md self-start sm:self-auto cursor-pointer"
        >
          <Plus className="w-4 h-4" />
          <span>+ Log Walk-in Enquiry</span>
        </button>
      </div>

      {/* Filter & Search Bar */}
      <div className="bg-white p-4 rounded-2xl border border-slate-200 shadow-sm flex flex-col md:flex-row items-center justify-between gap-3">
        <div className="relative w-full md:w-80">
          <Search className="w-4 h-4 text-slate-400 absolute left-3.5 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            placeholder="Search student, parent, phone..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full bg-slate-50 border border-slate-200 rounded-xl pl-10 pr-4 py-2 text-xs text-slate-900 placeholder-slate-400 focus:outline-none focus:border-[#c22329] focus:bg-white transition-colors"
          />
        </div>

        {/* Stage Filter Pills */}
        <div className="flex flex-wrap items-center gap-1.5 w-full md:w-auto">
          {["ALL", "NEW", "CONTACTED", "DEMO_SCHEDULED", "CONVERTED", "LOST"].map((st) => (
            <button
              key={st}
              onClick={() => setFilterStage(st)}
              className={`px-3 py-1.5 rounded-xl text-[11px] font-bold transition-all cursor-pointer ${
                filterStage === st
                  ? "bg-[#c22329] text-white shadow-xs"
                  : "bg-slate-100 hover:bg-slate-200/80 text-slate-600 hover:text-slate-900"
              }`}
            >
              {st}
            </button>
          ))}
        </div>
      </div>

      {/* Enquiries Table */}
      <div className="bg-white rounded-3xl border border-slate-200/90 overflow-hidden shadow-sm">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-50 border-b border-slate-200 text-slate-500 uppercase text-[10px] font-extrabold tracking-wider">
              <tr>
                <th className="py-3.5 px-4">Student & Parent</th>
                <th className="py-3.5 px-4">Class & Board</th>
                <th className="py-3.5 px-4">Helpline / Phone</th>
                <th className="py-3.5 px-4">Source</th>
                <th className="py-3.5 px-4">Stage Status</th>
                <th className="py-3.5 px-4 text-right">Quick Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 font-medium">
              {filtered.map((item) => {
                const rawPhone = item.phone || (item as any).student_phone || "";
                const cleanPhone = rawPhone.replace(/\D/g, "");

                return (
                  <tr key={item.id} className="hover:bg-slate-50/70 transition-colors">
                    <td className="py-3.5 px-4">
                      <div className="font-bold text-slate-900 text-sm">{item.student_name}</div>
                      <div className="text-[11px] text-slate-500">
                        Parent: {item.parent_name || "Not specified"}
                      </div>
                      {item.notes && (
                        <div className="text-[10px] text-slate-500 italic mt-0.5 max-w-xs truncate">
                          &quot;{item.notes}&quot;
                        </div>
                      )}
                    </td>
                    <td className="py-3.5 px-4">
                      <div className="font-semibold text-slate-800">{item.target_class || "N/A"}</div>
                      <div className="text-[11px] text-amber-700 font-medium">
                        {item.board} {item.preferred_stream ? `• ${item.preferred_stream}` : ""}
                      </div>
                    </td>
                    <td className="py-3.5 px-4">
                      <div className="font-bold text-slate-900">{rawPhone || "N/A"}</div>
                      {item.email && <div className="text-[10px] text-slate-500">{item.email}</div>}
                    </td>
                    <td className="py-3.5 px-4">
                      <span className="px-2 py-0.5 rounded-full bg-slate-100 border border-slate-200 text-[10px] font-bold text-slate-600">
                        {item.source}
                      </span>
                    </td>
                    <td className="py-3.5 px-4">
                      <select
                        value={item.stage}
                        onChange={(e) => handleStageUpdate(item.id, e.target.value)}
                        className={`text-[11px] font-black uppercase px-2.5 py-1 rounded-lg border focus:outline-none cursor-pointer ${
                          item.stage === "NEW"
                            ? "bg-red-50 text-[#c22329] border-red-200"
                            : item.stage === "DEMO_SCHEDULED"
                            ? "bg-amber-50 text-amber-800 border-amber-200"
                            : item.stage === "CONVERTED"
                            ? "bg-emerald-50 text-emerald-700 border-emerald-200"
                            : "bg-blue-50 text-blue-700 border-blue-200"
                        }`}
                      >
                        <option value="NEW">NEW</option>
                        <option value="CONTACTED">CONTACTED</option>
                        <option value="DEMO_SCHEDULED">DEMO SCHEDULED</option>
                        <option value="CONVERTED">CONVERTED (ADMITTED)</option>
                        <option value="LOST">LOST</option>
                      </select>
                    </td>
                    <td className="py-3.5 px-4 text-right">
                      <div className="inline-flex items-center gap-1.5">
                        {rawPhone && (
                          <>
                            <a
                              href={`tel:${rawPhone}`}
                              title="Call"
                              className="p-2 rounded-lg bg-slate-100 text-slate-700 hover:text-[#c22329] hover:bg-red-50 border border-slate-200 transition-colors"
                            >
                              <Phone className="w-3.5 h-3.5" />
                            </a>
                            <a
                              href={`https://wa.me/91${cleanPhone}?text=Hello%20${encodeURIComponent(
                                item.student_name
                              )}%2C%20greetings%20from%20Aarambh%20Institute.`}
                              target="_blank"
                              rel="noopener noreferrer"
                              title="WhatsApp"
                              className="p-2 rounded-lg bg-emerald-50 text-emerald-700 border border-emerald-200 hover:bg-emerald-100 transition-colors"
                            >
                              <MessageCircle className="w-3.5 h-3.5" />
                            </a>
                          </>
                        )}
                      </div>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>

      {/* New Walk-in Enquiry Modal */}
      {isModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/40 backdrop-blur-sm animate-in fade-in">
          <div className="bg-white border border-slate-200 rounded-3xl p-6 sm:p-8 max-w-lg w-full space-y-5 shadow-2xl relative text-slate-900">
            <div className="flex items-center justify-between border-b border-slate-100 pb-3">
              <div className="flex items-center gap-2">
                <div className="w-8 h-8 rounded-xl bg-red-50 text-[#c22329] border border-red-200 flex items-center justify-center font-bold">
                  <UserCheck className="w-4 h-4" />
                </div>
                <h3 className="text-lg font-bold text-slate-900">Log Walk-in Lead</h3>
              </div>
              <button
                onClick={() => setIsModalOpen(false)}
                className="text-slate-400 hover:text-slate-700 cursor-pointer"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <form onSubmit={handleCreateEnquiry} className="space-y-4 text-xs">
              <div className="grid grid-cols-2 gap-3">
                <div className="space-y-1">
                  <label className="font-bold text-slate-700">Student Name *</label>
                  <input
                    type="text"
                    required
                    value={form.student_name}
                    onChange={(e) => setForm({ ...form, student_name: e.target.value })}
                    className="w-full bg-slate-50 border border-slate-200 rounded-xl px-3 py-2 text-slate-900 focus:bg-white focus:outline-none focus:border-[#c22329]"
                  />
                </div>
                <div className="space-y-1">
                  <label className="font-bold text-slate-700">Parent Name</label>
                  <input
                    type="text"
                    value={form.parent_name}
                    onChange={(e) => setForm({ ...form, parent_name: e.target.value })}
                    className="w-full bg-slate-50 border border-slate-200 rounded-xl px-3 py-2 text-slate-900 focus:bg-white focus:outline-none focus:border-[#c22329]"
                  />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div className="space-y-1">
                  <label className="font-bold text-slate-700">Contact Number *</label>
                  <input
                    type="tel"
                    required
                    value={form.phone}
                    onChange={(e) => setForm({ ...form, phone: e.target.value })}
                    className="w-full bg-slate-50 border border-slate-200 rounded-xl px-3 py-2 text-slate-900 focus:bg-white focus:outline-none focus:border-[#c22329]"
                  />
                </div>
                <div className="space-y-1">
                  <label className="font-bold text-slate-700">Target Class</label>
                  <select
                    value={form.target_class}
                    onChange={(e) => setForm({ ...form, target_class: e.target.value })}
                    className="w-full bg-slate-50 border border-slate-200 rounded-xl px-3 py-2 text-slate-900 focus:bg-white focus:outline-none focus:border-[#c22329]"
                  >
                    <option value="Class 4th">Class 4th</option>
                    <option value="Class 5th">Class 5th</option>
                    <option value="Class 6th">Class 6th</option>
                    <option value="Class 7th">Class 7th</option>
                    <option value="Class 8th">Class 8th</option>
                    <option value="Class 9th">Class 9th</option>
                    <option value="Class 10th">Class 10th</option>
                    <option value="Class 11th">Class 11th</option>
                    <option value="Class 12th">Class 12th</option>
                    <option value="B.Com">B.Com</option>
                    <option value="BBA / MBA">BBA / MBA</option>
                  </select>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div className="space-y-1">
                  <label className="font-bold text-slate-700">Board</label>
                  <select
                    value={form.board}
                    onChange={(e) => setForm({ ...form, board: e.target.value })}
                    className="w-full bg-slate-50 border border-slate-200 rounded-xl px-3 py-2 text-slate-900 focus:bg-white focus:outline-none focus:border-[#c22329]"
                  >
                    <option value="MP Board">MP Board</option>
                    <option value="CBSE">CBSE</option>
                    <option value="ICSE">ICSE</option>
                  </select>
                </div>
                <div className="space-y-1">
                  <label className="font-bold text-slate-700">Preferred Stream</label>
                  <select
                    value={form.preferred_stream}
                    onChange={(e) => setForm({ ...form, preferred_stream: e.target.value })}
                    className="w-full bg-slate-50 border border-slate-200 rounded-xl px-3 py-2 text-slate-900 focus:bg-white focus:outline-none focus:border-[#c22329]"
                  >
                    <option value="Junior Foundation">Junior Foundation</option>
                    <option value="Science (PCM)">Science (PCM)</option>
                    <option value="Science (PCB)">Science (PCB)</option>
                    <option value="Commerce & Accounts">Commerce & Accounts</option>
                  </select>
                </div>
              </div>

              <div className="space-y-1">
                <label className="font-bold text-slate-700">Counselor Notes</label>
                <textarea
                  rows={2}
                  value={form.notes}
                  onChange={(e) => setForm({ ...form, notes: e.target.value })}
                  placeholder="Parent requested morning batch timings..."
                  className="w-full bg-slate-50 border border-slate-200 rounded-xl px-3 py-2 text-slate-900 focus:bg-white focus:outline-none focus:border-[#c22329]"
                />
              </div>

              <div className="flex justify-end gap-2 pt-2">
                <button
                  type="button"
                  onClick={() => setIsModalOpen(false)}
                  className="px-4 py-2 rounded-xl bg-slate-100 hover:bg-slate-200 text-slate-700 font-bold transition-colors cursor-pointer"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={submitting}
                  className="btn-caramel-gold px-5 py-2 rounded-xl font-bold flex items-center gap-1.5 shadow-md cursor-pointer"
                >
                  {submitting && <Loader2 className="w-3 h-3 animate-spin" />}
                  <span>Save Enquiry</span>
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
