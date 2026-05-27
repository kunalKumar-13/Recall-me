"use client";

// Section 7 — Search surface. Two-col with bullet rail on the left
// and a dark grouped result list on the right.

import * as React from "react";
import { useReveal } from "./hooks";
import { Chat, Code, DocIcon, Search, Tab } from "./icons";

export function SearchSurface() {
  const headRef = useReveal<HTMLDivElement>();
  const mockRef = useReveal<HTMLDivElement>(0.15);
  return (
    <section id="v2-search-surface" className="v2-section" style={{ position: "relative" }}>
      <div
        style={{
          position: "absolute",
          inset: 0,
          background:
            "radial-gradient(ellipse 50% 40% at 20% 30%, rgba(139,127,227,0.10), transparent 70%)",
        }}
      />
      <div
        className="v2-section-wrap v2-two-col"
        style={{
          display: "grid",
          gridTemplateColumns: "1fr 1.05fr",
          gap: 60,
          alignItems: "center",
        }}
      >
        <div ref={headRef} className="reveal">
          <div className="v2-eyebrow" style={{ marginBottom: 18 }}>07 — Search surface</div>
          <h2 className="v2-section-title">
            Half a thought<br />
            <span className="v2-serif-italic">is enough.</span>
          </h2>
          <p className="v2-section-sub">
            Episodic moments, sessions, and micro-contexts in one ranked bundle. Sub-100ms on 10K events. Type a fragment — Recall understands meaning, not filenames.
          </p>

          <ul
            style={{
              listStyle: "none",
              padding: 0,
              margin: "32px 0 0",
              display: "flex",
              flexDirection: "column",
              gap: 14,
            }}
          >
            {[
              { label: "Investigations", hint: "sessions of unfinished work" },
              { label: "Files",          hint: "PDFs, docs, code, notes" },
              { label: "Returns",        hint: "past chats and threads" },
              { label: "Events",         hint: "tabs, searches, and visits" },
            ].map((r, i) => (
              <li
                key={i}
                style={{
                  display: "flex",
                  alignItems: "center",
                  gap: 14,
                  padding: "10px 14px",
                  border: "1px solid var(--hairline)",
                  borderRadius: 10,
                  background: "rgba(255,255,255,0.02)",
                }}
              >
                <span
                  style={{
                    width: 8,
                    height: 8,
                    borderRadius: "50%",
                    background: "var(--primary)",
                    boxShadow: "0 0 10px var(--primary)",
                    flexShrink: 0,
                  }}
                />
                <span
                  style={{
                    fontSize: 14.5,
                    fontWeight: 500,
                    color: "var(--text)",
                    letterSpacing: "-0.008em",
                  }}
                >
                  {r.label}
                </span>
                <span
                  style={{
                    fontFamily: "var(--font-mono)",
                    fontSize: 11.5,
                    color: "var(--faint)",
                    letterSpacing: "0.04em",
                    marginLeft: "auto",
                  }}
                >
                  {r.hint}
                </span>
              </li>
            ))}
          </ul>
        </div>

        <div ref={mockRef} className="reveal" style={{ ["--delay" as never]: "120ms" }}>
          <SearchMock />
        </div>
      </div>
    </section>
  );
}

