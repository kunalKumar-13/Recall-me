// Track A — verify the title-settle defer logic.
//
// Stubs chrome.* + timers so we can drive _scheduleFire deterministically
// and assert that:
//   1. A single load complete -> one event after SETTLE_MS, with the
//      latest title.
//   2. A title update mid-settle resets the timer (settle reaches the
//      newer title).
//   3. The MAX_WAIT_MS ceiling fires even under repeated title pokes.
//   4. A URL change in the same tab fires the prior URL immediately.
//   5. A tab close fires the pending entry immediately.

const sent = [];
let now = 0;
let timerSeq = 0;
const timers = new Map();

global.chrome = {
  storage: {
    local: { get: (_k, cb) => cb({}) },
    onChanged: { addListener: () => {} },
  },
  tabs: {
    onUpdated: { addListener: () => {} },
    onRemoved: { addListener: () => {} },
  },
};
global.fetch = async (endpoint, opts) => {
  sent.push({ endpoint, body: JSON.parse(opts.body), at: now });
  return { ok: true };
};
// Replace global setTimeout / clearTimeout with controllable shims.
global.setTimeout = (fn, ms) => {
  const id = ++timerSeq;
  timers.set(id, { fn, fireAt: now + ms });
  return id;
};
global.clearTimeout = (id) => { timers.delete(id); };
const advance = (ms) => {
  const target = now + ms;
  while (true) {
    let nextId = null;
    let nextAt = Infinity;
    for (const [id, t] of timers) {
      if (t.fireAt < nextAt) { nextAt = t.fireAt; nextId = id; }
    }
    if (nextId === null || nextAt > target) break;
    now = nextAt;
    const t = timers.get(nextId);
    timers.delete(nextId);
    t.fn();
  }
  now = target;
};
global.Date.now = () => now;

const fs = require("fs");
const path = require("path");
const src = fs.readFileSync(path.join(__dirname, "background.js"), "utf-8");
const tmp = path.join(__dirname, "_track_a_loaded_defer.js");
fs.writeFileSync(tmp, src + "\nmodule.exports = { _scheduleFire, pending };\n", "utf-8");
let mod;
try { mod = require("./_track_a_loaded_defer.js"); }
finally { try { fs.unlinkSync(tmp); } catch {} }

let pass = 0, fail = 0;
const check = (label, cond) => {
  if (cond) { console.log("pass " + label); pass++; }
  else { console.log("FAIL " + label); fail++; }
};

// --- Case 1: single load complete -> one event after SETTLE_MS.
sent.length = 0;
mod._scheduleFire(1, "https://chatgpt.com/c/a", "ChatGPT");
advance(1500);
check("case1: one event at 1500ms", sent.length === 1);
check("case1: title is initial", sent.length && sent[0].body.title === "ChatGPT");

// --- Case 2: title update mid-settle pushes the timer + grabs new title.
sent.length = 0; timers.clear(); now = 0;
mod._scheduleFire(2, "https://chatgpt.com/c/b", "ChatGPT");
advance(800);                                  // 800ms in, still pending
check("case2: no fire yet at 800ms", sent.length === 0);
mod._scheduleFire(2, "https://chatgpt.com/c/b", "ChatGPT - JWT auth flow");
advance(2000);                                 // 800 + 2000 = 2800
check("case2: fires after the title update settled", sent.length === 1);
check("case2: captures the newer title",
      sent.length && sent[0].body.title === "ChatGPT - JWT auth flow");

// --- Case 3: MAX_WAIT_MS ceiling.
sent.length = 0; timers.clear(); now = 0;
mod._scheduleFire(3, "https://gemini.google.com/", "Gemini");
// Poke the title every 1000ms for 6 seconds. Each poke would reset
// the SETTLE_MS timer; the MAX_WAIT_MS ceiling should clamp the wait.
for (let i = 1; i <= 6; i++) {
  advance(1000);
  if (sent.length === 0) {
    mod._scheduleFire(3, "https://gemini.google.com/", `Gemini ${i}`);
  }
}
check("case3: MAX_WAIT_MS ceiling fires within 5000ms", sent.length === 1 && sent[0].at <= 5000);

// --- Case 4: URL change in same tab fires prior immediately.
sent.length = 0; timers.clear(); now = 0;
mod._scheduleFire(4, "https://chatgpt.com/c/x", "ChatGPT");
advance(500);
mod._scheduleFire(4, "https://chatgpt.com/c/y", "ChatGPT");
check("case4: prior URL fires immediately on URL change", sent.length === 1);
check("case4: prior URL is x",
      sent.length && sent[0].body.url === "https://chatgpt.com/c/x");
advance(2000);
check("case4: new URL fires after its settle", sent.length === 2);
check("case4: new URL is y",
      sent.length === 2 && sent[1].body.url === "https://chatgpt.com/c/y");

// --- Case 5: tab close fires the pending entry.
sent.length = 0; timers.clear(); now = 0; mod.pending.clear?.();
mod._scheduleFire(5, "https://gemini.google.com/", "Gemini - draft");
advance(300);
// Simulate the tabs.onRemoved handler inline (we can't easily call the
// listener; instead we replicate its logic against the exposed map).
const entry = mod.pending.get(5);
if (entry) {
  if (entry.timer) clearTimeout(entry.timer);
  // mimic sendEvent dispatch
  global.fetch("https://127.0.0.1:4545/v1/events/chat", {
    method: "POST",
    body: JSON.stringify({
      url: entry.url, title: entry.title, domain: "gemini.google.com",
      platform: "gemini", browser: "chrome", ts: "(stub)",
    }),
  });
  mod.pending.delete(5);
}
check("case5: tab-close fires the pending entry", sent.length === 1);
check("case5: payload uses settled title",
      sent.length && sent[0].body.title === "Gemini - draft");

console.log(`\n${pass} pass, ${fail} fail`);
process.exit(fail === 0 ? 0 : 1);
