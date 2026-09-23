"use client";

import React from "react";
import { usePathname } from "next/navigation";
import { MessageCircle } from "lucide-react";

export default function FloatingWhatsApp() {
  const pathname = usePathname();

  if (
    pathname?.startsWith("/admin") ||
    pathname?.startsWith("/teacher") ||
    pathname?.startsWith("/student") ||
    pathname?.startsWith("/login")
  ) {
    return null;
  }

  return (
    <aside
      aria-label="WhatsApp Support"
      className="fixed bottom-6 right-6 z-50 flex items-center group animate-fade-in-up"
      style={{ animationDelay: "600ms" }}
    >
      {/* Tooltip on hover */}
      <div className="hidden sm:block mr-3 px-3.5 py-1.5 rounded-xl bg-white/95 backdrop-blur-md border border-slate-200 text-xs font-bold text-slate-800 shadow-xl opacity-0 group-hover:opacity-100 translate-x-1 group-hover:translate-x-0 transition-all pointer-events-none">
        Chat with Indore Counselor
      </div>

      <a
        href="https://wa.me/918839714081?text=Hello%20Aarambh%20Institute%2C%20I%20want%20to%20enquire%20about%20admissions%20and%20batches."
        target="_blank"
        rel="noopener noreferrer"
        className="relative w-14 h-14 rounded-full bg-[#25D366] hover:bg-[#20ba59] text-white flex items-center justify-center shadow-2xl shadow-emerald-600/40 hover:scale-110 transition-transform"
        aria-label="Chat on WhatsApp"
        title="Chat on WhatsApp (+91 88397-14081)"
      >
        {/* Pulsing invite ring */}
        <span className="absolute inset-0 rounded-full bg-[#25D366] animate-ping opacity-40 pointer-events-none" />

        <MessageCircle className="relative w-8 h-8 fill-white text-[#25D366]" />

        {/* Notification badge like in video */}
        <span className="absolute -top-1 -right-1 w-5 h-5 rounded-full bg-red-600 text-white text-[10px] font-black flex items-center justify-center border-2 border-white shadow-md animate-gentle-bounce">
          1
        </span>
      </a>
    </aside>
  );
}
