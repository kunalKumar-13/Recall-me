import path from "node:path";
import os from "node:os";

/**
 * Single source of truth for every filesystem location the control
 * room reads. Centralised here so a path move or a config-dir env
 * override doesn't require hunting through six loaders.
 *
 * The admin web app runs from `apps/admin/web/`, so the repo root
 * is three `..` segments up. The user's local Recall data lives at
 * `~/.recall/` on every supported platform.
 */

export const REPO_ROOT = path.resolve(process.cwd(), "..", "..", "..");

export const ADMIN_DATA_DIR = path.resolve(REPO_ROOT, "apps", "admin", "data");
export const ADMIN_ROOT_DIR = path.resolve(REPO_ROOT, "apps", "admin");
export const ALPHA_DIR = path.resolve(REPO_ROOT, "alpha");
export const ALPHA_USERS_DIR = path.resolve(ALPHA_DIR, "users");
export const RECOVERY_JOURNAL = path.resolve(ALPHA_DIR, "recovery_journal.json");
export const RELEASE_STATE = path.resolve(ADMIN_ROOT_DIR, "release_state.json");

export const RECALL_HOME = process.env.RECALL_HOME
  ? path.resolve(process.env.RECALL_HOME)
  : path.resolve(os.homedir(), ".recall");

export const DAILY_LOOP_LOG = path.resolve(RECALL_HOME, "daily_loop.jsonl");
export const DAILY_LOOP_STATE = path.resolve(RECALL_HOME, "daily_loop_state.json");
export const DEMO_FILE = path.resolve(RECALL_HOME, "demo.json");
export const EVENTS_DIR = path.resolve(RECALL_HOME, "events");
export const CONFIG_FILE = path.resolve(RECALL_HOME, "config.json");
