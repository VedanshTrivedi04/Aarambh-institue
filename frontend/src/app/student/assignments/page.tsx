"use client";

import React, { useState } from "react";
import {
  FileText,
  Clock,
  CheckCircle2,
  AlertCircle,
  Download,
  UploadCloud,
  Send,
  X,
  Sparkles,
  Users,
  Check,
} from "lucide-react";

export default function StudentAssignmentsPage() {
  const [filter, setFilter] = useState<"ALL" | "PENDING" | "SUBMITTED" | "GRADED">("ALL");
  const [selectedTask, setSelectedTask] = useState<any | null>(null);
  const [submissionNotes, setSubmissionNotes] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [toastMessage, setToastMessage] = useState<string | null>(null);

  const [assignments, setAssignments] = useState([
    {
      id: "DPP-BIO-08",
      title: "DPP #08: Principles of Inheritance & Pedigree Chart Numericals",
      subject: "Biology",
      faculty: "Mr. Pankaj Dubey (30y Exp)",
      dueDate: "Today, 08:00 PM",
      totalMarks: 25,
      status: "PENDING",
      description: "Complete all 15 pedigree problem sets and monohybrid backcross ratio derivations in your class fair notebook.",
      grade: null,
      feedback: null,
    },
    {
      id: "HW-PHY-14",
      title: "HW #14: Ray Optics Sign Convention & Lens Maker Equation",
      subject: "Physics",
      faculty: "Mrs. Anita Holkar (15y Exp)",
      dueDate: "24 Sep 2026, 06:00 PM",
      totalMarks: 20,
      status: "PENDING",
      description: "Solve NCERT in-text numericals 9.1 to 9.8 with neat labeled ray diagrams.",
      grade: null,
      feedback: null,
    },
    {
      id: "DPP-BIO-07",
      title: "DPP #07: DNA Packaging & Meselson-Stahl Experiment",
      subject: "Biology",
      faculty: "Mr. Pankaj Dubey (30y Exp)",
      dueDate: "19 Sep 2026",
      totalMarks: 20,
      status: "GRADED",
      description: "Diagrammatic representation of nucleosome core octamer and heavy isotope centrifugation graph.",
      grade: "20 / 20 (Grade A+)",
      feedback: "Impeccable diagrams. Clear color coding of heavy 15N vs light 14N bands.",
    },
    {
      id: "HW-CHE-13",
      title: "HW #13: Coordination Compounds IUPAC Nomenclature",
      subject: "Chemistry",
      faculty: "Mr. Ansh Sir (10y Exp)",
      dueDate: "16 Sep 2026",
      totalMarks: 20,
      status: "GRADED",
      description: "Write IUPAC names and identify oxidation states for 20 coordination complexes.",
      grade: "19 / 20 (Grade A+)",
      feedback: "Great work. Be careful with bridging ligand prefix notations.",
    },
    {
      id: "DPP-PHY-13",
      title: "DPP #13: Total Internal Reflection & Prism Angle Derivations",
      subject: "Physics",
      faculty: "Mrs. Anita Holkar (15y Exp)",
      dueDate: "12 Sep 2026",
      totalMarks: 20,
      status: "GRADED",
      grade: "19 / 20 (Grade A+)",
      description: "Minimum deviation angle relation derivation and optical fiber critical angle calculations.",
      feedback: "Well formatted derivations.",
    },
  ]);

  const filteredTasks = assignments.filter((item) => {
    if (filter === "ALL") return true;
    return item.status === filter;
  });

  const handleDownloadSheet = (title: string) => {
    setToastMessage(`Downloaded question sheet: ${title}`);
    setTimeout(() => setToastMessage(null), 3000);
  };

  const handleConfirmSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedTask) return;
    setSubmitting(true);

    setTimeout(() => {
      setSubmitting(false);
      setAssignments((prev) =>
        prev.map((t) =>
          t.id === selectedTask.id
            ? { ...t, status: "SUBMITTED" }
            : t
        )
      );
      setToastMessage(`Successfully uploaded submission for ${selectedTask.id}`);
      setSelectedTask(null);
      setSubmissionNotes("");
      setTimeout(() => setToastMessage(null), 3500);
    }, 700);
  };

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      {/* Toast Alert */}
      {toastMessage && (
        <div className="fixed bottom-6 right-6 z-50 p-4 rounded-2xl bg-slate-900 text-white text-xs font-bold shadow-2xl flex items-center gap-2 animate-in fade-in">
          <CheckCircle2 className="w-4 h-4 text-emerald-400" />
          <span>{toastMessage}</span>
        </div>
      )}

      {/* Header */}
      <div className="bg-white rounded-3xl border border-slate-200/90 p-6 sm:p-8 shadow-sm">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <div className="flex items-center gap-2 mb-1">
              <span className="text-[10px] font-black uppercase tracking-wider px-2 py-0.5 rounded bg-red-50 text-[#c22329] border border-red-200">
                Daily Problem Solving Desk
              </span>
              <span className="text-[10px] font-bold text-slate-500">
                Class 12th Senior Biology
              </span>
            </div>
            <h1 className="text-2xl font-black text-slate-900 tracking-tight">
              Assignments & Daily Practice Problems (DPP)
            </h1>
            <p className="text-xs text-slate-500 mt-1 font-medium">
              Daily evaluated homework tracker • Faculty personalized remarks
            </p>
          </div>

          <div className="flex items-center gap-3">
            <div className="text-right">
              <span className="block text-[10px] font-bold text-slate-400 uppercase">
                DPP Completion Rate
              </span>
              <span className="text-2xl font-black text-slate-900">92.3%</span>
            </div>
            <div className="w-12 h-12 rounded-2xl bg-red-50 text-[#c22329] border border-red-200 flex items-center justify-center font-bold text-lg">
              <FileText className="w-6 h-6" />
            </div>
          </div>
        </div>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="bg-white rounded-3xl border border-slate-200/90 p-5 shadow-sm">
          <span className="text-xs font-bold text-slate-500 uppercase tracking-wider block">
            Total DPPs Assigned
          </span>
          <div className="text-2xl font-black text-slate-900 mt-1">26 Tasks</div>
          <p className="text-[11px] text-slate-500 mt-1">Session 2026-27 cycle</p>
        </div>

        <div className="bg-white rounded-3xl border border-slate-200/90 p-5 shadow-sm">
          <span className="text-xs font-bold text-red-700 uppercase tracking-wider block">
            Action Required
          </span>
          <div className="text-2xl font-black text-[#c22329] mt-1">2 Due</div>
          <p className="text-[11px] text-red-600 font-bold mt-1">DPP #08 due today 8:00 PM</p>
        </div>

        <div className="bg-white rounded-3xl border border-slate-200/90 p-5 shadow-sm">
          <span className="text-xs font-bold text-emerald-700 uppercase tracking-wider block">
            Graded Submissions
          </span>
          <div className="text-2xl font-black text-emerald-600 mt-1">24 Checked</div>
          <p className="text-[11px] text-emerald-600 font-bold mt-1">100% on-time submission</p>
        </div>

        <div className="bg-white rounded-3xl border border-slate-200/90 p-5 shadow-sm">
          <span className="text-xs font-bold text-amber-700 uppercase tracking-wider block">
            Average Grade
          </span>
          <div className="text-2xl font-black text-amber-700 mt-1">Grade A+</div>
          <p className="text-[11px] text-amber-600 font-bold mt-1">96.8% accuracy score</p>
        </div>
      </div>

      {/* Filter Tabs */}
      <div className="flex items-center gap-2">
        {(["ALL", "PENDING", "SUBMITTED", "GRADED"] as const).map((tab) => (
          <button
            key={tab}
            onClick={() => setFilter(tab)}
            className={`px-4 py-2 rounded-xl text-xs font-bold transition-all cursor-pointer ${
              filter === tab
                ? "bg-[#c22329] text-white shadow-sm"
                : "bg-white text-slate-600 hover:bg-slate-50 border border-slate-200"
            }`}
          >
            {tab === "ALL" && "All Homework"}
            {tab === "PENDING" && "Pending (2)"}
            {tab === "SUBMITTED" && "Submitted"}
            {tab === "GRADED" && "Graded (24)"}
          </button>
        ))}
      </div>

      {/* Tasks List */}
      <div className="space-y-4">
        {filteredTasks.map((task) => (
          <div
            key={task.id}
            className="bg-white rounded-3xl border border-slate-200/90 p-6 shadow-sm hover:shadow-md transition-shadow space-y-4"
          >
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
              <div className="space-y-1">
                <div className="flex items-center gap-2">
                  <span className="text-[10px] font-mono font-bold px-2 py-0.5 rounded bg-slate-100 text-slate-700 border border-slate-200">
                    {task.id}
                  </span>
                  <span
                    className={`text-[10px] font-black uppercase px-2 py-0.5 rounded ${
                      task.subject === "Biology"
                        ? "bg-emerald-100 text-emerald-800"
                        : task.subject === "Physics"
                        ? "bg-blue-100 text-blue-800"
                        : "bg-red-100 text-red-800"
                    }`}
                  >
                    {task.subject}
                  </span>
                </div>
                <h3 className="text-base font-black text-slate-900">{task.title}</h3>
                <p className="text-xs text-slate-500 font-medium flex items-center gap-2">
                  <Users className="w-3.5 h-3.5 text-slate-400" />
                  <span>Assigned by: <strong>{task.faculty}</strong></span>
                </p>
              </div>

              {/* Status Badge */}
              <div className="flex items-center gap-3">
                {task.status === "PENDING" ? (
                  <span className="px-3 py-1 rounded-full bg-red-50 text-[#c22329] border border-red-200 text-xs font-black flex items-center gap-1.5 animate-pulse">
                    <Clock className="w-3.5 h-3.5" />
                    <span>Due: {task.dueDate}</span>
                  </span>
                ) : task.status === "SUBMITTED" ? (
                  <span className="px-3 py-1 rounded-full bg-blue-50 text-blue-700 border border-blue-200 text-xs font-black flex items-center gap-1.5">
                    <CheckCircle2 className="w-3.5 h-3.5" />
                    <span>Under Teacher Review</span>
                  </span>
                ) : (
                  <span className="px-3 py-1 rounded-full bg-emerald-50 text-emerald-700 border border-emerald-200 text-xs font-black flex items-center gap-1.5">
                    <Sparkles className="w-3.5 h-3.5 text-emerald-500" />
                    <span>Score: {task.grade}</span>
                  </span>
                )}
              </div>
            </div>

            <p className="text-xs text-slate-600 bg-slate-50/80 p-3.5 rounded-2xl border border-slate-200 leading-relaxed font-normal">
              {task.description}
            </p>

            {/* Faculty Feedback if Graded */}
            {task.feedback && (
              <div className="p-3.5 rounded-2xl bg-emerald-50/60 border border-emerald-200/80 text-xs space-y-1">
                <span className="font-bold text-emerald-900 flex items-center gap-1">
                  <Sparkles className="w-3 h-3 text-emerald-600" />
                  Faculty Evaluation Notes:
                </span>
                <p className="text-slate-700 italic font-medium">&ldquo;{task.feedback}&rdquo;</p>
              </div>
            )}

            {/* Actions */}
            <div className="flex flex-wrap items-center justify-between gap-3 pt-2 border-t border-slate-100">
              <button
                onClick={() => handleDownloadSheet(task.title)}
                className="inline-flex items-center gap-1.5 text-xs font-bold text-slate-700 hover:text-slate-950 px-3 py-1.5 rounded-xl border border-slate-200 bg-white hover:bg-slate-50 transition-colors cursor-pointer shadow-xs"
              >
                <Download className="w-3.5 h-3.5 text-slate-500" />
                <span>Download DPP Question Paper</span>
              </button>

              {task.status === "PENDING" && (
                <button
                  onClick={() => setSelectedTask(task)}
                  className="inline-flex items-center gap-1.5 text-xs font-bold text-white bg-[#c22329] hover:bg-red-700 px-4 py-2 rounded-xl transition-all shadow-md cursor-pointer hover:scale-105"
                >
                  <UploadCloud className="w-3.5 h-3.5" />
                  <span>Upload & Submit Assignment</span>
                </button>
              )}
            </div>
          </div>
        ))}
      </div>

      {/* Submit Assignment Modal */}
      {selectedTask && (
        <div className="fixed inset-0 z-50 bg-slate-900/60 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-white rounded-3xl border border-slate-300 max-w-lg w-full p-6 sm:p-7 shadow-2xl space-y-5 relative">
            <button
              onClick={() => setSelectedTask(null)}
              className="absolute top-6 right-6 p-2 rounded-xl bg-slate-100 hover:bg-slate-200 text-slate-500 hover:text-slate-800 transition-colors"
            >
              <X className="w-5 h-5" />
            </button>

            <div>
              <span className="text-[10px] font-black uppercase text-[#c22329] bg-red-50 border border-red-200 px-2 py-0.5 rounded">
                Upload Submission
              </span>
              <h3 className="text-lg font-black text-slate-900 mt-2">{selectedTask.title}</h3>
              <p className="text-xs text-slate-500 mt-0.5">
                Evaluator: {selectedTask.faculty}
              </p>
            </div>

            <form onSubmit={handleConfirmSubmit} className="space-y-4 text-xs">
              <div className="border-2 border-dashed border-slate-300 rounded-2xl p-6 text-center space-y-2 hover:border-[#c22329] transition-colors cursor-pointer bg-slate-50/50">
                <UploadCloud className="w-8 h-8 text-slate-400 mx-auto" />
                <div>
                  <span className="font-bold text-slate-800 block">Click to upload notebook images or PDF</span>
                  <span className="text-[10px] text-slate-400">PDF, JPG, PNG up to 25MB</span>
                </div>
              </div>

              <div className="space-y-1">
                <label className="font-bold text-slate-700">Student Clarification / Notes</label>
                <textarea
                  rows={3}
                  value={submissionNotes}
                  onChange={(e) => setSubmissionNotes(e.target.value)}
                  placeholder="e.g. Completed questions 1 to 15. Had doubt on question 12 pedigree chart."
                  className="w-full bg-slate-50 border border-slate-200 rounded-xl p-3 text-slate-900 font-medium focus:bg-white focus:outline-none focus:border-[#c22329]"
                />
              </div>

              <button
                type="submit"
                disabled={submitting}
                className="w-full py-3 rounded-xl font-bold bg-[#c22329] hover:bg-red-700 text-white shadow-md transition-all flex items-center justify-center gap-2 cursor-pointer disabled:opacity-50"
              >
                <Send className="w-3.5 h-3.5" />
                <span>{submitting ? "Uploading Submission..." : "Confirm & Submit to Faculty"}</span>
              </button>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
