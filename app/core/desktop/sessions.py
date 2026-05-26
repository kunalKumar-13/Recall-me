"""Phase 6M — focus-session aggregator.

Turns a stream of per-tick foreground-window probes into
JSONL-ready ``desktop_window`` events. The aggregator owns three
rules:

  1. **Minimum focus duration.** Below the floor (default 30 s)
     the focus block is discarded — alt-tabs and notification
     pop-ups don't pollute the event log.
  2. **App-switch consolidation.** When the user toggles between
     the same window twice within a short re-focus window
     (``RE_FOCUS_WINDOW_S``), the two focus blocks merge into a
     single event with ``switch_count = 2`` rather than two
     short events with ``switch_count = 1``.
  3. **Blocklist.** The Recall launcher's own windows + the
     settings dialog never get logged (their titles match the
     ``BLOCKLIST_EXE`` prefix). This keeps the layer from
     observing itself.

The aggregator is **pure** — no I/O, no globals. The watcher
hands it probe results and reads back ``DesktopWindowEvent``s
when a focus block crosses the floor + a different window
becomes focused (or the watcher is asked to flush).
"""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Deque, List, Optional

from .events import DesktopWindowEvent, iso_now
from .windows import ForegroundWindow


# Defaults — tunable via the watcher's __init__ (or env vars in a
# future phase). The 30-second floor matches the alpha cohort's
# *return* threshold elsewhere in the product (PHASE_6F_STATUS).

MIN_FOCUS_S = 30
RE_FOCUS_WINDOW_S = 60

# Apps whose windows must never reach the JSONL log. Match by
# exe basename (case-insensitive prefix).
BLOCKLIST_EXE = (
    "recall.exe",       # the launcher binary itself
    "recall-launcher",  # dev-mode python wrapper
)


def _blocklisted(exe_name: Optional[str]) -> bool:
    if not exe_name:
        return False
    low = exe_name.lower()
    return any(low.startswith(p) for p in BLOCKLIST_EXE)


@dataclass
class _OpenBlock:
    """Aggregator's view of the currently-focused window."""

    key: str
    app: str
    title: str
    path: Optional[str]
    pid: int
    started_at: datetime
    last_seen_at: datetime
    switch_count: int = 1
    process: Optional[dict] = None


