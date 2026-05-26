"""Recall local memory API — Phase 2A.

In-process FastAPI service. Bound to 127.0.0.1 only. No auth (the
loopback bind is the security boundary; remote callers physically
cannot reach the port).

Two ways to use this module:

  • `create_app(deps)` — pure factory. Used by tests to build the
    app in isolation, and by anyone who wants to host the routes
    under their own ASGI server.
  • `APIService(deps).start(port=4545)` — production path. Wraps
    uvicorn in a daemon thread so the desktop process can start
    and stop it from a Qt thread.
"""

from __future__ import annotations

import logging
import threading
import time
from dataclasses import dataclass
from typing import Iterable, Optional

import uvicorn
from fastapi import Depends, FastAPI, HTTPException, Query, status
from fastapi.concurrency import run_in_threadpool
from fastapi.middleware.cors import CORSMiddleware

from app.core import daily_loop, demo_mode
from app.core.events import Event, EventLogger, EventStore
from app.core.episodic import EpisodicResult, EpisodicRetriever
from app.core.evolution import EvolutionBuilder, EvolutionPhase
from app.core.microcontexts import MicroContext, MicroContextReconstructor
from app.core.recovery import RecoveryCandidate, RecoveryEngine
from app.core.resurfacing import ResurfacedContext, ResurfacingEngine
from app.core.sessions import Session, SessionReconstructor
from app.core.threads import Thread, ThreadBuilder

from .logging_config import log_with, setup_logging
from .schemas import (
    BrowserSearchIn,
    BrowserVisitIn,
    ChatSessionIn,
    DemoInvestigationOut,
    DemoPayloadOut,
    DemoRecoveryOut,
    DemoStateResponse,
    DemoTimelineEventOut,
    DemoTrustOut,
    LoopBumpRequest,
    LoopBumpResponse,
    LoopDayOut,
    LoopSignalsOut,
    LoopSummaryResponse,
    EpisodicResultOut,
    EventOut,
    EvolutionPhaseOut,
    DesktopWindowIn,
    FileOpenIn,
    HealthResponse,
    IngestResponse,
    LegacyEventIn,
    MicroContextOut,
    OpenableTarget,
    RecentContextsResponse,
    RecentEventsResponse,
    RecentQueriesResponse,
    RecentSessionsResponse,
    RecoveryCandidateOut,
    RecoveryRecentResponse,
    RecoveryRestoreResponse,
    ReplayDayIn,
    ReplayDayResponse,
    RestorationStepOut,
    ResurfaceHistoryClearResponse,
    ResurfaceIdleResponse,
    ResurfacedContextOut,
    SearchResponse,
    SessionOut,
    ThreadDetailResponse,
    ThreadEvolutionResponse,
    ThreadForgetResponse,
    ThreadOut,
    ThreadsClearResponse,
    ThreadsRecentResponse,
)
from .services import (
    EvolutionService,
    IngestionService,
    ReconstructionService,
    RecoveryService,
    ResurfacingService,
    RetrievalService,
    StorageService,
    ThreadsService,
)

log = logging.getLogger("recall.api.app")


# --------------------------------------------------------------- DTOs


@dataclass
class AppDeps:
    """Everything the API needs to function, hung off one struct
    so route handlers can pull individual services via `Depends`."""

    event_logger: EventLogger
    event_store: EventStore
    storage: StorageService
    ingestion: IngestionService
    retrieval: RetrievalService
    reconstruction: ReconstructionService
    resurfacing: ResurfacingService
    threads: ThreadsService
    evolution: EvolutionService
    recovery: RecoveryService


def _event_to_out(ev: Event) -> EventOut:
    payload = ev.payload or {}
    return EventOut(
        ts=ev.ts,
        session_id=ev.session_id,
        kind=ev.kind,
        title=(payload.get("title") or payload.get("query") or "")[:500],
        url=(payload.get("url") or "")[:2048],
        domain=(payload.get("domain") or "")[:240],
        payload=payload,
    )


def _episodic_to_out(r: EpisodicResult) -> EpisodicResultOut:
    return EpisodicResultOut(
        kind=r.kind,
        title=r.title,
        subtitle=r.subtitle,
        url=r.url,
        ts_epoch=r.ts_epoch,
        score=r.score,
        session_id=r.session_id,
    )


# The launcher only renders the first handful of openable targets in
# a session card; nobody wants to "reopen" 200 tabs. Capping keeps the
# HTTP response small (a 10K-event session would otherwise serialize a
# 500 KB JSON payload of duplicate URLs).
_MAX_OPENABLE_TARGETS = 32


def _session_to_out(s: Session) -> SessionOut:
    return SessionOut(
        session_id=s.session_id,
        topic=s.topic,
        label=s.label,
        time_label=s.time_label,
        score=s.score,
        event_count=s.event_count,
        kinds=s.kinds,
        preview_events=[_event_to_out(ev) for ev in s.preview_events()],
        openable_targets=[
            OpenableTarget(kind=k, target=t)
            for k, t in s.openable_targets()[:_MAX_OPENABLE_TARGETS]
        ],
    )


def _context_to_out(c: MicroContext) -> MicroContextOut:
    return MicroContextOut(
        topic=c.topic,
        label=c.label,
        time_label=c.time_label,
        event_count=c.event_count,
        kinds=c.kinds,
        match_count=c.match_count,
        preview_events=[_event_to_out(ev) for ev in c.preview_events()],
        openable_targets=[
            OpenableTarget(kind=k, target=t)
            for k, t in c.openable_targets()[:_MAX_OPENABLE_TARGETS]
        ],
    )


