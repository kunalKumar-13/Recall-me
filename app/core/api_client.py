"""Thin HTTP client that turns the local API into Python objects.

Used by the launcher worker so retrieval flows through the API
service rather than touching `app.core.events` / `episodic` /
`sessions` / `microcontexts` directly. Adds maybe 5-10 ms over
in-process calls on localhost — well inside the 100 ms budget
for the full retrieval pass.

Uses only stdlib (`urllib`, `json`) — no new wheels for the
launcher to ship.
"""

from __future__ import annotations

import json
import logging
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from typing import List, Optional, Tuple

from .episodic import EpisodicResult
from .events import Event
from .evolution import EvolutionPhase, ThreadEvolution
from .microcontexts import MicroContext
from .recovery import RecoveryCandidate, RestorationPlan, RestorationStep
from .resurfacing import ResurfacedContext
from .sessions import Session
from .threads import Thread

log = logging.getLogger("recall.api.client")


@dataclass
class SearchResponse:
    """Local mirror of `api.schemas.SearchResponse`. Kept here so
    the launcher imports nothing from the `api` package — that
    package depends on FastAPI/pydantic which we don't want to
    pull into the Qt event loop's import graph."""

    query: str
    episodic: List[EpisodicResult]
    sessions: List[Session]
    contexts: List[MicroContext]
    elapsed_ms: float


