"use client";

import { useEffect, useState } from "react";
import { LINKS } from "../../lib/links";
import { Mark } from "../../lib/Mark";
import { Section } from "../../lib/reveal";

const COLS = [
  {
    label: "Product",
    links: [
      { t: "How it works", h: "#how" },
      { t: "Capabilities", h: "#features" },
      { t: "Extension", h: "#extension" },
      { t: "Download", h: "#download" },
    ],
  },
  {
    label: "Engine",
    links: [
      { t: "Architecture", h: "#engine" },
      { t: "Seven layers", h: "#layers" },
      { t: "Console", h: "/console" },
      { t: "Docs", h: LINKS.docs, ext: true },
    ],
  },
  {
    label: "Trust",
    links: [
      { t: "Privacy", h: "#trust" },
      { t: "FAQ", h: "#faq" },
      { t: "GitHub", h: LINKS.github, ext: true },
      { t: "Issues", h: LINKS.issues, ext: true },
    ],
  },
] as const;

/** Link columns, a truthful status line, then the giant outlined
 *  wordmark — the site keeps time the way the product keeps memory:
 *  quietly, on your machine. */
export function SiteFooter() {
  const [time, setTime] = useState("");
  useEffect(() => {
    const fmt = () =>
      new Date().toLocaleTimeString([], {
        hour: "2-digit",
        minute: "2-digit",
      });
    setTime(fmt());
    const t = setInterval(() => setTime(fmt()), 30_000);
    return () => clearInterval(t);
  }, []);
  return (
    <footer>
      <div className="fcols">
        <div className="fabout">
          <div className="brand">
            <Mark />
            Recall
          </div>
          <p>
            A local-first continuity OS. It reconstructs what you were
            working on and hands it back — from your machine, never a cloud.
          </p>
          <div className="fstatus mono">
            <i /> engine · 127.0.0.1:4545 · local only
          </div>
        </div>
        {COLS.map((c) => (
          <div className="fcol" key={c.label}>
            <div className="fhead mono">{c.label}</div>
            {c.links.map((l) => (
              <a
                key={l.t}
                href={l.h}
                {...("ext" in l && l.ext
                  ? { target: "_blank", rel: "noreferrer" }
                  : {})}
              >
                {l.t}
              </a>
            ))}
          </div>
        ))}
      </div>
      <div className="frow">
        <span>
          © {new Date().getFullYear()} Recall — plain files, one folder,
          yours{time ? ` · your time ${time}` : ""}
        </span>
        <nav className="fnav">
          <a href={LINKS.github} target="_blank" rel="noreferrer">
            GitHub
          </a>
          <a href="#download">Download</a>
        </nav>
      </div>
      {/* The wordmark evolves the way memory does: the thread stitches
          through the outline and the letters fill in behind it. */}
      <Section as="div" className="fmarkwrap">
        <div className="fmark" aria-hidden="true">
          <svg
            className="fthread"
            viewBox="0 0 1200 260"
            preserveAspectRatio="none"
          >
            <path
              className="fth"
              pathLength={1}
              d="M -10 208 C 120 246, 180 96, 320 128 S 560 236, 720 160 S 980 60, 1090 118 S 1170 96, 1196 88"
            />
          </svg>
          <div className="word">
            {"Recall".split("").map((ch, i) => (
              <span
                className="ch"
                key={`${ch}-${i}`}
                style={{ transitionDelay: `${(0.45 + i * 0.34).toFixed(2)}s` }}
              >
                {ch}
              </span>
            ))}
            <i>.</i>
          </div>
        </div>
      </Section>
    </footer>
  );
}
