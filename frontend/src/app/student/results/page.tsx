"use client";

import React, { useEffect, useState } from "react";
import {
  Award,
  Sparkles,
  Printer,
  X,
  FileText,
  Loader2,
  AlertTriangle,
} from "lucide-react";
import { authFetch, getCurrentUser } from "@/lib/auth";

interface TestRead {
  id: string;
  name: string;
  date: string;
  subject_name: string | null;
  max_marks: number;
}

interface Scorecard {
  test: TestRead;
  result: {
    marks_obtained: number | null;
    is_absent: boolean;
    percentage: number | null;
    percentile: number | null;
    rank: number | null;
    remarks: string | null;
  };
  max_marks: number;
  passing_marks: number | null;
  is_passed: boolean | null;
  class_highest_marks: number | null;
  class_average_marks: number | null;
}

export default function StudentResultsPage() {
  const [scorecards, setScorecards] = useState<Scorecard[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedReport, setSelectedReport] = useState<Scorecard | null>(null);
  const user = getCurrentUser();

  useEffect(() => {
    (async () => {
      setLoading(true);
      const testsRes = await authFetch<{ items: TestRead[] }>("/api/v1/examination/tests?page_size=50");
      if (testsRes.error) {
        setError(testsRes.error);
        setLoading(false);
        return;
      }
      const tests = (testsRes.data as any)?.items || [];
      const cards = await Promise.all(
        tests.map((t: TestRead) => authFetch<{ data: Scorecard }>(`/api/v1/examination/tests/${t.id}/my-scorecard`))
      );
      const valid = cards
        .map((c) => (c.data as any)?.data as Scorecard | undefined)
        .filter((c): c is Scorecard => !!c && c.result.marks_obtained !== null);
      setScorecards(valid);
      setLoading(false);
    })();
  }, []);

  const testsTaken = scorecards.length;
  const topperCount = scorecards.filter((s) => s.result.rank === 1).length;
  const avgPercentage =
    testsTaken > 0
      ? (scorecards.reduce((sum, s) => sum + (s.result.percentage || 0), 0) / testsTaken).toFixed(1)
      : "—";

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      {/* Header */}
      <div className="bg-white rounded-3xl border border-slate-200/90 p-6 sm:p-8 shadow-sm">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <div className="flex items-center gap-2 mb-1">
              <span className="text-[10px] font-black uppercase tracking-wider px-2 py-0.5 rounded bg-amber-50 text-amber-800 border border-amber-200">
                Official Academic Performance Record
              </span>
            </div>
            <h1 className="text-2xl font-black text-slate-900 tracking-tight">
              Report Card & Mock Test Ledger
            </h1>
            <p className="text-xs text-slate-500 mt-1 font-medium">
              Student: <strong className="text-slate-800">{user?.first_name} {user?.last_name}</strong>
            </p>
          </div>
        </div>
      </div>

      {error && (
        <div className="p-3.5 rounded-2xl bg-red-50 border border-red-200 text-[#c22329] text-xs flex items-center gap-2">
          <AlertTriangle className="w-4 h-4" />
          <span className="font-semibold">{error}</span>
        </div>
      )}

      {/* Performance Summary Banner */}
      {!loading && testsTaken > 0 && (
        <div className="bg-gradient-to-r from-amber-50 via-red-50 to-amber-50 rounded-3xl border border-amber-200/90 p-6 shadow-xs flex flex-col md:flex-row md:items-center justify-between gap-6">
          <div className="flex items-start gap-4">
            <div className="w-14 h-14 rounded-2xl bg-white border border-amber-300 flex items-center justify-center text-amber-600 shadow-md shrink-0">
              <Award className="w-8 h-8" />
            </div>
            <div className="space-y-1">
              <span className="text-xs font-bold text-slate-600">
                Cumulative Average: <strong className="text-emerald-700">{avgPercentage}%</strong>
              </span>
              <h2 className="text-lg font-black text-slate-900">
                Evaluated Test Performance
              </h2>
            </div>
          </div>

          <div className="grid grid-cols-2 gap-3 text-center shrink-0">
            <div className="p-3 bg-white/90 rounded-2xl border border-amber-200">
              <span className="text-[10px] font-bold text-slate-400 uppercase block">Tests Taken</span>
              <span className="text-xl font-black text-slate-900">{testsTaken}</span>
            </div>
            <div className="p-3 bg-white/90 rounded-2xl border border-amber-200">
              <span className="text-[10px] font-bold text-slate-400 uppercase block">Topper Ranks</span>
              <span className="text-xl font-black text-amber-700">{topperCount}</span>
            </div>
          </div>
        </div>
      )}

      {/* Test Scores Ledger */}
      <div className="bg-white rounded-3xl border border-slate-200/90 p-6 shadow-sm space-y-4">
        <div className="flex items-center justify-between pb-3 border-b border-slate-100">
          <div>
            <h2 className="text-base font-black text-slate-900 flex items-center gap-2">
              <FileText className="w-4 h-4 text-[#c22329]" />
              <span>Evaluated Test Scores</span>
            </h2>
          </div>
        </div>

        {loading ? (
          <div className="flex items-center justify-center py-12 text-slate-500 gap-2 text-sm font-bold">
            <Loader2 className="w-5 h-5 animate-spin" />
            <span>Loading your results…</span>
          </div>
        ) : scorecards.length === 0 ? (
          <div className="py-12 text-center text-sm text-slate-500">
            No evaluated test results published yet.
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs border-collapse">
              <thead>
                <tr className="bg-slate-50 border-b border-slate-200 text-slate-500 uppercase text-[10px] font-extrabold tracking-wider">
                  <th className="py-3 px-4">Test Title</th>
                  <th className="py-3 px-4">Date</th>
                  <th className="py-3 px-4">Score</th>
                  <th className="py-3 px-4">Percentage</th>
                  <th className="py-3 px-4">Batch Average</th>
                  <th className="py-3 px-4">Rank</th>
                  <th className="py-3 px-4 text-right">Official Slip</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 font-medium text-slate-700">
                {scorecards.map((s) => (
                  <tr key={s.test.id} className="hover:bg-slate-50/70 transition-colors">
                    <td className="py-3.5 px-4 font-bold text-slate-900">
                      <div>{s.test.name}</div>
                      {s.test.subject_name && (
                        <span className="text-[10px] text-slate-400">{s.test.subject_name}</span>
                      )}
                    </td>
                    <td className="py-3.5 px-4 text-slate-600">{s.test.date}</td>
                    <td className="py-3.5 px-4 font-black text-slate-900 text-sm">
                      {s.result.marks_obtained} <span className="text-xs font-normal text-slate-400">/ {s.max_marks}</span>
                    </td>
                    <td className="py-3.5 px-4 font-bold text-emerald-600">
                      {s.result.percentage?.toFixed(1)}%
                    </td>
                    <td className="py-3.5 px-4 text-slate-500">
                      {s.class_average_marks != null ? `${((s.class_average_marks / s.max_marks) * 100).toFixed(1)}%` : "—"}
                    </td>
                    <td className="py-3.5 px-4">
                      {s.result.rank ? (
                        <span className="px-2.5 py-1 rounded-full bg-amber-50 text-amber-800 border border-amber-200 text-[10px] font-black inline-flex items-center gap-1">
                          <Sparkles className="w-3 h-3 text-amber-500" />
                          Rank {s.result.rank}
                        </span>
                      ) : (
                        <span className="text-slate-400">—</span>
                      )}
                    </td>
                    <td className="py-3.5 px-4 text-right">
                      <button
                        onClick={() => setSelectedReport(s)}
                        className="inline-flex items-center gap-1 px-3 py-1.5 rounded-lg bg-red-50 hover:bg-[#c22329] text-[#c22329] hover:text-white border border-red-200 text-[11px] font-bold transition-colors cursor-pointer"
                      >
                        <Printer className="w-3 h-3" />
                        <span>View & Print</span>
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Official Report Card Modal */}
      {selectedReport && (
        <div className="fixed inset-0 z-50 bg-slate-900/60 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-white rounded-3xl border border-slate-300 max-w-xl w-full p-6 sm:p-8 shadow-2xl space-y-6 relative max-h-[90vh] overflow-y-auto">
            <button
              onClick={() => setSelectedReport(null)}
              className="absolute top-6 right-6 p-2 rounded-xl bg-slate-100 hover:bg-slate-200 text-slate-500 hover:text-slate-800 transition-colors"
            >
              <X className="w-5 h-5" />
            </button>

            <div className="text-center pb-5 border-b border-slate-200 space-y-2">
              <div className="w-12 h-12 mx-auto rounded-2xl bg-white border border-red-200 p-1 flex items-center justify-center shadow-md shadow-red-500/10">
                <div className="text-center">
                  <span className="block font-black text-xs text-[#c22329] leading-none">आरंभ</span>
                  <span className="block font-extrabold text-[7px] text-amber-600 uppercase mt-0.5">EST. 2015</span>
                </div>
              </div>
              <div>
                <h3 className="text-xl font-black text-slate-900 tracking-tight">
                  AARAMBH INSTITUTE, INDORE
                </h3>
                <div className="inline-block mt-2 px-3 py-1 rounded-full bg-red-50 text-[#c22329] border border-red-200 text-xs font-black uppercase tracking-wider">
                  Official Student Performance Certificate
                </div>
              </div>
            </div>

            <div className="grid grid-cols-2 gap-3 p-4 rounded-2xl bg-slate-50 border border-slate-200 text-xs">
              <div>
                <span className="text-[10px] text-slate-400 uppercase font-bold block">Student Name</span>
                <span className="font-black text-slate-900">{user?.first_name} {user?.last_name}</span>
              </div>
              <div>
                <span className="text-[10px] text-slate-400 uppercase font-bold block">Test</span>
                <span className="font-bold text-slate-800">{selectedReport.test.name}</span>
              </div>
            </div>

            <table className="w-full text-xs text-left border-collapse">
              <thead>
                <tr className="bg-slate-100 text-slate-600 font-extrabold text-[10px] uppercase">
                  <th className="p-2.5 rounded-l-lg">Metric</th>
                  <th className="p-2.5 text-right rounded-r-lg">Value</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 text-slate-700 font-medium">
                <tr>
                  <td className="p-2.5 font-bold text-slate-900">Marks Obtained</td>
                  <td className="p-2.5 text-right font-black">{selectedReport.result.marks_obtained} / {selectedReport.max_marks}</td>
                </tr>
                <tr>
                  <td className="p-2.5 font-bold text-slate-900">Percentage</td>
                  <td className="p-2.5 text-right text-emerald-700 font-bold">{selectedReport.result.percentage?.toFixed(1)}%</td>
                </tr>
                <tr>
                  <td className="p-2.5 font-bold text-slate-900">Rank</td>
                  <td className="p-2.5 text-right">{selectedReport.result.rank ?? "—"}</td>
                </tr>
                <tr>
                  <td className="p-2.5 font-bold text-slate-900">Percentile</td>
                  <td className="p-2.5 text-right">{selectedReport.result.percentile?.toFixed(1) ?? "—"}</td>
                </tr>
                <tr>
                  <td className="p-2.5 font-bold text-slate-900">Class Average</td>
                  <td className="p-2.5 text-right">{selectedReport.class_average_marks?.toFixed(1) ?? "—"}</td>
                </tr>
                <tr>
                  <td className="p-2.5 font-bold text-slate-900">Class Highest</td>
                  <td className="p-2.5 text-right">{selectedReport.class_highest_marks?.toFixed(1) ?? "—"}</td>
                </tr>
                <tr>
                  <td className="p-2.5 font-bold text-slate-900">Result</td>
                  <td className="p-2.5 text-right">
                    {selectedReport.is_passed === null ? "—" : selectedReport.is_passed ? (
                      <span className="text-emerald-600 font-bold">PASS</span>
                    ) : (
                      <span className="text-[#c22329] font-bold">FAIL</span>
                    )}
                  </td>
                </tr>
              </tbody>
            </table>

            {selectedReport.result.remarks && (
              <div className="p-4 rounded-2xl bg-slate-50 border border-slate-200 space-y-2 text-xs">
                <span className="font-bold text-slate-700 block">Faculty Remarks:</span>
                <p className="text-slate-600 italic font-medium leading-relaxed">
                  &ldquo;{selectedReport.result.remarks}&rdquo;
                </p>
              </div>
            )}

            <div className="pt-4 flex items-center justify-end border-t border-slate-200">
              <button
                onClick={() => window.print()}
                className="px-4 py-2 rounded-xl bg-slate-900 hover:bg-slate-800 text-white text-xs font-bold flex items-center gap-1.5 transition-colors cursor-pointer shadow-md"
              >
                <Printer className="w-3.5 h-3.5" />
                <span>Print Document</span>
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
