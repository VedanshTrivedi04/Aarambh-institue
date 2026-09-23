"use client";

import React, { useEffect, useState } from "react";
import {
  FileText,
  Video,
  Bell,
  Calendar,
  Compass,
  CreditCard,
  Download,
  ExternalLink,
  CheckCircle2,
  Sparkles,
  ArrowRight,
  BookOpen,
  Award,
  Play,
  QrCode,
  AlertCircle,
  HelpCircle
} from "lucide-react";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";

interface MaterialItem {
  title: string;
  target_class: string;
  pages: string;
  size: string;
  downloads: string;
  author: string;
  badge: string;
  badge_color: string;
}

interface NoticeItem {
  date: string;
  title: string;
  desc: string;
  priority: string;
  color: string;
}

interface HolidayItem {
  holiday: string;
  date: string;
  status: string;
}

const FALLBACK_MATERIALS: MaterialItem[] = [
  {
    title: "Class 10th Maths All Formulas Booklet",
    target_class: "Class 10th (MP Board / CBSE)",
    pages: "18 Pages",
    size: "2.4 MB PDF",
    downloads: "1,240+ Downloads",
    author: "Mrs. Shobhna Vyas & Mr. Vishal Rathore",
    badge: "Most Popular",
    badge_color: "bg-red-50 text-[#c22329] border-red-200",
  },
  {
    title: "Class 12th Physics Quick Revision & Derivations",
    target_class: "Class 12th Science",
    pages: "26 Pages",
    size: "3.8 MB PDF",
    downloads: "980+ Downloads",
    author: "Mrs. Anita Holkar",
    badge: "Board Essential",
    badge_color: "bg-blue-50 text-blue-700 border-blue-200",
  },
  {
    title: "Class 12th Biology Diagram Compendium & Labels",
    target_class: "Class 12th & PMT/NEET",
    pages: "32 Pages",
    size: "5.1 MB PDF",
    downloads: "1,450+ Downloads",
    author: "Mr. Pankaj Dubey (30 Yrs Exp)",
    badge: "NEET Ready",
    badge_color: "bg-emerald-50 text-emerald-700 border-emerald-200",
  },
];

const FALLBACK_NOTICES: NoticeItem[] = [
  {
    date: "24 March 2026",
    title: "Weekly Board Mock Test Series (Sunday Batch)",
    desc: "Mandatory for Class 10th and 12th students. Timings: 11:00 AM to 1:00 PM. Answer sheet evaluation will be handed over to parents on Wednesday.",
    priority: "High Priority",
    color: "bg-red-50 text-[#c22329] border-red-200",
  },
  {
    date: "20 March 2026",
    title: "New Academic Session (2026-27) Admissions Open",
    desc: "Classes 4th to 12th & Degree programs. Limited 20 seats per batch. Avail early bird fee benefits at Hawa Bangla campus.",
    priority: "Admission Alert",
    color: "bg-blue-50 text-blue-700 border-blue-200",
  },
  {
    date: "15 March 2026",
    title: "Doubt Clearing Clinic with HODs",
    desc: "Special extra classes every evening from 6:00 PM to 7:00 PM for physics numericals and organic chemistry reactions.",
    priority: "Academic",
    color: "bg-amber-50 text-amber-800 border-amber-200",
  },
];

const FALLBACK_HOLIDAYS: HolidayItem[] = [
  { holiday: "Mahavir Jayanti", date: "April 2026", status: "Holiday" },
  { holiday: "Good Friday / Ambedkar Jayanti", date: "April 2026", status: "Holiday" },
  { holiday: "Summer Break (Junior Batches Only)", date: "May 15 - May 25, 2026", status: "Special Timings" },
  { holiday: "Independence Day & Raksha Bandhan", date: "August 2026", status: "Celebration" },
  { holiday: "Ganesh Chaturthi / Anant Chaturdashi", date: "September 2026", status: "Holiday" },
  { holiday: "Dussehra & Diwali Break", date: "October / November 2026", status: "Festival Break" },
];

