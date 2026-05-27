"use client";

// Section 3 — Recovery pipeline. Auto-cycling 4-stage path
// (search → detect → recover → resume) once in view.

import * as React from "react";
import { useReveal, useInView } from "./hooks";
import { Check, Search } from "./icons";

const stages = [
  { label: "search", desc: "a fragment is enough" },
  { label: "detect", desc: "pattern across 14-day window" },
  { label: "recover", desc: "files · tabs · chats · in order" },
  { label: "resume", desc: "one keystroke, then back to work" },
];

export function RecoveryFlow() {
  const [stageRef, seen] = useInView<HTMLElement>(0.3);
  const [stage, setStage] = React.useState(0);
  const headRef = useReveal<HTMLDivElement>();

  React.useEffect(() => {
    if (!seen) return;
    setStage(0);
    let i = 0;
    const t = setInterval(() => {
      i = (i + 1) % 4;
      setStage(i);
    }, 2200);
    return () => clearInterval(t);
  }, [seen]);

  return (
    <section ref={stageRef} className="v2-section" style={{ position: "relative" }}>
      <div
        style={{
          position: "absolute",
          inset: 0,
          background:
            "radial-gradient(ellipse 40% 50% at 50% 50%, rgba(139,127,227,0.12), transparent 65%)",
        }}
      />

      <div className="v2-section-wrap">
        <div
          ref={headRef}
          className="reveal"
          style={{
            textAlign: "center",
            marginBottom: 60,
            maxWidth: 840,
            marginLeft: "auto",
            marginRight: "auto",
          }}
        >
          <div className="v2-eyebrow" style={{ justifyContent: "center", marginBottom: 18 }}>
            03 — Recovery
          </div>
          <h2 className="v2-section-title">
            Search. <span className="v2-serif-italic">Detect.</span> Recover.{" "}
            <span className="v2-serif-italic">Resume.</span>
          </h2>
          <p className="v2-section-sub" style={{ marginLeft: "auto", marginRight: "auto" }}>
            The recovery pipeline runs on local embeddings and your filesystem. Nothing leaves the machine.
          </p>
        </div>

        <RecoveryCanvas stage={stage} />

        <div
          style={{
            marginTop: 36,
            display: "grid",
            gridTemplateColumns: "repeat(4, 1fr)",
            gap: 14,
            maxWidth: 1180,
            marginLeft: "auto",
            marginRight: "auto",
          }}
        >
          {stages.map((s, i) => {
            const active = i === stage;
            return (
              <div
                key={i}
                style={{
                  padding: "20px 18px",
                  borderRadius: 14,
                  background: active
                    ? "linear-gradient(180deg, rgba(139,127,227,0.16), rgba(139,127,227,0.04))"
                    : "rgba(255,255,255,0.02)",
                  border: "1px solid " + (active ? "rgba(139,127,227,0.32)" : "var(--hairline)"),
                  position: "relative",
                  overflow: "hidden",
                  transition: "all 360ms cubic-bezier(.2,.7,.2,1)",
                }}
              >
                <div
                  style={{
                    position: "absolute",
                    top: 0,
                    left: 0,
                    right: 0,
                    height: 1.5,
                    background: "var(--hairline)",
                  }}
                >
                  <div
                    style={{
                      width: active ? "100%" : "0%",
                      height: "100%",
                      background: "linear-gradient(90deg, var(--primary), var(--accent))",
                      boxShadow: "0 0 8px var(--primary)",
                      transition: "width 2100ms linear",
                    }}
                  />
                </div>
                <div
                  style={{
                    fontFamily: "var(--font-mono)",
                    fontSize: 10.5,
                    fontWeight: 500,
                    color: active ? "var(--primary)" : "var(--faint)",
                    letterSpacing: "0.16em",
                    textTransform: "uppercase",
                    marginBottom: 8,
                    transition: "color 240ms ease",
                  }}
                >
                  0{i + 1} · {s.label}
                </div>
                <div
                  style={{
                    fontSize: 14,
                    color: active ? "var(--text)" : "var(--muted)",
                    letterSpacing: "-0.005em",
                  }}
                >
                  {s.desc}
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </section>
  );
}

function RecoveryCanvas({ stage }: { stage: number }) {
  return (
    <div
      style={{
        borderRadius: 18,
        overflow: "hidden",
        border: "1px solid var(--hairline-strong)",
        background: "linear-gradient(180deg, #14141C 0%, #07070A 100%)",
        boxShadow:
          "0 1px 0 rgba(255,255,255,0.04) inset, 0 40px 80px -30px rgba(0,0,0,0.7), 0 0 60px -16px rgba(139,127,227,0.30)",
        height: 400,
        position: "relative",
        maxWidth: 1180,
        margin: "0 auto",
      }}
    >
      <svg
        width="100%"
        height="100%"
        viewBox="0 0 1180 400"
        preserveAspectRatio="none"
        style={{ position: "absolute", inset: 0 }}
      >
        <defs>
          <linearGradient id="v2-rc-grad" x1="0" y1="0" x2="1" y2="0">
            <stop offset="0%" stopColor="#D7D1FF" stopOpacity="0.0" />
            <stop offset="20%" stopColor="#D7D1FF" stopOpacity="0.7" />
            <stop offset="100%" stopColor="#8B7FE3" stopOpacity="0.7" />
          </linearGradient>
        </defs>
        <path
          d="M120 200 C 360 60, 600 340, 840 200 S 1080 60, 1140 200"
          fill="none"
          stroke="url(#v2-rc-grad)"
          strokeWidth={2}
          strokeDasharray="6 8"
          style={{ animation: "v2-dash-flow 6s linear infinite" }}
        />
      </svg>

      {[
        { x: 120, y: 200 },
        { x: 480, y: 200 },
        { x: 840, y: 200 },
        { x: 1140, y: 200 },
      ].map((d, i) => {
        const active = i === stage;
        return (
          <div
            key={i}
            style={{
              position: "absolute",
              left: d.x,
              top: d.y,
              transform: "translate(-50%, -50%)",
              zIndex: 2,
            }}
          >
            <div
              style={{
                width: active ? 18 : 13,
                height: active ? 18 : 13,
                borderRadius: "50%",
                background: active ? "var(--primary)" : "#1B1B26",
                border: "2px solid " + (active ? "var(--accent)" : "var(--hairline-strong)"),
                boxShadow: active
                  ? "0 0 0 6px rgba(139,127,227,0.18), 0 0 24px var(--primary)"
                  : "none",
                transition: "all 360ms cubic-bezier(.2,.7,.2,1)",
              }}
            />
          </div>
        );
      })}

      <div
        style={{
          position: "absolute",
          left: "50%",
          top: "50%",
          transform: "translate(-50%, -50%)",
          width: 420,
        }}
      >
        <RecoveryStage stage={stage} />
      </div>
    </div>
  );
}

function RecoveryStage({ stage }: { stage: number }) {
  if (stage === 0) {
    return (
      <div
        style={{
          padding: "14px 18px",
          background: "linear-gradient(180deg, #15131F, #0A0810)",
          border: "1px solid var(--hairline-strong)",
          borderRadius: 12,
          boxShadow: "0 0 60px -20px rgba(139,127,227,0.6)",
        }}
      >
        <div style={{ display: "flex", alignItems: "center", gap: 12, color: "var(--primary)" }}>
          <Search size={16} />
          <span style={{ color: "var(--text)", fontSize: 16 }}>websocket retry</span>
          <span
            style={{
              display: "inline-block",
              width: 1.5,
              height: 16,
              background: "var(--primary)",
              animation: "v2-caret 1s steps(2) infinite",
            }}
          />
        </div>
      </div>
    );
  }
  if (stage === 1) {
    return (
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
        {[0, 1, 2, 3, 4].map((i) => (
          <div key={i} style={{ position: "relative" }}>
            <div
              style={{
                width: 14,
                height: 14,
                borderRadius: "50%",
                background: "var(--primary)",
                boxShadow: "0 0 14px var(--primary)",
                animation: `v2-pulse-soft ${1.6 + i * 0.2}s ease-in-out infinite`,
              }}
            />
            <div
              style={{
                position: "absolute",
                inset: -8,
                borderRadius: "50%",
                border: "1px solid var(--primary)",
                opacity: 0,
                animation: `v2-pulse-ring ${1.6 + i * 0.2}s ease-out infinite`,
              }}
            />
          </div>
        ))}
      </div>
    );
  }
  if (stage === 2) {
    return (
      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr 1fr", gap: 8 }}>
        {["◆ retry-handler.ts", "◇ proposal-v3.md", "⌘ ChatGPT — retry chat"].map((c, i) => (
          <div
            key={i}
            style={{
              padding: "12px 12px",
              background: "linear-gradient(180deg, #15131F, #0A0810)",
              border: "1px solid rgba(139,127,227,0.28)",
              borderRadius: 10,
              fontSize: 11,
              fontFamily: "var(--font-mono)",
              color: "var(--text-2)",
              boxShadow: "0 0 30px -10px rgba(139,127,227,0.40)",
            }}
          >
            {c}
          </div>
        ))}
      </div>
    );
  }
  return (
    <div style={{ textAlign: "center" }}>
      <div
        style={{
          width: 60,
          height: 60,
          margin: "0 auto 14px",
          borderRadius: "50%",
          background: "linear-gradient(135deg, #B79EFF, #8B7FE3)",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          color: "#fff",
          boxShadow: "0 0 50px rgba(139,127,227,0.7)",
        }}
      >
        <Check size={24} />
      </div>
      <div
        style={{
          fontSize: 17,
          fontWeight: 500,
          color: "var(--text)",
          letterSpacing: "-0.012em",
        }}
      >
        Restored — 2 files · 2 tabs · 1 chat
      </div>
    </div>
  );
}
