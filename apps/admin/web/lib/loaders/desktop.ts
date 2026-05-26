import path from "node:path";
import { EVENTS_DIR } from "./paths";
import { fileMtime, listDir, readJSONL } from "./fsx";

/**
 * Phase 6M — desktop loader.
 *
 * Streams the local `~/.recall/events/YYYY-MM-DD.jsonl` files and
 * filters for `desktop_window` events. Aggregates by app (focus
 * time + session count + last-seen) so the founder's `/desktop`
 * page can show the *top tools* + *session time* the directive
 * names.
 *
 * Metadata only — the loader never reads a screenshot, never reads
 * any byte the watcher didn't put on disk. Window titles are
 * exposed verbatim (the OS already exposed them); paths are
 * exposed when the watcher captured them.
 *
 * Window: the last `days` per-day jsonl files. Default 7.
 */

export interface DesktopEvent {
  ts: string;                    // ISO from the JSONL line's outer `ts`
  app: string;
  title: string;
  duration: number;
  focus_start: string;
  focus_end: string;
  switch_count: number;
  path: string | null;
}

export interface AppAggregate {
  app: string;
  events: number;
  total_seconds: number;
  longest_seconds: number;
  switch_count: number;
  last_seen: string;
  titles_sampled: string[];      // first 5 distinct titles for the founder's read
}

export interface DesktopSnapshot {
  events: DesktopEvent[];
  apps: AppAggregate[];
  total_events: number;
  total_seconds: number;
  unique_apps: number;
  events_dir: string;
  events_dir_mtime: string | null;
  window_days: number;
}


/** Stream-read the per-day JSONL files in the window. */
async function _read_window(days: number): Promise<DesktopEvent[]> {
  const files = (await listDir(EVENTS_DIR)).filter((f) => f.endsWith(".jsonl"));
  // Sort newest-first by name (YYYY-MM-DD sorts lexically).
  files.sort().reverse();
  const out: DesktopEvent[] = [];
  for (const f of files.slice(0, days)) {
    const rows = await readJSONL<Record<string, unknown>>(path.join(EVENTS_DIR, f));
    for (const r of rows) {
      if ((r.kind ?? "") !== "desktop_window") continue;
      const payload = (r.payload ?? {}) as Record<string, unknown>;
      out.push({
        ts: String(r.ts ?? ""),
        app: String(payload.app ?? "(unknown)"),
        title: String(payload.title ?? ""),
        duration: Number(payload.duration ?? 0),
        focus_start: String(payload.focus_start ?? ""),
        focus_end: String(payload.focus_end ?? ""),
        switch_count: Number(payload.switch_count ?? 1),
        path: payload.path == null ? null : String(payload.path),
      });
    }
  }
  return out;
}


function _aggregate(events: DesktopEvent[]): AppAggregate[] {
  const byApp = new Map<string, AppAggregate>();
  for (const e of events) {
    const a = byApp.get(e.app) ?? {
      app: e.app,
      events: 0,
      total_seconds: 0,
      longest_seconds: 0,
      switch_count: 0,
      last_seen: e.focus_end || e.ts,
      titles_sampled: [],
    };
    a.events += 1;
    a.total_seconds += e.duration;
    a.longest_seconds = Math.max(a.longest_seconds, e.duration);
    a.switch_count += e.switch_count;
    if ((e.focus_end || e.ts) > a.last_seen) a.last_seen = e.focus_end || e.ts;
    if (e.title && a.titles_sampled.length < 5 && !a.titles_sampled.includes(e.title)) {
      a.titles_sampled.push(e.title);
    }
    byApp.set(e.app, a);
  }
  return Array.from(byApp.values()).sort((a, b) => b.total_seconds - a.total_seconds);
}


export async function loadDesktop(days = 7): Promise<DesktopSnapshot> {
  const events = await _read_window(days);
  const apps = _aggregate(events);
  return {
    events,
    apps,
    total_events: events.length,
    total_seconds: events.reduce((s, e) => s + e.duration, 0),
    unique_apps: apps.length,
    events_dir: EVENTS_DIR,
    events_dir_mtime: await fileMtime(EVENTS_DIR),
    window_days: days,
  };
}
