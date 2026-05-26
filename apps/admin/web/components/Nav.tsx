"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

/**
 * Phase 6H — left-rail navigation.
 *
 * Sticky, collapsible-aside (CSS-only), keyboard-reachable. Ten
 * sections, each a Next.js route. The active route is matched by
 * exact pathname, with `/` treated as the overview synonym.
 *
 * No client state beyond the path read; the component is a thin
 * server-cousin styled link list.
 */

type NavRow = {
  href: string;
  label: string;
  hotkey?: string;
  group?: string;
};

const NAV: NavRow[] = [
  // Phase 6J — full directive order. 12 sections, four groups
  // (overview · cohort · engine · ship). The accesskey hotkeys
  // are 1-9 + 0 for the first ten; the last two (Experiments,
  // Docs) are reachable via the command palette.
  { href: "/", label: "Overview", hotkey: "1" },
  { href: "/users", label: "Users", hotkey: "2", group: "cohort" },
  { href: "/recovery", label: "Recovery", hotkey: "3", group: "engine" },
  { href: "/replays", label: "Replay", hotkey: "4", group: "engine" },
  { href: "/daily-loop", label: "Daily Loop", hotkey: "5", group: "engine" },
  { href: "/trust", label: "Trust", hotkey: "6", group: "engine" },
  { href: "/release", label: "Release", hotkey: "7", group: "ship" },
  { href: "/system", label: "System", hotkey: "8", group: "ship" },
  { href: "/extension", label: "Extension", hotkey: "9", group: "ship" },
  { href: "/launcher", label: "Launcher", hotkey: "0", group: "ship" },
  { href: "/desktop", label: "Desktop", group: "ship" },
  { href: "/experiments", label: "Experiments", group: "lab" },
  { href: "/docs", label: "Docs", group: "lab" },
];

function _isActive(pathname: string, href: string): boolean {
  if (href === "/") return pathname === "/";
  return pathname === href || pathname.startsWith(href + "/");
}

export function Nav() {
  const pathname = usePathname() ?? "/";

  // Group rows so we can drop a separator between cohort/engine/ship.
  const groups: { key: string; rows: NavRow[] }[] = [];
  for (const row of NAV) {
    const key = row.group ?? "overview";
    const tail = groups[groups.length - 1];
    if (!tail || tail.key !== key) groups.push({ key, rows: [row] });
    else tail.rows.push(row);
  }

  return (
    <nav className="rail" aria-label="Control room navigation">
      <div className="rail-head">
        <span className="rail-mark" aria-hidden />
        <span className="rail-title">Recall</span>
        <span className="rail-sub">control room</span>
      </div>

      <div className="rail-groups">
        {groups.map((g, gi) => (
          <ul key={g.key} className="rail-list" aria-label={`group ${g.key}`}>
            {g.rows.map((row) => {
              const active = _isActive(pathname, row.href);
              return (
                <li key={row.href}>
                  <Link
                    href={row.href}
                    className={`rail-link ${active ? "is-active" : ""}`}
                    aria-current={active ? "page" : undefined}
                    accessKey={row.hotkey}
                  >
                    <span className="rail-link-label">{row.label}</span>
                    {row.hotkey && (
                      <span className="rail-link-key" aria-hidden>
                        {row.hotkey}
                      </span>
                    )}
                  </Link>
                </li>
              );
            })}
            {gi < groups.length - 1 && <li className="rail-divider" aria-hidden />}
          </ul>
        ))}
      </div>

      <div className="rail-foot">
        <span className="rail-foot-line">local-first</span>
        <span className="rail-foot-line">no server</span>
        <span className="rail-foot-line">no auth</span>
      </div>
    </nav>
  );
}
