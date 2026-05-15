"""Continuity recovery — Phase 3B.

The first truly user-magical layer. Threads (Phase 2C) and evolution
(Phase 3A) describe *what* the user has been doing. Recovery answers
*"what should I open right now to keep going?"*

Recovery is **not** retrieval, **not** recommendation, **not**
search. It is the minimum coherent context the user needs to re-
enter unfinished work. Three candidates, max — fewer is better.

This file is the next abstraction layer on top of:

    events     →  raw capture                    (Phase 1A)
    sessions   →  30-min temporal groupings      (Phase 1E)
    contexts   →  topic-coherent sub-blocks      (Phase 1F)
    resurfacing→  query-time idle surfacing      (Phase 2B)
    threads    →  persistent topic identity      (Phase 2C)
    evolution  →  chronological phases           (Phase 3A)
    recovery   →  resumable work + one-click     (Phase 3B, this file)

Design rules:

  1. **Deterministic.** Same events in → same candidates out. No
     LLM, no embeddings, no probabilistic ranking.
  2. **Additive.** Composes on top of threads + evolution. Disabling
     recovery leaves every other layer untouched.
  3. **Conservative.** Max three candidates. A user staring at five
     things isn't being helped; they're being noised. The "max 3"
     ceiling is part of the API contract, enforced by the engine.
  4. **One-click.** A candidate carries `suggested_targets` — every
     URL or file path the user should reopen to restore context.
     The launcher iterates this list and hands each target to the
     OS. The engine does not pick "best", it picks "complete".
  5. **<80 ms** total path cost on a 10K-event log, p50.
"""

from __future__ import annotations

import hashlib
import logging
import math
import time
from collections import Counter
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

from .events import Event, EventStore, humanize_age
from .evolution import EvolutionBuilder, EvolutionPhase, ThreadEvolution
from .threads import Thread, ThreadBuilder

log = logging.getLogger("recall.core.recovery")


# --------------------------------------------------------------- tunables


# Hard ceiling. Brief is explicit: max 3. A list of recoverable work
# wider than three is no longer "the next thing to do", it's "an
# inbox" — which the brief equally explicitly forbids.
_MAX_CANDIDATES: int = 3

# Candidate pool before ranking. We look at the top-N threads from
# the threads layer and score each; the cap below `_MAX_CANDIDATES`
# trims down. Six is the smallest pool that lets the ranking
# heuristic actually express a preference.
_CANDIDATE_POOL: int = 6

# A thread whose last event is older than this is not "interrupted",
# it's "set aside". Surface it via resurfacing, not recovery.
_RECOVERY_WINDOW_DAYS: int = 14

# Minimum total events in the thread. Anything below this is too
# thin to call "work the user was doing".
_MIN_EVENTS: int = 4

# Minimum recovery confidence — below this the candidate is
# suppressed entirely. Phase 3C raised this from 0.40 → 0.45;
# Phase 4C raised again to 0.50 as part of the *fewer, stronger
# recoveries* sharpness pass. The smoke fixture sits at conf
# ≈ 0.74, well clear of the new floor; in real-world data the
# extra 0.05 separates "I'm reading about this" (sub-0.50) from
# "I was in the middle of this" (above 0.50).
_MIN_CONFIDENCE: float = 0.50

# Phase 4C — last-phase recency guard. The thread's
# `updated_at` (which gates the 14-day window above) is the
# timestamp of the *latest* event, which can be a stray browser
# visit that doesn't represent real engagement. The *last
# evolution phase's* `end_at` is the timestamp of the most
# recent **coherent block of work** on the topic, which is what
# "still in flow" actually means. If the last phase ended more
# than this many days ago, the topic isn't recoverable —
# resurfacing can still catch it as "on your radar".
_LAST_PHASE_RECENCY_DAYS: float = 10.0

