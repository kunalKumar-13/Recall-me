import { DAILY_LOOP_LOG, DAILY_LOOP_STATE } from "./paths";
import { fileMtime, pct, readJSON, readJSONL, type Verdict } from "./fsx";

/**
 * Live reader for the Phase 6F daily-loop layer.
 *
 * Mirrors `app/core/daily_loop.py:summary()` in TypeScript so the
 * dashboard never asks the daemon for the aggregation — it reads
 * `~/.recall/daily_loop.jsonl` (one JSON line per local day)
 * directly and reproduces the three derived signals.
 *
 * Empty file = honest zero; bad lines are skipped per `fsx.readJSONL`.
 */

export const COUNTER_BINS = [
  "day_started",
  "investigations_opened",
  "recoveries_shown",
  "recoveries_used",
  "returns",
  "resume_success",
] as const;

export type CounterBin = (typeof COUNTER_BINS)[number];

export type DayRecord = { date: string } & Record<CounterBin, number>;

export interface DailyLoopSummary {
  today: DayRecord;
  yesterday: DayRecord;
  window: Omit<DayRecord, "date"> & { days: number };
  daysWithActivity: number;
  signals: {
    continuity_restored: number | null;
    return_rate: number | null;
    resume_quality: number | null;
  };
  verdicts: {
    continuity_restored: Verdict;
    return_rate: Verdict;
    resume_quality: Verdict;
  };
  history: DayRecord[];
  source: {
    log_path: string;
    log_mtime: string | null;
    state_path: string;
    state_mtime: string | null;
    last_event_ts: number | null;
    last_return_ts: number | null;
  };
}

function emptyDay(d: string): DayRecord {
  const rec: Partial<DayRecord> = { date: d };
  for (const b of COUNTER_BINS) rec[b] = 0;
  return rec as DayRecord;
}

function dayISO(offset = 0, base = new Date()): string {
  const d = new Date(base);
  d.setDate(d.getDate() - offset);
  return d.toISOString().slice(0, 10);
}

function verdict(name: keyof DailyLoopSummary["signals"], p: number | null): Verdict {
  if (p === null) return "yellow"; // honest empty
  if (name === "continuity_restored") {
    return p >= 60 ? "green" : p >= 25 ? "yellow" : "red";
  }
  if (name === "return_rate") {
    return p >= 30 ? "green" : p >= 10 ? "yellow" : "red";
  }
  if (name === "resume_quality") {
    return p >= 80 ? "green" : p >= 50 ? "yellow" : "red";
  }
  return "mute";
}

export async function loadDailyLoop(days = 7): Promise<DailyLoopSummary> {
  const records = await readJSONL<Record<string, unknown>>(DAILY_LOOP_LOG);

  const byDay = new Map<string, DayRecord>();
  for (const r of records) {
    const d = String(r.date || "");
    if (!d) continue;
    const day = emptyDay(d);
    for (const b of COUNTER_BINS) {
      day[b] = Number(r[b] || 0);
    }
    byDay.set(d, day);
  }

  const todayKey = dayISO(0);
  const yestKey = dayISO(1);

  const today = byDay.get(todayKey) ?? emptyDay(todayKey);
  const yesterday = byDay.get(yestKey) ?? emptyDay(yestKey);

  const window: DailyLoopSummary["window"] = {
    days,
    day_started: 0,
    investigations_opened: 0,
    recoveries_shown: 0,
    recoveries_used: 0,
    returns: 0,
    resume_success: 0,
  };

  const history: DayRecord[] = [];
  let daysWithActivity = 0;
  for (let i = days - 1; i >= 0; i--) {
    const k = dayISO(i);
    const rec = byDay.get(k) ?? emptyDay(k);
    history.push(rec);
    let any = false;
    for (const b of COUNTER_BINS) {
      window[b] += rec[b];
      if (rec[b] > 0) any = true;
    }
    if (any) daysWithActivity += 1;
  }

  const signals = {
    continuity_restored: pct(window.recoveries_used, window.recoveries_shown),
    return_rate: pct(window.returns, Math.max(window.day_started, 1)),
    resume_quality: pct(window.resume_success, window.recoveries_used),
  };

  const verdicts = {
    continuity_restored: verdict("continuity_restored", signals.continuity_restored),
    return_rate: verdict("return_rate", signals.return_rate),
    resume_quality: verdict("resume_quality", signals.resume_quality),
  };

  const state = await readJSON<Record<string, number>>(DAILY_LOOP_STATE, {});
  const [logMtime, stateMtime] = await Promise.all([
    fileMtime(DAILY_LOOP_LOG),
    fileMtime(DAILY_LOOP_STATE),
  ]);

  return {
    today,
    yesterday,
    window,
    daysWithActivity,
    signals,
    verdicts,
    history,
    source: {
      log_path: DAILY_LOOP_LOG,
      log_mtime: logMtime,
      state_path: DAILY_LOOP_STATE,
      state_mtime: stateMtime,
      last_event_ts: typeof state.last_event_ts === "number" ? state.last_event_ts : null,
      last_return_ts: typeof state.last_return_ts === "number" ? state.last_return_ts : null,
    },
  };
}
