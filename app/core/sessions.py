"""Session reconstruction — turn isolated events into "working sessions".

Phase 1E layers on top of Phase 1A (event log), 1B (browser ingest), and
1C (episodic retrieval). The retrieval pipeline already finds the
*moments* that match a user's query; this module finds the *activity
contexts* those moments lived inside.

The product question is "what was I doing?", not "find this exact
keyword". A session that contains three relevant events scores higher
than three isolated events — and once the user picks the session, the
launcher can hand back the entire context (every URL + every file the
user touched in that session) via "Continue this session".

Algorithm in one paragraph:

  1. Run EpisodicRetriever to find matching events. (Already pays for
     query parsing, synonyms, fuzzy match, dedup.)
  2. Group those matching events by `session_id` — the existing log
     already assigns session IDs via 30-minute gap detection.
  3. For each candidate session, fetch ALL events (matching or not)
     from the log so the user sees the full context.
  4. Score the session: sum of matching event scores + count bonus
     + diversity bonus + recency. Cap at 1.0 for display sanity.
  5. Generate a dominant-topic label from the most common content
     tokens across every event title/query in the session.
  6. Return top-N sessions, sorted by score.

No embeddings. No clustering. No topic modelling. The cheap path
already gives strong signal because events that match the same
query and share a 30-minute window are almost always about the
same thing.
"""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Iterable, List, Optional, Tuple

from .episodic import (
    EpisodicResult,
    EpisodicRetriever,
    _content_tokens,
)
from .events import Event, EventStore, humanize_age

# Every event kind a session can contain. Wider than EpisodicRetriever's
# RETRIEVABLE_KINDS — sessions are about activity context, so launcher
# queries and file opens belong here too.
SESSION_KINDS: frozenset[str] = frozenset({
    "browser_visit",
    "browser_search",
    "chat_session",
    "open",
    "reveal",
    "query",
})

# How many events to display per session card. Wider than 6 would
# bloat the launcher; narrower than 3 would lose the context.
SESSION_PREVIEW_EVENTS = 6

# Thresholds — tuned conservatively. A session needs to clear the
# minimum-confidence bar before it surfaces, and gets a diminishing
# bonus for additional matching events to stop a single noisy session
# from dominating the launcher.
_SESSION_MIN_SCORE = 0.40
_COUNT_BONUS_PER_EXTRA = 0.08
_COUNT_BONUS_CAP = 0.30
_DIVERSITY_BONUS = 0.06       # +1 distinct event kind beyond the first
_DIVERSITY_BONUS_CAP = 0.18

# Templates for human-feeling labels. Picked based on the dominant
# event kind in the session — a session of mostly searches reads as
# "Researching X", a session of mostly chats reads as "Chats about X".
_LABEL_TEMPLATES: dict[str, str] = {
    "browser_search": "Researching",
    "chat_session": "Chats about",
    "browser_visit": "Reading about",
    "open": "Working on",
    "reveal": "Working on",
    "query": "Looking for",
}


# --------------------------------------------------------------- model


