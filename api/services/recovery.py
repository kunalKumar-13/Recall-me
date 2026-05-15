"""Recovery service — Phase 3B.

Thin facade over `app.core.recovery.RecoveryEngine`. Adds:

  • timing logs (the engine itself is silent),
  • a live `enabled` gate that mirrors `Config.recovery_enabled`,
  • candidate-by-id lookup for the one-click restore endpoint.

The service does not own data — every method reads from the event
store and reuses the threads + evolution builders. There is no
recovery cache on disk: a recovery candidate is the *current*
recoverable shape, not history. Caching would surface stale
"restore me" cards.
"""

from __future__ import annotations

import logging
import time
from typing import List, Optional

from app.core.events import EventStore
from app.core.evolution import EvolutionBuilder
from app.core.recovery import (
    RecoveryCandidate,
    RecoveryEngine,
    RestorationPlan,
)
from app.core.threads import ThreadBuilder

from ..logging_config import log_with
from .threads import ThreadsService

log = logging.getLogger("recall.api.recovery")


class RecoveryService:
    """Continuity-recovery facade.

    Composes on top of `ThreadsService` so the canonical-topic-key
    logic stays in one place. The threads + evolution caches are
    shared with the existing services — a recovery call shortly
    after a search or a thread fetch pays nothing extra for the
    upstream work.
    """

    def __init__(
        self,
        event_store: EventStore,
        threads_service: ThreadsService,
        builder: Optional[RecoveryEngine] = None,
        evolution_builder: Optional[EvolutionBuilder] = None,
        enabled: bool = True,
    ) -> None:
        self.event_store = event_store
        self.threads_service = threads_service
        if builder is None:
            # Reuse the threads service's underlying builders so
            # everything cooperates on the same in-memory caches.
            self.engine = RecoveryEngine(
                event_store,
                thread_builder=threads_service.builder,
                evolution_builder=evolution_builder,
            )
        else:
            self.engine = builder
        self.enabled = enabled

    # -- toggling --------------------------------------------------------

    def set_enabled(self, enabled: bool) -> None:
        """Honoured live; next `recent` call sees the new flag.
        When `False`, both endpoints behave as if the surface is
        empty — `recent` returns `[]`, `restore` 404s."""
        self.enabled = enabled

    # -- public ----------------------------------------------------------

    def recent(self, n: int = 3) -> tuple[List[RecoveryCandidate], float]:
        """Top-N recovery candidates, ranked by max(continuity,
        confidence). Returns `([], 0.0)` when disabled."""
        if not self.enabled:
            return [], 0.0
        t0 = time.perf_counter()
        candidates = self.engine.recover_recent(n=n)
        elapsed_ms = (time.perf_counter() - t0) * 1000
        log_with(
            log, logging.INFO, "recovery.recent",
            n_candidates=len(candidates),
            elapsed_ms=round(elapsed_ms, 2),
        )
        return candidates, elapsed_ms

    def get(self, candidate_id: str) -> Optional[RecoveryCandidate]:
        """Resolve one candidate by id for the restore endpoint.
        The engine doesn't index by id (candidates are derived);
        we resolve by re-scoring the candidate pool and matching."""
        if not self.enabled:
            return None
        candidates = self.engine.recover_recent(n=3)
        for c in candidates:
            if c.id == candidate_id:
                return c
        return None

    def plan(self, candidate_id: str) -> Optional[RestorationPlan]:
        """Resolve a candidate by id and return its orchestrated
        restoration plan (Phase 3C). Returns `None` when the id
        is unknown or the engine is disabled.

        Files → chats → tabs → searches, newest-first within
        each group. Each step carries a deterministic `reason`
        the debug overlay renders."""
        cand = self.get(candidate_id)
        if cand is None:
            return None
        return self.engine.plan_for(cand)
