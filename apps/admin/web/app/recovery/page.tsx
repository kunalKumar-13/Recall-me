import Link from "next/link";
import { loadAlpha, loadJournalEntries } from "../../lib/loaders";
import { VerdictPill } from "../../components/panels/Verdict";

export const dynamic = "force-dynamic";

const KINDS = [
  "shown",
  "accepted",
  "ignored",
  "correct_silence",
  "bad_recovery",
  "resume_ok",
] as const;

/**
 * `/recovery` — the Phase 6J Recovery Lab.
 *
 * Phase 6H built the ledger view; 6J extends it with directive-
 * named filters, a return-after-gap heatmap, and the confidence
 * distribution. Every value live-derived from
 * `alpha/recovery_journal.json` and the per-tester records.
 *
 * No content. Per the recovery_journal contract, the `investigation`
 * field is the launcher *title* only; URLs / filenames / queries
 * never appear here.
 */
export default async function RecoveryPage({
  searchParams,
}: {
  searchParams: { kind?: string };
}) {
  const [alpha, allEntries] = await Promise.all([
    loadAlpha(),
    loadJournalEntries(),
  ]);
  const t = alpha.trust;

  const kindFilter = (searchParams.kind || "").toLowerCase();
  const entries = kindFilter
    ? allEntries.filter((e) => (e.kind || "").toLowerCase() === kindFilter)
    : allEntries;

  // Confidence distribution — derives from the per-tester
  // `first_recovery` rows since `confidence` is a launcher-derived
  // band (not a journal field). When the cohort grows, future ledger
  // entries can include `confidence`; until then the *first
  // recovery* count is the best signal we have.
  const confidence = {
    high: alpha.testers.filter((u) => u.first_resume_ok === "yes" && u.first_recovery && u.first_recovery !== "none yet").length,
    medium: alpha.testers.filter((u) => u.first_resume_ok === "partial").length,
    low: alpha.testers.filter((u) => u.first_resume_ok === "wrong work").length,
  };

  // 7-day return-after-gap heatmap — counts the journal entries
  // with `return_after_gap = true` bucketed by date.
  const returnByDay = new Map<string, number>();
  for (const e of allEntries) {
    if (e.return_after_gap === true && e.date) {
      returnByDay.set(e.date, (returnByDay.get(e.date) || 0) + 1);
    }
  }

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
          <span className="section-title">Filter</span>
          <span className="section-aside">
            — {kindFilter ? `kind = ${kindFilter}` : "all kinds"} · {entries.length} of {allEntries.length}
          </span>
        </div>
        <div style={{ display: "flex", gap: 6, flexWrap: "wrap" }}>
          <FilterChip label="all" href="/recovery" active={!kindFilter} />
          {KINDS.map((k) => (
            <FilterChip
              key={k}
              label={k}
              href={`/recovery?kind=${k}`}
              active={kindFilter === k}
            />
          ))}
        </div>
      </section>

      <section className="section">
        <div className="section-header">
          <span className="section-title">Confidence distribution</span>
          <span className="section-aside">
            — derived from per-tester `first_resume_ok`
          </span>
        </div>
        <div className="grid grid-3">
          <ConfidenceBar label="high" count={confidence.high} verdict="green" />
          <ConfidenceBar label="medium" count={confidence.medium} verdict="yellow" />
          <ConfidenceBar label="low" count={confidence.low} verdict="red" />
        </div>
      </section>

      <section className="section">
        <div className="section-header">
          <span className="section-title">Return-after-gap heatmap</span>
          <span className="section-aside">
            — {t.entries_with_return} entry/entries with `return_after_gap = true`
          </span>
        </div>
        <ReturnHeatmap returnByDay={returnByDay} />
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

function FilterChip({
  label, href, active,
}: {
  label: string;
  href: string;
  active: boolean;
}) {
  return (
    <Link
      href={href}
      className="tag"
      style={{
        textDecoration: "none",
        background: active ? "var(--accent-soft)" : undefined,
        color: active ? "var(--accent)" : undefined,
        borderColor: active ? "var(--accent-line)" : undefined,
        cursor: "pointer",
        padding: "2px 9px",
        height: 22,
      }}
    >
      {label}
    </Link>
  );
}

function ConfidenceBar({
  label, count, verdict,
}: {
  label: string;
  count: number;
  verdict: "green" | "yellow" | "red" | "mute";
}) {
  return (
    <div className="card" style={{ padding: 14 }}>
      <div className="section-title" style={{ marginBottom: 0 }}>{label}</div>
      <div style={{ marginTop: 6, fontSize: 22, fontWeight: 600 }}>{count}</div>
      <div style={{ marginTop: 6 }}><VerdictPill value={verdict} /></div>
    </div>
  );
}

/**
 * 7-day return heatmap, styled-div only (no charts library). Empty
 * data renders an honest empty note rather than a flat grey row.
 */
function ReturnHeatmap({ returnByDay }: { returnByDay: Map<string, number> }) {
  if (returnByDay.size === 0) {
    return (
      <div className="card empty-note">
        No journal entries with <code>return_after_gap = true</code> yet.
      </div>
    );
  }
  const today = new Date();
  const cells: { date: string; count: number }[] = [];
  for (let i = 6; i >= 0; i--) {
    const d = new Date(today);
    d.setDate(d.getDate() - i);
    const iso = d.toISOString().slice(0, 10);
    cells.push({ date: iso, count: returnByDay.get(iso) || 0 });
  }
  const max = Math.max(1, ...cells.map((c) => c.count));
  return (
    <div className="card" style={{ padding: 14 }}>
      <div className="heatrow">
        <span className="heatrow-label">returns</span>
        {cells.map((c) => {
          const tier = c.count === 0 ? 0 : Math.min(4, Math.ceil((c.count / max) * 4));
          return (
            <span
              key={c.date}
              className="heatcell"
              data-v={tier}
              title={`${c.date}: ${c.count}`}
            />
          );
        })}
      </div>
    </div>
  );
}
