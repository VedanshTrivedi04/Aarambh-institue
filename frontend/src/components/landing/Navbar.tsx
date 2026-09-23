"use client";

import React, { useState, useEffect } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  Phone,
  User,
  Menu,
  X,
  MapPin,
  Clock,
  ArrowRight,
  MessageCircle,
  GraduationCap,
  Sparkles,
} from "lucide-react";
import { InstituteContactInfo } from "@/types/landing";

interface NavbarProps {
  contact?: InstituteContactInfo;
}

export default function Navbar({ contact }: NavbarProps) {
  const pathname = usePathname();
  const [scrolled, setScrolled] = useState(false);
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  if (
    pathname?.startsWith("/admin") ||
    pathname?.startsWith("/teacher") ||
    pathname?.startsWith("/student") ||
    pathname?.startsWith("/login")
  ) {
    return null;
  }

  const phonePrimary = contact?.primary_phone || "88397-14081";
  const whatsappNum = contact?.whatsapp_number || "88397-14081";
  const address = contact?.full_address || "8 Shantinath Puri, Hawa Bangla, Indore";
  const workingHours = contact?.working_hours || "10:00 AM - 8:00 PM";

  useEffect(() => {
    const handleScroll = () => {
      if (window.scrollY > 20) {
        setScrolled(true);
      } else {
        setScrolled(false);
      }
    };
    window.addEventListener("scroll", handleScroll, { passive: true });
    return () => window.removeEventListener("scroll", handleScroll);
  }, []);

  const navLinks = [
    { label: "Home", href: "/" },
    { label: "About Us", href: "/about" },
    { label: "Courses", href: "/courses" },
    { label: "Faculty", href: "/faculty" },
    { label: "Results & Toppers", href: "/results" },
    { label: "Student Corner", href: "/student-corner" },
    { label: "Contact", href: "/contact" },
  ];

  const isActive = (href: string) => {
    if (href === "/") return pathname === "/";
    return pathname.startsWith(href);
  };

  return (
    <header
      className="fixed top-0 left-0 right-0 z-50 transition-all duration-300 animate-fade-in-up"
      style={{ animationDuration: "0.5s" }}
    >
      {/* Top Utility Micro-Bar */}
      <div className="bg-slate-900 text-slate-300 text-[11px] sm:text-xs border-b border-slate-800 transition-all">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-8 sm:h-9 flex items-center justify-between">
          {/* Left: Campus & Timings */}
          <div className="flex items-center gap-3 sm:gap-5 overflow-hidden text-ellipsis whitespace-nowrap">
            <span className="flex items-center gap-1.5 text-slate-300 hover:text-white transition-colors">
              <MapPin className="w-3 h-3 text-[#c99a5e] shrink-0" />
              <span className="truncate max-w-[200px] sm:max-w-none">
                Hawa Bangla, Indore (MP)
              </span>
            </span>
            <span className="hidden md:flex items-center gap-1.5 text-slate-400">
              <Clock className="w-3 h-3 text-slate-500 shrink-0" />
              <span>{workingHours}</span>
            </span>
            <span className="hidden xl:inline-flex items-center gap-1 px-2 py-0.5 rounded-full bg-red-950/70 text-red-300 border border-red-800/60 font-semibold text-[10px]">
              <Sparkles className="w-2.5 h-2.5 text-amber-400" />
              <span>Admissions Open 2026-27</span>
            </span>
          </div>

          {/* Right: Quick Contacts & ERP Login */}
          <div className="flex items-center gap-3 sm:gap-4 shrink-0 font-medium">
            <a
              href={`tel:+91${phonePrimary.replace(/[^0-9]/g, "")}`}
              className="flex items-center gap-1.5 hover:text-white transition-colors text-slate-200"
            >
              <Phone className="w-3 h-3 text-[#c22329]" />
              <span className="font-semibold">{phonePrimary}</span>
            </a>

            <a
              href={`https://wa.me/91${whatsappNum.replace(/[^0-9]/g, "")}?text=Hello%20Aarambh%20Institute%2C%20I%20am%20interested%20in%20coaching%20classes.`}
              target="_blank"
              rel="noopener noreferrer"
              className="hidden sm:flex items-center gap-1 text-emerald-400 hover:text-emerald-300 transition-colors"
            >
              <MessageCircle className="w-3 h-3" />
              <span>WhatsApp</span>
            </a>

            <span className="text-slate-700 hidden sm:inline">|</span>

            <Link
              href="/admissions"
              className="flex items-center gap-1 text-[#c99a5e] hover:text-amber-300 font-semibold transition-colors"
            >
              <GraduationCap className="w-3.5 h-3.5" />
              <span>Free Demo</span>
            </Link>
          </div>
        </div>
      </div>

      {/* Main Spacious Navbar */}
      <div
        className={`bg-white/95 backdrop-blur-xl border-b border-slate-200/90 transition-all duration-200 ${
          scrolled ? "shadow-md py-2 sm:py-2.5" : "shadow-sm py-3 sm:py-3.5"
        }`}
      >
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex items-center justify-between">
          {/* Brand Logo & Name */}
          <Link href="/" className="flex items-center gap-3 group shrink-0">
            <div className="relative w-10 h-10 sm:w-11 sm:h-11 rounded-2xl bg-white border border-red-200 p-1 shadow-md shadow-red-500/10 flex items-center justify-center overflow-hidden group-hover:border-red-400 transition-colors">
              <div className="text-center">
                <span className="block font-black text-xs sm:text-sm text-[#c22329] leading-none tracking-tight">
                  आरंभ
                </span>
                <span className="block font-extrabold text-[7px] sm:text-[8px] text-amber-600 uppercase tracking-tighter mt-0.5">
                  AARAMBH
                </span>
              </div>
            </div>

            <div className="flex flex-col">
              <div className="flex items-center gap-1.5">
                <span className="font-black tracking-wide text-lg sm:text-xl text-slate-900">
                  AARAMBH
                </span>
                <span className="text-[10px] font-extrabold px-1.5 py-0.5 rounded bg-red-50 text-[#c22329] border border-red-200">
                  INSTITUTE
                </span>
              </div>
              <span className="text-[10px] text-[#c99a5e] tracking-wider uppercase font-bold">
                Step Toward Success • Est. 2015
              </span>
            </div>
          </Link>

          {/* Clean Desktop Navigation Links */}
          <nav className="hidden lg:flex items-center gap-1 xl:gap-2">
            {navLinks.map((link) => {
              const active = isActive(link.href);
              return (
                <Link
                  key={link.href}
                  href={link.href}
                  className={`group px-3 py-2 rounded-xl text-sm font-semibold transition-all relative ${
                    active
                      ? "text-[#c22329] bg-red-50/80 font-bold"
                      : "text-slate-700 hover:text-slate-950 hover:bg-slate-100/70"
                  }`}
                >
                  {link.label}
                  <span
                    className={`absolute bottom-0.5 left-3 right-3 h-0.5 bg-[#c22329] rounded-full origin-left transition-transform duration-300 ${
                      active ? "scale-x-100" : "scale-x-0 group-hover:scale-x-100"
                    }`}
                  />
                </Link>
              );
            })}
          </nav>

          {/* Desktop Right CTA Button */}
          <div className="hidden lg:flex items-center gap-3">
            <Link
              href="/admissions"
              className="btn-caramel-gold flex items-center gap-2 text-xs xl:text-sm font-extrabold px-4 xl:px-5 py-2.5 rounded-xl shadow-md transition-all hover:scale-105 active:scale-95"
            >
              <span>Join Free Demo</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </Link>
          </div>

          {/* Mobile Menu Toggle */}
          <div className="flex items-center gap-2 lg:hidden">
            <Link
              href="/admissions"
              className="text-xs font-bold px-3 py-1.5 rounded-lg bg-[#c22329] text-white shadow-sm"
            >
              Demo
            </Link>
            <button
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
              className="p-2 rounded-xl bg-slate-100 text-slate-700 hover:text-slate-950 border border-slate-200"
              aria-label="Toggle menu"
            >
              {mobileMenuOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
            </button>
          </div>
        </div>
      </div>

      {/* Mobile Drawer */}
      {mobileMenuOpen && (
        <div className="lg:hidden bg-white/98 border-b border-slate-200 px-6 py-5 space-y-4 shadow-2xl backdrop-blur-2xl animate-in fade-in slide-in-from-top-4 duration-200 max-h-[80vh] overflow-y-auto">
          <div className="flex flex-col space-y-1">
            {navLinks.map((link) => {
              const active = isActive(link.href);
              return (
                <Link
                  key={link.href}
                  href={link.href}
                  onClick={() => setMobileMenuOpen(false)}
                  className={`flex items-center justify-between py-2.5 px-3 rounded-xl text-base font-semibold transition-colors ${
                    active
                      ? "text-[#c22329] bg-red-50 font-bold"
                      : "text-slate-800 hover:bg-slate-50"
                  }`}
                >
                  <span>{link.label}</span>
                  {active && <span className="w-2 h-2 rounded-full bg-[#c22329]" />}
                </Link>
              );
            })}
          </div>

          <div className="pt-3 border-t border-slate-200 space-y-2.5">
            <Link
              href="/admissions"
              onClick={() => setMobileMenuOpen(false)}
              className="btn-caramel-gold w-full flex items-center justify-center gap-2 py-3 rounded-xl font-bold text-sm shadow-md"
            >
              <span>Join Free Demo Class</span>
              <ArrowRight className="w-4 h-4" />
            </Link>

            <div className="grid grid-cols-2 gap-2 pt-1">
              <a
                href={`tel:+91${phonePrimary.replace(/[^0-9]/g, "")}`}
                className="flex items-center justify-center gap-1.5 py-2.5 rounded-xl bg-slate-100 border border-slate-200 text-xs font-bold text-slate-800"
              >
                <Phone className="w-3.5 h-3.5 text-[#c22329]" />
                <span>Call Us</span>
              </a>
              <a
                href={`https://wa.me/91${whatsappNum.replace(/[^0-9]/g, "")}?text=Hello%20Aarambh%20Institute`}
                target="_blank"
                rel="noopener noreferrer"
                className="flex items-center justify-center gap-1.5 py-2.5 rounded-xl bg-emerald-50 border border-emerald-200 text-xs font-bold text-emerald-800"
              >
                <MessageCircle className="w-3.5 h-3.5 text-emerald-600" />
                <span>WhatsApp</span>
              </a>
            </div>
          </div>
        </div>
      )}
    </header>
  );
}
