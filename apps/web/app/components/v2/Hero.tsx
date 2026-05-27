"use client";

// Recall landing v2 — Hero. Left column: eyebrow + 3-line headline
// with serif italic "unfinished" + sub + 4-button row + trust strip.
// Right column: 3 floating glass cards on an orbit-ring backdrop
// with mouse-depth parallax + 3D drift animation.

import * as React from "react";
import { HeroCard, type HeroCardKind } from "./HeroCard";
import { useMouseDepth } from "./hooks";
import { Download, Play, Github, ArrowUp } from "./icons";
import { V2_LINKS, V2_ANCHORS } from "./links";

type FloatingCard = {
  x: number;
  y: number;
  w: number;
  depth: number;
  drift: "a" | "b" | "c";
  rotate: number;
  accent?: boolean;
  title: string;
  kind: HeroCardKind;
  source: string;
  tag: string;
};

const cards: FloatingCard[] = [
  {
    x: -14, y: -120, w: 280, depth: 1.0, drift: "a", rotate: -3, accent: true,
    title: "WebSocket retry debugging",
    kind: "thread",
    source: "~/code/socket.io/retry.ts",
    tag: "investigation · 2d",
  },
  {
    x: 130, y: 40, w: 290, depth: 0.85, drift: "b", rotate: 2,
    title: "Healthcare proposal v3",
    kind: "doc",
    source: "~/notes/pitch.md · Tue",
    tag: "document",
  },
  {
    x: -40, y: 175, w: 270, depth: 0.7, drift: "c", rotate: -2,
    title: "RLHF reward shaping research",
    kind: "research",
    source: "arxiv · 2305.18290 · 4 visits",
    tag: "research",
  },
];