class APIClient:
    """Synchronous HTTP client. Safe to call from a Qt worker thread.

    Every method has a `timeout` that caps the call at 2 seconds —
    a healthy local daemon answers in under 100 ms; anything over
    2 s is either a hung process or a port collision, and the
    launcher would rather show empty results than block typing.
    """

    def __init__(self, base_url: str = "http://127.0.0.1:4545") -> None:
        self.base_url = base_url.rstrip("/")
        self._opener = urllib.request.build_opener()

    # -- search -----------------------------------------------------------

    def search(
        self,
        query: str,
        n_episodic: int = 3,
        n_sessions: int = 2,
        n_contexts: int = 2,
        timeout: float = 2.0,
    ) -> Optional[SearchResponse]:
        """Run the full retrieval pipeline. Returns `None` on any
        transport failure — callers treat that as "API down, show
        empty results, don't crash"."""
        params = {
            "q": query,
            "n_episodic": n_episodic,
            "n_sessions": n_sessions,
            "n_contexts": n_contexts,
        }
        data = self._get_json("/v1/search", params, timeout=timeout)
        if data is None:
            return None

        return SearchResponse(
            query=data.get("query", query),
            episodic=[_episodic_from(d) for d in data.get("episodic", [])],
            sessions=[_session_from(d) for d in data.get("sessions", [])],
            contexts=[_context_from(d) for d in data.get("contexts", [])],
            elapsed_ms=float(data.get("elapsed_ms", 0.0)),
        )

    # -- digest data (idle launcher) -------------------------------------

    def recent_queries(self, n: int = 4, days: int = 14, timeout: float = 2.0) -> List[Event]:
        data = self._get_json(
            "/v1/queries/recent",
            {"n": n, "days": days},
            timeout=timeout,
        )
        if data is None:
            return []
        return [_event_from(d) for d in data.get("queries", [])]

    def recent_browser_activity(
        self, n: int = 4, days: int = 7, timeout: float = 2.0
    ) -> List[Event]:
        """Returns the last N browser-side events for the launcher
        digest's 'Recent digital activity' strip."""
        data = self._get_json(
            "/v1/events/recent",
            {
                "n": n,
                "days": days,
                "kinds": "browser_visit,browser_search,chat_session",
            },
            timeout=timeout,
        )
        if data is None:
            return []
        return [_event_from(d) for d in data.get("events", [])]

    # -- resurfacing (Phase 2B) ------------------------------------------

    def resurface_idle(
        self, n: int = 4, timeout: float = 2.0
    ) -> List[ResurfacedContext]:
        """Top-N "continue where you left off" cards. Empty list when
        the engine is disabled, the API is down, or no topic clears
        the score floor — the launcher hides the section in any of
        those cases."""
        data = self._get_json(
            "/v1/resurface/idle",
            {"n": n},
            timeout=timeout,
        )
        if data is None:
            return []
        return [
            _resurfaced_from(d) for d in data.get("contexts", [])
        ]

    def clear_resurfacing_history(self, timeout: float = 2.0) -> bool:
        """Powers the Settings 'Clear resurfacing history' button."""
        data = self._post_json(
            "/v1/resurface/history/clear", {}, timeout=timeout
        )
        return bool(data and data.get("cleared"))

    # -- threads (Phase 2C) ---------------------------------------------

    def threads_recent(
        self, n: int = 6, timeout: float = 2.0
    ) -> List[Thread]:
        """Top-N active memory threads, ranked by confidence. Returns
        `[]` when the engine is disabled or the API is down — the
        launcher hides the digest section in either case."""
        data = self._get_json(
            "/v1/threads/recent", {"n": n}, timeout=timeout
        )
        if data is None:
            return []
        return [_thread_from(d) for d in data.get("threads", [])]

    def clear_threads_cache(self, timeout: float = 2.0) -> bool:
        data = self._post_json(
            "/v1/threads/cache/clear", {}, timeout=timeout
        )
        return bool(data and data.get("cleared"))

    # -- evolution (Phase 3A) -------------------------------------------

    def thread_evolution(
        self, thread_id: str, timeout: float = 2.0
    ) -> Optional[ThreadEvolution]:
        """Top-N chronological phases for one thread. Returns
        `None` when the API is down or the thread id is unknown —
        the launcher hides the evolution strip in either case
        rather than render a half-empty surface."""
        if not thread_id:
            return None
        data = self._get_json(
            f"/v1/threads/{thread_id}/evolution", {}, timeout=timeout
        )
        if data is None:
            return None
        return _evolution_from(data)

    def clear_evolution_cache(self, timeout: float = 2.0) -> bool:
        data = self._post_json(
            "/v1/threads/evolution/clear", {}, timeout=timeout
        )
        return bool(data and data.get("cleared"))

    # -- recovery (Phase 3B) --------------------------------------------

    def recovery_recent(
        self, n: int = 3, timeout: float = 2.0
    ) -> List[RecoveryCandidate]:
        """Top-N continuity-recovery candidates. Returns `[]` when
        the API is down, the engine is disabled, or no thread
        clears the recovery-confidence floor."""
        data = self._get_json(
            "/v1/recovery/recent", {"n": n}, timeout=timeout
        )
        if data is None:
            return []
        return [_recovery_from(d) for d in data.get("candidates", [])]

    def recovery_restore(
        self, candidate_id: str, timeout: float = 2.0
    ) -> Optional[RestorationPlan]:
        """Resolve a candidate by id and return its orchestrated
        restoration plan (Phase 3C). The caller iterates
        `plan.steps` and hands each step's `target` to the OS.

        Returns `None` when the id is unknown, the engine is
        disabled, or the API is down — the launcher treats all
        three the same way (flash "Nothing to restore", do
        nothing else)."""
        if not candidate_id:
            return None
        data = self._post_json(
            f"/v1/recovery/{candidate_id}/restore", {}, timeout=timeout
        )
        if data is None:
            return None
        steps = [
            RestorationStep(
                kind=s.get("kind", ""),
                target=s.get("target", ""),
                group=s.get("group", ""),
                reason=s.get("reason", ""),
            )
            for s in data.get("steps", [])
        ]
        return RestorationPlan(
            candidate_id=data.get("id", candidate_id),
            thread_id=data.get("thread_id", ""),
            title=data.get("title", ""),
            preview_caption=data.get("preview_caption", ""),
            steps=steps,
        )

    # -- health ----------------------------------------------------------

    def health(self, timeout: float = 1.0) -> Optional[dict]:
        return self._get_json("/v1/health", {}, timeout=timeout)

    # -- ingestion (used by tests / scripts; the launcher writes
    #    directly via EventLogger for latency reasons) ------------------

    def post_browser_visit(self, payload: dict, timeout: float = 2.0) -> Optional[dict]:
        return self._post_json("/v1/events/browser", payload, timeout=timeout)

    def post_browser_search(self, payload: dict, timeout: float = 2.0) -> Optional[dict]:
        return self._post_json("/v1/events/search", payload, timeout=timeout)

    def post_chat_session(self, payload: dict, timeout: float = 2.0) -> Optional[dict]:
        return self._post_json("/v1/events/chat", payload, timeout=timeout)

    def post_open(self, payload: dict, timeout: float = 2.0) -> Optional[dict]:
        return self._post_json("/v1/events/open", payload, timeout=timeout)

    # -- internal --------------------------------------------------------

    def _get_json(
        self, path: str, params: dict, timeout: float
    ) -> Optional[dict]:
        url = self.base_url + path
        if params:
            url += "?" + urllib.parse.urlencode(params)
        return self._call(url, method="GET", body=None, timeout=timeout)

    def _post_json(
        self, path: str, payload: dict, timeout: float
    ) -> Optional[dict]:
        url = self.base_url + path
        body = json.dumps(payload).encode("utf-8")
        return self._call(url, method="POST", body=body, timeout=timeout)

    def _call(
        self,
        url: str,
        method: str,
        body: Optional[bytes],
        timeout: float,
    ) -> Optional[dict]:
        try:
            headers = {"Accept": "application/json"}
            if body is not None:
                headers["Content-Type"] = "application/json"
            req = urllib.request.Request(
                url, data=body, headers=headers, method=method
            )
            with self._opener.open(req, timeout=timeout) as r:
                raw = r.read()
            return json.loads(raw.decode("utf-8"))
        except urllib.error.URLError:
            # Daemon down, port in use elsewhere, etc.
            return None
        except (json.JSONDecodeError, UnicodeDecodeError):
            return None
        except Exception:
            # Defensive — the launcher never crashes on a bad
            # API response.
            return None


