"""Thread evolution — Phase 3A.

Threads (Phase 2C) are stable identities. Evolution (this module) is
how a thread *changes* across time: research → implementation →
debugging → abandonment → revisit. The output is a small ordered list
of phases that reads as a chronology of thought, not a static bucket.

This file is the next abstraction layer on top of:

    events     →  raw capture                    (Phase 1A)
    sessions   →  30-min temporal groupings      (Phase 1E)
    contexts   →  topic-coherent sub-blocks      (Phase 1F)
    resurfacing→  query-time idle surfacing      (Phase 2B)
    threads    →  persistent topic identity      (Phase 2C)
    evolution  →  chronological phases of a thread    (Phase 3A, this file)

Design rules, written down so they don't drift:

  1. Deterministic. Same events in → same phases out. No randomness,
     no learned weights, no adaptive thresholds that aren't a closed-
     form function of the input.
  2. Additive. Evolution composes on top of the existing engines.
     `ThreadBuilder` provides the topic_key; this file segments the
     events that bucket already grouped.
  3. Quiet. The launcher exposes evolution only when the user opens a
     thread — never inside live search, never as a notification.
  4. Local-first. The optional `ThreadEvolutionStore` is one JSON
     file at `~/.recall/evolution.json`; deleting it is safe.
  5. <70 ms reconstruction on a 10K-event log. The hot path is the
     topic filter pass over the event store; segmentation runs on
     the filtered subset (~tens of events) and adds milliseconds.
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
from typing import Dict, Iterable, List, Optional, Tuple

from .config import CONFIG_DIR
from .episodic import _content_tokens
from .events import Event, EventStore, humanize_age
from .threads import Thread, ThreadBuilder

log = logging.getLogger("recall.core.evolution")


# --------------------------------------------------------------- tunables


# Maximum number of phases per thread. Anti-noise — past this the
# timeline reads as a log dump, not a chronology. The dedupe pass
# collapses the noisiest boundaries until we're at or below this cap.
_MAX_PHASES: int = 8

# A phase below this size folds into its closer neighbour. Single-
# event phases are almost always noise in a properly threaded topic.
_MIN_PHASE_EVENTS: int = 2

# Adaptive temporal-gap floor. The actual threshold is the maximum of
# this and a multiple of the thread's typical inter-event interval.
_GAP_FLOOR_SECONDS: float = 86400.0  # 24 hours
# Multiple applied to the median inter-event interval to scale the
# gap threshold to the thread's cadence. A daily thread has a much
# wider "gap" than an hourly one.
_GAP_MEDIAN_MULTIPLIER: float = 6.0
# Big-gap threshold for transition labels — when a phase boundary
# spans more than (gap_threshold × this), the *previous* phase
# reads as abandoned and the new one as a revisit/resumption.
_BIG_GAP_MULTIPLIER: float = 2.0

# Window used for soft-boundary detection (surface + vocabulary
# shift). Three events on each side is the smallest window that
# survives one noisy outlier.
_SHIFT_WINDOW: int = 3
# Jaccard similarity threshold for vocabulary shift. Below this,
# the rolling-window token sets are considered to have shifted.
_VOCAB_JACCARD_THRESHOLD: float = 0.18

# Momentum normalization. Events-per-hour above this number map to
# momentum=1.0; below scales linearly. Tuned from the real-life
# observation that 4 events in one hour reads as "intense activity".
_MOMENTUM_PEAK_EVENTS_PER_HOUR: float = 4.0

# Revisit detection. A phase whose targets overlap earlier phases by
# at least this fraction is labelled a revisit transition.
_REVISIT_FRACTION: float = 0.5

# Representative slot counts. Mirrors the threads layer's bounds so
# the wire format stays predictable.
_REPRESENTATIVE_QUERIES: int = 3
_REPRESENTATIVE_TARGETS: int = 6


# Surface-type → user-facing phase title for the dominant kind. The
# brief lists *research / implementation / debugging / abandonment /
# revisit* as examples; we use those plus a handful of obvious
# stand-ins for chat / search / launcher activity.
_SURFACE_TITLES: Dict[str, str] = {
    "browser_visit":  "Reading",
    "browser_search": "Searching",
    "chat_session":   "Discussion",
    "open":           "Implementation",
    "reveal":         "Implementation",
    "query":          "Looking up",
}


# --------------------------------------------------------------- model


@dataclass
class EvolutionPhase:
    """One chronological phase inside a thread's evolution.

    `transition` records how the phase *started* relative to the
    previous one — `initial | continuation | acceleration | pivot |
    revisit | resumption`. `momentum_score` and `revisit_score` are
    independent scores in [0, 1] used to derive the transition and
    to power the debug overlay.
    """

    id: str
    thread_id: str
    title: str
    start_at: float
    end_at: float
    event_count: int
    dominant_surface: str
    representative_queries: List[str] = field(default_factory=list)
    representative_targets: List[Tuple[str, str]] = field(default_factory=list)
    momentum_score: float = 0.0
    revisit_score: float = 0.0
    transition: str = "initial"
    signals: Dict[str, float] = field(default_factory=dict)
    why: List[str] = field(default_factory=list)


@dataclass
class ThreadEvolution:
    """A thread's full chronology. The launcher renders this as a
    horizontal strip of phase chips; programmatic clients consume
    `phases` directly."""

    thread_id: str
    phases: List[EvolutionPhase] = field(default_factory=list)
    span_start: float = 0.0
    span_end: float = 0.0
    elapsed_ms: float = 0.0


# --------------------------------------------------------------- store


@dataclass
class _EvolutionCacheEntry:
    """One row in `~/.recall/evolution.json`. Fingerprint = event
    count + last-event timestamp on the thread; matching fingerprint
    means the cache is fresh."""

    thread_id: str
    fingerprint: str
    payload: dict       # serialized ThreadEvolution


class ThreadEvolutionStore:
    """Small JSON cache so a hover-on-thread doesn't rebuild the
    evolution from scratch every frame.

    Stores one entry per thread, keyed by the thread's id. The cache
    is invalidated when the thread's `(event_count, last_event_ts)`
    pair changes — i.e. when new events for the topic arrive.

    Failures are best-effort. The builder always returns correct
    output regardless of whether the cache hit or missed.
    """

    _PATH: Path = CONFIG_DIR / "evolution.json"
    _SCHEMA_VERSION: int = 1

    def __init__(self, path: Optional[Path] = None) -> None:
        self.path = path or self._PATH
        self._lock = threading.Lock()
        self._entries: Dict[str, _EvolutionCacheEntry] = {}
        self._load()

    def _load(self) -> None:
        try:
            data = json.loads(self.path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            self._entries = {}
            return
        out: Dict[str, _EvolutionCacheEntry] = {}
        for row in data.get("entries", []) or []:
            try:
                out[row["thread_id"]] = _EvolutionCacheEntry(
                    thread_id=row["thread_id"],
                    fingerprint=row.get("fingerprint", ""),
                    payload=row.get("payload") or {},
                )
            except (KeyError, TypeError):
                continue
        self._entries = out

    def _save(self) -> None:
        try:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            self.path.write_text(
                json.dumps(
                    {
                        "schema_version": self._SCHEMA_VERSION,
                        "entries": [
                            asdict(e) for e in self._entries.values()
                        ],
                    },
                    indent=2,
                    ensure_ascii=False,
                ),
                encoding="utf-8",
            )
        except OSError:
            pass

    def get(self, thread_id: str, fingerprint: str) -> Optional[dict]:
        entry = self._entries.get(thread_id)
        if entry is None:
            return None
        if entry.fingerprint != fingerprint:
            return None
        return entry.payload

    def put(self, thread_id: str, fingerprint: str, payload: dict) -> None:
        with self._lock:
            self._entries[thread_id] = _EvolutionCacheEntry(
                thread_id=thread_id,
                fingerprint=fingerprint,
                payload=payload,
            )
            self._save()

    def drop(self, thread_id: str) -> None:
        with self._lock:
            if thread_id in self._entries:
                del self._entries[thread_id]
                self._save()

    def clear(self) -> None:
        with self._lock:
            self._entries = {}
            try:
                if self.path.exists():
                    self.path.unlink()
            except OSError:
                pass


# --------------------------------------------------------------- builder


class EvolutionBuilder:
    """Pure-function evolution constructor.

    One public method, `build(thread)`. Reads the event log,
    filters to the thread's topic_key, segments chronologically,
    scores each phase, labels transitions, and packs a
    `ThreadEvolution`.

    Holds two pieces of state: the `EventStore` it reads from and a
    `ThreadBuilder` it borrows for the canonical-topic-key lookup
    (so the bucketing logic stays in one place).
    """

    def __init__(
        self,
        event_store: EventStore,
        thread_builder: Optional[ThreadBuilder] = None,
        store: Optional[ThreadEvolutionStore] = None,
    ) -> None:
        self.event_store = event_store
        self.thread_builder = thread_builder or ThreadBuilder(event_store)
        self.store = store or ThreadEvolutionStore()

    # -- public ----------------------------------------------------------

    def build(self, thread: Thread) -> ThreadEvolution:
        """Reconstruct the evolution for one thread.

        The thread comes from the threads layer; we trust its
        `topic_key` to filter events. Returns an empty
        `ThreadEvolution` (no phases) when the thread has fewer than
        `_MIN_PHASE_EVENTS` events — the caller decides whether to
        render that as "no evolution yet" or hide the surface.
        """
        t0 = time.perf_counter()

        events = self._collect_topic_events(thread.topic_key)
        if len(events) < _MIN_PHASE_EVENTS:
            empty = ThreadEvolution(
                thread_id=thread.id,
                phases=[],
                span_start=0.0,
                span_end=0.0,
                elapsed_ms=round((time.perf_counter() - t0) * 1000, 2),
            )
            return empty

        # Cache check before doing any work that depends on the full
        # event set. Fingerprint = (n, last_ts) — invalidated the
        # moment a new event for the topic lands.
        fingerprint = _fingerprint(events)
        cached = self.store.get(thread.id, fingerprint)
        if cached is not None:
            evo = _deserialize(cached)
            evo.elapsed_ms = round((time.perf_counter() - t0) * 1000, 2)
            return evo

        phases = self._segment(thread.id, events)
        phases = self._merge_tiny(phases, events)
        phases = self._dedupe_adjacent(phases, events)
        phases = self._label_transitions(phases, events)

        evo = ThreadEvolution(
            thread_id=thread.id,
            phases=phases,
            span_start=events[0].ts_epoch() if events else 0.0,
            span_end=events[-1].ts_epoch() if events else 0.0,
            elapsed_ms=round((time.perf_counter() - t0) * 1000, 2),
        )

        # Persist for next time. Best-effort — failures don't
        # affect the return value.
        self.store.put(thread.id, fingerprint, _serialize(evo))
        return evo

    # -- collection ------------------------------------------------------

    def _collect_topic_events(self, topic_key: str) -> List[Event]:
        """Walk the 30-day window and keep events whose canonical
        topic_key matches. Sorted chronologically (oldest first)."""
        out: list[Event] = []
        for ev in self.event_store.iter_events(days=30):
            if self.thread_builder._thread_key(ev) == topic_key:
                out.append(ev)
        out.sort(key=lambda e: e.ts_epoch())
        return out

    # -- segmentation ----------------------------------------------------

    def _segment(self, thread_id: str, events: List[Event]) -> List[EvolutionPhase]:
        """Cut the event list at every detected boundary and build
        one `EvolutionPhase` per slice.

        Boundary heuristics:

          1. Temporal gap > adaptive threshold (hard cut).
          2. Surface-type shift across a 3-event rolling window.
          3. Vocabulary Jaccard drop across a 3-event rolling
             window.

        Heuristic 1 alone is sometimes enough; (2) and (3) catch
        the case where activity stays continuous but the user's
        mode shifts (research → implementation, …).
        """
        if len(events) < 2:
            return []

        gap_threshold = _adaptive_gap_threshold(events)

        # Indices where a new phase begins. 0 is always a start.
        starts: list[int] = [0]
        for i in range(1, len(events)):
            prev_ts = events[i - 1].ts_epoch()
            curr_ts = events[i].ts_epoch()
            gap = curr_ts - prev_ts

            if gap > gap_threshold:
                starts.append(i)
                continue

            # Soft boundaries only fire when we have enough context
            # on both sides — a 2-event window would invent
            # boundaries everywhere.
            if i >= _SHIFT_WINDOW and (len(events) - i) >= _SHIFT_WINDOW:
                if (
                    _surface_shift(events, i)
                    or _vocabulary_shift(events, i)
                ):
                    starts.append(i)

        # Walk the starts list to make phases.
        phases: list[EvolutionPhase] = []
        earlier_targets: set[Tuple[str, str]] = set()
        for slot, start_idx in enumerate(starts):
            end_idx = starts[slot + 1] if slot + 1 < len(starts) else len(events)
            slice_events = events[start_idx:end_idx]
            if not slice_events:
                continue
            phase = self._score_phase(
                thread_id=thread_id,
                slot=slot,
                slice_events=slice_events,
                earlier_targets=earlier_targets,
            )
            phases.append(phase)
            # Update the earlier-targets pool for the *next* phase's
            # revisit calculation. We do this slot-by-slot so each
            # phase sees only what came before it.
            for ev in slice_events:
                key = _event_target_key(ev)
                if key is not None:
                    earlier_targets.add(key)

        return phases

    # -- per-phase scoring ----------------------------------------------

    def _score_phase(
        self,
        thread_id: str,
        slot: int,
        slice_events: List[Event],
        earlier_targets: set,
    ) -> EvolutionPhase:
        """Compute per-phase metrics + label."""
        start_ts = slice_events[0].ts_epoch()
        end_ts = slice_events[-1].ts_epoch()
        n = len(slice_events)

        # Momentum: events per hour, normalized. A phase whose span
        # is shorter than the per-hour scale gets the rate-cap so a
        # 5-events-in-90-seconds burst isn't read as "momentum 60".
        span_seconds = max(1.0, end_ts - start_ts)
        events_per_hour = (n * 3600.0) / span_seconds
        # Very short bursts (single event, or a few events within
        # one minute) can't carry full momentum credit — they're
        # tactical, not sustained.
        if n < 3 or span_seconds < 60.0:
            events_per_hour = min(events_per_hour, n / 0.5)
        momentum_score = min(1.0, events_per_hour / _MOMENTUM_PEAK_EVENTS_PER_HOUR)

        # Revisit: fraction of this phase's targets that appeared
        # in earlier phases of the same thread.
        phase_targets: set = set()
        for ev in slice_events:
            key = _event_target_key(ev)
            if key is not None:
                phase_targets.add(key)
        if phase_targets:
            revisits = len(phase_targets & earlier_targets)
            revisit_score = revisits / len(phase_targets)
        else:
            revisit_score = 0.0

        # Dominant surface among the slice.
        surface_counts = Counter(ev.kind for ev in slice_events)
        dominant_surface = surface_counts.most_common(1)[0][0]

        title = _phase_title(
            dominant_surface=dominant_surface,
            slice_events=slice_events,
            revisit_score=revisit_score,
        )

        queries = _representative_queries(slice_events)
        targets = _representative_targets(slice_events)

        signals = {
            "momentum":       round(momentum_score, 3),
            "revisit":        round(revisit_score, 3),
            "events_per_hour": round(events_per_hour, 2),
            "duration_hours": round(span_seconds / 3600.0, 2),
        }

        return EvolutionPhase(
            id=_phase_id(thread_id, slot, start_ts),
            thread_id=thread_id,
            title=title,
            start_at=start_ts,
            end_at=end_ts,
            event_count=n,
            dominant_surface=dominant_surface,
            representative_queries=queries,
            representative_targets=targets,
            momentum_score=round(momentum_score, 4),
            revisit_score=round(revisit_score, 4),
            transition="initial",   # filled in later
            signals=signals,
            why=[],                 # filled in by `_label_transitions`
        )

    # -- merging --------------------------------------------------------

    def _merge_tiny(
        self, phases: List[EvolutionPhase], events: List[Event]
    ) -> List[EvolutionPhase]:
        """Fold single-event phases into whichever neighbour they're
        closer to in time. Anti-noise: a phase of one event almost
        always reads as a stray boundary."""
        if len(phases) <= 1:
            return phases
        out: list[EvolutionPhase] = []
        for p in phases:
            if p.event_count >= _MIN_PHASE_EVENTS:
                out.append(p)
                continue
            # Tiny phase — merge into the closer of the two
            # neighbours by timestamp.
            if not out:
                # First phase; merge forward by skipping its add.
                continue
            prev = out[-1]
            # Merge forward into the next phase if available and
            # closer; otherwise back into the previous.
            next_idx = phases.index(p) + 1
            if next_idx < len(phases):
                nxt = phases[next_idx]
                gap_back = p.start_at - prev.end_at
                gap_fwd = nxt.start_at - p.end_at
                if gap_fwd < gap_back:
                    # Will be merged by the next iteration; don't
                    # add this one and let the next phase's
                    # `start_at` already cover it.
                    # We'll fix the next phase's start_at on its turn.
                    continue
            # Merge back into `prev`.
            prev.end_at = p.end_at
            prev.event_count += p.event_count
        return out or phases

    def _dedupe_adjacent(
        self, phases: List[EvolutionPhase], events: List[Event]
    ) -> List[EvolutionPhase]:
        """If we still have more than `_MAX_PHASES`, collapse the
        most-similar adjacent pair (same dominant surface, similar
        durations, low transition signal) until we're under the cap.
        Always preserves the first and last phase."""
        if len(phases) <= _MAX_PHASES:
            return phases
        # Iteratively merge the pair with the highest similarity
        # score until length ≤ _MAX_PHASES.
        # (Cheap on small lists; max-phases is single digits.)
        phases = list(phases)
        while len(phases) > _MAX_PHASES:
            best_idx = 1
            best_score = -1.0
            for i in range(len(phases) - 1):
                a, b = phases[i], phases[i + 1]
                same_surface = 1.0 if a.dominant_surface == b.dominant_surface else 0.0
                # Smaller is more "mergeable". Score: same surface
                # plus 1/duration weighting so tiny pairs collapse
                # before substantial ones.
                score = same_surface + (1.0 / max(1.0, b.end_at - a.start_at + 1))
                if score > best_score:
                    best_score = score
                    best_idx = i
            a, b = phases[best_idx], phases[best_idx + 1]
            merged = EvolutionPhase(
                id=a.id,
                thread_id=a.thread_id,
                title=a.title,
                start_at=a.start_at,
                end_at=b.end_at,
                event_count=a.event_count + b.event_count,
                dominant_surface=a.dominant_surface,
                representative_queries=(
                    a.representative_queries + b.representative_queries
                )[:_REPRESENTATIVE_QUERIES],
                representative_targets=(
                    a.representative_targets + b.representative_targets
                )[:_REPRESENTATIVE_TARGETS],
                momentum_score=max(a.momentum_score, b.momentum_score),
                revisit_score=max(a.revisit_score, b.revisit_score),
                transition=a.transition,
                signals=a.signals,
            )
            phases[best_idx : best_idx + 2] = [merged]
        return phases

    # -- transitions -----------------------------------------------------

    def _label_transitions(
        self, phases: List[EvolutionPhase], events: List[Event]
    ) -> List[EvolutionPhase]:
        """Walk the phase list and stamp each with how it *started*
        relative to the previous one. The first phase is `initial`;
        subsequent phases earn one of:

          • `resumption` — followed a >= big-gap inactivity window
          • `revisit`    — revisit score above threshold
          • `acceleration` — momentum doubled vs prev phase
          • `pivot`      — different dominant surface
          • `continuation` — none of the above
        """
        if not phases:
            return phases

        gap_threshold = _adaptive_gap_threshold(events)

        for i, p in enumerate(phases):
            if i == 0:
                p.transition = "initial"
                p.why = _explain_phase(
                    phase=p, prev=None, gap_threshold=gap_threshold
                )
                continue
            prev = phases[i - 1]
            gap_before = p.start_at - prev.end_at

            if gap_before > gap_threshold * _BIG_GAP_MULTIPLIER:
                if p.revisit_score >= _REVISIT_FRACTION:
                    p.transition = "revisit"
                else:
                    p.transition = "resumption"
            elif p.revisit_score >= _REVISIT_FRACTION:
                p.transition = "revisit"
            elif (
                p.momentum_score >= 0.4
                and p.momentum_score >= prev.momentum_score * 2.0
            ):
                p.transition = "acceleration"
            elif p.dominant_surface != prev.dominant_surface:
                p.transition = "pivot"
            else:
                p.transition = "continuation"

            p.why = _explain_phase(
                phase=p, prev=prev, gap_threshold=gap_threshold
            )

        return phases


# --------------------------------------------------------------- helpers


def _adaptive_gap_threshold(events: List[Event]) -> float:
    """Gap threshold for boundary detection. Floor: 24 hours.
    Otherwise: 6× the median inter-event interval, so daily-cadence
    threads have wider phase boundaries than hourly-cadence ones."""
    if len(events) < 3:
        return _GAP_FLOOR_SECONDS
    intervals: list[float] = []
    for i in range(1, len(events)):
        gap = events[i].ts_epoch() - events[i - 1].ts_epoch()
        if gap > 0:
            intervals.append(gap)
    if not intervals:
        return _GAP_FLOOR_SECONDS
    intervals.sort()
    median = intervals[len(intervals) // 2]
    return max(_GAP_FLOOR_SECONDS, median * _GAP_MEDIAN_MULTIPLIER)


def _surface_shift(events: List[Event], i: int) -> bool:
    """The dominant kind in events[i-W:i] differs from events[i:i+W]."""
    before = Counter(
        ev.kind for ev in events[max(0, i - _SHIFT_WINDOW):i]
    )
    after = Counter(
        ev.kind for ev in events[i:min(len(events), i + _SHIFT_WINDOW)]
    )
    if not before or not after:
        return False
    return before.most_common(1)[0][0] != after.most_common(1)[0][0]


def _vocabulary_shift(events: List[Event], i: int) -> bool:
    """Jaccard similarity of rolling-window content tokens drops
    below the configured threshold. Cheap; uses the existing
    `_content_tokens` extractor so the vocabulary aligns with every
    other layer."""
    before_tokens: set[str] = set()
    for ev in events[max(0, i - _SHIFT_WINDOW):i]:
        before_tokens.update(_event_tokens(ev))
    after_tokens: set[str] = set()
    for ev in events[i:min(len(events), i + _SHIFT_WINDOW)]:
        after_tokens.update(_event_tokens(ev))
    if not before_tokens or not after_tokens:
        return False
    inter = before_tokens & after_tokens
    union = before_tokens | after_tokens
    jaccard = len(inter) / max(1, len(union))
    return jaccard < _VOCAB_JACCARD_THRESHOLD


def _event_tokens(ev: Event) -> List[str]:
    """Top content tokens for a single event. Capped at 5 to keep
    the rolling-window comparison bounded."""
    payload = ev.payload or {}
    text = ""
    for fld in ("title", "query", "text"):
        v = (payload.get(fld) or "").strip()
        if v:
            text = v
            break
    if not text:
        return []
    return _content_tokens(text)[:5]


def _event_target_key(ev: Event) -> Optional[Tuple[str, str]]:
    """Stable (kind, target) identity for revisit detection. URLs
    and paths only — everything else (raw queries, chat-session
    sessionless events) can't be a revisit target."""
    payload = ev.payload or {}
    url = (payload.get("url") or "").strip().lower()
    path = (payload.get("path") or "").strip().lower()
    if url:
        return ("url", url)
    if path:
        return ("path", path)
    return None


