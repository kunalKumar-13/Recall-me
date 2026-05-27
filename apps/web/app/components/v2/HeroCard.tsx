// Glass hero card — used by the floating-card cluster in the Hero.
// Renders a small "investigation feel" tile: eyebrow kind + title +
// two skeleton lines + source microtext.

import * as React from "react";
import { Code, DocIcon, Research, Chat } from "./icons";

export type HeroCardKind = "thread" | "doc" | "research" | "chat";

export type HeroCardProps = {
  title: string;
  kind: HeroCardKind;
  source: string;
  tag: string;
  accent?: boolean;
};

export function HeroCard({ title, kind, source, tag, accent }: HeroCardProps) {
  const KindIcon = {
    thread:   <Code size={13} />,
    doc:      <DocIcon size={13} />,
    research: <Research size={13} />,
    chat:     <Chat size={13} />,
  }[kind];

  return (
    <div
      className="v2-glass"
      style={{
        padding: "14px 16px 14px",
        width: "100%",
        position: "relative",
        overflow: "hidden",
      }}
    >
      {accent && (
        <div
          style={{
            position: "absolute",
            left: 0,
            right: 0,
            top: 0,
            height: 1,
            background: "linear-gradient(90deg, transparent, var(--accent), transparent)",
            opacity: 0.7,
          }}
        />
      )}

      <div
        style={{
          display: "inline-flex",
          alignItems: "center",
          gap: 7,
          fontFamily: "var(--font-mono)",
          fontSize: 10,
          fontWeight: 500,
          color: accent ? "var(--accent)" : "var(--primary)",
          letterSpacing: "0.16em",
          textTransform: "uppercase",
          marginBottom: 10,
        }}
      >
        <span style={{ display: "flex" }}>{KindIcon}</span>
        {tag}
      </div>
      <div
        style={{
          fontSize: 15,
          fontWeight: 500,
          letterSpacing: "-0.012em",
          lineHeight: 1.25,
          color: "var(--white)",
          marginBottom: 10,
        }}
      >
        {title}
      </div>
      <div style={{ display: "flex", flexDirection: "column", gap: 4, marginBottom: 10 }}>
        <span style={{ height: 4, width: "82%", borderRadius: 3, background: "rgba(255,255,255,0.10)" }} />
        <span style={{ height: 4, width: "68%", borderRadius: 3, background: "rgba(255,255,255,0.06)" }} />
      </div>
      <div
        style={{
          fontFamily: "var(--font-mono)",
          fontSize: 10.5,
          color: "var(--faint)",
          letterSpacing: "0.02em",
          paddingTop: 8,
          borderTop: "1px solid rgba(255,255,255,0.06)",
          whiteSpace: "nowrap",
          overflow: "hidden",
          textOverflow: "ellipsis",
        }}
      >
        {source}
      </div>
    </div>
  );
}
