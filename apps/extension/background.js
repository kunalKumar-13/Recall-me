/**
 * Recall.me — Memory Sync (background service worker)
 *
 * Listens for tab-completion events and posts a small JSON envelope
 * to the local Recall daemon at 127.0.0.1:4545. Phase 2A pointed the
 * extension at the versioned `/v1/events/*` endpoints instead of the
 * legacy generic `/events` route — same daemon, same JSON, typed
 * routes.
 *
 * The legacy `/events` route still exists on the server side, so old
 * extension installs continue to work without an update.
 *
 * No remote networking, no DOM scraping, no telemetry. The
 * extension's manifest only permits `http://127.0.0.1:4545/*` — the
 * browser physically refuses any other URL.
 */

const BASE = "http://127.0.0.1:4545";
const ENDPOINTS = {
  browser_visit: `${BASE}/v1/events/browser`,
  browser_search: `${BASE}/v1/events/search`,
  chat_session: `${BASE}/v1/events/chat`,
};

// URL schemes we never send. The daemon also blocks these
// server-side; doing it here too saves an HTTP roundtrip.
const SCHEME_BLOCKLIST = [
  "chrome:",
  "chrome-extension:",
  "chrome-search:",
  "chrome-devtools:",
  "edge:",
  "extension:",
  "about:",
  "file:",
  "data:",
  "blob:",
  "view-source:",
  "javascript:",
];

// Domains we treat as chat platforms. Phase 8F-A: extended to the
// modern AI surface — Gemini / Copilot / DeepSeek / Mistral / Grok /
// Poe / t3.chat. Before this extension, conversations on any of these
// hosts were captured as generic browser_visit events, which made the
// chat_session count under-report what the user was actually doing.
const CHAT_DOMAINS = new Set([
  "chatgpt.com",
  "chat.openai.com",
  "claude.ai",
  "gemini.google.com",
  "aistudio.google.com",
  "copilot.microsoft.com",
  "chat.deepseek.com",
  "chat.mistral.ai",
  "grok.com",
  "poe.com",
  "t3.chat",
]);

// Search engines we recognise.
const SEARCH_PATTERNS = [
  { domain: "google.com", paramKey: "q", engine: "google" },
  { domain: "duckduckgo.com", paramKey: "q", engine: "duckduckgo" },
  { domain: "bing.com", paramKey: "q", engine: "bing" },
  { domain: "kagi.com", paramKey: "q", engine: "kagi" },
  { domain: "perplexity.ai", paramKey: "q", engine: "perplexity" },
  { domain: "you.com", paramKey: "q", engine: "you" },
];

let enabled = true;
let excludedDomains = new Set();

chrome.storage.local.get(["enabled", "excludedDomains"], (result) => {
  if (typeof result.enabled === "boolean") enabled = result.enabled;
  if (Array.isArray(result.excludedDomains)) {
    excludedDomains = new Set(result.excludedDomains);
  }
});

chrome.storage.onChanged.addListener((changes) => {
  if ("enabled" in changes) enabled = changes.enabled.newValue !== false;
  if ("excludedDomains" in changes) {
    excludedDomains = new Set(changes.excludedDomains.newValue || []);
  }
});

function shouldSkipScheme(url) {
  if (!url) return true;
  for (const scheme of SCHEME_BLOCKLIST) {
    if (url.startsWith(scheme)) return true;
  }
  return false;
}

function getDomain(url) {
  try {
    return new URL(url).hostname.toLowerCase().replace(/^www\./, "");
  } catch {
    return "";
  }
}

function isExcluded(domain) {
  if (!domain) return false;
  for (const ex of excludedDomains) {
    if (domain === ex || domain.endsWith("." + ex)) return true;
  }
  return false;
}

/**
 * Decide which `/v1/events/*` endpoint to hit for this URL, and
 * build the typed payload that endpoint expects. Returns
 * `{ endpoint, payload }` or `null` to skip.
 */
