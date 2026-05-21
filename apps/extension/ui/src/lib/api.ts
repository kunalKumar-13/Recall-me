import {
  DEFAULT_SETTINGS,
  type Health,
  type Investigation,
  type MemoryItem,
  type Recovery,
  type Settings,
} from "./types";

/**
 * The daemon lives on loopback only. This is the *entire* network
 * surface of the extension — there is no other origin it ever talks
 * to. The host_permission in the manifest is scoped to exactly this.
 */
const BASE = "http://127.0.0.1:4545";

/** A health probe must fail fast — a slow popup is a broken popup. */
const HEALTH_TIMEOUT_MS = 1800;

async function getJSON<T>(path: string, timeoutMs = 2500): Promise<T | null> {
  try {
    const ctrl = new AbortController();
    const timer = setTimeout(() => ctrl.abort(), timeoutMs);
    const r = await fetch(`${BASE}${path}`, {
      cache: "no-store",
      signal: ctrl.signal,
    });
    clearTimeout(timer);
    if (!r.ok) return null;
    return (await r.json()) as T;
  } catch {
    // Defensive by contract: the popup never throws on a dead daemon.
    return null;
  }
}

export async function fetchHealth(): Promise<Health | null> {
  const data = await getJSON<Record<string, unknown>>(
    "/v1/health",
    HEALTH_TIMEOUT_MS,
  );
  if (!data) return null;
  return {
    ok: true,
    ingestedTotal: numberOf(data.ingested_total),
    eventsToday: numberOf(data.events_today ?? data.ingested_today),
  };
}

export async function fetchRecovery(): Promise<Recovery | null> {
  const data = await getJSON<Record<string, unknown>>("/v1/recovery/recent");
  const list = asArray(data?.candidates ?? data);
  if (list.length === 0) return null;
  const c = list[0] as Record<string, unknown>;

  const caption = stringOf(c.preview_caption);
  const chips = caption
    .split("·")
    .map((s) => s.trim())
    .filter(Boolean);
  const targets = asArray(c.suggested_targets);
  const urls: string[] = [];
  let tabCount = 0;
  let fileCount = 0;
  for (const t of targets) {
    const [kind, target] = normalizeTarget(t);
    if (kind === "url") {
      urls.push(target);
      tabCount += 1;
    } else if (kind === "path") {
      fileCount += 1;
    }
  }
  return {
    id: stringOf(c.id),
    title: stringOf(c.title) || "Interrupted work",
    caption,
    chips,
    tabCount,
    fileCount,
    urls,
  };
}

export async function fetchInvestigations(): Promise<Investigation[]> {
  const data = await getJSON<Record<string, unknown>>("/v1/threads/recent");
  const list = asArray(data?.threads ?? data);
  return list.slice(0, 4).map((raw) => {
    const t = raw as Record<string, unknown>;
    return {
      id: stringOf(t.id),
      title: stringOf(t.title) || "Untitled thread",
      summary: stringOf(t.timeline_summary),
      surfaces: asArray(t.surface_types).map(stringOf).filter(Boolean),
    };
  });
}

export async function fetchMemory(): Promise<MemoryItem[]> {
  const data = await getJSON<Record<string, unknown>>("/v1/events/recent");
  const list = asArray(data?.events ?? data);
  const out: MemoryItem[] = [];
  for (const raw of list) {
    const e = raw as Record<string, unknown>;
    const kind = stringOf(e.kind);
    const payload = (e.payload ?? {}) as Record<string, unknown>;
    if (kind === "browser_search") {
      out.push({
        kind: "search",
        label: stringOf(payload.query) || "Search",
        detail: stringOf(payload.engine) || stringOf(payload.domain),
        url: stringOf(payload.url) || undefined,
      });
    } else if (kind === "chat_session") {
      out.push({
        kind: "chat",
        label: stringOf(payload.title) || "Conversation",
        detail: stringOf(payload.platform) || stringOf(payload.domain),
        url: stringOf(payload.url) || undefined,
      });
    } else if (kind === "browser_visit") {
      out.push({
        kind: "tab",
        label: stringOf(payload.title) || stringOf(payload.domain) || "Page",
        detail: stringOf(payload.domain),
        url: stringOf(payload.url) || undefined,
      });
    }
  }
  return out;
}

// ── settings (chrome.storage) ───────────────────────────────────────

const SETTINGS_KEY = "recall.settings";

export async function loadSettings(): Promise<Settings> {
  if (!hasChromeStorage()) return { ...DEFAULT_SETTINGS };
  return new Promise((resolve) => {
    chrome.storage.local.get([SETTINGS_KEY], (r) => {
      resolve({ ...DEFAULT_SETTINGS, ...(r?.[SETTINGS_KEY] ?? {}) });
    });
  });
}

