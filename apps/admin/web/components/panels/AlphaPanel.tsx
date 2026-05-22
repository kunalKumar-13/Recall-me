import type { AlphaExport } from "../../lib/loaders";
import { PanelMeta } from "./HealthPanel";
import { VerdictPill } from "./Verdict";

/**
 * AlphaPanel — Phase 6E cohort signals, live-derived.
 *
 * Five directive signals (installs / returning / first recoveries /
 * trust % / drop reasons), each with a green/yellow/red verdict
 * pill. Plus a per-cohort table beneath.
 */
export function AlphaPanel({ data, compact = false }: { data: AlphaExport; compact?: boolean }) {
  const v = data.verdicts;
  return (
    <div>
      <PanelMeta
        title="Alpha health"
        live="alpha/users/ + alpha/recovery_journal.json"
        mtime={data.cohort_mtime}
      />

      <div className="grid grid-3">
        <Signal label="installs" value={String(data.installs)} verdict={v.installs} />
        <Signal label="returning" value={String(data.returning)} verdict={v.returning} hint={">= 2 of 3 days"} />
        <Signal label="first recoveries" value={String(data.recoveries)} verdict={v.first_recoveries} />
        <Signal
          label="trust %"
          value={data.trust.pct_correct === null ? "—" : `${data.trust.pct_correct}%`}
          verdict={v.trust}
          hint={`${data.trust.resume_ok + data.trust.correct_silence}/${data.trust.shown} correct of shown`}
        />
        <Signal
          label="drop reasons"
          value={String(Object.values(data.drop_reasons).reduce((a, b) => a + b, 0))}
          verdict={v.drops}
        />
        <Signal
          label="install fails"
          value={String(data.install_fails)}
          verdict={v.install_fails}
        />
      </div>

      {!compact && (
        <div className="card" style={{ marginTop: 14, overflow: "hidden" }}>
          {data.cohorts.length === 0 ? (
            <div className="empty-note">No cohort folders yet.</div>
          ) : (
            data.cohorts
              .filter((c) => c.installs > 0 || true)
              .map((c) => (
                <div key={c.cohort} className="panel-row">
                  <span className="panel-row-label">{c.cohort}</span>
                  <span className="panel-row-detail">
                    installs {c.installs} · returning {c.returning} · first-rec {c.first_recoveries} · drops {c.drops}
                  </span>
                  <span className="tag">{c.testers.length}</span>
                </div>
              ))
          )}
        </div>
      )}

      {!compact && Object.keys(data.drop_reasons).length > 0 && (
        <div className="card" style={{ marginTop: 14, padding: 14 }}>
          <div className="section-title" style={{ marginBottom: 6 }}>drop reasons</div>
          {Object.entries(data.drop_reasons)
            .sort((a, b) => b[1] - a[1])
            .map(([reason, n]) => (
              <div key={reason} style={{ fontSize: 12.5, color: "var(--ink-2)" }}>
                <span className="tag" style={{ marginRight: 8 }}>{n}</span>
                {reason}
              </div>
            ))}
        </div>
      )}
    </div>
  );
}

function Signal({
  label,
  value,
  verdict,
  hint,
}: {
  label: string;
  value: string;
  verdict: "green" | "yellow" | "red" | "mute";
  hint?: string;
}) {
  return (
    <div className="card" style={{ padding: 14 }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "baseline" }}>
        <span className="section-title" style={{ marginBottom: 0 }}>{label}</span>
        <VerdictPill value={verdict} />
      </div>
      <div style={{ marginTop: 8, fontSize: 28, fontWeight: 600 }}>{value}</div>
      {hint && <div style={{ marginTop: 2, fontSize: 12, color: "var(--ink-3)" }}>{hint}</div>}
    </div>
  );
}
