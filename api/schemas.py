"""Pydantic models for every public surface of the local API.

Two design rules:

  • Inputs are *narrow*. Every request schema declares the exact
    fields its kind needs and forbids extras. A misbehaving client
    can't push arbitrary metadata into the event log.
  • Outputs are *stable*. Response shapes are versioned implicitly
    by the `/v1/` namespace and have been pinned to the field names
    the launcher already renders, so a client written against this
    schema today keeps working as the internals evolve.
"""

from __future__ import annotations

from typing import List, Literal, Optional

from pydantic import BaseModel, ConfigDict, Field

# --------------------------------------------------------------- ingestion


class _StrictModel(BaseModel):
    """Reject unknown payload fields. The HTTP allowlist already
    drops them; the strict model is belt-and-braces in case a
    client posts via the legacy `/events` shim that doesn't go
    through the same filter."""

    model_config = ConfigDict(extra="ignore")


class BrowserVisitIn(_StrictModel):
    url: str = Field(..., description="The page URL.")
    title: Optional[str] = Field(default="", description="Document title.")
    domain: Optional[str] = Field(default="", description="Hostname; derived from URL if absent.")
    browser: Optional[str] = Field(default="chrome")
    tab_title: Optional[str] = Field(default="")


class BrowserSearchIn(_StrictModel):
    url: str
    query: str = Field(..., description="The user's query text.")
    engine: str = Field(..., description="One of google, duckduckgo, bing, kagi, ...")
    domain: Optional[str] = ""
    browser: Optional[str] = "chrome"


class ChatSessionIn(_StrictModel):
    url: str
    title: Optional[str] = ""
    platform: str = Field(..., description="chatgpt | claude | ...")
    domain: Optional[str] = ""
    browser: Optional[str] = "chrome"


class FileOpenIn(_StrictModel):
    path: str = Field(..., description="Absolute or ~-relative file path.")
    title: Optional[str] = ""
    reveal: Optional[bool] = Field(
        default=False,
        description="True logs as `reveal` (Explorer/Finder); False as `open`.",
    )


class LegacyEventIn(BaseModel):
    """The pre-2A shape: a generic `{kind, payload}` envelope.
    Kept so existing extension installs don't have to be reloaded
    before the user upgrades them. The handler dispatches on
    `kind` and forwards to the right `/v1/` route internally."""

    kind: Literal[
        "browser_visit",
        "browser_search",
        "chat_session",
        "open",
        "reveal",
    ]
    payload: dict


class IngestResponse(BaseModel):
    received: int = Field(..., description="Events submitted in this request.")
    ingested: int = Field(..., description="Events actually written after filters.")
    reason: Optional[str] = Field(
        default=None,
        description="When `ingested < received`, the human-readable cause.",
    )


# --------------------------------------------------------------- retrieval


class EpisodicResultOut(BaseModel):
    kind: str
    title: str
    subtitle: str
    url: str = ""
    ts_epoch: float
    score: float
    session_id: str = ""


class OpenableTarget(BaseModel):
    kind: Literal["url", "path"]
    target: str


class EventOut(BaseModel):
    """A flat projection of an Event for clients that don't want to
    deal with the nested payload shape."""

    ts: str
    session_id: str
    kind: str
    title: str = ""
    url: str = ""
    domain: str = ""
    payload: dict


class MicroContextOut(BaseModel):
    topic: str
    label: str
    time_label: str
    event_count: int
    kinds: List[str]
    match_count: int = 0
    preview_events: List[EventOut]
    openable_targets: List[OpenableTarget]


class SessionOut(BaseModel):
    session_id: str
    topic: str
    label: str
    time_label: str
    score: float
    event_count: int
    kinds: List[str]
    preview_events: List[EventOut]
    openable_targets: List[OpenableTarget]


class SearchResponse(BaseModel):
    query: str
    episodic: List[EpisodicResultOut]
    contexts: List[MicroContextOut]
    sessions: List[SessionOut]
    elapsed_ms: float


class RecentSessionsResponse(BaseModel):
    sessions: List[SessionOut]


class RecentContextsResponse(BaseModel):
    contexts: List[MicroContextOut]


class RecentEventsResponse(BaseModel):
    events: List[EventOut]


class RecentQueriesResponse(BaseModel):
    queries: List[EventOut]


# --------------------------------------------------------------- replay


class ReplayDayIn(BaseModel):
    """`date` is `YYYY-MM-DD` (UTC). Matches the EventStore's
    per-day JSONL filename — no parsing ambiguity."""

    date: str = Field(..., pattern=r"^\d{4}-\d{2}-\d{2}$")


class ReplayDayResponse(BaseModel):
    date: str
    event_count: int
    sessions: List[SessionOut]
    contexts: List[MicroContextOut]
    elapsed_ms: float


# --------------------------------------------------------------- resurfacing


class ResurfacedContextOut(BaseModel):
    """One "continue where you left off" card. Mirrors the shape of
    `SessionOut`/`MicroContextOut` so the launcher can reuse the same
    row widget, but adds the resurfacing-specific signal block."""

    topic: str
    label: str
    time_label: str
    score: float
    confidence: float
    event_count: int
    kinds: List[str]
    preview_events: List[EventOut]
    openable_targets: List[OpenableTarget]
    why: List[str] = Field(
        default_factory=list,
        description=(
            "Plain-English reasons the engine surfaced this topic. "
            "Rendered in the launcher's debug hover; safe to ignore."
        ),
    )
    signals: dict = Field(
        default_factory=dict,
        description=(
            "Per-signal contributions to the score, in [0..1]. "
            "Provided for transparency; clients should not depend on "
            "specific keys."
        ),
    )


