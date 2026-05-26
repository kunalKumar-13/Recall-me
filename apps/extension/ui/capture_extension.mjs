/**
 * capture_extension.mjs — Phase 5A.1 extension screenshots.
 *
 * Renders the built popup (`../popup/index.html`) in headless
 * Chromium and screenshots every pairing state to
 * `assets/screenshots/extension-*.png`.
 *
 *   cd apps/extension/ui && node capture_extension.mjs
 *
 * The `?state=` query param drives the storybook-style states. The
 * populated "connected" surface is produced by intercepting the
 * popup's loopback fetches and fulfilling them with fixed demo
 * JSON — no daemon required, fully deterministic.
 */
import { chromium } from "playwright";
import { spawn } from "node:child_process";
import { mkdirSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { dirname, resolve } from "node:path";

const HERE = dirname(fileURLToPath(import.meta.url));
const POPUP_DIR = resolve(HERE, "../popup");
const OUT = resolve(HERE, "../../../assets/screenshots");

// Phase 6C: a sibling output for the v2 "premium" captures. Mirrors
// the launcher's `launcher-v2/` directory so 6B + 6C visual updates
// can be reviewed side-by-side with the historical screenshots
// without overwriting them.
const OUT_V2 = resolve(OUT, "extension-v2");

// Phase 6D — the demo overlay captures land here.
const OUT_DEMO = resolve(OUT, "demo");

// Phase 7A — premium extension surface captures land here.
const OUT_7A = resolve(OUT, "extension-7a");

// The popup is an ES-module bundle; Chromium refuses module scripts
// over file://, so the built popup is served over HTTP for capture.
const PORT = 8137;
const POPUP = `http://localhost:${PORT}/index.html`;

// Fixed demo payloads for the connected surface.
const MOCK = {
  "/v1/health": { ingested_total: 128, events_today: 128 },
  "/v1/recovery/recent": {
    candidates: [
      {
        id: "rc_demo",
        title: "WebSocket retry debugging",
        preview_caption:
          "2 tabs · 2 files · reopened after a 2-day gap",
        suggested_targets: [
          ["url", "https://stackoverflow.com/q/57294879"],
          ["url", "https://developer.mozilla.org/WebSocket"],
          ["path", "~/code/ws-retry/client.py"],
          ["path", "~/code/ws-retry/backoff.py"],
        ],
      },
    ],
  },
  "/v1/threads/recent": {
    threads: [
      {
        id: "t1",
        title: "RLHF reward shaping",
        timeline_summary: "Started 1w ago · 4 sessions",
        surface_types: ["browser_visit", "browser_search"],
      },
      {
        id: "t2",
        title: "Healthcare startup research",
        timeline_summary: "Started 2w ago · 6 sessions",
        surface_types: ["browser_visit", "open", "chat_session"],
      },
    ],
  },
  "/v1/events/recent": {
    // Phase 6A: `ts` (epoch seconds) is added so the deterministic
    // captures render the new timeline labels on each row. These
    // are fixture values, not real timestamps; the *renderer* logic
    // is what the screenshot validates.
    events: [
      { kind: "browser_search", ts: Date.now() / 1000 - 8 * 60,
        payload: { query: "websocket backoff jitter", engine: "google" } },
      { kind: "browser_visit", ts: Date.now() / 1000 - 22 * 60,
        payload: { title: "WebSocket — MDN", domain: "developer.mozilla.org" } },
      { kind: "chat_session", ts: Date.now() / 1000 - 2 * 3600,
        payload: { title: "Backoff with jitter — review", platform: "claude" } },
    ],
  },
};

async function shot(browser, name, query, { mock = false, dir = OUT, mockData = null, height = 600 } = {}) {
  const page = await browser.newPage({
    viewport: { width: 440, height },
    deviceScaleFactor: 2,
  });
  if (mock || mockData) {
    const source = mockData ?? MOCK;
    await page.route("**/v1/**", (route) => {
      const url = new URL(route.request().url());
      const body = source[url.pathname];
      if (body) {
        route.fulfill({
          status: 200,
          contentType: "application/json",
          body: JSON.stringify(body),
        });
      } else {
        route.fulfill({ status: 404, body: "{}" });
      }
    });
  }
  await page.goto(POPUP + query, { waitUntil: "load" });
  // Let the connection state machine settle + framer-motion finish.
  await page.waitForTimeout(1100);
  // Screenshot the viewport — the popup IS the 440px-wide viewport.
  await page.screenshot({ path: `${dir}/${name}.png` });
  await page.close();
  const subdir =
    dir === OUT_V2
      ? "extension-v2/"
      : dir === OUT_DEMO
        ? "demo/"
        : dir === OUT_7A
          ? "extension-7a/"
          : "";
  console.log(`  wrote assets/screenshots/${subdir}${name}.png`);
}

// Phase 6C — make sure the v2 output directory exists before
// Playwright's screenshot calls try to write into it.
mkdirSync(OUT_V2, { recursive: true });
mkdirSync(OUT_DEMO, { recursive: true });
mkdirSync(OUT_7A, { recursive: true });

// Serve the built popup over HTTP for the duration of the capture.
const server = spawn(
  "python",
  ["-m", "http.server", String(PORT), "--directory", POPUP_DIR],
  { stdio: "ignore" },
);
await new Promise((r) => setTimeout(r, 1200)); // let the server bind

// Empty payloads — health ok but nothing captured yet. Forces the
// popup into the Phase 5H EMPTY state ("Recall is watching locally",
// no demo card, no dead-click CTAs).
const MOCK_EMPTY = {
  "/v1/health": { ingested_total: 0, events_today: 0 },
  "/v1/recovery/recent": { candidates: [] },
  "/v1/threads/recent": { threads: [] },
  "/v1/events/recent": { events: [] },
};

// Mid-flow payloads — daemon ingesting, browser events captured, no
// investigations or recovery yet. Drives the Phase 5H CAPTURING
// state (live "Recent activity" feed + the muted debug strip).
const MOCK_CAPTURING = {
  "/v1/health": { ingested_total: 23, events_today: 23 },
  "/v1/recovery/recent": { candidates: [] },
  "/v1/threads/recent": { threads: [] },
  "/v1/events/recent": {
    // Phase 6A: ts values so the capturing-state screenshot
    // renders the new timeline labels on each row.
    events: [
      { kind: "browser_search", ts: Date.now() / 1000 - 3 * 60,
        payload: { query: "websocket backoff jitter", engine: "google" } },
      { kind: "browser_visit", ts: Date.now() / 1000 - 9 * 60,
        payload: { title: "WebSocket — MDN", domain: "developer.mozilla.org" } },
      { kind: "chat_session", ts: Date.now() / 1000 - 18 * 60,
        payload: { title: "Backoff with jitter — review", platform: "claude" } },
      { kind: "browser_visit", ts: Date.now() / 1000 - 32 * 60,
        payload: { title: "GitHub — kunalKumar-13/Recall-me", domain: "github.com" } },
      { kind: "browser_search", ts: Date.now() / 1000 - 50 * 60,
        payload: { query: "windows protocol handler registration", engine: "google" } },
    ],
  },
};

async function shotWithMock(browser, name, mockData, { dir = OUT, height = 600, postShot } = {}) {
  const page = await browser.newPage({
    viewport: { width: 440, height },
    deviceScaleFactor: 2,
  });
  await page.route("**/v1/**", (route) => {
    const url = new URL(route.request().url());
    const body = mockData[url.pathname] ?? {};
    route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify(body),
    });
  });
  await page.goto(POPUP, { waitUntil: "load" });
  await page.waitForTimeout(1100);
  if (postShot) await postShot(page);
  await page.screenshot({ path: `${dir}/${name}.png` });
  await page.close();
  const subdir =
    dir === OUT_V2
      ? "extension-v2/"
      : dir === OUT_DEMO
        ? "demo/"
        : dir === OUT_7A
          ? "extension-7a/"
          : "";
  console.log(`  wrote assets/screenshots/${subdir}${name}.png`);
}

