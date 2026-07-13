"use client";

import { useEffect, useRef } from "react";
import { Section } from "../../lib/reveal";

/**
 * The numbers band — hairline-celled, giant tabular numerals, every
 * figure honest and enforced by the smoke suite (the budgets are
 * assertions, not aspirations).
 */
const STATS = [
  { n: 100, prefix: "<", suffix: "ms", label: "to recall your work", sub: "smoke-tested budget" },
  { n: 7, suffix: "", label: "engine layers", sub: "strictly composing upward" },
  { n: 0, suffix: "", label: "bytes to any cloud", sub: "loopback is the boundary" },
  { n: 1, suffix: "", label: "folder holds it all", sub: "~/.recall — yours to delete" },
];

export function Stats() {
  const root = useRef<HTMLDivElement>(null);
  useEffect(() => {
    const el = root.current;
    if (!el || matchMedia("(prefers-reduced-motion: reduce)").matches) return;
    const io = new IntersectionObserver(
      (es) => {
        if (!es[0].isIntersecting) return;
        io.disconnect();
        el.querySelectorAll<HTMLElement>("[data-count]").forEach((s) => {
          const target = parseInt(s.dataset.count || "0", 10);
          let t0: number | null = null;
          const fr = (ts: number) => {
            if (t0 === null) t0 = ts;
            const p = Math.min(1, (ts - t0) / 900);
            s.textContent = String(Math.round(target * (1 - Math.pow(1 - p, 3))));
            if (p < 1) requestAnimationFrame(fr);
          };
          requestAnimationFrame(fr);
        });
      },
      { threshold: 0.4 },
    );
    io.observe(el);
    return () => io.disconnect();
  }, []);
  return (
    <Section className="statsband" as="div">
      <div className="statscells rise" ref={root}>
        {STATS.map((s) => (
          <div className="scell" key={s.label}>
            <div className="sl mono">{s.label}</div>
            <div className="sn">
              {s.prefix}
              <span data-count={s.n}>{s.n}</span>
              <span className="ssuf">{s.suffix}</span>
            </div>
            <div className="ss">{s.sub}</div>
          </div>
        ))}
      </div>
    </Section>
  );
}
