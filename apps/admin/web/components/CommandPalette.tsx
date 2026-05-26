"use client";

import { useEffect, useMemo, useRef, useState } from "react";
import { useRouter } from "next/navigation";

/**
 * Phase 6J — command palette.
 *
 * Ctrl+K (⌘K on macOS) → fuzzy-search the directive's nine named
 * actions + every route in the left nav. Selecting a *route* item
 * navigates; selecting an *action* either re-runs server data
 * (`refresh`) or copies the canonical CLI command to the clipboard
 * — the same *no server endpoint* contract as the Phase 6H actions
 * sidebar.
 *
 * The palette is open-state-tracked by the layout, so this is a
 * pure presentation component. The shell mounts it once and toggles
 * via the TopBar trigger.
 */

type Item =
  | { kind: "route"; id: string; label: string; sub?: string; href: string }
  | { kind: "action"; id: string; label: string; sub?: string; cmd: string }
  | { kind: "refresh"; id: string; label: string; sub?: string };

const ROUTES: Item[] = [
  { kind: "route", id: "overview", label: "Overview", sub: "every panel · compact", href: "/" },
  { kind: "route", id: "users", label: "Users", sub: "per-cohort table", href: "/users" },
  { kind: "route", id: "recovery", label: "Recovery Lab", sub: "6 outcomes + t2r + heatmap", href: "/recovery" },
  { kind: "route", id: "replays", label: "Replay Studio", sub: "per-tester timeline", href: "/replays" },
  { kind: "route", id: "daily-loop", label: "Daily Loop", sub: "today / yesterday / 7d", href: "/daily-loop" },
  { kind: "route", id: "trust", label: "Trust", sub: "recovery ledger", href: "/trust" },
  { kind: "route", id: "release", label: "Release Center", sub: "per-gate progress", href: "/release" },
  { kind: "route", id: "system", label: "System Console", sub: "doctor + ~/.recall", href: "/system" },
  { kind: "route", id: "extension", label: "Extension", sub: "popup pairing", href: "/extension" },
  { kind: "route", id: "launcher", label: "Launcher", sub: "v2/v3 captures + diff", href: "/launcher" },
  { kind: "route", id: "desktop", label: "Desktop", sub: "apps · focus · top tools · session time", href: "/desktop" },
  { kind: "route", id: "experiments", label: "Experiments", sub: "feature flags · demo · gates", href: "/experiments" },
  { kind: "route", id: "logs", label: "Logs", sub: "view + filter + download", href: "/logs" },
  { kind: "route", id: "screenshots", label: "Screenshot manager", sub: "every capture", href: "/screenshots" },
  { kind: "route", id: "docs", label: "Docs", sub: "canonical doc map", href: "/docs" },
];

const ACTIONS: Item[] = [
  { kind: "refresh", id: "refresh", label: "Refresh data", sub: "re-run loaders" },
  { kind: "action", id: "doctor", label: "Run doctor", sub: "python recall.py doctor", cmd: "python recall.py doctor" },
  { kind: "action", id: "bake", label: "Bake data", sub: "python recall.py founder bake", cmd: "python recall.py founder bake" },
  { kind: "action", id: "alpha-report", label: "Generate alpha report", sub: "python recall.py alpha export", cmd: "python recall.py alpha export" },
  { kind: "action", id: "stats", label: "Export trust (stats)", sub: "python recall.py stats --export", cmd: "python recall.py stats --export" },
  { kind: "action", id: "screens", label: "Open screenshots folder", sub: "explorer assets\\screenshots\\", cmd: "explorer assets\\screenshots" },
  { kind: "action", id: "alpha-folder", label: "Open alpha folder", sub: "explorer alpha\\users\\", cmd: "explorer alpha\\users" },
  { kind: "action", id: "logs-open", label: "Open logs", sub: "Get-Content ~/.recall/recall.log", cmd: "Get-Content -Wait $env:USERPROFILE\\.recall\\recall.log" },
  { kind: "action", id: "journal", label: "Open recovery journal", sub: "alpha/recovery_journal.json", cmd: "notepad alpha\\recovery_journal.json" },
  { kind: "action", id: "daily-file", label: "Open daily loop", sub: "~/.recall/daily_loop.jsonl", cmd: "notepad %USERPROFILE%\\.recall\\daily_loop.jsonl" },
];