// ─────────────────────────────────────────────────────────────────────
// Phase 6C — v2 capture fixtures
//
// `extension-home`     full populated popup (recovery + investigations
//                      + today rail) — the canonical "wait this looks
//                      like product" surface.
// `extension-recovery` recovery card alone (no investigations, no
//                      today rail), so the confidence pill + the
//                      domain preview are the focal point.
// `extension-repair`   the disconnected + everConnected screen — the
//                      one with Open Recall + Repair connection (the
//                      popup's repair affordance).
// ─────────────────────────────────────────────────────────────────────
const MOCK_HOME_V2 = {
  "/v1/health": { ingested_total: 248, events_today: 248 },
  "/v1/recovery/recent": {
    candidates: [
      {
        id: "rc_demo",
        title: "WebSocket retry debugging",
        preview_caption: "2 tabs · 2 files · reopened after a 2-day gap",
        suggested_targets: [
          ["url", "https://stackoverflow.com/q/57294879"],
          ["url", "https://developer.mozilla.org/WebSocket"],
          ["path", "~/code/ws-retry/client.py"],
          ["path", "~/code/ws-retry/backoff.py"],
        ],
      },
    ],
  },
  "/v1/threads/recent": {
    threads: [
      { id: "t1", title: "WebSocket retries",
        timeline_summary: "4 sessions · 1w",
        surface_types: ["browser_visit", "browser_search"] },
      { id: "t2", title: "RLHF reward shaping",
        timeline_summary: "6 sessions · 2w",
        surface_types: ["browser_visit", "open"] },
      { id: "t3", title: "Proposal — Q3 narrative",
        timeline_summary: "3 sessions · 4d",
        surface_types: ["open", "chat_session"] },
      { id: "t4", title: "Healthcare research",
        timeline_summary: "5 sessions · 2w",
        surface_types: ["browser_visit", "chat_session"] },
    ],
  },
  "/v1/events/recent": {
    events: [
      { kind: "browser_search", ts: Date.now() / 1000 - 5 * 60,
        payload: { query: "websocket backoff jitter", engine: "google" } },
      { kind: "browser_visit", ts: Date.now() / 1000 - 18 * 60,
        payload: { title: "WebSocket — MDN", domain: "developer.mozilla.org" } },
      { kind: "chat_session", ts: Date.now() / 1000 - 45 * 60,
        payload: { title: "Backoff with jitter — review", platform: "claude" } },
      { kind: "browser_visit", ts: Date.now() / 1000 - 80 * 60,
        payload: { title: "Stack Overflow — retry-after", domain: "stackoverflow.com" } },
      { kind: "browser_search", ts: Date.now() / 1000 - 120 * 60,
        payload: { query: "rlhf reward shaping survey", engine: "google" } },
    ],
  },
};

