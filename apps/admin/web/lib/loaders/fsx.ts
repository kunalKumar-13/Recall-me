import fs from "node:fs/promises";

/**
 * Defensive filesystem helpers. Every call here returns either the
 * parsed content or a typed fallback — never an exception. The
 * dashboard's *honest empty* rule lives here: when a file does not
 * exist, the founder sees a calm zero, not a 500 page.
 */

export async function readJSON<T>(file: string, fallback: T): Promise<T> {
  try {
    const text = await fs.readFile(file, "utf-8");
    return JSON.parse(text) as T;
  } catch {
    return fallback;
  }
}

/**
 * Append-only JSONL reader. Skips blank lines and lines that fail
 * to parse — pre-6E ledger entries that don't match the current
 * shape still flow through (per the `_compute_trust_pct` legacy
 * mapping).
 */
export async function readJSONL<T>(file: string): Promise<T[]> {
  let text: string;
  try {
    text = await fs.readFile(file, "utf-8");
  } catch {
    return [];
  }
  const out: T[] = [];
  for (const raw of text.split(/\r?\n/)) {
    const line = raw.trim();
    if (!line) continue;
    try {
      out.push(JSON.parse(line) as T);
    } catch {
      // Skip silently. Bad lines are pre-redacted notes or a half-
      // flushed write; the file is allowed to degrade.
    }
  }
  return out;
}

export async function listDir(dir: string): Promise<string[]> {
  try {
    return await fs.readdir(dir);
  } catch {
    return [];
  }
}

export async function exists(file: string): Promise<boolean> {
  try {
    await fs.access(file);
    return true;
  } catch {
    return false;
  }
}

export async function fileMtime(file: string): Promise<string | null> {
  try {
    const stat = await fs.stat(file);
    return stat.mtime.toISOString();
  } catch {
    return null;
  }
}

/**
 * Generic green/yellow/red mapper. The exact thresholds belong to
 * the per-domain loader; this is the *vocabulary*: anything that
 * resolves to a verdict in the UI uses the same three strings.
 */
export type Verdict = "green" | "yellow" | "red" | "mute";

export function pct(num: number, den: number): number | null {
  if (!den || den < 0) return null;
  return Math.round((num / den) * 100);
}
