/**
 * Shapes the admin UI reads from `apps/admin/data/`.
 *
 * Everything here is fed by a *file* the founder placed in
 * `apps/admin/data/`. There is no network call, no analytics SDK,
 * no auto-collected metric — the data model is intentionally small
 * and human-typable so an empty / partial state is the default and
 * a full state is what the founder *imported* themselves.
 */

export type Health = "green" | "yellow" | "red" | "mute";

export interface HealthCard {
  id: string;
  label: string;
  value: number | string;
  unit?: string;
  foot?: string;
  health: Health;
}

export interface SparkPoint {
  d: string; // ISO date (day granularity only — TRUST_LEDGER contract)
  v: number;
}

export interface SparkSeries {
  id: string;
  label: string;
  unit?: string;
  values: SparkPoint[];
}

export interface CohortCard {
  id: string;
  label: string;
  status: "forming" | "active" | "planned" | "paused";
  devices: number;
  returning: number;
  feedback_count: number;
  health: Health;
  notes?: string;
}

export interface ReleaseStatus {
  current_version: string;
  next_milestone: string;
  installer: "ready" | "blocked" | "partial";
  mac: "supported" | "preview" | "source-only";
  signing: "signed" | "unsigned";
  screenshots: "complete" | "partial" | "missing";
  go_no_go: "GO" | "PARTIAL" | "NO-GO";
  blocked: string[];
}

export type TrustState = "green" | "yellow" | "red";

export interface TrustCard {
  id: string;
  label: string;
  count: number | string;
  detail: string;
  state: TrustState;
}

export type FeedbackTag =
  | "pain"
  | "confusion"
  | "trust"
  | "bug"
  | "feature";

export interface FeedbackItem {
  id: string;
  date: string; // YYYY-MM-DD
  cohort: string;
  tag: FeedbackTag;
  quote: string;
  note?: string;
}

export interface TimelinePhase {
  name: string;
  label: string;
  done_pct: number; // 0..100
  state: "done" | "partial" | "now" | "next";
}
