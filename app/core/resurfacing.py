"""Passive resurfacing — Phase 2B.

Surfaces unfinished thinking when the launcher idles with no query.
This is *not* a recommendation feed, *not* social discovery, and *not*
AI summarization. It is lightweight cognitive continuity: a quiet
"continue where you left off" lane in the digest.

Design constraints, written down so they don't drift:

  1. No embeddings, no LLM, no network. Topics are derived from the
     same `_content_tokens` extractor the rest of the engine uses.
  2. No notifications, no badges, no dopamine mechanics. The output is
     a small ranked list — at most 4 items — that disappears the moment
     the user starts typing.
  3. Anti-noise is opinionated. A single accidental open is *not*
     unfinished work; a single-session burst is *not* resurfacing
     material. The signal is "this topic touched the user across days /
     sessions / revisits".
  4. Local state only. The history file lives at
     `~/.recall/resurfacing.json` and stores nothing but topic keys and
     surfacing counters. "Clear resurfacing history" is one
     `os.remove()`.
  5. <25 ms generation on a 10K-event log. The engine reuses the
     `EventStore` parse cache and the `searchable_text` cache; the
     per-topic bookkeeping is one Python dict pass over events.

The ranking is a transparent weighted sum of seven heuristic signals —
no learned weights, no opaque thresholds. Each contributing signal is
recorded on the `ResurfacedContext.signals` dict so the
"Why am I seeing this?" debug hover can reveal it without inventing
post-hoc explanations.
"""

from __future__ import annotations

import json
import logging
import math
import threading
import time
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from .config import CONFIG_DIR
from .episodic import _content_tokens
from .events import Event, EventStore, humanize_age

log = logging.getLogger("recall.core.resurfacing")


# --------------------------------------------------------------- kinds


# Only event kinds that represent intentional engagement count toward
# resurfacing. `query` events (launcher searches) are recorded as
# *repeated-search* signal but never form a topic of their own — a
# user looking for X doesn't mean X is unfinished, it means they're
# already on it.
_RESURFACEABLE_KINDS: frozenset[str] = frozenset({
    "browser_visit",
    "browser_search",
    "chat_session",
    "open",
})


# --------------------------------------------------------------- tunables


# Hard ceiling. The brief is non-negotiable: max four items.
_MAX_RESURFACED_ITEMS: int = 4

# How far back to look. Beyond two weeks the topic is "forgotten",
# not "unfinished".
_LOOKBACK_DAYS: int = 14

# An item with fewer than this many distinct events is trivial.
# Two events on the same topic across two sessions is the minimum
# threshold for "the user keeps coming back to this".
_MIN_EVENTS: int = 3

# Anything younger than this is too recent to call "unfinished" — it's
# what the user is doing *right now*, not what they need help
# reconnecting with.
_MIN_TOPIC_AGE_HOURS: float = 6.0

# Score weights. Each signal contributes [0..1] before weighting. The
# weights sum to ~1.0 by design so the final score also lands in
# roughly [0..1] without any clamping.
_W_RECENCY:           float = 0.18
_W_FREQUENCY:         float = 0.22
_W_SESSION_DIVERSITY: float = 0.18
_W_DAY_DIVERSITY:     float = 0.14
_W_URL_REVISITS:      float = 0.10
_W_REPEAT_SEARCH:     float = 0.10
_W_CONTEXT_SIZE:      float = 0.08

# Recency decay — half-life roughly aligned with the human "I was
# working on this last week" feeling. Sharper than the episodic
# retriever's 3.5 days because resurfacing already filters to events
# older than `_MIN_TOPIC_AGE_HOURS`.
_RECENCY_HALFLIFE_DAYS: float = 5.0

# Below this final score the topic is suppressed entirely. Two events
# from one session two weeks ago is technically a "topic" but it's
# noise; the threshold gives the engine room to say "nothing to
# resurface today" rather than fabricate a card.
_MIN_SCORE: float = 0.30


# Tokens that look like content but are actually so generic they
# would group unrelated events together. Kept short on purpose; this
# is in addition to the `_STOPWORDS` list `_content_tokens` already
# filters.
_GENERIC_TOPIC_TOKENS: frozenset[str] = frozenset({
    "github",     # every code repo would collapse together
    "docs",
    "home",
    "search",
    "results",
    "untitled",
    "google",
    "youtube",
    "stackoverflow",
    "wikipedia",
    "page",
    "site",
    "www",
    "html",
    "index",
})