# Phase 3C: substantive-engagement floor. A topic that consists
# entirely of `browser_visit` events with no `open`, `reveal`, or
# `chat_session` activity is passive consumption (reading) rather
# than active work. We surface it via resurfacing, never via
# recovery. The depth-event kinds below are the ones that imply
# the user *did* something with what they read.
_DEPTH_KINDS: frozenset[str] = frozenset({
    "open",
    "reveal",
    "chat_session",
    "browser_search",
})

# Phase 3C: minimum distinct targets. A thread whose entire
# activity is "the user reopened the same URL six times" reads as
# "stuck on one page", not "in the middle of multi-source work".
# Two distinct targets is the smallest pool that implies a
# *context* rather than a single reference.
_MIN_DISTINCT_TARGETS: int = 2

# How many representative events to surface per candidate. Three is
# the sweet spot: enough to feel like a context, not enough to read
# as a log dump.
_REPRESENTATIVE_EVENTS: int = 3

# How many one-click targets to surface. The user should rarely
# reopen more than this many tabs/files at once.
_MAX_TARGETS: int = 8


# Continuity-score weights. Each component lives in [0, 1] before
# weighting; weights sum to ~1.0 so the final score also lands in
# [0, 1] without clamping. Re-tunable in one place.
_W_RECENCY:        float = 0.30  # how fresh the abandonment is
_W_TARGET_REUSE:   float = 0.25  # do targets recur within the thread
_W_SURFACE_BREADTH: float = 0.15 # browser + files + chat = richer context
_W_DENSITY:        float = 0.15  # events / active hours
_W_LAST_MOMENTUM:  float = 0.15  # was the user mid-flow when they stopped


# Recovery-confidence weights — separate scoring system that decides
# *whether* this is something the user wants to resume, vs whether
# the context is *intact*. (You can have an intact context that the
# user is done with; or a fragmentary context that they desperately
# want back.)
_C_ABANDONMENT:    float = 0.35  # abrupt drop in momentum
_C_REVISIT:        float = 0.30  # revisit transition in the last phase
_C_ACCELERATION:   float = 0.20  # last phase was an acceleration
_C_UNRESOLVED:     float = 0.15  # repeated opens / repeated searches


# Recency half-life — sharper than the threads layer's half-life
# because recovery cares about *recent* abandonment.
_RECENCY_HALFLIFE_DAYS: float = 3.5


# --------------------------------------------------------------- model


@dataclass
class RecoveryCandidate:
    """One recovery card.

    `continuity_score` is *how intact* the resume context is.
    `recovery_confidence` is *how likely* the user wants to resume.
    They're scored independently; the rank uses the higher of the
    two but the wire format ships both for transparency.

    `preview_caption` (Phase 3C) is a deterministic one-liner the
    launcher displays under the title. *No AI prose, no LLM
    summary* — the caption is built from the same surface counts
    plus the last evolution phase name. Same data in → same
    caption out, every time.
    """

    id: str
    thread_id: str
    title: str
    last_active_at: float
    continuity_score: float
    recovery_confidence: float
    representative_events: List[Event] = field(default_factory=list)
    suggested_targets: List[Tuple[str, str]] = field(default_factory=list)
    related_sessions: List[str] = field(default_factory=list)
    related_contexts: int = 0
    unresolved_signals: List[str] = field(default_factory=list)
    signals: Dict[str, float] = field(default_factory=dict)
    why: List[str] = field(default_factory=list)

    # Phase 3C additions —
    preview_caption: str = ""
    last_phase_title: str = ""
    last_phase_transition: str = ""


@dataclass
class RestorationStep:
    """One step in an orchestrated restoration plan. Carries the
    target plus a deterministic `reason` explaining its position
    in the sequence ("file · grounds the work", "chat · informs
    the context", …). The launcher renders these in the debug
    overlay when `RECALL_EXPLAIN_RECOVERY=1`."""

    kind: str           # "url" | "path"
    target: str
    group: str          # "files" | "chats" | "tabs" | "searches"
    reason: str


