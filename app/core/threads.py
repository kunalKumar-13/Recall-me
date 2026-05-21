"""Memory threads — Phase 2C.

A *thread* is an evolving topic the user keeps returning to over time.
Built deterministically from the same event log every other layer
reads: no embeddings, no LLM, no clustering. The point is cognitive
continuity, not semantic discovery.

This module is the next abstraction layer on top of:

    events     →   raw capture                     (Phase 1A)
    sessions   →   30-min temporal groupings       (Phase 1E)
    contexts   →   topic-coherent sub-blocks       (Phase 1F)
    resurfacing →  query-time idle surfacing       (Phase 2B)
    threads    →   persistent topic continuity     (Phase 2C, this file)

Where resurfacing is a *transient* score recomputed each idle tick,
a thread is a *persistent* identity that strengthens across rebuilds
and decays naturally when activity stops. The ThreadStore at
`~/.recall/threads.json` only carries identity (id + topic_key +
created_at + title + muted flag) — every other field is derived from
events on demand. Threads are caches in the strict sense: deleting
the file at any time produces a slightly-different rebuild, but no
data is lost.

Design rules, written down so they don't drift:

  1. Deterministic. Same events in → same threads out, always. No
     stateful clustering, no randomization, no probabilistic
     assignment.
  2. Additive. Threads compose on top of the existing engines; they
     never replace them. The retrieval pipeline keeps working
     identically whether threads exist or not.
  3. Local-first. The ThreadStore is one JSON file. No network, no
     index server, no migration ceremony.
  4. Quiet. The launcher surfaces threads only on the idle digest,
     under "Active memory threads" — never inside live search
     results, never in a notification.
  5. <50 ms rebuild on 10K events. The engine reuses the EventStore
     parse cache and the per-Event searchable text cache, so the
     rebuild walk is just one pass with cheap per-event work.
"""

from __future__ import annotations

import hashlib
import json
import logging
import math
import threading
import time
from collections import Counter, defaultdict
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from .config import CONFIG_DIR
from .episodic import _SYNONYMS, _content_tokens
from .events import Event, EventStore, humanize_age

log = logging.getLogger("recall.core.threads")


# --------------------------------------------------------------- inputs


# Event kinds that participate in threads. Wider than the resurfacing
# layer's set because threads care about every surface the user
# touched — a thread of files + chats + browser visits is the
# *interesting* case.
_THREAD_KINDS: frozenset[str] = frozenset({
    "browser_visit",
    "browser_search",
    "chat_session",
    "open",
    "reveal",
    "query",
})

# Kinds that count as "intentional engagement" for grouping. Bare
# launcher queries (`query`) are evidence of *interest* but they
# rarely seed a thread on their own — we cluster around the
# substantive kinds and let `query` enrich the timeline.
_SEEDING_KINDS: frozenset[str] = frozenset({
    "browser_visit",
    "browser_search",
    "chat_session",
    "open",
    "reveal",
})

# Phase 4H — investigation coherence. A browser visit, a search, or
# a chat session carries a *topic* in its title/query text; a bare
# file open does not. These "anchor" kinds let a whole session be
# tagged with the topic it was about, so a file opened inside that
# session can bridge into the investigation it belongs to instead
# of each filename becoming its own disconnected thread.
_ANCHOR_KINDS: frozenset[str] = frozenset({
    "browser_visit",
    "browser_search",
    "chat_session",
})

# File-artifact kinds. These are the events that bridge into a
# session's anchor topic (see `_bucket_events`).
_FILE_KINDS: frozenset[str] = frozenset({
    "open",
    "reveal",
})


# --------------------------------------------------------------- tunables


# Lookback window for the rebuild pass. Wider than resurfacing's
# 14 days because threads accumulate across genuinely-long arcs —
# a healthcare-startup thread should still feel alive at three
# weeks of low activity.
_LOOKBACK_DAYS: int = 30

# A bucket must have at least this many seeding events to be considered
# a thread at all. Three is the smallest signal that means "the user
# keeps coming back" rather than "the user opened it once".
_MIN_SEEDING_EVENTS: int = 3

