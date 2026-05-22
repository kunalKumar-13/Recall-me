import path from "node:path";
import { ADMIN_DATA_DIR } from "./paths";
import { fileMtime, readJSON } from "./fsx";
import { loadAlpha, type TrustCounts } from "./alpha";

/**
 * Trust surface. Two layers:
 *
 *   - `cards`    — the baked operator cards from `data/trust.json`
 *                  (kept for visual continuity with the pre-6H room).
 *   - `live`     — the 6-kind recovery-ledger aggregation, re-derived
 *                  by `loadAlpha()` on every request. Always fresh.
 *
 * The dashboard's *Trust* panel renders the live block; the baked
 * cards are exposed for surfaces that want the older shape.
 */

export interface TrustCard {
  id: string;
  label: string;
  count: number | string;
  detail: string;
  state: "green" | "yellow" | "red";
}

export interface TrustSnapshot {
  cards: TrustCard[];
  baked_mtime: string | null;
  live: TrustCounts;
  ledger_mtime: string | null;
}

export async function loadTrustSnapshot(): Promise<TrustSnapshot> {
  const bakedPath = path.join(ADMIN_DATA_DIR, "trust.json");
  const cards = await readJSON<TrustCard[]>(bakedPath, []);
  const bakedMtime = await fileMtime(bakedPath);

  const alpha = await loadAlpha();

  return {
    cards,
    baked_mtime: bakedMtime,
    live: alpha.trust,
    ledger_mtime: alpha.ledger_mtime,
  };
}
