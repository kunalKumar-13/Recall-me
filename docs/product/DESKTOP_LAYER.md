# DESKTOP_LAYER.md — what Recall sees outside the browser

A continuity layer that only watches the browser misses half the
day. Phase 6M adds a desktop foreground watcher so an
investigation that spans *Cursor → VLC → Notion* reads as one
thread, not three disconnected silences.

The contract is strict — **metadata only**. No screenshots. No
OCR. No audio. No pixel data. The watcher reads what the
operating system already exposes (foreground window title,
process executable name, focus duration) and writes one
``desktop_window`` event per focus block to the same
`~/.recall/events/YYYY-MM-DD.jsonl` file every other event lives
in. Nothing more.

Pairs with [`TRUST.md`](TRUST.md) (the public boundary) and
[`STABILITY.md`](../engineering/STABILITY.md) (failure
philosophy — the watcher must never crash the host).

---

## What the watcher captures

| Field | Source | Notes |
|---|---|---|
| ``app`` | `QueryFullProcessImageNameW` basename | e.g. ``Cursor.exe``, ``vlc.exe`` |
| ``title`` | `GetWindowTextW` | the window title the OS already exposed |
| ``duration`` | aggregator | integer seconds; below the 30-second floor the block is dropped |
| ``focus_start`` / ``focus_end`` | aggregator | ISO 8601 UTC |
| ``switch_count`` | aggregator | how many times focus left & came back inside a 60-second re-focus window |
| ``path`` | best-effort from window title | **only** when the title exposes a real path; never inferred from the EXE or process command line |
| ``process`` | `OpenProcess` + `QueryFullProcessImageNameW` | `{pid, exe}` — never the command line |

## What the watcher does NOT capture

| Surface | Why excluded |
|---|---|
| Screenshots | Out of scope. Always. |
| OCR / accessibility-tree text | Out of scope. The watcher reads `GetWindowTextW` and stops. |
| Audio fragments | Out of scope. Always. |
| Clipboard | Out of scope. The watcher never reads or writes the clipboard. |
| Command line / `/proc/$pid/cmdline` | Out of scope. The EXE basename + path is enough; the full command line often leaks tokens. |
| Browser tabs | Already captured by the browser extension. The watcher's blocklist explicitly skips Recall's own windows; the extension owns the browser surface. |
| Recall's own windows | `BLOCKLIST_EXE` prefix-match keeps the launcher / settings dialog out of the log. |

## The aggregator rules

`app/core/desktop/sessions.py:FocusAggregator` enforces three
rules so the on-disk JSONL stays calm:

1. **Minimum focus duration** — `MIN_FOCUS_S = 30`. A focus
   block shorter than this never reaches the log. Alt-tabs,
   notification pop-ups, and the lock-screen pre-screensaver
   tick all fall below this floor.
2. **Re-focus consolidation** — if the user toggles between
   the same window twice within `RE_FOCUS_WINDOW_S = 60`, the
   two focus blocks merge into a single event with
   `switch_count = 2` (rather than two short events).
3. **Blocklist** — `BLOCKLIST_EXE` prefixes (Recall's own
   binaries) never produce events.

The aggregator is pure — no I/O, no globals; the watcher tests
drive it directly.

## The watcher

`app/core/desktop/watcher.py:DesktopWatcher` runs as a single
daemon thread:

- polls `windows.probe_foreground()` every `poll_interval`
  seconds (default 2 s),
- feeds the probe to the `FocusAggregator`,
- when a finalised focus block crosses the floor, writes one
  ``desktop_window`` event via the existing `EventLogger`.

Disable rules:

| Rule | Where |
|---|---|
| `RECALL_DESKTOP=off` in the environment | watcher refuses to start |
| Non-Windows host | watcher refuses to start (Windows is the only platform with a probe today) |
| `desktop_capture_enabled = False` in `~/.recall/config.json` | the application boot path doesn't call `start_watcher()` |
| Delete `app/core/desktop/` | engine layer is purely additive; no downstream code depends on it |

## The event shape on disk