class FocusAggregator:
    """Owns the *currently-focused* block + a short ring buffer of
    recently-closed blocks (so a re-focus inside
    ``RE_FOCUS_WINDOW_S`` can merge instead of emitting two events).
    """

    def __init__(
        self,
        *,
        min_focus_s: int = MIN_FOCUS_S,
        re_focus_window_s: int = RE_FOCUS_WINDOW_S,
    ) -> None:
        self._min_focus_s = max(1, int(min_focus_s))
        self._re_focus_window_s = max(1, int(re_focus_window_s))
        self._open: Optional[_OpenBlock] = None
        # Recent finalised blocks for the merge-on-re-focus rule.
        self._recent: Deque[_OpenBlock] = deque(maxlen=8)

    # ── public API ──────────────────────────────────────────────

    def observe(
        self,
        fg: Optional[ForegroundWindow],
        *,
        now: Optional[datetime] = None,
    ) -> List[DesktopWindowEvent]:
        """Drop one probe in. Returns the list of events that
        crossed the *finished* threshold on this tick (typically
        empty; non-empty only when the focused window changes
        and the prior block was long enough to log)."""
        now = now or datetime.now(timezone.utc)
        events: List[DesktopWindowEvent] = []

        if fg is None or not fg.title:
            # No focused window (lock screen, screen off) — close
            # any open block.
            ev = self._close_current(now=now)
            if ev is not None:
                events.append(ev)
            return events

        if _blocklisted(fg.exe_name):
            # Treat Recall's own windows as "no focus" — keep any
            # in-progress block on the prior app rather than
            # closing it on every dialog flash.
            return events

        key = fg.stable_key

        # ── same window still focused ──
        if self._open is not None and self._open.key == key:
            self._open.last_seen_at = now
            return events

        # ── focus changed; finalise the prior block ──
        if self._open is not None:
            ev = self._finalise(self._open, now=now)
            if ev is not None:
                events.append(ev)
            self._open = None

        # ── start a new block (or merge into a recent one) ──
        merged = self._merge_into_recent(key, now=now)
        if merged is not None:
            self._open = merged
        else:
            self._open = _OpenBlock(
                key=key,
                app=fg.exe_name or "(unknown)",
                title=fg.title,
                path=_path_from_window(fg),
                pid=fg.pid,
                started_at=now,
                last_seen_at=now,
                switch_count=1,
                process={"pid": fg.pid, "exe": fg.exe_path},
            )
        return events

    def flush(self, *, now: Optional[datetime] = None) -> List[DesktopWindowEvent]:
        """Close the open block. Used by the watcher on shutdown."""
        now = now or datetime.now(timezone.utc)
        ev = self._close_current(now=now)
        return [ev] if ev else []

    # ── internals ───────────────────────────────────────────────

    def _close_current(self, *, now: datetime) -> Optional[DesktopWindowEvent]:
        if self._open is None:
            return None
        ev = self._finalise(self._open, now=now)
        self._open = None
        return ev

    def _finalise(
        self,
        block: _OpenBlock,
        *,
        now: datetime,
    ) -> Optional[DesktopWindowEvent]:
        duration = int((now - block.started_at).total_seconds())
        # Always stash in `_recent` so a quick re-focus can merge
        # in, regardless of whether we emit an event for this block.
        block.last_seen_at = now
        self._recent.append(block)
        if duration < self._min_focus_s:
            return None
        return DesktopWindowEvent(
            app=block.app,
            title=block.title,
            duration=duration,
            focus_start=iso_now(when=block.started_at),
            focus_end=iso_now(when=now),
            switch_count=block.switch_count,
            path=block.path,
            process=block.process,
        )

    def _merge_into_recent(
        self,
        key: str,
        *,
        now: datetime,
    ) -> Optional[_OpenBlock]:
        for prior in reversed(self._recent):
            if prior.key != key:
                continue
            gap = (now - prior.last_seen_at).total_seconds()
            if gap > self._re_focus_window_s:
                return None
            # Resurrect the prior block — keep its `started_at` so
            # the duration accumulates; bump the switch count.
            prior.last_seen_at = now
            prior.switch_count += 1
            try:
                self._recent.remove(prior)
            except ValueError:  # noqa: BLE001
                pass
            return prior
        return None


def _path_from_window(fg: ForegroundWindow) -> Optional[str]:
    """Best-effort path inference from the window title — *only*
    when the title looks like a real filesystem path.

    The rule: a token containing both a path separator + an
    extension counts as a path. We never construct a path from
    the EXE name, the process command line, or any other
    inference; the user's own window title is the only source.
    """
    title = fg.title or ""
    # Common pattern: "<filename> - <app>". VSCode / Cursor /
    # Notepad++ all use this shape.
    for sep in (" - ", " — ", " · "):
        if sep in title:
            head = title.split(sep, 1)[0].strip()
            if _looks_like_path(head):
                return head
    if _looks_like_path(title):
        return title
    return None


def _looks_like_path(s: str) -> bool:
    """Cheap heuristic. The watcher prefers *false negative* over
    *false positive* — a real path that we miss is fine; pulling
    a non-path string into the `path` field would be a trust-
    contract violation."""
    if not s or len(s) < 4 or " " in s and s.count("/") + s.count("\\") < 1:
        return False
    has_sep = "/" in s or "\\" in s
    has_ext = "." in s.rsplit("/", 1)[-1].rsplit("\\", 1)[-1]
    return has_sep and has_ext


__all__ = [
    "FocusAggregator",
    "MIN_FOCUS_S",
    "RE_FOCUS_WINDOW_S",
    "BLOCKLIST_EXE",
]