export async function saveSettings(s: Settings): Promise<void> {
  if (!hasChromeStorage()) return;
  return new Promise((resolve) => {
    chrome.storage.local.set({ [SETTINGS_KEY]: s }, () => resolve());
  });
}

// ── pairing memory ──────────────────────────────────────────────────
//
// The popup cannot truly tell "Recall was never installed" from
// "Recall is installed but not running" — a health probe fails the
// same way for both. So it remembers: once the daemon has answered
// even once, a later failure means *not running*, not *missing*.

const EVER_KEY = "recall.everConnected";

/** Record that the daemon has answered at least once on this profile. */
export function markConnected(): void {
  if (hasChromeStorage()) {
    chrome.storage.local.set({ [EVER_KEY]: true });
  }
}

/** Has the daemon ever answered? Drives missing-vs-disconnected copy. */
export async function wasEverConnected(): Promise<boolean> {
  if (!hasChromeStorage()) return true; // dev preview: assume installed
  return new Promise((resolve) => {
    chrome.storage.local.get([EVER_KEY], (r) => resolve(!!r?.[EVER_KEY]));
  });
}

/** Open a URL in a new tab — used by Resume and memory rows. */
export function openTab(url: string): void {
  if (typeof chrome !== "undefined" && chrome.tabs?.create) {
    chrome.tabs.create({ url, active: false });
  } else {
    window.open(url, "_blank", "noopener");
  }
}

/**
 * Outcome of an `openRecall()` attempt.
 *
 *   - `launched`     — `recall://` was dispatched (the OS may or may
 *                       not have a handler; we cannot tell from the
 *                       popup, so the caller pairs this with a
 *                       short-delay daemon re-probe).
 *   - `repair`       — neither the protocol nor the daemon is
 *                       usable; the caller should surface the
 *                       repair flow.
 *
 * No `failed` because the click never raises - the rule is "never
 * dead click", so every call returns an actionable outcome.
 */
export type OpenRecallOutcome = "launched" | "repair";

/**
 * Try to bring the desktop Recall to the user. Three-rung ladder:
 *
 *   1. Probe the daemon's `/v1/health`. If it answers, Recall is
 *      already running locally - we don't need to launch it, and
 *      `recall://` would only re-focus it. Return `launched` and
 *      let the caller show a "Recall is already running" hint
 *      rather than firing a no-op protocol click.
 *   2. If the daemon does not answer, dispatch `recall://open` via
 *      `chrome.tabs.create` (or `location.href` in the dev preview).
 *      The OS routes the URL to a registered handler if one exists.
 *      Return `launched` so the caller can re-probe after a short
 *      delay (the OS launch is asynchronous).
 *   3. If we cannot even dispatch (no `chrome.tabs`, no `window`),
 *      return `repair` so the caller surfaces a reinstall / open-
 *      manually message.
 *
 * Phase 5F adds the `recall://` handler to the installer; until a
 * user reinstalls with that installer, step 2 may silently drop on
 * their machine - which is why the contract is "caller pairs this
 * with a visible follow-up", not "this guarantees focus".
 */
export async function openRecall(): Promise<OpenRecallOutcome> {
  // Step 1: is Recall already running?
  const h = await fetchHealth();
  if (h) return "launched"; // already running; caller surfaces "already running"
  // Step 2: dispatch the protocol.
  try {
    if (typeof chrome !== "undefined" && chrome.tabs?.create) {
      chrome.tabs.create({ url: "recall://open", active: false });
      return "launched";
    }
    if (typeof window !== "undefined") {
      window.location.href = "recall://open";
      return "launched";
    }
  } catch {
    /* fall through */
  }
  return "repair";
}

export function isOnline(): boolean {
  return typeof navigator === "undefined" ? true : navigator.onLine;
}

// ── helpers ─────────────────────────────────────────────────────────

function hasChromeStorage(): boolean {
  return typeof chrome !== "undefined" && !!chrome.storage?.local;
}

function asArray(v: unknown): unknown[] {
  return Array.isArray(v) ? v : [];
}

function numberOf(v: unknown): number {
  return typeof v === "number" && Number.isFinite(v) ? v : 0;
}

function stringOf(v: unknown): string {
  return typeof v === "string" ? v : "";
}

/** A target arrives as `["url", "https://…"]` or `{kind, target}`. */
function normalizeTarget(t: unknown): [string, string] {
  if (Array.isArray(t) && t.length >= 2) {
    return [stringOf(t[0]), stringOf(t[1])];
  }
  if (t && typeof t === "object") {
    const o = t as Record<string, unknown>;
    return [stringOf(o.kind), stringOf(o.target)];
  }
  return ["", ""];
}
