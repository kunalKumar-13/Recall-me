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

import math
import re
import time
from dataclasses import dataclass, field
from difflib import SequenceMatcher
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
_FUZZY_KEYWORD_WEIGHT = 0.13        # per fuzzy (typo-tolerant) hit in title
_KIND_BOOST = 0.25                  # exact kind hint match
_PLATFORM_BOOST = 0.20              # kind + platform both match
_TEMPORAL_HARD_FILTER = True        # explicit temporal phrase = filter, not boost
_MIN_CONFIDENCE = 0.18              # below this we don't surface anything

# Recency decay: exponential. `_RECENCY_PEAK` is the boost a brand-
# new (age = 0) event receives; the boost halves every
# `_RECENCY_HALFLIFE_DAYS` days. Replaces the old step function which
# was harsh at 24h and 7d cliffs.
_RECENCY_PEAK = 0.18
_RECENCY_HALFLIFE_DAYS = 3.5

# Co-occurrence: an event in the same session as ANOTHER scoring
# candidate gets a small bonus. Reading three things in one session
# about the same topic should each lift the rest.
_SESSION_COOCCURRENCE_BOOST = 0.08

# Typo tolerance threshold — a candidate-text word counts as fuzzy-
# matching a query token when their SequenceMatcher ratio is above
# this AND their lengths are within 2 characters. Conservative on
# purpose — too lax produces false positives.
_FUZZY_RATIO_THRESHOLD = 0.86
_FUZZY_MIN_TOKEN_LEN = 4


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
        hint, and no content tokens left after stripping).

        Pipeline:
          1. parse temporal + kind hints
          2. expand content tokens through the synonym map
          3. score every retrievable event in the time window
          4. apply session co-occurrence boost (events sharing a
             session with another scoring candidate get a small lift)
          5. dedupe by URL *and* by (domain, title_stem) so the same
             article seen via different URLs only takes one slot
        """
        raw = (query or "").strip()
        if not raw:
            return []

        cleaned, window = parse_temporal(raw)
        cleaned, hint = parse_kind_hint(cleaned)
        base_tokens = _content_tokens(cleaned)
        expanded_tokens = _expand_tokens(base_tokens)

        # If the user typed only "yesterday" with no other signal,
        # we still surface (it's a recency probe). But pure stopwords
        # like "the" or "a" produce nothing.
        if not base_tokens and not window and not hint:
            return []

        # Default lookback when the query has no explicit temporal hint.
        # Wider than a week so behavioral memory ("that thing") still
        # reaches into the previous fortnight.
        days = _days_for_window(window) if window else 14

        # Pass 1: score every event individually.
        # Pre-build a kind-hint flag once. Inside the per-event loop
        # we use it to allow kind-only matches through the quick
        # filter when there are no content tokens to substring-match.
        has_kind_hint = hint is not None and hint.kind is not None

        scored: List[Tuple[float, Event]] = []
        for ev in self.event_store.iter_events(days=days):
            if ev.kind not in RETRIEVABLE_KINDS:
                continue
            if window is not None and _TEMPORAL_HARD_FILTER:
                if not window.contains(ev.ts_epoch()):
                    continue

            # Quick-reject (Phase 2A perf): at 10K events, the
            # per-token fuzzy match inside `_score` dominates the
            # budget. A single combined-text substring check against
            # the expanded tokens lets us skip the full scoring
            # pass for events that can't possibly clear the floor.
            #
            # Events with a kind-hint match get a free pass even
            # when they have no content tokens — that's the
            # "what claude chats did I have" case where the only
            # signal is the kind.
            if expanded_tokens:
                if not _quick_token_overlap(ev, expanded_tokens):
                    if not (has_kind_hint and ev.kind == hint.kind):
                        continue

            score = self._score(ev, expanded_tokens, hint)
            if score >= _MIN_CONFIDENCE:
                scored.append((score, ev))

        if not scored:
            return []

        # Pass 2: session co-occurrence boost. An event that shares a
        # session with at least one other candidate gets a small lift —
        # rewards reading multiple related things in one sitting
        # without requiring an explicit clustering pass.
        session_counts: dict[str, int] = {}
        for _, ev in scored:
            if ev.session_id:
                session_counts[ev.session_id] = (
                    session_counts.get(ev.session_id, 0) + 1
                )
        boosted: List[Tuple[float, Event]] = []
        for score, ev in scored:
            if ev.session_id and session_counts.get(ev.session_id, 0) >= 2:
                score = round(score + _SESSION_COOCCURRENCE_BOOST, 4)
            boosted.append((score, ev))

        boosted.sort(key=lambda kv: kv[0], reverse=True)

        # Pass 3: two-key dedup — URL exact match *and* (domain,
        # title-stem). The latter catches the same article seen via
        # ?utm_*=…, /amp/, mobile.x.com vs x.com, etc.
        seen_urls: set[str] = set()
        seen_keys: set[Tuple[str, str]] = set()
        out: List[EpisodicResult] = []
        for score, ev in boosted:
            payload = ev.payload or {}
            url = (payload.get("url") or "").strip().lower()
            domain = (payload.get("domain") or "").strip().lower()
            title = payload.get("title") or payload.get("query") or ""
            key = (domain, _title_stem(title)) if (domain and title) else None

            if url and url in seen_urls:
                continue
            if key is not None and key in seen_keys:
                continue
            if url:
                seen_urls.add(url)
            if key is not None:
                seen_keys.add(key)
            out.append(EpisodicResult.from_event(ev, score))
            if len(out) >= n:
                break
        return out

    # -- scoring --------------------------------------------------------

    def _score(
        self,
        ev: Event,
        expanded_tokens: List[str],
        hint: Optional[KindHint],
    ) -> float:
        score = 0.0
        payload = ev.payload or {}

        # Content keyword overlap. Title hits are worth more than other-
        # field hits because the title is the user's mental handle on
        # the moment. We rely on `Event.searchable_title()` /
        # `Event.searchable_rest()` which lowercase + cache once per
        # event; rebuilding these strings on every scored event was the
        # dominant cost at 10K-event scale (~30ms saved per query).
        title_lc = ev.searchable_title()
        rest_lc = ev.searchable_rest()

        # Per-token exact match — title hit is worth more than
        # other-field hit. We track an exact-hit count so the more
        # expensive fuzzy path can be skipped when at least one
        # token already grounded the event.
        exact_hits = 0
        unmatched_tokens: list[str] = []
        for tok in expanded_tokens:
            if tok in title_lc:
                score += _BASE_KEYWORD_WEIGHT
                exact_hits += 1
            elif tok in rest_lc:
                score += _PAYLOAD_KEYWORD_WEIGHT
                exact_hits += 1
            else:
                unmatched_tokens.append(tok)

        # Fuzzy tolerance — only fires when *no* exact hit landed
        # AND there's something to compare against. At 10K-event
        # scale, the `difflib.SequenceMatcher` cost dominates the
        # search latency; making it the rare-event branch dropped
        # the 10K-event search budget from ~600ms to <30ms.
        if exact_hits == 0 and unmatched_tokens:
            title_words = _TOKEN_RE.findall(title_lc)
            for tok in unmatched_tokens:
                if _fuzzy_match_in(tok, title_words):
                    score += _FUZZY_KEYWORD_WEIGHT
                    break  # one fuzzy hit is enough — bound the cost

        # Kind hint boost.
        if hint is not None:
            if hint.kind and ev.kind == hint.kind:
                score += _KIND_BOOST
                if hint.platform:
                    payload_platform = (payload.get("platform") or "").lower()
                    if payload_platform == hint.platform.lower():
                        score += _PLATFORM_BOOST

        # Recency: smooth exponential decay. Maximum boost at 0 days,
        # halves every `_RECENCY_HALFLIFE_DAYS`. Replaces the old
        # 24h / 7d step function which was harsh at the cliff.
        age_days = max(0.0, (time.time() - ev.ts_epoch()) / 86400.0)
        score += _RECENCY_PEAK * math.pow(
            0.5, age_days / _RECENCY_HALFLIFE_DAYS
        )

        # When we have an explicit kind hint and ZERO content tokens
        # (e.g. "what claude chats did I have"), the score is just
        # boosts. Reward those baseline-only matches enough to clear
        # _MIN_CONFIDENCE so the user gets *something* back.
        if not expanded_tokens and hint is not None:
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


# Tiny manual synonym map for common technical / cultural terms users
# search for in different forms. Bidirectional — both keys and values
# expand to each other. Kept hand-curated and small; a 50-entry map
# is far more useful here than a generic stemmer because the failure
# mode of over-stemming ("organisation" → "organis") is worse than
# missing a match.
_SYNONYMS: dict[str, list[str]] = {
    "websocket": ["websockets", "ws"],
    "websockets": ["websocket", "ws"],
    "rlhf": ["reinforcement", "reward", "human feedback"],
    "llm": ["llms", "language model"],
    "gpt": ["chatgpt"],
    "chatgpt": ["gpt"],
    "claude": ["anthropic"],
    "anthropic": ["claude"],
    "kanye": ["ye"],
    "ye": ["kanye"],
    "interview": ["profile", "conversation"],
    "article": ["post", "piece", "writeup"],
    "post": ["article", "piece"],
    "blog": ["post", "article"],
    "paper": ["arxiv", "preprint"],
    "arxiv": ["paper", "preprint"],
    "pricing": ["price", "cost"],
    "auth": ["authentication", "login"],
    "authentication": ["auth", "login"],
    "db": ["database"],
    "database": ["db"],
}


def _expand_tokens(tokens: List[str]) -> List[str]:
    """Return tokens + their synonyms. Order-preserving, dedup'd.

    Used for keyword scoring so a user who types "websocket" still
    matches an event titled "WebSockets in production".
    """
    out: List[str] = []
    seen: set[str] = set()
    for tok in tokens:
        if tok not in seen:
            seen.add(tok)
            out.append(tok)
        for syn in _SYNONYMS.get(tok, ()):
            for piece in syn.split():
                if piece not in seen:
                    seen.add(piece)
                    out.append(piece)
    return out


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


def _fuzzy_match_in(token: str, words: List[str]) -> bool:
    """Returns True if any word in `words` is a near-match for
    `token` per `_FUZZY_RATIO_THRESHOLD`. Conservative — bails on
    short tokens and lopsided length pairs to avoid false positives
    that would make scoring noisy."""
    if len(token) < _FUZZY_MIN_TOKEN_LEN:
        return False
    for w in words:
        if abs(len(w) - len(token)) > 2:
            continue
        if SequenceMatcher(None, w, token).ratio() >= _FUZZY_RATIO_THRESHOLD:
            return True
    return False


def _title_stem(title: str) -> str:
    """First five content tokens of a title, joined. Used as a
    secondary dedup key — events with the same domain + title-stem
    are almost certainly the same article seen via different URLs
    (?ref=, /amp/, utm_*, …)."""
    return " ".join(_content_tokens(title)[:5])


def _collapse_spaces(s: str) -> str:
    return _WHITESPACE_RE.sub(" ", s).strip()


def _quick_token_overlap(ev: Event, tokens: List[str]) -> bool:
    """Cheap pre-filter: does any expanded token appear as a
    substring anywhere in the event's text-bearing payload?

    Uses `Event.searchable_text()` which is cached on the instance,
    so the per-event cost across many queries is just a hash lookup
    + a handful of `in` checks. The full `_score` is still
    authoritative for events that pass this filter; we just don't
    waste cycles on the 90% that don't.

    Phase 2A: combined with `Event.ts_epoch()` caching and the
    `EventStore` per-file parse cache, this took the 10K-event
    search budget from ~4.9 s to comfortably under 100 ms.
    """
    combined = ev.searchable_text()
    if not combined:
        return False
    for tok in tokens:
        if tok in combined:
            return True
    return False


def _days_for_window(window: Optional[TimeWindow]) -> int:
    """Translate a temporal window into the EventStore lookback in
    days. Always rounds up so an event at the edge of the window
    isn't accidentally excluded."""
    if window is None:
        return 14
    span_days = (window.end - window.start) / 86400.0
    return max(1, int(span_days + 1))
