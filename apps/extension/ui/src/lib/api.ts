import {
  DEFAULT_SETTINGS,
  type DemoPayload,
  type DemoState,
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

/**
 * Durable-outbox depth. The capture worker queues events in
 * chrome.storage.local and drains them to /v1/events/batch; when the
 * daemon is down the queue holds everything. Surfacing the count is
 * the honest version of "nothing is lost". Returns 0 outside an
 * extension context (npm run dev in a plain tab).
 */
export async function getQueuedCount(): Promise<number> {
  try {
    const c = (globalThis as { chrome?: any }).chrome;
    if (!c?.storage?.local) return 0;
    const got = await c.storage.local.get("outbox");
    const q = got?.outbox;
    return Array.isArray(q) ? q.length : 0;
  } catch {
    return 0;
  }
}

/**
 * The capture self-check: how many events the engine actually
 * received today (UTC). Read from the daemon's day file, so it is
 * ground truth, not a client-side guess — null when the daemon is
 * unreachable (the strip then says nothing rather than guessing).
 */
export async function getTodayCount(): Promise<number | null> {
  const data = await getJSON<{ count?: number }>("/v1/events/today");
  return typeof data?.count === "number" ? data.count : null;
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
    /* Phase 6M — desktop_apps_today is optional on the wire. The
       daemon adds the field after the desktop watcher emits its
       first event; older daemons (pre-6M) omit it. */
    desktopApps: numberOf(data.desktop_apps_today),
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
    // Phase 6A — read the event timestamp so the popup can paint a
    // small "ago" label on each memory row. The API returns `ts`
    // as an epoch float; absent => skipped (rendered as no label).
    const ts = typeof e.ts === "number" && Number.isFinite(e.ts)
      ? (e.ts as number)
      : undefined;
    if (kind === "browser_search") {
      out.push({
        kind: "search",
        label: stringOf(payload.query) || "Search",
        detail: stringOf(payload.engine) || stringOf(payload.domain),
        url: stringOf(payload.url) || undefined,
        ts,
      });
    } else if (kind === "chat_session") {
      out.push({
        kind: "chat",
        label: stringOf(payload.title) || "Conversation",
        detail: stringOf(payload.platform) || stringOf(payload.domain),
        url: stringOf(payload.url) || undefined,
        ts,
      });
    } else if (kind === "browser_visit") {
      out.push({
        kind: "tab",
        label: stringOf(payload.title) || stringOf(payload.domain) || "Page",
        detail: stringOf(payload.domain),
        url: stringOf(payload.url) || undefined,
        ts,
      });
    }
  }
  return out;
}

// ── capture pause ────────────────────────────────────────────────────
//
// The worker honours a `pauseUntil` epoch in chrome.storage.local —
// privacy at your fingertips without touching Settings.

export async function getPauseUntil(): Promise<number> {
  if (!hasChromeStorage()) return 0;
  return new Promise((resolve) => {
    chrome.storage.local.get(["pauseUntil"], (r) => {
      const v = r?.pauseUntil;
      resolve(typeof v === "number" ? v : 0);
    });
  });
}

export async function setPauseUntil(ts: number): Promise<void> {
  if (!hasChromeStorage()) return;
  return new Promise((resolve) => {
    chrome.storage.local.set({ pauseUntil: ts }, () => resolve());
  });
}

/**
 * Episodic search against the daemon — the overlay's remote corpus.
 * Fast timeout: a slow search is worse than a local-only one.
 */
export async function searchDaemon(
  q: string,
): Promise<Array<{ label: string; detail: string; url?: string }>> {
  const data = await getJSON<Record<string, unknown>>(
    `/v1/search?q=${encodeURIComponent(q)}`,
    1500,
  );
  const list = asArray(data?.episodic);
  return list.slice(0, 8).map((raw) => {
    const e = raw as Record<string, unknown>;
    return {
      label: stringOf(e.title) || stringOf(e.subtitle) || "Moment",
      detail: stringOf(e.subtitle) || stringOf(e.kind),
      url: stringOf(e.url) || undefined,
    };
  });
}

/**
 * Semantic file search via the daemon's vector index. Returns []
 * when the index isn't wired (enabled=false) — the overlay simply
 * skips the group.
 */