def _phase_title(
    dominant_surface: str,
    slice_events: List[Event],
    revisit_score: float,
) -> str:
    """Pick a calm, factual phase title from the slice's dominant
    surface. A high revisit score overrides the surface label to
    "Revisit" — that's the user-mental-model name for the case
    where they came back to a topic.

    Heuristic adjustments:
      - Mixing browser_visit + browser_search reads as "Research".
      - High momentum on `open` reads as "Implementation".
      - High momentum on a single domain reads as "Iteration".
    """
    if revisit_score >= _REVISIT_FRACTION:
        return "Revisit"

    kinds = Counter(ev.kind for ev in slice_events)

    # browser_visit alongside browser_search → research
    if (
        kinds.get("browser_visit", 0) >= 2
        and kinds.get("browser_search", 0) >= 1
    ):
        return "Research"

    # repeated revisits to the same domain across opens / visits
    domain_counts: Counter = Counter()
    for ev in slice_events:
        d = (ev.payload or {}).get("domain", "")
        if isinstance(d, str) and d:
            domain_counts[d.lower()] += 1
    if domain_counts and domain_counts.most_common(1)[0][1] >= 4:
        if dominant_surface == "open" or dominant_surface == "reveal":
            return "Iteration"

    return _SURFACE_TITLES.get(dominant_surface, "Activity")


