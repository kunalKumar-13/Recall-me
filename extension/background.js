/**
 * Recall.me — Memory Sync (background service worker)
 *
 * Listens for tab-completion events and posts a small JSON envelope
 * to the local Recall daemon at 127.0.0.1:49827. That's the entire
 * extension surface — there is no remote networking, no DOM scraping,
 * no telemetry, no analytics.
 *
 * Per-tab debounce keeps SPA reloads (which fire onUpdated many
 * times for a single navigation) from spamming the log. Incognito
 * tabs are filtered explicitly by the Chrome runtime; the extension
 * also drops chrome:// / file:// / about:// schemes locally.
 */

const ENDPOINT = "http://127.0.0.1:49827/events";

// Schemes we never send. The Recall daemon also blocks these
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

// Domains we treat as chat platforms. A visit on these surfaces
// becomes a `chat_session` event so the launcher's digest can
// distinguish them.
const CHAT_DOMAINS = new Set([
  "chatgpt.com",
  "chat.openai.com",
  "claude.ai",
]);

// Search engines we recognize. A visit whose URL has the configured
// query parameter populated becomes a `browser_search` event.
const SEARCH_PATTERNS = [
  { domain: "google.com", paramKey: "q", engine: "google" },
  { domain: "duckduckgo.com", paramKey: "q", engine: "duckduckgo" },
  { domain: "bing.com", paramKey: "q", engine: "bing" },
  { domain: "kagi.com", paramKey: "q", engine: "kagi" },
  { domain: "perplexity.ai", paramKey: "q", engine: "perplexity" },
  { domain: "you.com", paramKey: "q", engine: "you" },
];

// Local config — kept in chrome.storage.local so the popup can
// flip these and the worker picks up the change immediately via
// onChanged.
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

function classify(url, title) {
  const domain = getDomain(url);

  // Chat session?
  if (CHAT_DOMAINS.has(domain)) {
    let platform = "chat";
    if (domain.includes("openai") || domain.includes("chatgpt")) {
      platform = "chatgpt";
    } else if (domain.includes("claude")) {
      platform = "claude";
    }
    return {
      kind: "chat_session",
      payload: { url, title, domain, platform, source: "chrome" },
    };
  }

  // Search engine query?
  for (const pat of SEARCH_PATTERNS) {
    if (domain === pat.domain || domain.endsWith("." + pat.domain)) {
      try {
        const u = new URL(url);
        const q = u.searchParams.get(pat.paramKey);
        if (q && q.trim()) {
          return {
            kind: "browser_search",
            payload: {
              url,
              query: q.trim(),
              engine: pat.engine,
              domain,
              source: "chrome",
            },
          };
        }
      } catch {
        // fall through to plain visit
      }
    }
  }

  // Default: plain page visit.
  return {
    kind: "browser_visit",
    payload: { url, title, domain, source: "chrome" },
  };
}

async function sendEvent(event) {
  try {
    await fetch(ENDPOINT, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(event),
    });
  } catch (e) {
    // Recall daemon may not be running. Silent — the next visit
    // will retry on its own. We never queue/persist locally; the
    // log is local-machine-only, and missing a few visits is fine.
  }
}

// Per-tab debounce — SPA navigations fire onUpdated multiple times
// while the URL settles. We collapse near-duplicate hits within an
// 800 ms window.
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

  const event = classify(tab.url, tab.title || "");
  sendEvent(event);
});

chrome.tabs.onRemoved.addListener((tabId) => {
  recentByTab.delete(tabId);
});
