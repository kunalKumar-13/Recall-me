"""Phase 6M — desktop memory layer.

Captures *metadata only* about the foreground window the user is
focused on: app name, window title, focus duration, switch count,
optional file path (only when the title exposes one).

Strict contract:

  - **No screenshots, no OCR, no audio, no pixel data.**
  - Events land in the same `~/.recall/events/YYYY-MM-DD.jsonl`
    files the rest of the engine writes to. The new event kind
    is ``desktop_window`` (see `events.KIND`).
  - The aggregator drops focus blocks shorter than
    `MIN_FOCUS_S` (default 30 s) so alt-tabs / notification
    pop-ups never make it to the log.
  - The watcher itself can be killed by `RECALL_DESKTOP=off` in
    the environment.
  - Recall's own windows are blocklisted (the layer never observes
    itself).

Modules:

  - ``events``      `KIND` constant + `DesktopWindowEvent` dataclass
  - ``processes``   PID → exe-name resolver (Windows)
  - ``windows``     foreground-window probe (Windows)
  - ``sessions``    pure focus-block aggregator
  - ``watcher``     the background thread that polls + emits

Public surface: `DesktopWatcher`, `start_watcher()`,
`stop_watcher()`, `KIND`, `DesktopWindowEvent`.
"""

from .events import KIND, DesktopWindowEvent, iso_now
from .processes import resolve as resolve_pid
from .sessions import (
    BLOCKLIST_EXE,
    FocusAggregator,
    MIN_FOCUS_S,
    RE_FOCUS_WINDOW_S,
)
from .watcher import (
    DEFAULT_POLL_INTERVAL_S,
    DesktopWatcher,
    start_watcher,
    stop_watcher,
)
from .windows import ForegroundWindow, is_supported, probe_foreground

__all__ = [
    "BLOCKLIST_EXE",
    "DEFAULT_POLL_INTERVAL_S",
    "DesktopWatcher",
    "DesktopWindowEvent",
    "FocusAggregator",
    "ForegroundWindow",
    "KIND",
    "MIN_FOCUS_S",
    "RE_FOCUS_WINDOW_S",
    "is_supported",
    "iso_now",
    "probe_foreground",
    "resolve_pid",
    "start_watcher",
    "stop_watcher",
]
