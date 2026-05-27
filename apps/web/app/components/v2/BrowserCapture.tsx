"use client";

// Section 4 — Browser capture. Two-col with copy on the left and
// a mock browser window with the extension popup overlaid on top-right.

import * as React from "react";
import { useReveal } from "./hooks";
import { Ext, Github, Search } from "./icons";
import { V2_LINKS } from "./links";

export function BrowserCapture() {
  const headRef = useReveal<HTMLDivElement>();
  const winRef = useReveal<HTMLDivElement>(0.15);
  return (
    <section className="v2-section" style={{ position: "relative" }}>
      <div
        className="v2-section-wrap v2-two-col"
        style={{
          display: "grid",
          gridTemplateColumns: "0.95fr 1.05fr",
          gap: 60,
          alignItems: "center",
        }}
      >
        <div ref={headRef} className="reveal">
          <div className="v2-eyebrow" style={{ marginBottom: 18 }}>04 — Browser capture</div>
          <h2 className="v2-section-title">
            A 200-line<br />
            <span className="v2-serif-italic">browser memory.</span>
          </h2>
          <p className="v2-section-sub">
            Tabs, search queries, ChatGPT sessions, Notion pages — captured on completion. Posted only to 127.0.0.1. No analytics. Audit it with{" "}
            <code
              style={{
                fontFamily: "var(--font-mono)",
                fontSize: 14,
                color: "var(--accent)",
                background: "rgba(139,127,227,0.10)",
                padding: "2px 6px",
                borderRadius: 4,
              }}
            >
              cat ~/.recall/events/*.jsonl
            </code>
            .
          </p>
          <div style={{ display: "flex", gap: 12, marginTop: 30, flexWrap: "wrap" }}>
            <a href={V2_LINKS.extension} className="v2-btn-primary">
              <Ext size={14} /> Install extension
            </a>
            <a
              href={`${V2_LINKS.github}/tree/main/apps/extension`}
              target="_blank"
              rel="noopener noreferrer"
              className="v2-btn-text"
            >
              <Github size={15} /> Read the source
            </a>
          </div>
        </div>

        <div ref={winRef} className="reveal" style={{ ["--delay" as never]: "120ms" }}>
          <BrowserMock />
        </div>
      </div>
    </section>
  );
}

function BrowserMock() {
  return (
    <div
      style={{
        position: "relative",
        borderRadius: 16,
        overflow: "hidden",
        border: "1px solid var(--hairline-strong)",
        background: "linear-gradient(180deg, #16161E 0%, #0B0B12 100%)",
        boxShadow:
          "0 1px 0 rgba(255,255,255,0.04) inset, 0 40px 80px -30px rgba(0,0,0,0.7), 0 0 60px -16px rgba(139,127,227,0.20)",
      }}
    >
      <div style={{ borderBottom: "1px solid var(--hairline)" }}>
        <div style={{ height: 38, display: "flex", alignItems: "center", padding: "0 14px", gap: 12 }}>
          <div style={{ display: "flex", gap: 7 }}>
            <span style={{ width: 11, height: 11, borderRadius: "50%", background: "#FF5F57" }} />
            <span style={{ width: 11, height: 11, borderRadius: "50%", background: "#FEBC2E" }} />
            <span style={{ width: 11, height: 11, borderRadius: "50%", background: "#28C840" }} />
          </div>
          <div style={{ display: "flex", gap: 4 }}>
            <TabPill>chatgpt.com</TabPill>
            <TabPill active>github.com/socket.io</TabPill>
            <TabPill>arxiv.org</TabPill>
          </div>
          <div style={{ flex: 1 }} />
          <div
            style={{
              padding: "5px 9px",
              borderRadius: 6,
              background: "rgba(139,127,227,0.18)",
              border: "1px solid rgba(139,127,227,0.35)",
              fontFamily: "var(--font-mono)",
              fontSize: 10.5,
              color: "var(--accent)",
              letterSpacing: "0.06em",
              display: "inline-flex",
              alignItems: "center",
              gap: 6,
            }}
          >
            <span
              style={{
                width: 5,
                height: 5,
                borderRadius: "50%",
                background: "#5DBE89",
                boxShadow: "0 0 8px #5DBE89",
              }}
            />
            RECALL
          </div>
        </div>
        <div
          style={{
            height: 36,
            padding: "0 14px",
            display: "flex",
            alignItems: "center",
            gap: 8,
            background: "rgba(255,255,255,0.02)",
          }}
        >
          <span style={{ color: "var(--muted)", display: "flex" }}><Search size={12} /></span>
          <span
            style={{
              fontFamily: "var(--font-mono)",
              fontSize: 11,
              color: "var(--text-2)",
            }}
          >
            github.com/socket.io · PR #482 — websocket retry handler
          </span>
        </div>
      </div>

      <div
        style={{
          height: 380,
          position: "relative",
          background: "linear-gradient(180deg, #0E0E15 0%, #07070A 100%)",
        }}
      >
        <div style={{ padding: "22px 28px 0" }}>
          <div
            style={{
              height: 18,
              width: "38%",
              background: "rgba(255,255,255,0.06)",
              borderRadius: 4,
              marginBottom: 14,
            }}
          />
          <div style={{ display: "flex", flexDirection: "column", gap: 6 }}>
            {[80, 70, 76, 64, 72, 58, 80, 66].map((w, i) => (
              <div
                key={i}
                style={{
                  height: 4,
                  width: `${w}%`,
                  background: "rgba(255,255,255,0.04)",
                  borderRadius: 3,
                }}
              />
            ))}
          </div>
        </div>

        <ExtensionPopup />
      </div>
    </div>
  );
}

function TabPill({
  children,
  active,
}: {
  children: React.ReactNode;
  active?: boolean;
}) {
  return (
    <span
      style={{
        padding: "4px 10px",
        borderRadius: 6,
        fontSize: 11,
        color: active ? "var(--text)" : "var(--muted)",
        background: active ? "rgba(139,127,227,0.12)" : "rgba(255,255,255,0.04)",
        border: active ? "1px solid rgba(139,127,227,0.22)" : undefined,
      }}
    >
      {children}
    </span>
  );
}

function ExtensionPopup() {
  return (
    <div
      style={{
        position: "absolute",
        top: 14,
        right: 14,
        width: 300,
        background: "linear-gradient(180deg, #16161E 0%, #0E0E15 100%)",
        border: "1px solid rgba(139,127,227,0.28)",
        borderRadius: 12,
        padding: 16,
        boxShadow:
          "0 30px 60px -20px rgba(0,0,0,0.7), 0 0 60px -10px rgba(139,127,227,0.40)",
      }}
    >
      <div style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 12 }}>
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none">
          <circle cx="12" cy="12" r="9" stroke="rgba(255,255,255,0.30)" strokeWidth={1.3} />
          <path d="M12 3a9 9 0 017.7 4.4" stroke="#D7D1FF" strokeWidth={1.7} strokeLinecap="round" />
          <circle cx="12" cy="3" r="1.6" fill="#D7D1FF" />
        </svg>
        <span style={{ fontSize: 13, fontWeight: 500 }}>Recall</span>
        <div style={{ flex: 1 }} />
        <span
          style={{
            fontFamily: "var(--font-mono)",
            fontSize: 10,
            color: "#5DBE89",
            display: "inline-flex",
            alignItems: "center",
            gap: 6,
          }}
        >
          <span
            style={{
              width: 5,
              height: 5,
              borderRadius: "50%",
              background: "#5DBE89",
              boxShadow: "0 0 8px #5DBE89",
            }}
          />
          CONNECTED
        </span>
      </div>

      <div style={{ fontSize: 26, fontWeight: 500, letterSpacing: "-0.02em", marginBottom: 2 }}>
        2,148
      </div>
      <div
        style={{
          fontFamily: "var(--font-mono)",
          fontSize: 10.5,
          color: "var(--faint)",
          letterSpacing: "0.06em",
          marginBottom: 14,
        }}
      >
        EVENTS CAPTURED · LAST 30 DAYS
      </div>

      <div style={{ display: "flex", flexDirection: "column", gap: 6 }}>
        {[
          { l: "tabs", n: "1,204" },
          { l: "searches", n: "612" },
          { l: "chats", n: "218" },
          { l: "pdfs", n: "114" },
        ].map((r, i) => (
          <div
            key={i}
            style={{
              display: "flex",
              justifyContent: "space-between",
              alignItems: "center",
              padding: "6px 10px",
              background: "rgba(255,255,255,0.02)",
              border: "1px solid var(--hairline)",
              borderRadius: 6,
              fontSize: 12,
              color: "var(--text-2)",
            }}
          >
            <span>{r.l}</span>
            <span style={{ fontFamily: "var(--font-mono)", color: "var(--muted)" }}>{r.n}</span>
          </div>
        ))}
      </div>

      <div
        style={{
          marginTop: 12,
          padding: "8px 10px",
          background: "rgba(0,0,0,0.4)",
          border: "1px solid var(--hairline)",
          borderRadius: 6,
          fontFamily: "var(--font-mono)",
          fontSize: 10.5,
          color: "var(--dim)",
          letterSpacing: "0.02em",
        }}
      >
        host: 127.0.0.1:4545 · lo only
      </div>
    </div>
  );
}
