import type { DailyLoopSummary } from "../../lib/loaders";
import { PanelMeta } from "./HealthPanel";
import { VerdictPill } from "./Verdict";

/**
 * DailyLoopPanel — Phase 6F counters surfaced live.
 *
 * Three rows of numbers (today / yesterday / 7d window), three
 * derived signals with green/yellow/red pills, and a 7-day
 * heatmap per counter. Pure projection of `loadDailyLoop()`'s
 * return value — no hardcoded numbers.
 */
export function DailyLoopPanel({
  summary,
  compact = false,
}: {
  summary: DailyLoopSummary;
  compact?: boolean;
}) {
  const sig = summary.signals;
  const v = summary.verdicts;
  const w = summary.window;
  return (
    <div>
      <PanelMeta
        title="Daily loop"
        live="~/.recall/daily_loop.jsonl"
        mtime={summary.source.log_mtime}
        extra={`${summary.daysWithActivity} of ${w.days} day(s) with activity`}
      />

      <div className="grid grid-3">
        <SignalCard
          label="Continuity restored"
          pct={sig.continuity_restored}
          detail={`${w.recoveries_used} used / ${w.recoveries_shown} shown`}
          verdict={v.continuity_restored}
        />
        <SignalCard
          label="Return rate"
          pct={sig.return_rate}
          detail={`${w.returns} returns / ${w.day_started} days`}
          verdict={v.return_rate}
        />
        <SignalCard
          label="Resume quality"
          pct={sig.resume_quality}
          detail={`${w.resume_success} succeeded / ${w.recoveries_used} used`}
          verdict={v.resume_quality}
        />
      </div>

      {!compact && (
        <div className="card" style={{ marginTop: 14, overflow: "hidden" }}>
          <CounterRow
            label="started"
            today={summary.today.day_started}
            yest={summary.yesterday.day_started}
            window={w.day_started}
          />
          <CounterRow
            label="recoveries shown"
            today={summary.today.recoveries_shown}
            yest={summary.yesterday.recoveries_shown}
            window={w.recoveries_shown}
          />
          <CounterRow
            label="recoveries used"
            today={summary.today.recoveries_used}
            yest={summary.yesterday.recoveries_used}
            window={w.recoveries_used}
          />
          <CounterRow
            label="resume success"
            today={summary.today.resume_success}
            yest={summary.yesterday.resume_success}
            window={w.resume_success}
          />
          <CounterRow
            label="returns"
            today={summary.today.returns}
            yest={summary.yesterday.returns}
            window={w.returns}
          />
          <CounterRow
            label="investigations"
            today={summary.today.investigations_opened}
            yest={summary.yesterday.investigations_opened}
            window={w.investigations_opened}
          />
        </div>
      )}

      {!compact && (
        <div style={{ marginTop: 18 }}>
          <Heatmap summary={summary} />
        </div>
      )}
    </div>
  );
}

function SignalCard({
  label,
  pct,
  detail,
  verdict,
}: {
  label: string;
  pct: number | null;
  detail: string;
  verdict: "green" | "yellow" | "red" | "mute";
}) {
  return (
    <div className="card" style={{ padding: 14 }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "baseline" }}>
        <span className="section-title" style={{ marginBottom: 0 }}>{label}</span>
        <VerdictPill value={verdict} />
      </div>
      <div style={{ marginTop: 8, fontSize: 28, fontWeight: 600 }}>
        {pct === null ? "—" : `${pct}%`}
      </div>
      <div style={{ marginTop: 2, fontSize: 12, color: "var(--ink-3)" }}>{detail}</div>
    </div>
  );
}

function CounterRow({
  label,
  today,
  yest,
  window: w,
}: {
  label: string;
  today: number;
  yest: number;
  window: number;
}) {
  return (
    <div className="panel-row">
      <span className="panel-row-label">{label}</span>
      <span className="panel-row-detail">
        today {today} · yesterday {yest} · 7-day {w}
      </span>
      <span className="tag">{w}</span>
    </div>
  );
}

const BINS = [
  "day_started",
  "recoveries_shown",
  "recoveries_used",
  "resume_success",
  "returns",
] as const;

function Heatmap({ summary }: { summary: DailyLoopSummary }) {
  // 7-day cells per bin; saturation scales 0-4 against the row max.
  return (
    <div className="card" style={{ padding: 14 }}>
      <div className="section-title" style={{ marginBottom: 8 }}>7-day heatmap</div>
      {BINS.map((bin) => {
        const row = summary.history.map((d) => d[bin]);
        const rowMax = Math.max(1, ...row);
        return (
          <div key={bin} className="heatrow" style={{ margin: "6px 0" }}>
            <span className="heatrow-label">{bin}</span>
            {row.map((v, i) => {
              const tier = v === 0 ? 0 : Math.min(4, Math.ceil((v / rowMax) * 4));
              return (
                <span
                  key={i}
                  className="heatcell"
                  data-v={tier}
                  title={`${summary.history[i].date}: ${v}`}
                />
              );
            })}
          </div>
        );
      })}
    </div>
  );
}
