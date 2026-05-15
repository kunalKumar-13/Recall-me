"""Threads service — Phase 2C.

Thin facade over `app.core.threads.ThreadBuilder`. Adds:

  • timing logs (the engine itself is silent),
  • a live `enabled` gate that mirrors `Config.threads_enabled`,
  • detail reconstruction that fans the engine's primitives out
    through `SessionReconstructor` + `MicroContextReconstructor`
    (no rewriting; just composition).

Threads are a *cache* over the event log. The service never owns
data — every method either reads from the event store or writes
identity rows into the on-disk thread cache.
"""

from __future__ import annotations

import logging
import time
from collections import defaultdict
from typing import Iterable, List, Optional, Tuple

from app.core.episodic import EpisodicRetriever
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
from app.core.threads import Thread, ThreadBuilder, ThreadStore

from ..logging_config import log_with

log = logging.getLogger("recall.api.threads")


class ThreadsService:
    """Memory-threads facade.

    Keeps two pieces of state: the `ThreadBuilder` (read-only over
    events; reads/writes the identity cache) and an `enabled` flag
    that lets the desktop turn the feature off live without
    restarting uvicorn.
    """

    def __init__(
        self,
        event_store: EventStore,
        builder: Optional[ThreadBuilder] = None,
        episodic_retriever: Optional[EpisodicRetriever] = None,
        session_reconstructor: Optional[SessionReconstructor] = None,
        context_reconstructor: Optional[MicroContextReconstructor] = None,
        enabled: bool = True,
    ) -> None:
        self.event_store = event_store
        self.builder = builder or ThreadBuilder(event_store)
        self._episodic = episodic_retriever or EpisodicRetriever(event_store)
        self._sessions = session_reconstructor or SessionReconstructor(
            event_store, self._episodic
        )
        self._contexts = context_reconstructor or MicroContextReconstructor()
        self.enabled = enabled

    # -- toggling --------------------------------------------------------

    def set_enabled(self, enabled: bool) -> None:
        """Live toggle; next `recent` call sees the new flag."""
        self.enabled = enabled

    # -- recent ----------------------------------------------------------

    def recent(self, n: int = 6) -> tuple[List[Thread], float]:
        """Top-N currently-active threads, ranked by confidence.
        Returns `([], 0.0)` when disabled — no event-log scan."""
        if not self.enabled:
            return [], 0.0
        t0 = time.perf_counter()
        threads = self.builder.rebuild()
        elapsed_ms = (time.perf_counter() - t0) * 1000
        log_with(
            log, logging.INFO, "threads.rebuild",
            n_threads=len(threads),
            elapsed_ms=round(elapsed_ms, 2),
        )
        return threads[:n], elapsed_ms

    # -- detail (open-thread flow) ---------------------------------------

    def detail(
        self, thread_id: str
    ) -> Optional[tuple[Thread, List[Session], List[MicroContext], List[Event]]]:
        """Chronological reconstruction for one thread.

        Strategy:

          1. Rebuild the thread set (cheap; reuses the parse cache).
          2. Find the requested thread by id.
          3. Re-walk the event log, keep events whose canonical
             topic key matches the thread's topic_key.
          4. Reconstruct sessions + micro-contexts over that
             subset using the existing Phase 1E + 1F engines.

        Returns `None` when the id is unknown or the thread has
        dropped out of the active set."""
        # Rebuild without disabling — the user explicitly asked for
        # this thread, ignoring the enabled flag would be confusing.
        threads = self.builder.rebuild()
        target: Optional[Thread] = None
        for t in threads:
            if t.id == thread_id:
                target = t
                break
        if target is None:
            return None

        # Collect events that fall into this thread's bucket. We use
        # the same canonical-key derivation as the builder so the
        # set is consistent.
        topic_key = target.topic_key
        events: list[Event] = []
        for ev in self.event_store.iter_events(days=30):
            if self.builder._thread_key(ev) == topic_key:
                events.append(ev)
        events.sort(key=lambda e: e.ts_epoch())

        # Reconstruct sessions over the topic events. Group by
        # session_id, then run the same scoring/labelling helpers
        # the recent-sessions endpoint uses.
        events_by_sid: dict[str, list[Event]] = defaultdict(list)
        for ev in events:
            if ev.kind in SESSION_KINDS and ev.session_id:
                events_by_sid[ev.session_id].append(ev)

        sessions: list[Session] = []
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
        sessions.sort(
            key=lambda s: max(e.ts_epoch() for e in s.events),
            reverse=True,
        )

        # Micro-contexts: reconstruct over each session, keep the
        # ones that materially split the timeline.
        contexts: list[MicroContext] = []
        for sess in sessions:
            for ctx in self._contexts.reconstruct(sess.events):
                contexts.append(ctx)
        contexts.sort(
            key=lambda c: max(e.ts_epoch() for e in c.events),
            reverse=True,
        )

        log_with(
            log, logging.INFO, "threads.detail",
            thread_id=thread_id, n_events=len(events),
            n_sessions=len(sessions), n_contexts=len(contexts),
        )
        return target, sessions, contexts, events

    # -- forget / clear --------------------------------------------------

    def forget_thread(self, thread_id: str) -> bool:
        ok = self.builder.forget_thread(thread_id)
        log_with(
            log, logging.INFO, "threads.forget",
            thread_id=thread_id, ok=ok,
        )
        return ok

    def clear_cache(self) -> None:
        self.builder.clear()
        log_with(log, logging.INFO, "threads.cache.cleared")

    # -- handle accessors (mainly for tests / launcher) ------------------

    @property
    def store(self) -> ThreadStore:
        return self.builder.store