function _score(item: Item, q: string): number {
  if (!q) return 1;
  const needle = q.toLowerCase();
  const hay = `${item.label} ${item.sub ?? ""}`.toLowerCase();
  if (hay.startsWith(needle)) return 3;
  if (hay.includes(needle)) return 2;
  // Fuzzy: every character must appear in order.
  let i = 0;
  for (const c of hay) {
    if (c === needle[i]) i += 1;
    if (i >= needle.length) return 1;
  }
  return 0;
}


export function CommandPalette({
  open,
  onClose,
}: {
  open: boolean;
  onClose: () => void;
}) {
  const router = useRouter();
  const [query, setQuery] = useState("");
  const [index, setIndex] = useState(0);
  const [copied, setCopied] = useState<string | null>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  const items = useMemo<Item[]>(() => [...ROUTES, ...ACTIONS], []);
  const filtered = useMemo(() => {
    const scored = items
      .map((it) => ({ it, s: _score(it, query) }))
      .filter((p) => p.s > 0)
      .sort((a, b) => b.s - a.s);
    return scored.map((p) => p.it);
  }, [items, query]);

  useEffect(() => {
    if (open) {
      setQuery("");
      setIndex(0);
      setCopied(null);
      setTimeout(() => inputRef.current?.focus(), 30);
    }
  }, [open]);

  useEffect(() => { setIndex(0); }, [query]);

  async function pick(item: Item) {
    if (item.kind === "route") {
      onClose();
      router.push(item.href);
      return;
    }
    if (item.kind === "refresh") {
      router.refresh();
      setCopied("refresh");
      setTimeout(onClose, 350);
      return;
    }
    // action — copy the CLI command to the clipboard.
    try {
      await navigator.clipboard.writeText(item.cmd);
    } catch {
      const t = document.createElement("textarea");
      t.value = item.cmd;
      document.body.appendChild(t);
      t.select();
      document.execCommand("copy");
      document.body.removeChild(t);
    }
    setCopied(item.id);
    setTimeout(onClose, 700);
  }

  function onKeyDown(e: React.KeyboardEvent<HTMLInputElement>) {
    if (e.key === "Escape") {
      e.preventDefault();
      onClose();
      return;
    }
    if (e.key === "ArrowDown") {
      e.preventDefault();
      setIndex((i) => Math.min(filtered.length - 1, i + 1));
      return;
    }
    if (e.key === "ArrowUp") {
      e.preventDefault();
      setIndex((i) => Math.max(0, i - 1));
      return;
    }
    if (e.key === "Enter") {
      e.preventDefault();
      const it = filtered[index];
      if (it) void pick(it);
    }
  }

  if (!open) return null;

  return (
    <div
      className="palette-backdrop"
      role="dialog"
      aria-modal="true"
      aria-label="Command palette"
      onClick={onClose}
    >
      <div className="palette" onClick={(e) => e.stopPropagation()}>
        <div className="palette-search">
          <svg viewBox="0 0 24 24" width="14" height="14" aria-hidden
               fill="none" stroke="currentColor" strokeWidth="1.6"
               strokeLinecap="round" strokeLinejoin="round">
            <circle cx="10.5" cy="10.5" r="6.5" />
            <path d="M20 20l-4.5-4.5" />
          </svg>
          <input
            ref={inputRef}
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onKeyDown={onKeyDown}
            placeholder="Type a command or navigate…"
            spellCheck={false}
          />
          <kbd>esc</kbd>
        </div>
        <ul className="palette-list" role="listbox">
          {filtered.length === 0 ? (
            <li className="palette-empty">no match · try a route name or “doctor”</li>
          ) : (
            filtered.map((it, i) => (
              <li
                key={`${it.kind}-${it.id}`}
                role="option"
                aria-selected={i === index}
                className={`palette-row ${i === index ? "is-active" : ""}`}
                onMouseEnter={() => setIndex(i)}
                onClick={() => void pick(it)}
              >
                <span className="palette-kind">
                  {it.kind === "route" ? "→" : it.kind === "refresh" ? "↻" : "$"}
                </span>
                <span className="palette-label">
                  <span className="palette-label-main">{it.label}</span>
                  {it.sub && <span className="palette-label-sub">{it.sub}</span>}
                </span>
                <span className="palette-tail">
                  {copied === it.id
                    ? "copied"
                    : it.kind === "route" ? "↩"
                    : it.kind === "refresh" ? "↩"
                    : "copy"}
                </span>
              </li>
            ))
          )}
        </ul>
        <div className="palette-foot">
          <span>↑↓ navigate</span>
          <span>↩ select</span>
          <span>esc close</span>
        </div>
      </div>
    </div>
  );
}