// Phase 6D — the demo overlay fixture. Mirrors the payload the
// daemon ships from /v1/demo/state when state === "active":
// canonical WebSocket / Proposal / Research stories, deterministic
// HH:MM timeline. No engine; the popup short-circuits straight to
// the demo body when this endpoint returns state="active".
const _now = Math.floor(Date.now() / 1000);
const MOCK_DEMO_ACTIVE = {
  "/v1/health": { ingested_total: 0, events_today: 0 },
  "/v1/recovery/recent": { candidates: [] },
  "/v1/threads/recent": { threads: [] },
  "/v1/events/recent": { events: [] },
  "/v1/demo/state": {
    state: "active",
    payload: {
      recovery: {
        id: "demo-recovery-websocket",
        thread_id: "demo-thread-websocket",
        title: "WebSocket retry debugging",
        preview_caption: "2 tabs · 2 files · reopened after a 2-day gap",
        confidence: "high",
        tab_count: 2,
        file_count: 2,
        gap_label: "2-day gap",
        urls: [
          "https://stackoverflow.com/questions/57294879/websocket-retry-on-disconnect-best-practices",
          "https://developer.mozilla.org/en-US/docs/Web/API/WebSocket",
        ],
        files: ["~/code/ws-retry/client.py", "~/code/ws-retry/backoff.py"],
        chips: ["2 tabs", "2 files", "2d gap", "interrupted"],
      },
      investigations: [
        { id: "demo-thread-websocket", title: "WebSocket retry debugging",
          timeline_summary: "4 sessions · 3 days",
          surface_types: ["browser_visit", "browser_search", "open", "chat_session"] },
        { id: "demo-thread-proposal", title: "Healthcare pitch — proposal draft",
          timeline_summary: "3 sessions · 10 days",
          surface_types: ["open", "browser_visit", "chat_session"] },
        { id: "demo-thread-rlhf", title: "RLHF reward shaping",
          timeline_summary: "3 sessions · 1 week",
          surface_types: ["browser_visit", "browser_search"] },
      ],
      timeline: [
        { kind: "browser_search", ts: _now - 5 * 60,
          label: "websocket backoff jitter", detail: "google.com" },
        { kind: "browser_visit", ts: _now - 18 * 60,
          label: "WebSocket — MDN", detail: "developer.mozilla.org" },
        { kind: "open", ts: _now - 32 * 60,
          label: "backoff.py", detail: "~/code/ws-retry/" },
        { kind: "chat_session", ts: _now - 60 * 60,
          label: "Backoff with jitter — review", detail: "claude.ai" },
        { kind: "open", ts: _now - 95 * 60,
          label: "notes.md", detail: "~/Documents/healthcare-startup/" },
        { kind: "browser_visit", ts: _now - 120 * 60,
          label: "Y Combinator — Healthcare companies", detail: "ycombinator.com" },
        { kind: "browser_search", ts: _now - 150 * 60,
          label: "rlhf reward shaping", detail: "google.com" },
        { kind: "browser_visit", ts: _now - 180 * 60,
          label: "Training language models to follow instructions...",
          detail: "arxiv.org" },
      ],
      trust: {
        banner_title: "Example data",
        banner_body: "Nothing here came from your device.",
      },
      generated_at: _now,
    },
  },
};