def _representative_queries(events: List[Event]) -> List[str]:
    """Distinct user-typed strings tied to a phase. Newest-first."""
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


def _representative_targets(events: List[Event]) -> List[Tuple[str, str]]:
    """Distinct openable targets, newest-first. Matches the threads
    layer's shape so the launcher row widget reuses straight."""
    seen: set[str] = set()
    out: list[Tuple[str, str]] = []
    for ev in reversed(events):
        payload = ev.payload or {}
        url = (payload.get("url") or "").strip()
        path = (payload.get("path") or "").strip()
        target = url or path
        if not target:
            continue
        k = target.lower()
        if k in seen:
            continue
        seen.add(k)
        out.append(("url" if url else "path", target))
        if len(out) >= _REPRESENTATIVE_TARGETS:
            break
    return out


def _explain_phase(
    phase: EvolutionPhase,
    prev: Optional[EvolutionPhase],
    gap_threshold: float,
) -> List[str]:
    """Plain-English reasons rendered in the debug overlay. Each
    line is observational — we describe what we saw, never
    speculate."""
    lines: list[str] = []
    if prev is None:
        lines.append("first phase observed in the thread")
    else:
        gap_before = phase.start_at - prev.end_at
        if gap_before > gap_threshold * _BIG_GAP_MULTIPLIER:
            days = round(gap_before / 86400.0, 1)
            lines.append(f"long gap before this phase ({days} days idle)")
        if phase.dominant_surface != prev.dominant_surface:
            lines.append(
                f"dominant surface shifted: {prev.dominant_surface} → {phase.dominant_surface}"
            )
        if phase.momentum_score >= 0.4 and phase.momentum_score >= prev.momentum_score * 2.0:
            lines.append("momentum more than doubled vs previous phase")
    if phase.revisit_score >= _REVISIT_FRACTION:
        lines.append(
            f"{int(phase.revisit_score * 100)}% of targets appeared earlier in the thread"
        )
    lines.append(f"{phase.event_count} events  ·  {humanize_age(phase.end_at)}")
    return lines


