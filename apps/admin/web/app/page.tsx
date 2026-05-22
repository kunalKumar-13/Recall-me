import {
  loadAlpha,
  loadDailyLoop,
  loadHealthSnapshot,
  loadRelease,
  loadSystemSnapshot,
  loadTrustSnapshot,
} from "../lib/loaders";
import { AlphaPanel } from "../components/panels/AlphaPanel";
import { DailyLoopPanel } from "../components/panels/DailyLoopPanel";
import { HealthPanel } from "../components/panels/HealthPanel";
import { ReleasePanel } from "../components/panels/ReleasePanel";
import { SystemPanel } from "../components/panels/SystemPanel";
import { TrustPanel } from "../components/panels/TrustPanel";

export const dynamic = "force-dynamic";

/**
 * Phase 6H — control-room overview.
 *
 * One server component, six panels, every value live-derived.
 * The directive's *30-second understanding* lives here: this page
 * is what the founder opens first, and after one scroll they know
 * the engine's health, the cohort's pulse, the day-loop's state,
 * the release verdict, and what `~/.recall/` looks like right now.
 *
 * Each panel renders in `compact` mode where applicable so the
 * overview reads as a *briefing*, not a deep-dive. The deep dives
 * live at `/alpha`, `/trust`, `/daily-loop`, `/release`, `/system`.
 */
export default async function OverviewPage() {
  const [health, alpha, daily, trust, release, system] = await Promise.all([
    loadHealthSnapshot(),
    loadAlpha(),
    loadDailyLoop(7),
    loadTrustSnapshot(),
    loadRelease(),
    loadSystemSnapshot(),
  ]);

  return (
    <div className="page">
      <header className="page-header">
        <div>
          <h1 className="page-title">Overview</h1>
          <div className="page-subtitle">
            local-first · no server · no auth · no telemetry
          </div>
        </div>
        <div className="page-subtitle">
          generated {new Date().toISOString()}
        </div>
      </header>

      <section className="section">
        <HealthPanel snapshot={health} />
      </section>

      <section className="section">
        <AlphaPanel data={alpha} compact />
      </section>

      <section className="section">
        <DailyLoopPanel summary={daily} compact />
      </section>

      <section className="section">
        <TrustPanel snapshot={trust} compact />
      </section>

      <section className="section">
        <ReleasePanel release={release} compact />
      </section>

      <section className="section">
        <SystemPanel snapshot={system} />
      </section>

      <footer className="footer" style={{ marginTop: 36, fontSize: 12, color: "var(--ink-3)" }}>
        sources: <code>apps/admin/data/</code> · <code>alpha/users/</code> ·{" "}
        <code>alpha/recovery_journal.json</code> · <code>~/.recall/</code>
      </footer>
    </div>
  );
}
