import { Sparkline } from "./Sparkline";
import type { SparkSeries } from "../lib/types";

/**
 * Six sparklines, one per metric, in a calm 3-up grid. No live
 * range toggle (no JS for now — the data file is the source) but
 * the toggle is rendered statically so the founder can see the
 * intent: 7d / 30d / all. A future client-side variant can swap it
 * for a real selector when the cohort grows past one series.
 */
export function TractionRoom({ series }: { series: SparkSeries[] }) {
  if (series.length === 0) {
    return (
      <div className="card empty">no traction.json yet</div>
    );
  }
  return (
    <div className="grid grid-3">
      {series.map((s) => {
        const last = s.values[s.values.length - 1]?.v;
        const first = s.values[0]?.v;
        const delta =
          typeof last === "number" && typeof first === "number"
            ? last - first
            : 0;
        return (
          <div key={s.id} className="card spark-card">
            <div className="spark-row">
              <div>
                <div className="health-label">{s.label}</div>
                <div className="health-value" style={{ fontSize: 18 }}>
                  {formatValue(last, s.unit)}
                  <span
                    className="health-unit"
                    style={{ color: delta >= 0 ? "var(--ok)" : "var(--danger)" }}
                  >
                    {delta >= 0 ? "+" : ""}
                    {formatValue(delta, s.unit, true)}
                  </span>
                </div>
              </div>
              <Sparkline values={s.values} />
            </div>
            <div className="health-foot">
              {s.values.length}-day series ·{" "}
              <span className="kv-mono">
                {s.values[0]?.d} → {s.values[s.values.length - 1]?.d}
              </span>
            </div>
          </div>
        );
      })}
      <div className="card" style={{ padding: "10px 14px", gridColumn: "1 / -1" }}>
        <div className="range-toggle" aria-label="(static — no live selector)">
          <span>7d</span>
          <span className="active">30d</span>
          <span>all</span>
        </div>
      </div>
    </div>
  );
}

function formatValue(v: number | undefined, unit?: string, isDelta = false): string {
  if (v === undefined || v === null) return "—";
  if (unit === "%") return `${(v * 100).toFixed(isDelta ? 0 : 0)}%`;
  return `${v}`;
}
