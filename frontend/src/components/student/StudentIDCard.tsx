"use client";

import React, { useEffect, useRef, useState } from "react";
import { X, Download, Printer, Loader2 } from "lucide-react";
import { authFetch } from "@/lib/auth";

interface StudentIDCardProps {
  onClose: () => void;
}

interface CardData {
  full_name: string;
  admission_number: string;
  class_name: string | null;
  batch_name: string | null;
  joining_date: string | null;
}

export default function StudentIDCard({ onClose }: StudentIDCardProps) {
  const cardRef = useRef<HTMLDivElement>(null);
  const [data, setData] = useState<CardData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    (async () => {
      const meRes = await authFetch<{ data: { type: string; profile: any } }>("/api/v1/me/profile");
      const profile = (meRes.data as any)?.data?.profile;
      if (meRes.error || !profile) {
        setError(meRes.error || "Could not load your student profile");
        setLoading(false);
        return;
      }

      let className: string | null = null;
      if (profile.current_class_id) {
        const classRes = await authFetch<any[]>("/api/v1/admin/academic/classes");
        const match = ((classRes.data as any) || []).find((c: any) => c.id === profile.current_class_id);
        className = match?.name || null;
      }

      let batchName: string | null = null;
      const enrollRes = await authFetch<any[]>("/api/v1/me/enrollments");
      const activeEnrollment = ((enrollRes.data as any) || []).find((e: any) => e.status === "ACTIVE");
      if (activeEnrollment) {
        const batchRes = await authFetch<any>(`/api/v1/admin/academic/batches/${activeEnrollment.batch_id}`);
        batchName = (batchRes.data as any)?.name || null;
      }

      setData({
        full_name: profile.full_name,
        admission_number: profile.admission_number || "—",
        class_name: className,
        batch_name: batchName,
        joining_date: profile.joining_date,
      });
      setLoading(false);
    })();
  }, []);

  const initials = data
    ? data.full_name
        .split(" ")
        .map((p) => p[0])
        .slice(0, 2)
        .join("")
        .toUpperCase()
    : "";

  const handlePrint = () => {
    const cardHTML = cardRef.current?.innerHTML;
    if (!cardHTML || !data) return;

    const printWindow = window.open("", "_blank", "width=800,height=600");
    if (!printWindow) return;

    printWindow.document.write(`
      <!DOCTYPE html>
      <html>
        <head>
          <title>Student ID — ${data.full_name} (${data.admission_number})</title>
          <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@400;600;700;900&display=swap" rel="stylesheet">
          <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body {
              font-family: 'Outfit', Arial, sans-serif;
              background: #fff;
              display: flex;
              align-items: center;
              justify-content: center;
              min-height: 100vh;
              padding: 20px;
            }
            .id-card {
              width: 360px;
              border-radius: 16px;
              overflow: hidden;
              border: 2px solid #c22329;
              box-shadow: 0 8px 32px rgba(194,35,41,0.15);
            }
            .card-header {
              background: #c22329;
              padding: 16px 20px;
              text-align: center;
            }
            .card-header .hindi { font-size: 20px; font-weight: 900; color: #ffd580; }
            .card-header .eng { font-size: 13px; font-weight: 700; color: #fff; letter-spacing: 2px; margin-top: 2px; }
            .card-header .tagline { font-size: 10px; color: #ffcccc; margin-top: 4px; }
            .gold-stripe { height: 4px; background: #c99a5e; }
            .card-body { background: #fff; padding: 24px 20px; }
            .photo-row { display: flex; align-items: center; gap: 18px; margin-bottom: 20px; }
            .photo-circle {
              width: 72px; height: 72px;
              border-radius: 50%;
              background: #fff0f0;
              border: 3px solid #c22329;
              display: flex; align-items: center; justify-content: center;
              font-size: 22px; font-weight: 900; color: #c22329;
              flex-shrink: 0;
            }
            .student-name { font-size: 18px; font-weight: 900; color: #1e293b; }
            .student-class { font-size: 12px; color: #c22329; font-weight: 700; margin-top: 4px; }
            .divider { height: 1px; background: #e2e8f0; margin: 16px 0; }
            .info-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }
            .info-item {}
            .info-label { font-size: 9px; font-weight: 700; text-transform: uppercase; letter-spacing: 1px; color: #94a3b8; }
            .info-value { font-size: 13px; font-weight: 700; color: #1e293b; margin-top: 2px; }
            .validity-box {
              margin-top: 16px;
              padding: 10px 14px;
              background: #f0fdf4;
              border: 1px solid #bbf7d0;
              border-radius: 10px;
              display: flex; align-items: center; justify-content: space-between;
            }
            .validity-label { font-size: 9px; font-weight: 700; text-transform: uppercase; color: #15803d; }
            .validity-value { font-size: 12px; font-weight: 700; color: #166534; }
            .card-footer {
              background: #c22329;
              padding: 12px 20px;
              text-align: center;
              font-size: 10px;
              color: #ffcccc;
              line-height: 1.6;
            }
            .card-footer strong { color: #fff; }
            @media print {
              body { background: white; }
              .id-card { box-shadow: none; }
            }
          </style>
        </head>
        <body>
          <div class="id-card">
            <div class="card-header">
              <div class="hindi">आरंभ</div>
              <div class="eng">AARAMBH INSTITUTE</div>
              <div class="tagline">Step Toward Success • Est. 2015 • Hawa Bangla, Indore</div>
            </div>
            <div class="gold-stripe"></div>
            <div class="card-body">
              <div class="photo-row">
                <div class="photo-circle">${initials}</div>
                <div>
                  <div class="student-name">${data.full_name}</div>
                  <div class="student-class">${data.class_name || "Class Not Assigned"}</div>
                </div>
              </div>
              <div class="divider"></div>
              <div class="info-grid">
                <div class="info-item">
                  <div class="info-label">Admission Number</div>
                  <div class="info-value">${data.admission_number}</div>
                </div>
                <div class="info-item">
                  <div class="info-label">Batch</div>
                  <div class="info-value">${data.batch_name || "Unassigned"}</div>
                </div>
              </div>
              <div class="validity-box">
                <div>
                  <div class="validity-label">Admitted On</div>
                  <div class="validity-value">${data.joining_date || "—"}</div>
                </div>
                <div class="validity-label" style="color:#16a34a">✓ ACTIVE</div>
              </div>
            </div>
            <div class="gold-stripe"></div>
            <div class="card-footer">
              <strong>8 Shantinath Puri, Hawa Bangla, Indore — 452001</strong><br/>
              Helpline: 88397-14081 • aarambhinstitute09@gmail.com
            </div>
          </div>
          <script>window.onload = function() { window.print(); }<\/script>
        </body>
      </html>
    `);
    printWindow.document.close();
  };

  return (
    <div className="fixed inset-0 z-50 bg-slate-900/70 backdrop-blur-sm flex items-center justify-center p-4">
      <div className="bg-white rounded-3xl border border-slate-200 shadow-2xl w-full max-w-md p-6 space-y-5 relative">
        {/* Modal Header */}
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-base font-black text-slate-900">Student Identity Card</h2>
            {data && (
              <p className="text-xs text-slate-500 font-medium">{data.full_name} • {data.admission_number}</p>
            )}
          </div>
          <button
            onClick={onClose}
            className="p-2 rounded-xl bg-slate-100 hover:bg-slate-200 text-slate-500 transition-colors cursor-pointer"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {loading ? (
          <div className="flex items-center justify-center py-16 text-slate-500 gap-2 text-sm font-bold">
            <Loader2 className="w-5 h-5 animate-spin" />
            <span>Loading your ID card…</span>
          </div>
        ) : error || !data ? (
          <div className="py-10 text-center text-sm text-[#c22329] font-semibold">{error}</div>
        ) : (
          <>
            {/* ID Card Preview */}
            <div ref={cardRef} className="rounded-2xl overflow-hidden border-2 border-[#c22329] shadow-lg shadow-red-200/40">
              {/* Card Header */}
              <div className="bg-[#c22329] px-5 py-4 text-center">
                <div className="text-xl font-black text-[#ffd580]">आरंभ</div>
                <div className="text-xs font-bold text-white tracking-[2px] mt-0.5">AARAMBH INSTITUTE</div>
                <div className="text-[10px] text-red-200 mt-1">Step Toward Success • Est. 2015 • Hawa Bangla, Indore</div>
              </div>

              {/* Gold Stripe */}
              <div className="h-1 bg-[#c99a5e]" />

              {/* Card Body */}
              <div className="bg-white px-5 py-5 space-y-4">
                {/* Photo + Name Row */}
                <div className="flex items-center gap-4">
                  <div className="w-16 h-16 rounded-full bg-red-50 border-[3px] border-[#c22329] flex items-center justify-center text-[#c22329] text-xl font-black shrink-0">
                    {initials}
                  </div>
                  <div>
                    <div className="text-lg font-black text-slate-900">{data.full_name}</div>
                    <div className="text-[11px] font-bold text-[#c22329] mt-0.5">
                      {data.class_name || "Class Not Assigned"}
                    </div>
                  </div>
                </div>

                <div className="h-px bg-slate-100" />

                {/* Info Grid */}
                <div className="grid grid-cols-2 gap-3">
                  <div>
                    <div className="text-[9px] font-bold uppercase tracking-wider text-slate-400">Admission Number</div>
                    <div className="text-sm font-bold text-slate-900 mt-0.5">{data.admission_number}</div>
                  </div>
                  <div>
                    <div className="text-[9px] font-bold uppercase tracking-wider text-slate-400">Batch</div>
                    <div className="text-sm font-bold text-slate-900 mt-0.5">{data.batch_name || "Unassigned"}</div>
                  </div>
                </div>

                {/* Validity */}
                <div className="flex items-center justify-between px-3 py-2.5 rounded-xl bg-emerald-50 border border-emerald-200">
                  <div>
                    <div className="text-[9px] font-bold uppercase tracking-wider text-emerald-700">Admitted On</div>
                    <div className="text-sm font-bold text-emerald-900 mt-0.5">{data.joining_date || "—"}</div>
                  </div>
                  <span className="text-[10px] font-black text-emerald-700 bg-emerald-100 border border-emerald-300 px-2 py-0.5 rounded-full">
                    ✓ ACTIVE
                  </span>
                </div>
              </div>

              {/* Gold Stripe */}
              <div className="h-1 bg-[#c99a5e]" />

              {/* Card Footer */}
              <div className="bg-[#c22329] px-5 py-3 text-center">
                <div className="text-[10px] font-bold text-white">8 Shantinath Puri, Hawa Bangla, Indore — 452001</div>
                <div className="text-[10px] text-red-200 mt-0.5">Helpline: 88397-14081 • aarambhinstitute09@gmail.com</div>
              </div>
            </div>

            {/* Action Buttons */}
            <div className="flex items-center gap-3 pt-1">
              <button
                onClick={handlePrint}
                className="flex-1 flex items-center justify-center gap-2 py-2.5 rounded-xl border border-slate-200 bg-white hover:bg-slate-50 text-xs font-bold text-slate-800 transition-colors shadow-xs cursor-pointer"
              >
                <Printer className="w-4 h-4 text-slate-500" />
                <span>Print / Save as PDF</span>
              </button>
              <button
                onClick={handlePrint}
                className="flex-1 flex items-center justify-center gap-2 py-2.5 rounded-xl bg-[#c22329] hover:bg-red-700 text-white text-xs font-bold transition-colors shadow-md cursor-pointer"
              >
                <Download className="w-4 h-4" />
                <span>Download Card</span>
              </button>
            </div>
          </>
        )}
      </div>
    </div>
  );
}
