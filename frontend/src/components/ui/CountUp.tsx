"use client";

import React, { useEffect, useRef, useState } from "react";

type CountUpProps = {
  /** Full display value, e.g. "98.5%", "2,000+", "15+ Yrs", "Class 4–12" */
  value: string;
  className?: string;
  duration?: number;
};

/** Extracts the first numeric run (with optional decimal/commas) plus its prefix/suffix text */
function parseValue(value: string) {
  const match = value.match(/([\d,]+(\.\d+)?)/);
  if (!match) return null;

  const numStr = match[1];
  const num = parseFloat(numStr.replace(/,/g, ""));
  const prefix = value.slice(0, match.index);
  const suffix = value.slice((match.index ?? 0) + numStr.length);
  const decimals = numStr.includes(".") ? numStr.split(".")[1].length : 0;
  const hasCommas = numStr.includes(",");

  return { num, prefix, suffix, decimals, hasCommas };
}

function formatNumber(num: number, decimals: number, hasCommas: boolean) {
  const fixed = num.toFixed(decimals);
  if (!hasCommas) return fixed;
  const [intPart, decPart] = fixed.split(".");
  const withCommas = intPart.replace(/\B(?=(\d{3})+(?!\d))/g, ",");
  return decPart ? `${withCommas}.${decPart}` : withCommas;
}

export default function CountUp({ value, className = "", duration = 1400 }: CountUpProps) {
  const ref = useRef<HTMLSpanElement | null>(null);
  const [display, setDisplay] = useState(value);
  const started = useRef(false);

  useEffect(() => {
    const parsed = parseValue(value);
    const el = ref.current;
    if (!parsed || !el) {
      setDisplay(value);
      return;
    }

    setDisplay(`${parsed.prefix}${formatNumber(0, parsed.decimals, parsed.hasCommas)}${parsed.suffix}`);

    if (typeof IntersectionObserver === "undefined") {
      setDisplay(value);
      return;
    }

    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting && !started.current) {
            started.current = true;
            const start = performance.now();

            const tick = (now: number) => {
              const elapsed = now - start;
              const progress = Math.min(elapsed / duration, 1);
              const eased = 1 - Math.pow(1 - progress, 3);
              const current = parsed.num * eased;
              setDisplay(
                `${parsed.prefix}${formatNumber(current, parsed.decimals, parsed.hasCommas)}${parsed.suffix}`
              );
              if (progress < 1) requestAnimationFrame(tick);
            };

            requestAnimationFrame(tick);
            observer.unobserve(el);
          }
        });
      },
      { threshold: 0.4 }
    );

    observer.observe(el);
    return () => observer.disconnect();
  }, [value, duration]);

  return (
    <span ref={ref} className={className}>
      {display}
    </span>
  );
}