export default function StudentResources() {
  const [activeTab, setActiveTab] = useState<"portal" | "materials" | "notices" | "guidance" | "fee">("portal");
  const [quizScore, setQuizScore] = useState<number | null>(null);
  const [currentQuestion, setCurrentQuestion] = useState(0);
  const [selectedAnswer, setSelectedAnswer] = useState<number | null>(null);

  const [materials, setMaterials] = useState<MaterialItem[]>(FALLBACK_MATERIALS);
  const [notices, setNotices] = useState<NoticeItem[]>(FALLBACK_NOTICES);
  const [holidays, setHolidays] = useState<HolidayItem[]>(FALLBACK_HOLIDAYS);

  useEffect(() => {
    fetch(`${API_BASE_URL}/api/v1/admin/cms/content/student_corner`, { cache: "no-store" })
      .then((res) => (res.ok ? res.json() : null))
      .then((json) => {
        const data = json?.data;
        if (data?.materials?.length) setMaterials(data.materials);
        if (data?.notices?.length) setNotices(data.notices);
        if (data?.holidays?.length) setHolidays(data.holidays);
      })
      .catch(() => {});
  }, []);

  // Sample Quiz for Scholarship / Aptitude
  const quizQuestions = [
    {
      q: "If 5x - 7 = 3x + 9, what is the value of x?",
      options: ["x = 4", "x = 8", "x = 16", "x = 2"],
      answer: 1, // 8
    },
    {
      q: "Which organelle is famously known as the 'Powerhouse of the Cell'?",
      options: ["Ribosome", "Mitochondria", "Nucleus", "Endoplasmic Reticulum"],
      answer: 1,
    },
    {
      q: "In accounting, what is the Golden Rule for 'Real Accounts'?",
      options: [
        "Debit what comes in, Credit what goes out",
        "Debit all expenses, Credit all incomes",
        "Debit the receiver, Credit the giver",
        "Debit assets, Credit liabilities only",
      ],
      answer: 0,
    },
  ];

  const handleQuizAnswer = (idx: number) => {
    setSelectedAnswer(idx);
    if (idx === quizQuestions[currentQuestion].answer) {
      setQuizScore((prev) => (prev !== null ? prev + 1 : 1));
    } else if (quizScore === null) {
      setQuizScore(0);
    }
  };

  const nextQuestion = () => {
    if (currentQuestion < quizQuestions.length - 1) {
      setCurrentQuestion((prev) => prev + 1);
      setSelectedAnswer(null);
    }
  };

  const restartQuiz = () => {
    setCurrentQuestion(0);
    setSelectedAnswer(null);
    setQuizScore(null);
  };

  return (
    <section id="student-corner" className="relative py-24 bg-white text-slate-900 border-b border-slate-200/80">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Section Header */}
        <div className="text-center max-w-3xl mx-auto space-y-4">
          <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-blue-50 border border-blue-200 text-blue-700 text-xs font-bold uppercase tracking-wider">
            <Sparkles className="w-3.5 h-3.5" />
            <span>Student & Parent Resource Hub</span>
          </div>

          <h2 className="text-3xl sm:text-5xl font-black tracking-tight text-slate-900">
            Aarambh Institute <br />
            <span className="text-[#c22329]">Digital Learning & Student Services</span>
          </h2>

          <p className="text-sm sm:text-base text-slate-600">
            Everything in one place: Online Tests, Free Downloadable Notes, Notice Board, Career Counseling, and Online Fee Payments.
          </p>
        </div>

        {/* Tab Selection Navigation */}
        <div className="flex flex-wrap items-center justify-center gap-2 mt-10 mb-12">
          {[
            { id: "portal", label: "Online Test & Quiz", icon: FileText },
            { id: "materials", label: "Free Study Material", icon: Download },
            { id: "notices", label: "Notice Board & Calendar", icon: Bell },
            { id: "guidance", label: "Career & Stream Guidance", icon: Compass },
            { id: "fee", label: "Fee Payment Portal", icon: CreditCard },
          ].map((tab) => {
            const Icon = tab.icon;
            const isActive = activeTab === tab.id;
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id as any)}
                className={`flex items-center gap-2 px-4 py-2.5 rounded-xl text-xs sm:text-sm font-bold transition-all ${
                  isActive
                    ? "bg-[#c22329] text-white shadow-md shadow-red-500/20 scale-105"
                    : "bg-slate-100 text-slate-700 hover:text-slate-950 hover:bg-slate-200 border border-slate-200"
                }`}
              >
                <Icon className="w-4 h-4" />
                <span>{tab.label}</span>
              </button>
            );
          })}
        </div>

        {/* Tab 1: Online Test Portal & Scholarship Quiz */}
        {activeTab === "portal" && (
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
            <div className="lg:col-span-7 bg-[#f8fafd] p-7 sm:p-8 rounded-3xl border border-slate-200 shadow-sm space-y-6">
              <div className="flex items-center justify-between">
                <div>
                  <span className="text-xs font-bold text-amber-700 uppercase tracking-wider">
                    Interactive Mini Assessment
                  </span>
                  <h3 className="text-xl sm:text-2xl font-black text-slate-900 mt-1">
                    Take the 3-Minute Aarambh Aptitude Quiz
                  </h3>
                </div>
                <span className="px-3 py-1 rounded-full bg-blue-100 text-blue-800 text-xs font-bold">
                  Question {currentQuestion + 1} of {quizQuestions.length}
                </span>
              </div>

              <div className="p-5 rounded-2xl bg-white border border-slate-200 shadow-sm space-y-4">
                <p className="text-base font-bold text-slate-900">
                  {quizQuestions[currentQuestion].q}
                </p>

                <div className="space-y-2">
                  {quizQuestions[currentQuestion].options.map((opt, idx) => {
                    const isSelected = selectedAnswer === idx;
                    const isCorrect = idx === quizQuestions[currentQuestion].answer;
                    return (
                      <button
                        key={idx}
                        onClick={() => handleQuizAnswer(idx)}
                        disabled={selectedAnswer !== null}
                        className={`w-full text-left p-3.5 rounded-xl text-xs sm:text-sm font-semibold border transition-all flex items-center justify-between ${
                          selectedAnswer === null
                            ? "bg-slate-50 border-slate-200 hover:bg-slate-100 text-slate-800"
                            : isSelected
                            ? isCorrect
                              ? "bg-emerald-50 border-emerald-400 text-emerald-800"
                              : "bg-red-50 border-red-400 text-red-800"
                            : isCorrect
                            ? "bg-emerald-50 border-emerald-400 text-emerald-800"
                            : "bg-slate-50 border-slate-200 text-slate-400"
                        }`}
                      >
                        <span>{opt}</span>
                        {selectedAnswer !== null && isCorrect && (
                          <CheckCircle2 className="w-4 h-4 text-emerald-600" />
                        )}
                      </button>
                    );
                  })}
                </div>

                {selectedAnswer !== null && (
                  <div className="pt-2 flex items-center justify-between">
                    <span className="text-xs font-bold text-slate-600">
                      {selectedAnswer === quizQuestions[currentQuestion].answer ? (
                        <span className="text-emerald-700">✓ Correct answer! Great work.</span>
                      ) : (
                        <span className="text-red-700">✗ Incorrect. Review the fundamental concept!</span>
                      )}
                    </span>
                    {currentQuestion < quizQuestions.length - 1 ? (
                      <button
                        onClick={nextQuestion}
                        className="px-4 py-2 rounded-xl bg-blue-600 text-white text-xs font-bold hover:bg-blue-700 transition-colors flex items-center gap-1.5"
                      >
                        <span>Next Question</span>
                        <ArrowRight className="w-3.5 h-3.5" />
                      </button>
                    ) : (
                      <button
                        onClick={restartQuiz}
                        className="px-4 py-2 rounded-xl bg-slate-800 text-white text-xs font-bold hover:bg-slate-900 transition-colors"
                      >
                        Restart Quiz
                      </button>
                    )}
                  </div>
                )}
              </div>

              <div className="p-4 rounded-2xl bg-amber-50 border border-amber-200 flex items-start gap-3 text-xs text-amber-900">
                <Award className="w-5 h-5 text-amber-600 flex-shrink-0 mt-0.5" />
                <div>
                  <span className="font-bold">A-SAT Scholarship Benefit:</span> Score 80%+ on our full Aarambh Scholarship & Aptitude Test to claim up to a 50% waiver on tuition fees.
                </div>
              </div>
            </div>

            <div className="lg:col-span-5 bg-white p-7 sm:p-8 rounded-3xl border border-slate-200 shadow-md space-y-5">
              <span className="text-xs font-bold text-red-700 uppercase tracking-wider">
                Student Online Examination Portal
              </span>
              <h3 className="text-xl font-bold text-slate-900">
                Full CBT Mock Test Portal
              </h3>
              <p className="text-xs text-slate-600 leading-relaxed font-normal">
                Enrolled students get access to weekly Chapter Mock Tests, MP Board / CBSE pattern question papers, and instant analytics with step-by-step solutions.
              </p>

              <div className="space-y-3 pt-2">
                <div className="p-3.5 rounded-2xl bg-slate-50 border border-slate-200 flex items-center justify-between text-xs">
                  <div className="flex items-center gap-2.5">
                    <div className="w-8 h-8 rounded-xl bg-blue-100 text-blue-700 flex items-center justify-center font-bold">
                      10
                    </div>
                    <div>
                      <p className="font-bold text-slate-900">Class 10th Board Mock Test #4</p>
                      <p className="text-[11px] text-slate-500">Science & Mathematics • 80 Marks</p>
                    </div>
                  </div>
                  <span className="px-2.5 py-1 rounded bg-emerald-100 text-emerald-800 font-bold text-[10px]">
                    LIVE NOW
                  </span>
                </div>

                <div className="p-3.5 rounded-2xl bg-slate-50 border border-slate-200 flex items-center justify-between text-xs">
                  <div className="flex items-center gap-2.5">
                    <div className="w-8 h-8 rounded-xl bg-purple-100 text-purple-700 flex items-center justify-center font-bold">
                      12
                    </div>
                    <div>
                      <p className="font-bold text-slate-900">Class 12th Physics & Accountancy</p>
                      <p className="text-[11px] text-slate-500">Board Speed Drill • 70 Marks</p>
                    </div>
                  </div>
                  <span className="px-2.5 py-1 rounded bg-blue-100 text-blue-800 font-bold text-[10px]">
                    SUNDAY 11 AM
                  </span>
                </div>
              </div>

              <div className="pt-2">
                <a
                  href="/login?role=student"
                  className="btn-caramel-gold w-full py-3.5 rounded-xl text-center text-xs font-extrabold flex items-center justify-center gap-2 shadow-md"
                >
                  <span>Student Portal Login & Test Dashboard</span>
                  <ExternalLink className="w-4 h-4" />
                </a>
              </div>
            </div>
          </div>
        )}

        {/* Tab 2: Free Study Material Download */}
        {activeTab === "materials" && (
          <div className="space-y-6">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
              <div>
                <h3 className="text-xl sm:text-2xl font-black text-slate-900">
                  Free Downloadable Handouts, Formula Sheets & Model Papers
                </h3>
                <p className="text-xs sm:text-sm text-slate-600 mt-1">
                  Prepared by Aarambh senior faculty with 15-30 years of classroom experience.
                </p>
              </div>
              <span className="text-xs font-bold px-3 py-1.5 rounded-full bg-emerald-50 text-emerald-700 border border-emerald-200 self-start sm:self-auto">
                100% Free Downloads • PDF Format
              </span>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {materials.map((item, idx) => (
                <div
                  key={idx}
                  className="light-card-interactive p-6 rounded-3xl flex flex-col justify-between"
                >
                  <div>
                    <div className="flex items-center justify-between mb-3">
                      <span className={`text-[10px] font-black uppercase px-2.5 py-0.5 rounded border ${item.badge_color}`}>
                        {item.badge}
                      </span>
                      <span className="text-[11px] text-slate-500 font-semibold">{item.size}</span>
                    </div>

                    <h4 className="font-bold text-base text-slate-900 group-hover:text-[#c22329] transition-colors leading-snug">
                      {item.title}
                    </h4>

                    <p className="text-xs text-slate-600 mt-1 font-medium">
                      Target: <strong className="text-slate-900">{item.target_class}</strong>
                    </p>

                    <div className="mt-3 p-3 rounded-xl bg-slate-50 border border-slate-100 text-[11px] text-slate-600 space-y-1">
                      <div>Faculty: <span className="font-semibold text-slate-900">{item.author}</span></div>
                      <div className="flex items-center justify-between text-slate-500">
                        <span>{item.pages}</span>
                        <span>{item.downloads}</span>
                      </div>
                    </div>
                  </div>

                  <div className="pt-4 mt-4 border-t border-slate-100">
                    <button
                      onClick={() => alert(`Starting download for: ${item.title}`)}
                      className="w-full py-2.5 rounded-xl bg-slate-100 hover:bg-[#c22329] hover:text-white text-slate-800 text-xs font-bold transition-all flex items-center justify-center gap-2 border border-slate-200"
                    >
                      <Download className="w-3.5 h-3.5" />
                      <span>Download Free PDF</span>
                    </button>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Tab 3: Notice Board & Holiday Calendar */}
        {activeTab === "notices" && (
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
            {/* Live Notice Board */}
            <div className="lg:col-span-6 bg-white p-7 sm:p-8 rounded-3xl border border-slate-200 shadow-md space-y-5">
              <div className="flex items-center justify-between border-b border-slate-100 pb-3">
                <div className="flex items-center gap-2.5">
                  <div className="w-9 h-9 rounded-xl bg-red-100 text-[#c22329] flex items-center justify-center font-bold">
                    <Bell className="w-4 h-4" />
                  </div>
                  <div>
                    <h3 className="font-black text-lg text-slate-900">
                      Institute Notice Board
                    </h3>
                    <p className="text-[11px] text-slate-500">Campus & Academic Announcements</p>
                  </div>
                </div>
                <span className="flex items-center gap-1.5 text-xs text-emerald-700 font-bold">
                  <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
                  Active Notices
                </span>
              </div>

              <div className="space-y-3.5">
                {notices.map((notice, idx) => (
                  <div key={idx} className="p-4 rounded-2xl bg-slate-50 border border-slate-200/90 space-y-1.5">
                    <div className="flex items-center justify-between">
                      <span className="text-[10px] font-bold text-slate-500">{notice.date}</span>
                      <span className={`text-[10px] font-black uppercase px-2 py-0.5 rounded border ${notice.color}`}>
                        {notice.priority}
                      </span>
                    </div>
                    <h4 className="text-sm font-bold text-slate-900">{notice.title}</h4>
                    <p className="text-xs text-slate-600 leading-relaxed font-normal">{notice.desc}</p>
                  </div>
                ))}
              </div>
            </div>

            {/* Holiday Calendar 2026 */}
            <div className="lg:col-span-6 bg-white p-7 sm:p-8 rounded-3xl border border-slate-200 shadow-md space-y-5">
              <div className="flex items-center justify-between border-b border-slate-100 pb-3">
                <div className="flex items-center gap-2.5">
                  <div className="w-9 h-9 rounded-xl bg-blue-100 text-blue-700 flex items-center justify-center font-bold">
                    <Calendar className="w-4 h-4" />
                  </div>
                  <div>
                    <h3 className="font-black text-lg text-slate-900">
                      Academic Holiday Calendar (2026)
                    </h3>
                    <p className="text-[11px] text-slate-500">Official Scheduled Aarambh Institute Breaks</p>
                  </div>
                </div>
                <span className="text-xs font-bold text-slate-600">Session 2026</span>
              </div>

              <div className="space-y-2.5">
                {holidays.map((item, idx) => (
                  <div
                    key={idx}
                    className="flex items-center justify-between p-3 rounded-xl bg-slate-50 border border-slate-100 text-xs"
                  >
                    <div className="flex items-center gap-2 font-semibold text-slate-900">
                      <span className="w-1.5 h-1.5 rounded-full bg-blue-600"></span>
                      <span>{item.holiday}</span>
                    </div>
                    <div className="flex items-center gap-3">
                      <span className="text-slate-500 font-medium">{item.date}</span>
                      <span className="px-2 py-0.5 rounded bg-slate-200 text-slate-700 font-bold text-[10px]">
                        {item.status}
                      </span>
                    </div>
                  </div>
                ))}
              </div>

              <div className="p-3.5 rounded-xl bg-blue-50 border border-blue-200 text-[11px] text-blue-800 flex items-center gap-2">
                <AlertCircle className="w-4 h-4 flex-shrink-0 text-blue-600" />
                <span>During examination months, special Sunday booster revision classes run without interruption.</span>
              </div>
            </div>
          </div>
        )}

        {/* Tab 4: Stream and Career Guidance After Class 10th & 12th */}
        {activeTab === "guidance" && (
          <div className="space-y-8">
            <div className="text-center max-w-2xl mx-auto space-y-2">
              <h3 className="text-2xl sm:text-3xl font-black text-slate-900">
                Confused Which Stream or Career to Pick?
              </h3>
              <p className="text-xs sm:text-sm text-slate-600">
                Get clarity after Class 10th & 12th with expert academic roadmap counseling by Founder Shobhna Vyas and our Senior HODs.
              </p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              {/* PCM */}
              <div className="light-card-interactive p-6 rounded-3xl space-y-4">
                <div className="w-10 h-10 rounded-2xl bg-blue-100 text-blue-800 flex items-center justify-center font-black">
                  PCM
                </div>
                <div>
                  <h4 className="font-extrabold text-lg text-slate-900">Science (PCM)</h4>
                  <p className="text-xs text-slate-500 font-medium">Physics, Chemistry, Mathematics</p>
                </div>
                <div className="space-y-1.5 text-xs text-slate-700">
                  <div className="font-bold text-slate-900">Career Horizons:</div>
                  <ul className="list-disc pl-4 space-y-1 text-slate-600">
                    <li>Engineering (IIT JEE, B.Tech, Computer Science, AI)</li>
                    <li>Defence (NDA, Air Force Technical, Navy)</li>
                    <li>Architecture (B.Arch, NATA) & Data Science</li>
                    <li>Research, ISRO & Pure Mathematics</li>
                  </ul>
                </div>
                <div className="pt-2 border-t border-slate-100 text-[11px] text-blue-700 font-bold">
                  Mentored by: Mr. Vishal Rathore & Mrs. Anita Holkar
                </div>
              </div>

              {/* PCB */}
              <div className="light-card-interactive p-6 rounded-3xl space-y-4">
                <div className="w-10 h-10 rounded-2xl bg-emerald-100 text-emerald-800 flex items-center justify-center font-black">
                  PCB
                </div>
                <div>
                  <h4 className="font-extrabold text-lg text-slate-900">Science (PCB)</h4>
                  <p className="text-xs text-slate-500 font-medium">Physics, Chemistry, Biology</p>
                </div>
                <div className="space-y-1.5 text-xs text-slate-700">
                  <div className="font-bold text-slate-900">Career Horizons:</div>
                  <ul className="list-disc pl-4 space-y-1 text-slate-600">
                    <li>Medical (MBBS, BDS, BAMS, BHMS through NEET)</li>
                    <li>Pharmacy (B.Pharm, Clinical Research)</li>
                    <li>Biotechnology, Microbiology & Genetics</li>
                    <li>Nursing, Physiotherapy & Forensic Sciences</li>
                  </ul>
                </div>
                <div className="pt-2 border-t border-slate-100 text-[11px] text-emerald-700 font-bold">
                  Mentored by: Mr. Pankaj Dubey (30 Yrs Exp)
                </div>
              </div>

              {/* Commerce */}
              <div className="light-card-interactive p-6 rounded-3xl space-y-4">
                <div className="w-10 h-10 rounded-2xl bg-amber-100 text-amber-900 flex items-center justify-center font-black">
                  COMM
                </div>
                <div>
                  <h4 className="font-extrabold text-lg text-slate-900">Commerce Stream</h4>
                  <p className="text-xs text-slate-500 font-medium">Accounts, Business Studies, Economics</p>
                </div>
                <div className="space-y-1.5 text-xs text-slate-700">
                  <div className="font-bold text-slate-900">Career Horizons:</div>
                  <ul className="list-disc pl-4 space-y-1 text-slate-600">
                    <li>Chartered Accountancy (CA), Company Secretary (CS)</li>
                    <li>B.Com, M.Com, BBA, MBA & Financial Modeling</li>
                    <li>Investment Banking, Stock Market & Taxation</li>
                    <li>Government Banking PO & Civil Services (UPSC)</li>
                  </ul>
                </div>
                <div className="pt-2 border-t border-slate-100 text-[11px] text-amber-800 font-bold">
                  Mentored by: Mr. Jitendra Shindey (30 Yrs Exp)
                </div>
              </div>
            </div>

            {/* Book Free 1:1 Counseling Banner */}
            <div className="p-7 sm:p-8 rounded-3xl bg-gradient-to-r from-slate-900 to-blue-950 text-white flex flex-col md:flex-row items-center justify-between gap-6 shadow-xl">
              <div className="space-y-2 text-center md:text-left">
                <span className="text-amber-400 text-xs font-black uppercase tracking-wider">
                  Complimentary Parent-Student Counseling
                </span>
                <h4 className="text-xl sm:text-2xl font-black">
                  Book A Free 1-on-1 Career Session at Hawa Bangla Campus
                </h4>
                <p className="text-xs sm:text-sm text-slate-300 max-w-xl">
                  Sit down with Mrs. Shobhna Vyas to review the student&apos;s past marksheets, strengths, and create an actionable 2-year study roadmap.
                </p>
              </div>

              <a
                href="https://wa.me/918839714081?text=Hello%20Aarambh%20Institute%2C%20I%20want%20to%20book%20a%20free%201%3A1%20career%20counseling%20session."
                target="_blank"
                rel="noopener noreferrer"
                className="btn-caramel-gold px-6 py-3.5 rounded-xl text-xs sm:text-sm font-extrabold flex items-center gap-2 whitespace-nowrap shadow-lg flex-shrink-0"
              >
                <span>Book Free Career Counseling</span>
                <ArrowRight className="w-4 h-4" />
              </a>
            </div>
          </div>
        )}

        {/* Tab 5: Fee Payment Portal & Details */}
        {activeTab === "fee" && (
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
            <div className="lg:col-span-7 bg-[#f8fafd] p-7 sm:p-8 rounded-3xl border border-slate-200 shadow-sm space-y-5">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-2xl bg-emerald-100 text-emerald-800 flex items-center justify-center font-bold">
                  <CreditCard className="w-5 h-5" />
                </div>
                <div>
                  <h3 className="text-xl font-bold text-slate-900">
                    Online Fee Payment Options
                  </h3>
                  <p className="text-xs text-slate-500">Transparent & Affordable Education Policy</p>
                </div>
              </div>

              <p className="text-xs text-slate-600 leading-relaxed font-normal">
                Aarambh Institute offers student-friendly monthly and quarterly installment options. Parents can pay via UPI (Google Pay, PhonePe, Paytm), Net Banking, or visit the campus fee counter.
              </p>

              <div className="p-5 rounded-2xl bg-white border border-slate-200 space-y-3 text-xs">
                <div className="font-bold text-slate-900 flex items-center justify-between pb-2 border-b border-slate-100">
                  <span>Official UPI Payment ID</span>
                  <span className="text-emerald-700 font-mono text-sm font-black">aarambhinstitute@upi</span>
                </div>
                <div className="flex items-center justify-between text-slate-600">
                  <span>Beneficiary Name:</span>
                  <span className="font-semibold text-slate-900">Aarambh Institute / Shobhna Vyas</span>
                </div>
                <div className="flex items-center justify-between text-slate-600">
                  <span>Helpline for Payment Confirmation:</span>
                  <span className="font-bold text-slate-900">88397-14081 / 79097-14081</span>
                </div>
                <div className="flex items-center justify-between text-slate-600">
                  <span>Campus Receipt Window:</span>
                  <span className="text-slate-900">10:00 AM to 8:00 PM (Monday to Saturday)</span>
                </div>
              </div>

              <div className="p-4 rounded-2xl bg-slate-100 border border-slate-200 text-xs text-slate-700 flex items-start gap-2.5">
                <CheckCircle2 className="w-4 h-4 text-emerald-600 flex-shrink-0 mt-0.5" />
                <span>Every transaction generates an official printed Aarambh Institute fee receipt with student roll number, batch timing, and GST/PAN credentials.</span>
              </div>
            </div>

            <div className="lg:col-span-5 bg-white p-7 sm:p-8 rounded-3xl border border-slate-200 shadow-md text-center space-y-4">
              <div className="w-12 h-12 rounded-2xl bg-blue-100 text-blue-700 flex items-center justify-center mx-auto">
                <QrCode className="w-6 h-6" />
              </div>
              <h4 className="font-bold text-base text-slate-900">
                Instant UPI QR Code Scan
              </h4>
              <p className="text-xs text-slate-500 font-medium">
                Scan using Google Pay, PhonePe, Paytm, or BHIM UPI to pay admission or tuition fees.
              </p>

              {/* QR Mockup */}
              <div className="w-48 h-48 mx-auto p-4 rounded-2xl bg-slate-50 border-2 border-dashed border-slate-300 flex flex-col items-center justify-center space-y-2">
                <div className="w-32 h-32 bg-slate-900 rounded-xl p-2 flex items-center justify-center text-white text-[10px] font-mono text-center">
                  [ UPI QR CODE ]
                  <br />
                  AARAMBH INST
                  <br />
                  88397-14081
                </div>
                <span className="text-[10px] text-slate-500 font-bold">Verified Merchant</span>
              </div>

              <a
                href="https://wa.me/918839714081?text=Hello%2C%20I%20have%20transferred%20the%20admission%20fee.%20Attaching%20screenshot%20for%20receipt."
                target="_blank"
                rel="noopener noreferrer"
                className="w-full py-3 rounded-xl bg-emerald-600 hover:bg-emerald-700 text-white text-xs font-bold transition-all flex items-center justify-center gap-2 shadow-md"
              >
                <span>Send Payment Screenshot on WhatsApp</span>
              </a>
            </div>
          </div>
        )}
      </div>
    </section>
  );
}