@dataclass
class RestorationPlan:
    """The orchestrated sequence the launcher follows when
    restoring a candidate. Ordered by group (files first, then
    chats, then tabs, then searches) so the user re-enters the
    mental room in a stable sequence. Within a group, targets
    are ordered newest-first to preserve recency.

    The plan is *purely advisory*. The launcher may diverge under
    OS constraints; the perf-tracked `RestorationResult` records
    what actually happened.
    """

    candidate_id: str
    thread_id: str
    title: str
    preview_caption: str
    steps: List[RestorationStep] = field(default_factory=list)


@dataclass
class RestorationResult:
    """The launcher's tally of one restoration. Used for the
    acknowledgement footer ('Restored 4 of 5'), the debug
    overlay, and nothing else — there is no telemetry channel.
    """

    candidate_id: str
    title: str
    requested: int = 0
    restored: int = 0
    skipped: List[Tuple[str, str, str]] = field(default_factory=list)
    elapsed_ms: float = 0.0


# --------------------------------------------------------------- engine


class RecoveryEngine:
    """Heuristic, deterministic recovery-state reconstructor.

    Reads from the event store and reuses the threads + evolution
    builders. Holds no mutable state of its own; safe to call from
    any thread. Cache state lives on the event store and the threads
    cache, so a recovery call shortly after a search pays nothing
    for parsing.
    """

    def __init__(
        self,
        event_store: EventStore,
        thread_builder: Optional[ThreadBuilder] = None,
        evolution_builder: Optional[EvolutionBuilder] = None,
    ) -> None:
        self.event_store = event_store
        self.thread_builder = thread_builder or ThreadBuilder(event_store)
        self.evolution_builder = evolution_builder or EvolutionBuilder(
            event_store, thread_builder=self.thread_builder
        )

    # -- public ----------------------------------------------------------

    def recover_recent(
        self, n: int = _MAX_CANDIDATES, now: Optional[float] = None
    ) -> List[RecoveryCandidate]:
        """Return up to `n` recovery candidates, ranked by the higher
        of `continuity_score` and `recovery_confidence`.

        The cap is non-negotiable: `n` is clamped to
        `[0, _MAX_CANDIDATES]`. A caller asking for 20 gets 3."""
        n = max(0, min(n, _MAX_CANDIDATES))
        if n == 0:
            return []
        if now is None:
            now = time.time()

        threads = self.thread_builder.rebuild(now=now)
        if not threads:
            return []

        # Score the top-N threads. We can't score *every* thread —
        # the evolution build per thread is the heaviest sub-cost.
        # The threads layer already ranks by confidence, so the
        # top-K is the right candidate pool.
        candidates: list[RecoveryCandidate] = []
        for thread in threads[:_CANDIDATE_POOL]:
            cand = self._score_thread(thread, now)
            if cand is None:
                continue
            candidates.append(cand)

        # Rank by `max(continuity, confidence)`. Higher = more
        # urgent to surface.
        candidates.sort(
            key=lambda c: max(c.continuity_score, c.recovery_confidence),
            reverse=True,
        )
        return candidates[:n]

    def candidate_for_thread(
        self, thread_id: str, now: Optional[float] = None
    ) -> Optional[RecoveryCandidate]:
        """Resolve a single candidate by `thread_id`. Used by the
        one-click restore endpoint to confirm the candidate is still
        valid before the launcher opens its targets."""
        if now is None:
            now = time.time()
        threads = self.thread_builder.rebuild(now=now)
        for thread in threads:
            if thread.id == thread_id:
                return self._score_thread(thread, now)
        return None

    # -- per-thread scoring ---------------------------------------------

    def _score_thread(
        self, thread: Thread, now: float
    ) -> Optional[RecoveryCandidate]:
        """Compute both scores + assemble the candidate. Returns
        `None` if the thread fails an anti-noise filter."""
        if thread.event_count < _MIN_EVENTS:
            return None

        age_days = max(0.0, (now - thread.updated_at) / 86400.0)
        if age_days > _RECOVERY_WINDOW_DAYS:
            return None

        # Pull evolution. The evolution builder shares its cache
        # with subsequent calls and is fast on warm event-store
        # caches; the per-thread cost is dominated by the topic
        # filter, which threads.rebuild has already done once.
        evo = self.evolution_builder.build(thread)
        if not evo.phases:
            return None

        last_phase = evo.phases[-1]

        # Phase 4C — last-phase recency guard. The thread's
        # `updated_at` may be a stray browser visit; the last
        # evolution phase's `end_at` is the last coherent block
        # of work. If that's stale, the topic belongs in
        # resurfacing ("on your radar"), not recovery.
        last_phase_age_days = max(
            0.0, (now - last_phase.end_at) / 86400.0
        )
        if last_phase_age_days > _LAST_PHASE_RECENCY_DAYS:
            return None

        events = self._collect_thread_events(thread.topic_key)
        if len(events) < _MIN_EVENTS:
            return None

        surfaces = {ev.kind for ev in events if ev.kind}
        if len(surfaces) < 2 and len(events) < 6:
            # Single-surface, low-density activity isn't a thread
            # the user "was doing work in" — it's a passive read.
            return None

        # Phase 3C: depth filter. A thread of pure browser visits
        # is reading material; recovery should surface work the
        # user *acted on* — file opens, chat sessions, or active
        # searches. The resurfacing layer catches the rest.
        depth_events = sum(1 for ev in events if ev.kind in _DEPTH_KINDS)
        if depth_events == 0:
            return None

        # Phase 3C: distinct-target floor. A thread of "the user
        # reopened the same URL six times" is stuck, not
        # interrupted. At least two distinct openable targets are
        # required for the candidate to read as a multi-source
        # context worth restoring.
        distinct_targets = {
            ((ev.payload or {}).get("url") or (ev.payload or {}).get("path") or "").strip().lower()
            for ev in events
        }
        distinct_targets.discard("")
        if len(distinct_targets) < _MIN_DISTINCT_TARGETS:
            return None

        # ── continuity_score: is the context intact? ──
        s_recency = math.pow(0.5, age_days / _RECENCY_HALFLIFE_DAYS)
        s_targets = self._target_reuse_score(events)
        s_surface = min(1.0, (len(surfaces) - 1) / 3.0)
        s_density = self._density_score(events, now)
        s_lastmom = float(last_phase.momentum_score)

        continuity = (
            _W_RECENCY            * s_recency
            + _W_TARGET_REUSE     * s_targets
            + _W_SURFACE_BREADTH  * s_surface
            + _W_DENSITY          * s_density
            + _W_LAST_MOMENTUM    * s_lastmom
        )
        continuity = round(min(1.0, continuity), 4)

        # ── recovery_confidence: does the user want to resume? ──
        abandonment = self._abandonment_score(evo, now)
        revisit = 1.0 if last_phase.transition == "revisit" else (
            0.5 if last_phase.transition == "resumption" else 0.0
        )
        acceleration = 1.0 if last_phase.transition == "acceleration" else 0.0
        unresolved = self._unresolved_score(events)

        confidence = (
            _C_ABANDONMENT  * abandonment
            + _C_REVISIT    * revisit
            + _C_ACCELERATION * acceleration
            + _C_UNRESOLVED * unresolved
        )
        confidence = round(min(1.0, confidence), 4)

        # Confidence floor. Trivial / completed work fails here.
        if max(continuity, confidence) < _MIN_CONFIDENCE:
            return None

        # ── assemble the candidate ──
        rep_events = self._representative_events(events)
        targets = self._suggested_targets(events)
        if not targets:
            # Nothing to one-click. Suppress the candidate — the
            # surface only earns its weight when there's something
            # to restore.
            return None

        sessions = self._related_session_ids(events)
        unresolved_signals = self._unresolved_signal_lines(
            events, evo, abandonment, unresolved
        )

        signals = {
            "recency":            round(s_recency, 3),
            "target_reuse":       round(s_targets, 3),
            "surface_breadth":    round(s_surface, 3),
            "density":            round(s_density, 3),
            "last_momentum":      round(s_lastmom, 3),
            "abandonment":        round(abandonment, 3),
            "revisit":            round(revisit, 3),
            "acceleration":       round(acceleration, 3),
            "unresolved_pattern": round(unresolved, 3),
        }

        why = self._explain(
            thread=thread,
            last_phase=last_phase,
            n_events=len(events),
            n_surfaces=len(surfaces),
            abandonment=abandonment,
            now=now,
        )

        cand_id = _candidate_id(thread.id, thread.updated_at)

        # Phase 3C — deterministic preview caption built from
        # surface counts + last phase. No AI prose; same inputs
        # always produce the same caption.
        preview = self._preview_caption(targets, last_phase)

        return RecoveryCandidate(
            id=cand_id,
            thread_id=thread.id,
            title=thread.title,
            last_active_at=thread.updated_at,
            continuity_score=continuity,
            recovery_confidence=confidence,
            representative_events=rep_events,
            suggested_targets=targets,
            related_sessions=sessions,
            related_contexts=0,  # the threads layer doesn't surface
                                  # contexts; left as a placeholder
                                  # for the field-contract API.
            unresolved_signals=unresolved_signals,
            signals=signals,
            why=why,
            preview_caption=preview,
            last_phase_title=last_phase.title,
            last_phase_transition=last_phase.transition,
        )

    # -- inputs ---------------------------------------------------------

    def _collect_thread_events(self, topic_key: str) -> List[Event]:
        """Reuse the thread builder's canonical-topic-key lookup
        so the filter stays in one place. Returns chronologically
        sorted events for the topic across the recovery window."""
        out: list[Event] = []
        for ev in self.event_store.iter_events(days=_RECOVERY_WINDOW_DAYS):
            if self.thread_builder._thread_key(ev) == topic_key:
                out.append(ev)
        out.sort(key=lambda e: e.ts_epoch())
        return out

    # -- component scores -----------------------------------------------

    @staticmethod
    def _target_reuse_score(events: List[Event]) -> float:
        """How concentrated is the thread's attention?

        We count distinct (kind, target) keys and the most-frequent
        one's occurrence. Heavy reuse of a small target set = the
        user kept opening the same things = high recovery value.
        """
        counter: Counter = Counter()
        for ev in events:
            payload = ev.payload or {}
            target = (payload.get("url") or payload.get("path") or "").strip().lower()
            if not target:
                continue
            counter[target] += 1
        if not counter:
            return 0.0
        # The top target's count, divided by an "interesting"
        # threshold of 4 hits. Saturates at 1.0.
        top_n = counter.most_common(1)[0][1]
        return min(1.0, top_n / 4.0)

    @staticmethod
    def _density_score(events: List[Event], now: float) -> float:
        """Events per active hour across the *recent* tail of the
        thread (last 48 h). High recent density = the user was deep
        in flow; low recent density = the thread was already
        winding down."""
        cutoff = now - 48 * 3600
        recent = [ev for ev in events if ev.ts_epoch() >= cutoff]
        if not recent:
            return 0.0
        first = recent[0].ts_epoch()
        last = recent[-1].ts_epoch()
        span_hours = max(0.5, (last - first) / 3600.0)
        rate = len(recent) / span_hours
        # Saturate at 3 events per hour.
        return min(1.0, rate / 3.0)

    @staticmethod
    def _abandonment_score(evo: ThreadEvolution, now: float) -> float:
        """Did the thread end with a drop in momentum?

        Two ingredients:
          • the last phase carried real momentum (>= 0.4), AND
          • activity stopped some time ago (gap > 6 h, < 7 d).

        The combination is the signal: the user was mid-flow and
        then stopped abruptly. That's the moment recovery is most
        useful — the context is still in their head, almost.
        """
        if not evo.phases:
            return 0.0
        last = evo.phases[-1]
        if last.momentum_score < 0.4:
            return 0.0
        age_hours = max(0.0, (now - last.end_at) / 3600.0)
        if age_hours < 6.0:
            # Still in flow; not abandoned.
            return 0.0
        if age_hours > 168.0:
            # A week+ idle is "set aside", not "interrupted".
            return 0.0
        # Score peaks around the 24 h mark — the most recoverable
        # gap is overnight + the next day.
        if age_hours <= 24.0:
            return last.momentum_score
        # Linear taper from 24 h → 168 h.
        return last.momentum_score * (1.0 - (age_hours - 24.0) / 144.0)

    @staticmethod
    def _unresolved_score(events: List[Event]) -> float:
        """Look for the pattern of *repeated* opens / searches —
        the user kept coming back to the same things without
        apparent resolution.

        Two signals contribute:
          • a single target opened ≥ 3 times
          • a single search query repeated ≥ 2 times

        The two are summed and capped at 1.0.
        """
        target_counts: Counter = Counter()
        search_counts: Counter = Counter()
        for ev in events:
            payload = ev.payload or {}
            target = (payload.get("url") or payload.get("path") or "").strip().lower()
            if target and ev.kind in ("open", "reveal", "browser_visit"):
                target_counts[target] += 1
            if ev.kind == "browser_search":
                q = (payload.get("query") or "").strip().lower()
                if q:
                    search_counts[q] += 1
            elif ev.kind == "query":
                t = (payload.get("text") or "").strip().lower()
                if t:
                    search_counts[t] += 1
        score = 0.0
        if target_counts:
            top = target_counts.most_common(1)[0][1]
            if top >= 3:
                score += min(0.6, (top - 2) * 0.2)
        if search_counts:
            top = search_counts.most_common(1)[0][1]
            if top >= 2:
                score += min(0.4, (top - 1) * 0.2)
        return min(1.0, score)

    # -- assembly --------------------------------------------------------

    @staticmethod
    def _representative_events(events: List[Event]) -> List[Event]:
        """Newest-first events, deduped by target. Three rows is
        the right amount for the launcher card — enough context, not
        a feed."""
        seen: set[str] = set()
        out: list[Event] = []
        for ev in reversed(events):
            payload = ev.payload or {}
            target = (payload.get("url") or payload.get("path") or "").strip().lower()
            key = target or f"{ev.ts}:{ev.kind}"
            if key in seen:
                continue
            seen.add(key)
            out.append(ev)
            if len(out) >= _REPRESENTATIVE_EVENTS:
                break
        return out

    @staticmethod
    def _suggested_targets(events: List[Event]) -> List[Tuple[str, str]]:
        """The one-click open list. Newest-first, deduped, capped.

        We weight by recency *and* repetition — a target that was
        both recently touched *and* repeatedly touched is the most
        important thing to reopen. The implementation is the
        natural one: newest-first traversal, drop duplicates.
        """
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
            if len(out) >= _MAX_TARGETS:
                break
        return out

    # -- preview + orchestration (Phase 3C) ----------------------------

    @staticmethod
    def _preview_caption(
        targets: List[Tuple[str, str]],
        last_phase,
    ) -> str:
        """Deterministic one-liner for the launcher's recovery row.

        Format examples:
            "3 tabs · 2 files · 1 chat · last active during implementation"
            "4 tabs · last active during research"
            "2 files · 1 chat · last active during discussion"

        The caption is built entirely from the candidate's own
        data — same inputs, same string, every time. No prose
        generation, no model, no LLM. The phase suffix names the
        last evolution phase the user lived through; it's the
        signal closest to "what state of mind were you in?"
        without inventing one.
        """
        groups = _classify_targets(targets)
        parts: list[str] = []
        if groups["tabs"]:
            n = len(groups["tabs"])
            parts.append(f"{n} tab{'s' if n != 1 else ''}")
        if groups["files"]:
            n = len(groups["files"])
            parts.append(f"{n} file{'s' if n != 1 else ''}")
        if groups["chats"]:
            n = len(groups["chats"])
            parts.append(f"{n} chat{'s' if n != 1 else ''}")
        # Phase suffix — anchored on the *title* of the last phase
        # which is itself already produced by the evolution layer's
        # deterministic title heuristic.
        if last_phase and last_phase.title:
            phase_word = last_phase.title.lower()
            # Some phase titles read naturally ("during implementation");
            # `Revisit` is a transition state better phrased as
            # "after a revisit", and `Looking up` is too generic.
            if phase_word == "revisit":
                parts.append("after a revisit")
            elif phase_word == "activity":
                pass
            elif phase_word == "looking up":
                parts.append("after a launcher search")
            else:
                parts.append(f"last active during {phase_word}")
        return "  ·  ".join(parts) if parts else ""

    def plan_for(
        self, candidate: RecoveryCandidate
    ) -> RestorationPlan:
        """Build the orchestrated restoration sequence for one
        candidate. Ordering rules, deterministic:

          1. Files first — they ground the work in the user's
             local artifacts. Open one before reopening the web
             is the most "where am I?" answer there is.
          2. Chats next — the conversation that informed the
             work. Reading the chat after the file gives the user
             "what was I asking?" context.
          3. Browser tabs by domain, newest-first within each
             domain — same-domain pages cluster together so the
             browser presents them as related.
          4. Repeated searches last (rendered as URLs to the
             results page).

        Each step carries a `reason` the debug overlay renders
        when `RECALL_EXPLAIN_RECOVERY=1` is set.
        """
        groups = _classify_targets(candidate.suggested_targets)

        steps: list[RestorationStep] = []
        for kind, target in groups["files"]:
            steps.append(RestorationStep(
                kind=kind, target=target,
                group="files",
                reason="grounds the work in your local artifacts",
            ))
        for kind, target in groups["chats"]:
            steps.append(RestorationStep(
                kind=kind, target=target,
                group="chats",
                reason="conversation that informed the work",
            ))
        for kind, target in groups["tabs"]:
            steps.append(RestorationStep(
                kind=kind, target=target,
                group="tabs",
                reason="reading material to re-anchor context",
            ))
        for kind, target in groups["searches"]:
            steps.append(RestorationStep(
                kind=kind, target=target,
                group="searches",
                reason="repeated search worth re-running",
            ))

        return RestorationPlan(
            candidate_id=candidate.id,
            thread_id=candidate.thread_id,
            title=candidate.title,
            preview_caption=candidate.preview_caption,
            steps=steps,
        )

    @staticmethod
    def _related_session_ids(events: List[Event]) -> List[str]:
        seen: set[str] = set()
        out: list[str] = []
        # Most recent session first.
        for ev in reversed(events):
            sid = ev.session_id
            if not sid or sid in seen:
                continue
            seen.add(sid)
            out.append(sid)
            if len(out) >= 4:
                break
        return out

    @staticmethod
    def _unresolved_signal_lines(
        events: List[Event],
        evo: ThreadEvolution,
        abandonment: float,
        unresolved: float,
    ) -> List[str]:
        """Human-readable bullets the launcher's debug overlay
        renders. Each one describes a concrete pattern we *saw*."""
        lines: list[str] = []
        # Repeated opens
        target_counts: Counter = Counter()
        for ev in events:
            payload = ev.payload or {}
            tgt = (payload.get("url") or payload.get("path") or "").strip().lower()
            if tgt:
                target_counts[tgt] += 1
        if target_counts:
            top_t, top_c = target_counts.most_common(1)[0]
            if top_c >= 3:
                lines.append(f"reopened the same target {top_c} times")
        # Repeated searches
        search_counts: Counter = Counter()
        for ev in events:
            payload = ev.payload or {}
            if ev.kind == "browser_search":
                q = (payload.get("query") or "").strip().lower()
            elif ev.kind == "query":
                q = (payload.get("text") or "").strip().lower()
            else:
                continue
            if q:
                search_counts[q] += 1
        if search_counts:
            top_q, top_c = search_counts.most_common(1)[0]
            if top_c >= 2:
                lines.append(f"searched for the same phrase {top_c} times")
        # Abandonment
        if abandonment > 0.3 and evo.phases:
            last = evo.phases[-1]
            lines.append(
                f"last phase ({last.title}) had momentum {last.momentum_score:.2f} "
                f"and then went quiet"
            )
        return lines

    @staticmethod
    def _explain(
        thread: Thread,
        last_phase: EvolutionPhase,
        n_events: int,
        n_surfaces: int,
        abandonment: float,
        now: float,
    ) -> List[str]:
        """Plain-English reasons rendered by the launcher's debug
        overlay. The same style as resurfacing/threads/evolution
        explanations — observational, never speculative."""
        lines: list[str] = []
        age = humanize_age(thread.updated_at, now=now)
        lines.append(f"last active {age}")
        if n_surfaces >= 2:
            lines.append(f"{n_surfaces} surfaces (browser/files/chat) in play")
        if abandonment > 0.4:
            lines.append("abandoned mid-flow — momentum was high")
        if last_phase.transition == "revisit":
            lines.append("last phase was a revisit (returned to old material)")
        elif last_phase.transition == "acceleration":
            lines.append("last phase was an acceleration (intensifying)")
        lines.append(f"{n_events} events in the thread")
        return lines


