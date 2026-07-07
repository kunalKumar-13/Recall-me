/**
 * Browser dwell — the work-session signal (Capture C4).
 *
 * sources.js records *arrivals* (you opened a page). This module
 * records *attention*: one `browser_focus` event when focus leaves a
 * page after at least MIN_DWELL_MS, carrying how long you were there
 * and a work-block hint. A block is an unbroken run of browser
 * attention; BLOCK_GAP_MS of silence starts a new one, so the id is
 * the epoch second the run began (`wb-1751882400`) — derived from the
 * data, no randomness. The engine stores the kind as a grouping
 * signal only; it is deliberately absent from episodic retrieval.
 *
 * The tracker core is pure ((page, now) → emission) and node-tested;
 * the Chrome listeners are thin wrappers. In-memory state may be lost
 * to MV3 worker eviction — that costs at most one dwell interval,
 * never a queued event (delivery stays durable via the outbox).
 */

import { getDomain, shouldSkipScheme, isExcluded } from "./normalize.js";
import { enqueue } from "./outbox.js";

// Below this, attention reads as passing through, not working.
export const MIN_DWELL_MS = 8_000;
// Above this, the "attention" is a tab left focused overnight.
export const MAX_DWELL_MS = 30 * 60_000;
// Browser silence that ends one work block and starts the next.
export const BLOCK_GAP_MS = 5 * 60_000;

export function createDwellTracker({
  minDwellMs = MIN_DWELL_MS,
  maxDwellMs = MAX_DWELL_MS,
  blockGapMs = BLOCK_GAP_MS,
} = {}) {
  let current = null; // { url, title, startedAt }
  let blockStart = 0; // epoch ms of the current work block's first focus
  let lastSeen = 0; // last moment attention was on the browser

  function finish(now) {
    if (!current) return null;
    const page = current;
    current = null;
    const dwell = Math.min(now - page.startedAt, maxDwellMs);
    if (dwell < minDwellMs) return null;
    return {
      url: page.url,
      title: page.title || "",
      dwell_ms: dwell,
      block: `wb-${Math.floor(blockStart / 1000)}`,
      ts: new Date(now).toISOString(),
    };
  }

  return {
    /**
     * Attention landed on a page (tab switch, window focus, nav).
     * Returns the finished dwell record for the previous page, or
     * null. Pass `page = null` for "focused something untrackable".
     */
    focus(page, now) {
      if (blockStart === 0 || now - lastSeen > blockGapMs) blockStart = now;
      lastSeen = now;
      const done = finish(now);
      current = page
        ? { url: page.url, title: page.title || "", startedAt: now }
        : null;
      return done;
    },

    /** Attention left the browser (window blur, last tab closed). */
    blur(now) {
      lastSeen = now;
      return finish(now);
    },

    /** Titles settle after focus lands; keep the current page's fresh. */
    retitle(url, title) {
      if (current && current.url === url && title) current.title = title;
    },
  };
}

/**
 * Register the dwell listeners. Same getter contract as
 * registerSources: `isEnabled` / `excluded` / `allowKind` are read
 * live so the Settings toggles and pause are honoured without
 * re-registering. Dwell rides the browsing switch.
 */
export function registerDwell({ isEnabled, excluded, allowKind }) {
  const tracker = createDwellTracker();
  const allowed =
    typeof allowKind === "function" ? allowKind : () => true;

  function emit(record) {
    if (!record) return;
    if (!allowed("browser_focus")) return;
    if (shouldSkipScheme(record.url)) return;
    const domain = getDomain(record.url);
    if (isExcluded(domain, excluded())) return;
    void enqueue({ kind: "browser_focus", payload: { ...record, domain } });
  }

  function focusTab(tab, now) {
    // Anything untrackable (capture off, incognito, internal pages)
    // still ends the previous dwell — attention has moved on.
    const trackable =
      isEnabled() &&
      tab &&
      tab.url &&
      !tab.incognito &&
      !shouldSkipScheme(tab.url);
    if (!trackable) {
      emit(tracker.blur(now));
      return;
    }
    emit(tracker.focus({ url: tab.url, title: tab.title || "" }, now));
  }

  chrome.tabs.onActivated.addListener(({ tabId }) => {
    chrome.tabs.get(tabId, (tab) => {
      if (chrome.runtime.lastError) return;
      focusTab(tab, Date.now());
    });
  });

  chrome.windows.onFocusChanged.addListener((windowId) => {
    const now = Date.now();
    if (windowId === chrome.windows.WINDOW_ID_NONE) {
      emit(tracker.blur(now));
      return;
    }
    chrome.tabs.query({ active: true, windowId }, (tabs) => {
      if (chrome.runtime.lastError) return;
      focusTab(tabs && tabs[0], now);
    });
  });

  chrome.tabs.onUpdated.addListener((tabId, changeInfo, tab) => {
    if (!tab || !tab.active) return;
    if (typeof changeInfo.url === "string") {
      // Same-tab navigation — attention moved to a new page.
      focusTab(tab, Date.now());
    } else if (typeof changeInfo.title === "string" && tab.url) {
      tracker.retitle(tab.url, changeInfo.title);
    }
  });

  // SPA route changes never fire onUpdated with a url; treat them as
  // attention moving pages, same as sources.js does for visits.
  if (chrome.webNavigation && chrome.webNavigation.onHistoryStateUpdated) {
    chrome.webNavigation.onHistoryStateUpdated.addListener((details) => {
      if (details.frameId !== 0) return;
      chrome.tabs.get(details.tabId, (tab) => {
        if (chrome.runtime.lastError) return;
        if (!tab || !tab.active) return;
        focusTab({ ...tab, url: details.url }, Date.now());
      });
    });
  }
}
