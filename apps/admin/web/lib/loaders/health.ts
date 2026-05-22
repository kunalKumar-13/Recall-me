import path from "node:path";
import { ADMIN_DATA_DIR, RECALL_HOME, EVENTS_DIR } from "./paths";
import { exists, fileMtime, listDir, readJSON } from "./fsx";

/**
 * Engine-health snapshot. Derives from three sources, in order of
 * authority:
 *
 *   1. `apps/admin/data/health.json`     — baked by `bake_data.py`
 *   2. `~/.recall/`                       — live filesystem state
 *      (config.json present, events/ has files, log mtime)
 *   3. derived booleans (recovery layer + extension pairing)
 *
 * No hardcoded card values — every number on the dashboard's
 * health surface is a live read or comes from the baked file.
 */

export interface HealthCard {
  id: string;
  label: string;
  value: number | string;
  unit?: string;
  foot?: string;
  health: "green" | "yellow" | "red" | "mute";
}

export interface HealthSnapshot {
  baked: HealthCard[];
  live: {
    recall_home_exists: boolean;
    events_files: number;
    last_event_mtime: string | null;
    config_present: boolean;
  };
  baked_mtime: string | null;
}

export async function loadHealthSnapshot(): Promise<HealthSnapshot> {
  const bakedPath = path.join(ADMIN_DATA_DIR, "health.json");
  const baked = await readJSON<HealthCard[]>(bakedPath, []);
  const bakedMtime = await fileMtime(bakedPath);

  const recallHomeExists = await exists(RECALL_HOME);
  const eventsFiles = (await listDir(EVENTS_DIR)).filter((f) =>
    f.endsWith(".jsonl"),
  );
  let lastEventMtime: string | null = null;
  for (const f of eventsFiles) {
    const m = await fileMtime(path.join(EVENTS_DIR, f));
    if (m && (!lastEventMtime || m > lastEventMtime)) lastEventMtime = m;
  }
  const configPresent = await exists(path.join(RECALL_HOME, "config.json"));

  return {
    baked,
    baked_mtime: bakedMtime,
    live: {
      recall_home_exists: recallHomeExists,
      events_files: eventsFiles.length,
      last_event_mtime: lastEventMtime,
      config_present: configPresent,
    },
  };
}
