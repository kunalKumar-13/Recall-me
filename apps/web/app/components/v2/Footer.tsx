"use client";

// Footer — brand col + 3 link cols + bottom row.

import * as React from "react";
import { ArrowUp, Mark } from "./icons";
import { smoothScroll } from "./hooks";
import { V2_ANCHORS, V2_LINKS } from "./links";

type Item = {
  label: string;
  href: string;
  ext?: boolean;
  download?: boolean;
};

export function Footer() {
  return (
    <footer className="v2-foot">
      <div className="v2-foot-grid">
        <div className="v2-foot-col">
          <a
            href={V2_ANCHORS.hero}
            onClick={smoothScroll(V2_ANCHORS.hero)}
            style={{
              display: "inline-flex",
              alignItems: "center",
              gap: 10,
              color: "var(--white)",
              textDecoration: "none",
              fontWeight: 500,
              fontSize: 16,
              letterSpacing: "-0.012em",
              padding: 0,
            }}
          >
            <Mark size={22} />
            <span>Recall</span>
          </a>
          <div
            style={{
              fontSize: 13.5,
              color: "var(--muted)",
              lineHeight: 1.55,
              maxWidth: 320,
              marginTop: 12,
            }}
          >
            A continuity layer for unfinished thought. Local-first. Open source. Small enough to read.
          </div>
          <div
            style={{
              marginTop: 22,
              display: "inline-flex",
              alignItems: "center",
              gap: 8,
              fontFamily: "var(--font-mono)",
              fontSize: 11,
              color: "var(--faint)",
              letterSpacing: "0.06em",
              padding: "6px 10px",
              background: "rgba(255,255,255,0.02)",
              border: "1px solid var(--hairline)",
              borderRadius: 6,
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
            local only · no cloud
          </div>
        </div>

        <FootCol
          title="Product"
          items={[
            { label: "Memory OS",  href: V2_ANCHORS.window },
            { label: "Continuity", href: V2_ANCHORS.continuity },
            { label: "Demo",       href: V2_ANCHORS.demo },
            { label: "Download",   href: V2_LINKS.download, download: true },
          ]}
        />
        <FootCol
          title="Engineering"
          items={[
            { label: "GitHub",    href: V2_LINKS.github,    ext: true },
            { label: "Docs",      href: V2_LINKS.docs },
            { label: "Extension", href: V2_LINKS.extension },
            { label: "Audit log", href: `${V2_LINKS.github}/blob/main/AUDIT/REPO_STABILIZATION.md`, ext: true },
          ]}
        />
        <FootCol
          title="Trust"
          items={[
            { label: "Local-first", href: V2_ANCHORS.privacy },
            { label: "Resume flow", href: V2_ANCHORS.timeline },
            { label: "Security",    href: `${V2_LINKS.github}/security`, ext: true },
            // Phase 11B — no LICENSE file at repo root yet; point at the
            // FAQ that documents the MIT claim. Repoint to /blob/main/LICENSE
            // once that file lands.
            { label: "MIT License", href: `${V2_LINKS.github}/blob/main/apps/docs/faq.mdx`, ext: true },
          ]}
        />
      </div>

      <div
        style={{
          maxWidth: 1320,
          margin: "40px auto 0",
          paddingTop: 22,
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
        <span>v0.1.0 · alpha cohort</span>
      </div>
    </footer>
  );
}

function FootCol({ title, items }: { title: string; items: Item[] }) {
  const handleClick = (it: Item) => (e: React.MouseEvent<HTMLAnchorElement>) => {
    if (it.ext || it.download) return;
    if (it.href.startsWith("#")) {
      e.preventDefault();
      document.querySelector(it.href)?.scrollIntoView({ behavior: "smooth", block: "start" });
    }
  };
  return (
    <div className="v2-foot-col">
      <div className="v2-foot-col-title">{title}</div>
      <ul style={{ listStyle: "none", padding: 0, margin: 0 }}>
        {items.map((it, i) => (
          <li key={i}>
            <a
              href={it.href}
              target={it.ext ? "_blank" : undefined}
              rel={it.ext ? "noopener noreferrer" : undefined}
              download={it.download ? "" : undefined}
              onClick={handleClick(it)}
            >
              {it.label}
              {it.ext ? <ArrowUp size={10} /> : null}
            </a>
          </li>
        ))}
      </ul>
    </div>
  );
}
