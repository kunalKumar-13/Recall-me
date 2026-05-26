import path from "node:path";
import fs from "node:fs/promises";
import { RECALL_HOME, ALPHA_DIR, ADMIN_DATA_DIR } from "./paths";
import { exists, fileMtime, readJSONL, type Verdict } from "./fsx";

/**
 * Phase 6J — log/journal reader.
 *
 * "Logs" in Recall means *any append-only file the operator might
 * want to scan in order to understand what happened*. The directive
 * names five surfaces — doctor / recovery / daily / alpha / release
 * — and the loader matches each to a concrete path under
 * `~/.recall/` or `alpha/`. **No** ad-hoc parsing; every reader is
 * line-based JSON, which is the format every Recall-owned file
 * already uses.
 *
 * Lines are pre-redacted before they ever reach disk (the
 * trust-ledger contract), so the dashboard surfaces them verbatim.
 */

export interface LogEntry {
  ts: string | null;          // ISO date if present, else null
  level: string | null;       // "info" | "warn" | "error" | etc.
  message: string;            // the raw line, with the JSON noise stripped
  raw: Record<string, unknown>;
}

export interface LogSource {
  id: string;
  label: string;
  path: string;
  mtime: string | null;
  exists: boolean;
  kind: "jsonl" | "json";
  entries: LogEntry[];
  verdict: Verdict;
}

const SOURCES: { id: string; label: string; relpath: string; kind: "jsonl" | "json" }[] = [
  { id: "doctor",   label: "doctor",   relpath: path.join(RECALL_HOME, "doctor.jsonl"),       kind: "jsonl" },
  { id: "recovery", label: "recovery", relpath: path.join(ALPHA_DIR, "recovery_journal.json"), kind: "json"  },
  { id: "daily",    label: "daily",    relpath: path.join(RECALL_HOME, "daily_loop.jsonl"),   kind: "jsonl" },
  { id: "alpha",    label: "alpha",    relpath: path.join(ALPHA_DIR, "alpha_report.md"),      kind: "jsonl" },
  { id: "release",  label: "release",  relpath: path.join(ADMIN_DATA_DIR, "release.json"),    kind: "json"  },
];


function _flatten(raw: Record<string, unknown>): LogEntry {
  // Heuristic: pick the first stringish field as the message; pluck
  // common timestamp + level fields if present.
  const ts = (raw.ts as string) || (raw.date as string) || (raw.generated_at as string) || null;
  const level = (raw.level as string) || (raw.kind as string) || null;
  let message = "";
  if (typeof raw.message === "string") message = raw.message;
  else if (typeof raw.label === "string") message = raw.label;
  else if (typeof raw.investigation === "string") message = raw.investigation;
  else message = JSON.stringify(raw);
  return { ts, level, message, raw };
}


async function _readJSONLBest(file: string): Promise<LogEntry[]> {
  const rows = await readJSONL<Record<string, unknown>>(file);
  return rows.map(_flatten);
}


async function _readJSONBest(file: string): Promise<LogEntry[]> {
  try {
    const text = await fs.readFile(file, "utf-8");
    const parsed = JSON.parse(text) as unknown;
    if (Array.isArray(parsed)) {
      return parsed.map((r) => _flatten(r as Record<string, unknown>));
    }
    if (parsed && typeof parsed === "object") {
      const obj = parsed as Record<string, unknown>;
      // recovery_journal.json shape — `entries: [...]`.
      if (Array.isArray(obj.entries)) {
        return (obj.entries as Record<string, unknown>[]).map(_flatten);
      }
      // Otherwise treat the object itself as a single entry.
      return [_flatten(obj)];
    }
    return [];
  } catch {
    return [];
  }
}


export async function loadLogSources(): Promise<LogSource[]> {
  const out: LogSource[] = [];
  for (const s of SOURCES) {
    const fileExists = await exists(s.relpath);
    const entries: LogEntry[] = fileExists
      ? (s.kind === "jsonl"
          ? await _readJSONLBest(s.relpath)
          : await _readJSONBest(s.relpath))
      : [];
    const mtime = await fileMtime(s.relpath);
    const verdict: Verdict = !fileExists
      ? "mute"
      : entries.length === 0
        ? "yellow"
        : "green";
    out.push({
      id: s.id,
      label: s.label,
      path: s.relpath,
      mtime,
      exists: fileExists,
      kind: s.kind,
      entries,
      verdict,
    });
  }
  return out;
}


export async function loadOneLog(id: string): Promise<LogSource | null> {
  const all = await loadLogSources();
  return all.find((s) => s.id === id) ?? null;
}
