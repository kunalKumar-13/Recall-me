import path from "node:path";
import { ALPHA_USERS_DIR, RECOVERY_JOURNAL } from "./paths";
import { fileMtime, listDir, pct, readJSON, type Verdict } from "./fsx";

/**
 * Live reader for the alpha cohort tree (`alpha/users/<cohort>/<handle>/status.json`)
 * + the recovery ledger (`alpha/recovery_journal.json`).
 *
 * Mirrors `app/core/alpha_cli._compute_trust_pct` + `cmd_export` so the
 * dashboard is *not* dependent on the founder running `recall founder
 * bake`. Every count here is re-derived from the source files on
 * every request.
 */

export const COHORTS = [
  "alpha-001",
  "alpha-002",
  "friends",
  "builders",
  "students",
] as const;
export type Cohort = (typeof COHORTS)[number];

export interface TesterRecord {
  handle: string;
  cohort: string;
  install_date: string | null;
  platform: string | null;
  install_ok: string | null;
  install_minutes: number | null;
  installer_version: string | null;
  extension: string | null;
  day1: string | null;
  day2: string | null;
  day3: string | null;
  first_recovery: string | null;
  first_resume_ok: string | null;
  kept_using: string | null;
  wow_moment: string | null;
  confusion: string | null;
  drop_reason: string | null;
  feedback_returned: boolean;
  notes: string;
}

export interface CohortSummary {
  cohort: string;
  installs: number;
  returning: number;
  first_recoveries: number;
  drops: number;
  testers: TesterRecord[];
}

export interface JournalEntry {
  date: string;
  tester: string;
  cohort: string;
  kind?: string;
  investigation?: string;
  recovered?: string;
  notes?: string;
  return_after_gap?: boolean | null;
  time_to_resume?: number | null;
  accepted?: boolean | null;
  wrong?: boolean | null;
}

export interface TrustCounts {
  shown: number;
  accepted: number;
  ignored: number;
  correct_silence: number;
  bad_recovery: number;
  resume_ok: number;
  pct_correct: number | null;
  total_entries: number;
  entries_by_tester: Record<string, number>;
  entries_with_return: number;
  median_time_to_resume_s: number | null;
}

export interface AlphaExport {
  generated_at: string;
  installs: number;
  returning: number;
  recoveries: number;
  drops: number;
  install_fails: number;
  wrong_recoveries: number;
  drop_reasons: Record<string, number>;
  cohorts: CohortSummary[];
  testers: TesterRecord[];
  trust: TrustCounts;
  verdicts: Record<string, Verdict>;
  ledger_mtime: string | null;
  cohort_mtime: string | null;
}

function _yes(v: string | null | undefined): boolean {
  return v === "yes";
}

function _emptyTester(handle: string, cohort: string): TesterRecord {
  return {
    handle, cohort,
    install_date: null, platform: null, install_ok: null,
    install_minutes: null, installer_version: null, extension: null,
    day1: null, day2: null, day3: null,
    first_recovery: null, first_resume_ok: null, kept_using: null,
    wow_moment: null, confusion: null, drop_reason: null,
    feedback_returned: false, notes: "",
  };
}

async function _loadCohort(cohort: string): Promise<CohortSummary> {
  const base = path.join(ALPHA_USERS_DIR, cohort);
  const entries = await listDir(base);
  const testers: TesterRecord[] = [];
  let installs = 0, returning = 0, first_recoveries = 0, drops = 0;
  for (const handle of entries) {
    if (handle.startsWith(".") || handle.startsWith("_")) continue;
    const statusFile = path.join(base, handle, "status.json");
    const raw = await readJSON<Partial<TesterRecord> | null>(statusFile, null);
    if (!raw) continue;
    const t: TesterRecord = { ..._emptyTester(handle, cohort), ...raw };
    if (!t.handle) t.handle = handle;
    if (!t.cohort) t.cohort = cohort;
    testers.push(t);
    installs += 1;
    const yesDays = [t.day1, t.day2, t.day3].filter(_yes).length;
    if (yesDays >= 2) returning += 1;
    if (t.first_recovery && t.first_recovery !== "none yet") first_recoveries += 1;
    if (t.drop_reason && !["n/a", ""].includes(t.drop_reason)) drops += 1;
  }
  return { cohort, installs, returning, first_recoveries, drops, testers };
}

