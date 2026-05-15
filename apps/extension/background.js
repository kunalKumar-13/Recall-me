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

// Domains we treat as chat platforms.
const CHAT_DOMAINS = new Set([
  "chatgpt.com",
  "chat.openai.com",
  "claude.ai",
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
    let platform = "chat";
    if (domain.includes("openai") || domain.includes("chatgpt")) {
      platform = "chatgpt";
    } else if (domain.includes("claude")) {
      platform = "claude";
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

// Per-tab debounce — SPA navigations fire onUpdated multiple times
// while the URL settles. Collapse near-duplicate hits within 800 ms.
const recentByTab = new Map();
const DEBOUNCE_MS = 800;

chrome.tabs.onUpdated.addListener((tabId, changeInfo, tab) => {
  if (!enabled) return;
  if (changeInfo.status !== "complete") return;
  if (!tab || !tab.url) return;
  if (tab.incognito) return;
  if (shouldSkipScheme(tab.url)) return;

  const domain = getDomain(tab.url);
  if (isExcluded(domain)) return;

  const last = recentByTab.get(tabId);
  if (last && last.url === tab.url && Date.now() - last.ts < DEBOUNCE_MS) {
    return;
  }
  recentByTab.set(tabId, { url: tab.url, ts: Date.now() });

  const cls = classify(tab.url, tab.title || "");
  if (cls) sendEvent(cls.endpoint, cls.payload);
});

chrome.tabs.onRemoved.addListener((tabId) => {
  recentByTab.delete(tabId);
});
