"""Reconstruction service — sessions + micro-contexts.

Layered on top of the retrieval service:

  retrieval        → "which moments match this query?"
  reconstruction   → "what work blocks did those moments live inside?"

Two methods that mirror the Phase 1E / 1F entry points but
return pydantic-serializable payloads ready for HTTP.
"""

from __future__ import annotations

import logging
import time
from collections import defaultdict
from typing import List, Optional, Sequence

from app.core.episodic import EpisodicResult, EpisodicRetriever
from app.core.events import Event, EventStore
from app.core.microcontexts import MicroContext, MicroContextReconstructor
from app.core.sessions import (
    SESSION_KINDS,
    Session,
    SessionReconstructor,
    derive_label,
    derive_topic,
    format_time_range,
)

from ..logging_config import log_with

log = logging.getLogger("recall.api.reconstruction")


class ReconstructionService:
    """Wraps SessionReconstructor + MicroContextReconstructor.

    Provides three high-level operations:

      • `sessions_for_query`            — Phase 1E entry point.
      • `contexts_from_sessions`        — Phase 1F entry, filtered
                                          to contexts that contain at
                                          least one matched event.
      • `replay_day`                    — new: reconstruct everything
                                          from a single per-day file.
    """

    def __init__(
        self,
        event_store: EventStore,
        episodic_retriever: EpisodicRetriever,
        session_reconstructor: Optional[SessionReconstructor] = None,
        context_reconstructor: Optional[MicroContextReconstructor] = None,
    ) -> None:
        self.event_store = event_store
        self.episodic = episodic_retriever
        self.sessions = session_reconstructor or SessionReconstructor(
            event_store, episodic_retriever
        )
        self.contexts = context_reconstructor or MicroContextReconstructor()

    # -- query-driven reconstruction ------------------------------------

    def sessions_for_query(self, query: str, n: int = 2) -> List[Session]:
        t0 = time.perf_counter()
        sessions = self.sessions.reconstruct_for_query(query, n=n)
        log_with(
            log, logging.INFO, "sessions.reconstruct",
            query=query[:60], n_sessions=len(sessions),
            elapsed_ms=round((time.perf_counter() - t0) * 1000, 2),
        )
        return sessions

    def sessions_from_results(
        self, matching: Sequence[EpisodicResult], n: int = 2
    ) -> List[Session]:
        """Reconstruct sessions from an already-computed episodic
        result pool. `/v1/search` uses this to avoid scoring the log
        twice on a single request."""
        t0 = time.perf_counter()
        sessions = self.sessions.reconstruct_from_results(list(matching), n=n)
        log_with(
            log, logging.INFO, "sessions.reconstruct",
            n_matches=len(matching), n_sessions=len(sessions),
            elapsed_ms=round((time.perf_counter() - t0) * 1000, 2),
        )
        return sessions

    def contexts_from_sessions(
        self,
        sessions: Sequence[Session],
        episodic_results: Sequence[EpisodicResult],
        n: int = 2,
    ) -> List[MicroContext]:
        """Phase 1F: derive micro-contexts from candidate sessions,
        keep only those containing at least one of the
        episodic-matched events, rank by match count."""
        if not sessions:
            return []

        match_keys: set[tuple[str, str]] = {
            (r.session_id, (r.url or "").lower())
            for r in episodic_results
        }

        t0 = time.perf_counter()
        candidates: list[MicroContext] = []
        for sess in sessions:
            for ctx in self.contexts.reconstruct(sess.events):
                n_match = 0
                for ev in ctx.events:
                    key = (
                        ev.session_id,
                        (ev.payload.get("url") or "").lower(),
                    )
                    if key in match_keys:
                        n_match += 1
                if n_match > 0:
                    ctx.match_count = n_match
                    candidates.append(ctx)

        candidates.sort(
            key=lambda c: (c.match_count, c.event_count), reverse=True
        )
        log_with(
            log, logging.INFO, "contexts.reconstruct",
            n_sessions=len(sessions), n_contexts=len(candidates),
            elapsed_ms=round((time.perf_counter() - t0) * 1000, 2),
        )
        return candidates[:n]

    # -- recent (browse-style) reconstruction ---------------------------

    def recent_sessions(self, n: int = 5, days: int = 7) -> List[Session]:
        """Recent sessions without a query filter — built by walking
        the log, grouping by `session_id`, scoring each by recency
        + event count, returning top-N."""
        events_by_sid: dict[str, list[Event]] = defaultdict(list)
        for ev in self.event_store.iter_events(days=days):
            if ev.kind not in SESSION_KINDS:
                continue
            events_by_sid[ev.session_id].append(ev)

        scored: list[tuple[float, Session]] = []
        for sid, events in events_by_sid.items():
            if len(events) < 2:
                continue
            events.sort(key=lambda e: e.ts_epoch())
            topic = derive_topic(events)
            sess = Session(
                session_id=sid,
                events=events,
                matching_events=[],
                topic=topic,
                label=derive_label(events, topic),
                time_label=format_time_range(events),
                score=0.0,
            )
            # Recency score = newest event timestamp + size bonus.
            recency = max(e.ts_epoch() for e in events)
            scored.append((recency + 0.001 * len(events), sess))

        scored.sort(key=lambda kv: kv[0], reverse=True)
        return [s for _, s in scored[:n]]

    def recent_contexts(self, n: int = 5, days: int = 7) -> List[MicroContext]:
        """Recent micro-contexts. Built by reconstructing
        sessions, splitting each, and returning the top-N most
        recent."""
        sessions = self.recent_sessions(n=max(n, 5), days=days)
        out: list[tuple[float, MicroContext]] = []
        for sess in sessions:
            for ctx in self.contexts.reconstruct(sess.events):
                last_ts = max(ev.ts_epoch() for ev in ctx.events)
                out.append((last_ts, ctx))
        out.sort(key=lambda kv: kv[0], reverse=True)
        return [c for _, c in out[:n]]

    # -- replay ---------------------------------------------------------

    def replay_day(self, date_str: str) -> tuple[
        int, List[Session], List[MicroContext], float
    ]:
        """Reconstruct everything from a single per-day file.

        Returns `(event_count, sessions, contexts, elapsed_ms)`. An
        empty file yields zero events and empty lists; the endpoint
        wraps this in a typed response.
        """
        t0 = time.perf_counter()
        events = list(self.event_store.iter_events_for_date(date_str))
        events.sort(key=lambda e: e.ts_epoch())

        # Group by session_id (same logic as Phase 1E, but with no
        # query filter — every session that touched this day is
        # surfaced).
        events_by_sid: dict[str, list[Event]] = defaultdict(list)
        for ev in events:
            if ev.kind not in SESSION_KINDS:
                continue
            events_by_sid[ev.session_id].append(ev)

        sessions: list[Session] = []
        all_contexts: list[MicroContext] = []
        for sid, evs in events_by_sid.items():
            if len(evs) < 2:
                continue
            evs.sort(key=lambda e: e.ts_epoch())
            topic = derive_topic(evs)
            sess = Session(
                session_id=sid,
                events=evs,
                matching_events=[],
                topic=topic,
                label=derive_label(evs, topic),
                time_label=format_time_range(evs),
                score=0.0,
            )
            sessions.append(sess)
            all_contexts.extend(self.contexts.reconstruct(evs))

        # Order both lists newest-first for predictable rendering.
        sessions.sort(key=lambda s: max(e.ts_epoch() for e in s.events), reverse=True)
        all_contexts.sort(
            key=lambda c: max(e.ts_epoch() for e in c.events),
            reverse=True,
        )

        elapsed_ms = round((time.perf_counter() - t0) * 1000, 2)
        log_with(
            log, logging.INFO, "replay.day",
            date=date_str, n_events=len(events),
            n_sessions=len(sessions), n_contexts=len(all_contexts),
            elapsed_ms=elapsed_ms,
        )
        return len(events), sessions, all_contexts, elapsed_ms
