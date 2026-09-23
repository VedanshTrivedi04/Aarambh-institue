"use client";

import React, { useState, useEffect } from "react";
import Link from "next/link";
import {
  fetchAdminCmsContent,
  updateAdminCmsSection,
  resetAdminCmsDefaults,
} from "@/lib/api";
import {
  Globe,
  Save,
  RotateCcw,
  ExternalLink,
  Plus,
  Trash2,
  CheckCircle2,
  AlertCircle,
  Sparkles,
  Home,
  BookOpen,
  GraduationCap,
  Users,
  Award,
  FileText,
  Phone,
  BookmarkCheck,
  ChevronRight,
  Info,
} from "lucide-react";

type TabKey =
  | "home"
  | "about"
  | "courses"
  | "faculty"
  | "results"
  | "admissions"
  | "contact"
  | "student_corner";

interface TabMeta {
  key: TabKey;
  label: string;
  icon: any;
  publicUrl: string;
  description: string;
}

const TABS: TabMeta[] = [
  {
    key: "home",
    label: "Home Page",
    icon: Home,
    publicUrl: "/",
    description: "Hero banner, trust statistics, value highlights, and primary CTAs.",
  },
  {
    key: "about",
    label: "About Us",
    icon: GraduationCap,
    publicUrl: "/about",
    description: "Director's message, founding story, award recognition, and core values.",
  },
  {
    key: "courses",
    label: "Courses & Fees",
    icon: BookOpen,
    publicUrl: "/courses",
    description: "Batch streams, class ranges, timings, transparent fees, and curriculum bullets.",
  },
  {
    key: "faculty",
    label: "Faculty & Mentors",
    icon: Users,
    publicUrl: "/faculty",
    description: "Subject heads, teaching experience (up to 30 yrs), qualifications, and bio highlights.",
  },
  {
    key: "results",
    label: "Results & Toppers",
    icon: Award,
    publicUrl: "/results",
    description: "Board rankers, merit scores, student quotes, and parent testimonials.",
  },
  {
    key: "admissions",
    label: "Admissions & Demo",
    icon: BookmarkCheck,
    publicUrl: "/admissions",
    description: "4-step enrollment process, required documents, fee rules, and FAQs.",
  },
  {
    key: "contact",
    label: "Contact & Campus",
    icon: Phone,
    publicUrl: "/contact",
    description: "Campus address, helpline phone numbers, WhatsApp, working hours, and Google Maps.",
  },
  {
    key: "student_corner",
    label: "Student Corner",
    icon: FileText,
    publicUrl: "/student-corner",
    description: "Notice board, 2026 academic holidays, and free downloadable formula booklets.",
  },
];

