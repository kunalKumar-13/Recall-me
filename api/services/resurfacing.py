"""Resurfacing service — Phase 2B.

Wraps `app.core.resurfacing.ResurfacingEngine` with HTTP-shaped
methods and timing. The engine itself is local-first and synchronous;
the service adds nothing but a logger and a thin
`enabled` gate so the API route never even runs the engine when the
user has the feature off.
"""

from __future__ import annotations

import logging
import time
from typing import List, Optional

from app.core.events import EventStore
from app.core.resurfacing import (
    ResurfacedContext,
    ResurfacingEngine,
    ResurfacingHistory,
)

from ..logging_config import log_with

log = logging.getLogger("recall.api.resurfacing")


class ResurfacingService:
    """Idle-digest resurfacing layer.

    `enabled` mirrors `Config.resurfacing_enabled` and is flipped live
    from Settings, exactly like the ingestion service's enabled flag.
    When `False`, `resurface_idle` returns an empty list without
    touching the engine — no event-log scan, no history file read.
    """

    def __init__(
        self,
        event_store: EventStore,
        engine: Optional[ResurfacingEngine] = None,
        enabled: bool = True,
    ) -> None:
        self.event_store = event_store
        self.engine = engine or ResurfacingEngine(event_store)
        self.enabled = enabled

    # -- toggling --------------------------------------------------------

    def set_enabled(self, enabled: bool) -> None:
        """Honoured synchronously. The next `resurface_idle` call sees
        the new flag."""
        self.enabled = enabled

    # -- public ----------------------------------------------------------

    def resurface_idle(self, n: int = 4) -> tuple[List[ResurfacedContext], float]:
        """Return the top-N resurfacing cards plus the engine's wall-
        clock elapsed time in milliseconds. When disabled the wall-
        clock cost is effectively zero and the list is empty."""
        if not self.enabled:
            return [], 0.0
        t0 = time.perf_counter()
        contexts = self.engine.resurface_idle(n=n)
        elapsed_ms = (time.perf_counter() - t0) * 1000
        log_with(
            log, logging.INFO, "resurface.idle",
            n_contexts=len(contexts),
            elapsed_ms=round(elapsed_ms, 2),
        )
        return contexts, elapsed_ms

    # -- history management ---------------------------------------------

    def clear_history(self) -> None:
        """Drop the surfacing-counter + mute file. Exposed via
        `POST /v1/resurface/history/clear` and the Settings button."""
        # Re-use the engine's history handle — both reads and writes
        # have to flow through the same object so the in-memory
        # cache stays consistent with disk.
        self.engine.history.clear()
        log_with(log, logging.INFO, "resurface.history.cleared")

    @property
    def history(self) -> ResurfacingHistory:
        return self.engine.history
