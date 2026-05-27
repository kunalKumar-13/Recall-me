"use client";

// Section 9 — Final CTA. Pulsing dot field + headline + three CTAs.

import * as React from "react";
import { useReveal } from "./hooks";
import { ArrowUp, Download, Ext } from "./icons";
import { V2_LINKS } from "./links";

export function FinalCTA() {
  const ref = useReveal<HTMLDivElement>();
  return (
    <section
      id="v2-final"
      className="v2-section"
      style={{
        position: "relative",
        padding: "160px 32px 140px",
        borderTop: "1px solid var(--hairline)",
        overflow: "hidden",
      }}
    >
      <div
        style={{
          position: "absolute",
          inset: 0,
          background:
            "radial-gradient(ellipse 50% 60% at 50% 50%, rgba(139,127,227,0.20), transparent 60%)",
        }}
      />

      <BackgroundPulses />

      <div
        ref={ref}
        className="reveal v2-section-wrap"
        style={{ position: "relative", textAlign: "center", maxWidth: 980 }}
      >
        <div className="v2-eyebrow" style={{ justifyContent: "center", marginBottom: 24 }}>
          09 — v0.1.0 public alpha
        </div>

        <h2
          style={{
            fontSize: "clamp(56px, 8vw, 124px)",
            fontWeight: 500,
            letterSpacing: "-0.04em",
            lineHeight: 0.96,
            margin: "0 0 32px",
          }}
        >
          Remember <span className="v2-serif-italic">less.</span><br />
          Continue more.
        </h2>

        <p
          style={{
            fontSize: 17,
            color: "var(--muted)",
            maxWidth: 540,
            margin: "0 auto 40px",
            lineHeight: 1.55,
            letterSpacing: "-0.005em",
          }}
        >
          Recall is a single binary. macOS, Linux, and Windows. The download is ~38 MB and the install is one command.
        </p>

        <div
          style={{
            display: "flex",
            gap: 12,
            justifyContent: "center",
            flexWrap: "wrap",
            marginBottom: 28,
          }}
        >
          <a
            href={V2_LINKS.download}
            download
            className="v2-btn-primary"
            style={{ height: 56, padding: "0 26px", fontSize: 15.5 }}
          >
            <Download size={15} /> Download alpha
          </a>
          <a
            href={V2_LINKS.extension}
            className="v2-btn-ghost"
            style={{ height: 56, padding: "0 22px", fontSize: 15.5 }}
          >
            <Ext size={15} /> Install extension
          </a>
          <a
            href={V2_LINKS.docs}
            className="v2-btn-ghost"
            style={{ height: 56, padding: "0 22px", fontSize: 15.5 }}
          >
            Read the docs <ArrowUp size={13} />
          </a>
        </div>

        <div
          style={{
            fontFamily: "var(--font-mono)",
            fontSize: 12,
            color: "var(--faint)",
            letterSpacing: "0.06em",
          }}
        >
          macOS 13+ · Windows 11 · Linux (X11/Wayland) · MIT licensed
        </div>
      </div>
    </section>
  );
}

function BackgroundPulses() {
  return (
    <svg
      width="100%"
      height="100%"
      viewBox="0 0 1400 600"
      preserveAspectRatio="xMidYMid slice"
      style={{ position: "absolute", inset: 0, pointerEvents: "none", opacity: 0.5 }}
    >
      <defs>
        <radialGradient id="v2-bg-glow" cx="50%" cy="50%">
          <stop offset="0%" stopColor="#A78BFA" stopOpacity={0.7} />
          <stop offset="100%" stopColor="#A78BFA" stopOpacity={0} />
        </radialGradient>
      </defs>
      {[[160, 120], [300, 220], [110, 400], [260, 520], [1100, 160], [1240, 280], [1160, 420], [1300, 520]].map(
        ([x, y], i) => (
          <g
            key={i}
            style={{
              animation: `v2-pulse-soft ${3 + i * 0.4}s ease-in-out infinite`,
              transformOrigin: `${x}px ${y}px`,
            }}
          >
            <circle cx={x} cy={y} r={14} fill="url(#v2-bg-glow)" />
            <circle cx={x} cy={y} r={2.5} fill="#A78BFA" opacity={0.7} />
          </g>
        ),
      )}
    </svg>
  );
}
