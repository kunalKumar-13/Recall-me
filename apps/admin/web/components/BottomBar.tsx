/**
 * Phase 6J — bottom status bar.
 *
 * One sticky row at the bottom of every page. Three groups, all
 * live-derived:
 *
 *   left:    version (recall package version + admin build mtime)
 *   middle:  doctor verdict + last-bake mtime
 *   right:   build label ("phase-6J · local · no server")
 *
 * Server component — no client state needed.
 */

import type { Verdict } from "../lib/loaders/fsx";

export interface BottomBarStats {
  version: string;
  build_label: string;
  doctor_state: Verdict;
  doctor_label: string;
  baked_mtime: string | null;
}

export function BottomBar({ stats }: { stats: BottomBarStats }) {
  return (
    <footer className="bottombar" aria-label="Control room footer">
      <span className="bottombar-left">
        <span className="bottombar-version">v{stats.version}</span>
      </span>
      <span className="bottombar-middle">
        <span className={`bottombar-pill ${stats.doctor_state}`}>
          doctor {stats.doctor_label}
        </span>
        {stats.baked_mtime && (
          <span className="bottombar-meta">
            baked {new Date(stats.baked_mtime).toLocaleString()}
          </span>
        )}
      </span>
      <span className="bottombar-right">{stats.build_label}</span>
    </footer>
  );
}
