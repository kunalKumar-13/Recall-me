"use client";

// Section 1 — Memory OS window. A dark, faithful screenshot of the
// launcher rendered in HTML: chrome + search + 3-column body
// (sidebar / results / preview).

import * as React from "react";
import { useReveal } from "./hooks";
import { Search, DocIcon, Arrow } from "./icons";

export function MemoryOSWindow() {
  const headRef = useReveal<HTMLDivElement>();
  const winRef = useReveal<HTMLDivElement>(0.15);
  return (
    <section id="v2-window" className="v2-section" style={{ position: "relative" }}>
      <div
        style={{
          position: "absolute",
          inset: 0,
          background:
            "radial-gradient(ellipse 50% 40% at 50% 30%, rgba(139,127,227,0.10), transparent 60%)",
        }}
      />
      <div className="v2-section-wrap">
        <div
          ref={headRef}
          className="reveal"
          style={{
            textAlign: "center",
            marginBottom: 56,
            maxWidth: 820,
            marginLeft: "auto",
            marginRight: "auto",
          }}
        >
          <div className="v2-eyebrow" style={{ justifyContent: "center", marginBottom: 18 }}>
            01 — The launcher
          </div>
          <h2 className="v2-section-title">
            A memory OS<br />
            <span style={{ color: "var(--muted)" }}>for your laptop.</span>
          </h2>
          <p
            className="v2-section-sub"
            style={{ marginLeft: "auto", marginRight: "auto" }}
          >
            Press ⌃ Space anywhere. Empty input shows resumable work first. Type a fragment and the day before reopens in order.
          </p>
        </div>

        <div
          ref={winRef}
          className="reveal"
          style={{ ["--delay" as never]: "120ms", maxWidth: 1180, margin: "0 auto" }}
        >
          <LauncherWindow />
        </div>
      </div>
    </section>
  );
}

function LauncherWindow() {
  return (
    <div
      style={{
        borderRadius: 18,
        overflow: "hidden",
        border: "1px solid var(--hairline-strong)",
        background: "linear-gradient(180deg, #14141C 0%, #07070A 100%)",
        boxShadow:
          "0 1px 0 rgba(255,255,255,0.04) inset, " +
          "0 60px 120px -40px rgba(0,0,0,0.8), " +
          "0 0 100px -20px rgba(139,127,227,0.30)",
      }}
    >
      {/* chrome */}
      <div
        style={{
          height: 38,
          display: "flex",
          alignItems: "center",
          padding: "0 16px",
          borderBottom: "1px solid var(--hairline)",
          background: "rgba(255,255,255,0.02)",
        }}
      >
        <div style={{ display: "flex", gap: 7 }}>
          <span style={{ width: 11, height: 11, borderRadius: "50%", background: "#FF5F57" }} />
          <span style={{ width: 11, height: 11, borderRadius: "50%", background: "#FEBC2E" }} />
          <span style={{ width: 11, height: 11, borderRadius: "50%", background: "#28C840" }} />
        </div>
        <div
          style={{
            flex: 1,
            textAlign: "center",
            fontFamily: "var(--font-mono)",
            fontSize: 11,
            color: "var(--faint)",
            letterSpacing: "0.04em",
          }}
        >
          recall · launcher
        </div>
        <div style={{ width: 33 }} />
      </div>

      {/* search bar */}
      <div
        style={{
          display: "flex",
          alignItems: "center",
          padding: "14px 20px",
          gap: 14,
          borderBottom: "1px solid var(--hairline)",
        }}
      >
        <span style={{ color: "var(--muted)", display: "flex" }}><Search size={16} /></span>
        <span style={{ fontSize: 15.5, color: "var(--text)", letterSpacing: "-0.005em", flex: 1 }}>
          that healthcare startup idea from last winter
        </span>
        <span
          style={{
            display: "inline-block",
            width: 1.5,
            height: 16,
            background: "var(--primary)",
            animation: "v2-caret 1s steps(2) infinite",
          }}
        />
        <span
          style={{
            fontFamily: "var(--font-mono)",
            fontSize: 11,
            color: "var(--muted)",
            padding: "3px 7px",
            border: "1px solid var(--hairline-strong)",
            borderRadius: 6,
            letterSpacing: "0.03em",
          }}
        >
          ⌃ Space
        </span>
      </div>

      {/* body */}
      <div style={{ display: "grid", gridTemplateColumns: "170px 1fr 1fr", minHeight: 420 }}>
        <Sidebar />
        <ResultsColumn />
        <PreviewColumn />
      </div>
    </div>
  );
}