function _aggregateTrust(entries: JournalEntry[]): TrustCounts {
  const counts: Record<string, number> = {
    shown: 0, accepted: 0, ignored: 0,
    correct_silence: 0, bad_recovery: 0, resume_ok: 0,
  };
  const entriesByTester: Record<string, number> = {};
  let entriesWithReturn = 0;
  const t2r: number[] = [];

  for (const e of entries) {
    const tester = e.tester || "(unknown)";
    entriesByTester[tester] = (entriesByTester[tester] || 0) + 1;

    if (typeof e.return_after_gap === "boolean" && e.return_after_gap) {
      entriesWithReturn += 1;
    }
    if (typeof e.time_to_resume === "number") {
      t2r.push(e.time_to_resume);
    }

    const kind = e.kind;
    if (typeof kind === "string" && kind in counts) {
      counts[kind] += 1;
      continue;
    }
    // Legacy mapping — matches app/core/alpha_cli._compute_trust_pct.
    if (e.accepted === true && e.wrong === true) {
      counts.bad_recovery += 1;
      counts.shown += 1;
    } else if (e.accepted === true && e.wrong === false) {
      counts.resume_ok += 1;
      counts.accepted += 1;
      counts.shown += 1;
    } else if (e.accepted === false) {
      counts.ignored += 1;
      counts.shown += 1;
    }
  }

  const total = counts.shown;
  const correct = counts.resume_ok + counts.correct_silence;
  const median = t2r.length
    ? t2r.sort((a, b) => a - b)[Math.floor(t2r.length / 2)]
    : null;

  return {
    shown: counts.shown,
    accepted: counts.accepted,
    ignored: counts.ignored,
    correct_silence: counts.correct_silence,
    bad_recovery: counts.bad_recovery,
    resume_ok: counts.resume_ok,
    pct_correct: pct(correct, total),
    total_entries: entries.length,
    entries_by_tester: entriesByTester,
    entries_with_return: entriesWithReturn,
    median_time_to_resume_s: median,
  };
}

function _verdicts(args: {
  installs: number;
  returning: number;
  recoveries: number;
  trust: TrustCounts;
  worstDropCount: number;
  installFails: number;
}): Record<string, Verdict> {
  const { installs, returning, recoveries, trust, worstDropCount, installFails } = args;
  return {
    installs: installs >= 5 ? "green" : installs >= 1 ? "yellow" : "red",
    returning: returning >= 2 ? "green" : returning >= 1 ? "yellow" : "red",
    first_recoveries: recoveries >= 3 ? "green" : recoveries >= 1 ? "yellow" : "red",
    trust: trust.shown === 0
      ? "yellow"
      : (trust.pct_correct ?? 0) >= 80
        ? "green"
        : (trust.pct_correct ?? 0) >= 50
          ? "yellow"
          : "red",
    drops: worstDropCount >= 2 ? "red" : worstDropCount >= 1 ? "yellow" : "green",
    install_fails: installFails >= 2 ? "red" : installFails >= 1 ? "yellow" : "green",
  };
}

export async function loadAlpha(): Promise<AlphaExport> {
  const cohorts = await Promise.all(COHORTS.map(_loadCohort));
  const testers = cohorts.flatMap((c) => c.testers);
  const installs = testers.length;
  const returning = cohorts.reduce((a, c) => a + c.returning, 0);
  const recoveries = cohorts.reduce((a, c) => a + c.first_recoveries, 0);
  const drops = cohorts.reduce((a, c) => a + c.drops, 0);

  let install_fails = 0;
  let wrong_recoveries = 0;
  const drop_reasons: Record<string, number> = {};
  for (const t of testers) {
    if (t.install_ok === "no" || t.install_ok === "partial") install_fails += 1;
    if (t.first_resume_ok === "wrong work") wrong_recoveries += 1;
    if (t.drop_reason && !["n/a", ""].includes(t.drop_reason)) {
      drop_reasons[t.drop_reason] = (drop_reasons[t.drop_reason] || 0) + 1;
    }
  }

  const journal = await readJSON<{ entries?: JournalEntry[] }>(RECOVERY_JOURNAL, {});
  const entries = Array.isArray(journal.entries) ? journal.entries : [];
  const trust = _aggregateTrust(entries);

  const worstDropCount = Object.values(drop_reasons).reduce((a, b) => Math.max(a, b), 0);

  const verdicts = _verdicts({
    installs, returning, recoveries: recoveries,
    trust, worstDropCount, installFails: install_fails,
  });

  const [ledgerMtime, cohortMtime] = await Promise.all([
    fileMtime(RECOVERY_JOURNAL),
    fileMtime(ALPHA_USERS_DIR),
  ]);

  return {
    generated_at: new Date().toISOString(),
    installs, returning, recoveries, drops,
    install_fails, wrong_recoveries, drop_reasons,
    cohorts, testers, trust, verdicts,
    ledger_mtime: ledgerMtime,
    cohort_mtime: cohortMtime,
  };
}

export async function loadJournalEntries(): Promise<JournalEntry[]> {
  const j = await readJSON<{ entries?: JournalEntry[] }>(RECOVERY_JOURNAL, {});
  return Array.isArray(j.entries) ? j.entries : [];
}
