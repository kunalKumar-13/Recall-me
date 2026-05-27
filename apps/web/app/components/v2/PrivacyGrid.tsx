"use client";

// Section 5 — Local-first privacy. 4 trust blocks with code proofs.

import * as React from "react";
import { useReveal } from "./hooks";
import { CloudOff, Export, EyeOff, Shield } from "./icons";

type Block = {
  icon: React.ReactNode;
  title: string;
  sub: string;
  proof: string;
};

const blocks: Block[] = [
  {
    icon: <Shield size={20} />,
    title: "Local only",
    sub: "Every event, embedding, and index lives in ~/.recall/ as JSONL. Auditable with cat.",
    proof: "cat ~/.recall/events/*.jsonl",
  },
  {
    icon: <CloudOff size={20} />,
    title: "No cloud",
    sub: "No accounts, no servers, no sync. The HTTP API binds to loopback. Nothing else.",
    proof: "lsof -i :4545  →  127.0.0.1",
  },
  {
    icon: <EyeOff size={20} />,
    title: "No telemetry",
    sub: "No analytics, no error reporting, no model-update pings. ChromaDB telemetry off at boot.",
    proof: "no outbound calls after install",
  },
  {
    icon: <Export size={20} />,
    title: "Export anytime",
    sub: "JSONL is the export. Pipe it into anything. Delete the folder and Recall is gone.",
    proof: "rm -rf ~/.recall  →  full reset",
  },
];

export function PrivacyGrid() {
  const headRef = useReveal<HTMLDivElement>();
  return (
    <section
      id="v2-privacy"
      className="v2-section"
      style={{
        position: "relative",
        borderTop: "1px solid var(--hairline)",
        borderBottom: "1px solid var(--hairline)",
      }}
    >
      <div
        style={{
          position: "absolute",
          inset: 0,
          opacity: 0.55,
          backgroundImage:
            "linear-gradient(rgba(255,255,255,0.04) 1px, transparent 1px)," +
            "linear-gradient(90deg, rgba(255,255,255,0.04) 1px, transparent 1px)",
          backgroundSize: "56px 56px",
          maskImage: "radial-gradient(ellipse 75% 70% at 50% 50%, #000 30%, transparent 92%)",
          WebkitMaskImage: "radial-gradient(ellipse 75% 70% at 50% 50%, #000 30%, transparent 92%)",
        }}
      />
      <div
        style={{
          position: "absolute",
          inset: 0,
          background:
            "radial-gradient(ellipse 40% 40% at 50% 50%, rgba(139,127,227,0.10), transparent 70%)",
        }}
      />

      <div className="v2-section-wrap">
        <div
          ref={headRef}
          className="reveal"
          style={{
            textAlign: "center",
            marginBottom: 64,
            maxWidth: 880,
            marginLeft: "auto",
            marginRight: "auto",
          }}
        >
          <div className="v2-eyebrow" style={{ justifyContent: "center", marginBottom: 18 }}>
            05 — Trust ledger
          </div>
          <h2 className="v2-section-title">
            A continuity layer is only worth using<br />
            <span className="v2-serif-italic">if it never leaves your machine.</span>
          </h2>
          <p className="v2-section-sub" style={{ marginLeft: "auto", marginRight: "auto" }}>
            We picked the harder side. Everything Recall sees stays on disk, in plain text — auditable with cat, deletable with rm.
          </p>
        </div>

        <div
          className="v2-privacy-grid"
          style={{
            display: "grid",
            maxWidth: 1280,
            margin: "0 auto",
            border: "1px solid var(--hairline)",
            borderRadius: 18,
            overflow: "hidden",
            background: "rgba(17,17,24,0.65)",
            backdropFilter: "blur(14px)",
            WebkitBackdropFilter: "blur(14px)",
          }}
        >
          {blocks.map((b, i) => (
            <PrivacyBlock key={i} {...b} index={i} last={i === blocks.length - 1} />
          ))}
        </div>
      </div>
    </section>
  );
}

function PrivacyBlock({
  icon,
  title,
  sub,
  proof,
  index,
  last,
}: Block & { index: number; last: boolean }) {
  const ref = useReveal<HTMLDivElement>(0.2);
  return (
    <div
      ref={ref}
      className="reveal"
      style={{
        ["--delay" as never]: `${index * 80}ms`,
        padding: "32px 26px 28px",
        borderRight: last ? "none" : "1px solid var(--hairline)",
        display: "flex",
        flexDirection: "column",
        minHeight: 280,
      }}
    >
      <div
        style={{
          width: 40,
          height: 40,
          borderRadius: 11,
          background: "rgba(139,127,227,0.10)",
          border: "1px solid rgba(139,127,227,0.22)",
          color: "var(--accent)",
          display: "inline-flex",
          alignItems: "center",
          justifyContent: "center",
          marginBottom: 18,
          boxShadow: "0 0 24px -8px rgba(139,127,227,0.40)",
        }}
      >
        {icon}
      </div>
      <div style={{ fontSize: 18, fontWeight: 500, letterSpacing: "-0.016em", marginBottom: 8 }}>
        {title}
      </div>
      <div
        style={{
          fontSize: 13.5,
          color: "var(--muted)",
          lineHeight: 1.55,
          letterSpacing: "-0.005em",
          marginBottom: 18,
          flex: 1,
        }}
      >
        {sub}
      </div>
      <div
        style={{
          fontFamily: "var(--font-mono)",
          fontSize: 11,
          color: "var(--text-2)",
          padding: "8px 10px",
          background: "rgba(0,0,0,0.4)",
          border: "1px solid var(--hairline)",
          borderRadius: 6,
          letterSpacing: "0.01em",
          whiteSpace: "nowrap",
          overflow: "hidden",
          textOverflow: "ellipsis",
        }}
      >
        {proof}
      </div>
    </div>
  );
}