@dataclass
class Session:
    """One reconstructed working session ready for the launcher to
    render. Built once per query — never cached across queries because
    a query change re-ranks which sessions are surfaced.
    """

    session_id: str
    events: List[Event] = field(default_factory=list)
    matching_events: List[Event] = field(default_factory=list)
    topic: str = ""
    label: str = ""           # full label like "Researching websocket retries"
    time_label: str = ""      # "2h ago · ~25min"
    score: float = 0.0

    @property
    def event_count(self) -> int:
        return len(self.events)

    @property
    def work_blocks(self) -> int:
        """How many behavioural work-blocks this clock session actually
        contains (Capture C5). 1 means one continuous run of attention;
        more means the 30-minute window lumped together separate
        bursts. Derived, never stored — see `workblocks.py`."""
        from .workblocks import group_work_blocks

        return len(group_work_blocks(self.events))

    @property
    def behavioural_label(self) -> str:
        """One quiet clause naming the session's attention shape, e.g.
        "one 47-minute focus block" or "3 attention blocks". Empty when
        there's no signal worth adding to the clock label."""
        from .workblocks import describe_blocks, group_work_blocks

        return describe_blocks(group_work_blocks(self.events))

    @property
    def kinds(self) -> List[str]:
        seen: set[str] = set()
        out: List[str] = []
        for ev in self.events:
            if ev.kind not in seen:
                seen.add(ev.kind)
                out.append(ev.kind)
        return out

    def preview_events(self, max_n: int = SESSION_PREVIEW_EVENTS) -> List[Event]:
        """Return up to `max_n` events from the session, dedup'd by URL/path
        and by (kind, title-stem). Newest-first so the most recent event
        in the session anchors the preview.
        """
        seen_urls: set[str] = set()
        seen_keys: set[Tuple[str, str]] = set()
        out: List[Event] = []
        # Already chronological-ascending in the Session.events list;
        # reverse so preview is newest-first.
        for ev in reversed(self.events):
            url = (ev.payload.get("url") or ev.payload.get("path") or "").strip().lower()
            title = _event_display_text(ev)
            key = (ev.kind, title.lower()[:60])
            if url and url in seen_urls:
                continue
            if key in seen_keys:
                continue
            if url:
                seen_urls.add(url)
            seen_keys.add(key)
            out.append(ev)
            if len(out) >= max_n:
                break
        return out

    def openable_targets(self) -> List[Tuple[str, str]]:
        """Return [(kind, target)] pairs for "Continue this session".
        kind is "url" or "path"; target is what to hand to the OS.
        Dedup'd identically to the preview, so a session with two visits
        to the same article only opens it once."""
        seen: set[str] = set()
        out: List[Tuple[str, str]] = []
        for ev in self.events:
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
            kind = "url" if url else "path"
            out.append((kind, target))
        return out


# --------------------------------------------------------------- helpers


def _event_display_text(ev: Event) -> str:
    """One short string suitable for showing this event inside a
    session card — title is preferred, query is fallback for searches,
    domain is the last resort."""
    p = ev.payload or {}
    if ev.kind == "browser_search":
        q = (p.get("query") or "").strip()
        if q:
            return f"“{q}”"
    if ev.kind == "query":
        text = (p.get("text") or "").strip()
        if text:
            return f"“{text}”"
    title = (p.get("title") or "").strip()
    if title:
        return title
    path = (p.get("path") or "").strip()
    if path:
        # short tail of the path so the user sees the filename
        return path.split("/")[-1].split("\\")[-1] or path
    return (p.get("domain") or p.get("url") or "Untitled moment").strip()


# A real user session rarely has more than a few dozen events; the cap
# only kicks in on pathological inputs (synthetic stress tests, long-
# running automated jobs). At 500 events the top-token frequency
# distribution is already stable, and the cost stays well under 10ms
# even on a worst-case 10K-event session.
_DERIVE_TOPIC_MAX_EVENTS = 500


def derive_topic(events: Iterable[Event], max_tokens: int = 2) -> str:
    """Frequency-based topic extraction across the session's text fields.

    Picks the top `max_tokens` content tokens (length >= 3, stopwords
    removed) by occurrence count. Returns "Untitled session" when the
    session has no usable text — rare, but possible for sessions made
    entirely of file opens with cryptic filenames.
    """
    counter: Counter = Counter()
    for idx, ev in enumerate(events):
        if idx >= _DERIVE_TOPIC_MAX_EVENTS:
            break
        p = ev.payload or {}
        for field_name in ("title", "query", "text"):
            val = (p.get(field_name) or "").strip()
            if val:
                counter.update(_content_tokens(val))
        # Filename fallback — useful when title is empty.
        path = (p.get("path") or "").strip()
        if path:
            tail = path.split("/")[-1].split("\\")[-1]
            counter.update(_content_tokens(tail))

    most = counter.most_common(max_tokens)
    if not most:
        return "Untitled session"
    return " · ".join(tok for tok, _ in most)


def derive_label(session_events: List[Event], topic: str) -> str:
    """Combine a verb template with the topic, picked by the dominant
    event kind in the session. The result is the human-readable
    headline shown in the session card.
    """
    if not session_events or topic == "Untitled session":
        return topic or "Untitled session"
    kind_counter: Counter = Counter(ev.kind for ev in session_events)
    dominant = kind_counter.most_common(1)[0][0]
    verb = _LABEL_TEMPLATES.get(dominant, "About")
    return f"{verb} {topic}"


