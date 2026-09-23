"use client";

import React, { useEffect, useRef, useState, useCallback } from "react";
import { Sparkles, ChevronDown, BookOpen, Compass, Award, ArrowRight, CheckCircle2, Phone, MessageCircle } from "lucide-react";

const TOTAL_FRAMES = 240;

export default function HeroVideoScroll() {
  const containerRef = useRef<HTMLDivElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const imagesRef = useRef<HTMLImageElement[]>([]);
  const currentFrameRef = useRef<number>(0);
  const animationFrameIdRef = useRef<number | null>(null);

  const [loadedCount, setLoadedCount] = useState<number>(0);
  const [scrollProgress, setScrollProgress] = useState<number>(0);
  const [activeStage, setActiveStage] = useState<number>(1);
  const [isReady, setIsReady] = useState<boolean>(false);

  // Preload frames progressively
  useEffect(() => {
    const images: HTMLImageElement[] = [];
    imagesRef.current = images;
    let loaded = 0;

    // Load frame 0 immediately
    const firstImg = new Image();
    firstImg.src = "/frames/frame_000.webp";
    firstImg.onload = () => {
      images[0] = firstImg;
      loaded++;
      setLoadedCount(loaded);
      setIsReady(true);
      drawFrame(0);

      // Priority load next 35 frames
      for (let i = 1; i <= 35; i++) {
        loadSingleFrame(i);
      }

      // Load remaining in background
      const loadRemaining = () => {
        for (let i = 36; i < TOTAL_FRAMES; i++) {
          loadSingleFrame(i);
        }
      };

      if ("requestIdleCallback" in window) {
        (window as any).requestIdleCallback(loadRemaining, { timeout: 1000 });
      } else {
        setTimeout(loadRemaining, 80);
      }
    };

    const loadSingleFrame = (idx: number) => {
      const img = new Image();
      const padded = String(idx).padStart(3, "0");
      img.src = `/frames/frame_${padded}.webp`;
      img.onload = () => {
        images[idx] = img;
        loaded++;
        setLoadedCount(loaded);
      };
    };

    return () => {
      images.length = 0;
    };
  }, []);

  // Draw frame on canvas with aspect ratio preservation
  const drawFrame = useCallback((frameIndex: number) => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext("2d", { alpha: false });
    if (!ctx) return;

    let imgToDraw = imagesRef.current[frameIndex];
    if (!imgToDraw || !imgToDraw.complete) {
      for (let offset = 1; offset < 20; offset++) {
        if (imagesRef.current[frameIndex - offset]?.complete) {
          imgToDraw = imagesRef.current[frameIndex - offset];
          break;
        }
        if (imagesRef.current[frameIndex + offset]?.complete) {
          imgToDraw = imagesRef.current[frameIndex + offset];
          break;
        }
      }
    }

    if (!imgToDraw || !imgToDraw.complete) return;

    ctx.drawImage(imgToDraw, 0, 0, canvas.width, canvas.height);
  }, []);

  // Handle scroll calculation
  useEffect(() => {
    const handleScroll = () => {
      if (!containerRef.current) return;
      const rect = containerRef.current.getBoundingClientRect();
      const containerHeight = rect.height;
      const windowHeight = window.innerHeight;
      const totalScrollDistance = containerHeight - windowHeight;

      if (totalScrollDistance <= 0) return;

      const currentScroll = -rect.top;
      const progress = Math.min(1, Math.max(0, currentScroll / totalScrollDistance));

      setScrollProgress(progress);

      const targetFrame = Math.min(TOTAL_FRAMES - 1, Math.max(0, Math.floor(progress * (TOTAL_FRAMES - 1))));

      if (progress < 0.25) {
        setActiveStage(1);
      } else if (progress < 0.55) {
        setActiveStage(2);
      } else if (progress < 0.8) {
        setActiveStage(3);
      } else {
        setActiveStage(4);
      }

      if (targetFrame !== currentFrameRef.current) {
        currentFrameRef.current = targetFrame;
        if (animationFrameIdRef.current) {
          cancelAnimationFrame(animationFrameIdRef.current);
        }
        animationFrameIdRef.current = requestAnimationFrame(() => {
          drawFrame(targetFrame);
        });
      }
    };

    window.addEventListener("scroll", handleScroll, { passive: true });
    window.addEventListener("resize", handleScroll, { passive: true });
    handleScroll();

    return () => {
      window.removeEventListener("scroll", handleScroll);
      window.removeEventListener("resize", handleScroll);
      if (animationFrameIdRef.current) {
        cancelAnimationFrame(animationFrameIdRef.current);
      }
    };
  }, [drawFrame]);

  const jumpToStage = (stage: number) => {
    if (!containerRef.current) return;
    const containerTop = containerRef.current.offsetTop;
    const containerHeight = containerRef.current.offsetHeight;
    const scrollableDistance = containerHeight - window.innerHeight;

    let targetRatio = 0;
    if (stage === 1) targetRatio = 0.05;
    if (stage === 2) targetRatio = 0.35;
    if (stage === 3) targetRatio = 0.65;
    if (stage === 4) targetRatio = 0.95;

    window.scrollTo({
      top: containerTop + scrollableDistance * targetRatio,
      behavior: "smooth",
    });
  };

  const skipToContent = () => {
    const el = document.getElementById("about");
    if (el) {
      el.scrollIntoView({ behavior: "smooth" });
    }
  };

  return (
    <div
      ref={containerRef}
      className="relative w-full bg-[#f8fafd]"
      style={{ height: "420vh" }}
    >
      {/* Sticky Viewport */}
      <div className="sticky top-0 h-screen w-full overflow-hidden flex items-center justify-center bg-[#f0f6fc]">
        {/* Soft Background Radial Ambient Glows matching video */}
        <div className="absolute inset-0 pointer-events-none -z-10 overflow-hidden">
          <div className="absolute top-1/4 left-1/4 w-[600px] h-[600px] bg-blue-100/60 rounded-full blur-3xl" />
          <div className="absolute bottom-1/3 right-1/4 w-[600px] h-[600px] bg-amber-100/50 rounded-full blur-3xl" />
        </div>

        {/* Video Canvas */}
        <div className="relative w-full h-full flex items-center justify-center">
          <canvas
            ref={canvasRef}
            width={1280}
            height={720}
            className="w-full h-full object-cover sm:object-contain drop-shadow-md transition-opacity duration-500"
            style={{ opacity: isReady ? 1 : 0 }}
          />

          {/* Soft vignette to blend video canvas naturally */}
          <div className="absolute inset-0 pointer-events-none bg-gradient-to-t from-[#f8fafd]/40 via-transparent to-white/40" />
        </div>

        {/* Loading Indicator */}
        {loadedCount < TOTAL_FRAMES && (
          <div className="absolute top-20 right-6 z-20 flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-white/95 backdrop-blur-md border border-slate-200 text-xs font-semibold text-slate-700 shadow-md">
            <div className="w-2 h-2 rounded-full bg-[#c22329] animate-ping" />
            <span>Loading Aarambh Animation: {Math.round((loadedCount / TOTAL_FRAMES) * 100)}%</span>
          </div>
        )}

        {/* ======================================================== */}
        {/* STAGE 1 OVERLAY (0% - 25%): The Authentic Aarambh Hero */}
        {/* ======================================================== */}
        <div
          className={`absolute inset-0 flex flex-col items-end justify-center pr-6 sm:pr-14 md:pr-24 text-right pointer-events-none transition-all duration-700 ${
            activeStage === 1 && scrollProgress < 0.23
              ? "opacity-100 scale-100 translate-y-0"
              : "opacity-0 scale-95 translate-y-8"
          }`}
        >
          <div className="max-w-xl space-y-4 pt-12">
            <div className="inline-flex items-center gap-2 px-3.5 py-1 rounded-full bg-red-50 border border-red-200 text-[#c22329] text-xs font-extrabold uppercase tracking-wider shadow-sm">
              <Sparkles className="w-3.5 h-3.5 text-amber-500" />
              <span>Step Toward Success • Est. 2015</span>
            </div>

            <h1 className="text-3xl sm:text-5xl font-black tracking-tight text-slate-900 leading-tight">
              Excel in Boards with <br />
              <span className="text-[#c22329]">Expert Guidance</span>
            </h1>

            <p className="text-sm sm:text-base text-slate-700 font-medium leading-relaxed">
              15 Years of trusted coaching for <strong className="text-slate-900">Class 4th to 12th</strong>, B.Sc, B.Com, M.Com, BBA & MBA.
            </p>

            <div className="flex flex-wrap items-center justify-end gap-2 text-xs font-bold text-slate-700 pt-1">
              <span className="px-3 py-1 rounded-lg bg-white/95 border border-slate-200 shadow-sm">
                MP Board
              </span>
              <span className="px-3 py-1 rounded-lg bg-white/95 border border-slate-200 shadow-sm">
                CBSE
              </span>
              <span className="px-3 py-1 rounded-lg bg-white/95 border border-slate-200 shadow-sm">
                ICSE
              </span>
              <span className="px-3 py-1 rounded-lg bg-amber-50 text-amber-900 border border-amber-200 shadow-sm">
                College Degrees
              </span>
            </div>

            <div className="flex items-center justify-end gap-3 pt-3 pointer-events-auto">
              <a
                href="#admissions"
                className="btn-caramel-gold px-5 py-2.5 rounded-xl text-xs sm:text-sm font-black shadow-md flex items-center gap-1.5"
              >
                <span>Enroll Now</span>
                <ArrowRight className="w-3.5 h-3.5" />
              </a>
              <a
                href="#programs"
                className="btn-oceanic-teal px-5 py-2.5 rounded-xl text-xs sm:text-sm font-black shadow-md flex items-center gap-1.5"
              >
                <span>View Courses</span>
                <BookOpen className="w-3.5 h-3.5" />
              </a>
            </div>
          </div>
        </div>

        {/* ======================================================== */}
        {/* STAGE 2 OVERLAY (25% - 55%): Student Desk & Small Batches */}
        {/* ======================================================== */}
        <div
          className={`absolute inset-0 flex items-center justify-start pl-6 sm:pl-14 md:pl-24 pointer-events-none transition-all duration-700 ${
            activeStage === 2
              ? "opacity-100 scale-100 translate-y-0"
              : "opacity-0 scale-95 translate-y-8"
          }`}
        >
          <div className="max-w-md space-y-4 text-left bg-white/95 backdrop-blur-xl p-7 rounded-3xl border border-slate-200 shadow-xl">
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-amber-50 text-amber-800 text-xs font-bold tracking-wider uppercase border border-amber-200">
              <Compass className="w-3.5 h-3.5 text-amber-600" />
              <span>Personalised Attention</span>
            </div>

            <h2 className="text-2xl sm:text-3xl font-black text-slate-900 leading-tight">
              Small Batches <br />
              <span className="text-[#c22329]">Maximum Individual Care</span>
            </h2>

            <p className="text-xs sm:text-sm text-slate-600 leading-relaxed font-medium">
              Only 20–35 students per batch. Teachers directly track your child&apos;s daily homework, conduct weekly progress tests, and resolve doubts on the spot.
            </p>

            <div className="space-y-2 pt-1 text-xs text-slate-800 font-bold">
              <div className="flex items-center gap-2">
                <CheckCircle2 className="w-4 h-4 text-emerald-600 flex-shrink-0" />
                <span>Weekly Subject Assessment Tests</span>
              </div>
              <div className="flex items-center gap-2">
                <CheckCircle2 className="w-4 h-4 text-emerald-600 flex-shrink-0" />
                <span>Direct Parent-Teacher Interaction</span>
              </div>
              <div className="flex items-center gap-2">
                <CheckCircle2 className="w-4 h-4 text-emerald-600 flex-shrink-0" />
                <span>Affordable Monthly Fee (₹800 - ₹1000/mo)</span>
              </div>
            </div>
          </div>
        </div>

        {/* ======================================================== */}
        {/* STAGE 3 OVERLAY (55% - 80%): 3D Open Book & Concepts */}
        {/* ======================================================== */}
        <div
          className={`absolute inset-0 flex flex-col items-center justify-end pb-28 text-center px-4 pointer-events-none transition-all duration-700 ${
            activeStage === 3
              ? "opacity-100 scale-100 translate-y-0"
              : "opacity-0 scale-95 translate-y-8"
          }`}
        >
          <div className="max-w-xl mx-auto space-y-3 bg-white/95 backdrop-blur-md p-6 rounded-3xl border border-slate-200 shadow-xl">
            <div className="inline-flex items-center gap-2 px-3.5 py-1 rounded-full bg-blue-50 border border-blue-200 text-blue-800 text-xs font-bold uppercase tracking-wider">
              <BookOpen className="w-3.5 h-3.5 text-blue-600" />
              <span>Comprehensive Study Material</span>
            </div>

            <h2 className="text-2xl sm:text-4xl font-black text-slate-900 leading-tight">
              Concept Clarity That Builds <br />
              <span className="text-amber-600">Top Board Achievers</span>
            </h2>

            <p className="text-xs sm:text-sm text-slate-600 font-medium max-w-lg mx-auto">
              Well-researched return modules, chapter-wise formula notes, and daily doubt clinics led by veteran faculty with up to 30 years of experience.
            </p>

            <div className="grid grid-cols-3 gap-2 pt-1 text-center">
              <div className="p-2 rounded-xl bg-slate-50 border border-slate-100">
                <span className="block text-lg font-black text-[#c22329]">98.5%</span>
                <span className="text-[10px] font-bold text-slate-600">Highest Board Result</span>
              </div>
              <div className="p-2 rounded-xl bg-slate-50 border border-slate-100">
                <span className="block text-lg font-black text-blue-700">12+</span>
                <span className="text-[10px] font-bold text-slate-600">Expert Faculty</span>
              </div>
              <div className="p-2 rounded-xl bg-slate-50 border border-slate-100">
                <span className="block text-lg font-black text-emerald-700">2000+</span>
                <span className="text-[10px] font-bold text-slate-600">Students Since 2015</span>
              </div>
            </div>
          </div>
        </div>

        {/* ======================================================== */}
        {/* STAGE 4 OVERLAY (80% - 100%): Knowledge Orbit & Call to Action */}
        {/* ======================================================== */}
        <div
          className={`absolute inset-0 flex flex-col items-center justify-end pb-16 sm:pb-24 text-center px-4 pointer-events-auto transition-all duration-700 ${
            activeStage === 4
              ? "opacity-100 scale-100 translate-y-0"
              : "opacity-0 scale-95 translate-y-8 pointer-events-none"
          }`}
        >
          <div className="max-w-2xl mx-auto space-y-4 bg-white/95 backdrop-blur-2xl p-6 sm:p-8 rounded-3xl border border-slate-200 shadow-2xl">
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-emerald-50 border border-emerald-200 text-emerald-800 text-xs font-bold">
              <span className="w-2 h-2 rounded-full bg-emerald-600 animate-pulse" />
              <span>Admissions Open for 2026 – 2027 Batches</span>
            </div>

            <h2 className="text-2xl sm:text-4xl font-black tracking-tight text-slate-900 leading-tight">
              Aarambh Institute <br />
              <span className="text-[#c22329]">Step Toward Success</span>
            </h2>

            <p className="text-xs sm:text-sm text-slate-600 max-w-lg mx-auto font-medium">
              8 Shantinath Puri, Hawa Bangla, Near Sai Mandir, Indore (MP). <br />
              Call us today for your child&apos;s free diagnostic demo session.
            </p>

            <div className="flex flex-wrap items-center justify-center gap-3 pt-1">
              <a
                href="#admissions"
                className="btn-caramel-gold px-6 py-3 rounded-xl text-xs sm:text-sm font-black shadow-lg hover:scale-105 transition-all flex items-center gap-2"
              >
                <span>Join Free Demo Class</span>
                <ArrowRight className="w-4 h-4" />
              </a>

              <a
                href="https://wa.me/918839714081?text=Hello%20Aarambh%20Institute%2C%20I%20want%20to%20enquire%20about%20admissions"
                target="_blank"
                rel="noopener noreferrer"
                className="px-6 py-3 rounded-xl text-xs sm:text-sm font-bold text-emerald-800 bg-emerald-50 hover:bg-emerald-100 border border-emerald-200 transition-all flex items-center gap-2"
              >
                <MessageCircle className="w-4 h-4 text-emerald-600" />
                <span>Chat on WhatsApp</span>
              </a>
            </div>
          </div>
        </div>

        {/* ======================================================== */}
        {/* FIXED HUD: Interactive Chapter Navigation & Scroll Hint */}
        {/* ======================================================== */}
        <div className="absolute bottom-6 left-6 right-6 z-30 flex items-center justify-between pointer-events-none">
          {/* Chapter Selector */}
          <div className="pointer-events-auto flex items-center gap-1.5 p-1.5 rounded-2xl bg-white/90 backdrop-blur-xl border border-slate-200 shadow-md">
            {[
              { id: 1, name: "01 Hero" },
              { id: 2, name: "02 Classroom" },
              { id: 3, name: "03 Concepts" },
              { id: 4, name: "04 Aarambh" },
            ].map((chapter) => (
              <button
                key={chapter.id}
                onClick={() => jumpToStage(chapter.id)}
                className={`px-3 py-1.5 rounded-xl text-xs font-bold transition-all ${
                  activeStage === chapter.id
                    ? "bg-[#c22329] text-white shadow-sm"
                    : "text-slate-600 hover:text-slate-950 hover:bg-slate-100"
                }`}
              >
                {chapter.name}
              </button>
            ))}
          </div>

          {/* Scroll percentage & Skip button */}
          <div className="pointer-events-auto flex items-center gap-3">
            <div className="hidden sm:flex items-center gap-2 px-3 py-1.5 rounded-xl bg-white/90 backdrop-blur-md border border-slate-200 text-xs font-mono text-slate-700 shadow-sm">
              <span className="font-semibold text-slate-500">SCROLL</span>
              <span className="text-[#c22329] font-bold">{Math.round(scrollProgress * 100)}%</span>
            </div>

            <button
              onClick={skipToContent}
              className="flex items-center gap-1 text-xs font-bold text-slate-700 hover:text-slate-950 px-3 py-1.5 rounded-xl bg-white/90 hover:bg-white border border-slate-200 shadow-sm transition-colors"
              title="Skip straight to Courses and Institute details"
            >
              <span>Explore Institute</span>
              <ChevronDown className="w-3.5 h-3.5" />
            </button>
          </div>
        </div>

        {/* Animated Scroll Down Indicator */}
        {scrollProgress < 0.15 && (
          <div className="absolute bottom-20 left-1/2 -translate-x-1/2 flex flex-col items-center gap-2 pointer-events-none text-slate-700 animate-bounce">
            <span className="text-[11px] uppercase tracking-widest font-extrabold text-[#c99a5e]">
              Scroll To Experience
            </span>
            <ChevronDown className="w-4 h-4 text-[#c22329]" />
          </div>
        )}
      </div>
    </div>
  );
}