# Confidence floor for surfacing. Threads below this exist in the
# store but aren't returned from `recent`. Setting the bar at 0.40
# matches the resurfacing engine's surfacing floor — same human
# judgement, different surface.
_MIN_CONFIDENCE: float = 0.40

# Distinct title threshold for `representative_queries`. Three is the
# sweet spot: enough to feel like a recap, not enough to read as a
# log dump.
_REPRESENTATIVE_QUERIES: int = 3
_REPRESENTATIVE_TARGETS: int = 6

# Confidence weights. The components sum to ~1.0 by design so the
# final score lands in [0, 1] without any clamping.
_W_SPAN:    float = 0.20    # how long the thread has been alive
_W_DENSITY: float = 0.25    # event-arrival rate during the lookback
_W_SURFACE: float = 0.15    # cross-surface participation
_W_SESSION: float = 0.20    # distinct sessions involved
_W_RECENCY: float = 0.20    # how fresh the most recent event is

# Recency half-life. Sharper than resurfacing's because a thread that
# hasn't seen an event in two weeks is fading; one with last activity
# yesterday is alive.
_RECENCY_HALFLIFE_DAYS: float = 7.0

# Bucket-merge dedupe: if two threads share at least this fraction of
# events, the lower-scoring one folds into the higher-scoring one.
# Catches the edge case where the synonym table misses a pair
# (`kanye` / `ye`).
_DEDUPE_OVERLAP_THRESHOLD: float = 0.55

# Generic tokens that would collide unrelated activity. Mirrors the
# resurfacing engine's blocklist — kept in sync deliberately.
_GENERIC_TOPIC_TOKENS: frozenset[str] = frozenset({
    "github", "docs", "home", "search", "results", "untitled",
    "google", "youtube", "stackoverflow", "wikipedia", "page",
    "site", "www", "html", "index",
})


# --------------------------------------------------------------- synonyms


def _build_canonical_map() -> Dict[str, str]:
    """Collapse the episodic synonym map into a {alias → canonical}
    lookup. We pick the lexicographically-first key in each synonym
    cluster as the canonical form so the choice is deterministic.

    Built once at module load — synonyms are static; no need to
    rebuild on every rebuild call.
    """
    # Each "cluster" is the closure of mutually-listed synonyms. A
    # token's canonical form is the smallest token in its cluster.
    clusters: Dict[str, set[str]] = {}
    for key, aliases in _SYNONYMS.items():
        members = {key}
        for raw_alias in aliases:
            for piece in raw_alias.split():
                if piece:
                    members.add(piece)
        # Merge with any existing cluster that already overlaps.
        rep = None
        for r, members_set in clusters.items():
            if members & members_set:
                rep = r
                members_set |= members
                break
        if rep is None:
            rep = key
            clusters[rep] = members

    # Flatten with the deterministic canonical name.
    canonical: Dict[str, str] = {}
    for members_set in clusters.values():
        canonical_name = min(members_set)
        for tok in members_set:
            canonical[tok] = canonical_name
    return canonical


_CANONICAL: Dict[str, str] = _build_canonical_map()


def _canonical(token: str) -> str:
    return _CANONICAL.get(token, token)


# --------------------------------------------------------------- model


@dataclass
class Thread:
    """One memory thread.

    `id` is a short, stable hash of the canonical topic_key. The
    derivation is deterministic — a topic that returns after a hiatus
    gets the same id again. `confidence` is recomputed on every
    rebuild and lives in [0, 1]; `created_at` and `id` come from the
    `ThreadStore` so identity survives.
    """

    id: str
    topic_key: str
    title: str
    confidence: float
    created_at: float
    updated_at: float
    event_count: int
    session_count: int
    surface_types: List[str] = field(default_factory=list)
    representative_queries: List[str] = field(default_factory=list)
    representative_targets: List[Tuple[str, str]] = field(default_factory=list)
    timeline_summary: str = ""
    signals: Dict[str, float] = field(default_factory=dict)
    why: List[str] = field(default_factory=list)


# --------------------------------------------------------------- store


@dataclass
class _ThreadMeta:
    """Identity payload stored at `~/.recall/threads.json`. Only the
    fields that *must* survive rebuilds live here — everything else
    is recomputed from events."""

    id: str
    topic_key: str
    title: str
    created_at: float
    last_active_at: float
    muted: bool = False