# --------------------------------------------------------------- decoders


def _event_from(d: dict) -> Event:
    return Event(
        ts=d.get("ts", ""),
        session_id=d.get("session_id", ""),
        kind=d.get("kind", ""),
        payload=d.get("payload") or {},
    )


def _episodic_from(d: dict) -> EpisodicResult:
    return EpisodicResult(
        kind=d.get("kind", ""),
        title=d.get("title", ""),
        subtitle=d.get("subtitle", ""),
        url=d.get("url", ""),
        ts_epoch=float(d.get("ts_epoch") or 0.0),
        score=float(d.get("score") or 0.0),
        session_id=d.get("session_id", ""),
        payload={},
    )


def _session_from(d: dict) -> Session:
    events = [_event_from(e) for e in d.get("preview_events", [])]
    s = Session(
        session_id=d.get("session_id", ""),
        events=events,
        matching_events=[],
        topic=d.get("topic", ""),
        label=d.get("label", ""),
        time_label=d.get("time_label", ""),
        score=float(d.get("score") or 0.0),
    )
    # Cache the openable targets so `Session.openable_targets()`
    # returns the same list the server computed, without recomputing
    # from the truncated preview events.
    raw_targets = [
        (t.get("kind", ""), t.get("target", ""))
        for t in d.get("openable_targets", [])
    ]
    s._cached_openable_targets = raw_targets  # type: ignore[attr-defined]

    def _openable_targets():  # type: ignore[no-redef]
        return list(raw_targets)

    s.openable_targets = _openable_targets  # type: ignore[assignment]
    return s


def _context_from(d: dict) -> MicroContext:
    events = [_event_from(e) for e in d.get("preview_events", [])]
    c = MicroContext(
        events=events,
        topic=d.get("topic", ""),
        label=d.get("label", ""),
        time_label=d.get("time_label", ""),
        match_count=int(d.get("match_count") or 0),
    )
    raw_targets = [
        (t.get("kind", ""), t.get("target", ""))
        for t in d.get("openable_targets", [])
    ]
    c._cached_openable_targets = raw_targets  # type: ignore[attr-defined]

    def _openable_targets():  # type: ignore[no-redef]
        return list(raw_targets)

    c.openable_targets = _openable_targets  # type: ignore[assignment]
    return c


