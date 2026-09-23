import type { Metadata } from "next";
import "./globals.css";
import Navbar from "@/components/landing/Navbar";
import Footer from "@/components/landing/Footer";
import FloatingWhatsApp from "@/components/landing/FloatingWhatsApp";
import MarketingWrapper from "@/components/layout/MarketingWrapper";
import ScrollProgress from "@/components/ui/ScrollProgress";
import { getLandingData } from "@/lib/api";

export const metadata: Metadata = {
  title: "Aarambh Institute | Step Toward Success | Coaching Classes 4th to 12th & Degree, Indore",
  description:
    "Aarambh Institute (Est. 2015), Indore — 15+ Years Experience faculty offering coaching for Classes 4th to 12th (MP Board, CBSE, ICSE), B.Com, M.Com, BBA, MBA, B.Sc. Small batches, 98% board results. 8 Shantinath Puri, Hawa Bangla, Indore.",
  keywords: [
    "Aarambh Institute",
    "Coaching in Indore",
    "MP Board Coaching Indore",
    "CBSE Coaching Class 10 12",
    "Hawa Bangla Coaching",
    "Class 4 to 12 Coaching",
    "B.Com M.Com Coaching Indore",
  ],
};

export default async function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const data = await getLandingData();

  return (
    <html lang="en" className="scroll-smooth">
      <head>
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="anonymous" />
        <link
          href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800;900&family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap"
          rel="stylesheet"
        />
      </head>
      <body className="min-h-screen bg-[#f8fafd] text-slate-900 font-['Outfit',sans-serif] selection:bg-[#c99a5e]/30 selection:text-[#991b1b] flex flex-col">
        {/* Scroll progress indicator */}
        <ScrollProgress />

        {/* Redesigned spacious dual-layer header */}
        <Navbar contact={data.contact} />

        {/* Dynamic page content with dynamic top offset for marketing pages only */}
        <MarketingWrapper>
          {children}
        </MarketingWrapper>

        {/* Global Footer */}
        <Footer contact={data.contact} />

        {/* Global Floating WhatsApp Quick Action */}
        <FloatingWhatsApp />
      </body>
    </html>
  );
}