def _dates_from_session_ids(session_ids: Iterable[str]) -> List[str]:
    """Extract the YYYY-MM-DD per-day-file dates encoded in each
    session_id and return a small set including the immediately-next
    day (to cover the rare case of a session crossing UTC midnight).

    Used by the session reconstructor's enrichment pass to skip
    walking days that can't contain any of the candidate sessions.
    """
    dates: set[str] = set()
    for sid in session_ids:
        # Format: s_YYYYMMDD_HHMMSS_microseconds
        if not isinstance(sid, str) or len(sid) < 10 or not sid.startswith("s_"):
            continue
        ymd = sid[2:10]
        if len(ymd) != 8 or not ymd.isdigit():
            continue
        base = f"{ymd[:4]}-{ymd[4:6]}-{ymd[6:8]}"
        dates.add(base)
        # Cover a session that started just before UTC midnight and
        # rolled into the next day's JSONL file.
        try:
            base_dt = datetime.strptime(base, "%Y-%m-%d")
            dates.add(
                (base_dt + timedelta(days=1)).strftime("%Y-%m-%d")
            )
        except ValueError:
            continue
    return sorted(dates, reverse=True)


def format_time_range(events: List[Event]) -> str:
    """Compose a session time label like '2h ago · ~25min'."""
    if not events:
        return ""
    times = [ev.ts_epoch() for ev in events]
    start, end = min(times), max(times)
    age = humanize_age(end)
    duration_min = max(0.0, (end - start) / 60.0)
    if duration_min < 3:
        return age
    if duration_min < 60:
        return f"{age}  ·  ~{int(round(duration_min))}min"
    hours = duration_min / 60.0
    if hours < 10:
        return f"{age}  ·  {hours:.1f}h"
    return f"{age}  ·  {int(hours)}h"


# --------------------------------------------------------------- reconstructor