class ThreadStore:
    """JSON-backed cache of thread identity.

    Two responsibilities:

      • Allocate stable ids: a topic_key always gets the same id back.
      • Carry `created_at`: the *first* time we ever observed a topic,
        not the first time it appeared in the current lookback window.

    Everything else (confidence, event_count, surfaces, …) is rebuilt
    from events at every `ThreadBuilder.rebuild()` call.
    """

    _PATH: Path = CONFIG_DIR / "threads.json"
    _SCHEMA_VERSION: int = 1

    def __init__(self, path: Optional[Path] = None) -> None:
        self.path = path or self._PATH
        self._lock = threading.Lock()
        self._meta: Dict[str, _ThreadMeta] = {}
        self._load()

    # -- persistence -----------------------------------------------------

    def _load(self) -> None:
        try:
            data = json.loads(self.path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            self._meta = {}
            return
        self._meta = {}
        for row in data.get("threads", []) or []:
            try:
                m = _ThreadMeta(
                    id=row["id"],
                    topic_key=row["topic_key"],
                    title=row.get("title") or row["topic_key"],
                    created_at=float(row.get("created_at") or 0.0),
                    last_active_at=float(row.get("last_active_at") or 0.0),
                    muted=bool(row.get("muted", False)),
                )
                self._meta[m.topic_key] = m
            except (KeyError, TypeError, ValueError):
                continue

    def _save(self) -> None:
        try:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            self.path.write_text(
                json.dumps(
                    {
                        "schema_version": self._SCHEMA_VERSION,
                        "threads": [asdict(m) for m in self._meta.values()],
                    },
                    indent=2,
                    ensure_ascii=False,
                ),
                encoding="utf-8",
            )
        except OSError:
            # Best-effort persistence; the rebuild still returns the
            # correct thread set, identity continuity just may not
            # survive the next launch. Consistent with EventLogger's
            # "never raise on persistence" rule.
            pass

    # -- queries ---------------------------------------------------------

    def get(self, topic_key: str) -> Optional[_ThreadMeta]:
        return self._meta.get(topic_key)

    def all_metadata(self) -> List[_ThreadMeta]:
        return list(self._meta.values())

    def is_muted(self, topic_key: str) -> bool:
        m = self._meta.get(topic_key)
        return bool(m and m.muted)

    # -- mutations -------------------------------------------------------

    def upsert(
        self,
        topic_key: str,
        title: str,
        first_event_ts: float,
        last_event_ts: float,
    ) -> _ThreadMeta:
        """Idempotent get-or-create. New threads get an id derived
        from the topic_key so the wire format is short and stable
        across machines (same key on two machines = same id)."""
        with self._lock:
            m = self._meta.get(topic_key)
            if m is None:
                m = _ThreadMeta(
                    id=_thread_id(topic_key),
                    topic_key=topic_key,
                    title=title,
                    created_at=first_event_ts,
                    last_active_at=last_event_ts,
                )
            else:
                # Identity wins — never move `created_at` forward.
                # The title can drift (we'd rather show "WebSocket
                # retries in production" than the canonical stem
                # `websocket`), and `last_active_at` advances.
                m.title = title
                m.last_active_at = max(m.last_active_at, last_event_ts)
            self._meta[topic_key] = m
            self._save()
            return m

    def mute(self, thread_id: str) -> bool:
        with self._lock:
            for m in self._meta.values():
                if m.id == thread_id:
                    m.muted = True
                    self._save()
                    return True
            return False

    def forget(self, thread_id: str) -> bool:
        """Drop a thread by id. Re-allocates the id if the topic
        ever reappears in the events."""
        with self._lock:
            target_key: Optional[str] = None
            for key, m in self._meta.items():
                if m.id == thread_id:
                    target_key = key
                    break
            if target_key is None:
                return False
            del self._meta[target_key]
            self._save()
            return True

    def clear(self) -> None:
        """User-facing "Clear thread cache" — drops the whole store.
        Subsequent rebuilds will re-derive thread ids from current
        events."""
        with self._lock:
            self._meta = {}
            try:
                if self.path.exists():
                    self.path.unlink()
            except OSError:
                pass


# --------------------------------------------------------------- builder


class ThreadBuilder:
    """Deterministic heuristic grouping pipeline.

    One public method, `rebuild()`. Reads the event log, buckets
    events by their canonical topic_key (synonyms collapsed), scores
    each bucket, persists identity into the `ThreadStore`, and
    returns the top-N threads ranked by confidence.

    Stateless w.r.t. the user query — threads are a property of the
    user's activity, not the launcher input.
    """

    def __init__(
        self,
        event_store: EventStore,
        store: Optional[ThreadStore] = None,
    ) -> None:
        self.event_store = event_store
        self.store = store or ThreadStore()
        # Phase 4H — one-entry `now`-keyed memo of the bucketing
        # pass. `recover_recent` calls `rebuild()` and then, per
        # candidate, `events_for_topic()` — all with the same `now`.
        # Memoizing keeps that to a single bucketing walk.
        self._bucket_cache: Optional[
            Tuple[float, Dict[str, List[Event]]]
        ] = None

    # -- public ----------------------------------------------------------

    def rebuild(
        self, now: Optional[float] = None
    ) -> List[Thread]:
        """Compute the current thread set and update the store.

        Returns the threads above `_MIN_CONFIDENCE`, sorted by
        confidence descending. Threads in the store that weren't
        observed this rebuild are kept (for identity continuity) but
        not returned — they decay implicitly when their events fall
        outside the lookback window.
        """
        if now is None:
            now = time.time()

        buckets = self._bucket_events(now)
        if not buckets:
            return []

        candidates: list[Thread] = []
        for topic_key, events in buckets.items():
            if self.store.is_muted(topic_key):
                continue
            seeding = [ev for ev in events if ev.kind in _SEEDING_KINDS]
            if len(seeding) < _MIN_SEEDING_EVENTS:
                continue
            thread = self._build_thread(topic_key, events, seeding, now)
            if thread is None:
                continue
            candidates.append(thread)

        # Dedupe by event overlap. Two buckets with effectively the
        # same events fold together — the synonym map is the primary
        # defence, this is the fallback.
        candidates = self._dedupe_by_overlap(candidates)

        candidates.sort(key=lambda t: t.confidence, reverse=True)
        return [t for t in candidates if t.confidence >= _MIN_CONFIDENCE]

    def events_for_topic(
        self, topic_key: str, now: Optional[float] = None
    ) -> List[Event]:
        """Every event the rebuild groups under `topic_key`, using
        the *same* session-anchored bucketing as `rebuild()`.

        Consumers that need a thread's members (recovery, in
        particular) must read membership from here — not by
        re-deriving it per event with `_thread_key`. Phase 4H made
        file artifacts bridge into their investigation's session
        anchor; a consumer that re-derived per-event would key
        `backoff.py` back to its filename and miss it, recovering
        objects instead of the whole room.
        """
        if now is None:
            now = time.time()
        return list(self._bucket_events(now).get(topic_key, []))

    def forget_thread(self, thread_id: str) -> bool:
        """Forward to the store. Exposed so the service layer doesn't
        have to know about the store implementation detail."""
        return self.store.forget(thread_id)

    def mute_thread(self, thread_id: str) -> bool:
        return self.store.mute(thread_id)

    def clear(self) -> None:
        self.store.clear()

    # -- bucketing -------------------------------------------------------

    def _bucket_events(self, now: float) -> Dict[str, List[Event]]:
        """Two-pass bucketing (Phase 4H — investigation coherence).

        Pass 1 — *anchor* each session. Browser visits, searches,
        and chat sessions name a topic in their text; bucketing
        those by topic gives every session a dominant topic_key.

        Pass 2 — bucket every event. A file open/reveal bridges
        into its session's anchor topic when one exists, so
        `backoff.py` opened inside the WebSocket-debugging session
        joins the WebSocket investigation rather than forming its
        own filename-keyed thread. A file opened in a session with
        no anchor (a pure coding session, no browser activity)
        keeps its filename-derived key — a standalone coding arc is
        genuinely its own thread until it connects to something.

        Per-event work stays cheap — two dict lookups and a cached
        canonical translate — so the <50 ms rebuild budget holds.
        """
        cached = self._bucket_cache
        if cached is not None and cached[0] == now:
            return cached[1]

        cutoff = now - _LOOKBACK_DAYS * 86400
        # Tokenize once. `_thread_key` runs `_content_tokens`, the
        # one genuinely expensive per-event call — compute it
        # exactly once per event, then both passes below are just
        # cheap dict work. (A naive two-pass version that re-keyed
        # anchor events doubled the tokenization cost and blew the
        # rebuild budget.)
        keyed: list[Tuple[Event, str]] = []
        for ev in self.event_store.iter_events(days=_LOOKBACK_DAYS):
            if ev.kind not in _THREAD_KINDS:
                continue
            if ev.ts_epoch() < cutoff:
                continue
            keyed.append((ev, self._thread_key(ev)))

        # Pass 1 — per-session anchor topic, from anchor surfaces.
        anchor_votes: Dict[str, Counter] = defaultdict(Counter)
        for ev, key in keyed:
            if key and ev.session_id and ev.kind in _ANCHOR_KINDS:
                anchor_votes[ev.session_id][key] += 1
        session_anchor: Dict[str, str] = {}
        for sid, votes in anchor_votes.items():
            # Deterministic: highest vote count, ties broken by the
            # lexicographically-smallest key.
            session_anchor[sid] = min(
                votes.items(), key=lambda kv: (-kv[1], kv[0])
            )[0]

        # Pass 2 — bucket, bridging file artifacts into their
        # session's investigation.
        buckets: Dict[str, list[Event]] = defaultdict(list)
        for ev, key in keyed:
            if ev.kind in _FILE_KINDS:
                bucket_key = session_anchor.get(ev.session_id or "") or key
            else:
                bucket_key = key
            if not bucket_key:
                continue
            buckets[bucket_key].append(ev)

        self._bucket_cache = (now, buckets)
        return buckets

    @staticmethod
    def _thread_key(ev: Event) -> str:
        """Choose the canonical bucket key for an event. Title /
        query first, then domain; synonyms collapse before return.

        `query` events grab their token from `payload.text` (the
        launcher's input), which the other surfaces don't carry."""
        payload = ev.payload or {}
        text_sources: list[str] = []
        for fld in ("title", "query", "text"):
            v = (payload.get(fld) or "").strip()
            if v:
                text_sources.append(v)
        for text in text_sources:
            for tok in _content_tokens(text):
                if tok in _GENERIC_TOPIC_TOKENS:
                    continue
                return _canonical(tok)
        # Domain fallback (rare — used when title/query/text are
        # absent or carry only generic tokens).
        domain = (payload.get("domain") or "").strip().lower()
        if domain:
            head = domain.split(".")[0]
            if head and head not in _GENERIC_TOPIC_TOKENS:
                return _canonical(head)
        return ""

    # -- per-thread build ------------------------------------------------

    def _build_thread(
        self,
        topic_key: str,
        events: List[Event],
        seeding: List[Event],
        now: float,
    ) -> Optional[Thread]:
        """Score the bucket, pick a human title, register identity in
        the store, and pack a `Thread`. Returns None when the bucket
        fails an anti-noise filter that depends on cross-event state
        (which the `_MIN_SEEDING_EVENTS` precheck couldn't enforce)."""
        events.sort(key=lambda e: e.ts_epoch())
        first_ts = events[0].ts_epoch()
        last_ts = events[-1].ts_epoch()

        sessions = {ev.session_id for ev in events if ev.session_id}
        surfaces: list[str] = []
        seen_surface: set[str] = set()
        for ev in events:
            if ev.kind in _THREAD_KINDS and ev.kind not in seen_surface:
                seen_surface.add(ev.kind)
                surfaces.append(ev.kind)

        # Refuse threads built entirely inside one session — those are
        # already a session, not a thread.
        if len(sessions) <= 1:
            return None

        # Span score: log-shaped age of the thread (since first event).
        days_alive = max(0.0, (now - first_ts) / 86400.0)
        s_span = min(1.0, math.log1p(days_alive) / math.log(15.0))

        # Density: events per active day, normalized to the
        # 1-event-per-day baseline.
        active_days = self._active_day_count(events)
        density_raw = len(events) / max(1, active_days)
        s_density = min(1.0, density_raw / 4.0)
        # Floor it for very small threads so a 3-event thread doesn't
        # collapse density to 0.05.
        s_density = max(s_density, min(1.0, len(events) / 12.0))

        # Surface diversity. 1 surface = 0 bonus; 4 surfaces = full.
        s_surface = min(1.0, (len(surfaces) - 1) / 3.0)

        # Session diversity. Capped at 5 distinct sessions.
        s_session = min(1.0, (len(sessions) - 1) / 4.0)

        # Recency: exponential decay from most recent event.
        days_since = max(0.0, (now - last_ts) / 86400.0)
        s_recency = math.pow(0.5, days_since / _RECENCY_HALFLIFE_DAYS)

        confidence = (
            _W_SPAN    * s_span
            + _W_DENSITY * s_density
            + _W_SURFACE * s_surface
            + _W_SESSION * s_session
            + _W_RECENCY * s_recency
        )
        confidence = round(min(1.0, confidence), 4)

        # Representative queries — distinct, normalized, newest-first.
        queries = self._representative_queries(events)
        # Representative openable targets — distinct, newest-first.
        targets = self._representative_targets(events)

        title = self._derive_title(topic_key, events)

        # Persist identity in the store. This is where stabilization
        # *happens*: the second rebuild that observes this topic gets
        # the *same* id and the same created_at, no matter what the
        # caller does.
        meta = self.store.upsert(
            topic_key=topic_key,
            title=title,
            first_event_ts=first_ts,
            last_event_ts=last_ts,
        )

        timeline_summary = self._format_timeline_summary(
            created_at=meta.created_at,
            last_active=last_ts,
            event_count=len(events),
            session_count=len(sessions),
            surface_count=len(surfaces),
            now=now,
        )

        signals = {
            "span":      round(s_span, 3),
            "density":   round(s_density, 3),
            "surface":   round(s_surface, 3),
            "session":   round(s_session, 3),
            "recency":   round(s_recency, 3),
        }
        why = self._explain(
            topic_key=topic_key,
            event_count=len(events),
            session_count=len(sessions),
            day_count=active_days,
            surface_count=len(surfaces),
        )

        return Thread(
            id=meta.id,
            topic_key=topic_key,
            title=title,
            confidence=confidence,
            created_at=meta.created_at,
            updated_at=last_ts,
            event_count=len(events),
            session_count=len(sessions),
            surface_types=surfaces,
            representative_queries=queries,
            representative_targets=targets,
            timeline_summary=timeline_summary,
            signals=signals,
            why=why,
        )

    # -- helpers ---------------------------------------------------------

    @staticmethod
    def _active_day_count(events: List[Event]) -> int:
        days: set = set()
        for ev in events:
            ts = ev.ts_epoch()
            if ts > 0:
                days.add(datetime.fromtimestamp(ts, timezone.utc).date())
        return max(1, len(days))

    @staticmethod
    def _representative_queries(events: List[Event]) -> List[str]:
        """Pick up to `_REPRESENTATIVE_QUERIES` distinct user-typed
        queries (or search-engine queries) tied to the thread.
        Newest-first; deduped by lowercased form."""
        seen: set[str] = set()
        out: list[str] = []
        for ev in reversed(events):
            payload = ev.payload or {}
            text = ""
            if ev.kind == "browser_search":
                text = (payload.get("query") or "").strip()
            elif ev.kind == "query":
                text = (payload.get("text") or "").strip()
            else:
                continue
            if not text:
                continue
            key = text.lower()
            if key in seen:
                continue
            seen.add(key)
            out.append(text)
            if len(out) >= _REPRESENTATIVE_QUERIES:
                break
        return out

    @staticmethod
    def _representative_targets(events: List[Event]) -> List[Tuple[str, str]]:
        """Distinct openable (kind, target) pairs, newest-first.
        Limited to `_REPRESENTATIVE_TARGETS` so the UI never gets a
        wall of URLs."""
        seen: set[str] = set()
        out: list[Tuple[str, str]] = []
        for ev in reversed(events):
            payload = ev.payload or {}
            url = (payload.get("url") or "").strip()
            path = (payload.get("path") or "").strip()
            target = url or path
            if not target:
                continue
            key = target.lower()
            if key in seen:
                continue
            seen.add(key)
            out.append(("url" if url else "path", target))
            if len(out) >= _REPRESENTATIVE_TARGETS:
                break
        return out

    @staticmethod
    def _derive_title(topic_key: str, events: List[Event]) -> str:
        """Prefer the most-common substantive title across the
        thread's events. Falls back to the most-recent title, then to
        the topic_key. Capitalized minimally — we never invent
        sentence casing where the user didn't have any."""
        counter: Counter = Counter()
        for ev in events:
            payload = ev.payload or {}
            title = (payload.get("title") or "").strip()
            if title and len(title) >= 4:
                counter[title] += 1
        if counter:
            top, _ = counter.most_common(1)[0]
            if len(top) > 80:
                top = top[:77].rstrip() + "…"
            return top
        # No usable title in any event — fall back to topic.
        return topic_key.capitalize()

    @staticmethod
    def _format_timeline_summary(
        created_at: float,
        last_active: float,
        event_count: int,
        session_count: int,
        surface_count: int,
        now: float,
    ) -> str:
        """One-line timeline like `Started 2w ago · 4 sessions · 14 events`.
        Deliberately undecorated; the launcher row prints it dim."""
        parts: list[str] = []
        if created_at > 0:
            parts.append(f"Started {humanize_age(created_at, now=now)}")
        if session_count >= 2:
            parts.append(f"{session_count} sessions")
        parts.append(
            f"{event_count} event{'s' if event_count != 1 else ''}"
        )
        if surface_count >= 2:
            parts.append(
                f"{surface_count} surface{'s' if surface_count != 1 else ''}"
            )
        return "  ·  ".join(parts)

    @staticmethod
    def _explain(
        topic_key: str,
        event_count: int,
        session_count: int,
        day_count: int,
        surface_count: int,
    ) -> List[str]:
        """Plain-English reasons. The launcher's debug overlay
        ("Why am I seeing this?") renders these verbatim — we never
        speculate, only report."""
        lines: list[str] = []
        if session_count >= 2:
            lines.append(f"spans {session_count} sessions")
        if day_count >= 2:
            lines.append(f"touched on {day_count} different days")
        if surface_count >= 2:
            lines.append(f"appears across {surface_count} surfaces")
        if event_count >= 6:
            lines.append(f"{event_count} related events")
        lines.append(f'(topic key: "{topic_key}")')
        return lines

    # -- dedupe ----------------------------------------------------------

    @staticmethod
    def _dedupe_by_overlap(threads: List[Thread]) -> List[Thread]:
        """If two threads share >55% of their representative-target
        URLs, fold the lower-scoring one into the higher-scoring one
        (i.e., drop it). Catches the synonym-table gap case."""
        if len(threads) <= 1:
            return threads
        threads.sort(key=lambda t: t.confidence, reverse=True)
        kept: list[Thread] = []
        kept_sets: list[set[str]] = []
        for t in threads:
            tgt_set = {tgt.lower() for _, tgt in t.representative_targets}
            if not tgt_set:
                kept.append(t)
                kept_sets.append(set())
                continue
            duplicate = False
            for prev in kept_sets:
                if not prev:
                    continue
                overlap = len(tgt_set & prev)
                if overlap / max(1, min(len(tgt_set), len(prev))) >= _DEDUPE_OVERLAP_THRESHOLD:
                    duplicate = True
                    break
            if not duplicate:
                kept.append(t)
                kept_sets.append(tgt_set)
        return kept


# --------------------------------------------------------------- helpers


def _thread_id(topic_key: str) -> str:
    """Deterministic short id derived from the canonical topic_key.
    Same key on any machine → same id (useful for syncing settings
    files in the future without re-keying)."""
    h = hashlib.sha1(topic_key.encode("utf-8")).hexdigest()[:8]
    return f"thr_{h}"