const MOCK_RECOVERY_V2 = {
  "/v1/health": { ingested_total: 96, events_today: 96 },
  "/v1/recovery/recent": {
    candidates: [
      {
        id: "rc_v2",
        title: "Q3 narrative — proposal draft",
        preview_caption: "3 tabs · 1 file · reopened after a 5-day gap",
        suggested_targets: [
          ["url", "https://docs.google.com/document/d/abc"],
          ["url", "https://notion.so/q3-narrative"],
          ["url", "https://github.com/team/proposal"],
          ["path", "~/Documents/proposal-q3.md"],
        ],
      },
    ],
  },
  "/v1/threads/recent": { threads: [] },
  "/v1/events/recent": { events: [] },
};

// ─────────────────────────────────────────────────────────────────────
// Phase 7A — premium extension surface fixtures.
//
// The directive asks for an audit covering:
//   empty · capturing · active · resume · offline · search · demo
//
// `active` = populated body without a recovery (investigations +
//            timeline + activity). The hero slot is empty.
// `resume` = populated body WITH a recovery hero. This is the
//            *first opening of the popup after returning from
//            elsewhere* picture.
// `search` = the SearchOverlay open over a populated body.
// ─────────────────────────────────────────────────────────────────────
const MOCK_ACTIVE_NO_HERO = {
  "/v1/health": { ingested_total: 41, events_today: 41, desktop_apps_today: 2 },
  "/v1/recovery/recent": { candidates: [] },
  "/v1/threads/recent": {
    threads: [
      { id: "t1", title: "WebSocket retries",
        timeline_summary: "4 sessions - 3 days",
        surface_types: ["browser_visit", "browser_search", "open"] },
      { id: "t2", title: "Healthcare proposal",
        timeline_summary: "3 sessions - 1 week",
        surface_types: ["open", "browser_visit"] },
      { id: "t3", title: "RLHF reward shaping",
        timeline_summary: "3 sessions - 1 week",
        surface_types: ["browser_search"] },
    ],
  },
  "/v1/events/recent": {
    events: [
      { kind: "chat_session", ts: Date.now() / 1000 - 18 * 60,
        payload: { title: "prompt engineering notes", platform: "ChatGPT" } },
      { kind: "browser_visit", ts: Date.now() / 1000 - 55 * 60,
        payload: { title: "backoff retry article", domain: "GitHub" } },
      { kind: "browser_visit", ts: Date.now() / 1000 - 110 * 60,
        payload: { title: "websocket reconnect", domain: "StackOverflow" } },
      { kind: "browser_search", ts: Date.now() / 1000 - 175 * 60,
        payload: { query: "websocket backoff jitter", engine: "Google" } },
    ],
  },
};

