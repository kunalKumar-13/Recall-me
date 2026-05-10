"""Episodic retrieval — keyword + recency + kind-hint scoring over the
local event log.

Phase 1C deliberately avoids embeddings: every event is scored cheaply
in Python, the worst case is a few thousand JSONL lines, and the result
arrives well inside the launcher's perceived-instant window. Embeddings
become valuable only once the retrieval shape is well understood, which
is a Phase 1D concern.

The retriever answers queries the launcher's file search cannot:

  • "that GPT chat about websocket retries"
  • "the Kanye interview I read yesterday"
  • "the RLHF article from Chrome"
  • "what was I researching last night"

Three layers of query understanding:

  1. parse_temporal       — finds "yesterday" / "last night" / "this
                            morning" etc., returns a time window the
                            event iterator can filter against.
  2. parse_kind_hint      — finds "GPT" / "Claude" / "chat" / "search"
                            / "article", returns a kind+platform hint
                            that boosts matching events.
  3. content tokens       — what's left after stripping temporal and
                            kind phrases, used for keyword overlap.

Scoring stays additive and small-numbered so a future re-rank
(embeddings, BM25, …) can layer on top without rewriting the pipeline.
"""

from __future__ import annotations

import re
import time
from dataclasses import dataclass, field
from typing import List, Optional, Tuple

from .events import Event, EventStore, humanize_age

# Only browser-side events are episodic-retrievable in Phase 1C —
# launcher queries and file opens already surface in the file search,
# so re-presenting them as episodic results would feel duplicative.
RETRIEVABLE_KINDS: frozenset[str] = frozenset({
    "browser_visit",
    "browser_search",
    "chat_session",
})

# Tiny stopword set — just the most common English filler that
# never carries content signal.
_STOPWORDS: frozenset[str] = frozenset({
    "the", "a", "an", "and", "or", "but", "of", "in", "to", "for",
    "from", "with", "by", "on", "at", "as", "is", "are", "was", "were",
    "be", "been", "being", "have", "has", "had", "do", "does", "did",
    "this", "that", "these", "those", "it", "its", "they", "them",
    "there", "here", "what", "which", "when", "where", "who", "how",
    "why", "about", "into", "onto", "more", "less", "very", "can",
    "should", "would", "could", "may", "might", "i", "my", "me",
    "you", "your", "we", "our", "us", "thing",
})


# --------------------------------------------------------------- temporal


@dataclass(frozen=True)
class TimeWindow:
    """Inclusive range expressed as (start, end) Unix timestamps.
    `label` is the source phrase, kept for debug/logging only."""

    start: float
    end: float
    label: str

    def contains(self, ts: float) -> bool:
        return self.start <= ts <= self.end


# Each pattern owns the phrases that map to a single time window. The
# resolver fills in concrete (start, end) timestamps relative to "now"
# at call time so the window slides as the user keeps the launcher open.
_TEMPORAL_RULES: List[Tuple[re.Pattern, str]] = [
    (
        re.compile(
            r"\b(?:right now|just now|this minute)\b", re.IGNORECASE
        ),
        "minute",
    ),
    (
        re.compile(
            r"\b(?:this morning|earlier today|today|tonight|this evening|this afternoon)\b",
            re.IGNORECASE,
        ),
        "today",
    ),
    (
        re.compile(
            r"\b(?:yesterday|last night|last evening)\b", re.IGNORECASE
        ),
        "yesterday",
    ),
    (
        re.compile(
            r"\b(?:past few days|few days ago|couple of days|recently|lately)\b",
            re.IGNORECASE,
        ),
        "few_days",
    ),
    (
        re.compile(
            r"\b(?:this week|past week|last week)\b", re.IGNORECASE
        ),
        "week",
    ),
    (
        re.compile(
            r"\b(?:this month|past month|last month)\b", re.IGNORECASE
        ),
        "month",
    ),
]


