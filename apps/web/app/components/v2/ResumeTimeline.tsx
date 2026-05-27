"use client";

// Section 6 — Resume timeline. Four-beat vertical timeline with
// progress rail. Final beat is the Recall recovery moment.

import * as React from "react";
import { useReveal, useScrollProgress } from "./hooks";

type Beat = {
  when: string;
  kind: string;
  title: string;
  desc: string;
  terminal?: boolean;
};

const beats: Beat[] = [
  {
    when: "Mon · 09:14",
    kind: "CONTEXT",
    title: "Started the retry investigation",
    desc: "opened socket.io PR #482 · skimmed retry-handler.ts",
  },
  {
    when: "Mon · 14:36",
    kind: "WORK",
    title: "Patched the websocket retry handler",
    desc: "3 commits · 11 files touched",
  },
  {
    when: "Tue",
    kind: "AWAY",
    title: "Sidetracked into the healthcare proposal",
    desc: "~/notes/proposal-v3.md · 4 hours",
  },
  {
    when: "Wed · ⌃ Space",
    kind: "RESUME",
    title: "Two keystrokes, the whole investigation reopens.",
    desc: "2 files · 2 tabs · 1 chat · in order",
    terminal: true,
  },
];

export function ResumeTimeline() {
  const sectionRef = React.useRef<HTMLElement>(null);
  const headRef = useReveal<HTMLDivElement>();
  const progress = useScrollProgress(sectionRef);

  return (
    <section
      id="v2-timeline"
      ref={sectionRef}
      className="v2-section"
      style={{ position: "relative", minHeight: "140vh" }}
    >
      <div className="v2-section-wrap">
        <div ref={headRef} className="reveal" style={{ marginBottom: 80, maxWidth: 880 }}>
          <div className="v2-eyebrow" style={{ marginBottom: 18 }}>06 — Resume timeline</div>
          <h2 className="v2-section-title">
            You don&apos;t remember filenames.<br />
            <span className="v2-serif-italic">You remember the day.</span>
          </h2>
          <p className="v2-section-sub">
            Recall stitches related work into resumable sessions so picking up an investigation feels like opening a chapter, not crawling through history.
          </p>
        </div>

        <div style={{ position: "relative", maxWidth: 920, marginLeft: 32 }}>
          <div
            className="v2-tl-rail"
            style={{ ["--progress" as never]: `${Math.max(6, progress * 100)}%` }}
          />
          <div style={{ display: "flex", flexDirection: "column", gap: 70, paddingLeft: 110 }}>
            {beats.map((b, i) => {
              const dotProgress = (i + 0.4) / beats.length;
              const active = progress >= dotProgress - 0.1;
              return <ResumeBeat key={i} {...b} active={active} index={i} />;
            })}
          </div>
        </div>
      </div>
    </section>
  );
}

function ResumeBeat({
  when,
  kind,
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
            ? "0 0 16px var(--primary), 0 0 36px rgba(139,127,227,0.4)"
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
        <span>{when}</span>
        <span style={{ width: 3, height: 3, borderRadius: "50%", background: "currentColor" }} />
        <span style={{ color: terminal ? "var(--accent)" : "inherit" }}>{kind}</span>
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
            Two keystrokes, the whole{" "}
            <span className="v2-serif-italic">investigation reopens.</span>
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