class ResurfaceIdleResponse(BaseModel):
    contexts: List[ResurfacedContextOut]
    enabled: bool = True
    elapsed_ms: float = 0.0


class ResurfaceHistoryClearResponse(BaseModel):
    cleared: bool


# --------------------------------------------------------------- threads


class ThreadOut(BaseModel):
    """One memory thread on the wire. Mirrors `app.core.threads.Thread`
    but with `representative_targets` projected onto the same
    `OpenableTarget` shape every other retrieval surface uses."""

    id: str
    topic_key: str
    title: str
    confidence: float
    created_at: float
    updated_at: float
    event_count: int
    session_count: int
    surface_types: List[str]
    representative_queries: List[str]
    representative_targets: List[OpenableTarget]
    timeline_summary: str
    signals: dict = Field(
        default_factory=dict,
        description=(
            "Per-signal contributions to confidence in [0..1]. "
            "Provided for transparency; clients should not rely on "
            "specific keys."
        ),
    )
    why: List[str] = Field(
        default_factory=list,
        description=(
            "Plain-English reasons the thread surfaced. Rendered by "
            "the launcher's debug overlay; safe to ignore."
        ),
    )


class ThreadsRecentResponse(BaseModel):
    threads: List[ThreadOut]
    elapsed_ms: float = 0.0


class ThreadDetailResponse(BaseModel):
    """Full chronological reconstruction for one thread. Bundles the
    existing session + micro-context primitives so the open-thread
    flow doesn't have to invent a new shape."""

    thread: ThreadOut
    sessions: List[SessionOut]
    contexts: List[MicroContextOut]
    events: List[EventOut]


class ThreadForgetResponse(BaseModel):
    forgotten: bool
    thread_id: str


class ThreadsClearResponse(BaseModel):
    cleared: bool


# --------------------------------------------------------------- evolution


class EvolutionPhaseOut(BaseModel):
    """One chronological phase of a thread's evolution. Mirrors
    `app.core.evolution.EvolutionPhase`, with `representative_targets`
    projected onto the same `OpenableTarget` envelope every other
    retrieval surface uses."""

    id: str
    thread_id: str
    title: str
    start_at: float
    end_at: float
    event_count: int
    dominant_surface: str
    representative_queries: List[str]
    representative_targets: List[OpenableTarget]
    momentum_score: float
    revisit_score: float
    transition: str
    signals: dict = Field(default_factory=dict)
    why: List[str] = Field(default_factory=list)


class ThreadEvolutionResponse(BaseModel):
    """Full chronology for one thread."""

    thread_id: str
    phases: List[EvolutionPhaseOut]
    span_start: float
    span_end: float
    elapsed_ms: float = 0.0


# --------------------------------------------------------------- recovery


class RecoveryCandidateOut(BaseModel):
    """One "continue where you left off" card. The launcher renders
    these as the primary idle surface; clicking one opens every
    `suggested_targets` URL/path in sequence.

    `preview_caption` is the deterministic Phase-3C subtitle line
    the launcher renders under the title (e.g. "3 tabs · 2 files
    · last active during implementation"). Same inputs always
    produce the same caption — no AI prose, no LLM summary.
    """

    id: str
    thread_id: str
    title: str
    last_active_at: float
    continuity_score: float
    recovery_confidence: float
    representative_events: List[EventOut]
    suggested_targets: List[OpenableTarget]
    related_sessions: List[str]
    related_contexts: int = 0
    unresolved_signals: List[str] = Field(
        default_factory=list,
        description=(
            "Concrete patterns the engine observed (repeated opens, "
            "repeated searches, abandoned-mid-flow). Rendered by the "
            "launcher's debug overlay."
        ),
    )
    signals: dict = Field(default_factory=dict)
    why: List[str] = Field(default_factory=list)
    # Phase 3C additions —
    preview_caption: str = ""
    last_phase_title: str = ""
    last_phase_transition: str = ""


class RecoveryRecentResponse(BaseModel):
    candidates: List[RecoveryCandidateOut]
    elapsed_ms: float = 0.0


class RestorationStepOut(BaseModel):
    """One step in an orchestrated restoration plan. The launcher
    iterates these in order; each carries a `reason` the debug
    overlay renders when `RECALL_EXPLAIN_RECOVERY=1` is set."""

    kind: str = Field(..., description="\"url\" or \"path\"")
    target: str
    group: str = Field(
        ..., description="\"files\" | \"chats\" | \"tabs\" | \"searches\""
    )
    reason: str


class RecoveryRestoreResponse(BaseModel):
    """The orchestrated restoration plan. Files first, chats next,
    then tabs by domain, then repeated searches. The launcher
    executes this sequence; the endpoint itself does not open
    anything."""

    id: str
    thread_id: str
    title: str
    preview_caption: str = ""
    steps: List[RestorationStepOut]
    # Kept for backward compatibility with Phase-3B clients that
    # only know about `suggested_targets`. Same data, flat shape.
    suggested_targets: List[OpenableTarget]


# --------------------------------------------------------------- health


class HealthResponse(BaseModel):
    status: Literal["ok", "degraded", "down"] = "ok"
    name: str = "recall-api"
    version: str = "2A"
    enabled: bool = True
    ingested_total: int = 0
    dropped_total: int = 0
    events_dir: str = ""