def _resolve_window(label: str, now_ts: float) -> Optional[TimeWindow]:
    """Map a temporal phrase to a sliding time window.

    Relative-24h windows are used instead of calendar-day boundaries
    because the user's mental model of "today" / "yesterday" doesn't
    snap to UTC midnight. Asking "what did I read today" at 1am should
    pick up the article they read at 11pm.
    """
    if label == "minute":
        return TimeWindow(now_ts - 600, now_ts, label)            # last 10 min
    if label == "today":
        return TimeWindow(now_ts - 86400, now_ts, label)          # last 24h
    if label == "yesterday":
        return TimeWindow(
            now_ts - 2 * 86400, now_ts - 86400, label
        )                                                          # 24-48h ago
    if label == "few_days":
        return TimeWindow(now_ts - 3 * 86400, now_ts, label)
    if label == "week":
        return TimeWindow(now_ts - 7 * 86400, now_ts, label)
    if label == "month":
        return TimeWindow(now_ts - 30 * 86400, now_ts, label)
    return None


def parse_temporal(
    query: str, now_ts: Optional[float] = None
) -> Tuple[str, Optional[TimeWindow]]:
    """Strip the first temporal phrase from `query` and return
    (cleaned_query, window). If no phrase is present the window is None
    and `cleaned_query == query`.

    Only the *first* match wins — "yesterday morning's RLHF article"
    resolves to yesterday, not to "morning + yesterday" (which would
    require composition logic out of scope for the Phase 1C MVP).
    """
    if now_ts is None:
        now_ts = time.time()
    cleaned = query
    for pattern, label in _TEMPORAL_RULES:
        m = pattern.search(cleaned)
        if m:
            window = _resolve_window(label, now_ts)
            cleaned = pattern.sub(" ", cleaned, count=1)
            return _collapse_spaces(cleaned), window
    return query, None


# --------------------------------------------------------------- kind hint


@dataclass(frozen=True)
class KindHint:
    """A soft constraint pushing certain event kinds up the ranking.

    `kind` is the EventStore kind to favor (e.g. "chat_session"); when
    `platform` is non-empty the boost stacks if the event's payload
    matches (e.g. platform="chatgpt" only fires on ChatGPT chats).
    Either or both can be present.
    """

    kind: Optional[str]
    platform: Optional[str]
    label: str


_KIND_RULES: List[Tuple[re.Pattern, KindHint]] = [
    (
        re.compile(r"\b(?:chat\s*gpt|chatgpt|gpt(?:\s*chat)?)\b", re.IGNORECASE),
        KindHint(kind="chat_session", platform="chatgpt", label="chatgpt"),
    ),
    (
        re.compile(r"\b(?:claude(?:\s*chat)?)\b", re.IGNORECASE),
        KindHint(kind="chat_session", platform="claude", label="claude"),
    ),
    (
        re.compile(r"\b(?:chat|conversation|convo)\b", re.IGNORECASE),
        KindHint(kind="chat_session", platform=None, label="chat"),
    ),
    (
        re.compile(
            r"\b(?:google(?:d)?|searched|search\s+engine)\b",
            re.IGNORECASE,
        ),
        KindHint(kind="browser_search", platform=None, label="search"),
    ),
    (
        re.compile(
            r"\b(?:article|page|read|reading|browsed|website|site)\b",
            re.IGNORECASE,
        ),
        KindHint(kind="browser_visit", platform=None, label="visit"),
    ),
]


def parse_kind_hint(query: str) -> Tuple[str, Optional[KindHint]]:
    """Extract a kind hint and return (cleaned_query, hint).

    Like temporal, only the first matching rule wins so that hints
    don't compound silently. The cleaned query has the matched phrase
    replaced with whitespace, which collapse_spaces tidies."""
    for pattern, hint in _KIND_RULES:
        if pattern.search(query):
            cleaned = pattern.sub(" ", query, count=1)
            return _collapse_spaces(cleaned), hint
    return query, None


# --------------------------------------------------------------- result