# --------------------------------------------------------------- helpers


_CHAT_HOSTS: tuple[str, ...] = (
    "claude.ai",
    "chat.openai.com",
    "chatgpt.com",
    "gemini.google.com",
    "perplexity.ai",
    "poe.com",
)


def _classify_targets(
    targets: List[Tuple[str, str]],
) -> Dict[str, List[Tuple[str, str]]]:
    """Group recovery targets by orchestration bucket.

    Buckets:
      • `files`     — `kind == "path"`
      • `chats`     — URL whose host matches `_CHAT_HOSTS`
      • `searches`  — URL whose host looks like a search engine
      • `tabs`      — everything else (the default URL bucket)

    Deterministic. Same inputs in, same buckets out.
    """
    files: list[Tuple[str, str]] = []
    chats: list[Tuple[str, str]] = []
    searches: list[Tuple[str, str]] = []
    tabs: list[Tuple[str, str]] = []
    for kind, target in targets:
        if kind == "path":
            files.append((kind, target))
            continue
        lowered = target.lower()
        if any(host in lowered for host in _CHAT_HOSTS):
            chats.append((kind, target))
        elif (
            "google.com/search" in lowered
            or "duckduckgo.com/?q=" in lowered
            or "bing.com/search" in lowered
            or "kagi.com/search" in lowered
        ):
            searches.append((kind, target))
        else:
            tabs.append((kind, target))
    return {
        "files": files,
        "chats": chats,
        "tabs": tabs,
        "searches": searches,
    }


def _candidate_id(thread_id: str, last_active_at: float) -> str:
    """Deterministic candidate id. Stable across rebuilds within the
    same active-day; a new event in the thread changes the last-
    active timestamp and therefore the id. This is intentional — a
    candidate is *this* recovery state, not just *this* thread."""
    day = int(last_active_at // 86400)
    raw = f"{thread_id}|{day}"
    return "rc_" + hashlib.sha1(raw.encode("utf-8")).hexdigest()[:10]
