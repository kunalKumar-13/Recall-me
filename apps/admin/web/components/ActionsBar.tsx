"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";

/**
 * Phase 6H — actions sidebar.
 *
 * Seven buttons the directive names: refresh / bake / doctor /
 * alpha report / open screenshots / open logs / export health.
 *
 * Strict server-side stance: there is *no* server endpoint that
 * runs these tools — they live as instructions the founder
 * executes on their own machine. The button copies the canonical
 * command to the clipboard; the founder pastes into a terminal.
 *
 * This keeps the rule "no server" intact while still surfacing the
 * action set the directive names. Refresh is the only button that
 * actually does something in-page — it re-runs the server
 * component data fetch via `router.refresh()`.
 */

type Action = {
  id: string;
  label: string;
  hint: string;
  cmd?: string;
  kind: "refresh" | "copy" | "external";
  href?: string;
};

const ACTIONS: Action[] = [
  { id: "refresh", label: "Refresh data", hint: "re-read all loaders", kind: "refresh" },
  { id: "bake", label: "Run bake", hint: "regenerate apps/admin/data/*.json", kind: "copy", cmd: "python recall.py founder bake" },
  { id: "doctor", label: "Run doctor", hint: "10-check diagnostics", kind: "copy", cmd: "python recall.py doctor" },
  { id: "alpha", label: "Alpha report", hint: "JSON export of the cohort", kind: "copy", cmd: "python recall.py alpha export" },
  { id: "screens", label: "Open screenshots", hint: "assets/screenshots/", kind: "external", href: "/screens/launcher/launcher-digest.png" },
  { id: "logs", label: "Open logs", hint: "~/.recall/recall.log", kind: "copy", cmd: "Get-Content -Wait $env:USERPROFILE\\.recall\\recall.log" },
  { id: "export", label: "Export health", hint: "recall stats --export", kind: "copy", cmd: "python recall.py stats --export" },
];

export function ActionsBar() {
  const router = useRouter();
  const [copied, setCopied] = useState<string | null>(null);

  async function handleClick(a: Action) {
    if (a.kind === "refresh") {
      router.refresh();
      setCopied("refresh");
      setTimeout(() => setCopied(null), 900);
      return;
    }
    if (a.kind === "copy" && a.cmd) {
      try {
        await navigator.clipboard.writeText(a.cmd);
        setCopied(a.id);
        setTimeout(() => setCopied(null), 1400);
      } catch {
        // Older browsers / file:// — fall back to a textarea trick.
        const t = document.createElement("textarea");
        t.value = a.cmd;
        document.body.appendChild(t);
        t.select();
        document.execCommand("copy");
        document.body.removeChild(t);
        setCopied(a.id);
        setTimeout(() => setCopied(null), 1400);
      }
      return;
    }
    if (a.kind === "external" && a.href) {
      window.open(a.href, "_blank", "noopener");
    }
  }

  return (
    <aside className="actions" aria-label="Operator actions">
      <div className="actions-head">
        <span className="actions-eyebrow">Actions</span>
        <span className="actions-hint">all local · no server</span>
      </div>
      <ul className="actions-list">
        {ACTIONS.map((a) => (
          <li key={a.id}>
            <button
              type="button"
              className={`actions-btn ${copied === a.id ? "is-copied" : ""}`}
              onClick={() => handleClick(a)}
              title={a.cmd || a.hint}
            >
              <span className="actions-btn-label">{a.label}</span>
              <span className="actions-btn-hint">
                {copied === a.id
                  ? a.kind === "refresh" ? "refreshed" : "copied"
                  : a.hint}
              </span>
            </button>
          </li>
        ))}
      </ul>
    </aside>
  );
}