A `desktop_window` event in the JSONL looks like:

```json
{
  "ts": "2026-05-23T12:10:00Z",
  "session_id": "s_…",
  "kind": "desktop_window",
  "payload": {
    "app": "Cursor.exe",
    "title": "backoff.py - Cursor",
    "duration": 600,
    "focus_start": "2026-05-23T12:00:00Z",
    "focus_end": "2026-05-23T12:10:00Z",
    "switch_count": 1,
    "path": "~/code/ws-retry/backoff.py",
    "process": { "pid": 1234, "exe": "C:/Users/x/AppData/Local/.../Cursor.exe" }
  }
}
```

The `payload.path` field is optional — only present when the
window title exposed a real path. The `payload.process` field
is informational; it carries `pid` + `exe` only (never
command-line, never environment).

## How it joins the rest of the engine

`desktop_window` is a peer kind to `browser_visit`,
`browser_search`, `chat_session`, `open`, `reveal`. The existing
engine layers consume the event without modification:

- **sessions** — groups events by 30-minute idle gap. Desktop
  focus blocks naturally join browser visits + file opens into
  one session.
- **micro-contexts** — coherent slices inside a session. A
  Cursor + Stack Overflow + claude.ai pairing reads as one
  context.
- **threads** — persistent topic identity over time. A WebSocket
  debugging thread now legitimately spans browser tabs, code
  files, and Cursor focus blocks.
- **recovery** — surfaces resumable work. The recovery card's
  *target count* now factors in the desktop apps the user was
  focused on; the launcher's chip strip can read
  `[2 tabs] [3 files] [1 app] [2d gap]` once the engine flows
  the new count through (a follow-up phase wires the engine
  side; the data layer is already there).

## Where the founder sees it

- **`/desktop` route** in the control room
  ([`apps/admin/web/app/desktop/page.tsx`](../../apps/admin/web/app/desktop/page.tsx))
  surfaces apps / focus / top tools / session log. Live read
  from `~/.recall/events/*.jsonl`.
- **Extension popup header** shows a small `⊞-N` badge next
  to the today caption when `health.desktop_apps_today > 0`.
- **Launcher's Continue chip strip** (a planned follow-up):
  `[N app]` joins the existing `[2 tabs] [3 files] [2d gap]`
  chips when the engine's recovery surface counts desktop
  events.

## Verification

The aggregator + watcher are unit-testable without Qt or a
running OS shell:

```python
from datetime import datetime, timedelta, timezone
from app.core.desktop import FocusAggregator, ForegroundWindow

agg = FocusAggregator(min_focus_s=10, re_focus_window_s=20)
now = datetime(2026, 5, 23, 12, 0, 0, tzinfo=timezone.utc)
fg1 = ForegroundWindow(hwnd=1, title="backoff.py - Cursor",
                       pid=1, exe_name="Cursor.exe", exe_path="…")
fg2 = ForegroundWindow(hwnd=2, title="startup.mp4 - VLC",
                       pid=2, exe_name="vlc.exe", exe_path="…")

# 15 seconds of fg1 → an event (above 10s floor).
agg.observe(fg1, now=now)
events = agg.observe(fg2, now=now + timedelta(seconds=15))
assert events[0].app == "Cursor.exe"
assert events[0].duration == 15
```

The HTTP path is `POST /v1/events/desktop` with the
`DesktopWindowIn` schema in `api/schemas.py`. Any field outside
the schema is ignored (the directive's *metadata only* rule
enforced at the request boundary).

## Related

- [`PHASE_6M_STATUS.md`](../../archive/phase-status/PHASE_6M_STATUS.md) —
  the engineering receipt.
- [`TRUST.md`](TRUST.md) — the public five-rule contract this
  layer respects.
- [`TRUST_LEDGER.md`](../engineering/TRUST_LEDGER.md) — the
  on-disk boundary spec.
- `app/core/desktop/` — the watcher + aggregator + Windows
  bindings.
- `apps/admin/web/app/desktop/page.tsx` — the founder view.
