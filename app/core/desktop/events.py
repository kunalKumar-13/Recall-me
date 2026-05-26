"""Phase 6M — desktop event data model.

Defines the *one* event kind this layer emits — ``desktop_window`` —
plus a typed accessor (`DesktopWindowEvent`) the watcher constructs
in memory before handing it to the existing `EventLogger`. The
JSONL shape lands inside `~/.recall/events/YYYY-MM-DD.jsonl`
alongside every other event kind; the engine reads it via the
shared `EventStore`.

Strict metadata-only contract:

  - ``app``           process executable name (e.g. ``code.exe``)
  - ``title``         the window title the OS exposed (the user's
                      own filename / tab name often appears here)
  - ``process``       the PID + parent PID, when the watcher can
                      resolve them (informational only)
  - ``focus_start``   ISO timestamp the focus began
  - ``focus_end``     ISO timestamp the focus ended
  - ``duration``      integer seconds (focus_end - focus_start)
  - ``switch_count``  how many times the focus left & came back
                      *within* this aggregation window
  - ``path``          file path if the OS exposed it through the
                      window title or accessibility API; **never
                      inferred**

No screenshots, no OCR, no audio, no pixel data — the trust
ledger contract restated at the data layer.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Dict, Optional


# The single event-kind string consumed by the rest of the engine.
KIND = "desktop_window"


@dataclass
class DesktopWindowEvent:
    """One captured focus block. Constructed by ``windows.py`` /
    ``sessions.py`` and serialised into a single JSONL line by the
    watcher's call to `EventLogger.log()`."""

    app: str
    title: str
    duration: int                          # seconds
    focus_start: str                       # ISO 8601 UTC
    focus_end: str                         # ISO 8601 UTC
    switch_count: int = 1
    path: Optional[str] = None
    process: Optional[Dict[str, Any]] = None

    def to_payload(self) -> Dict[str, Any]:
        """The exact `payload` dict the EventLogger writes. Keys
        match the JSONL contract documented in the module docstring
        + the schemas in `api/schemas.py:DesktopWindowIn`."""
        p: Dict[str, Any] = {
            "app": self.app,
            "title": self.title,
            "duration": int(self.duration),
            "focus_start": self.focus_start,
            "focus_end": self.focus_end,
            "switch_count": int(self.switch_count),
        }
        if self.path:
            p["path"] = self.path
        if self.process:
            # Strict whitelist — only the two fields the watcher
            # actually fills; defensive against future shape drift.
            p["process"] = {
                k: v for k, v in self.process.items()
                if k in ("pid", "ppid", "exe")
            }
        return p

    def to_json(self) -> str:
        return json.dumps(self.to_payload(), ensure_ascii=False)


def iso_now(*, when: Optional[datetime] = None) -> str:
    """Helper used by the watcher + tests."""
    if when is None:
        when = datetime.now(timezone.utc)
    return when.strftime("%Y-%m-%dT%H:%M:%SZ")


__all__ = [
    "KIND",
    "DesktopWindowEvent",
    "iso_now",
]