function classify(url, title) {
  const domain = getDomain(url);
  const ts = new Date().toISOString();

  if (CHAT_DOMAINS.has(domain)) {
    // Map the matching domain to a stable platform tag. Keep the
    // existing "chatgpt" / "claude" tags so old data lines up; new
    // platforms each get their own tag rather than collapsing into
    // a generic "chat".
    let platform = "chat";
    if (domain.includes("openai") || domain.includes("chatgpt")) {
      platform = "chatgpt";
    } else if (domain.includes("claude")) {
      platform = "claude";
    } else if (domain.includes("gemini") || domain.includes("aistudio")) {
      platform = "gemini";
    } else if (domain.includes("copilot")) {
      platform = "copilot";
    } else if (domain.includes("deepseek")) {
      platform = "deepseek";
    } else if (domain.includes("mistral")) {
      platform = "mistral";
    } else if (domain.includes("grok")) {
      platform = "grok";
    } else if (domain === "poe.com") {
      platform = "poe";
    } else if (domain === "t3.chat") {
      platform = "t3";
    }
    return {
      endpoint: ENDPOINTS.chat_session,
      payload: { url, title, domain, platform, browser: "chrome", ts },
    };
  }

  for (const pat of SEARCH_PATTERNS) {
    if (domain === pat.domain || domain.endsWith("." + pat.domain)) {
      try {
        const u = new URL(url);
        const q = u.searchParams.get(pat.paramKey);
        if (q && q.trim()) {
          return {
            endpoint: ENDPOINTS.browser_search,
            payload: {
              url,
              query: q.trim(),
              engine: pat.engine,
              domain,
              browser: "chrome",
              ts,
            },
          };
        }
      } catch {
        // fall through to plain visit
      }
    }
  }

  return {
    endpoint: ENDPOINTS.browser_visit,
    payload: { url, title, domain, browser: "chrome", ts },
  };
}

async function sendEvent(endpoint, payload) {
  try {
    await fetch(endpoint, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
  } catch (e) {
    // Daemon down / port collision / first-launch race. Silent —
    // the next visit retries on its own; we never queue locally.
  }
}

// Phase 8F-A — title-settle defer.
//
// `chrome.tabs.onUpdated` fires when a tab loads (status=complete) AND
// when SPAs later update their title (changeInfo.title). On
// ChatGPT / Gemini / GitHub-PR / Notion etc., the title at load time
// is usually a generic placeholder ("ChatGPT", "GitHub") that gets
// rewritten to something specific ("ChatGPT — explain JWT auth flow")
// within a second of the page settling. Sending the event at
// load-complete time means we capture the generic title, not the
// truthful one.
//
// Fix: when a tab completes loading or has its title updated, schedule
// a single deferred send `SETTLE_MS` after the most recent change.
// Cap the wait at `MAX_WAIT_MS` so a tab that keeps poking its title
// still emits something. If the URL changes for the same tab before
// the timer fires, emit the prior URL immediately (with whatever
// title we last saw) and start a fresh timer for the new URL.
const pending = new Map();
const SETTLE_MS = 1500;
const MAX_WAIT_MS = 4000;

function _scheduleFire(tabId, url, title) {
  const now = Date.now();
  const prior = pending.get(tabId);

  if (prior && prior.url !== url) {
    // URL changed for this tab — fire the old URL now with its last
    // known title, then start a fresh timer for the new URL.
    if (prior.timer) clearTimeout(prior.timer);
    const cls = classify(prior.url, prior.title || "");
    if (cls) sendEvent(cls.endpoint, cls.payload);
    pending.delete(tabId);
  }

  const existing = pending.get(tabId);
  const startedAt = existing ? existing.startedAt : now;
  const remaining = Math.max(0, MAX_WAIT_MS - (now - startedAt));
  const delay = Math.min(SETTLE_MS, remaining);

  if (existing && existing.timer) clearTimeout(existing.timer);

  const timer = setTimeout(() => {
    const entry = pending.get(tabId);
    if (!entry || entry.url !== url) return;
    pending.delete(tabId);
    const cls = classify(entry.url, entry.title || "");
    if (cls) sendEvent(cls.endpoint, cls.payload);
  }, delay);

  pending.set(tabId, {
    url,
    title: title || (existing && existing.url === url ? existing.title : ""),
    startedAt,
    timer,
  });
}

chrome.tabs.onUpdated.addListener((tabId, changeInfo, tab) => {
  if (!enabled) return;
  if (!tab || !tab.url) return;
  if (tab.incognito) return;
  if (shouldSkipScheme(tab.url)) return;

  const domain = getDomain(tab.url);
  if (isExcluded(domain)) return;

  // We schedule on either (a) load completion, or (b) a title update.
  // Both are signals that something meaningful happened on this tab.
  // Anything else (favicon, audible, mutedInfo, pinned…) is ignored.
  const isLoadComplete = changeInfo.status === "complete";
  const isTitleUpdate = typeof changeInfo.title === "string";
  if (!isLoadComplete && !isTitleUpdate) return;

  _scheduleFire(tabId, tab.url, tab.title || "");
});

chrome.tabs.onRemoved.addListener((tabId) => {
  // If a tab is closed before its timer fires, emit one final event
  // so we don't silently lose work the user was looking at.
  const entry = pending.get(tabId);
  if (entry) {
    if (entry.timer) clearTimeout(entry.timer);
    const cls = classify(entry.url, entry.title || "");
    if (cls) sendEvent(cls.endpoint, cls.payload);
    pending.delete(tabId);
  }
});
