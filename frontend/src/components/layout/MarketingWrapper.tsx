"use client";

import React from "react";
import { usePathname } from "next/navigation";

export default function MarketingWrapper({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const isPortal =
    pathname?.startsWith("/admin") ||
    pathname?.startsWith("/teacher") ||
    pathname?.startsWith("/student") ||
    pathname?.startsWith("/login");

  return (
    <div className={`flex-1 flex flex-col ${isPortal ? "" : "pt-20 sm:pt-24"}`}>
      {children}
    </div>
  );
}