# --------------------------------------------------------------- cache helpers


def _fingerprint(events: List[Event]) -> str:
    """Deterministic fingerprint of an event list. Two pieces of
    info uniquely identify a thread's evolution state: how many
    events it has, and when the last one fired. Anything else
    (titles, surfaces) is downstream of those two and is rebuilt
    on cache miss."""
    n = len(events)
    last_ts = events[-1].ts if events else ""
    raw = f"{n}|{last_ts}"
    return hashlib.sha1(raw.encode("utf-8")).hexdigest()[:12]


def _phase_id(thread_id: str, slot: int, start_ts: float) -> str:
    """Stable per-phase id; same input → same output. Used so a
    cached evolution round-trips byte-for-byte through the store."""
    raw = f"{thread_id}|{slot}|{int(start_ts)}"
    return "ph_" + hashlib.sha1(raw.encode("utf-8")).hexdigest()[:8]


# --------------------------------------------------------------- serialization


def _serialize(evo: ThreadEvolution) -> dict:
    """Convert to a JSON-safe dict for the on-disk cache."""
    return {
        "thread_id": evo.thread_id,
        "span_start": evo.span_start,
        "span_end": evo.span_end,
        "phases": [
            {
                **asdict(p),
                # asdict() preserves tuple-of-tuples, which json
                # can serialize as a nested list. Decoder
                # re-tuples them.
            }
            for p in evo.phases
        ],
    }


