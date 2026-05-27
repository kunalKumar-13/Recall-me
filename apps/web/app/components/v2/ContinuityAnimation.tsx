"use client";

// Section 2 — Continuity timeline. One workday rendered as a
// scrubable vertical rail with 4 beats; the last beat is the
// Recall recovery moment.

import * as React from "react";
import { useReveal, useScrollProgress } from "./hooks";
import { Chat, Code, DocIcon, Search } from "./icons";

type Beat = {
  time: string;
  surface: string;
  icon: React.ReactNode;
  title: string;
  desc: string;
  terminal?: boolean;
};

const beats: Beat[] = [
  {
    time: "08:42",
    surface: "ChatGPT",
    icon: <Chat size={13} />,
    title: "Read about RLHF reward shaping",
    desc: "4 messages · arxiv skim · two notes",
  },
  {
    time: "14:18",
    surface: "GitHub",
    icon: <Code size={13} />,
    title: "Patched the websocket retry handler",
    desc: "3 commits · PR #482 · 11 files",
  },
  {
    time: "22:07",
    surface: "Notes",
    icon: <DocIcon size={13} />,
    title: "Drafted the healthcare proposal",
    desc: "~/notes/proposal-v3.md",
  },
  {
    time: "⌃ Space",
    surface: "Recall",
    icon: <Search size={13} />,
    title: "Everything reopens in the right order.",
    desc: "2 files · 2 tabs · 1 chat",
    terminal: true,
  },
];

export function ContinuityAnimation() {
  const sectionRef = React.useRef<HTMLElement>(null);
  const headRef = useReveal<HTMLDivElement>();
  const progress = useScrollProgress(sectionRef);

  return (
    <section
      id="v2-continuity"
      ref={sectionRef}
      className="v2-section"
      style={{ position: "relative", paddingTop: 140, paddingBottom: 140 }}
    >
      <div
        style={{
          position: "absolute",
          inset: 0,
          background:
            "radial-gradient(ellipse 30% 60% at 10% 50%, rgba(139,127,227,0.10), transparent 70%)",
        }}
      />

      <div className="v2-section-wrap">
        <div ref={headRef} className="reveal" style={{ marginBottom: 70, maxWidth: 880 }}>
          <div className="v2-eyebrow" style={{ marginBottom: 18 }}>02 — Continuity</div>
          <h2 className="v2-section-title">
            One day on your machine,<br />
            <span style={{ color: "var(--muted)" }}>still warm when you return.</span>
          </h2>
        </div>

        <div style={{ position: "relative", maxWidth: 920, marginLeft: 32 }}>
          <div
            className="v2-tl-rail"
            style={{ ["--progress" as never]: `${Math.max(8, progress * 100)}%` }}
          />
          <div style={{ display: "flex", flexDirection: "column", gap: 70, paddingLeft: 110 }}>
            {beats.map((b, i) => {
              const dotProgress = (i + 0.4) / beats.length;
              const active = progress >= dotProgress - 0.1;
              return <BeatRow key={i} {...b} active={active} index={i} />;
            })}
          </div>
        </div>
      </div>
    </section>
  );
}

function BeatRow({
  time,
  surface,
  icon,
  title,
  desc,
  terminal,
  active,
  index,
}: Beat & { active: boolean; index: number }) {
  const ref = useReveal<HTMLDivElement>(0.25);
  return (
    <div
      ref={ref}
      className="reveal"
      style={{ ["--delay" as never]: `${index * 60}ms`, position: "relative" }}
    >
      <div
        style={{
          position: "absolute",
          left: -78,
          top: 6,
          width: 13,
          height: 13,
          borderRadius: "50%",
          background: active ? "var(--primary)" : "#1B1B26",
          border: `1.5px solid ${active ? "var(--primary)" : "var(--hairline-strong)"}`,
          boxShadow: active
            ? "0 0 16px var(--primary), 0 0 36px rgba(215,209,255,0.18)"
            : "none",
          transition: "all 240ms ease",
        }}
      />
      <div
        style={{
          fontFamily: "var(--font-mono)",
          fontSize: 11.5,
          color: active ? "var(--primary)" : "var(--faint)",
          letterSpacing: "0.14em",
          textTransform: "uppercase",
          marginBottom: 10,
          transition: "color 240ms ease",
          display: "inline-flex",
          alignItems: "center",
          gap: 10,
        }}
      >
        <span>{time}</span>
        <span style={{ width: 3, height: 3, borderRadius: "50%", background: "currentColor" }} />
        <span style={{ color: terminal ? "var(--accent)" : "inherit" }}>{surface}</span>
        <span style={{ color: "var(--muted)", display: "flex" }}>{icon}</span>
      </div>
      <div
        style={{
          fontSize: terminal ? 32 : 24,
          fontWeight: 500,
          lineHeight: 1.18,
          letterSpacing: "-0.022em",
          marginBottom: 10,
          color: terminal ? "var(--text)" : "var(--text-2)",
          maxWidth: 640,
        }}
      >
        {terminal ? (
          <>
            Everything reopens <span className="v2-serif-italic">in the right order.</span>
          </>
        ) : (
          title
        )}
      </div>
      <div
        style={{
          fontFamily: "var(--font-mono)",
          fontSize: 12,
          color: "var(--faint)",
          letterSpacing: "0.02em",
        }}
      >
        {desc}
      </div>
    </div>
  );
}
