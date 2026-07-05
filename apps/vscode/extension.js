/**
 * Recall — VS Code companion.
 *
 * The editor half of capture: when you settle on a file (active
 * editor for a beat, or a save), one `open` event goes to the local
 * daemon. Same contract as the browser extension — metadata only
 * (path + filename), one loopback destination, a small in-memory
 * outbox so a sleeping daemon never loses events.
 *
 * Plain JavaScript on purpose: no build step, no dependencies. The
 * folder itself is the extension.
 */

const vscode = require("vscode");

const SETTLE_MS = 2000; // active-editor dwell before an event counts
const FLUSH_MS = 30_000; // outbox retry cadence
const MAX_QUEUE = 500;
const DEDUPE_MS = 5 * 60_000; // same file within 5 min → one event

/** @type {Array<{kind: string, payload: object}>} */
const outbox = [];
/** @type {Map<string, number>} last-sent per path */
const lastSent = new Map();
let settleTimer = null;
let flushTimer = null;

function config() {
  const c = vscode.workspace.getConfiguration("recall");
  return {
    enabled: c.get("enabled", true),
    endpoint: String(c.get("endpoint", "http://127.0.0.1:4545")).replace(/\/$/, ""),
  };
}

function fileOf(document) {
  if (!document || document.uri.scheme !== "file") return null;
  if (document.isUntitled) return null;
  return document.uri.fsPath;
}

function enqueue(path) {
  const now = Date.now();
  const prev = lastSent.get(path) || 0;
  if (now - prev < DEDUPE_MS) return;
  lastSent.set(path, now);
  outbox.push({
    kind: "open",
    payload: {
      path,
      title: path.split(/[\\/]/).pop() || path,
      ts: new Date().toISOString(),
    },
  });
  while (outbox.length > MAX_QUEUE) outbox.shift();
  void flush();
}

let flushing = false;
async function flush() {
  if (flushing || outbox.length === 0) return;
  const { enabled, endpoint } = config();
  if (!enabled) return;
  flushing = true;
  try {
    const batch = outbox.slice(0, 100);
    const res = await fetch(`${endpoint}/v1/events/batch`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ events: batch }),
    });
    if (res.ok) outbox.splice(0, batch.length);
    // Non-OK / network error: keep the backlog; the interval retries.
  } catch {
    /* daemon asleep — the outbox holds everything */
  } finally {
    flushing = false;
  }
}

function onActiveEditor(editor) {
  if (settleTimer) clearTimeout(settleTimer);
  const path = editor ? fileOf(editor.document) : null;
  if (!path || !config().enabled) return;
  // Only count a file you actually settled on — flicking through the
  // tab strip should not pollute memory.
  settleTimer = setTimeout(() => enqueue(path), SETTLE_MS);
}

function onSave(document) {
  const path = fileOf(document);
  if (!path || !config().enabled) return;
  // A save is deliberate — no settle needed, but still deduped.
  lastSent.delete(path);
  enqueue(path);
}

function activate(context) {
  context.subscriptions.push(
    vscode.window.onDidChangeActiveTextEditor(onActiveEditor),
    vscode.workspace.onDidSaveTextDocument(onSave),
  );
  onActiveEditor(vscode.window.activeTextEditor);
  flushTimer = setInterval(() => void flush(), FLUSH_MS);
  context.subscriptions.push({
    dispose() {
      if (settleTimer) clearTimeout(settleTimer);
      if (flushTimer) clearInterval(flushTimer);
    },
  });
}

function deactivate() {
  void flush();
}

module.exports = { activate, deactivate };
