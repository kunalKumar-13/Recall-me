// Track A verification harness. Stubs the chrome.* surface so
// background.js can be node-loaded, then exercises classify() across
// the directive-named sites + the modern AI surface added in 8F-A.
//
// Run: node apps/extension/_track_a_verify.js
//
// This file is a scratch verifier, not a unit test — delete after the
// Track A commit if you want; the commit message references it.

const sent = [];
global.chrome = {
  storage: {
    local: { get: (_keys, cb) => cb({}) },
    onChanged: { addListener: () => {} },
  },
  tabs: {
    onUpdated: { addListener: () => {} },
    onRemoved: { addListener: () => {} },
  },
};
global.fetch = async (endpoint, opts) => {
  sent.push({ endpoint, body: JSON.parse(opts.body) });
  return { ok: true };
};

// Inject the file as a string and evaluate it in this scope so the
// internal `classify` / `_scheduleFire` symbols are reachable.
const fs = require("fs");
const path = require("path");
const src = fs.readFileSync(path.join(__dirname, "background.js"), "utf-8");
// Strip the const/let leading keywords on the symbols we want to read
// from the outer scope, by appending a tail that pushes them out.
const exposed =
  src +
  "\nmodule.exports = { classify, _scheduleFire, pending, sendEvent };\n";

// Write to a temp file and require it so node treats it as a module.
const tmp = path.join(__dirname, "_track_a_loaded.js");
fs.writeFileSync(tmp, exposed, "utf-8");
let mod;
try {
  mod = require("./_track_a_loaded.js");
} finally {
  // Always remove the temp file.
  try { fs.unlinkSync(tmp); } catch {}
}

// --------------------------------------------------------- classify()

const cases = [
  // [url, expected kind, expected platform-or-engine]
  ["https://chatgpt.com/c/abc123", "chat_session", "chatgpt"],
  ["https://chat.openai.com/c/x", "chat_session", "chatgpt"],
  ["https://claude.ai/chat/123", "chat_session", "claude"],
  ["https://gemini.google.com/app", "chat_session", "gemini"],
  ["https://aistudio.google.com/app/prompts/123", "chat_session", "gemini"],
  ["https://copilot.microsoft.com/?q=hi", "chat_session", "copilot"],
  ["https://chat.deepseek.com/", "chat_session", "deepseek"],
  ["https://chat.mistral.ai/chat", "chat_session", "mistral"],
  ["https://grok.com/?q=hi", "chat_session", "grok"],
  ["https://poe.com/abc", "chat_session", "poe"],
  ["https://t3.chat/c/x", "chat_session", "t3"],
  // Search engines still classify as searches.
  ["https://www.google.com/search?q=what+is+react", "browser_search", "google"],
  ["https://duckduckgo.com/?q=privacy", "browser_search", "duckduckgo"],
  // Generic browsing.
  ["https://github.com/recall/repo/pull/42", "browser_visit", null],
  ["https://stackoverflow.com/questions/123", "browser_visit", null],
  ["https://stitch.design/project/abc", "browser_visit", null],
];

let pass = 0;
let fail = 0;
for (const [url, wantKind, wantTag] of cases) {
  const out = mod.classify(url, "title");
  if (!out) { console.log(`FAIL ${url} -> null`); fail++; continue; }
  const actualKind = (out.endpoint || "").split("/").pop();
  const actualKindMap = {
    browser: "browser_visit",
    search: "browser_search",
    chat: "chat_session",
  };
  const got = actualKindMap[actualKind] || actualKind;
  const tag = out.payload.platform || out.payload.engine || null;
  const ok = got === wantKind && tag === wantTag;
  if (ok) {
    console.log(`pass ${url.padEnd(60)} ${got}  ${tag || ""}`);
    pass++;
  } else {
    console.log(`FAIL ${url.padEnd(60)} got=${got} tag=${tag}   want=${wantKind} ${wantTag}`);
    fail++;
  }
}
console.log(`\n${pass} pass, ${fail} fail`);
process.exit(fail === 0 ? 0 : 1);