function Sidebar() {
  const rows: Array<{ label: string; active?: boolean; icon: React.ReactNode }> = [
    { label: "Search", icon: <Search size={13} />, active: true },
    {
      label: "Memories",
      icon: (
        <svg width="13" height="13" viewBox="0 0 14 14" fill="none">
          <circle cx="7" cy="7" r="5" stroke="currentColor" strokeWidth={1.4} fill="none" />
        </svg>
      ),
    },
    {
      label: "Digest",
      icon: (
        <svg width="13" height="13" viewBox="0 0 14 14" fill="none">
          <path d="M3 4h8M3 7h6M3 10h8" stroke="currentColor" strokeWidth={1.4} strokeLinecap="round" />
        </svg>
      ),
    },
    {
      label: "Graph",
      icon: (
        <svg width="13" height="13" viewBox="0 0 14 14" fill="none">
          <circle cx="7" cy="3" r="1.5" stroke="currentColor" strokeWidth={1.4} fill="none" />
          <circle cx="3" cy="11" r="1.5" stroke="currentColor" strokeWidth={1.4} fill="none" />
          <circle cx="11" cy="11" r="1.5" stroke="currentColor" strokeWidth={1.4} fill="none" />
          <path d="M6.2 4l-2.4 5.6M7.8 4l2.4 5.6M4.5 11h5" stroke="currentColor" strokeWidth={1.4} strokeLinecap="round" />
        </svg>
      ),
    },
    {
      label: "Settings",
      icon: (
        <svg width="13" height="13" viewBox="0 0 14 14" fill="none">
          <circle cx="7" cy="7" r="1.6" stroke="currentColor" strokeWidth={1.4} fill="none" />
          <path d="M7 1.5v1.6M7 10.9v1.6M12.5 7h-1.6M3.1 7H1.5" stroke="currentColor" strokeWidth={1.4} strokeLinecap="round" />
        </svg>
      ),
    },
  ];
  return (
    <div
      style={{
        padding: "14px 10px",
        borderRight: "1px solid var(--hairline)",
        background: "rgba(255,255,255,0.015)",
        display: "flex",
        flexDirection: "column",
        gap: 2,
      }}
    >
      {rows.map((s, i) => (
        <div
          key={i}
          style={{
            display: "flex",
            alignItems: "center",
            gap: 10,
            padding: "8px 10px",
            borderRadius: 8,
            fontSize: 13,
            fontWeight: s.active ? 500 : 450,
            color: s.active ? "var(--accent)" : "var(--text-2)",
            background: s.active ? "rgba(139,127,227,0.10)" : "transparent",
            position: "relative",
          }}
        >
          {s.active && (
            <span
              style={{
                position: "absolute",
                left: 0,
                top: 8,
                bottom: 8,
                width: 2.5,
                borderRadius: 2,
                background: "var(--primary)",
              }}
            />
          )}
          <span style={{ color: s.active ? "var(--primary)" : "var(--muted)", display: "flex" }}>
            {s.icon}
          </span>
          {s.label}
        </div>
      ))}
    </div>
  );
}

function ResultsColumn() {
  const rows = [
    { title: "Healthcare Startup Pitch", meta: "pitch_healthcare_v3.pdf · Jan 12, 2024", score: 98, selected: true },
    { title: "User Research Notes",      meta: "research_interviews.md · Jan 10, 2024", score: 92 },
    { title: "MVP Technical Plan",       meta: "technical_plan_v2.md · Jan 8, 2024",    score: 91 },
    { title: "Competitor Analysis",      meta: "analysis_competitors.xlsx · Dec 26, 2023", score: 87 },
  ];
  return (
    <div style={{ padding: "16px 18px 18px", borderRight: "1px solid var(--hairline)" }}>
      <div
        style={{
          fontFamily: "var(--font-mono)",
          fontSize: 10.5,
          color: "var(--faint)",
          letterSpacing: "0.14em",
          textTransform: "uppercase",
          marginBottom: 14,
        }}
      >
        Top results
      </div>
      {rows.map((r, i) => (
        <DarkResultRow key={i} {...r} />
      ))}
      <div
        style={{
          marginTop: 14,
          padding: "8px 0",
          fontSize: 12,
          color: "var(--accent)",
          fontWeight: 500,
          letterSpacing: "-0.005em",
          display: "inline-flex",
          alignItems: "center",
          gap: 6,
          cursor: "pointer",
        }}
      >
        See 24 more results <Arrow size={11} />
      </div>
    </div>
  );
}

