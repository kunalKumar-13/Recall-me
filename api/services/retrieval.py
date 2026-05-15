"""Retrieval service — wraps the Phase 1C episodic retriever.

The episodic + file retrievers are stateless; one instance can
serve every request. File search (over the Chroma vector store)
is optional — when no `SearchEngine` is injected, the service
skips that layer entirely and the launcher falls back to its
own in-process engine.
"""

from __future__ import annotations

import logging
import time
from typing import List, Optional

from app.core.episodic import EpisodicResult, EpisodicRetriever
from app.core.events import EventStore

from ..logging_config import log_with

log = logging.getLogger("recall.api.retrieval")


class RetrievalService:
    """Episodic search + (optionally) file search.

    Reconstruction (sessions, micro-contexts) lives in a separate
    service — see `reconstruction.py`. Splitting them keeps each
    HTTP route's wiring narrow.
    """

    def __init__(
        self,
        event_store: EventStore,
        episodic_retriever: Optional[EpisodicRetriever] = None,
    ) -> None:
        self.event_store = event_store
        self.episodic = episodic_retriever or EpisodicRetriever(event_store)

    def episodic_search(self, query: str, n: int = 3) -> List[EpisodicResult]:
        t0 = time.perf_counter()
        results = self.episodic.search(query, n=n)
        elapsed_ms = (time.perf_counter() - t0) * 1000
        log_with(
            log, logging.INFO, "episodic.search",
            query=query[:60], n_results=len(results),
            elapsed_ms=round(elapsed_ms, 2),
        )
        return results

    def episodic_search_with_pool(
        self, query: str, n: int = 3, pool_size: int = 20
    ) -> tuple[List[EpisodicResult], List[EpisodicResult]]:
        """Run episodic search once but return both the top-N display
        slice and the wider session-reconstruction pool.

        `/v1/search` used to score the 10K-event log twice — once at
        n=3 (display) and once at n=20 (inside session reconstruction).
        Sharing the single scan halves the per-query cost.
        """
        t0 = time.perf_counter()
        pool = self.episodic.search(query, n=max(n, pool_size))
        elapsed_ms = (time.perf_counter() - t0) * 1000
        log_with(
            log, logging.INFO, "episodic.search",
            query=query[:60], n_results=len(pool),
            elapsed_ms=round(elapsed_ms, 2),
        )
        return pool[:n], pool
