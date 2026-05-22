import Link from "next/link";
import { loadAlpha, loadJournalEntries } from "../../lib/loaders";
import { VerdictPill } from "../../components/panels/Verdict";

export const dynamic = "force-dynamic";

/**
 * `/recovery` — the Phase 6H Recovery Room.
 *
 * Per-entry view of the recovery ledger: every Resume decision the
 * cohort has reported, grouped by tester, with the 6E vocabulary
 * + the 6F return / time-to-resume fields. Click-through lands on
 * `/replays?tester=<handle>` (the per-tester timeline).
 *
 * No content. Per the recovery_journal contract, the `investigation`
 * field is the launcher *title* only; URLs / filenames / queries
 * never appear here.
 */
export default async function RecoveryPage() {
  const [alpha, entries] = await Promise.all([
    loadAlpha(),
    loadJournalEntries(),
  ]);
  const t = alpha.trust;

  return (
    <div className="page">
      <header className="page-header">
        <div>
          <h1 className="page-title">Recovery</h1>
          <div className="page-subtitle">
            live read from <code>alpha/recovery_journal.json</code> · {t.total_entries} entries
          </div>
        </div>
      </header>

      <section className="section">
        <div className="grid grid-6">
          <Stat label="shown" value={t.shown} />
          <Stat label="accepted" value={t.accepted} />
          <Stat label="ignored" value={t.ignored} />
          <Stat label="correct_silence" value={t.correct_silence} variant="ok" />
          <Stat label="bad_recovery" value={t.bad_recovery} variant="bad" />
          <Stat label="resume_ok" value={t.resume_ok} variant="ok" />
        </div>
      </section>

      <section className="section">
        <div className="section-header">
          <span className="section-title">Time-to-resume</span>
          <span className="section-aside">
            — median {t.median_time_to_resume_s === null ? "—" : `${t.median_time_to_resume_s}s`} · {t.entries_with_return} entries followed a return
          </span>
        </div>
        <T2RSparkline entries={entries} />
      </section>

      <section className="section">
        <div className="section-header">
          <span className="section-title">Ledger</span>
          <span className="section-aside">— click a row to replay the tester</span>
        </div>
        {entries.length === 0 ? (
          <div className="card empty-note">
            No ledger entries yet. Append per Resume click to{" "}
            <code>alpha/recovery_journal.json</code>.
          </div>
        ) : (
          <div className="card" style={{ overflow: "hidden" }}>
            {entries
              .slice()
              .sort((a, b) => (b.date || "").localeCompare(a.date || ""))
              .map((e, i) => (
                <Link
                  key={`${e.tester}-${i}`}
                  href={`/replays?tester=${encodeURIComponent(e.tester || "")}`}
                  className="panel-row"
                  style={{ textDecoration: "none", color: "inherit", cursor: "pointer" }}
                >
                  <span className="panel-row-label">
                    {e.date || "—"} · {e.tester || "—"}
                  </span>
                  <span className="panel-row-detail">
                    {e.investigation ? <>{e.investigation} · </> : null}
                    {e.recovered ? <>{e.recovered} · </> : null}
                    {typeof e.time_to_resume === "number" ? <>t2r {e.time_to_resume}s · </> : null}
                    {e.return_after_gap ? <>after-gap · </> : null}
                    {e.notes || ""}
                  </span>
                  <span style={{ display: "inline-flex", gap: 4 }}>
                    <VerdictPill
                      value={
                        e.kind === "resume_ok" || e.kind === "correct_silence"
                          ? "green"
                          : e.kind === "bad_recovery"
                            ? "red"
                            : "yellow"
                      }
                      label={e.kind || "—"}
                    />
                  </span>
                </Link>
              ))}
          </div>
        )}
      </section>
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

/**
 * Minimal in-line trend: each ledger entry's `time_to_resume`
 * plotted as bars in chronological order. Empty data → an honest
 * empty note, never a placeholder zero line.
 */
function T2RSparkline({ entries }: { entries: Awaited<ReturnType<typeof loadJournalEntries>> }) {
  const points = entries
    .filter((e) => typeof e.time_to_resume === "number")
    .slice()
    .sort((a, b) => (a.date || "").localeCompare(b.date || ""));
  if (points.length === 0) {
    return (
      <div className="card empty-note">
        No time-to-resume data yet. Add a <code>time_to_resume</code> field on the next ledger entry.
      </div>
    );
  }
  const max = Math.max(...points.map((p) => p.time_to_resume as number));
  return (
    <div className="card" style={{ padding: 14 }}>
      <div style={{ display: "flex", alignItems: "flex-end", gap: 3, height: 80 }}>
        {points.map((p, i) => {
          const h = Math.max(2, Math.round(((p.time_to_resume as number) / max) * 76));
          return (
            <div
              key={`${p.date}-${i}`}
              title={`${p.date} · ${p.tester} · ${p.time_to_resume}s`}
              style={{
                flex: "1 1 0",
                height: `${h}px`,
                background: "var(--accent)",
                borderRadius: 2,
                opacity: 0.85,
              }}
            />
          );
        })}
      </div>
    </div>
  );
}