def _recovery_to_out(c: RecoveryCandidate) -> RecoveryCandidateOut:
    """Project a `RecoveryCandidate` onto its HTTP shape. The
    suggested targets keep their order (newest-touched first); the
    launcher iterates this list to open everything in one click.

    Phase 3C ships three additional fields on the wire:
    `preview_caption`, `last_phase_title`, `last_phase_transition`.
    The launcher renders the caption directly under the title; the
    phase fields power debug-mode overlays."""
    return RecoveryCandidateOut(
        id=c.id,
        thread_id=c.thread_id,
        title=c.title,
        last_active_at=c.last_active_at,
        continuity_score=c.continuity_score,
        recovery_confidence=c.recovery_confidence,
        representative_events=[_event_to_out(ev) for ev in c.representative_events],
        suggested_targets=[
            OpenableTarget(kind=k, target=t)
            for k, t in c.suggested_targets[:_MAX_OPENABLE_TARGETS]
        ],
        related_sessions=list(c.related_sessions),
        related_contexts=c.related_contexts,
        unresolved_signals=list(c.unresolved_signals),
        signals=dict(c.signals),
        why=list(c.why),
        preview_caption=c.preview_caption,
        last_phase_title=c.last_phase_title,
        last_phase_transition=c.last_phase_transition,
    )


def _phase_to_out(p: EvolutionPhase) -> EvolutionPhaseOut:
    """Project an `EvolutionPhase` onto its HTTP shape. Representative
    targets fold into the same `OpenableTarget` envelope every other
    surface uses so the launcher's existing open handlers apply."""
    return EvolutionPhaseOut(
        id=p.id,
        thread_id=p.thread_id,
        title=p.title,
        start_at=p.start_at,
        end_at=p.end_at,
        event_count=p.event_count,
        dominant_surface=p.dominant_surface,
        representative_queries=list(p.representative_queries),
        representative_targets=[
            OpenableTarget(kind=k, target=t)
            for k, t in p.representative_targets[:_MAX_OPENABLE_TARGETS]
        ],
        momentum_score=p.momentum_score,
        revisit_score=p.revisit_score,
        transition=p.transition,
        signals=dict(p.signals),
        why=list(p.why),
    )


def _thread_to_out(t: Thread) -> ThreadOut:
    """Project a `Thread` onto its HTTP shape. Representative
    targets fold into the same `OpenableTarget` envelope every other
    retrieval surface uses, so the launcher can open thread targets
    with the same handler as session / context / resurfacing targets."""
    return ThreadOut(
        id=t.id,
        topic_key=t.topic_key,
        title=t.title,
        confidence=t.confidence,
        created_at=t.created_at,
        updated_at=t.updated_at,
        event_count=t.event_count,
        session_count=t.session_count,
        surface_types=list(t.surface_types),
        representative_queries=list(t.representative_queries),
        representative_targets=[
            OpenableTarget(kind=k, target=tgt)
            for k, tgt in t.representative_targets
        ],
        timeline_summary=t.timeline_summary,
        signals=dict(t.signals),
        why=list(t.why),
    )


def _demo_payload_out() -> DemoPayloadOut:
    """Project the in-memory demo fixture (`demo_mode.demo_payload`)
    onto its HTTP shape. Pure data transform; no scoring, no
    engine read."""
    raw = demo_mode.demo_payload()
    return DemoPayloadOut(
        recovery=DemoRecoveryOut(**raw["recovery"]),
        investigations=[DemoInvestigationOut(**i) for i in raw["investigations"]],
        timeline=[DemoTimelineEventOut(**t) for t in raw["timeline"]],
        trust=DemoTrustOut(**raw["trust"]),
        generated_at=raw["generated_at"],
    )


def _demo_state_response() -> DemoStateResponse:
    """Build the response body for /v1/demo/state. Payload is
    attached only when the overlay is currently active so
    consumers don't accidentally render demo content."""
    current = demo_mode.state()
    return DemoStateResponse(
        state=current,
        payload=_demo_payload_out() if current == "active" else None,
    )


def _resurfaced_to_out(r: ResurfacedContext) -> ResurfacedContextOut:
    """Project a `ResurfacedContext` onto its HTTP shape. Mirrors the
    session/micro-context transformer so the launcher's existing
    preview/openable rendering applies unchanged."""
    return ResurfacedContextOut(
        topic=r.topic,
        label=r.label,
        time_label=r.time_label,
        score=r.score,
        confidence=r.confidence,
        event_count=r.event_count,
        kinds=r.kinds,
        preview_events=[_event_to_out(ev) for ev in r.preview_events()],
        openable_targets=[
            OpenableTarget(kind=k, target=t)
            for k, t in r.openable_targets[:_MAX_OPENABLE_TARGETS]
        ],
        why=list(r.why),
        signals=dict(r.signals),
    )


# --------------------------------------------------------------- factory


