import Link from "next/link";
import { loadAlpha } from "../../lib/loaders";

export const dynamic = "force-dynamic";

/**
 * `/users` — the per-tester table. Every row is one
 * `alpha/users/<cohort>/<handle>/status.json`; click → `/replays`.
 *
 * No content. Metadata only (handle, cohort, platform, day-flags,
 * first_recovery date, kept_using, drop_reason). Mirrors what
 * `recall alpha status` prints.
 */
export default async function UsersPage() {
  const alpha = await loadAlpha();
  return (
    <div className="page">
      <header className="page-header">
        <div>
          <h1 className="page-title">Users</h1>
          <div className="page-subtitle">
            {alpha.installs} tester record(s) across {alpha.cohorts.filter((c) => c.installs > 0).length} cohort(s)
          </div>
        </div>
      </header>

      {alpha.testers.length === 0 ? (
        <div className="card empty-note">
          No tester records yet. Create one with{" "}
          <code>recall alpha create &lt;handle&gt; --cohort &lt;name&gt;</code>.
        </div>
      ) : (
        alpha.cohorts
          .filter((c) => c.installs > 0)
          .map((c) => (
            <section key={c.cohort} className="section">
              <div className="section-header">
                <span className="section-title">{c.cohort}</span>
                <span className="section-aside">
                  — installs {c.installs} · returning {c.returning} · first-rec {c.first_recoveries} · drops {c.drops}
                </span>
              </div>
              <div className="card" style={{ overflow: "hidden" }}>
                {c.testers.map((t) => {
                  const yesDays = [t.day1, t.day2, t.day3].filter((d) => d === "yes").length;
                  return (
                    <Link
                      key={t.handle}
                      href={`/replays?tester=${encodeURIComponent(t.handle)}`}
                      className="panel-row"
                      style={{ textDecoration: "none", color: "inherit" }}
                    >
                      <span className="panel-row-label">{t.handle}</span>
                      <span className="panel-row-detail">
                        {t.platform || "—"} · install {t.install_ok || "—"} · days {yesDays}/3 ·{" "}
                        {t.first_recovery && t.first_recovery !== "none yet"
                          ? `first-rec ${t.first_recovery}`
                          : "first-rec none yet"}
                        {t.drop_reason ? <> · drop: {t.drop_reason}</> : null}
                      </span>
                      <span className="tag">{t.cohort}</span>
                    </Link>
                  );
                })}
              </div>
            </section>
          ))
      )}
    </div>
  );
}