export function Hero({ onOpenDemo }: { onOpenDemo?: () => void }) {
  const mouse = useMouseDepth(1);

  return (
    <section
      id="v2-hero"
      style={{
        position: "relative",
        minHeight: "100vh",
        paddingTop: 130,
        overflow: "hidden",
      }}
    >
      <div
        style={{
          position: "absolute",
          inset: 0,
          pointerEvents: "none",
          background:
            "radial-gradient(ellipse 55% 50% at 70% 30%, rgba(139,127,227,0.22), transparent 60%)," +
            "radial-gradient(ellipse 50% 50% at 25% 90%, rgba(215,209,255,0.08), transparent 60%)",
        }}
      />
      <div
        style={{
          position: "absolute",
          top: 240,
          right: "-10%",
          width: 540,
          height: 540,
          borderRadius: "50%",
          background: "radial-gradient(circle, rgba(139,127,227,0.25), transparent 65%)",
          filter: "blur(40px)",
          pointerEvents: "none",
        }}
      />

      <div
        className="v2-section-wrap v2-hero-grid"
        style={{
          display: "grid",
          gridTemplateColumns: "minmax(0, 1.05fr) minmax(0, 1fr)",
          gap: 56,
          alignItems: "center",
          padding: "40px 32px 80px",
        }}
      >
        {/* LEFT */}
        <div style={{ maxWidth: 640, position: "relative", zIndex: 2 }}>
          <div className="reveal in" style={{ marginBottom: 24 }}>
            <span className="v2-eyebrow">a continuity layer for unfinished thought</span>
          </div>

          <h1
            className="reveal in"
            style={{
              fontSize: "clamp(52px, 7vw, 100px)",
              fontWeight: 500,
              letterSpacing: "-0.036em",
              lineHeight: 0.98,
              margin: "0 0 28px",
              color: "var(--text)",
              ["--delay" as never]: "60ms",
            }}
          >
            <span style={{ display: "block" }}>Recall notices</span>
            <span
              className="v2-serif-italic"
              style={{
                display: "block",
                fontSize: "1.04em",
                lineHeight: 1.05,
                paddingTop: "0.04em",
                paddingBottom: "0.14em",
              }}
            >
              unfinished
            </span>
            <span style={{ display: "block" }}>work.</span>
          </h1>

          <p
            className="reveal in"
            style={{
              fontSize: 19,
              color: "var(--text-2)",
              letterSpacing: "-0.005em",
              lineHeight: 1.55,
              maxWidth: 480,
              margin: "0 0 36px",
              ["--delay" as never]: "120ms",
            }}
          >
            Recall remembers work across tabs, documents, chats — and reopens it the moment you return, with the right files, tabs, and conversations already in place.
          </p>

          <div
            className="reveal in"
            style={{
              display: "flex",
              flexWrap: "wrap",
              gap: 12,
              alignItems: "center",
              marginBottom: 44,
              ["--delay" as never]: "180ms",
            }}
          >
            <a href={V2_LINKS.download} download className="v2-btn-primary">
              <Download size={13} /> Get alpha
            </a>
            <button type="button" className="v2-btn-ghost" onClick={onOpenDemo}>
              <Play size={11} /> Watch demo
            </button>
            <a
              href={V2_LINKS.github}
              target="_blank"
              rel="noopener noreferrer"
              className="v2-btn-text"
            >
              <Github size={15} /> GitHub
            </a>
            <a href={V2_LINKS.docs} className="v2-btn-text">
              Docs <ArrowUp size={11} />
            </a>
          </div>

          <div
            className="reveal in"
            style={{
              display: "flex",
              flexWrap: "wrap",
              gap: 22,
              fontFamily: "var(--font-mono)",
              fontSize: 11.5,
              color: "var(--faint)",
              letterSpacing: "0.06em",
              ["--delay" as never]: "240ms",
            }}
          >
            {["LOCAL ONLY", "NO CLOUD", "MIT LICENSE"].map((t) => (
              <span key={t} style={{ display: "inline-flex", alignItems: "center", gap: 7 }}>
                <span
                  style={{
                    width: 5,
                    height: 5,
                    borderRadius: "50%",
                    background: "var(--primary)",
                    boxShadow: "0 0 8px var(--primary)",
                  }}
                />
                {t}
              </span>
            ))}
          </div>
        </div>

        {/* RIGHT — orbit + floating cards */}
        <div
          className="v2-hero-cards"
          style={{ position: "relative", height: 580, perspective: 1600 }}
        >
          <div
            style={{
              position: "absolute",
              left: "50%",
              top: "50%",
              width: 520,
              height: 520,
              transform: "translate(-50%, -50%) rotateX(58deg)",
              borderRadius: "50%",
              border: "1px dashed rgba(215,209,255,0.16)",
              pointerEvents: "none",
            }}
          />
          <div
            style={{
              position: "absolute",
              left: "50%",
              top: "50%",
              transform: "translate(-50%, -50%)",
              width: 240,
              height: 240,
              borderRadius: "50%",
              background: "radial-gradient(circle, rgba(139,127,227,0.32), transparent 65%)",
              filter: "blur(20px)",
              pointerEvents: "none",
            }}
          />
          <div
            style={{
              position: "absolute",
              left: "50%",
              top: "50%",
              transform: "translate(-50%, -50%)",
              width: 10,
              height: 10,
              borderRadius: "50%",
              background: "var(--accent)",
              boxShadow: "0 0 18px var(--accent), 0 0 36px var(--primary)",
              animation: "v2-pulse-soft 2.6s ease-in-out infinite",
            }}
          />

          {cards.map((c, i) => {
            const px = mouse.x * 16 * c.depth;
            const py = mouse.y * 12 * c.depth;
            const rx = mouse.y * -3 * c.depth;
            const ry = mouse.x * 4 * c.depth;
            return (
              <div
                key={i}
                style={{
                  position: "absolute",
                  left: "50%",
                  top: "50%",
                  width: c.w,
                  transform: `translate(-50%, -50%) translate3d(${c.x + px}px, ${c.y + py}px, 0) rotateX(${rx}deg) rotateY(${ry}deg) rotate(${c.rotate}deg)`,
                  transition: "transform 80ms linear",
                  transformStyle: "preserve-3d",
                  animation: `v2-drift-${c.drift} ${14 + i * 2}s ease-in-out infinite`,
                  willChange: "transform",
                  zIndex: c.accent ? 5 : Math.round(c.depth * 4),
                }}
              >
                <HeroCard {...c} />
              </div>
            );
          })}
        </div>
      </div>

      {/* scroll indicator */}
      <div
        style={{
          position: "absolute",
          bottom: 24,
          left: "50%",
          transform: "translateX(-50%)",
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          gap: 8,
          fontFamily: "var(--font-mono)",
          fontSize: 10.5,
          color: "var(--faint)",
          letterSpacing: "0.18em",
        }}
      >
        <span>SCROLL</span>
        <span
          style={{
            width: 1,
            height: 32,
            background: "linear-gradient(180deg, var(--faint), transparent)",
          }}
        />
      </div>
    </section>
  );
}
