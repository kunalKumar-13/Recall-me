import type { Verdict } from "../../lib/loaders/fsx";

/**
 * The single green/yellow/red pill the dashboard reuses everywhere.
 * Three colours + a `mute` for "we don't have data yet, that's not
 * a failure" — matches the daily-loop loader's `verdict()`.
 */
export function VerdictPill({
  value,
  label,
}: {
  value: Verdict;
  label?: string;
}) {
  return <span className={`pill ${value}`}>{label ?? value}</span>;
}