def _deserialize(payload: dict) -> ThreadEvolution:
    phases: list[EvolutionPhase] = []
    for row in payload.get("phases") or []:
        targets_raw = row.get("representative_targets") or []
        targets: list[Tuple[str, str]] = []
        for t in targets_raw:
            if isinstance(t, (list, tuple)) and len(t) == 2:
                targets.append((str(t[0]), str(t[1])))
        phases.append(EvolutionPhase(
            id=row.get("id", ""),
            thread_id=row.get("thread_id", ""),
            title=row.get("title", ""),
            start_at=float(row.get("start_at") or 0.0),
            end_at=float(row.get("end_at") or 0.0),
            event_count=int(row.get("event_count") or 0),
            dominant_surface=row.get("dominant_surface", ""),
            representative_queries=list(row.get("representative_queries") or []),
            representative_targets=targets,
            momentum_score=float(row.get("momentum_score") or 0.0),
            revisit_score=float(row.get("revisit_score") or 0.0),
            transition=row.get("transition", "initial"),
            signals=dict(row.get("signals") or {}),
            why=list(row.get("why") or []),
        ))
    return ThreadEvolution(
        thread_id=payload.get("thread_id", ""),
        phases=phases,
        span_start=float(payload.get("span_start") or 0.0),
        span_end=float(payload.get("span_end") or 0.0),
    )