def create_app(deps: AppDeps) -> FastAPI:
    """Build the FastAPI app from a hydrated dependency struct.

    Imports of FastAPI/Pydantic are eager; the cost of constructing
    the app is dominated by route registration (~50 ms total).
    """
    setup_logging()

    app = FastAPI(
        title="Recall — local memory API",
        description=(
            "Recall's local-only memory layer. All endpoints serve "
            "from 127.0.0.1 — none are reachable from the network. "
            "No auth: the loopback bind is the boundary."
        ),
        version="2A",
        docs_url="/docs-api",
        redoc_url=None,
        openapi_url="/openapi.json",
    )

    # Permissive CORS — the bind is the boundary, so this is just
    # browser-extension ergonomics, not an attack surface.
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=False,
        allow_methods=["GET", "POST", "OPTIONS"],
        allow_headers=["*"],
    )

    # Pin deps to the app for `Depends()` access without globals.
    app.state.deps = deps

    def get_deps() -> AppDeps:
        return app.state.deps

    # ----------- ingestion routes (POST /v1/events/*) ------------------
    #
    # Every ingest path calls this after a successful write so the
    # demo overlay fades when real activity arrives. The hook is a
    # JSON-file flip; no engine touch.
    #
    # Phase 6F: the same hook also feeds the daily-loop return
    # detector so a return-after-gap is counted on the *first* event
    # after the gap, not on the next launcher open.

    def _post_ingest_hook(ok: bool) -> None:
        if not ok:
            return
        demo_mode.mark_real_activity()
        # Best-effort — never propagate a daily-loop persistence
        # failure into the ingest response.
        try:
            daily_loop.mark_event(time.time())
        except Exception:  # noqa: BLE001
            log.warning("daily_loop: mark_event failed silently")


    @app.post(
        "/v1/events/browser",
        response_model=IngestResponse,
        tags=["ingestion"],
        summary="Ingest a browser page visit.",
    )
    async def ingest_browser(
        ev: BrowserVisitIn, deps: AppDeps = Depends(get_deps)
    ) -> IngestResponse:
        ok, reason = await run_in_threadpool(
            deps.ingestion.ingest_typed, "browser_visit", ev.model_dump()
        )
        _post_ingest_hook(ok)
        return IngestResponse(
            received=1, ingested=1 if ok else 0, reason=reason,
        )

    @app.post(
        "/v1/events/search",
        response_model=IngestResponse,
        tags=["ingestion"],
        summary="Ingest a search-engine query.",
    )
    async def ingest_search(
        ev: BrowserSearchIn, deps: AppDeps = Depends(get_deps)
    ) -> IngestResponse:
        ok, reason = await run_in_threadpool(
            deps.ingestion.ingest_typed, "browser_search", ev.model_dump()
        )
        _post_ingest_hook(ok)
        return IngestResponse(
            received=1, ingested=1 if ok else 0, reason=reason,
        )

    @app.post(
        "/v1/events/chat",
        response_model=IngestResponse,
        tags=["ingestion"],
        summary="Ingest a chat-platform session (ChatGPT / Claude / etc).",
    )
    async def ingest_chat(
        ev: ChatSessionIn, deps: AppDeps = Depends(get_deps)
    ) -> IngestResponse:
        ok, reason = await run_in_threadpool(
            deps.ingestion.ingest_typed, "chat_session", ev.model_dump()
        )
        _post_ingest_hook(ok)
        return IngestResponse(
            received=1, ingested=1 if ok else 0, reason=reason,
        )

    @app.post(
        "/v1/events/open",
        response_model=IngestResponse,
        tags=["ingestion"],
        summary="Ingest a file-open (or reveal-in-Finder) event.",
    )
    async def ingest_open(
        ev: FileOpenIn, deps: AppDeps = Depends(get_deps)
    ) -> IngestResponse:
        kind = "reveal" if ev.reveal else "open"
        ok, reason = await run_in_threadpool(
            deps.ingestion.ingest_typed,
            kind,
            ev.model_dump(exclude={"reveal"}),
        )
        _post_ingest_hook(ok)
        return IngestResponse(
            received=1, ingested=1 if ok else 0, reason=reason,
        )

    @app.post(
        "/v1/events/desktop",
        response_model=IngestResponse,
        tags=["ingestion"],
        summary=(
            "Phase 6M — ingest a `desktop_window` focus event. "
            "Metadata only (app, title, duration, switch_count, "
            "optional path/process). No screenshots, no OCR, no "
            "pixel data; the schema rejects any other field."
        ),
    )
    async def ingest_desktop(
        ev: DesktopWindowIn, deps: AppDeps = Depends(get_deps)
    ) -> IngestResponse:
        ok, reason = await run_in_threadpool(
            deps.ingestion.ingest_typed, "desktop_window", ev.model_dump(),
        )
        _post_ingest_hook(ok)
        return IngestResponse(
            received=1, ingested=1 if ok else 0, reason=reason,
        )

    # Legacy compat: pre-2A extension posts `{kind, payload}` to a
    # single `/events` route. Forward to the right /v1/ endpoint.
    @app.post(
        "/events",
        response_model=IngestResponse,
        tags=["ingestion"],
        summary="Legacy generic ingest endpoint. Prefer /v1/events/*.",
    )
    async def ingest_legacy(
        ev: LegacyEventIn, deps: AppDeps = Depends(get_deps)
    ) -> IngestResponse:
        ok, reason = await run_in_threadpool(
            deps.ingestion.ingest_typed, ev.kind, ev.payload
        )
        _post_ingest_hook(ok)
        return IngestResponse(
            received=1, ingested=1 if ok else 0, reason=reason,
        )

    # ----------- retrieval routes (GET /v1/search etc.) ----------------

    @app.get(
        "/v1/search",
        response_model=SearchResponse,
        tags=["retrieval"],
        summary="Episodic + session + micro-context search for a query.",
    )
    async def search(
        q: str = Query(..., min_length=1, description="User query string."),
        n_episodic: int = Query(default=3, ge=0, le=20),
        n_sessions: int = Query(default=2, ge=0, le=10),
        n_contexts: int = Query(default=2, ge=0, le=10),
        deps: AppDeps = Depends(get_deps),
    ) -> SearchResponse:
        t0 = time.perf_counter()
        episodic, pool = await run_in_threadpool(
            deps.retrieval.episodic_search_with_pool, q, n_episodic, 20
        )
        sessions = await run_in_threadpool(
            deps.reconstruction.sessions_from_results, pool, n_sessions
        )
        contexts = await run_in_threadpool(
            deps.reconstruction.contexts_from_sessions,
            sessions, pool, n_contexts,
        )
        elapsed_ms = round((time.perf_counter() - t0) * 1000, 2)
        log_with(
            log, logging.INFO, "search",
            query=q[:60], elapsed_ms=elapsed_ms,
            n_episodic=len(episodic), n_sessions=len(sessions),
            n_contexts=len(contexts),
        )
        return SearchResponse(
            query=q,
            episodic=[_episodic_to_out(r) for r in episodic],
            sessions=[_session_to_out(s) for s in sessions],
            contexts=[_context_to_out(c) for c in contexts],
            elapsed_ms=elapsed_ms,
        )

    @app.get(
        "/v1/sessions/recent",
        response_model=RecentSessionsResponse,
        tags=["retrieval"],
        summary="Reconstruct recent sessions without a query filter.",
    )
    async def recent_sessions(
        days: int = Query(default=7, ge=1, le=90),
        n: int = Query(default=5, ge=1, le=20),
        deps: AppDeps = Depends(get_deps),
    ) -> RecentSessionsResponse:
        sessions = await run_in_threadpool(
            deps.reconstruction.recent_sessions, n, days
        )
        return RecentSessionsResponse(
            sessions=[_session_to_out(s) for s in sessions]
        )

    @app.get(
        "/v1/contexts/recent",
        response_model=RecentContextsResponse,
        tags=["retrieval"],
        summary="Reconstruct recent micro-contexts without a query filter.",
    )
    async def recent_contexts(
        days: int = Query(default=7, ge=1, le=90),
        n: int = Query(default=5, ge=1, le=20),
        deps: AppDeps = Depends(get_deps),
    ) -> RecentContextsResponse:
        contexts = await run_in_threadpool(
            deps.reconstruction.recent_contexts, n, days
        )
        return RecentContextsResponse(
            contexts=[_context_to_out(c) for c in contexts]
        )

    # Bonus — surfaces the launcher's idle-digest sources behind the
    # same API so the launcher can stop touching the event store
    # directly. Not in the original brief but matches the pattern.
    @app.get(
        "/v1/events/recent",
        response_model=RecentEventsResponse,
        tags=["retrieval"],
        summary="Flat newest-first stream of recent events, optionally filtered by kind.",
    )
    async def recent_events(
        kinds: Optional[str] = Query(
            default=None,
            description="Comma-separated kind whitelist. Empty = all kinds.",
        ),
        days: int = Query(default=14, ge=1, le=90),
        n: int = Query(default=20, ge=1, le=200),
        deps: AppDeps = Depends(get_deps),
    ) -> RecentEventsResponse:
        allowed = (
            {k.strip() for k in kinds.split(",") if k.strip()}
            if kinds else None
        )

        def _walk() -> list[Event]:
            out: list[Event] = []
            for ev in deps.storage.iter_events(days=days):
                if allowed is not None and ev.kind not in allowed:
                    continue
                out.append(ev)
                if len(out) >= n:
                    break
            return out

        events = await run_in_threadpool(_walk)
        return RecentEventsResponse(events=[_event_to_out(e) for e in events])

    @app.get(
        "/v1/queries/recent",
        response_model=RecentQueriesResponse,
        tags=["retrieval"],
        summary="Distinct recent launcher queries — for the digest's 'Lately you searched'.",
    )
    async def recent_queries(
        days: int = Query(default=14, ge=1, le=90),
        n: int = Query(default=5, ge=1, le=20),
        deps: AppDeps = Depends(get_deps),
    ) -> RecentQueriesResponse:
        queries = await run_in_threadpool(
            deps.storage.recent_queries, n, days
        )
        return RecentQueriesResponse(
            queries=[_event_to_out(e) for e in queries]
        )

    # ----------- replay -----------------------------------------------

    @app.post(
        "/v1/replay/day",
        response_model=ReplayDayResponse,
        tags=["replay"],
        summary="Reconstruct sessions + micro-contexts for a single per-day log file.",
    )
    async def replay_day(
        body: ReplayDayIn, deps: AppDeps = Depends(get_deps)
    ) -> ReplayDayResponse:
        n_events, sessions, contexts, elapsed_ms = await run_in_threadpool(
            deps.reconstruction.replay_day, body.date
        )
        return ReplayDayResponse(
            date=body.date,
            event_count=n_events,
            sessions=[_session_to_out(s) for s in sessions],
            contexts=[_context_to_out(c) for c in contexts],
            elapsed_ms=elapsed_ms,
        )

    # ----------- resurfacing (Phase 2B) -------------------------------

    @app.get(
        "/v1/resurface/idle",
        response_model=ResurfaceIdleResponse,
        tags=["resurfacing"],
        summary=(
            "Top-N 'continue where you left off' cards. Empty list "
            "when the engine is disabled or has nothing surfaceable."
        ),
    )
    async def resurface_idle(
        n: int = Query(default=4, ge=0, le=4),
        deps: AppDeps = Depends(get_deps),
    ) -> ResurfaceIdleResponse:
        contexts, elapsed_ms = await run_in_threadpool(
            deps.resurfacing.resurface_idle, n
        )
        return ResurfaceIdleResponse(
            contexts=[_resurfaced_to_out(c) for c in contexts],
            enabled=deps.resurfacing.enabled,
            elapsed_ms=round(elapsed_ms, 2),
        )

    @app.post(
        "/v1/resurface/history/clear",
        response_model=ResurfaceHistoryClearResponse,
        tags=["resurfacing"],
        summary=(
            "Drop the resurfacing surfacing-counter + mute file. "
            "Powers the Settings 'Clear resurfacing history' button."
        ),
    )
    async def resurface_clear_history(
        deps: AppDeps = Depends(get_deps),
    ) -> ResurfaceHistoryClearResponse:
        await run_in_threadpool(deps.resurfacing.clear_history)
        return ResurfaceHistoryClearResponse(cleared=True)

    # ----------- threads (Phase 2C) -----------------------------------

    @app.get(
        "/v1/threads/recent",
        response_model=ThreadsRecentResponse,
        tags=["threads"],
        summary=(
            "Top-N active memory threads, ranked by confidence. "
            "Empty list when the feature is disabled or no topic "
            "clears the confidence floor."
        ),
    )
    async def threads_recent(
        n: int = Query(default=6, ge=0, le=20),
        deps: AppDeps = Depends(get_deps),
    ) -> ThreadsRecentResponse:
        threads, elapsed_ms = await run_in_threadpool(
            deps.threads.recent, n
        )
        return ThreadsRecentResponse(
            threads=[_thread_to_out(t) for t in threads],
            elapsed_ms=round(elapsed_ms, 2),
        )

    @app.get(
        "/v1/threads/{thread_id}",
        response_model=ThreadDetailResponse,
        tags=["threads"],
        summary=(
            "Full chronological reconstruction for one thread: the "
            "thread itself, its sessions, micro-contexts, and a flat "
            "event list."
        ),
    )
    async def thread_detail(
        thread_id: str,
        deps: AppDeps = Depends(get_deps),
    ) -> ThreadDetailResponse:
        result = await run_in_threadpool(deps.threads.detail, thread_id)
        if result is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"thread not found: {thread_id}",
            )
        thread, sessions, contexts, events = result
        return ThreadDetailResponse(
            thread=_thread_to_out(thread),
            sessions=[_session_to_out(s) for s in sessions],
            contexts=[_context_to_out(c) for c in contexts],
            events=[_event_to_out(e) for e in events],
        )

    @app.get(
        "/v1/threads/{thread_id}/evolution",
        response_model=ThreadEvolutionResponse,
        tags=["threads"],
        summary=(
            "Chronological phases for one thread (Phase 3A). Each "
            "phase carries momentum + revisit scores and a "
            "transition label; the launcher renders them as a "
            "horizontal strip when a thread is opened."
        ),
    )
    async def thread_evolution(
        thread_id: str,
        deps: AppDeps = Depends(get_deps),
    ) -> ThreadEvolutionResponse:
        evo = await run_in_threadpool(deps.evolution.for_thread, thread_id)
        if evo is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"thread not found or evolution disabled: {thread_id}",
            )
        return ThreadEvolutionResponse(
            thread_id=evo.thread_id,
            phases=[_phase_to_out(p) for p in evo.phases],
            span_start=evo.span_start,
            span_end=evo.span_end,
            elapsed_ms=evo.elapsed_ms,
        )

    @app.post(
        "/v1/threads/{thread_id}/forget",
        response_model=ThreadForgetResponse,
        tags=["threads"],
        summary=(
            "Drop one thread from the local cache. Its events stay; "
            "the next rebuild may re-derive a new id if the topic "
            "remains active."
        ),
    )
    async def thread_forget(
        thread_id: str,
        deps: AppDeps = Depends(get_deps),
    ) -> ThreadForgetResponse:
        ok = await run_in_threadpool(deps.threads.forget_thread, thread_id)
        return ThreadForgetResponse(forgotten=ok, thread_id=thread_id)

    @app.post(
        "/v1/threads/cache/clear",
        response_model=ThreadsClearResponse,
        tags=["threads"],
        summary=(
            "Drop the entire thread cache at ~/.recall/threads.json. "
            "Subsequent rebuilds re-derive ids from current events."
        ),
    )
    async def threads_clear_cache(
        deps: AppDeps = Depends(get_deps),
    ) -> ThreadsClearResponse:
        await run_in_threadpool(deps.threads.clear_cache)
        return ThreadsClearResponse(cleared=True)

    @app.post(
        "/v1/threads/evolution/clear",
        response_model=ThreadsClearResponse,
        tags=["threads"],
        summary=(
            "Drop the evolution cache at ~/.recall/evolution.json. "
            "Phases are recomputed from events on the next call."
        ),
    )
    async def threads_clear_evolution_cache(
        deps: AppDeps = Depends(get_deps),
    ) -> ThreadsClearResponse:
        await run_in_threadpool(deps.evolution.clear_cache)
        return ThreadsClearResponse(cleared=True)

    # ----------- recovery (Phase 3B) ----------------------------------

    @app.get(
        "/v1/recovery/recent",
        response_model=RecoveryRecentResponse,
        tags=["recovery"],
        summary=(
            "Top-N continuity-recovery candidates. Capped at 3 by "
            "the engine; the response is the launcher's primary "
            "idle-state surface ('Continue where you left off')."
        ),
    )
    async def recovery_recent(
        n: int = Query(default=3, ge=0, le=3),
        deps: AppDeps = Depends(get_deps),
    ) -> RecoveryRecentResponse:
        candidates, elapsed_ms = await run_in_threadpool(
            deps.recovery.recent, n
        )
        # Phase 6F — count *non-empty* recovery surfaces. An empty
        # response is correct silence, not a shown card; surface
        # silence is tracked at the alpha-ledger level, not in the
        # daily-loop counters.
        if candidates:
            try:
                daily_loop.record_recovery_shown()
            except Exception:  # noqa: BLE001
                log.warning("daily_loop: shown bump failed silently")
        return RecoveryRecentResponse(
            candidates=[_recovery_to_out(c) for c in candidates],
            elapsed_ms=round(elapsed_ms, 2),
        )

    @app.post(
        "/v1/recovery/{candidate_id}/restore",
        response_model=RecoveryRestoreResponse,
        tags=["recovery"],
        summary=(
            "Resolve one candidate by id and return its orchestrated "
            "restoration plan: files first, then chats, then tabs by "
            "domain, then repeated searches. The launcher executes "
            "the sequence; the endpoint itself does not open anything."
        ),
    )
    async def recovery_restore(
        candidate_id: str,
        deps: AppDeps = Depends(get_deps),
    ) -> RecoveryRestoreResponse:
        plan = await run_in_threadpool(deps.recovery.plan, candidate_id)
        if plan is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"recovery candidate not found: {candidate_id}",
            )
        # Phase 6F — a successful plan means the user clicked Resume
        # and the engine produced a restoration. Bump
        # `recoveries_used`; the `resume_success` bin is the deferred
        # signal that fires only when the launcher's executor reports
        # back that the targets actually opened.
        try:
            daily_loop.record_recovery_used()
        except Exception:  # noqa: BLE001
            log.warning("daily_loop: used bump failed silently")
        steps_out = [
            RestorationStepOut(
                kind=s.kind, target=s.target,
                group=s.group, reason=s.reason,
            )
            for s in plan.steps[:_MAX_OPENABLE_TARGETS]
        ]
        return RecoveryRestoreResponse(
            id=plan.candidate_id,
            thread_id=plan.thread_id,
            title=plan.title,
            preview_caption=plan.preview_caption,
            steps=steps_out,
            # Mirror the steps as a flat `suggested_targets` list so
            # Phase-3B clients that haven't updated keep working.
            suggested_targets=[
                OpenableTarget(kind=s.kind, target=s.target)
                for s in plan.steps[:_MAX_OPENABLE_TARGETS]
            ],
        )

    # ----------- demo overlay (Phase 6D) ------------------------------
    #
    # Three tiny routes for the first-run demo experience. The state
    # is owned by `app.core.demo_mode`, persisted at
    # `~/.recall/demo.json`. The engine itself never reads this state
    # — the launcher + extension consult these endpoints and overlay
    # the demo payload on top of the empty engine surface.

    @app.get(
        "/v1/demo/state",
        response_model=DemoStateResponse,
        tags=["demo"],
        summary=(
            "Current demo overlay state. `payload` is non-null only when "
            "`state == 'active'`, so consumers can render the demo "
            "directly off this single endpoint."
        ),
    )
    async def demo_state() -> DemoStateResponse:
        return _demo_state_response()

    @app.post(
        "/v1/demo/activate",
        response_model=DemoStateResponse,
        tags=["demo"],
        summary=(
            "User clicked Show example. Flip the overlay on and "
            "return the fresh state + payload."
        ),
    )
    async def demo_activate() -> DemoStateResponse:
        await run_in_threadpool(demo_mode.activate)
        return _demo_state_response()

    @app.post(
        "/v1/demo/dismiss",
        response_model=DemoStateResponse,
        tags=["demo"],
        summary=(
            "User clicked Dismiss on the demo banner. Flip the "
            "overlay off without altering any engine state."
        ),
    )
    async def demo_dismiss() -> DemoStateResponse:
        await run_in_threadpool(demo_mode.dismiss)
        return _demo_state_response()

    # ----------- daily loop (Phase 6F) --------------------------------
    #
    # Six counters about Recall's own surfaces (not user content).
    # Counts only — never URLs / filenames / queries / titles. See
    # `app.core.daily_loop` for the data model + storage.

    _BUMPER = {
        "day_started": daily_loop.record_day_started,
        "investigations_opened": daily_loop.record_investigation_opened,
        "recoveries_shown": daily_loop.record_recovery_shown,
        "recoveries_used": daily_loop.record_recovery_used,
        "returns": lambda: daily_loop.record_return(
            gap_seconds=daily_loop.RETURN_GAP_MIN_SECONDS
        ),
        "resume_success": daily_loop.record_resume_success,
    }

    def _today_count(bin_name: str) -> int:
        s = daily_loop.summary(days=1)
        return int(s["today"].get(bin_name, 0))

    @app.post(
        "/v1/loop/bump",
        response_model=LoopBumpResponse,
        tags=["loop"],
        summary=(
            "Bump one daily-loop counter. Body is `{bin: <name>}`. "
            "Six named bins; anything else is rejected by pydantic."
        ),
    )
    async def loop_bump(body: LoopBumpRequest) -> LoopBumpResponse:
        await run_in_threadpool(_BUMPER[body.bin])
        return LoopBumpResponse(bin=body.bin, today=_today_count(body.bin))

    @app.get(
        "/v1/loop/summary",
        response_model=LoopSummaryResponse,
        tags=["loop"],
        summary=(
            "Today / yesterday / 7-day counter summary + the three "
            "derived signals (continuity_restored, return_rate, "
            "resume_quality) with green/yellow/red verdicts."
        ),
    )
    async def loop_summary(
        days: int = Query(default=7, ge=1, le=90),
    ) -> LoopSummaryResponse:
        s = await run_in_threadpool(daily_loop.summary, days=days)
        return LoopSummaryResponse(
            today=LoopDayOut(**s["today"]),
            yesterday=LoopDayOut(**s["yesterday"]),
            window=LoopDayOut(date="window", **s["window"]),
            window_days=s["window_days"],
            days_with_any_activity=s["days_with_any_activity"],
            signals=LoopSignalsOut(**s["signals"]),
            green_yellow_red=s["green_yellow_red"],
        )

    # ----------- health -----------------------------------------------

    @app.get(
        "/v1/health",
        response_model=HealthResponse,
        tags=["misc"],
        summary="Liveness + counters. Cheap; suitable for the extension's popup polling.",
    )
    async def health(deps: AppDeps = Depends(get_deps)) -> HealthResponse:
        return HealthResponse(
            status="ok",
            enabled=deps.ingestion.enabled,
            ingested_total=deps.ingestion.ingested_total,
            dropped_total=deps.ingestion.dropped_total,
            events_dir=deps.storage.events_dir(),
        )

    # Legacy `/health` (pre-2A path used by the existing extension).
    @app.get("/health", response_model=HealthResponse, tags=["misc"])
    async def health_legacy(deps: AppDeps = Depends(get_deps)) -> HealthResponse:
        return await health(deps)  # type: ignore[arg-type]

    return app


