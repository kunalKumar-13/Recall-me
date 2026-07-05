"use client";

import { useEffect, useRef } from "react";
import { Section } from "../../lib/reveal";

const STATS = [
  { n: 7, suffix: "", label: "engine layers, strictly upward" },
  { n: 0, suffix: "", label: "bytes sent to any cloud" },
  { n: 100, prefix: "<", suffix: "ms", label: "to recall your work" },
  { n: 1, suffix: "", label: "folder — delete it, it's gone" },
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
    <Section className="stats" as="div">
      <div className="row rise" ref={root}>
        {STATS.map((s) => (
          <div className="stat" key={s.label}>
            <div className="n">
              {s.prefix}
              <span data-count={s.n}>{s.n}</span>
              {s.suffix}
            </div>
            <div className="l">{s.label}</div>
          </div>
        ))}
      </div>
    </Section>
  );
}
