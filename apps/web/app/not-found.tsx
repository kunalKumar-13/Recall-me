"use client";

// Phase 11B — 404 screen. Same v2 dark-cinematic palette, no new
// aesthetic. Pulsing bloom mark, mono "404" microtype, serif-italic
// accent, two CTAs back to safe ground.

import * as React from "react";
import Link from "next/link";
import { Github, Mark } from "./components/v2/icons";
import { V2_LINKS } from "./components/v2/links";

export default function NotFound() {
  return (
    <div
      className="v2-root"
      style={{
        position: "relative",
        minHeight: "100vh",
        display: "flex",
        flexDirection: "column",
        background: "var(--bg)",
        color: "var(--text)",
        overflow: "hidden",
      }}
    >
      {/* atmosphere */}
      <div
        style={{
          position: "absolute",
          inset: 0,
          pointerEvents: "none",
          background:
            "radial-gradient(ellipse 55% 50% at 50% 30%, rgba(139,127,227,0.20), transparent 60%)," +
            "radial-gradient(ellipse 40% 50% at 50% 90%, rgba(215,209,255,0.06), transparent 65%)",
        }}
      />

      {/* nav bar (mini, just the brand) */}
      <header
        style={{
          position: "relative",
          padding: "20px 32px",
          display: "flex",
          alignItems: "center",
          gap: 10,
        }}
      >
        <Link
          href="/"
          style={{
            display: "inline-flex",
            alignItems: "center",
            gap: 10,
            color: "var(--text)",
            textDecoration: "none",
            fontWeight: 500,
            fontSize: 15.5,
            letterSpacing: "-0.012em",
          }}
        >
          <Mark size={20} />
          <span>Recall</span>
          <span
            style={{
              fontFamily: "var(--font-mono)",
              fontSize: 10.5,
              color: "var(--faint)",
              letterSpacing: "0.08em",
              padding: "2px 7px",
              border: "1px solid var(--hairline)",
              borderRadius: 5,
              marginLeft: 6,
            }}
          >
            v0.1 ALPHA
          </span>
        </Link>
      </header>

      {/* center stage */}
      <main
        style={{
          flex: 1,
          position: "relative",
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          justifyContent: "center",
          padding: "40px 32px 80px",
          textAlign: "center",
        }}
      >
        {/* bloom mark — same primitive as the empty launcher state */}
        <div
          style={{
            position: "relative",
            width: 96,
            height: 96,
            marginBottom: 36,
          }}
        >
          <div
            style={{
              position: "absolute",
              inset: -18,
              background:
                "radial-gradient(circle, rgba(139,127,227,0.32) 0%, transparent 65%)",
              borderRadius: "50%",
              filter: "blur(8px)",
            }}
          />
          <svg width="96" height="96" viewBox="0 0 96 96" fill="none" style={{ position: "relative" }}>
            <defs>
              <radialGradient id="v2-nf-bloom" cx="50%" cy="40%">
                <stop offset="0%"  stopColor="#FFFFFF" stopOpacity="0.95" />
                <stop offset="40%" stopColor="#C9B6FF" stopOpacity="0.9" />
                <stop offset="100%" stopColor="#6B5FCB" stopOpacity="0.5" />
              </radialGradient>
            </defs>
            <circle cx="48" cy="48" r="40" fill="none" stroke="rgba(167,139,250,0.18)" strokeWidth="1" />
            <circle cx="48" cy="48" r="28" fill="none" stroke="rgba(167,139,250,0.30)" strokeWidth="1" />
            <circle
              cx="48"
              cy="48"
              r="14"
              fill="url(#v2-nf-bloom)"
              style={{ filter: "drop-shadow(0 0 12px rgba(167,139,250,0.6))" }}
            />
            <circle cx="48" cy="48" r="4" fill="#FFFFFF" />
          </svg>
        </div>

        <div
          className="v2-eyebrow"
          style={{ justifyContent: "center", marginBottom: 22 }}
        >
          404 · this memory never landed
        </div>

        <h1
          style={{
            fontSize: "clamp(40px, 6vw, 76px)",
            fontWeight: 500,
            letterSpacing: "-0.032em",
            lineHeight: 1.02,
            margin: "0 auto 18px",
            maxWidth: 760,
          }}
        >
          We&apos;ve looked everywhere.<br />
          <span className="v2-serif-italic">No event matches this url.</span>
        </h1>

        <p
          className="v2-section-sub"
          style={{ margin: "8px auto 0", maxWidth: 540 }}
        >
          Recall captures intent on your machine, not URLs on the public web. The path you followed isn&apos;t in the index — most likely a typo, a moved doc, or a link from before the v2 launch.
        </p>

        <div
          style={{
            marginTop: 38,
            display: "flex",
            gap: 12,
            flexWrap: "wrap",
            justifyContent: "center",
          }}
        >
          <Link href="/" className="v2-btn-primary">
            ← Back to landing
          </Link>
          <Link href="/docs" className="v2-btn-ghost">
            Open the docs
          </Link>
          <a
            href={V2_LINKS.github}
            target="_blank"
            rel="noopener noreferrer"
            className="v2-btn-text"
          >
            <Github size={15} /> Browse the repo
          </a>
        </div>

        {/* mono debug line — small wink to the local-first audience */}
        <div
          style={{
            marginTop: 56,
            fontFamily: "var(--font-mono)",
            fontSize: 11.5,
            color: "var(--faint)",
            letterSpacing: "0.06em",
            display: "inline-flex",
            alignItems: "center",
            gap: 10,
            padding: "8px 14px",
            border: "1px solid var(--hairline)",
            borderRadius: 8,
            background: "rgba(255,255,255,0.02)",
          }}
        >
          <span
            style={{
              width: 6,
              height: 6,
              borderRadius: "50%",
              background: "#E15050",
              boxShadow: "0 0 8px #E15050",
            }}
          />
          GET · 404 · NO RESUMABLE WORK AT THIS PATH
        </div>
      </main>

      {/* footer microline — keep it minimal on the 404 */}
      <footer
        style={{
          position: "relative",
          padding: "24px 32px",
          borderTop: "1px solid var(--hairline)",
          display: "flex",
          justifyContent: "space-between",
          fontFamily: "var(--font-mono)",
          fontSize: 11,
          color: "var(--dim)",
          letterSpacing: "0.04em",
        }}
      >
        <span>© 2026 Recall — built for unfinished thought</span>
        <span>v0.1.0 · alpha cohort · local only</span>
      </footer>
    </div>
  );
}