# --------------------------------------------------------------- service


class APIService:
    """Hosts the FastAPI app inside the desktop process via uvicorn.

    Exposes the same surface as the pre-2A `IngestServer` so
    `app/ui/settings.py` doesn't need to know which implementation
    is mounted:

      • `start(port=...)` / `stop()`
      • `is_running`, `port`
      • `enabled` (mirrors ingestion.enabled)
      • `set_enabled(bool)` / `set_excluded_domains(list)`
      • `excluded_domains`, `ingested_total`, `dropped_total`
    """

    def __init__(
        self,
        event_logger: EventLogger,
        event_store: Optional[EventStore] = None,
        port: int = 4545,
        excluded_domains: Optional[Iterable[str]] = None,
        enabled: bool = True,
        episodic_retriever: Optional[EpisodicRetriever] = None,
        session_reconstructor: Optional[SessionReconstructor] = None,
        context_reconstructor: Optional[MicroContextReconstructor] = None,
        resurfacing_enabled: bool = True,
        resurfacing_engine: Optional[ResurfacingEngine] = None,
        threads_enabled: bool = True,
        thread_builder: Optional[ThreadBuilder] = None,
        evolution_enabled: bool = True,
        evolution_builder: Optional[EvolutionBuilder] = None,
        recovery_enabled: bool = True,
        recovery_engine: Optional[RecoveryEngine] = None,
    ) -> None:
        self.port = port
        self._server: Optional[uvicorn.Server] = None
        self._thread: Optional[threading.Thread] = None

        store = event_store or EventStore(event_logger.base_dir)
        storage = StorageService(event_logger, store)
        ingestion = IngestionService(
            storage,
            excluded_domains=excluded_domains,
            enabled=enabled,
        )
        episodic = episodic_retriever or EpisodicRetriever(store)
        retrieval = RetrievalService(store, episodic)
        reconstruction = ReconstructionService(
            store, episodic,
            session_reconstructor=session_reconstructor,
            context_reconstructor=context_reconstructor,
        )
        # Phase 2B: passive resurfacing. The engine reads from the same
        # EventStore the retrieval pipeline uses, so it benefits from
        # the per-file parse cache without any extra wiring.
        resurfacing = ResurfacingService(
            store,
            engine=resurfacing_engine,
            enabled=resurfacing_enabled,
        )
        # Phase 2C: memory threads. Composes on top of events +
        # sessions + contexts; persists identity at
        # ~/.recall/threads.json so threads strengthen across
        # rebuilds.
        threads = ThreadsService(
            store,
            builder=thread_builder,
            episodic_retriever=episodic,
            session_reconstructor=session_reconstructor,
            context_reconstructor=context_reconstructor,
            enabled=threads_enabled,
        )
        # Phase 3A: thread evolution. Reuses the threads service's
        # ThreadBuilder for canonical-topic-key lookups, so the
        # bucketing logic stays in one place.
        evolution = EvolutionService(
            store,
            threads_service=threads,
            builder=evolution_builder,
            enabled=evolution_enabled,
        )
        # Phase 3B: continuity recovery. Composes on top of threads +
        # evolution; shares both builders so the upstream parse caches
        # are paid once across the whole stack.
        recovery = RecoveryService(
            store,
            threads_service=threads,
            builder=recovery_engine,
            evolution_builder=evolution.builder,
            enabled=recovery_enabled,
        )

        self.deps = AppDeps(
            event_logger=event_logger,
            event_store=store,
            storage=storage,
            ingestion=ingestion,
            retrieval=retrieval,
            reconstruction=reconstruction,
            resurfacing=resurfacing,
            threads=threads,
            evolution=evolution,
            recovery=recovery,
        )
        self.app = create_app(self.deps)

    # -- IngestServer-compatible surface --------------------------------

    @property
    def enabled(self) -> bool:
        return self.deps.ingestion.enabled

    @property
    def ingested_total(self) -> int:
        return self.deps.ingestion.ingested_total

    @property
    def dropped_total(self) -> int:
        return self.deps.ingestion.dropped_total

    @property
    def is_running(self) -> bool:
        return self._server is not None

    @property
    def excluded_domains(self) -> list[str]:
        return self.deps.ingestion.excluded_domains

    def set_enabled(self, enabled: bool) -> None:
        self.deps.ingestion.set_enabled(enabled)

    def set_excluded_domains(self, domains: Iterable[str]) -> None:
        self.deps.ingestion.set_excluded_domains(domains)

    # -- Phase 2B resurfacing surface ----------------------------------

    @property
    def resurfacing_enabled(self) -> bool:
        return self.deps.resurfacing.enabled

    def set_resurfacing_enabled(self, enabled: bool) -> None:
        """Toggle the resurfacing feature live; matches the
        Settings dialog's checkbox without touching disk."""
        self.deps.resurfacing.set_enabled(enabled)

    def clear_resurfacing_history(self) -> None:
        """Drop `~/.recall/resurfacing.json` (surfacing counters + the
        muted-topic list). Used by the Settings dialog's "Clear
        resurfacing history" button."""
        self.deps.resurfacing.clear_history()

    # -- Phase 2C threads surface --------------------------------------

    @property
    def threads_enabled(self) -> bool:
        return self.deps.threads.enabled

    def set_threads_enabled(self, enabled: bool) -> None:
        """Toggle the thread engine live; matches the Settings
        checkbox without touching disk."""
        self.deps.threads.set_enabled(enabled)

    def clear_threads_cache(self) -> None:
        """Drop `~/.recall/threads.json` (identity store). The next
        rebuild re-derives ids from current events."""
        self.deps.threads.clear_cache()

    # -- Phase 3A evolution surface ------------------------------------

    @property
    def evolution_enabled(self) -> bool:
        return self.deps.evolution.enabled

    def set_evolution_enabled(self, enabled: bool) -> None:
        """Toggle the evolution engine live. When False,
        `/v1/threads/{id}/evolution` returns 404 without scanning
        the event log."""
        self.deps.evolution.set_enabled(enabled)

    def clear_evolution_cache(self) -> None:
        """Drop `~/.recall/evolution.json` (per-thread chronology
        cache). Phases are recomputed from events on the next call."""
        self.deps.evolution.clear_cache()

    # -- Phase 3B recovery surface -------------------------------------

    @property
    def recovery_enabled(self) -> bool:
        return self.deps.recovery.enabled

    def set_recovery_enabled(self, enabled: bool) -> None:
        """Live toggle. When False, /v1/recovery/recent returns []
        and /v1/recovery/{id}/restore returns 404."""
        self.deps.recovery.set_enabled(enabled)

    # -- lifecycle -----------------------------------------------------

    def start(self) -> bool:
        if self._server is not None:
            return True
        log_with(
            log, logging.INFO, "api.service.start",
            port=self.port, events_dir=self.deps.storage.events_dir(),
        )
        config = uvicorn.Config(
            self.app,
            host="127.0.0.1",
            port=self.port,
            log_level="warning",
            access_log=False,
            # Use the default asyncio loop — the desktop process is
            # not async, so don't pull in uvloop on Windows.
            loop="asyncio",
        )
        server = uvicorn.Server(config)

        # Suppress uvicorn's own signal handlers so the desktop's
        # Qt application can manage them.
        server.install_signal_handlers = lambda: None  # type: ignore[method-assign]

        self._server = server
        self._thread = threading.Thread(
            target=server.run, name="recall-api", daemon=True
        )
        self._thread.start()

        # Wait up to 2 s for uvicorn to mark itself ready. The
        # boot log shows whether we hit the timeout.
        deadline = time.monotonic() + 2.0
        while time.monotonic() < deadline:
            if getattr(server, "started", False):
                return True
            time.sleep(0.02)
        log_with(
            log, logging.WARNING, "api.service.slow_start",
            port=self.port,
        )
        return True  # thread is up; readiness can still take a tick

    def stop(self) -> None:
        if self._server is not None:
            try:
                self._server.should_exit = True
            except Exception:
                pass
            self._server = None
        self._thread = None
        log_with(log, logging.INFO, "api.service.stop", port=self.port)
