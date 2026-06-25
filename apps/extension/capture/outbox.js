/**
 * Durable, batched, retrying sender.
 *
 * The pre-refactor capture did a fire-and-forget fetch per event and
 * explicitly "never queued locally" — so every event captured while
 * the daemon was unreachable (restarting, laptop asleep, first-launch
 * race) was lost forever. For a continuity product, silently losing
 * the user's work is the cardinal sin. This module fixes it:
 *
 *   • enqueue() appends to a queue persisted in chrome.storage.local,
 *     so a backlog survives MV3 service-worker eviction.
 *   • flush() drains the queue to POST /v1/events/batch in one
 *     round-trip; on success it removes exactly the delivered items,
 *     on failure it leaves them and schedules a retry.
 *   • a chrome.alarms tick re-runs flush() so a backlog drains the
 *     moment the daemon is reachable again — even after the worker was
 *     evicted, which a setTimeout would not survive.
 *
 * Each queued item carries a client id so a flush that races with new
 * enqueues removes only what it actually delivered. Capture time is
 * stamped at enqueue (in normalize.js), so a delayed flush still
 * records the true event time.
 */

const ENGINE = "http://127.0.0.1:4545";
const BATCH_URL = `${ENGINE}/v1/events/batch`;
const QUEUE_KEY = "outbox";
const MAX_BATCH = 500; // matches the server's per-request cap
const MAX_QUEUE = 5000; // backlog ceiling; oldest dropped past this
const RETRY_ALARM = "recall-outbox-retry";

let _seq = 0;
let _flushing = false;
let _rerun = false;

async function _read() {
  const got = await chrome.storage.local.get(QUEUE_KEY);
  const q = got[QUEUE_KEY];
  return Array.isArray(q) ? q : [];
}

async function _write(queue) {
  await chrome.storage.local.set({ [QUEUE_KEY]: queue });
}

export async function enqueue(event) {
  if (!event) return;
  const queue = await _read();
  // A monotonic counter + capture time is enough to dedupe a flush;
  // no Math.random needed.
  const id = `${Date.now()}-${_seq++}`;
  queue.push({ id, kind: event.kind, payload: event.payload });
  // Drop oldest if a long offline stretch blew past the ceiling.
  const trimmed =
    queue.length > MAX_QUEUE ? queue.slice(queue.length - MAX_QUEUE) : queue;
  await _write(trimmed);
  void flush(); // best-effort immediate delivery; retries are alarm-driven
}

export async function flush() {
  // A flush already running picks up newly-enqueued items on its next
  // pass; we only need to re-arm it so the just-added item isn't
  // stranded if it lands as the running flush is finishing.
  if (_flushing) {
    _rerun = true;
    return;
  }
  _flushing = true;
  try {
    do {
      _rerun = false;
      let queue = await _read();
      while (queue.length) {
        const batch = queue.slice(0, MAX_BATCH);
        const ids = new Set(batch.map((e) => e.id));
        let ok = false;
        try {
          const res = await fetch(BATCH_URL, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
              events: batch.map((e) => ({ kind: e.kind, payload: e.payload })),
            }),
          });
          ok = res.ok;
        } catch {
          ok = false; // daemon down / port race — keep the backlog
        }
        if (!ok) {
          await _scheduleRetry();
          return; // finally clears _flushing; the alarm will retry
        }
        // Remove exactly what we delivered; items enqueued during the
        // POST survive (re-read from storage, not the stale snapshot).
        queue = (await _read()).filter((e) => !ids.has(e.id));
        await _write(queue);
      }
    } while (_rerun);
  } finally {
    _flushing = false;
  }
}

async function _scheduleRetry() {
  try {
    // 1 minute is the MV3 alarms floor; fine — the backlog is durable,
    // so a slightly delayed drain loses nothing.
    chrome.alarms.create(RETRY_ALARM, { delayInMinutes: 1 });
  } catch {
    // alarms unavailable — the next enqueue will retry.
  }
}

// Wire the alarm to a flush. Call once at worker startup.
export function registerRetryAlarm() {
  try {
    chrome.alarms.onAlarm.addListener((alarm) => {
      if (alarm.name === RETRY_ALARM) void flush();
    });
  } catch {
    // no alarms API — degrade to enqueue-triggered flushes only.
  }
}

export async function pendingCount() {
  return (await _read()).length;
}