const MOCK_RESUME_7A = {
  ...MOCK_ACTIVE_NO_HERO,
  "/v1/recovery/recent": {
    candidates: [
      {
        id: "rc_7a",
        title: "WebSocket retry debugging",
        preview_caption: "2 tabs - 2 files - returned after 2d",
        suggested_targets: [
          ["url", "https://stackoverflow.com/q/57294879"],
          ["url", "https://developer.mozilla.org/WebSocket"],
          ["path", "~/code/ws-retry/client.py"],
          ["path", "~/code/ws-retry/backoff.py"],
        ],
      },
    ],
  },
};

try {
  const browser = await chromium.launch();
  // historical v1 outputs — preserved untouched for diffability
  await shot(browser, "extension-connected", "", { mock: true });
  await shotWithMock(browser, "extension-empty", MOCK_EMPTY);
  await shotWithMock(browser, "extension-capturing", MOCK_CAPTURING);
  await shot(browser, "extension-missing", "?state=missing");
  await shot(browser, "extension-disconnected", "?state=disconnected");
  await shot(browser, "extension-offline", "?state=offline");
  await shot(browser, "extension-loading", "?state=loading");

  // Phase 6C v2 outputs — the premium captures.
  await shotWithMock(browser, "extension-home", MOCK_HOME_V2, { dir: OUT_V2 });
  await shotWithMock(browser, "extension-empty", MOCK_EMPTY, { dir: OUT_V2 });
  await shotWithMock(browser, "extension-recovery", MOCK_RECOVERY_V2, { dir: OUT_V2 });
  await shot(browser, "extension-repair", "?state=disconnected", { dir: OUT_V2 });
  await shot(browser, "extension-offline", "?state=offline", { dir: OUT_V2 });

  // Phase 6D demo overlay — engine empty + demo_mode.state === "active".
  // The DemoState endpoint returns the canonical payload (WebSocket /
  // Proposal / Research), and the popup renders the demo overlay via
  // the same ConnectedBody as a real populated surface.
  await shotWithMock(browser, "demo-extension", MOCK_DEMO_ACTIVE, { dir: OUT_DEMO });
  // The "post-transition" shot — same engine state, but the user
  // dismissed the demo (or a real event arrived); the popup falls
  // back to the empty surface. Captured for FIRST_MAGIC.md.
  await shotWithMock(browser, "demo-extension-empty", MOCK_EMPTY, { dir: OUT_DEMO });

  // Phase 7A — premium extension surface captures. Viewport bumps to
  // 640 to match the directive's frozen 440 × 640 popup size.
  const opt7a = { dir: OUT_7A, height: 640 };
  await shotWithMock(browser, "empty", MOCK_EMPTY, opt7a);
  await shotWithMock(browser, "capturing", MOCK_CAPTURING, opt7a);
  await shotWithMock(browser, "active", MOCK_ACTIVE_NO_HERO, opt7a);
  await shotWithMock(browser, "resume", MOCK_RESUME_7A, opt7a);
  await shotWithMock(browser, "demo", MOCK_DEMO_ACTIVE, opt7a);
  await shot(browser, "offline", "?state=offline", { dir: OUT_7A, height: 640 });
  await shotWithMock(browser, "search", MOCK_RESUME_7A, {
    ...opt7a,
    postShot: async (page) => {
      await page.keyboard.press("Control+K");
      await page.waitForTimeout(360);
    },
  });

  await browser.close();
  console.log("done.");
} finally {
  server.kill();
}