@dataclass
class EpisodicResult:
    """One episodic moment ready for the launcher to render and act
    on. `score` is exposed for debugging — the UI doesn't display it."""

    kind: str               # browser_visit | browser_search | chat_session
    title: str
    subtitle: str           # "ChatGPT", "google · 2h ago" — for the card
    url: str
    ts_epoch: float
    score: float
    session_id: str = ""
    payload: dict = field(default_factory=dict)

    @classmethod
    def from_event(
        cls, ev: Event, score: float, subtitle: Optional[str] = None
    ) -> "EpisodicResult":
        title = _display_title(ev)
        if subtitle is None:
            subtitle = _display_subtitle(ev)
        return cls(
            kind=ev.kind,
            title=title,
            subtitle=subtitle,
            url=(ev.payload.get("url") or "").strip(),
            ts_epoch=ev.ts_epoch(),
            score=score,
            session_id=ev.session_id or "",
            payload=ev.payload or {},
        )


def _display_title(ev: Event) -> str:
    p = ev.payload or {}
    if ev.kind == "browser_search":
        q = (p.get("query") or "").strip()
        if q:
            return f"“{q}”"
    title = (p.get("title") or "").strip()
    if title:
        return title
    return (p.get("domain") or p.get("url") or "Untitled moment").strip()


def _display_subtitle(ev: Event) -> str:
    p = ev.payload or {}
    age = humanize_age(ev.ts_epoch())
    if ev.kind == "chat_session":
        platform = (p.get("platform") or "chat").strip()
        return f"{platform.capitalize()}  ·  {age}" if age else platform
    if ev.kind == "browser_search":
        engine = (p.get("engine") or "search").strip()
        return f"{engine}  ·  {age}" if age else engine
    domain = (p.get("domain") or "").strip()
    if domain and age:
        return f"{domain}  ·  {age}"
    return domain or age


# --------------------------------------------------------------- retriever


# Tunable knobs — kept small and explicit so a future tuning pass can
# walk through them in one place.
_BASE_KEYWORD_WEIGHT = 0.20         # per content-token hit in title
_PAYLOAD_KEYWORD_WEIGHT = 0.10      # per content-token hit elsewhere in payload
_KIND_BOOST = 0.25                  # exact kind hint match
_PLATFORM_BOOST = 0.20              # kind + platform both match
_RECENCY_FRESH = 0.18               # event within last 24h
_RECENCY_RECENT = 0.10              # event within last 7d
_TEMPORAL_HARD_FILTER = True        # explicit temporal phrase = filter, not boost
_MIN_CONFIDENCE = 0.18              # below this we don't surface anything


