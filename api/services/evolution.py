"""Evolution service — Phase 3A.

Thin facade over `app.core.evolution.EvolutionBuilder`. Adds:

  • timing logs,
  • a live `enabled` gate that mirrors `Config.evolution_enabled`,
  • thread-id → Thread resolution via the threads service so the
    route handler only has to pass the id.

Evolutions are a *derived view* — the data lives in the event log
and the threads cache. The service writes only to the optional
`~/.recall/evolution.json` cache; deleting that file is always safe.
"""

from __future__ import annotations

import logging
import time
from typing import Optional

from app.core.evolution import (
    EvolutionBuilder,
    ThreadEvolution,
    ThreadEvolutionStore,
)
from app.core.events import EventStore
from app.core.threads import Thread

from ..logging_config import log_with
from .threads import ThreadsService

log = logging.getLogger("recall.api.evolution")


class EvolutionService:
    """Reconstructs one thread's evolution on demand.

    Owns the `EvolutionBuilder` and points it at the same
    `ThreadBuilder` the threads service already uses, so the
    canonical-topic-key lookup stays in one place.
    """

    def __init__(
        self,
        event_store: EventStore,
        threads_service: ThreadsService,
        builder: Optional[EvolutionBuilder] = None,
        enabled: bool = True,
    ) -> None:
        self.event_store = event_store
        self.threads_service = threads_service
        self.builder = builder or EvolutionBuilder(
            event_store,
            thread_builder=threads_service.builder,
        )
        self.enabled = enabled

    # -- toggling --------------------------------------------------------

    def set_enabled(self, enabled: bool) -> None:
        self.enabled = enabled

    # -- public ----------------------------------------------------------

    def for_thread(self, thread_id: str) -> Optional[ThreadEvolution]:
        """Build the evolution for one thread, by id.

        Returns `None` when the engine is disabled or the id isn't
        currently active — callers map that to 404. We don't fall
        back to the cache when the thread itself is gone: an
        evolution without its source thread would be a ghost.
        """
        if not self.enabled:
            return None

        t0 = time.perf_counter()

        # Rebuild the current thread set so we can resolve `thread_id`
        # → Thread. The threads service already pays the EventStore
        # parse cost, so this is roughly free.
        thread: Optional[Thread] = None
        threads = self.threads_service.builder.rebuild()
        for t in threads:
            if t.id == thread_id:
                thread = t
                break
        if thread is None:
            log_with(
                log, logging.INFO, "evolution.thread_not_found",
                thread_id=thread_id,
            )
            return None

        evo = self.builder.build(thread)
        elapsed_ms = (time.perf_counter() - t0) * 1000
        # The builder already recorded its own elapsed; we overwrite
        # with the total path time so the wire field reflects what
        # the user actually waited for.
        evo.elapsed_ms = round(elapsed_ms, 2)
        log_with(
            log, logging.INFO, "evolution.build",
            thread_id=thread_id,
            n_phases=len(evo.phases),
            elapsed_ms=evo.elapsed_ms,
        )
        return evo

    # -- cache --------------------------------------------------------

    def clear_cache(self) -> None:
        self.builder.store.clear()
        log_with(log, logging.INFO, "evolution.cache.cleared")

    @property
    def store(self) -> ThreadEvolutionStore:
        return self.builder.store
