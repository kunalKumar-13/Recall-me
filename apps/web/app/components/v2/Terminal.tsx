"use client";

import { useEffect, useRef } from "react";
import { Section, SectionHead, Words } from "../../lib/reveal";

const POOL: Array<[string, string]> = [
  ["visit", "github.com/tokio-rs/tokio — Scheduler internals"],
  ["search", 'google.com — "exponential backoff jitter"'],
  ["chat", "chatgpt.com — WebSocket reconnect strategy"],
  ["visit", "developer.mozilla.org — WebSocket.close()"],
  ["open", "~/dev/relay/src/socket.rs"],
  ["visit", "news.ycombinator.com — Show HN thread"],
  ["chat", "claude.ai — tighten the seed narrative"],
  ["search", 'kagi.com — "tauri tray icon macos"'],
  ["visit", "docs.rs/tokio — time::interval"],
  ["open", "~/decks/seed-v4.key"],
  ["search", 'duckduckgo.com — "designer portfolios 2026"'],
  ["visit", "linear.app — RECALL-142 restore choreography"],
  ["chat", "gemini.google.com — summarize retry papers"],
  ["visit", "stripe.com/docs — usage records"],
  ["open", "~/notes/hiring-scorecard.md"],
];

export function Terminal() {
  const view = useRef<HTMLDivElement>(null);
  useEffect(() => {
    const el = view.current;
    if (!el) return;
    let t = new Date();
    let i = 0;
    const MAX = 30;
    const pad = (s: string, w: number) => s.padEnd(w, " ");
    const line = () => {
      t = new Date(t.getTime() + 2000 + Math.random() * 6000);
      const hh = String(t.getHours()).padStart(2, "0");
      const mm = String(t.getMinutes()).padStart(2, "0");
      const ss = String(t.getSeconds()).padStart(2, "0");
      const e = POOL[i % POOL.length];
      i += 1;
      const d = document.createElement("div");
      const b = document.createElement("b");
      b.textContent = pad(e[0], 6);
      d.append(`${hh}:${mm}:${ss}  `, b, ` ${e[1]}`);
      el.appendChild(d);
      while (el.children.length > MAX) el.firstChild?.remove();
      el.scrollTop = el.scrollHeight;
    };
    for (let k = 0; k < 9; k += 1) line();
    if (matchMedia("(prefers-reduced-motion: reduce)").matches) return;
    let vis = true;
    const io = new IntersectionObserver((es) => {
      vis = es[0].isIntersecting;
    });
    io.observe(el);
    const iv = setInterval(() => {
      if (vis) line();
    }, 1100);
    return () => {
      clearInterval(iv);
      io.disconnect();
    };
  }, []);
  return (
    <Section id="live" className="sec">
      <div className="wrap sechead tight">
        <SectionHead index="04" eyebrow="While you work, it writes">
          <h2>
            <Words>Your memory, </Words>
            <em>
              <Words>one line at a time.</Words>
            </em>
          </h2>
        </SectionHead>
        <div className="term rise">
          <div className="tbar">
            <span>tail -f ~/.recall/events/2026-06-25.jsonl</span>
            <span className="tag">demo stream</span>
          </div>
          <div className="tick-view" ref={view} />
        </div>
      </div>
    </Section>
  );
}
