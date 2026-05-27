"use client";

// Sticky navbar with scroll-state glow. Real anchors + GitHub +
// Docs links + the "Get alpha" pill that scrolls to the final CTA.

import * as React from "react";
import { Mark, Github, ArrowUp, Arrow } from "./icons";
import { useScrolled, smoothScroll } from "./hooks";
import { V2_LINKS, V2_ANCHORS } from "./links";

export function Nav() {
  const scrolled = useScrolled(20);
  return (
    <nav className={`v2-nav ${scrolled ? "scrolled" : ""}`}>
      <a className="v2-nav-brand" href={V2_ANCHORS.hero} onClick={smoothScroll(V2_ANCHORS.hero)}>
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
      </a>

      <div className="v2-nav-links">
        <a href={V2_ANCHORS.window}     onClick={smoothScroll(V2_ANCHORS.window)}>Memory OS</a>
        <a href={V2_ANCHORS.continuity} onClick={smoothScroll(V2_ANCHORS.continuity)}>Continuity</a>
        <a href={V2_ANCHORS.privacy}    onClick={smoothScroll(V2_ANCHORS.privacy)}>Local-first</a>
        <a href={V2_ANCHORS.demo}       onClick={smoothScroll(V2_ANCHORS.demo)}>Demo</a>
        <a href={V2_LINKS.docs}>Docs <ArrowUp size={10} /></a>
      </div>

      <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
        <a
          href={V2_LINKS.github}
          target="_blank"
          rel="noopener noreferrer"
          aria-label="GitHub"
          style={{
            width: 36,
            height: 36,
            borderRadius: 10,
            border: "1px solid var(--hairline-strong)",
            background: "rgba(255,255,255,0.02)",
            color: "var(--text-2)",
            display: "inline-flex",
            alignItems: "center",
            justifyContent: "center",
            textDecoration: "none",
            transition: "background 180ms ease, color 180ms ease, border-color 180ms ease",
          }}
          onMouseEnter={(e) => {
            const t = e.currentTarget;
            t.style.background = "rgba(255,255,255,0.06)";
            t.style.color = "var(--white)";
            t.style.borderColor = "rgba(255,255,255,0.22)";
          }}
          onMouseLeave={(e) => {
            const t = e.currentTarget;
            t.style.background = "rgba(255,255,255,0.02)";
            t.style.color = "var(--text-2)";
            t.style.borderColor = "var(--hairline-strong)";
          }}
        >
          <Github size={15} />
        </a>
        <a
          href={V2_ANCHORS.final}
          onClick={smoothScroll(V2_ANCHORS.final)}
          className="v2-btn-primary"
          style={{ height: 36, padding: "0 14px", fontSize: 13 }}
        >
          Get alpha <Arrow size={12} />
        </a>
      </div>
    </nav>
  );
}
