"""Phase 6M — desktop foreground watcher.

A small background thread that:

  1. polls the OS for the foreground window every ``poll_interval`` s
     (default 2 s),
  2. feeds each probe into the `FocusAggregator`,
  3. when the aggregator finalises a focus block, writes one
     ``desktop_window`` event via the existing `EventLogger`
     (so the event lands in the same `~/.recall/events/YYYY-MM-DD.jsonl`
     file every other kind of event lands in).

The watcher is **off by default** on the engine side; the
application boot path decides whether to start it (the recall
launcher will call `start_watcher()` once the API service is up).
A future `recall doctor` check will surface its state.

Disable rules:

  - The watcher refuses to start on hosts without a probe
    (Windows via ``windows.py``, macOS via ``darwin.py``; a Linux
    sibling drops in next to them).
  - ``RECALL_DESKTOP=off`` in the environment makes start_watcher
    a no-op — the directive's *metadata only* contract gives the
    user a single env flag to silence the whole layer.
  - The `config.json` field ``desktop_capture_enabled`` (default
    ``False``) is the explicit opt-in. A consumer that turns the
    layer on without flipping the config also has to set the
    env flag — belt and braces.
"""

from __future__ import annotations

import logging
import os
import sys
import threading
from typing import Optional

from ..events import EventLogger
from . import darwin
from .events import KIND, DesktopWindowEvent
from .sessions import FocusAggregator
from .windows import is_supported as windows_is_supported
from .windows import probe_foreground as _probe_windows


log = logging.getLogger("recall.core.desktop.watcher")


DEFAULT_POLL_INTERVAL_S = 2.0


def _env_disabled() -> bool:
    """``RECALL_DESKTOP=off`` is the engine-wide kill switch."""
    return os.environ.get("RECALL_DESKTOP", "on").strip().lower() == "off"


def _platform_supported() -> bool:
    if sys.platform.startswith("win"):
        return windows_is_supported()
    if sys.platform == "darwin":
        return darwin.is_supported()
    return False


def probe_foreground():
    """Platform-dispatched foreground probe (Windows / macOS)."""
    if sys.platform == "darwin":
        return darwin.probe_foreground()
    return _probe_windows()


class DesktopWatcher:
    """Background watcher. Single-thread; stops cleanly on `stop()`.

    Construct with the *same* `EventLogger` the rest of the engine
    writes into so `desktop_window` events flow through the same
    on-disk format every other event uses.

    Usage::

        watcher = DesktopWatcher(event_logger=event_logger)
        watcher.start()
        # … application runs …
        watcher.stop()
    """

    def __init__(
        self,
        *,
        event_logger: EventLogger,
        poll_interval: float = DEFAULT_POLL_INTERVAL_S,
        aggregator: Optional[FocusAggregator] = None,
    ) -> None:
        self._event_logger = event_logger
        self._poll_interval = max(0.5, float(poll_interval))
        self._aggregator = aggregator or FocusAggregator()
        self._thread: Optional[threading.Thread] = None
        self._stop = threading.Event()
        self._supported = _platform_supported()

    # ── lifecycle ─────────────────────────────────────────────

    @property
    def is_running(self) -> bool:
        return self._thread is not None and self._thread.is_alive()

    @property
    def supported(self) -> bool:
        return self._supported

    def start(self) -> bool:
        """Start the watcher thread. Returns True if started,
        False if the platform is unsupported / disabled."""
        if _env_disabled():
            log.info("desktop watcher: RECALL_DESKTOP=off; not starting")
            return False
        if not self._supported:
            log.info("desktop watcher: platform unsupported; not starting")
            return False
        if self.is_running:
            return True
        self._stop.clear()
        self._thread = threading.Thread(
            target=self._run, name="recall-desktop", daemon=True,
        )
        self._thread.start()
        log.info("desktop watcher: started (interval=%.1fs)", self._poll_interval)
        return True

    def stop(self) -> None:
        if not self.is_running:
            return
        self._stop.set()
        if self._thread is not None:
            self._thread.join(timeout=2.0)
        # Flush any open block as a final event.
        try:
            for ev in self._aggregator.flush():
                self._emit(ev)
        except Exception:  # noqa: BLE001
            log.warning("desktop watcher: flush failed silently")
        self._thread = None
        log.info("desktop watcher: stopped")

    # ── loop ──────────────────────────────────────────────────

    def _run(self) -> None:
        while not self._stop.is_set():
            try:
                fg = probe_foreground()
                for ev in self._aggregator.observe(fg):
                    self._emit(ev)
            except Exception:  # noqa: BLE001
                # The watcher MUST NOT crash the host process. A
                # single tick that fails (window handle gone,
                # process died) is silent; the next tick retries.
                log.debug("desktop watcher: tick failed silently", exc_info=True)
            # Wait — interruptible by stop().
            self._stop.wait(timeout=self._poll_interval)

    # ── emit ──────────────────────────────────────────────────

    def _emit(self, event: DesktopWindowEvent) -> None:
        """Write one finalised focus block to the event log."""
        try:
            self._event_logger.log(KIND, event.to_payload())
        except Exception:  # noqa: BLE001
            log.warning("desktop watcher: event_logger.log failed silently")


# ── module-level convenience ─────────────────────────────────────


_singleton: Optional[DesktopWatcher] = None


def start_watcher(
    event_logger: EventLogger,
    *,
    poll_interval: float = DEFAULT_POLL_INTERVAL_S,
) -> Optional[DesktopWatcher]:
    """Application-boot helper. Creates (or reuses) the process-wide
    watcher singleton and starts it; returns the watcher or
    ``None`` if the platform is unsupported / RECALL_DESKTOP=off.

    The host (``app/main.py``) owns the lifetime — call
    ``stop_watcher()`` on shutdown."""
    global _singleton
    if _singleton is None:
        _singleton = DesktopWatcher(
            event_logger=event_logger, poll_interval=poll_interval,
        )
    if _singleton.start():
        return _singleton
    return None


def stop_watcher() -> None:
    global _singleton
    if _singleton is not None:
        _singleton.stop()
        _singleton = None


__all__ = [
    "DEFAULT_POLL_INTERVAL_S",
    "DesktopWatcher",
    "start_watcher",
    "stop_watcher",
]
