/**
 * Recall — capture service worker (MV3, ES module).
 *
 * Thin wiring only: load the enabled flag + domain exclude list from
 * chrome.storage, then register the capture sources and the durable
 * outbox's retry alarm. All the logic lives in capture/:
 *
 *   capture/normalize.js  pure URL → event classifier (node-tested)
 *   capture/outbox.js     durable, batched, retrying sender
 *   capture/sources.js    tab + SPA listeners with title-settle
 *   capture/dwell.js      attention tracker → browser_focus events
 *
 * No remote networking, no DOM scraping, no telemetry. The manifest
 * permits exactly one network origin — http://127.0.0.1:4545 — so the
 * browser physically refuses any other destination. Capture writes go
 * to the durable outbox, which drains to POST /v1/events/batch.
 */

import { registerDwell } from "./capture/dwell.js";
import { registerSources } from "./capture/sources.js";
import { registerRetryAlarm, flush } from "./capture/outbox.js";

let enabled = true;
let excludedDomains = new Set();
// Temporary pause (epoch ms). The popup writes it; capture skips
// everything until the moment passes — no restart, no alarm needed.
let pauseUntil = 0;
// Per-kind capture switches — the Settings toggles. Every toggle in
// the popup maps to a real gate here; a control that changes nothing
// is worse than no control.
let settings = {
  captureBrowsing: true,
  captureSearches: true,
  captureChats: true,
};

const SETTINGS_KEY = "recall.settings";

// browser_focus (dwell) rides the browsing switch — attention on
// pages is browsing capture, not a fourth category to explain.
const KIND_GATE = {
  browser_visit: () => settings.captureBrowsing,
  browser_focus: () => settings.captureBrowsing,
  browser_search: () => settings.captureSearches,
  chat_session: () => settings.captureChats,
};

function applySettings(blob) {
  if (!blob || typeof blob !== "object") return;
  for (const key of Object.keys(settings)) {
    if (typeof blob[key] === "boolean") settings[key] = blob[key];
  }
}

chrome.storage.local.get(
  ["enabled", "excludedDomains", "pauseUntil", SETTINGS_KEY],
  (result) => {
    if (typeof result.enabled === "boolean") enabled = result.enabled;
    if (Array.isArray(result.excludedDomains)) {
      excludedDomains = new Set(result.excludedDomains);
    }
    if (typeof result.pauseUntil === "number") pauseUntil = result.pauseUntil;
    applySettings(result[SETTINGS_KEY]);
    // A backlog may have built up while the worker was evicted/asleep.
    void flush();
  },
);

chrome.storage.onChanged.addListener((changes) => {
  if ("enabled" in changes) enabled = changes.enabled.newValue !== false;
  if ("excludedDomains" in changes) {
    excludedDomains = new Set(changes.excludedDomains.newValue || []);
  }
  if ("pauseUntil" in changes) {
    pauseUntil = typeof changes.pauseUntil.newValue === "number"
      ? changes.pauseUntil.newValue
      : 0;
  }
  if (SETTINGS_KEY in changes) applySettings(changes[SETTINGS_KEY].newValue);
});

registerRetryAlarm();
const gates = {
  isEnabled: () => enabled && Date.now() >= pauseUntil,
  excluded: () => excludedDomains,
  allowKind: (kind) => {
    const gate = KIND_GATE[kind];
    return gate ? gate() : true;
  },
};
registerSources(gates);
registerDwell(gates);
