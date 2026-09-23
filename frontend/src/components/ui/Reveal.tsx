"use client";

import React, { useEffect, useRef, useState } from "react";

type RevealProps = {
  children: React.ReactNode;
  className?: string;
  /** Animation delay in milliseconds, useful for staggering lists */
  delay?: number;
  /** Direction the element travels in from */
  direction?: "up" | "down" | "left" | "right" | "none";
  /** Distance in pixels for the travel direction */
  distance?: number;
  /** Replay the animation every time it re-enters the viewport */
  repeat?: boolean;
  as?: keyof React.JSX.IntrinsicElements;
};

const AXIS: Record<string, [string, string]> = {
  up: ["translateY", "px"],
  down: ["translateY", "px"],
  left: ["translateX", "px"],
  right: ["translateX", "px"],
};

function getInitialTransform(direction: RevealProps["direction"], distance: number) {
  switch (direction) {
    case "up":
      return `translateY(${distance}px)`;
    case "down":
      return `translateY(-${distance}px)`;
    case "left":
      return `translateX(${distance}px)`;
    case "right":
      return `translateX(-${distance}px)`;
    default:
      return "none";
  }
}

export default function Reveal({
  children,
  className = "",
  delay = 0,
  direction = "up",
  distance = 28,
  repeat = false,
  as = "div",
}: RevealProps) {
  const ref = useRef<HTMLDivElement | null>(null);
  const [visible, setVisible] = useState(false);

  useEffect(() => {
    const el = ref.current;
    if (!el) return;

    if (typeof IntersectionObserver === "undefined") {
      setVisible(true);
      return;
    }

    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            setVisible(true);
            if (!repeat) observer.unobserve(el);
          } else if (repeat) {
            setVisible(false);
          }
        });
      },
      { threshold: 0.15, rootMargin: "0px 0px -8% 0px" }
    );

    observer.observe(el);
    return () => observer.disconnect();
  }, [repeat]);

  const Tag = as as any;

  return (
    <Tag
      ref={ref}
      className={className}
      style={{
        opacity: visible ? 1 : 0,
        transform: visible ? "none" : getInitialTransform(direction, distance),
        transition: `opacity 0.7s cubic-bezier(0.16,1,0.3,1) ${delay}ms, transform 0.7s cubic-bezier(0.16,1,0.3,1) ${delay}ms`,
        willChange: "opacity, transform",
      }}
    >
      {children}
    </Tag>
  );
}
