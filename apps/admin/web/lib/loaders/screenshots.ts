import path from "node:path";
import { SCREENSHOTS_DIR } from "./paths";
import { exists, fileMtime, listDir, type Verdict } from "./fsx";

/**
 * Phase 6J — screenshot manager.
 *
 * Scans `assets/screenshots/` and groups what's present into the six
 * named buckets the directive listed:
 *
 *   launcher-v2 · launcher-v3 · extension(-v2) · demo · alpha · top-level
 *
 * Each bucket reports `count` + `mtime` + a verdict (`green` when
 * the expected captures are all present; `yellow` when some are
 * missing; `mute` when the directory is empty). Missing markers
 * are exposed as `missing` so the directive's *missing markers*
 * surface lives here.
 */

export interface ScreenshotBucket {
  id: string;
  label: string;
  dir: string;
  exists: boolean;
  count: number;
  files: string[];
  mtime: string | null;
  expected: string[];
  missing: string[];
  verdict: Verdict;
}

const BUCKETS: { id: string; label: string; subdir: string | null; expected: string[] }[] = [
  { id: "launcher-v2", label: "launcher v2", subdir: "launcher-v2",
    expected: [
      "launcher-digest.png", "launcher-empty.png", "launcher-first-week.png",
      "launcher-loading.png", "launcher-offline.png",
      "recovery-card.png", "recovery-card-focused.png",
    ] },
  { id: "launcher-v3", label: "launcher v3", subdir: "launcher-v3",
    expected: [
      "digest.png", "continue.png", "empty.png", "trust.png", "focused.png",
    ] },
  { id: "extension-v2", label: "extension v2", subdir: "extension-v2",
    expected: [
      "extension-home.png", "extension-empty.png", "extension-recovery.png",
      "extension-repair.png", "extension-offline.png",
    ] },
  { id: "demo", label: "demo", subdir: "demo",
    expected: [
      "demo-launcher.png", "demo-extension.png", "demo-transition.png",
      "demo-extension-empty.png",
    ] },
  { id: "alpha", label: "alpha", subdir: "alpha",
    expected: [
      "alpha-control-room.png", "alpha-status.png", "alpha-empty.png",
    ] },
  { id: "extension-flat", label: "extension (legacy flat)", subdir: null,
    expected: [
      "extension-connected.png", "extension-empty.png", "extension-capturing.png",
      "extension-missing.png", "extension-disconnected.png", "extension-offline.png",
      "extension-loading.png",
    ] },
];


async function _scan(bucket: typeof BUCKETS[number]): Promise<ScreenshotBucket> {
  const dir = bucket.subdir
    ? path.join(SCREENSHOTS_DIR, bucket.subdir)
    : SCREENSHOTS_DIR;
  const dirExists = await exists(dir);
  let files: string[] = [];
  if (dirExists) {
    files = (await listDir(dir)).filter((f) => f.endsWith(".png"));
  }
  const fileset = new Set(files);
  // Legacy flat extension bucket only counts the directive-named PNGs
  // that sit at the screenshots root.
  const present = bucket.expected.filter((e) => fileset.has(e));
  const missing = bucket.expected.filter((e) => !fileset.has(e));
  const mtime = dirExists ? await fileMtime(dir) : null;
  const verdict: Verdict = !dirExists
    ? "mute"
    : missing.length === 0
      ? "green"
      : present.length > 0
        ? "yellow"
        : "red";
  return {
    id: bucket.id,
    label: bucket.label,
    dir,
    exists: dirExists,
    count: bucket.subdir ? files.length : present.length,
    files: bucket.subdir ? files : present,
    mtime,
    expected: bucket.expected,
    missing,
    verdict,
  };
}


export async function loadScreenshots(): Promise<ScreenshotBucket[]> {
  return Promise.all(BUCKETS.map(_scan));
}
