"use client";

import { useEffect, useRef, useState } from "react";
import { LINKS } from "../../lib/links";

/**
 * Top bar: brand · Product (capabilities dropdown) · anchors ·
 * GitHub chip · Download pill. The dropdown is a drafting card —
 * capability rows left, one featured cell right — and closes on
 * escape, outside click, or scroll-away.
 */

const CAPS = [
  {
    href: "#top",
    title: "Launcher",
    desc: "⌃space — resume in one keystroke",
    icon: (
      <svg viewBox="0 0 16 16" aria-hidden>
        <path
          d="M3 10.5 8 3l5 7.5M5.2 10.5h5.6"
          fill="none"
          stroke="currentColor"
          strokeWidth="1.3"
          strokeLinecap="round"
          strokeLinejoin="round"
        />
      </svg>
    ),
  },
  {
    href: "#extension",
    title: "Browser extension",
    desc: "quiet capture, durable outbox",
    icon: (
      <svg viewBox="0 0 16 16" aria-hidden>
        <circle
          cx="8"
          cy="8"
          r="5.4"
          fill="none"
          stroke="currentColor"
          strokeWidth="1.3"
        />
        <path
          d="M2.8 8h10.4M8 2.6c1.9 1.5 1.9 9.3 0 10.8M8 2.6c-1.9 1.5-1.9 9.3 0 10.8"
          fill="none"
          stroke="currentColor"
          strokeWidth="1.1"
        />
      </svg>
    ),
  },
  {
    href: "#how",
    title: "Recovery",
    desc: "files → chats → tabs, in order",
    icon: (
      <svg viewBox="0 0 16 16" aria-hidden>
        <path
          d="M3 8a5 5 0 1 1 1.5 3.6M3 8V4.7M3 8h3.3"
          fill="none"
          stroke="currentColor"
          strokeWidth="1.3"
          strokeLinecap="round"
          strokeLinejoin="round"
        />
      </svg>
    ),
  },
  {
    href: "#engine",
    title: "Search",
    desc: "memory + files, under 100 ms",
    icon: (
      <svg viewBox="0 0 16 16" aria-hidden>
        <circle
          cx="7"
          cy="7"
          r="4.4"
          fill="none"
          stroke="currentColor"
          strokeWidth="1.3"
        />
        <path
          d="m10.4 10.4 3 3"
          stroke="currentColor"
          strokeWidth="1.3"
          strokeLinecap="round"
        />
      </svg>
    ),
  },
];

export function SiteNav() {
  const [open, setOpen] = useState(false);
  const rootRef = useRef<HTMLDivElement>(null);
  const closeTimer = useRef<ReturnType<typeof setTimeout> | null>(null);

  useEffect(() => {
    if (!open) return;
    const onKey = (e: KeyboardEvent) => {
      if (e.key === "Escape") setOpen(false);
    };
    const onDown = (e: PointerEvent) => {
      if (!rootRef.current?.contains(e.target as Node)) setOpen(false);
    };
    window.addEventListener("keydown", onKey);
    window.addEventListener("pointerdown", onDown);
    return () => {
      window.removeEventListener("keydown", onKey);
      window.removeEventListener("pointerdown", onDown);
    };
  }, [open]);

  const hoverOpen = () => {
    if (closeTimer.current) clearTimeout(closeTimer.current);
    setOpen(true);
  };
  const hoverClose = () => {
    closeTimer.current = setTimeout(() => setOpen(false), 160);
  };

  return (
    <div className="topbar">
      <div className="row">
        <a className="brand" href="#top">
          <span className="dot" />
          Recall
        </a>
        <nav className="topnav">
          <div
            className="navdd"
            ref={rootRef}
            onMouseEnter={hoverOpen}
            onMouseLeave={hoverClose}
          >
            <button
              className={`navbtn${open ? " on" : ""}`}
              aria-expanded={open}
              aria-haspopup="true"
              onClick={() => setOpen((v) => !v)}
            >
              Product <span className="chev" aria-hidden>⌄</span>
            </button>
            {open && (
              <div className="menu" role="menu">
                <div className="menu-grid">
                  <div className="menu-caps">
                    <div className="menu-label">Capabilities</div>
                    <div className="menu-2col">
                      {CAPS.map((c) => (
                        <a
                          key={c.title}
                          className="mitem"
                          href={c.href}
                          role="menuitem"
                          onClick={() => setOpen(false)}
                        >
                          <span className="mic">{c.icon}</span>
                          <span>
                            <span className="mt">{c.title}</span>
                            <span className="md">{c.desc}</span>
                          </span>
                        </a>
                      ))}
                    </div>
                  </div>
                  <a
                    className="mfeat"
                    href="#trust"
                    onClick={() => setOpen(false)}
                  >
                    <span className="mt">Local-first engine</span>
                    <span className="md">
                      Seven deterministic layers over plain files in ~/.recall.
                      No cloud, ever.
                    </span>
                  </a>
                </div>
                <div className="menu-foot">
                  <span>New to Recall?</span>
                  <a
                    href={LINKS.docs}
                    target="_blank"
                    rel="noreferrer"
                    onClick={() => setOpen(false)}
                  >
                    Read the docs ↗
                  </a>
                </div>
              </div>
            )}
          </div>
          <a className="hide-sm" href="#how">
            How it works
          </a>
          <a className="hide-sm" href="#extension">
            Extension
          </a>
          <a className="hide-sm" href="#faq">
            FAQ
          </a>
        </nav>
        <div className="topright">
          <a
            className="ghchip"
            href={LINKS.github}
            target="_blank"
            rel="noreferrer"
            aria-label="Recall on GitHub"
          >
            <svg viewBox="0 0 16 16" width="14" height="14" aria-hidden>
              <path
                fill="currentColor"
                d="M8 0C3.58 0 0 3.58 0 8c0 3.54 2.29 6.53 5.47 7.59.4.07.55-.17.55-.38 0-.19-.01-.82-.01-1.49-2.01.37-2.53-.49-2.69-.94-.09-.23-.48-.94-.82-1.13-.28-.15-.68-.52-.01-.53.63-.01 1.08.58 1.23.82.72 1.21 1.87.87 2.33.66.07-.52.28-.87.51-1.07-1.78-.2-3.64-.89-3.64-3.95 0-.87.31-1.59.82-2.15-.08-.2-.36-1.02.08-2.12 0 0 .67-.21 2.2.82a7.42 7.42 0 0 1 4 0c1.53-1.04 2.2-.82 2.2-.82.44 1.1.16 1.92.08 2.12.51.56.82 1.27.82 2.15 0 3.07-1.87 3.75-3.65 3.95.29.25.54.73.54 1.48 0 1.07-.01 1.93-.01 2.2 0 .21.15.46.55.38A8.01 8.01 0 0 0 16 8c0-4.42-3.58-8-8-8Z"
              />
            </svg>
            Star
          </a>
          <a className="btn solid navcta" href="#download">
            Download
          </a>
        </div>
      </div>
    </div>
  );
}
