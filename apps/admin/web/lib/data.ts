import fs from "node:fs/promises";
import path from "node:path";
import type {
  CohortCard,
  FeedbackItem,
  HealthCard,
  ReleaseStatus,
  SparkSeries,
  TimelinePhase,
  TrustCard,
} from "./types";

/**
 * Server-side JSON loaders.
 *
 * Every loader reads a file the founder placed in
 * `apps/admin/data/`. If a file is missing or unreadable, the
 * loader returns an empty / default value — the page never throws,
 * never alarms, never tries to fetch from elsewhere. The whole
 * data plane is *what is on disk*, nothing more.
 */
const DATA = path.resolve(process.cwd(), "..", "data");

async function read<T>(name: string, fallback: T): Promise<T> {
  try {
    const text = await fs.readFile(path.join(DATA, name), "utf-8");
    return JSON.parse(text) as T;
  } catch {
    return fallback;
  }
}

// ── health overview ────────────────────────────────────────────────

export async function loadHealth(): Promise<HealthCard[]> {
  return read<HealthCard[]>("health.json", []);
}

// ── traction ───────────────────────────────────────────────────────

export async function loadTraction(): Promise<SparkSeries[]> {
  return read<SparkSeries[]>("traction.json", []);
}

// ── cohorts ────────────────────────────────────────────────────────

export async function loadCohorts(): Promise<CohortCard[]> {
  return read<CohortCard[]>("cohorts.json", []);
}

// ── release ────────────────────────────────────────────────────────

export async function loadRelease(): Promise<ReleaseStatus | null> {
  return read<ReleaseStatus | null>("release.json", null);
}

// ── trust ──────────────────────────────────────────────────────────

export async function loadTrust(): Promise<TrustCard[]> {
  return read<TrustCard[]>("trust.json", []);
}

// ── feedback ───────────────────────────────────────────────────────

export async function loadFeedback(): Promise<FeedbackItem[]> {
  return read<FeedbackItem[]>("feedback.json", []);
}

// ── timeline ───────────────────────────────────────────────────────

export async function loadTimeline(): Promise<TimelinePhase[]> {
  return read<TimelinePhase[]>("timeline.json", []);
}

// ── meta ───────────────────────────────────────────────────────────

export async function loadMeta(): Promise<{
  generated_at?: string;
  source_note?: string;
}> {
  return read("meta.json", { source_note: "no meta.json yet" });
}