# --------------------------------------------------------------- model


@dataclass
class ResurfacedContext:
    """One quiet "continue where you left off" card.

    `topic` is the bucket key; `label` is the human-friendly headline;
    `score` and `confidence` are both [0..1]. `signals` carries the raw
    per-signal contributions so the debug hover can show them without
    re-deriving anything. `events` is *not* the full bucket — only the
    last few, enough for the row to render a preview.
    """

    topic: str
    label: str
    time_label: str
    score: float
    confidence: float
    why: List[str] = field(default_factory=list)
    events: List[Event] = field(default_factory=list)
    openable_targets: List[Tuple[str, str]] = field(default_factory=list)
    signals: Dict[str, float] = field(default_factory=dict)

    @property
    def event_count(self) -> int:
        return len(self.events)

    @property
    def kinds(self) -> List[str]:
        seen: set[str] = set()
        out: List[str] = []
        for ev in self.events:
            if ev.kind not in seen:
                seen.add(ev.kind)
                out.append(ev.kind)
        return out

    def preview_events(self, max_n: int = 4) -> List[Event]:
        """Newest-first preview, deduped by URL/path. Mirrors the shape
        of `Session.preview_events` so the launcher can reuse the same
        row widget."""
        seen: set[str] = set()
        out: List[Event] = []
        for ev in reversed(self.events):
            payload = ev.payload or {}
            key = (payload.get("url") or payload.get("path") or "").strip().lower()
            if key and key in seen:
                continue
            if key:
                seen.add(key)
            out.append(ev)
            if len(out) >= max_n:
                break
        return out


# --------------------------------------------------------------- history


class ResurfacingHistory:
    """Tiny JSON-backed counter of how often a topic has been surfaced.

    Used for two things:

      1. Honoring the "clear resurfacing history" user control.
      2. A small "freshness" downweight — a topic surfaced six times in
         the last day is probably annoying the user; back off.

    The file is read once at startup and written through every update.
    The writes are best-effort: if the disk is full we fall back to an
    in-memory-only history rather than crashing the engine. This is
    consistent with the EventLogger's "logger must never raise" rule.
    """

    _PATH: Path = CONFIG_DIR / "resurfacing.json"

    def __init__(self, path: Optional[Path] = None) -> None:
        self.path = path or self._PATH
        self._lock = threading.Lock()
        self._surfaced: Dict[str, Dict[str, float]] = {}
        self._muted: set[str] = set()
        self._load()

    def _load(self) -> None:
        try:
            data = json.loads(self.path.read_text(encoding="utf-8"))
            self._surfaced = data.get("surfaced", {}) or {}
            self._muted = set(data.get("muted", []) or [])
        except (OSError, ValueError):
            self._surfaced = {}
            self._muted = set()

    def _save(self) -> None:
        try:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            self.path.write_text(
                json.dumps(
                    {"surfaced": self._surfaced, "muted": sorted(self._muted)},
                    indent=2,
                    ensure_ascii=False,
                ),
                encoding="utf-8",
            )
        except OSError:
            # Best-effort persistence; an in-memory history is still
            # better than crashing on a full disk.
            pass

    def is_muted(self, topic: str) -> bool:
        return topic in self._muted

    def surfaced_recently_factor(
        self, topic: str, now: Optional[float] = None
    ) -> float:
        """Returns a multiplier in [0.4, 1.0]. 1.0 = never surfaced
        recently (no downweight). Drops as we surface the same topic
        in a short window — a topic that was just shown to the user
        an hour ago gets ~0.6, one shown six times today gets ~0.4."""
        rec = self._surfaced.get(topic)
        if not rec:
            return 1.0
        if now is None:
            now = time.time()
        last = float(rec.get("last_surfaced") or 0.0)
        count = int(rec.get("count") or 0)
        age_hours = max(0.0, (now - last) / 3600.0)
        # A topic surfaced once half a day ago is basically fresh.
        # A topic surfaced six times in the last day is fatiguing.
        if age_hours > 24:
            return 1.0
        if count <= 1:
            return 1.0 if age_hours > 4 else 0.85
        # Each additional recent surface drops the factor by 0.1,
        # bottoming out at 0.4.
        return max(0.4, 1.0 - 0.1 * (count - 1))

    def record_surfaced(
        self, topics: List[str], now: Optional[float] = None
    ) -> None:
        if not topics:
            return
        if now is None:
            now = time.time()
        with self._lock:
            for t in topics:
                rec = self._surfaced.get(t) or {"count": 0, "last_surfaced": 0.0}
                # Reset the count if the previous surface was a day ago
                # — we only fatigue on bursts.
                last = float(rec.get("last_surfaced") or 0.0)
                if (now - last) > 86400:
                    rec["count"] = 1
                else:
                    rec["count"] = int(rec.get("count") or 0) + 1
                rec["last_surfaced"] = float(now)
                self._surfaced[t] = rec
            self._save()

    def mute(self, topic: str) -> None:
        with self._lock:
            self._muted.add(topic)
            self._save()

    def unmute(self, topic: str) -> None:
        with self._lock:
            self._muted.discard(topic)
            self._save()

    def clear(self) -> None:
        """User-facing "clear resurfacing history" control."""
        with self._lock:
            self._surfaced = {}
            self._muted = set()
            try:
                if self.path.exists():
                    self.path.unlink()
            except OSError:
                pass


