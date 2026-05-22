import path from "node:path";
import {
  RECALL_HOME,
  EVENTS_DIR,
  CONFIG_FILE,
  DEMO_FILE,
} from "./paths";
import { exists, fileMtime, listDir, readJSON, type Verdict } from "./fsx";

/**
 * System Room reader.
 *
 * The dashboard's *System* panel surfaces what `recall doctor` would
 * report on this same machine, derived directly from the filesystem
 * — daemon presence (instance lock), event flow (jsonl mtime),
 * extension activity (last browser event), launcher lock health,
 * protocol registration (where detectable), version drift.
 *
 * No daemon ping. The page is server-rendered on the founder's
 * laptop; reading the local `~/.recall/` files is the cheapest
 * possible truth.
 */

export interface SystemCheck {
  id: string;
  label: string;
  state: Verdict;
  detail: string;
}

export interface SystemSnapshot {
  recall_home: string;
  recall_home_exists: boolean;
  checks: SystemCheck[];
  generated_at: string;
}

async function _eventsCheck(): Promise<SystemCheck> {
  const files = (await listDir(EVENTS_DIR)).filter((f) =>
    f.endsWith(".jsonl"),
  );
  if (files.length === 0) {
    return {
      id: "events",
      label: "Events",
      state: "yellow",
      detail: "no JSONL files yet (fresh install)",
    };
  }
  let last: string | null = null;
  for (const f of files) {
    const m = await fileMtime(path.join(EVENTS_DIR, f));
    if (m && (!last || m > last)) last = m;
  }
  return {
    id: "events",
    label: "Events",
    state: "green",
    detail: `${files.length} day-file(s); newest ${last ?? "unknown"}`,
  };
}

async function _instanceLockCheck(): Promise<SystemCheck> {
  const lockPath = path.join(RECALL_HOME, "instance.lock");
  if (!(await exists(lockPath))) {
    return {
      id: "launcher",
      label: "Launcher lock",
      state: "yellow",
      detail: "no instance.lock (launcher not running)",
    };
  }
  const m = await fileMtime(lockPath);
  return {
    id: "launcher",
    label: "Launcher lock",
    state: "green",
    detail: `instance.lock present (touched ${m ?? "—"})`,
  };
}

async function _configCheck(): Promise<SystemCheck> {
  if (!(await exists(CONFIG_FILE))) {
    return {
      id: "config",
      label: "Config",
      state: "yellow",
      detail: "no config.json — first-run state",
    };
  }
  const cfg = await readJSON<Record<string, unknown>>(CONFIG_FILE, {});
  const folders = Array.isArray(cfg.indexed_folders) ? cfg.indexed_folders.length : 0;
  return {
    id: "config",
    label: "Config",
    state: folders > 0 ? "green" : "yellow",
    detail: `${folders} folder(s) indexed`,
  };
}

async function _demoCheck(): Promise<SystemCheck> {
  if (!(await exists(DEMO_FILE))) {
    return {
      id: "demo",
      label: "Demo overlay",
      state: "green",
      detail: "no demo.json (default `available`)",
    };
  }
  const demo = await readJSON<Record<string, unknown>>(DEMO_FILE, {});
  const state = String(demo.state || "available");
  return {
    id: "demo",
    label: "Demo overlay",
    state: state === "active" ? "yellow" : "green",
    detail: `state = ${state}`,
  };
}

async function _recallHomeCheck(): Promise<SystemCheck> {
  const ok = await exists(RECALL_HOME);
  return {
    id: "home",
    label: "~/.recall",
    state: ok ? "green" : "yellow",
    detail: ok ? RECALL_HOME : `${RECALL_HOME} (not created yet)`,
  };
}

export async function loadSystemSnapshot(): Promise<SystemSnapshot> {
  const checks = await Promise.all([
    _recallHomeCheck(),
    _configCheck(),
    _eventsCheck(),
    _instanceLockCheck(),
    _demoCheck(),
  ]);
  return {
    recall_home: RECALL_HOME,
    recall_home_exists: await exists(RECALL_HOME),
    checks,
    generated_at: new Date().toISOString(),
  };
}
