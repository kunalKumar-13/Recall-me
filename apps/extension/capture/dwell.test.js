/**
 * Node test for the pure dwell tracker. Run:
 *   node apps/extension/capture/dwell.test.js
 *
 * createDwellTracker() is pure (no chrome.*, time passed in), same
 * split as normalize.js: the attention state machine is verifiable
 * without a browser.
 */
import assert from "node:assert/strict";
import {
  createDwellTracker,
  MIN_DWELL_MS,
  MAX_DWELL_MS,
  BLOCK_GAP_MS,
} from "./dwell.js";

let n = 0;
const ok = (m) => {
  console.log(`  [ok] ${m}`);
  n += 1;
};

const T0 = 1_751_882_400_000; // fixed epoch, deterministic block ids
const page = (u, t = "") => ({ url: u, title: t });

// A dwell shorter than the minimum emits nothing — passing through
// a tab is not working in it.
{
  const tr = createDwellTracker();
  assert.equal(tr.focus(page("https://a.com/x"), T0), null);
  const out = tr.focus(page("https://b.com/y"), T0 + MIN_DWELL_MS - 1);
  assert.equal(out, null);
}
ok("sub-minimum dwell → no event");

// A real dwell emits on the switch away, with duration and block id.
{
  const tr = createDwellTracker();
  tr.focus(page("https://a.com/x", "Docs"), T0);
  const out = tr.focus(page("https://b.com/y"), T0 + 12_000);
  assert.equal(out.url, "https://a.com/x");
  assert.equal(out.title, "Docs");
  assert.equal(out.dwell_ms, 12_000);
  assert.equal(out.block, `wb-${Math.floor(T0 / 1000)}`);
  assert.equal(out.ts, new Date(T0 + 12_000).toISOString());
}
ok("tab switch after 12s → browser_focus record with block id");

// Blur (window focus lost) also finishes the interval.
{
  const tr = createDwellTracker();
  tr.focus(page("https://a.com/x"), T0);
  const out = tr.blur(T0 + 20_000);
  assert.equal(out.dwell_ms, 20_000);
  assert.equal(tr.blur(T0 + 30_000), null); // nothing left to finish
}
ok("window blur finishes the dwell; second blur is a no-op");

// Attention within the gap stays in one block; a gap starts a new one.
{
  const tr = createDwellTracker();
  tr.focus(page("https://a.com/1"), T0);
  const first = tr.focus(page("https://a.com/2"), T0 + 10_000);
  assert.equal(first.block, `wb-${Math.floor(T0 / 1000)}`);
  tr.blur(T0 + 25_000);

  const resume = T0 + 25_000 + BLOCK_GAP_MS + 1;
  tr.focus(page("https://a.com/3"), resume);
  const second = tr.focus(page("https://a.com/4"), resume + 10_000);
  assert.equal(second.block, `wb-${Math.floor(resume / 1000)}`);
  assert.notEqual(second.block, first.block);
}
ok("5-minute silence starts a new work block");

// An overnight "dwell" is capped — a focused tab is not 9 hours of work.
{
  const tr = createDwellTracker();
  tr.focus(page("https://a.com/x"), T0);
  const out = tr.blur(T0 + 9 * 3600_000);
  assert.equal(out.dwell_ms, MAX_DWELL_MS);
}
ok("dwell capped at the 30-minute ceiling");

// Titles settle late; retitle keeps the record truthful.
{
  const tr = createDwellTracker();
  tr.focus(page("https://a.com/x", ""), T0);
  tr.retitle("https://a.com/x", "Settled title");
  tr.retitle("https://other.com/", "Wrong page"); // ignored
  const out = tr.blur(T0 + 15_000);
  assert.equal(out.title, "Settled title");
}
ok("late title settle updates the in-flight dwell only for its page");

// Untrackable focus (null page) ends tracking without starting more.
{
  const tr = createDwellTracker();
  tr.focus(page("https://a.com/x"), T0);
  const out = tr.focus(null, T0 + 10_000);
  assert.equal(out.url, "https://a.com/x");
  assert.equal(tr.blur(T0 + 60_000), null);
}
ok("focus on an untrackable surface finishes the dwell, tracks nothing");

console.log(`\n${n} dwell checks passed`);
