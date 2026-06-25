/**
 * Pure capture normalizer — no `chrome.*`, no I/O — so it runs in
 * node and is unit-tested (`normalize.test.js`). Given a URL and a
 * title it decides the event kind and builds the typed payload the
 * engine's ingest routes expect, or returns null to skip.
 *
 * Behaviour matches the pre-refactor `background.js` classify(); the
 * value of the split is that the decision logic is now pure and
 * testable, separate from the stateful tab listeners (sources.js) and
 * the durable sender (outbox.js).
 */

// Hosts we treat as chat platforms — the modern AI surface.
export const CHAT_DOMAINS = new Set([
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

// Search engines we recognise (domain + the query param to read).
export const SEARCH_PATTERNS = [
  { domain: "google.com", paramKey: "q", engine: "google" },
  { domain: "duckduckgo.com", paramKey: "q", engine: "duckduckgo" },
  { domain: "bing.com", paramKey: "q", engine: "bing" },
  { domain: "kagi.com", paramKey: "q", engine: "kagi" },
  { domain: "perplexity.ai", paramKey: "q", engine: "perplexity" },
  { domain: "you.com", paramKey: "q", engine: "you" },
];

// Schemes we never send. The daemon blocks these server-side too;
// dropping here keeps them out of the outbox entirely.
export const SCHEME_BLOCKLIST = [
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

export function getDomain(url) {
  try {
    return new URL(url).hostname.toLowerCase().replace(/^www\./, "");
  } catch {
    return "";
  }
}

export function shouldSkipScheme(url) {
  if (!url) return true;
  for (const scheme of SCHEME_BLOCKLIST) {
    if (url.startsWith(scheme)) return true;
  }
  return false;
}

export function isExcluded(domain, excluded) {
  if (!domain) return false;
  for (const ex of excluded) {
    if (domain === ex || domain.endsWith("." + ex)) return true;
  }
  return false;
}

// Map a chat host to a stable platform tag. Keeps the existing
// "chatgpt" / "claude" tags so historical data lines up; new
// platforms get their own tag rather than collapsing into "chat".
export function platformFor(domain) {
  if (domain.includes("openai") || domain.includes("chatgpt")) return "chatgpt";
  if (domain.includes("claude")) return "claude";
  if (domain.includes("gemini") || domain.includes("aistudio")) return "gemini";
  if (domain.includes("copilot")) return "copilot";
  if (domain.includes("deepseek")) return "deepseek";
  if (domain.includes("mistral")) return "mistral";
  if (domain.includes("grok")) return "grok";
  if (domain === "poe.com") return "poe";
  if (domain === "t3.chat") return "t3";
  return "chat";
}

/**
 * Decide the event kind + payload for one (url, title). Returns
 * `{ kind, payload }` for the `/v1/events/batch` envelope, or null to
 * skip. `nowIso` is injectable so the timestamp is deterministic in
 * tests; in production it defaults to *capture* time — which is the
 * real event time even when the outbox flushes it minutes later.
 */
export function classify(url, title, nowIso) {
  if (shouldSkipScheme(url)) return null;
  const domain = getDomain(url);
  const ts = nowIso || new Date().toISOString();

  if (CHAT_DOMAINS.has(domain)) {
    return {
      kind: "chat_session",
      payload: {
        url,
        title: title || "",
        domain,
        platform: platformFor(domain),
        browser: "chrome",
        ts,
      },
    };
  }

  for (const pat of SEARCH_PATTERNS) {
    if (domain === pat.domain || domain.endsWith("." + pat.domain)) {
      try {
        const q = new URL(url).searchParams.get(pat.paramKey);
        if (q && q.trim()) {
          return {
            kind: "browser_search",
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
        // fall through to a plain visit
      }
    }
  }

  return {
    kind: "browser_visit",
    payload: { url, title: title || "", domain, browser: "chrome", ts },
  };
}
