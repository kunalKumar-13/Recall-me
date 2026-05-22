import type { ReleaseStatus } from "../../lib/loaders";
import { PanelMeta } from "./HealthPanel";
import { VerdictPill } from "./Verdict";

/**
 * ReleasePanel — the Phase 6H release-center surface.
 *
 * Shows the per-gate progress bars + the GO/PARTIAL/NO-GO verdict
 * + the live blockers list. Each gate's progress is derived from
 * the source value (`ready`/`signed`/`complete`/...); no
 * hardcoded percentages.
 */
export function ReleasePanel({ release, compact = false }: { release: ReleaseStatus; compact?: boolean }) {
  const v: "green" | "yellow" | "red" =
    release.go_no_go === "GO"
      ? "green"
      : release.go_no_go === "PARTIAL"
        ? "yellow"
        : release.go_no_go === "NO-GO"
          ? "red"
          : "yellow";
  return (
    <div>
      <PanelMeta
        title="Release center"
        live="apps/admin/release_state.json"
        mtime={release.source_mtime}
        extra={`${release.current_version} → ${release.next_milestone}`}
      />

      <div className="card" style={{ padding: 16 }}>
        <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: 12 }}>
          <span className="section-title" style={{ marginBottom: 0 }}>go / no-go</span>
          <span className={`pill ${v}`}>{release.go_no_go}</span>
        </div>
        <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
          {(release.progress ?? []).map((p) => (
            <ProgressRow key={p.label} {...p} />
          ))}
        </div>
      </div>

      {!compact && release.blocked.length > 0 && (
        <div className="card" style={{ marginTop: 14, padding: 14 }}>
          <div className="section-title" style={{ marginBottom: 6 }}>blockers</div>
          <ul style={{ paddingLeft: 18, margin: 0, color: "var(--ink-2)", fontSize: 13, lineHeight: 1.6 }}>
            {release.blocked.map((b, i) => <li key={i}>{b}</li>)}
          </ul>
        </div>
      )}
    </div>
  );
}

function ProgressRow({
  label,
  pct,
  verdict,
}: {
  label: string;
  pct: number;
  verdict: "green" | "yellow" | "red" | "mute";
}) {
  const barColor =
    verdict === "green" ? "var(--ok)" : verdict === "red" ? "var(--danger)" : "var(--warn)";
  return (
    <div>
      <div style={{ display: "flex", justifyContent: "space-between", fontSize: 12, color: "var(--ink-2)" }}>
        <span>{label}</span>
        <span>
          <VerdictPill value={verdict} label={`${pct}%`} />
        </span>
      </div>
      <div
        style={{
          marginTop: 4,
          height: 6,
          borderRadius: 3,
          background: "var(--surface-sunken)",
          overflow: "hidden",
        }}
      >
        <div
          style={{
            width: `${Math.max(0, Math.min(100, pct))}%`,
            height: "100%",
            background: barColor,
            transition: "width 200ms ease",
          }}
        />
      </div>
    </div>
  );
}
