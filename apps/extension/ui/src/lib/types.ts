/**
 * Shapes the popup reads from the local Recall daemon. These mirror
 * the `/v1/*` responses loosely — the popup is defensive by design
 * (a memory surface must degrade calmly, never throw), so every
 * field that could be missing is optional and the mappers in
 * `api.ts` fill safe defaults.
 */

/** Where the popup is in its connection lifecycle. */
export type ConnectionState =
  | "loading" // first health check in flight
  | "connected" // daemon answered
  | "disconnected" // daemon not reachable
  | "reconnecting" // a retry is in flight
  | "offline"; // the browser itself reports no network

/**
 * The single observable state of the popup body. Derived from the
 * connection lifecycle + what the daemon returned. The popup renders
 * exactly one of these at a time; the state machine is the contract
 * between data and pixels.
 *
 * Phase 5H rules:
 *   - daemon dead / browser offline / a fetch in flight → one of the
 *     pre-connect states (`offline` / `loading` / `reconnecting` /
 *     `disconnected`).
 *   - daemon healthy + 0 ingested events + 0 memory rows → `empty`.
 *   - daemon healthy + events captured, no investigations / recovery
 *     yet → `capturing` (the "Recall is watching locally" surface).
 *   - investigations exist, no recovery → `investigations`.
 *   - a recovery is ready → `recovery` (the leading section).
 *
 * Invariant: if the daemon is healthy AND ingestedTotal > 0, the
 * `empty` state is forbidden — see `App.tsx`'s `derivePopupState`.
 */
export type PopupState =
  | "loading"
  | "reconnecting"
  | "offline"
  | "disconnected"
  | "empty"
  | "capturing"
  | "investigations"
  | "recovery"
  // Phase 6D — demo overlay. Engine is empty AND demo_mode is
  // `active`; the body renders the canned `WebSocket / Proposal
  // / Research` story on top of a quiet trust banner.
  | "demo";

export interface Health {
  ok: boolean;
  ingestedTotal: number;
  eventsToday: number;
}

/** One restorable investigation — the ContinueCard's subject. */
export interface Recovery {
  id: string;
  title: string;
  /** Deterministic caption, e.g. "2 tabs · 2 files · reopened after a 2-day gap". */
  caption: string;
  /** Parsed caption parts, one chip each. */
  chips: string[];
  tabCount: number;
  fileCount: number;
  /** URLs the popup can reopen directly (files open via the desktop app). */
  urls: string[];
}

/** A longer-lived topic — the InvestigationCard's subject. */
export interface Investigation {
  id: string;
  title: string;
  summary: string;
  surfaces: string[];
}

export type MemoryKind = "search" | "tab" | "chat";

export interface MemoryItem {
  kind: MemoryKind;
  label: string;
  detail: string;
  url?: string;
  /** Event timestamp (epoch seconds). Used by the Phase 6A timeline
   *  label; absent on rows where the API omits `ts` (defensive
   *  default is treated as "unknown time"). */
  ts?: number;
}

export interface Settings {
  captureBrowsing: boolean;
  captureSearches: boolean;
  captureChats: boolean;
  paused: boolean;
}

export const DEFAULT_SETTINGS: Settings = {
  captureBrowsing: true,
  captureSearches: true,
  captureChats: true,
  paused: false,
};

// ── Phase 6D — demo overlay ────────────────────────────────────────────

/** State machine for the first-run *Show example* demo. */
export type DemoStateKind =
  | "disabled"
  | "available"
  | "active"
  | "dismissed"
  | "completed";

/** The full demo payload the daemon returns when state === "active". */
export interface DemoPayload {
  recovery: Recovery;
  investigations: Investigation[];
  timeline: MemoryItem[];
  trust: { bannerTitle: string; bannerBody: string };
}

export interface DemoState {
  state: DemoStateKind;
  payload: DemoPayload | null;
}
