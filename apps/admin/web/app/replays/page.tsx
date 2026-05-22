import Link from "next/link";
import { loadAlpha, loadJournalEntries } from "../../lib/loaders";

export const dynamic = "force-dynamic";

/**
 * `/replays?tester=<handle>` — per-tester event-only timeline.
 *
 * Mirrors `recall alpha replay <handle>` in the dashboard: compiles
 * the tester's `status.json` + every `recovery_journal.json` row
 * with `tester == <handle>` into a chronological list of dated
 * events (install / activity / first recovery / first resume /
 * wow / journal kinds).
 *
 * No content. Dates + kinds + handle-assigned labels only.
 */
export default async function ReplaysPage({
  searchParams,
}: {
  searchParams: { tester?: string };
}) {
  const handle = (searchParams.tester || "").trim();
  const [alpha, entries] = await Promise.all([
    loadAlpha(),
    loadJournalEntries(),
  ]);

  return (
    <div className="page">
      <header className="page-header">
        <div>
          <h1 className="page-title">Replays</h1>
          <div className="page-subtitle">
            per-tester event timeline · no content · counts + dates only
          </div>
        </div>
      </header>

      <section className="section">
        <div className="section-header">
          <span className="section-title">Pick a tester</span>
          <span className="section-aside">— {alpha.testers.length} known</span>
        </div>
        {alpha.testers.length === 0 ? (
          <div className="card empty-note">
            No tester records yet. Create one with{" "}
            <code>recall alpha create &lt;handle&gt; --cohort &lt;name&gt;</code>.
          </div>
        ) : (
          <div className="card" style={{ overflow: "hidden" }}>
            {alpha.testers.map((t) => (
              <Link
                key={t.handle}
                href={`/replays?tester=${encodeURIComponent(t.handle)}`}
                className="panel-row"
                style={{
                  textDecoration: "none",
                  color: "inherit",
                  cursor: "pointer",
                  background: handle === t.handle ? "var(--accent-soft)" : undefined,
                }}
              >
                <span className="panel-row-label">{t.handle}</span>
                <span className="panel-row-detail">
                  {t.cohort} · {t.platform || "—"} · install {t.install_ok || "—"}
                </span>
                <span className="tag">
                  {[t.day1, t.day2, t.day3].filter((d) => d === "yes").length}/3
                </span>
              </Link>
            ))}
          </div>
        )}
      </section>

      {handle ? (
        <ReplayBlock handle={handle} alpha={alpha} entries={entries} />
      ) : null}
    </div>
  );
}

function ReplayBlock({
  handle, alpha, entries,
}: {
  handle: string;
  alpha: Awaited<ReturnType<typeof loadAlpha>>;
  entries: Awaited<ReturnType<typeof loadJournalEntries>>;
}) {
  const tester = alpha.testers.find((t) => t.handle === handle);
  if (!tester) {
    return (
      <section className="section">
        <div className="card empty-note">No tester with handle <code>{handle}</code>.</div>
      </section>
    );
  }
  type Row = { date: string; kind: string; label: string; meta: string };
  const rows: Row[] = [];
  const push = (d: string | null, kind: string, label: string, meta = "") => {
    if (!d || ["none yet", "n/a", ""].includes(d)) return;
    rows.push({ date: d, kind, label, meta });
  };

  if (tester.install_date) {
    push(tester.install_date, "install", "install",
      `${tester.platform || "—"} (${tester.install_ok || "unknown"})`);
  }
  for (const [field, value] of [
    ["day1", tester.day1],
    ["day2", tester.day2],
    ["day3", tester.day3],
  ] as const) {
    if (value === "yes") push(tester.install_date, "activity", field, "kept_using=yes");
  }
  if (tester.first_recovery && tester.first_recovery !== "none yet") {
    push(tester.first_recovery, "recovery", "first recovery", `resume=${tester.first_resume_ok || "unknown"}`);
  }
  if (tester.first_resume_ok === "yes") {
    push(tester.first_recovery, "resume", "first resume", "");
  }
  if (tester.wow_moment) {
    push(tester.install_date, "wow", "wow moment", tester.wow_moment.slice(0, 60));
  }
  for (const e of entries) {
    if (e.tester !== handle) continue;
    const kind = e.kind || "shown";
    const etype =
      kind === "resume_ok"
        ? "resume"
        : e.return_after_gap === true
          ? "return"
          : kind === "bad_recovery"
            ? "failure"
            : "recovery";
    const metaParts: string[] = [];
    if (e.recovered) metaParts.push(e.recovered);
    if (typeof e.time_to_resume === "number") metaParts.push(`t2r=${e.time_to_resume}s`);
    push(
      e.date || null,
      etype,
      etype === "return" ? `return → ${kind}` : kind,
      metaParts.join(" · "),
    );
  }
  rows.sort((a, b) => a.date.localeCompare(b.date));

  const has = (kind: string) => rows.some((r) => r.kind === kind);

  return (
    <section className="section">
      <div className="section-header">
        <span className="section-title">{handle}</span>
        <span className="section-aside">— {rows.length} event(s)</span>
      </div>
      {rows.length === 0 ? (
        <div className="card empty-note">No recorded events for this tester yet.</div>
      ) : (
        <div className="card" style={{ overflow: "hidden" }}>
          {rows.map((r, i) => (
            <div key={i} className="panel-row">
              <span className="panel-row-label" style={{ fontFamily: "ui-monospace, monospace" }}>
                {r.date}
              </span>
              <span className="panel-row-detail">
                <span style={{ color: "var(--ink-3)", marginRight: 8 }}>{r.kind}</span>
                {r.label} {r.meta ? <span style={{ color: "var(--ink-3)" }}>· {r.meta}</span> : null}
              </span>
              <span className="tag">{r.kind}</span>
            </div>
          ))}
        </div>
      )}
      <div style={{ marginTop: 10, fontSize: 12, color: "var(--ink-3)" }}>
        coverage:{" "}
        {[
          ["install", has("install")],
          ["activity", has("activity")],
          ["recovery", has("recovery") || has("resume")],
          ["resume", has("resume")],
          ["return", has("return")],
          ["wow", has("wow")],
          ["failure", has("failure")],
        ].map(([label, ok]) => (
          <span
            key={label as string}
            className="tag"
            style={{ marginRight: 6, color: ok ? "var(--ok)" : "var(--ink-4)" }}
          >
            {ok ? "OK" : "no"} {label}
          </span>
        ))}
      </div>
    </section>
  );
}