class EpisodicRetriever:
    """Stateless retriever over an EventStore.

    Reads-on-each-query. Cheap because the EventStore itself is just
    per-day JSONL files and Phase 1C only walks a 14-day window by
    default. Construction is free; can live for the launcher's lifetime
    without holding any state of its own.
    """

    def __init__(self, event_store: EventStore) -> None:
        self.event_store = event_store

    def search(self, query: str, n: int = 3) -> List[EpisodicResult]:
        """Return top-N episodic results for `query`. Empty list when
        the query has no actionable signal at all (no temporal, no kind
        hint, and no content tokens left after stripping)."""
        raw = (query or "").strip()
        if not raw:
            return []

        cleaned, window = parse_temporal(raw)
        cleaned, hint = parse_kind_hint(cleaned)
        content_tokens = _content_tokens(cleaned)

        # If the user typed only "yesterday" with no other signal,
        # we still surface (it's a recency probe). But pure stopwords
        # like "the" or "a" produce nothing.
        if not content_tokens and not window and not hint:
            return []

        # Default lookback when the query has no explicit temporal hint.
        # Wider than a week so behavioral memory ("that thing") still
        # reaches into the previous fortnight.
        days = _days_for_window(window) if window else 14

        scored: List[Tuple[float, Event]] = []
        for ev in self.event_store.iter_events(days=days):
            if ev.kind not in RETRIEVABLE_KINDS:
                continue
            if window is not None and _TEMPORAL_HARD_FILTER:
                if not window.contains(ev.ts_epoch()):
                    continue
            score = self._score(ev, content_tokens, hint)
            if score >= _MIN_CONFIDENCE:
                scored.append((score, ev))

        scored.sort(key=lambda kv: kv[0], reverse=True)

        # Dedupe by URL — the same article visited twice in a day
        # shouldn't take two of the three slots.
        seen_urls: set[str] = set()
        out: List[EpisodicResult] = []
        for score, ev in scored:
            url = (ev.payload.get("url") or "").strip().lower()
            if url and url in seen_urls:
                continue
            if url:
                seen_urls.add(url)
            out.append(EpisodicResult.from_event(ev, score))
            if len(out) >= n:
                break
        return out

    # -- scoring --------------------------------------------------------

    def _score(
        self,
        ev: Event,
        content_tokens: List[str],
        hint: Optional[KindHint],
    ) -> float:
        score = 0.0
        payload = ev.payload or {}

        # Content keyword overlap. Title hits are worth more than other-
        # field hits because the title is the user's mental handle on
        # the moment.
        title_lc = (
            (payload.get("title") or "")
            + " "
            + (payload.get("query") or "")
        ).lower()
        rest_lc = " ".join(
            str(v) for k, v in payload.items()
            if k not in ("title", "query") and isinstance(v, str)
        ).lower()

        for tok in content_tokens:
            if tok in title_lc:
                score += _BASE_KEYWORD_WEIGHT
            elif tok in rest_lc:
                score += _PAYLOAD_KEYWORD_WEIGHT

        # Kind hint boost.
        if hint is not None:
            if hint.kind and ev.kind == hint.kind:
                score += _KIND_BOOST
                if hint.platform:
                    payload_platform = (payload.get("platform") or "").lower()
                    if payload_platform == hint.platform.lower():
                        score += _PLATFORM_BOOST

        # Recency decay — the smaller of two thresholds wins.
        age_days = max(0.0, (time.time() - ev.ts_epoch()) / 86400.0)
        if age_days < 1:
            score += _RECENCY_FRESH
        elif age_days < 7:
            score += _RECENCY_RECENT

        # When we have an explicit kind hint and ZERO content tokens
        # (e.g. "what claude chats did I have"), the score is just
        # boosts. Reward those baseline-only matches enough to clear
        # _MIN_CONFIDENCE so the user gets *something* back.
        if not content_tokens and hint is not None:
            score += 0.10

        return round(score, 4)

    # -- session enrichment --------------------------------------------

    def session_neighbors(
        self,
        ev: Event,
        max_n: int = 2,
        max_minutes: int = 30,
    ) -> List[Event]:
        """Return up to `max_n` other events from the same session,
        within `max_minutes` of `ev`. Used by the launcher's preview
        pane to render "related moments" alongside an episodic result.

        Cheaper than embedding-based co-occurrence: we just read the
        same per-day file and filter on session_id and timestamp.
        """
        if not ev.session_id:
            return []
        anchor = ev.ts_epoch()
        window_s = max_minutes * 60
        out: List[Event] = []
        for other in self.event_store.iter_events(days=2):
            if other.session_id != ev.session_id:
                continue
            if (other.payload.get("url") or "") == (ev.payload.get("url") or ""):
                # skip the anchor itself (and exact duplicates)
                continue
            ots = other.ts_epoch()
            if abs(ots - anchor) > window_s:
                continue
            out.append(other)
            if len(out) >= max_n:
                break
        return out


# --------------------------------------------------------------- helpers


_TOKEN_RE = re.compile(r"[A-Za-z][A-Za-z0-9'_-]+")
_WHITESPACE_RE = re.compile(r"\s+")


def _content_tokens(text: str) -> List[str]:
    """Lowercase tokens of length >= 3, stopwords removed,
    duplicates dropped, order preserved."""
    out: List[str] = []
    seen: set[str] = set()
    for tok in _TOKEN_RE.findall(text.lower()):
        if len(tok) < 3 or tok in _STOPWORDS:
            continue
        if tok in seen:
            continue
        seen.add(tok)
        out.append(tok)
    return out


def _collapse_spaces(s: str) -> str:
    return _WHITESPACE_RE.sub(" ", s).strip()


def _days_for_window(window: Optional[TimeWindow]) -> int:
    """Translate a temporal window into the EventStore lookback in
    days. Always rounds up so an event at the edge of the window
    isn't accidentally excluded."""
    if window is None:
        return 14
    span_days = (window.end - window.start) / 86400.0
    return max(1, int(span_days + 1))