function DarkResultRow({
  title,
  meta,
  score,
  selected,
}: { title: string; meta: string; score: number; selected?: boolean }) {
  return (
    <div
      style={{
        display: "flex",
        alignItems: "center",
        gap: 12,
        padding: "12px 12px",
        borderRadius: 10,
        background: selected ? "rgba(139,127,227,0.10)" : "transparent",
        border: "1px solid " + (selected ? "rgba(139,127,227,0.25)" : "transparent"),
        marginBottom: 6,
      }}
    >
      <span
        style={{
          width: 30,
          height: 30,
          borderRadius: 7,
          background: selected ? "rgba(139,127,227,0.20)" : "rgba(255,255,255,0.03)",
          border: "1px solid " + (selected ? "rgba(139,127,227,0.32)" : "var(--hairline)"),
          color: selected ? "var(--accent)" : "var(--muted)",
          display: "inline-flex",
          alignItems: "center",
          justifyContent: "center",
          flexShrink: 0,
        }}
      >
        <DocIcon size={13} />
      </span>
      <div style={{ flex: 1, minWidth: 0 }}>
        <div
          style={{
            fontSize: 13.5,
            fontWeight: 500,
            letterSpacing: "-0.008em",
            color: "var(--text)",
            marginBottom: 3,
            whiteSpace: "nowrap",
            overflow: "hidden",
            textOverflow: "ellipsis",
          }}
        >
          {title}
        </div>
        <div
          style={{
            fontFamily: "var(--font-mono)",
            fontSize: 10.5,
            color: "var(--faint)",
            letterSpacing: "0.01em",
            whiteSpace: "nowrap",
            overflow: "hidden",
            textOverflow: "ellipsis",
          }}
        >
          {meta}
        </div>
      </div>
      <span
        style={{
          fontFamily: "var(--font-mono)",
          fontSize: 11,
          fontWeight: 500,
          color: selected ? "var(--accent)" : "var(--muted)",
          letterSpacing: "0.02em",
        }}
      >
        {score}%
      </span>
    </div>
  );
}

function PreviewColumn() {
  return (
    <div style={{ padding: "16px 20px 18px" }}>
      <div
        style={{
          fontFamily: "var(--font-mono)",
          fontSize: 10.5,
          color: "var(--faint)",
          letterSpacing: "0.14em",
          textTransform: "uppercase",
          marginBottom: 14,
        }}
      >
        Preview
      </div>
      <div
        style={{
          display: "inline-flex",
          alignItems: "center",
          gap: 8,
          padding: "4px 8px",
          background: "rgba(229,80,80,0.10)",
          border: "1px solid rgba(229,80,80,0.25)",
          borderRadius: 6,
          fontFamily: "var(--font-mono)",
          fontSize: 10.5,
          color: "#E58080",
          letterSpacing: "0.04em",
          marginBottom: 14,
        }}
      >
        <span
          style={{
            fontSize: 9,
            padding: "1px 4px",
            background: "#E15050",
            color: "#fff",
            borderRadius: 3,
            fontWeight: 600,
            letterSpacing: "0.08em",
          }}
        >
          PDF
        </span>
        pitch_healthcare_v3.pdf
      </div>
      <div
        style={{
          fontSize: 17,
          fontWeight: 500,
          color: "var(--text)",
          letterSpacing: "-0.018em",
          marginBottom: 6,
        }}
      >
        Healthcare Startup Pitch
      </div>
      <div
        style={{
          fontFamily: "var(--font-mono)",
          fontSize: 11,
          color: "var(--faint)",
          letterSpacing: "0.02em",
          marginBottom: 16,
        }}
      >
        ~/work/healthcare/pitch_healthcare_v3.pdf
      </div>

      <div
        style={{
          fontFamily: "var(--font-mono)",
          fontSize: 10.5,
          color: "var(--primary)",
          letterSpacing: "0.14em",
          textTransform: "uppercase",
          marginBottom: 8,
        }}
      >
        Excerpt
      </div>
      <div style={{ fontSize: 13.5, color: "var(--text-2)", lineHeight: 1.6, marginBottom: 18 }}>
        Our vision is to build AI agents that{" "}
        <mark
          style={{
            background: "rgba(139,127,227,0.22)",
            color: "var(--white)",
            padding: "1px 4px",
            borderRadius: 3,
          }}
        >
          assist healthcare teams
        </mark>{" "}
        by triaging patient queries, summarizing history, and routing to the right specialist…
      </div>

      <div
        style={{
          fontFamily: "var(--font-mono)",
          fontSize: 10.5,
          color: "var(--faint)",
          letterSpacing: "0.14em",
          textTransform: "uppercase",
          marginBottom: 10,
        }}
      >
        Related memories
      </div>
      <ul
        style={{
          listStyle: "none",
          padding: 0,
          margin: 0,
          display: "flex",
          flexDirection: "column",
          gap: 8,
        }}
      >
        {[
          "AI agent evaluation metrics",
          "Patient triage flow discussion",
          "Insurance verification logic",
        ].map((t, i) => (
          <li
            key={i}
            style={{
              display: "flex",
              alignItems: "center",
              gap: 8,
              fontSize: 12.5,
              color: "var(--text-2)",
            }}
          >
            <span
              style={{ width: 5, height: 5, borderRadius: "50%", background: "var(--primary)" }}
            />
            {t}
          </li>
        ))}
      </ul>
    </div>
  );
}