def _recovery_from(d: dict) -> RecoveryCandidate:
    """Decode a `RecoveryCandidateOut` payload back into the engine
    dataclass. Representative events round-trip through the same
    `_event_from` decoder the rest of the client uses."""
    raw_targets = [
        (t.get("kind", ""), t.get("target", ""))
        for t in d.get("suggested_targets", [])
    ]
    return RecoveryCandidate(
        id=d.get("id", ""),
        thread_id=d.get("thread_id", ""),
        title=d.get("title", ""),
        last_active_at=float(d.get("last_active_at") or 0.0),
        continuity_score=float(d.get("continuity_score") or 0.0),
        recovery_confidence=float(d.get("recovery_confidence") or 0.0),
        representative_events=[
            _event_from(e) for e in d.get("representative_events", [])
        ],
        suggested_targets=raw_targets,
        related_sessions=list(d.get("related_sessions") or []),
        related_contexts=int(d.get("related_contexts") or 0),
        unresolved_signals=list(d.get("unresolved_signals") or []),
        signals=dict(d.get("signals") or {}),
        why=list(d.get("why") or []),
        # Phase 3C —
        preview_caption=d.get("preview_caption", ""),
        last_phase_title=d.get("last_phase_title", ""),
        last_phase_transition=d.get("last_phase_transition", ""),
    )


def _phase_from(d: dict) -> EvolutionPhase:
    """Decode one `EvolutionPhaseOut` row back into the engine
    dataclass."""
    raw_targets = [
        (t.get("kind", ""), t.get("target", ""))
        for t in d.get("representative_targets", [])
    ]
    return EvolutionPhase(
        id=d.get("id", ""),
        thread_id=d.get("thread_id", ""),
        title=d.get("title", ""),
        start_at=float(d.get("start_at") or 0.0),
        end_at=float(d.get("end_at") or 0.0),
        event_count=int(d.get("event_count") or 0),
        dominant_surface=d.get("dominant_surface", ""),
        representative_queries=list(d.get("representative_queries") or []),
        representative_targets=raw_targets,
        momentum_score=float(d.get("momentum_score") or 0.0),
        revisit_score=float(d.get("revisit_score") or 0.0),
        transition=d.get("transition", "initial"),
        signals=dict(d.get("signals") or {}),
        why=list(d.get("why") or []),
    )


def _evolution_from(d: dict) -> ThreadEvolution:
    """Decode a `ThreadEvolutionResponse` payload."""
    return ThreadEvolution(
        thread_id=d.get("thread_id", ""),
        phases=[_phase_from(p) for p in d.get("phases", [])],
        span_start=float(d.get("span_start") or 0.0),
        span_end=float(d.get("span_end") or 0.0),
        elapsed_ms=float(d.get("elapsed_ms") or 0.0),
    )


def _thread_from(d: dict) -> Thread:
    """Decode a `ThreadOut` payload back into the engine dataclass.
    Representative targets are flattened from `{kind, target}` rows
    back into `(kind, target)` tuples to match the dataclass."""
    raw_targets = [
        (t.get("kind", ""), t.get("target", ""))
        for t in d.get("representative_targets", [])
    ]
    return Thread(
        id=d.get("id", ""),
        topic_key=d.get("topic_key", ""),
        title=d.get("title", ""),
        confidence=float(d.get("confidence") or 0.0),
        created_at=float(d.get("created_at") or 0.0),
        updated_at=float(d.get("updated_at") or 0.0),
        event_count=int(d.get("event_count") or 0),
        session_count=int(d.get("session_count") or 0),
        surface_types=list(d.get("surface_types") or []),
        representative_queries=list(d.get("representative_queries") or []),
        representative_targets=raw_targets,
        timeline_summary=d.get("timeline_summary", ""),
        signals=dict(d.get("signals") or {}),
        why=list(d.get("why") or []),
    )


def _resurfaced_from(d: dict) -> ResurfacedContext:
    """Decode a `ResurfacedContextOut` payload back into the engine's
    dataclass. The server already truncated openable_targets, so the
    client keeps the list verbatim."""
    events = [_event_from(e) for e in d.get("preview_events", [])]
    raw_targets = [
        (t.get("kind", ""), t.get("target", ""))
        for t in d.get("openable_targets", [])
    ]
    return ResurfacedContext(
        topic=d.get("topic", ""),
        label=d.get("label", ""),
        time_label=d.get("time_label", ""),
        score=float(d.get("score") or 0.0),
        confidence=float(d.get("confidence") or 0.0),
        why=list(d.get("why") or []),
        events=events,
        openable_targets=raw_targets,
        signals=dict(d.get("signals") or {}),
    )
