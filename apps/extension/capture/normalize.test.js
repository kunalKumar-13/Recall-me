/**
 * Node test for the pure capture normalizer. Run:
 *   node apps/extension/capture/normalize.test.js
 *
 * classify() is pure (no chrome.*), which is the point of the split:
 * the riskiest capture logic is verifiable without a browser. This
 * replaces the old root-level scratch verifiers with a real test.
 */
import assert from "node:assert/strict";
import {
  classify,
  getDomain,
  platformFor,
  shouldSkipScheme,
} from "./normalize.js";

const NOW = "2026-06-25T12:00:00.000Z";
let n = 0;
const ok = (m) => {
  console.log(`  [ok] ${m}`);
  n += 1;
};

// Chat detection across the modern AI surface, with stable platform tags.
for (const [host, platform] of [
  ["chatgpt.com", "chatgpt"],
  ["chat.openai.com", "chatgpt"],
  ["claude.ai", "claude"],
  ["gemini.google.com", "gemini"],
  ["copilot.microsoft.com", "copilot"],
  ["chat.deepseek.com", "deepseek"],
  ["grok.com", "grok"],
  ["poe.com", "poe"],
  ["t3.chat", "t3"],
]) {
  const r = classify(`https://${host}/c/abc`, "A conversation", NOW);
  assert.equal(r.kind, "chat_session", `${host} should be chat_session`);
  assert.equal(r.payload.platform, platform, `${host} platform tag`);
}
ok("chat hosts → chat_session with the right platform tag");

// Search detection + query extraction (www. is stripped for the host).
const s = classify(
  "https://www.google.com/search?q=launchd+keepalive",
  "google",
  NOW,
);
assert.equal(s.kind, "browser_search");
assert.equal(s.payload.query, "launchd keepalive");
assert.equal(s.payload.engine, "google");
ok("search URL → browser_search with decoded query + engine");

// A search host with no query falls back to a plain visit.
const sv = classify("https://duckduckgo.com/about", "About", NOW);
assert.equal(sv.kind, "browser_visit");
ok("search host without ?q → browser_visit");

// Generic page → browser_visit with a derived domain and injected ts.
const v = classify(
  "https://docs.python.org/3/library/asyncio.html",
  "asyncio",
  NOW,
);
assert.equal(v.kind, "browser_visit");
assert.equal(v.payload.domain, "docs.python.org");
assert.equal(v.payload.ts, NOW);
ok("generic page → browser_visit with derived domain + injected ts");

// www. stripping + scheme blocklist.
assert.equal(getDomain("https://www.example.com/x"), "example.com");
assert.equal(shouldSkipScheme("chrome://settings"), true);
assert.equal(shouldSkipScheme("file:///etc/passwd"), true);
assert.equal(classify("chrome://settings", "settings", NOW), null);
assert.equal(classify("file:///etc/passwd", "passwd", NOW), null);
ok("www stripped; chrome:// and file:// skipped (classify → null)");

// platformFor fallback for an unknown chat-ish host.
assert.equal(platformFor("unknown-chat.example"), "chat");
ok("unknown chat host → generic 'chat' tag");

console.log(`\n[ALL ${n} NORMALIZER CHECKS PASSED]`);