function SearchMock() {
  return (
    <div
      style={{
        borderRadius: 18,
        overflow: "hidden",
        border: "1px solid var(--hairline-strong)",
        background: "linear-gradient(180deg, #14141C 0%, #07070A 100%)",
        boxShadow:
          "0 1px 0 rgba(255,255,255,0.04) inset, " +
          "0 40px 80px -30px rgba(0,0,0,0.7), " +
          "0 0 60px -16px rgba(139,127,227,0.30)",
      }}
    >
      <div
        style={{
          display: "flex",
          alignItems: "center",
          padding: "16px 20px",
          gap: 14,
          borderBottom: "1px solid var(--hairline)",
        }}
      >
        <span style={{ color: "var(--primary)", display: "flex" }}><Search size={17} /></span>
        <span style={{ fontSize: 16, color: "var(--text)", letterSpacing: "-0.005em", flex: 1 }}>
          rlhf reward shaping
        </span>
        <span
          style={{
            display: "inline-block",
            width: 1.5,
            height: 18,
            background: "var(--primary)",
            animation: "v2-caret 1s steps(2) infinite",
          }}
        />
        <span
          style={{
            fontFamily: "var(--font-mono)",
            fontSize: 10.5,
            color: "var(--faint)",
            letterSpacing: "0.04em",
          }}
        >
          11 results
        </span>
      </div>

      <div style={{ padding: "12px 14px" }}>
        <SrGroup label="Investigations">
          <SrRow icon={<Code size={13} />} title="WebSocket retry debugging" meta="2d · 5 events" score={98} selected />
        </SrGroup>
        <SrGroup label="Files">
          <SrRow icon={<DocIcon size={13} />} title="proposal_healthcare_v3.pdf" meta="~/notes · Jan 12" score={94} />
          <SrRow icon={<DocIcon size={13} />} title="rlhf-eval-protocol.md" meta="~/research · 4d" score={91} />
        </SrGroup>
        <SrGroup label="Returns">
          <SrRow icon={<Chat size={13} />} title="ChatGPT — reward shaping basics" meta="4 visits · 3d" score={89} />
        </SrGroup>
        <SrGroup label="Events">
          <SrRow icon={<Tab size={13} />} title="arxiv.org/2305.18290" meta="tab · 1d" score={84} />
        </SrGroup>
      </div>

      <div
        style={{
          padding: "12px 22px",
          borderTop: "1px solid var(--hairline)",
          display: "flex",
          justifyContent: "space-between",
          fontFamily: "var(--font-mono)",
          fontSize: 10.5,
          color: "var(--dim)",
          letterSpacing: "0.06em",
        }}
      >
        <span>11 RESULTS</span>
        <span>54 MS · LOCAL</span>
      </div>
    </div>
  );
}

function SrGroup({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <div style={{ marginBottom: 6 }}>
      <div
        style={{
          fontFamily: "var(--font-mono)",
          fontSize: 10.5,
          fontWeight: 500,
          color: "var(--faint)",
          letterSpacing: "0.14em",
          textTransform: "uppercase",
          padding: "6px 12px 4px",
        }}
      >
        {label}
      </div>
      {children}
    </div>
  );
}

function SrRow({
  icon,
  title,
  meta,
  score,
  selected,
}: {
  icon: React.ReactNode;
  title: string;
  meta: string;
  score: number;
  selected?: boolean;
}) {
  return (
    <div
      style={{
        display: "flex",
        alignItems: "center",
        gap: 12,
        padding: "10px 12px",
        borderRadius: 9,
        background: selected ? "rgba(139,127,227,0.10)" : "transparent",
        border: "1px solid " + (selected ? "rgba(139,127,227,0.25)" : "transparent"),
        position: "relative",
      }}
    >
      {selected && (
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
      <span style={{ color: selected ? "var(--accent)" : "var(--muted)", display: "flex", width: 14, justifyContent: "center" }}>
        {icon}
      </span>
      <span
        style={{
          flex: 1,
          minWidth: 0,
          fontSize: 13.5,
          color: "var(--text)",
          fontWeight: selected ? 500 : 400,
          letterSpacing: "-0.005em",
          whiteSpace: "nowrap",
          overflow: "hidden",
          textOverflow: "ellipsis",
        }}
      >
        {title}
      </span>
      <span
        style={{
          fontFamily: "var(--font-mono)",
          fontSize: 10.5,
          color: "var(--dim)",
          letterSpacing: "0.04em",
        }}
      >
        {meta}
      </span>
      <span
        style={{
          fontFamily: "var(--font-mono)",
          fontSize: 10.5,
          color: selected ? "var(--accent)" : "var(--faint)",
          fontWeight: 500,
          letterSpacing: "0.02em",
          minWidth: 26,
          textAlign: "right",
        }}
      >
        {score}
      </span>
    </div>
  );
}
