import { loadDailyLoop } from "../../lib/loaders";
import { DailyLoopPanel } from "../../components/panels/DailyLoopPanel";

export const dynamic = "force-dynamic";

/**
 * `/daily-loop` — the Phase 6F counter deep-dive. Today + yesterday
 * + 7-day window + per-counter heatmap + the three signals with
 * green/yellow/red verdicts.
 */
export default async function DailyLoopPage() {
  const summary = await loadDailyLoop(7);
  return (
    <div className="page">
      <header className="page-header">
        <div>
          <h1 className="page-title">Daily loop</h1>
          <div className="page-subtitle">
            live read from <code>~/.recall/daily_loop.jsonl</code>
          </div>
        </div>
      </header>
      <section className="section">
        <DailyLoopPanel summary={summary} />
      </section>
    </div>
  );
}