# --------------------------------------------------------------- engine


class ResurfacingEngine:
    """Heuristic ranking pipeline over the local event log.

    One method (`resurface_idle`) does the work; everything else is
    private helpers. Holds two pieces of state: the `EventStore` it
    reads from and the `ResurfacingHistory` it writes through.

    Stateless w.r.t. the user query (resurfacing is for the *empty*
    query state); thread-safe (the history's own lock guards mutating
    state; the event scan is read-only).
    """

    def __init__(
        self,
        event_store: EventStore,
        history: Optional[ResurfacingHistory] = None,
    ) -> None:
        self.event_store = event_store
        self.history = history or ResurfacingHistory()

    # -- public ----------------------------------------------------------

    def resurface_idle(
        self,
        n: int = _MAX_RESURFACED_ITEMS,
        now: Optional[float] = None,
    ) -> List[ResurfacedContext]:
        """Top-N resurfacing cards for the current idle digest.

        `n` is clamped to `[0, _MAX_RESURFACED_ITEMS]` so a misbehaving
        caller can't ask the engine to render a feed. Returns `[]` when
        nothing clears the score floor — the launcher hides the whole
        section in that case rather than show an empty header.
        """
        n = max(0, min(n, _MAX_RESURFACED_ITEMS))
        if n == 0:
            return []
        if now is None:
            now = time.time()

        buckets = self._bucket_events(now)
        if not buckets:
            return []

        scored: list[ResurfacedContext] = []
        for topic, events in buckets.items():
            if self.history.is_muted(topic):
                continue
            ctx = self._score_bucket(topic, events, now)
            if ctx is None:
                continue
            scored.append(ctx)

        # Topic-level dedupe. Two buckets that share most of their
        # events (e.g. "rlhf" and "reinforcement") would otherwise
        # take two slots. We keep the higher-scoring one.
        scored = self._dedupe_by_event_overlap(scored)

        scored.sort(key=lambda c: c.score, reverse=True)
        top = scored[:n]

        # Record what we surfaced so the next call can fatigue these.
        self.history.record_surfaced([c.topic for c in top], now=now)
        return top

    # -- bucketing -------------------------------------------------------

    def _bucket_events(self, now: float) -> Dict[str, List[Event]]:
        """Group resurfaceable events into topic buckets.

        Bucket key = the first content token of each event's title /
        query, falling back to the domain when the title yields no
        usable token. Generic tokens (`github`, `docs`, …) are
        rejected outright so unrelated activity doesn't collide.

        Single-pass over events; the per-event token extraction is the
        dominant cost (~0.5 µs on cached `searchable_title`).
        """
        cutoff = now - _LOOKBACK_DAYS * 86400
        max_topic_age = now - _MIN_TOPIC_AGE_HOURS * 3600

        buckets: Dict[str, list[Event]] = defaultdict(list)
        for ev in self.event_store.iter_events(days=_LOOKBACK_DAYS):
            if ev.kind not in _RESURFACEABLE_KINDS:
                continue
            ts = ev.ts_epoch()
            if ts < cutoff or ts > max_topic_age:
                # Too old (forgotten) or too recent (still-doing).
                continue
            token = self._topic_key(ev)
            if not token:
                continue
            buckets[token].append(ev)

        return buckets

    @staticmethod
    def _topic_key(ev: Event) -> str:
        """Pick one stable bucket key for an event.

        Title is preferred (the most user-facing handle). When the
        title has no content tokens (rare — chat-session events with
        empty titles), the domain is the fallback. The token is
        rejected if it's in the generic blocklist."""
        payload = ev.payload or {}
        for field_name in ("title", "query"):
            text = (payload.get(field_name) or "").strip()
            if text:
                tokens = _content_tokens(text)
                for tok in tokens:
                    if tok not in _GENERIC_TOPIC_TOKENS:
                        return tok
        # Domain fallback. Keep the first label only ("arxiv.org" →
        # "arxiv") and drop generics.
        domain = (payload.get("domain") or "").strip().lower()
        if domain:
            head = domain.split(".")[0]
            if head and head not in _GENERIC_TOPIC_TOKENS:
                return head
        return ""

    # -- scoring ---------------------------------------------------------

    def _score_bucket(
        self, topic: str, events: List[Event], now: float
    ) -> Optional[ResurfacedContext]:
        """Compute the full set of signals for one bucket. Returns
        `None` if the bucket fails an anti-noise filter."""
        if len(events) < _MIN_EVENTS:
            return None

        # Sort chronologically once; everything below assumes order.
        events.sort(key=lambda e: e.ts_epoch())

        first_ts = events[0].ts_epoch()
        last_ts  = events[-1].ts_epoch()

        # ── distinct-session / distinct-day diversity ──
        sessions = {ev.session_id for ev in events if ev.session_id}
        days = set()
        for ev in events:
            ts = ev.ts_epoch()
            if ts > 0:
                days.add(datetime.fromtimestamp(ts, timezone.utc).date())

        # Anti-noise: a single-session burst is not unfinished
        # thinking — it's a session. Resurfacing fires across days
        # OR across sessions, not within one sitting.
        if len(sessions) <= 1 and len(days) <= 1:
            return None

        # ── URL revisits and repeated opens ──
        url_visits: Counter = Counter()
        path_opens: Counter = Counter()
        for ev in events:
            payload = ev.payload or {}
            url = (payload.get("url") or "").strip().lower()
            path = (payload.get("path") or "").strip().lower()
            if url:
                url_visits[url] += 1
            if path:
                path_opens[path] += 1
        url_revisits = sum(c - 1 for c in url_visits.values() if c > 1)
        path_revisits = sum(c - 1 for c in path_opens.values() if c > 1)

        # Anti-noise: if the bucket is built entirely from one URL hit
        # once per session, that's not a revisit — it's the same
        # link living in three different sessions for no reason. The
        # rule is: at least one URL was revisited, OR the events
        # cover multiple URLs.
        distinct_targets = len(set(url_visits.keys()) | set(path_opens.keys()))
        if url_revisits + path_revisits == 0 and distinct_targets <= 1:
            return None

        # ── repeated-search signal ──
        # Counted against the bucket's topic, sourced from `query`
        # events whose payload text contains the topic token.
        repeat_searches = self._repeat_search_count(topic, now)

        # ── per-signal scores [0..1] ──
        # Recency: exponential decay from the most recent event.
        age_days = max(0.0, (now - last_ts) / 86400.0)
        s_recency = math.pow(0.5, age_days / _RECENCY_HALFLIFE_DAYS)

        # Frequency: log-shaped so the 20th event doesn't dominate.
        s_frequency = min(1.0, math.log1p(len(events)) / math.log(8.0))

        # Session / day diversity: capped at 4 to stop pathological
        # buckets dominating.
        s_session_div = min(1.0, (len(sessions) - 1) / 3.0)
        s_day_div     = min(1.0, (len(days) - 1) / 3.0)

        # URL revisits: each revisit adds half a unit, cap at 4 revisits.
        s_url_revisits = min(1.0, (url_revisits + path_revisits) / 4.0)

        # Repeated searches: at least one repeat search puts the
        # signal at 0.6; three repeats → 1.0.
        s_repeat_search = (
            min(1.0, 0.4 + 0.3 * repeat_searches) if repeat_searches else 0.0
        )

        # Context size: a sweet-spot signal — 3 to 8 events is ideal;
        # 1 or 2 is trivial (already filtered); 30+ smells like an
        # accidental tab graveyard.
        n = len(events)
        if 3 <= n <= 8:
            s_context_size = 1.0
        elif 9 <= n <= 15:
            s_context_size = 0.8
        elif 16 <= n <= 30:
            s_context_size = 0.5
        else:
            s_context_size = 0.25

        # ── weighted sum ──
        raw_score = (
            _W_RECENCY            * s_recency
            + _W_FREQUENCY        * s_frequency
            + _W_SESSION_DIVERSITY * s_session_div
            + _W_DAY_DIVERSITY    * s_day_div
            + _W_URL_REVISITS     * s_url_revisits
            + _W_REPEAT_SEARCH    * s_repeat_search
            + _W_CONTEXT_SIZE     * s_context_size
        )

        # Fatigue downweight from the surfacing-history file.
        fatigue = self.history.surfaced_recently_factor(topic, now=now)
        score = raw_score * fatigue

        if score < _MIN_SCORE:
            return None

        # ── confidence: are we sure this is real unfinished work? ──
        confidence = self._compute_confidence(
            event_count=len(events),
            session_count=len(sessions),
            day_count=len(days),
            url_revisits=url_revisits + path_revisits,
            repeat_searches=repeat_searches,
        )

        # ── label + time label + openable targets ──
        label = self._derive_label(events, topic)
        time_label = self._format_window(first_ts, last_ts, now)
        openable = self._openable_targets(events)
        why = self._explain(
            topic=topic,
            event_count=len(events),
            session_count=len(sessions),
            day_count=len(days),
            url_revisits=url_revisits + path_revisits,
            repeat_searches=repeat_searches,
        )

        signals = {
            "recency":           round(s_recency, 3),
            "frequency":         round(s_frequency, 3),
            "session_diversity": round(s_session_div, 3),
            "day_diversity":     round(s_day_div, 3),
            "url_revisits":      round(s_url_revisits, 3),
            "repeat_search":     round(s_repeat_search, 3),
            "context_size":      round(s_context_size, 3),
            "fatigue_factor":    round(fatigue, 3),
            "raw_score":         round(raw_score, 3),
        }

        return ResurfacedContext(
            topic=topic,
            label=label,
            time_label=time_label,
            score=round(score, 4),
            confidence=round(confidence, 3),
            why=why,
            events=events,
            openable_targets=openable,
            signals=signals,
        )

    def _repeat_search_count(self, topic: str, now: float) -> int:
        """How many launcher `query` events in the lookback window
        match the topic? Substring check on the cached searchable
        text — cheap enough to run for every bucket."""
        cutoff = now - _LOOKBACK_DAYS * 86400
        count = 0
        topic_lc = topic.lower()
        for ev in self.event_store.iter_events(days=_LOOKBACK_DAYS):
            if ev.kind != "query":
                continue
            if ev.ts_epoch() < cutoff:
                continue
            text = (ev.payload.get("text") or "").lower()
            if topic_lc in text:
                count += 1
        return max(0, count - 1)  # first search isn't a "repeat"

    # -- confidence ------------------------------------------------------

    @staticmethod
    def _compute_confidence(
        event_count: int,
        session_count: int,
        day_count: int,
        url_revisits: int,
        repeat_searches: int,
    ) -> float:
        """Resume confidence — separate from rank score. High when the
        evidence is *broad* (many sessions × days × revisits); low when
        it's just a few events that happen to share a token.

        The scale is deliberately conservative — even a strong bucket
        rarely passes 0.85. The launcher uses this only to soften the
        wording ("Continue", "Look back at", etc.) and to drive the
        debug hover; we never gate on it."""
        score = 0.0
        if event_count >= 3:
            score += 0.25
        if event_count >= 6:
            score += 0.10
        if session_count >= 2:
            score += 0.20
        if session_count >= 3:
            score += 0.05
        if day_count >= 2:
            score += 0.15
        if day_count >= 3:
            score += 0.05
        if url_revisits >= 1:
            score += 0.10
        if url_revisits >= 3:
            score += 0.05
        if repeat_searches >= 1:
            score += 0.05
        return min(1.0, score)

    # -- dedupe ----------------------------------------------------------

    @staticmethod
    def _dedupe_by_event_overlap(
        scored: List[ResurfacedContext],
    ) -> List[ResurfacedContext]:
        """Drop a lower-scoring bucket when most of its events appear
        in a higher-scoring one. Topics often overlap (`rlhf` /
        `reinforcement`) and we want only one slot per real thread."""
        if len(scored) <= 1:
            return scored
        scored.sort(key=lambda c: c.score, reverse=True)
        kept: list[ResurfacedContext] = []
        kept_sets: list[set[str]] = []
        for ctx in scored:
            ev_keys = {
                _event_key(ev) for ev in ctx.events
                if _event_key(ev)
            }
            if not ev_keys:
                kept.append(ctx)
                kept_sets.append(set())
                continue
            is_duplicate = False
            for prev in kept_sets:
                if not prev:
                    continue
                # Heavy overlap = same thread, just a different token.
                overlap = len(ev_keys & prev)
                if overlap / max(1, min(len(ev_keys), len(prev))) >= 0.6:
                    is_duplicate = True
                    break
            if not is_duplicate:
                kept.append(ctx)
                kept_sets.append(ev_keys)
        return kept

    # -- labels ----------------------------------------------------------

    @staticmethod
    def _derive_label(events: List[Event], topic: str) -> str:
        """A short, calm headline. The bucket's primary token shapes
        the headline, but we prefer the title of the bucket's most
        recent event when one is available — it reads more like a
        memory and less like a tag cloud."""
        latest = events[-1] if events else None
        if latest is not None:
            payload = latest.payload or {}
            title = (payload.get("title") or "").strip()
            if title:
                if len(title) > 70:
                    title = title[:67].rstrip() + "…"
                return title
            query = (payload.get("query") or "").strip()
            if query:
                return f'"{query}"' if len(query) <= 70 else f'"{query[:67]}…"'
        # Fallback: capitalize the topic token. This is the path for
        # rare events whose titles are empty.
        return topic.capitalize()

    @staticmethod
    def _format_window(first_ts: float, last_ts: float, now: float) -> str:
        """A two-part time label: when the activity *last* happened
        and a rough span. Mirrors `format_time_range` from sessions.py
        but expressed across days, not minutes."""
        if first_ts <= 0 or last_ts <= 0:
            return ""
        age = humanize_age(last_ts, now=now)
        span_days = max(0.0, (last_ts - first_ts) / 86400.0)
        if span_days < 1.0:
            return age
        if span_days < 2.0:
            return f"{age}  ·  across 2 days"
        if span_days < 7.0:
            return f"{age}  ·  across {int(round(span_days)) + 1} days"
        weeks = max(1, int(round(span_days / 7.0)))
        return f"{age}  ·  ~{weeks}w span"

    @staticmethod
    def _openable_targets(events: List[Event]) -> List[Tuple[str, str]]:
        """Return up to 16 distinct (kind, target) pairs. Same shape
        as Session/MicroContext openable_targets so the launcher row
        widget renders identically."""
        seen: set[str] = set()
        out: list[Tuple[str, str]] = []
        for ev in reversed(events):  # newest first → most recent target wins
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
            if len(out) >= 16:
                break
        return out

    # -- "why" ----------------------------------------------------------

    @staticmethod
    def _explain(
        topic: str,
        event_count: int,
        session_count: int,
        day_count: int,
        url_revisits: int,
        repeat_searches: int,
    ) -> List[str]:
        """A small list of plain-English reasons, ordered most-
        important-first. Rendered in the debug hover when the user is
        in `RECALL_DEBUG` mode. Each line is short and observational,
        not predictive — we report what we saw, never speculate."""
        lines: list[str] = []
        if day_count >= 2:
            lines.append(f"touched on {day_count} different days")
        if session_count >= 2:
            lines.append(f"spanned {session_count} sessions")
        if url_revisits >= 1:
            target_word = "place" if url_revisits == 1 else "places"
            lines.append(
                f"revisited the same {target_word} {url_revisits} time"
                + ("s" if url_revisits > 1 else "")
            )
        if repeat_searches >= 1:
            lines.append(
                f"searched for it {repeat_searches} more time"
                + ("s" if repeat_searches > 1 else "")
                + " after the first"
            )
        if event_count >= 6:
            lines.append(f"{event_count} related events in the window")
        # Always end with the bucket key so the hover spells out what
        # the engine actually grouped on.
        lines.append(f'(topic key: "{topic}")')
        return lines


# --------------------------------------------------------------- helper


def _event_key(ev: Event) -> str:
    """Stable event identity for dedupe — URL/path if present, else
    the (ts, session_id) tuple as a string. The latter case rarely
    fires because we restrict bucketing to events with usable
    payloads, but keeping it makes the dedupe pure."""
    payload = ev.payload or {}
    target = (payload.get("url") or payload.get("path") or "").strip().lower()
    if target:
        return target
    return f"{ev.ts}:{ev.session_id}"
