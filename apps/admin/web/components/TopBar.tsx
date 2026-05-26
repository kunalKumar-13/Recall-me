"use client";

import Link from "next/link";
import { useEffect, useState } from "react";

import type { Verdict } from "../lib/loaders/fsx";

/**
 * Phase 6J — global top bar.
 *
 * Always-visible row that gives the founder the *30-second
 * understanding* even before they leave the current route. Four
 * groups:
 *
 *   [Recall]    health pill · readiness · active installs
 *   [search]    command-palette trigger (opens via CmdK or click)
 *
 * Every value here comes from live loader data plumbed by the
 * layout. The component itself owns no state beyond the
 * command-palette open flag.
 */

export interface TopBarStats {
  installs: number;
  daemon_state: Verdict;
  daemon_label: string;
  readiness_state: Verdict;
  readiness_label: string;
  version: string;
}

export function TopBar({
  stats,
  onOpenPalette,
}: {
  stats: TopBarStats;
  onOpenPalette: () => void;
}) {
  // ⌘K / Ctrl-K listener. Lives on the TopBar so the trigger is
  // visible *and* the keyboard surface lights up the same button.
  useEffect(() => {
    function onKey(e: KeyboardEvent) {
      const k = e.key.toLowerCase();
      if ((e.metaKey || e.ctrlKey) && k === "k") {
        e.preventDefault();
        onOpenPalette();
      }
    }
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [onOpenPalette]);

  return (
    <header className="topbar" aria-label="Control room top bar">
      <Link href="/" className="topbar-brand">
        <span className="topbar-mark" aria-hidden />
        <span className="topbar-wordmark">Recall</span>
        <span className="topbar-edition">control room</span>
      </Link>

      <div className="topbar-stats">
        <TopBarPill state={stats.daemon_state} label={`daemon ${stats.daemon_label}`} />
        <TopBarPill state={stats.readiness_state} label={stats.readiness_label} />
        <TopBarPill state={stats.installs > 0 ? "green" : "mute"}
                    label={`${stats.installs} installs`} />
      </div>

      <button
        type="button"
        className="topbar-search"
        onClick={onOpenPalette}
        aria-label="Open command palette (Ctrl+K)"
      >
        <svg viewBox="0 0 24 24" width="14" height="14" aria-hidden
             fill="none" stroke="currentColor" strokeWidth="1.6"
             strokeLinecap="round" strokeLinejoin="round">
          <circle cx="10.5" cy="10.5" r="6.5" />
          <path d="M20 20l-4.5-4.5" />
        </svg>
        <span>Search · run command</span>
        <kbd>⌘K</kbd>
      </button>
    </header>
  );
}


export function TopBarPill({
  state,
  label,
}: {
  state: Verdict;
  label: string;
}) {
  return <span className={`topbar-pill ${state}`}>{label}</span>;
}


/**
 * Hook the layout uses to track command-palette open/close from the
 * server-rendered top bar. The TopBar itself is a client component,
 * but the palette renders inline so it can fan out into the rest of
 * the shell.
 */
export function usePaletteToggle(): { open: boolean; setOpen: (v: boolean) => void } {
  const [open, setOpen] = useState(false);
  return { open, setOpen };
}