export async function searchFilesDaemon(
  q: string,
): Promise<Array<{ label: string; detail: string }>> {
  const data = await getJSON<Record<string, unknown>>(
    `/v1/search/files?q=${encodeURIComponent(q)}&n=4`,
    1800,
  );
  if (!data || data.enabled === false) return [];
  return asArray(data.results).map((raw) => {
    const h = raw as Record<string, unknown>;
    return {
      label: stringOf(h.name) || "File",
      detail: stringOf(h.path).replace(/^\/Users\/[^/]+/, "~"),
    };
  });
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
 * Plan-driven resume. Asks the engine for the candidate's
 * restoration plan (files → chats → tabs → searches) and opens the
 * URL steps *in that order*, gently staggered so the tab strip
 * reads like the work coming back rather than an explosion.
 * `path` steps (files) can't be opened from a browser — the daemon
 * side handles those; we just report how many were left to it.
 * Returns null when the endpoint is unreachable so the caller can
 * fall back to the raw suggested URLs.
 */
export async function restoreRecovery(
  id: string,
): Promise<{ opened: number; files: number } | null> {
  try {
    const r = await fetch(
      `${BASE}/v1/recovery/${encodeURIComponent(id)}/restore`,
      { method: "POST" },
    );
    if (!r.ok) return null;
    const plan = (await r.json()) as {
      steps?: Array<{ kind?: string; target?: string }>;
    };
    const steps = Array.isArray(plan.steps) ? plan.steps : [];
    let opened = 0;
    let files = 0;
    for (const s of steps) {
      if (s?.kind === "url" && s.target) {
        const url = s.target;
        setTimeout(() => openTab(url), opened * 140);
        opened += 1;
      } else if (s?.kind === "path") {
        files += 1;
      }
    }
    return { opened, files };
  } catch {
    return null;
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

// ── Phase 6D — demo overlay ────────────────────────────────────────────

/**
 * Read the current demo-overlay state. Returns `null` only when the
 * daemon is unreachable; otherwise the response always carries a
 * named state (defaults to `available` on a fresh install). The
 * `payload` field is present iff `state === "active"`.
 */
export async function fetchDemoState(): Promise<DemoState | null> {
  const data = await getJSON<Record<string, unknown>>("/v1/demo/state");
  if (!data) return null;
  return _parseDemoState(data);
}

/**
 * The user clicked *Show example*. POST the activation and return
 * the new state + payload so the popup can render the overlay
 * immediately without an extra round-trip.
 */
export async function activateDemo(): Promise<DemoState | null> {
  return _postDemo("/v1/demo/activate");
}

/**
 * The user clicked *Dismiss* on the demo banner — OR *Start
 * normally* on the empty state. Either way, the overlay turns
 * off.
 */
export async function dismissDemo(): Promise<DemoState | null> {
  return _postDemo("/v1/demo/dismiss");
}

async function _postDemo(path: string): Promise<DemoState | null> {
  try {
    const r = await fetch(`${BASE}${path}`, {
      method: "POST",
      cache: "no-store",
    });
    if (!r.ok) return null;
    return _parseDemoState(await r.json());
  } catch {
    return null;
  }
}

function _parseDemoState(raw: Record<string, unknown>): DemoState {
  const state = (raw.state as DemoState["state"]) ?? "available";
  const payload = raw.payload as Record<string, unknown> | null;
  if (!payload) return { state, payload: null };
  return { state, payload: _parseDemoPayload(payload) };
}

function _parseDemoPayload(raw: Record<string, unknown>): DemoPayload {
  const rec = raw.recovery as Record<string, unknown>;
  const recovery: Recovery = {
    id: stringOf(rec.id),
    title: stringOf(rec.title),
    caption: stringOf(rec.preview_caption),
    chips: asArray(rec.chips).map((c) => stringOf(c)),
    tabCount: numberOf(rec.tab_count),
    fileCount: numberOf(rec.file_count),
    urls: asArray(rec.urls).map((u) => stringOf(u)),
  };
  const investigations = asArray(raw.investigations).map(
    (i): Investigation => {
      const r = i as Record<string, unknown>;
      return {
        id: stringOf(r.id),
        title: stringOf(r.title),
        summary: stringOf(r.timeline_summary),
        surfaces: asArray(r.surface_types).map((s) => stringOf(s)),
      };
    },
  );
  const timeline = asArray(raw.timeline).map((t): MemoryItem => {
    const r = t as Record<string, unknown>;
    const kindRaw = stringOf(r.kind);
    const kind: MemoryItem["kind"] =
      kindRaw === "browser_search"
        ? "search"
        : kindRaw === "chat_session"
          ? "chat"
          : "tab";
    return {
      kind,
      label: stringOf(r.label),
      detail: stringOf(r.detail),
      ts: numberOf(r.ts),
    };
  });
  const trust = raw.trust as Record<string, unknown>;
  return {
    recovery,
    investigations,
    timeline,
    trust: {
      bannerTitle: stringOf(trust?.banner_title) || "Example data",
      bannerBody:
        stringOf(trust?.banner_body) ||
        "Nothing here came from your device.",
    },
  };
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
