/**
 * Capture sources — the stateful half: listens to the browser and
 * turns activity into normalized events handed to the durable outbox.
 *
 * Title-settle: chrome.tabs.onUpdated fires at load and again when an
 * SPA rewrites document.title a beat later (ChatGPT, Gemini, GitHub).
 * Firing at load captures the generic placeholder; we defer SETTLE_MS
 * past the last change (capped at MAX_WAIT_MS) so we record the
 * truthful title. webNavigation.onHistoryStateUpdated adds SPA route
 * changes (pushState) that never trigger a full load.
 *
 * Coalescing is best-effort (an in-memory timer that may not survive
 * worker eviction); *delivery* is not — every settle hands the event
 * to the durable outbox, which is what guarantees it reaches the
 * engine.
 */

import {
  classify,
  getDomain,
  shouldSkipScheme,
  isExcluded,
} from "./normalize.js";
import { enqueue } from "./outbox.js";

const SETTLE_MS = 1500;
const MAX_WAIT_MS = 4000;

const pending = new Map();

// The per-kind Settings gate. Checked at emit time (not schedule
// time) so a toggle flipped mid-settle is still honoured.
let _allowKind = () => true;

function _emit(url, title) {
  const cls = classify(url, title || "");
  if (cls && _allowKind(cls.kind)) void enqueue(cls);
}

function _scheduleFire(tabId, url, title, isEnabled, excluded) {
  if (!isEnabled()) return;
  const domain = getDomain(url);
  if (isExcluded(domain, excluded())) return;

  const now = Date.now();
  const prior = pending.get(tabId);
  if (prior && prior.url !== url) {
    // URL changed for this tab — emit the old URL now with its last
    // known title, then start a fresh timer for the new URL.
    if (prior.timer) clearTimeout(prior.timer);
    _emit(prior.url, prior.title);
    pending.delete(tabId);
  }

  const existing = pending.get(tabId);
  const startedAt = existing ? existing.startedAt : now;
  const remaining = Math.max(0, MAX_WAIT_MS - (now - startedAt));
  const delay = Math.min(SETTLE_MS, remaining);
  if (existing && existing.timer) clearTimeout(existing.timer);

  const timer = setTimeout(() => {
    const entry = pending.get(tabId);
    if (!entry || entry.url !== url) return;
    pending.delete(tabId);
    _emit(entry.url, entry.title);
  }, delay);

  pending.set(tabId, {
    url,
    title: title || (existing && existing.url === url ? existing.title : ""),
    startedAt,
    timer,
  });
}

/**
 * Register all capture listeners. `isEnabled` / `excluded` /
 * `allowKind` are getters so a live Settings toggle is honoured
 * without re-registering.
 */
export function registerSources({ isEnabled, excluded, allowKind }) {
  if (typeof allowKind === "function") _allowKind = allowKind;
  chrome.tabs.onUpdated.addListener((tabId, changeInfo, tab) => {
    if (!isEnabled()) return;
    if (!tab || !tab.url || tab.incognito) return;
    if (shouldSkipScheme(tab.url)) return;
    // Schedule on load completion or a title update; ignore favicon,
    // audible, pinned, and other noise.
    const isLoadComplete = changeInfo.status === "complete";
    const isTitleUpdate = typeof changeInfo.title === "string";
    if (!isLoadComplete && !isTitleUpdate) return;
    _scheduleFire(tabId, tab.url, tab.title || "", isEnabled, excluded);
  });

  // SPA route changes that never trigger a full page load (the URL
  // changes via the History API). The title usually updates a moment
  // later, which the settle timer above then captures.
  if (chrome.webNavigation && chrome.webNavigation.onHistoryStateUpdated) {
    chrome.webNavigation.onHistoryStateUpdated.addListener((details) => {
      if (!isEnabled()) return;
      if (details.frameId !== 0) return; // top frame only
      if (shouldSkipScheme(details.url)) return;
      _scheduleFire(details.tabId, details.url, "", isEnabled, excluded);
    });
  }

  chrome.tabs.onRemoved.addListener((tabId) => {
    // A tab closed before its timer fired — emit one final event so we
    // don't silently lose work the user was looking at.
    const entry = pending.get(tabId);
    if (entry) {
      if (entry.timer) clearTimeout(entry.timer);
      _emit(entry.url, entry.title);
      pending.delete(tabId);
    }
  });
}
