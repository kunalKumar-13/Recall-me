"""Storage service — thin wrapper around the Phase 1A event log.

Owns the read path AND the write path. Higher-layer services
(ingestion, retrieval, reconstruction) call into this one rather
than touching `EventLogger` / `EventStore` directly, so the
durability + format guarantees live in exactly one place.
"""

from __future__ import annotations

import logging
from typing import Iterator, List, Optional

from app.core.events import Event, EventLogger, EventStore

log = logging.getLogger("recall.api.storage")


class StorageService:
    """Wraps an EventLogger (writes) + EventStore (reads).

    Single instances of each are passed in at construction. The
    launcher and the API service share the same EventLogger
    instance via dependency injection in `app/main.py`, so the
    launcher's own write path (logging its own queries / opens)
    continues to flow through the same lock + file handle as
    HTTP-posted events.
    """

    def __init__(
        self,
        event_logger: EventLogger,
        event_store: Optional[EventStore] = None,
    ) -> None:
        self.event_logger = event_logger
        # If no store is passed, default to one pointed at the
        # logger's base dir. Tests usually pass an explicit store
        # backed by a temp folder.
        self.event_store = event_store or EventStore(event_logger.base_dir)

    # -- writes ---------------------------------------------------------

    def write(self, kind: str, payload: dict) -> bool:
        """Append one event. Returns True if the logger accepted it.

        The logger is a no-op when episodic capture is disabled in
        Settings. Honored synchronously.
        """
        if not self.event_logger.enabled:
            return False
        self.event_logger.log(kind, payload)
        return True

    # -- reads ----------------------------------------------------------

    def iter_events(self, days: int = 14) -> Iterator[Event]:
        """Newest-first stream of events from the last `days` days."""
        return self.event_store.iter_events(days=days)

    def iter_events_for_date(self, date_str: str) -> Iterator[Event]:
        """Events for a specific YYYY-MM-DD UTC date.

        Used by the replay endpoint. Wraps the same JSONL reader
        as `iter_events` but scoped to a single day file.
        """
        return self.event_store.iter_events_for_date(date_str)

    def recent_queries(self, n: int = 5, days: int = 14) -> List[Event]:
        return self.event_store.recent_queries(n=n, days=days)

    def recent_browser_activity(self, n: int = 4, days: int = 7) -> List[Event]:
        return self.event_store.recent_browser_activity(n=n, days=days)

    # -- diagnostics ----------------------------------------------------

    def events_dir(self) -> str:
        return str(self.event_store.base_dir)

    def event_count_window(self, days: int = 14) -> int:
        """Cheap count of events in the recent window. Used by the
        health endpoint and structured-log lines."""
        n = 0
        for _ in self.event_store.iter_events(days=days):
            n += 1
        return n