class SessionReconstructor:
    """Stateless reconstructor — every call walks the event log fresh.
    Cheap because we already cap retrieval to a 14-day window; sessions
    are derived from event groupings inside that window."""

    def __init__(
        self,
        event_store: EventStore,
        episodic_retriever: EpisodicRetriever,
    ) -> None:
        self.event_store = event_store
        self.episodic_retriever = episodic_retriever

    def reconstruct_for_query(self, query: str, n: int = 2) -> List[Session]:
        """Find sessions relevant to `query` and return up to `n`,
        sorted by score (highest first).

        Tightly coupled to EpisodicRetriever's scoring: we let the
        retriever do the keyword/synonym/fuzzy/temporal/kind work, then
        group those matching events by session_id and aggregate.
        """
        if not (query or "").strip():
            return []

        # Phase 1: get matching events from the existing retrieval
        # pipeline. Lift the per-call cap so a session with many small-
        # score events isn't truncated to three before grouping.
        matching = self.episodic_retriever.search(query, n=20)
        return self.reconstruct_from_results(matching, n=n)

    def reconstruct_from_results(
        self, matching: List[EpisodicResult], n: int = 2
    ) -> List[Session]:
        """Same as `reconstruct_for_query` but starting from a
        pre-computed list of `EpisodicResult`s. Lets `/v1/search`
        share the single expensive episodic scan with the session
        layer instead of running it twice (~60ms saved on 10K-event
        logs).
        """
        if not matching:
            return []

        # Map matching events to their session_id and accumulate score.
        # We also build a (session_id, url) match set so the Phase 2
        # enrichment scan can recover the underlying `Event` objects
        # for `matching_events` in one pass — vastly cheaper than the
        # old `_find_event` per-result walk (20 walks × 10K events =
        # ~200ms on a stress test).
        session_score_pool: dict[str, float] = {}
        match_url_set: set[tuple[str, str]] = set()
        match_ts_set: set[tuple[str, float]] = set()
        for r in matching:
            sid = r.session_id
            if not sid:
                continue
            session_score_pool[sid] = session_score_pool.get(sid, 0.0) + r.score
            url_lc = (r.url or "").strip().lower()
            if url_lc:
                match_url_set.add((sid, url_lc))
            else:
                match_ts_set.add((sid, r.ts_epoch))

        if not session_score_pool:
            return []

        # Phase 2: enrich each candidate session with ALL events from
        # the log (not just matching ones) — that's what makes the
        # session card "what was I doing", not "what matched".
        #
        # Phase 2A perf: instead of walking the full 14-day log, parse
        # the date out of each candidate `session_id` and walk only
        # those per-day files (plus the next day in case a session
        # crossed UTC midnight). On a 10K-event log this drops the
        # enrichment pass from ~700ms to ~5ms.
        candidate_sids = set(session_score_pool.keys())
        candidate_dates = _dates_from_session_ids(candidate_sids)
        sessions_by_id: dict[str, List[Event]] = {sid: [] for sid in candidate_sids}
        session_match_pool: dict[str, List[Event]] = {}
        for date_str in candidate_dates:
            for ev in self.event_store.iter_events_for_date(date_str):
                sid = ev.session_id
                if sid not in candidate_sids:
                    continue
                if ev.kind in SESSION_KINDS:
                    sessions_by_id[sid].append(ev)
                # While we're already iterating this file, recover the
                # matching-event objects so `_aggregate_score` can read
                # the count without a second walk.
                ev_url_lc = (ev.payload.get("url") or "").strip().lower()
                if ev_url_lc and (sid, ev_url_lc) in match_url_set:
                    session_match_pool.setdefault(sid, []).append(ev)
                elif match_ts_set:
                    ev_ts = ev.ts_epoch()
                    for mts_key in match_ts_set:
                        if mts_key[0] == sid and abs(mts_key[1] - ev_ts) < 1.5:
                            session_match_pool.setdefault(sid, []).append(ev)
                            break

        # Phase 3: score + label each session.
        sessions: List[Session] = []
        for sid, events in sessions_by_id.items():
            if not events:
                continue
            # Chronological order — preview_events reverses to newest-first.
            events.sort(key=lambda e: e.ts_epoch())
            matching_events = session_match_pool.get(sid, [])
            base_score = session_score_pool.get(sid, 0.0)
            score = self._aggregate_score(
                base_score=base_score,
                matching_events=matching_events,
                all_events=events,
            )
            if score < _SESSION_MIN_SCORE:
                continue
            topic = derive_topic(events)
            label = derive_label(events, topic)
            time_label = format_time_range(events)
            sessions.append(
                Session(
                    session_id=sid,
                    events=events,
                    matching_events=matching_events,
                    topic=topic,
                    label=label,
                    time_label=time_label,
                    score=round(score, 4),
                )
            )

        sessions.sort(key=lambda s: s.score, reverse=True)
        return sessions[:n]

    # -- internals -------------------------------------------------------

    def _find_event(
        self,
        session_id: str,
        url: str,
        ts_epoch: float,
    ) -> Optional[Event]:
        """Recover the underlying Event from EventStore given the keys
        an EpisodicResult exposes. Walks only the per-day files
        encoded in the session_id (plus the next-day rollover) so
        large 14-day logs don't make this a hot loop."""
        target_dates = _dates_from_session_ids([session_id])
        for date_str in target_dates:
            for ev in self.event_store.iter_events_for_date(date_str):
                if ev.session_id != session_id:
                    continue
                ev_url = (ev.payload.get("url") or "").strip().lower()
                if url and ev_url == url.lower():
                    return ev
                # Fallback: timestamp match (within 1s) when URL is empty
                if not url and abs(ev.ts_epoch() - ts_epoch) < 1.5:
                    return ev
        return None

    def _aggregate_score(
        self,
        base_score: float,
        matching_events: List[Event],
        all_events: List[Event],
    ) -> float:
        """Aggregate per-event match scores into a single session score.

        Components:
          • base   = sum of EpisodicResult scores for matching events
          • count  = +0.08 per extra matching event (capped at +0.30)
          • diverse= +0.06 per distinct event kind beyond the first
                     (capped at +0.18) — sessions that mix searches +
                     visits + chats are richer context anchors than
                     single-kind sessions.
        """
        score = base_score

        n_matching = len(matching_events)
        if n_matching > 1:
            count_bonus = min(_COUNT_BONUS_CAP, (n_matching - 1) * _COUNT_BONUS_PER_EXTRA)
            score += count_bonus

        kinds = {ev.kind for ev in all_events}
        if len(kinds) > 1:
            diversity_bonus = min(_DIVERSITY_BONUS_CAP, (len(kinds) - 1) * _DIVERSITY_BONUS)
            score += diversity_bonus

        # Cap at 1.0 so display percentages stay sensible.
        return min(1.0, score)
