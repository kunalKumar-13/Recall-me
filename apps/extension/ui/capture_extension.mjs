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
import { fileURLToPath } from "node:url";
import { dirname, resolve } from "node:path";

const HERE = dirname(fileURLToPath(import.meta.url));
const POPUP_DIR = resolve(HERE, "../popup");
const OUT = resolve(HERE, "../../../assets/screenshots");

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
    events: [
      { kind: "browser_search", payload: { query: "websocket backoff jitter", engine: "google" } },
      { kind: "browser_visit", payload: { title: "WebSocket — MDN", domain: "developer.mozilla.org" } },
      { kind: "chat_session", payload: { title: "Backoff with jitter — review", platform: "claude" } },
    ],
  },
};

async function shot(browser, name, query, { mock = false } = {}) {
  const page = await browser.newPage({
    viewport: { width: 440, height: 600 },
    deviceScaleFactor: 2,
  });
  if (mock) {
    await page.route("**/v1/**", (route) => {
      const url = new URL(route.request().url());
      const body = MOCK[url.pathname];
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
  await page.screenshot({ path: `${OUT}/${name}.png` });
  await page.close();
  console.log(`  wrote assets/screenshots/${name}.png`);
}

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
    events: [
      { kind: "browser_search", payload: { query: "websocket backoff jitter", engine: "google" } },
      { kind: "browser_visit", payload: { title: "WebSocket — MDN", domain: "developer.mozilla.org" } },
      { kind: "chat_session", payload: { title: "Backoff with jitter — review", platform: "claude" } },
      { kind: "browser_visit", payload: { title: "GitHub — kunalKumar-13/Recall-me", domain: "github.com" } },
      { kind: "browser_search", payload: { query: "windows protocol handler registration", engine: "google" } },
    ],
  },
};

async function shotWithMock(browser, name, mockData) {
  const page = await browser.newPage({
    viewport: { width: 440, height: 600 },
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
  await page.screenshot({ path: `${OUT}/${name}.png` });
  await page.close();
  console.log(`  wrote assets/screenshots/${name}.png`);
}

try {
  const browser = await chromium.launch();
  await shot(browser, "extension-connected", "", { mock: true });
  await shotWithMock(browser, "extension-empty", MOCK_EMPTY);
  await shotWithMock(browser, "extension-capturing", MOCK_CAPTURING);
  await shot(browser, "extension-missing", "?state=missing");
  await shot(browser, "extension-disconnected", "?state=disconnected");
  await shot(browser, "extension-offline", "?state=offline");
  await shot(browser, "extension-loading", "?state=loading");
  await browser.close();
  console.log("done.");
} finally {
  server.kill();
}