export default function AdminCmsPage() {
  const [activeTab, setActiveTab] = useState<TabKey>("home");
  const [cmsData, setCmsData] = useState<Record<string, any>>({});
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [statusMessage, setStatusMessage] = useState<{
    type: "success" | "error";
    text: string;
  } | null>(null);

  // Load CMS data on mount
  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    setLoading(true);
    setStatusMessage(null);
    const res = await fetchAdminCmsContent();
    if (res.success && res.pages) {
      setCmsData(res.pages);
    } else {
      // Fallback local defaults if API is cold
      setCmsData(getDefaultsFallback());
    }
    setLoading(false);
  };

  const handleSaveCurrentTab = async () => {
    setSaving(true);
    setStatusMessage(null);
    const currentPayload = cmsData[activeTab] || {};
    const res = await updateAdminCmsSection(
      activeTab,
      currentPayload,
      TABS.find((t) => t.key === activeTab)?.label
    );

    if (res.success) {
      setStatusMessage({
        type: "success",
        text: `Changes saved to database! The ${TABS.find((t) => t.key === activeTab)?.label} is now updated live.`,
      });
      setTimeout(() => setStatusMessage(null), 5000);
    } else {
      setStatusMessage({
        type: "error",
        text: res.error || "Failed to save changes to database. Please retry.",
      });
    }
    setSaving(false);
  };

  const handleResetCurrentTab = async () => {
    if (!confirm(`Are you sure you want to reset "${TABS.find((t) => t.key === activeTab)?.label}" to canonical institute defaults?`)) {
      return;
    }
    setSaving(true);
    const res = await resetAdminCmsDefaults(activeTab);
    if (res.success) {
      await loadData();
      setStatusMessage({
        type: "success",
        text: `Section reset to institute canonical defaults!`,
      });
    } else {
      setStatusMessage({
        type: "error",
        text: res.error || "Unable to reset at this moment.",
      });
    }
    setSaving(false);
  };

  // Helper to update active tab state
  const updateActiveSection = (updater: (prev: any) => any) => {
    setCmsData((prev) => ({
      ...prev,
      [activeTab]: updater(prev[activeTab] || {}),
    }));
  };

  const activeMeta = TABS.find((t) => t.key === activeTab)!;
  const currentSection = cmsData[activeTab] || {};

  return (
    <div className="space-y-6 pb-20">
      {/* Top Header Banner */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 bg-white p-6 rounded-3xl border border-slate-200/80 shadow-sm">
        <div className="space-y-1">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-xl bg-red-50 text-[#c22329] border border-red-200 flex items-center justify-center">
              <Globe className="w-4 h-4" />
            </div>
            <span className="text-xs font-bold text-[#c99a5e] uppercase tracking-wider">
              Content Management System (CMS)
            </span>
          </div>
          <h1 className="text-2xl font-black text-slate-900 tracking-tight">
            Dynamic Public Website Editor
          </h1>
          <p className="text-xs sm:text-sm text-slate-600">
            Customize all public-facing pages in real time. Changes are stored in PostgreSQL and immediately rendered on the live portal.
          </p>
        </div>

        <div className="flex items-center gap-2.5">
          <Link
            href={activeMeta.publicUrl}
            target="_blank"
            className="inline-flex items-center gap-2 px-3.5 py-2 rounded-xl text-xs font-bold text-slate-700 bg-slate-100 hover:bg-slate-200 border border-slate-200 transition-colors"
          >
            <ExternalLink className="w-3.5 h-3.5 text-[#c22329]" />
            <span>Preview {activeMeta.label}</span>
          </Link>

          <button
            onClick={handleResetCurrentTab}
            disabled={saving || loading}
            title="Reset to Defaults"
            className="inline-flex items-center gap-1.5 px-3 py-2 rounded-xl text-xs font-semibold text-slate-600 hover:text-slate-900 hover:bg-slate-100 border border-slate-200 transition-colors"
          >
            <RotateCcw className="w-3.5 h-3.5 text-slate-500" />
            <span className="hidden sm:inline">Reset</span>
          </button>

          <button
            onClick={handleSaveCurrentTab}
            disabled={saving || loading}
            className="inline-flex items-center gap-2 px-5 py-2 rounded-xl text-xs font-bold text-white bg-[#c22329] hover:bg-[#a61c22] shadow-md shadow-red-500/20 transition-all disabled:opacity-50"
          >
            <Save className="w-3.5 h-3.5" />
            <span>{saving ? "Saving Changes..." : "Save Changes"}</span>
          </button>
        </div>
      </div>

      {/* Toast Notification */}
      {statusMessage && (
        <div
          className={`p-4 rounded-2xl border flex items-center gap-3 text-xs font-semibold transition-all ${
            statusMessage.type === "success"
              ? "bg-emerald-50 text-emerald-800 border-emerald-200"
              : "bg-red-50 text-red-800 border-red-200"
          }`}
        >
          {statusMessage.type === "success" ? (
            <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0" />
          ) : (
            <AlertCircle className="w-4 h-4 text-red-600 shrink-0" />
          )}
          <span>{statusMessage.text}</span>
        </div>
      )}

      {/* Navigation Sub-Tabs by Page */}
      <div className="flex items-center gap-2 overflow-x-auto pb-2 scrollbar-none">
        {TABS.map((tab) => {
          const Icon = tab.icon;
          const isActive = activeTab === tab.key;
          return (
            <button
              key={tab.key}
              onClick={() => {
                setActiveTab(tab.key);
                setStatusMessage(null);
              }}
              className={`flex items-center gap-2 px-4 py-2.5 rounded-2xl text-xs font-bold transition-all whitespace-nowrap shrink-0 border ${
                isActive
                  ? "bg-white text-[#c22329] border-red-200 shadow-sm shadow-red-500/5 ring-2 ring-red-500/10"
                  : "bg-white/60 text-slate-600 border-slate-200/80 hover:bg-white hover:text-slate-900"
              }`}
            >
              <Icon className={`w-3.5 h-3.5 ${isActive ? "text-[#c22329]" : "text-slate-400"}`} />
              <span>{tab.label}</span>
            </button>
          );
        })}
      </div>

      {/* Main Tab Content Card */}
      <div className="bg-white rounded-3xl border border-slate-200/80 shadow-sm p-6 sm:p-8">
        <div className="flex items-center justify-between pb-6 mb-6 border-b border-slate-100">
          <div>
            <span className="text-[10px] font-black uppercase text-[#c99a5e] tracking-wider">
              Editing Section
            </span>
            <h2 className="text-xl font-bold text-slate-900 flex items-center gap-2">
              <span>{activeMeta.label}</span>
              <span className="text-xs font-normal text-slate-400">({activeMeta.publicUrl})</span>
            </h2>
            <p className="text-xs text-slate-500 mt-0.5">{activeMeta.description}</p>
          </div>

          <div className="hidden sm:flex items-center gap-2 text-xs font-semibold text-slate-400 bg-slate-50 px-3 py-1.5 rounded-xl border border-slate-200">
            <Info className="w-3.5 h-3.5 text-[#c22329]" />
            <span>Database-backed dynamic sync</span>
          </div>
        </div>

        {loading ? (
          <div className="py-20 text-center space-y-3">
            <div className="w-8 h-8 border-2 border-[#c22329] border-t-transparent rounded-full animate-spin mx-auto" />
            <p className="text-xs text-slate-500 font-semibold">Loading page configurations from database...</p>
          </div>
        ) : (
          <div>
            {/* Render Tab Editor according to activeTab */}
            {activeTab === "home" && (
              <HomeEditor section={currentSection} onChange={updateActiveSection} />
            )}
            {activeTab === "about" && (
              <AboutEditor section={currentSection} onChange={updateActiveSection} />
            )}
            {activeTab === "courses" && (
              <CoursesEditor section={currentSection} onChange={updateActiveSection} />
            )}
            {activeTab === "faculty" && (
              <FacultyEditor section={currentSection} onChange={updateActiveSection} />
            )}
            {activeTab === "results" && (
              <ResultsEditor section={currentSection} onChange={updateActiveSection} />
            )}
            {activeTab === "admissions" && (
              <AdmissionsEditor section={currentSection} onChange={updateActiveSection} />
            )}
            {activeTab === "contact" && (
              <ContactEditor section={currentSection} onChange={updateActiveSection} />
            )}
            {activeTab === "student_corner" && (
              <StudentCornerEditor section={currentSection} onChange={updateActiveSection} />
            )}
          </div>
        )}
      </div>
    </div>
  );
}

// ─────────────────────────────────────────────────────────────────────────────
// Sub-Editors for each Public Page
// ─────────────────────────────────────────────────────────────────────────────

function HomeEditor({ section, onChange }: { section: any; onChange: any }) {
  const stats = section.stats || {};
  const uspPoints = section.usp_points || [];

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div>
          <label className="block text-xs font-bold text-slate-700 mb-1.5">
            Hero Top Badge Pill
          </label>
          <input
            type="text"
            value={section.hero_badge || ""}
            onChange={(e) => onChange((s: any) => ({ ...s, hero_badge: e.target.value }))}
            className="w-full px-3.5 py-2.5 rounded-xl border border-slate-200 text-xs font-medium focus:outline-none focus:border-[#c22329]"
            placeholder="e.g. Admissions Open 2026-27 • Hawa Bangla, Indore"
          />
        </div>

        <div>
          <label className="block text-xs font-bold text-slate-700 mb-1.5">
            Hero Headline Prefix
          </label>
          <input
            type="text"
            value={section.hero_title_prefix || ""}
            onChange={(e) => onChange((s: any) => ({ ...s, hero_title_prefix: e.target.value }))}
            className="w-full px-3.5 py-2.5 rounded-xl border border-slate-200 text-xs font-medium focus:outline-none focus:border-[#c22329]"
            placeholder="e.g. Excel in Boards with"
          />
        </div>

        <div>
          <label className="block text-xs font-bold text-slate-700 mb-1.5">
            Hero Headline Highlight (Red Accent)
          </label>
          <input
            type="text"
            value={section.hero_title_highlight || ""}
            onChange={(e) => onChange((s: any) => ({ ...s, hero_title_highlight: e.target.value }))}
            className="w-full px-3.5 py-2.5 rounded-xl border border-slate-200 text-xs font-medium focus:outline-none focus:border-[#c22329]"
            placeholder="e.g. Expert Guidance"
          />
        </div>

        <div>
          <label className="block text-xs font-bold text-slate-700 mb-1.5">
            Primary CTA Button Text
          </label>
          <input
            type="text"
            value={section.primary_cta_text || ""}
            onChange={(e) => onChange((s: any) => ({ ...s, primary_cta_text: e.target.value }))}
            className="w-full px-3.5 py-2.5 rounded-xl border border-slate-200 text-xs font-medium focus:outline-none focus:border-[#c22329]"
            placeholder="e.g. Join Free Demo Class"
          />
        </div>
      </div>

      <div>
        <label className="block text-xs font-bold text-slate-700 mb-1.5">
          Hero Description Paragraph
        </label>
        <textarea
          rows={3}
          value={section.hero_description || ""}
          onChange={(e) => onChange((s: any) => ({ ...s, hero_description: e.target.value }))}
          className="w-full px-3.5 py-2.5 rounded-xl border border-slate-200 text-xs font-medium focus:outline-none focus:border-[#c22329]"
          placeholder="Brief intro for prospective parents and students..."
        />
      </div>

      {/* Hero Stats */}
      <div className="pt-4 border-t border-slate-100">
        <h3 className="text-sm font-bold text-slate-900 mb-3 flex items-center gap-2">
          <Sparkles className="w-4 h-4 text-amber-600" />
          <span>Trust & Experience Metric Badges</span>
        </h3>
        <div className="grid grid-cols-2 sm:grid-cols-3 gap-4">
          <div>
            <label className="block text-[11px] font-bold text-slate-600 mb-1">
              Years Legacy
            </label>
            <input
              type="text"
              value={stats.years_experience || ""}
              onChange={(e) =>
                onChange((s: any) => ({
                  ...s,
                  stats: { ...s.stats, years_experience: e.target.value },
                }))
              }
              className="w-full px-3 py-2 rounded-xl border border-slate-200 text-xs font-semibold focus:outline-none focus:border-[#c22329]"
            />
          </div>

          <div>
            <label className="block text-[11px] font-bold text-slate-600 mb-1">
              Total Mentored Students
            </label>
            <input
              type="text"
              value={stats.total_students || ""}
              onChange={(e) =>
                onChange((s: any) => ({
                  ...s,
                  stats: { ...s.stats, total_students: e.target.value },
                }))
              }
              className="w-full px-3 py-2 rounded-xl border border-slate-200 text-xs font-semibold focus:outline-none focus:border-[#c22329]"
            />
          </div>

          <div>
            <label className="block text-[11px] font-bold text-slate-600 mb-1">
              Highest Board Score
            </label>
            <input
              type="text"
              value={stats.highest_board_score || ""}
              onChange={(e) =>
                onChange((s: any) => ({
                  ...s,
                  stats: { ...s.stats, highest_board_score: e.target.value },
                }))
              }
              className="w-full px-3 py-2 rounded-xl border border-slate-200 text-xs font-semibold focus:outline-none focus:border-[#c22329]"
            />
          </div>

          <div>
            <label className="block text-[11px] font-bold text-slate-600 mb-1">
              Board Pass Rate
            </label>
            <input
              type="text"
              value={stats.board_pass_rate || ""}
              onChange={(e) =>
                onChange((s: any) => ({
                  ...s,
                  stats: { ...s.stats, board_pass_rate: e.target.value },
                }))
              }
              className="w-full px-3 py-2 rounded-xl border border-slate-200 text-xs font-semibold focus:outline-none focus:border-[#c22329]"
            />
          </div>

          <div>
            <label className="block text-[11px] font-bold text-slate-600 mb-1">
              Faculty Count
            </label>
            <input
              type="text"
              value={stats.faculty_count || ""}
              onChange={(e) =>
                onChange((s: any) => ({
                  ...s,
                  stats: { ...s.stats, faculty_count: e.target.value },
                }))
              }
              className="w-full px-3 py-2 rounded-xl border border-slate-200 text-xs font-semibold focus:outline-none focus:border-[#c22329]"
            />
          </div>

          <div>
            <label className="block text-[11px] font-bold text-slate-600 mb-1">
              Batch Size Limit
            </label>
            <input
              type="text"
              value={stats.batch_size_limit || ""}
              onChange={(e) =>
                onChange((s: any) => ({
                  ...s,
                  stats: { ...s.stats, batch_size_limit: e.target.value },
                }))
              }
              className="w-full px-3 py-2 rounded-xl border border-slate-200 text-xs font-semibold focus:outline-none focus:border-[#c22329]"
            />
          </div>
        </div>
      </div>

      {/* Bullet USPs */}
      <div className="pt-4 border-t border-slate-100">
        <label className="block text-xs font-bold text-slate-700 mb-2">
          Key Highlight Bullet Points (Hero Badges)
        </label>
        <div className="space-y-2">
          {uspPoints.map((usp: string, idx: number) => (
            <div key={idx} className="flex items-center gap-2">
              <input
                type="text"
                value={usp}
                onChange={(e) => {
                  const updated = [...uspPoints];
                  updated[idx] = e.target.value;
                  onChange((s: any) => ({ ...s, usp_points: updated }));
                }}
                className="flex-1 px-3 py-2 rounded-xl border border-slate-200 text-xs font-medium focus:outline-none focus:border-[#c22329]"
              />
              <button
                type="button"
                onClick={() => {
                  const updated = uspPoints.filter((_: any, i: number) => i !== idx);
                  onChange((s: any) => ({ ...s, usp_points: updated }));
                }}
                className="p-2 text-slate-400 hover:text-red-600 rounded-lg hover:bg-red-50"
              >
                <Trash2 className="w-3.5 h-3.5" />
              </button>
            </div>
          ))}
          <button
            type="button"
            onClick={() => {
              onChange((s: any) => ({
                ...s,
                usp_points: [...uspPoints, "New Key Advantage"],
              }));
            }}
            className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-xl border border-dashed border-slate-300 text-xs font-bold text-[#c22329] hover:bg-red-50"
          >
            <Plus className="w-3.5 h-3.5" />
            <span>Add Highlight Bullet</span>
          </button>
        </div>
      </div>
    </div>
  );
}

function AboutEditor({ section, onChange }: { section: any; onChange: any }) {
  const paragraphs = section.paragraphs || [];
  const coreValues = section.core_values || [];

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div>
          <label className="block text-xs font-bold text-slate-700 mb-1.5">
            Section Title
          </label>
          <input
            type="text"
            value={section.title || ""}
            onChange={(e) => onChange((s: any) => ({ ...s, title: e.target.value }))}
            className="w-full px-3.5 py-2.5 rounded-xl border border-slate-200 text-xs font-medium focus:outline-none focus:border-[#c22329]"
          />
        </div>

        <div>
          <label className="block text-xs font-bold text-slate-700 mb-1.5">
            Award Title / Distinction
          </label>
          <input
            type="text"
            value={section.award_title || ""}
            onChange={(e) => onChange((s: any) => ({ ...s, award_title: e.target.value }))}
            className="w-full px-3.5 py-2.5 rounded-xl border border-slate-200 text-xs font-medium focus:outline-none focus:border-[#c22329]"
          />
        </div>

        <div>
          <label className="block text-xs font-bold text-slate-700 mb-1.5">
            Director Name
          </label>
          <input
            type="text"
            value={section.director_name || ""}
            onChange={(e) => onChange((s: any) => ({ ...s, director_name: e.target.value }))}
            className="w-full px-3.5 py-2.5 rounded-xl border border-slate-200 text-xs font-medium focus:outline-none focus:border-[#c22329]"
          />
        </div>

        <div>
          <label className="block text-xs font-bold text-slate-700 mb-1.5">
            Director Experience
          </label>
          <input
            type="text"
            value={section.director_experience || ""}
            onChange={(e) => onChange((s: any) => ({ ...s, director_experience: e.target.value }))}
            className="w-full px-3.5 py-2.5 rounded-xl border border-slate-200 text-xs font-medium focus:outline-none focus:border-[#c22329]"
          />
        </div>
      </div>

      <div>
        <label className="block text-xs font-bold text-slate-700 mb-1.5">
          Director&apos;s Personal Message Quote
        </label>
        <textarea
          rows={3}
          value={section.director_quote || ""}
          onChange={(e) => onChange((s: any) => ({ ...s, director_quote: e.target.value }))}
          className="w-full px-3.5 py-2.5 rounded-xl border border-slate-200 text-xs font-medium focus:outline-none focus:border-[#c22329]"
        />
      </div>

      {/* Paragraphs */}
      <div className="pt-4 border-t border-slate-100">
        <label className="block text-xs font-bold text-slate-700 mb-2">
          Story & Background Paragraphs
        </label>
        <div className="space-y-3">
          {paragraphs.map((p: string, idx: number) => (
            <div key={idx} className="flex gap-2">
              <textarea
                rows={2}
                value={p}
                onChange={(e) => {
                  const updated = [...paragraphs];
                  updated[idx] = e.target.value;
                  onChange((s: any) => ({ ...s, paragraphs: updated }));
                }}
                className="flex-1 px-3 py-2 rounded-xl border border-slate-200 text-xs font-medium focus:outline-none focus:border-[#c22329]"
              />
              <button
                type="button"
                onClick={() => {
                  const updated = paragraphs.filter((_: any, i: number) => i !== idx);
                  onChange((s: any) => ({ ...s, paragraphs: updated }));
                }}
                className="p-2 text-slate-400 hover:text-red-600 rounded-lg hover:bg-red-50 self-start"
              >
                <Trash2 className="w-3.5 h-3.5" />
              </button>
            </div>
          ))}
          <button
            type="button"
            onClick={() => {
              onChange((s: any) => ({
                ...s,
                paragraphs: [...paragraphs, "New story paragraph..."],
              }));
            }}
            className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-xl border border-dashed border-slate-300 text-xs font-bold text-[#c22329] hover:bg-red-50"
          >
            <Plus className="w-3.5 h-3.5" />
            <span>Add Paragraph</span>
          </button>
        </div>
      </div>

      {/* Core Values */}
      <div className="pt-4 border-t border-slate-100">
        <label className="block text-xs font-bold text-slate-700 mb-2">
          Institute Core Values
        </label>
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
          {coreValues.map((val: any, idx: number) => (
            <div key={idx} className="p-3.5 rounded-2xl bg-slate-50 border border-slate-200 space-y-2">
              <input
                type="text"
                value={val.title || ""}
                onChange={(e) => {
                  const updated = [...coreValues];
                  updated[idx] = { ...val, title: e.target.value };
                  onChange((s: any) => ({ ...s, core_values: updated }));
                }}
                className="w-full px-2.5 py-1.5 rounded-lg border border-slate-200 text-xs font-bold text-slate-900 bg-white"
                placeholder="Value Title"
              />
              <textarea
                rows={2}
                value={val.desc || ""}
                onChange={(e) => {
                  const updated = [...coreValues];
                  updated[idx] = { ...val, desc: e.target.value };
                  onChange((s: any) => ({ ...s, core_values: updated }));
                }}
                className="w-full px-2.5 py-1.5 rounded-lg border border-slate-200 text-[11px] text-slate-600 bg-white"
                placeholder="Description"
              />
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

function CoursesEditor({ section, onChange }: { section: any; onChange: any }) {
  const courses = section.courses_list || [];

  const handleUpdateCourse = (idx: number, field: string, val: any) => {
    const updated = [...courses];
    updated[idx] = { ...updated[idx], [field]: val };
    onChange((s: any) => ({ ...s, courses_list: updated }));
  };

  const handleAddCourse = () => {
    const newCourse = {
      id: `course-${Date.now()}`,
      category: "school",
      title: "New Coaching Course",
      subtitle: "Comprehensive Subject Guidance",
      target: "Classes 9th to 12th",
      duration: "1 Academic Year",
      board: "MP Board / CBSE",
      timings: "5:00 PM - 7:00 PM",
      batch_size: "Strict 20 Students",
      fee: "₹1,000/month",
      badge: "Enrollment Open",
      badge_color: "bg-red-50 text-[#c22329] border-red-200",
      features: [
        "Small Batches of 20 Students",
        "Weekly Test Evaluations",
        "Complete Study Notes",
      ],
      popular: false,
    };
    onChange((s: any) => ({ ...s, courses_list: [...courses, newCourse] }));
  };

  const handleDeleteCourse = (idx: number) => {
    const updated = courses.filter((_: any, i: number) => i !== idx);
    onChange((s: any) => ({ ...s, courses_list: updated }));
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-sm font-bold text-slate-900">Academic Batches & Fee Structure</h3>
          <p className="text-xs text-slate-500">Manage course cards displayed on the public Courses page and home page.</p>
        </div>
        <button
          type="button"
          onClick={handleAddCourse}
          className="inline-flex items-center gap-1.5 px-3.5 py-2 rounded-xl bg-red-50 text-[#c22329] border border-red-200 text-xs font-bold hover:bg-red-100 transition-colors"
        >
          <Plus className="w-3.5 h-3.5" />
          <span>Add Course Card</span>
        </button>
      </div>

      <div className="space-y-4">
        {courses.map((course: any, idx: number) => (
          <div key={course.id || idx} className="p-5 rounded-2xl bg-slate-50 border border-slate-200 space-y-4">
            <div className="flex items-center justify-between">
              <span className="text-xs font-black px-2.5 py-1 rounded-md bg-white border border-slate-200 text-slate-700">
                #{idx + 1} • {course.id}
              </span>
              <button
                type="button"
                onClick={() => handleDeleteCourse(idx)}
                className="text-xs font-bold text-red-600 hover:text-red-700 inline-flex items-center gap-1 p-1 hover:bg-red-100 rounded"
              >
                <Trash2 className="w-3.5 h-3.5" />
                <span>Remove</span>
              </button>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
              <div>
                <label className="block text-[11px] font-bold text-slate-600 mb-1">Course Title</label>
                <input
                  type="text"
                  value={course.title || ""}
                  onChange={(e) => handleUpdateCourse(idx, "title", e.target.value)}
                  className="w-full px-3 py-2 rounded-xl border border-slate-200 text-xs font-semibold bg-white"
                />
              </div>

              <div>
                <label className="block text-[11px] font-bold text-slate-600 mb-1">Target Audience</label>
                <input
                  type="text"
                  value={course.target || ""}
                  onChange={(e) => handleUpdateCourse(idx, "target", e.target.value)}
                  className="w-full px-3 py-2 rounded-xl border border-slate-200 text-xs font-medium bg-white"
                />
              </div>

              <div>
                <label className="block text-[11px] font-bold text-slate-600 mb-1">Fee Structure</label>
                <input
                  type="text"
                  value={course.fee || ""}
                  onChange={(e) => handleUpdateCourse(idx, "fee", e.target.value)}
                  className="w-full px-3 py-2 rounded-xl border border-slate-200 text-xs font-medium bg-white"
                />
              </div>

              <div>
                <label className="block text-[11px] font-bold text-slate-600 mb-1">Batch Timings</label>
                <input
                  type="text"
                  value={course.timings || ""}
                  onChange={(e) => handleUpdateCourse(idx, "timings", e.target.value)}
                  className="w-full px-3 py-2 rounded-xl border border-slate-200 text-xs font-medium bg-white"
                />
              </div>

              <div>
                <label className="block text-[11px] font-bold text-slate-600 mb-1">Batch Size Cap</label>
                <input
                  type="text"
                  value={course.batch_size || ""}
                  onChange={(e) => handleUpdateCourse(idx, "batch_size", e.target.value)}
                  className="w-full px-3 py-2 rounded-xl border border-slate-200 text-xs font-medium bg-white"
                />
              </div>

              <div>
                <label className="block text-[11px] font-bold text-slate-600 mb-1">Badge Label</label>
                <input
                  type="text"
                  value={course.badge || ""}
                  onChange={(e) => handleUpdateCourse(idx, "badge", e.target.value)}
                  className="w-full px-3 py-2 rounded-xl border border-slate-200 text-xs font-medium bg-white"
                />
              </div>
            </div>

            <div>
              <label className="block text-[11px] font-bold text-slate-600 mb-1">Subtitle</label>
              <input
                type="text"
                value={course.subtitle || ""}
                onChange={(e) => handleUpdateCourse(idx, "subtitle", e.target.value)}
                className="w-full px-3 py-2 rounded-xl border border-slate-200 text-xs font-medium bg-white"
              />
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

function FacultyEditor({ section, onChange }: { section: any; onChange: any }) {
  const faculty = section.faculty_list || [];

  const handleUpdateFaculty = (idx: number, field: string, val: any) => {
    const updated = [...faculty];
    updated[idx] = { ...updated[idx], [field]: val };
    onChange((s: any) => ({ ...s, faculty_list: updated }));
  };

  const handleAddFaculty = () => {
    const newFaculty = {
      name: "New Faculty Educator",
      subject: "Science & Mathematics",
      experience: "10 Years Experience",
      highlight: "Senior Subject Mentor",
      specialty: "Conceptual Clarity & Speed Techniques",
      initials: "FE",
      avatar_bg: "bg-blue-50 text-blue-800",
      subject_badge: "bg-blue-50 text-blue-800 border-blue-200",
    };
    onChange((s: any) => ({ ...s, faculty_list: [...faculty, newFaculty] }));
  };

  const handleDeleteFaculty = (idx: number) => {
    const updated = faculty.filter((_: any, i: number) => i !== idx);
    onChange((s: any) => ({ ...s, faculty_list: updated }));
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-sm font-bold text-slate-900">Faculty Members & Mentors</h3>
          <p className="text-xs text-slate-500">Configure veteran educator cards shown on the website.</p>
        </div>
        <button
          type="button"
          onClick={handleAddFaculty}
          className="inline-flex items-center gap-1.5 px-3.5 py-2 rounded-xl bg-red-50 text-[#c22329] border border-red-200 text-xs font-bold hover:bg-red-100 transition-colors"
        >
          <Plus className="w-3.5 h-3.5" />
          <span>Add Faculty Member</span>
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {faculty.map((f: any, idx: number) => (
          <div key={idx} className="p-4 rounded-2xl bg-slate-50 border border-slate-200 space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-xs font-black text-slate-800">
                #{idx + 1} {f.name}
              </span>
              <button
                type="button"
                onClick={() => handleDeleteFaculty(idx)}
                className="text-xs text-red-600 hover:text-red-700 font-bold"
              >
                Delete
              </button>
            </div>

            <div className="grid grid-cols-2 gap-2.5">
              <div>
                <label className="block text-[10px] font-bold text-slate-500 mb-0.5">Name</label>
                <input
                  type="text"
                  value={f.name || ""}
                  onChange={(e) => handleUpdateFaculty(idx, "name", e.target.value)}
                  className="w-full px-2.5 py-1.5 rounded-lg border border-slate-200 text-xs bg-white font-bold"
                />
              </div>

              <div>
                <label className="block text-[10px] font-bold text-slate-500 mb-0.5">Subject</label>
                <input
                  type="text"
                  value={f.subject || ""}
                  onChange={(e) => handleUpdateFaculty(idx, "subject", e.target.value)}
                  className="w-full px-2.5 py-1.5 rounded-lg border border-slate-200 text-xs bg-white font-semibold text-[#c22329]"
                />
              </div>

              <div>
                <label className="block text-[10px] font-bold text-slate-500 mb-0.5">Experience</label>
                <input
                  type="text"
                  value={f.experience || ""}
                  onChange={(e) => handleUpdateFaculty(idx, "experience", e.target.value)}
                  className="w-full px-2.5 py-1.5 rounded-lg border border-slate-200 text-xs bg-white"
                />
              </div>

              <div>
                <label className="block text-[10px] font-bold text-slate-500 mb-0.5">Initials</label>
                <input
                  type="text"
                  value={f.initials || ""}
                  onChange={(e) => handleUpdateFaculty(idx, "initials", e.target.value)}
                  className="w-full px-2.5 py-1.5 rounded-lg border border-slate-200 text-xs bg-white uppercase font-bold"
                />
              </div>
            </div>

            <div>
              <label className="block text-[10px] font-bold text-slate-500 mb-0.5">Highlight</label>
              <input
                type="text"
                value={f.highlight || ""}
                onChange={(e) => handleUpdateFaculty(idx, "highlight", e.target.value)}
                className="w-full px-2.5 py-1.5 rounded-lg border border-slate-200 text-xs bg-white"
              />
            </div>

            <div>
              <label className="block text-[10px] font-bold text-slate-500 mb-0.5">Specialty</label>
              <input
                type="text"
                value={f.specialty || ""}
                onChange={(e) => handleUpdateFaculty(idx, "specialty", e.target.value)}
                className="w-full px-2.5 py-1.5 rounded-lg border border-slate-200 text-xs bg-white"
              />
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

function ResultsEditor({ section, onChange }: { section: any; onChange: any }) {
  const toppers = section.featured_toppers || [];
  const testimonials = section.testimonials || [];

  return (
    <div className="space-y-6">
      {/* Featured Toppers */}
      <div>
        <h3 className="text-sm font-bold text-slate-900 mb-3 flex items-center gap-2">
          <Award className="w-4 h-4 text-amber-600" />
          <span>Featured Board Rankers</span>
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
          {toppers.map((t: any, idx: number) => (
            <div key={idx} className="p-4 rounded-2xl bg-slate-50 border border-slate-200 space-y-2.5">
              <div className="flex items-center justify-between">
                <span className="text-xs font-black text-slate-900">{t.name}</span>
                <span className="text-[10px] font-black px-1.5 py-0.5 rounded bg-amber-100 text-amber-800">
                  {t.rank}
                </span>
              </div>

              <div className="grid grid-cols-2 gap-2">
                <div>
                  <label className="block text-[10px] font-bold text-slate-500">Score %</label>
                  <input
                    type="text"
                    value={t.score || ""}
                    onChange={(e) => {
                      const updated = [...toppers];
                      updated[idx] = { ...t, score: e.target.value };
                      onChange((s: any) => ({ ...s, featured_toppers: updated }));
                    }}
                    className="w-full px-2 py-1.5 rounded-lg border border-slate-200 text-xs font-bold text-[#c22329] bg-white"
                  />
                </div>
                <div>
                  <label className="block text-[10px] font-bold text-slate-500">Grade / Class</label>
                  <input
                    type="text"
                    value={t.grade || ""}
                    onChange={(e) => {
                      const updated = [...toppers];
                      updated[idx] = { ...t, grade: e.target.value };
                      onChange((s: any) => ({ ...s, featured_toppers: updated }));
                    }}
                    className="w-full px-2 py-1.5 rounded-lg border border-slate-200 text-xs bg-white"
                  />
                </div>
              </div>

              <div>
                <label className="block text-[10px] font-bold text-slate-500">Student Quote</label>
                <textarea
                  rows={2}
                  value={t.quote || ""}
                  onChange={(e) => {
                    const updated = [...toppers];
                    updated[idx] = { ...t, quote: e.target.value };
                    onChange((s: any) => ({ ...s, featured_toppers: updated }));
                  }}
                  className="w-full px-2 py-1.5 rounded-lg border border-slate-200 text-[11px] bg-white"
                />
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Testimonials */}
      <div className="pt-4 border-t border-slate-100">
        <h3 className="text-sm font-bold text-slate-900 mb-3">Parent & Student Testimonials</h3>
        <div className="space-y-3">
          {testimonials.map((test: any, idx: number) => (
            <div key={idx} className="p-3.5 rounded-2xl bg-slate-50 border border-slate-200 space-y-2">
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-2">
                <input
                  type="text"
                  value={test.name || ""}
                  onChange={(e) => {
                    const updated = [...testimonials];
                    updated[idx] = { ...test, name: e.target.value };
                    onChange((s: any) => ({ ...s, testimonials: updated }));
                  }}
                  className="px-2.5 py-1.5 rounded-lg border border-slate-200 text-xs font-bold bg-white"
                  placeholder="Reviewer Name"
                />
                <input
                  type="text"
                  value={test.class_info || ""}
                  onChange={(e) => {
                    const updated = [...testimonials];
                    updated[idx] = { ...test, class_info: e.target.value };
                    onChange((s: any) => ({ ...s, testimonials: updated }));
                  }}
                  className="px-2.5 py-1.5 rounded-lg border border-slate-200 text-xs bg-white"
                  placeholder="Class Info"
                />
                <input
                  type="text"
                  value={test.role || ""}
                  onChange={(e) => {
                    const updated = [...testimonials];
                    updated[idx] = { ...test, role: e.target.value };
                    onChange((s: any) => ({ ...s, testimonials: updated }));
                  }}
                  className="px-2.5 py-1.5 rounded-lg border border-slate-200 text-xs bg-white text-slate-500"
                  placeholder="Parent / Student Review"
                />
              </div>
              <textarea
                rows={2}
                value={test.review || ""}
                onChange={(e) => {
                  const updated = [...testimonials];
                  updated[idx] = { ...test, review: e.target.value };
                  onChange((s: any) => ({ ...s, testimonials: updated }));
                }}
                className="w-full px-2.5 py-1.5 rounded-lg border border-slate-200 text-xs bg-white"
                placeholder="Review content..."
              />
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

function AdmissionsEditor({ section, onChange }: { section: any; onChange: any }) {
  const steps = section.admission_steps || [];
  const faqs = section.faqs || [];
  const docs = section.documents_required || [];

  return (
    <div className="space-y-6">
      {/* 4 Steps */}
      <div>
        <h3 className="text-sm font-bold text-slate-900 mb-3">Simple 4-Step Admission Journey</h3>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
          {steps.map((step: any, idx: number) => (
            <div key={idx} className="p-3.5 rounded-2xl bg-slate-50 border border-slate-200 space-y-2">
              <div className="flex items-center gap-2">
                <span className="w-6 h-6 rounded-lg bg-red-100 text-[#c22329] font-black text-xs flex items-center justify-center">
                  {step.step || `0${idx + 1}`}
                </span>
                <input
                  type="text"
                  value={step.title || ""}
                  onChange={(e) => {
                    const updated = [...steps];
                    updated[idx] = { ...step, title: e.target.value };
                    onChange((s: any) => ({ ...s, admission_steps: updated }));
                  }}
                  className="flex-1 px-2.5 py-1 rounded-lg border border-slate-200 text-xs font-bold bg-white"
                />
              </div>
              <textarea
                rows={2}
                value={step.desc || ""}
                onChange={(e) => {
                  const updated = [...steps];
                  updated[idx] = { ...step, desc: e.target.value };
                  onChange((s: any) => ({ ...s, admission_steps: updated }));
                }}
                className="w-full px-2.5 py-1.5 rounded-lg border border-slate-200 text-xs bg-white"
              />
            </div>
          ))}
        </div>
      </div>

      {/* FAQs */}
      <div className="pt-4 border-t border-slate-100">
        <h3 className="text-sm font-bold text-slate-900 mb-3">Frequently Asked Questions (Admissions FAQ)</h3>
        <div className="space-y-3">
          {faqs.map((faq: any, idx: number) => (
            <div key={idx} className="p-3.5 rounded-2xl bg-slate-50 border border-slate-200 space-y-2">
              <input
                type="text"
                value={faq.question || ""}
                onChange={(e) => {
                  const updated = [...faqs];
                  updated[idx] = { ...faq, question: e.target.value };
                  onChange((s: any) => ({ ...s, faqs: updated }));
                }}
                className="w-full px-2.5 py-1.5 rounded-lg border border-slate-200 text-xs font-bold bg-white"
                placeholder="Question"
              />
              <textarea
                rows={2}
                value={faq.answer || ""}
                onChange={(e) => {
                  const updated = [...faqs];
                  updated[idx] = { ...faq, answer: e.target.value };
                  onChange((s: any) => ({ ...s, faqs: updated }));
                }}
                className="w-full px-2.5 py-1.5 rounded-lg border border-slate-200 text-xs bg-white"
                placeholder="Answer"
              />
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

function ContactEditor({ section, onChange }: { section: any; onChange: any }) {
  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
      <div>
        <label className="block text-xs font-bold text-slate-700 mb-1.5">Institute Name</label>
        <input
          type="text"
          value={section.institute_name || ""}
          onChange={(e) => onChange((s: any) => ({ ...s, institute_name: e.target.value }))}
          className="w-full px-3.5 py-2.5 rounded-xl border border-slate-200 text-xs font-bold"
        />
      </div>

      <div>
        <label className="block text-xs font-bold text-slate-700 mb-1.5">Campus Tagline</label>
        <input
          type="text"
          value={section.tagline || ""}
          onChange={(e) => onChange((s: any) => ({ ...s, tagline: e.target.value }))}
          className="w-full px-3.5 py-2.5 rounded-xl border border-slate-200 text-xs"
        />
      </div>

      <div className="sm:col-span-2">
        <label className="block text-xs font-bold text-slate-700 mb-1.5">Campus Full Address</label>
        <input
          type="text"
          value={section.full_address || ""}
          onChange={(e) => onChange((s: any) => ({ ...s, full_address: e.target.value }))}
          className="w-full px-3.5 py-2.5 rounded-xl border border-slate-200 text-xs"
        />
      </div>

      <div>
        <label className="block text-xs font-bold text-slate-700 mb-1.5">Primary Helpline Phone</label>
        <input
          type="text"
          value={section.primary_phone || ""}
          onChange={(e) => onChange((s: any) => ({ ...s, primary_phone: e.target.value }))}
          className="w-full px-3.5 py-2.5 rounded-xl border border-slate-200 text-xs font-bold text-[#c22329]"
        />
      </div>

      <div>
        <label className="block text-xs font-bold text-slate-700 mb-1.5">Secondary Helpline Phone</label>
        <input
          type="text"
          value={section.secondary_phone || ""}
          onChange={(e) => onChange((s: any) => ({ ...s, secondary_phone: e.target.value }))}
          className="w-full px-3.5 py-2.5 rounded-xl border border-slate-200 text-xs"
        />
      </div>

      <div>
        <label className="block text-xs font-bold text-slate-700 mb-1.5">Official WhatsApp Number</label>
        <input
          type="text"
          value={section.whatsapp_number || ""}
          onChange={(e) => onChange((s: any) => ({ ...s, whatsapp_number: e.target.value }))}
          className="w-full px-3.5 py-2.5 rounded-xl border border-slate-200 text-xs font-semibold text-emerald-700"
        />
      </div>

      <div>
        <label className="block text-xs font-bold text-slate-700 mb-1.5">Contact Email Address</label>
        <input
          type="email"
          value={section.email || ""}
          onChange={(e) => onChange((s: any) => ({ ...s, email: e.target.value }))}
          className="w-full px-3.5 py-2.5 rounded-xl border border-slate-200 text-xs"
        />
      </div>

      <div>
        <label className="block text-xs font-bold text-slate-700 mb-1.5">Working Hours</label>
        <input
          type="text"
          value={section.working_hours || ""}
          onChange={(e) => onChange((s: any) => ({ ...s, working_hours: e.target.value }))}
          className="w-full px-3.5 py-2.5 rounded-xl border border-slate-200 text-xs"
        />
      </div>

      <div>
        <label className="block text-xs font-bold text-slate-700 mb-1.5">Google Maps Link</label>
        <input
          type="text"
          value={section.google_maps_url || ""}
          onChange={(e) => onChange((s: any) => ({ ...s, google_maps_url: e.target.value }))}
          className="w-full px-3.5 py-2.5 rounded-xl border border-slate-200 text-xs"
        />
      </div>
    </div>
  );
}

function StudentCornerEditor({ section, onChange }: { section: any; onChange: any }) {
  const notices = section.notices || [];
  const holidays = section.holidays || [];
  const materials = section.materials || [];

  return (
    <div className="space-y-6">
      {/* Notice Board */}
      <div>
        <h3 className="text-sm font-bold text-slate-900 mb-3">Notice Board Bulletins</h3>
        <div className="space-y-3">
          {notices.map((n: any, idx: number) => (
            <div key={idx} className="p-3.5 rounded-2xl bg-slate-50 border border-slate-200 space-y-2">
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-2">
                <input
                  type="text"
                  value={n.date || ""}
                  onChange={(e) => {
                    const updated = [...notices];
                    updated[idx] = { ...n, date: e.target.value };
                    onChange((s: any) => ({ ...s, notices: updated }));
                  }}
                  className="px-2.5 py-1.5 rounded-lg border border-slate-200 text-xs bg-white"
                  placeholder="Date"
                />
                <input
                  type="text"
                  value={n.title || ""}
                  onChange={(e) => {
                    const updated = [...notices];
                    updated[idx] = { ...n, title: e.target.value };
                    onChange((s: any) => ({ ...s, notices: updated }));
                  }}
                  className="sm:col-span-2 px-2.5 py-1.5 rounded-lg border border-slate-200 text-xs font-bold bg-white"
                  placeholder="Notice Title"
                />
              </div>
              <textarea
                rows={2}
                value={n.desc || ""}
                onChange={(e) => {
                  const updated = [...notices];
                  updated[idx] = { ...n, desc: e.target.value };
                  onChange((s: any) => ({ ...s, notices: updated }));
                }}
                className="w-full px-2.5 py-1.5 rounded-lg border border-slate-200 text-xs bg-white"
                placeholder="Description"
              />
            </div>
          ))}
        </div>
      </div>

      {/* Free Study Materials */}
      <div className="pt-4 border-t border-slate-100">
        <h3 className="text-sm font-bold text-slate-900 mb-3">Downloadable Formula Booklets & Materials</h3>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
          {materials.map((m: any, idx: number) => (
            <div key={idx} className="p-3.5 rounded-2xl bg-slate-50 border border-slate-200 space-y-2">
              <input
                type="text"
                value={m.title || ""}
                onChange={(e) => {
                  const updated = [...materials];
                  updated[idx] = { ...m, title: e.target.value };
                  onChange((s: any) => ({ ...s, materials: updated }));
                }}
                className="w-full px-2.5 py-1.5 rounded-lg border border-slate-200 text-xs font-bold bg-white"
                placeholder="Material Title"
              />
              <div className="grid grid-cols-2 gap-2">
                <input
                  type="text"
                  value={m.target_class || ""}
                  onChange={(e) => {
                    const updated = [...materials];
                    updated[idx] = { ...m, target_class: e.target.value };
                    onChange((s: any) => ({ ...s, materials: updated }));
                  }}
                  className="px-2.5 py-1.5 rounded-lg border border-slate-200 text-[11px] bg-white"
                  placeholder="Class"
                />
                <input
                  type="text"
                  value={m.size || ""}
                  onChange={(e) => {
                    const updated = [...materials];
                    updated[idx] = { ...m, size: e.target.value };
                    onChange((s: any) => ({ ...s, materials: updated }));
                  }}
                  className="px-2.5 py-1.5 rounded-lg border border-slate-200 text-[11px] bg-white"
                  placeholder="Size (e.g. 2.4 MB PDF)"
                />
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

// Client fallback helper if backend is loading
function getDefaultsFallback(): Record<string, any> {
  return {
    home: {
      hero_badge: "Admissions Open 2026-27 • Hawa Bangla, Indore",
      hero_title_prefix: "Excel in Boards with",
      hero_title_highlight: "Expert Guidance",
      hero_description: "15 Years of trusted coaching for Class 4th to 12th & Degree Courses (MP Board, CBSE & ICSE). Small batches of 20 students, personalized attention, and proven 98.5% top results.",
      primary_cta_text: "Join Free Demo Class",
      stats: {
        years_experience: "15+ Yrs",
        total_students: "2,000+",
        highest_board_score: "98.5%",
        board_pass_rate: "98%",
        faculty_count: "7 Educators",
        batch_size_limit: "20 Students",
      },
      usp_points: [
        "Strict 20 Students per Batch",
        "Weekly Tests & Instant Doubt Clearing",
        "Expert Faculty (Up to 30 Yrs Experience)",
        "Student-Friendly Affordable Fees (From ₹800/mo)",
      ],
    },
    about: {
      title: "Empowering Students With Values, Safety & Excellence",
      director_name: "Mrs. Shobhna Vyas",
      director_designation: "Founder & Academic Director",
      director_experience: "20 Years Teaching Experience",
      director_quote: "As a parent myself, I know what you want: safety, learning, and happiness for your child. At Aarambh Institute, you will get all three. Let's grow together.",
      award_title: "Best Coaching Institute Award, Indore 2023",
      paragraphs: [
        "Aarambh Institute was founded in 2015 by Mrs. Shobhna Vyas with a clear vision: to establish an academic environment where no student is left behind in overcrowded classrooms.",
      ],
      core_values: [
        { title: "Child Safety First", desc: "Protected, CCTV-monitored and encouraging learning environment." },
        { title: "Effective Learning", desc: "Proven concept-building, model test series, and analytical speed drills." },
        { title: "Joyful Environment", desc: "Education with happiness and zero fear, building lifelong confidence." },
      ],
    },
    contact: {
      institute_name: "Aarambh Institute",
      tagline: "Step Toward Success • Est. 2015",
      full_address: "8 Shantinath Puri, Hawa Bangla, Near Sai Mandir, Indore, Madhya Pradesh — 452009",
      primary_phone: "88397-14081",
      secondary_phone: "79097-14081",
      whatsapp_number: "88397-14081",
      email: "aarambhinstitute09@gmail.com",
      working_hours: "10:00 AM to 8:00 PM (Monday to Saturday)",
      google_maps_url: "https://maps.app.goo.gl/T2m2g9b8tjVMCDqL9",
    },
  };
}
