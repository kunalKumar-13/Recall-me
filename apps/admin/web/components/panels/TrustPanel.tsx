import type { TrustSnapshot } from "../../lib/loaders";
import { PanelMeta } from "./HealthPanel";
import { VerdictPill } from "./Verdict";

/**
 * TrustPanel — the live recovery ledger surface.
 *
 * Six outcome counts + the derived trust % + a small *return
 * correlation* line. The baked `trust.json` cards (pre-6H) still
 * render below if present, for visual continuity with the older
 * room. Both sources are read live; nothing here is hardcoded.
 */
export function TrustPanel({ snapshot, compact = false }: { snapshot: TrustSnapshot; compact?: boolean }) {
  const t = snapshot.live;
  return (
    <div>
      <PanelMeta
        title="Trust ledger"
        live="alpha/recovery_journal.json"
        mtime={snapshot.ledger_mtime}
        extra={`${t.total_entries} entries · trust ${t.pct_correct ?? "—"}${t.pct_correct !== null ? "%" : ""}`}
      />

      <div className="grid grid-6">
        <Stat label="shown" value={t.shown} />
        <Stat label="accepted" value={t.accepted} />
        <Stat label="resume_ok" value={t.resume_ok} variant="ok" />
        <Stat label="correct_silence" value={t.correct_silence} variant="ok" />
        <Stat label="ignored" value={t.ignored} variant="warn" />
        <Stat label="bad_recovery" value={t.bad_recovery} variant="bad" />
      </div>

      {!compact && (
        <div className="card" style={{ marginTop: 14, padding: 14 }}>
          <div className="section-title" style={{ marginBottom: 8 }}>derived signals</div>
          <div style={{ display: "flex", gap: 14, flexWrap: "wrap" }}>
            <Detail
              label="trust %"
              value={t.pct_correct === null ? "—" : `${t.pct_correct}%`}
              verdict={
                t.shown === 0
                  ? "yellow"
                  : (t.pct_correct ?? 0) >= 80
                    ? "green"
                    : (t.pct_correct ?? 0) >= 50
                      ? "yellow"
                      : "red"
              }
            />
            <Detail
              label="returns linked"
              value={`${t.entries_with_return} of ${t.total_entries}`}
              verdict={t.entries_with_return > 0 ? "green" : "yellow"}
            />
            <Detail
              label="median time-to-resume"
              value={t.median_time_to_resume_s === null ? "—" : `${t.median_time_to_resume_s}s`}
              verdict={t.median_time_to_resume_s === null ? "mute" : "green"}
            />
          </div>
        </div>
      )}

      {!compact && snapshot.cards.length > 0 && (
        <div className="card" style={{ marginTop: 14, padding: 14 }}>
          <div className="section-title" style={{ marginBottom: 8 }}>baked operator cards</div>
          <div style={{ fontSize: 12.5, color: "var(--ink-3)" }}>
            from <code>apps/admin/data/trust.json</code>
            {snapshot.baked_mtime ? <> · {new Date(snapshot.baked_mtime).toLocaleString()}</> : null}
          </div>
          <div style={{ marginTop: 8, display: "flex", flexDirection: "column", gap: 6 }}>
            {snapshot.cards.map((c) => (
              <div key={c.id} className="panel-row" style={{ borderTop: "1px solid var(--line)" }}>
                <span className="panel-row-label">{c.label}</span>
                <span className="panel-row-detail">{c.detail}</span>
                <span className={`pill ${c.state}`}>{String(c.count)}</span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

function Stat({
  label, value, variant = "neutral",
}: {
  label: string;
  value: number;
  variant?: "neutral" | "ok" | "warn" | "bad";
}) {
  const color = variant === "ok"
    ? "var(--ok)"
    : variant === "warn"
      ? "var(--warn)"
      : variant === "bad"
        ? "var(--danger)"
        : "var(--ink)";
  return (
    <div className="card" style={{ padding: 12 }}>
      <div className="section-title" style={{ marginBottom: 0 }}>{label}</div>
      <div style={{ marginTop: 6, fontSize: 22, fontWeight: 600, color }}>{value}</div>
    </div>
  );
}

function Detail({
  label, value, verdict,
}: {
  label: string;
  value: string;
  verdict: "green" | "yellow" | "red" | "mute";
}) {
  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 4, minWidth: 160 }}>
      <span style={{ fontSize: 12, color: "var(--ink-3)" }}>{label}</span>
      <span style={{ fontSize: 18, fontWeight: 600 }}>{value}</span>
      <VerdictPill value={verdict} />
    </div>
  );
}
