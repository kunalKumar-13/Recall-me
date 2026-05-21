"""Micro-context reconstruction — semantic splits inside a temporal
session.

Phase 1F layers on top of Phase 1E sessions. A session is what the
event logger sees: a contiguous block of activity with <30-minute
gaps. A micro-context is what the *user* mentally was doing: a
coherent topic that may share a session with other unrelated topics.

The product question is "what was I mentally working on?", not
"what 30-minute window am I looking at?". One real session may
hold three or four mental work blocks; Phase 1F splits them.

Algorithm — a single greedy pass:

  1. De-noise the event list (drop reload-duplicates within 30 s).
  2. For each event in chronological order, compute its affinity
     against every existing micro-context.
  3. If max(affinity) clears the threshold, join that context;
     otherwise open a new one (capped at 6).
  4. Post-pass: merge singleton contexts into the temporally-
     nearest multi-event context if within 10 minutes.

Affinity is the maximum of three signals plus a temporal bonus:

  • domain match  : 0.8  (same hostname appears in the context)
  • path match    : 0.8  (same file appears in the context)
  • token Jaccard : 0.0 - 0.7 (synonym-expanded; via Phase 1C tokens)
  • temporal bonus: +0.15 if <1 min since last, +0.08 if <5 min

No embeddings. No LLM. No clustering library. The cheap path is good
enough because a person rarely pivots topic without changing at
least one of (domain, file, vocabulary) — and when they don't, the
temporal adjacency carries the assignment.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional, Tuple
from urllib.parse import urlparse

from .episodic import _content_tokens, _expand_tokens
from .events import Event
from .sessions import (
    SESSION_KINDS,
    _event_display_text,
    derive_label,
    derive_topic,
    format_time_range,
)

# Number of micro-contexts a single session can produce. Hard cap
# stops over-fragmentation; in practice 2-3 is typical.
MAX_CONTEXTS = 6

# Minimum events for the reconstructor to even attempt a split.
# Below this, a single context is returned and we don't try to
# fragment further.
MIN_EVENTS_TO_SPLIT = 3

# Affinity threshold to join an existing context. Below this, a new
# context opens — unless we're already at MAX_CONTEXTS, in which
# case the event is merged into the best-affinity existing context.
_MIN_AFFINITY_TO_JOIN = 0.20

# Component weights — each capped at 1.0 total.
_DOMAIN_MATCH_SCORE = 0.80
_PATH_MATCH_SCORE = 0.80
_TOKEN_JACCARD_SCALE = 0.70

# Temporal adjacency bonus, applied on top of the structural signal.
_TEMPORAL_NEAR_BONUS = 0.15      # < 60 s since last event in context
_TEMPORAL_MID_BONUS = 0.08       # < 300 s since last event in context
_TEMPORAL_NEAR_S = 60
_TEMPORAL_MID_S = 300

# De-noise: ignore reload-duplicates (same URL within this window).
_DENOISE_WINDOW_S = 30

# Singleton merge: a 1-event context gets merged into the nearest
# multi-event context only if the temporal gap is below this.
_SINGLETON_MERGE_GAP_S = 600


# --------------------------------------------------------------- model


@dataclass
class MicroContext:
    """One topical work block inside a session.

    `match_count` is set by the launcher after construction (zero by
    default). It carries the number of EpisodicResult-matched events
    the context contains and is used to rank micro-contexts when more
    than one is candidate-surfaceable for a single query.
    """

    events: List[Event] = field(default_factory=list)
    topic: str = ""
    label: str = ""
    time_label: str = ""
    match_count: int = 0

    @classmethod
    def from_events(cls, events: List[Event]) -> "MicroContext":
        if not events:
            return cls()
        ordered = sorted(events, key=lambda e: e.ts_epoch())
        topic = derive_topic(ordered)
        return cls(
            events=ordered,
            topic=topic,
            label=derive_label(ordered, topic),
            time_label=format_time_range(ordered),
        )

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

    def preview_events(self, max_n: int = 6) -> List[Event]:
        """Newest-first dedup'd preview list for the ContextCard."""
        seen_urls: set[str] = set()
        seen_keys: set[Tuple[str, str]] = set()
        out: List[Event] = []
        for ev in reversed(self.events):
            url = (
                ev.payload.get("url") or ev.payload.get("path") or ""
            ).strip().lower()
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
        """[(kind, target)] pairs for 'Resume context' — dedup'd."""
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


# --------------------------------------------------------------- reconstructor


class MicroContextReconstructor:
    """Stateless splitter. Construction is free; one instance can be
    reused for every session reconstruction call.

    Reads no I/O. Operates on whatever event list it's handed. Safe
    to call from a worker thread."""

    def __init__(self) -> None:
        pass

    def reconstruct(self, events: List[Event]) -> List[MicroContext]:
        """Return 0..MAX_CONTEXTS micro-contexts from `events`.

        Empty input → empty output.
        Fewer than MIN_EVENTS_TO_SPLIT events → a single context.
        Otherwise → greedy cluster + singleton merge.
        """
        if not events:
            return []
        if len(events) < MIN_EVENTS_TO_SPLIT:
            return [MicroContext.from_events(events)]

        ordered = sorted(
            (e for e in events if e.kind in SESSION_KINDS),
            key=lambda e: e.ts_epoch(),
        )
        if len(ordered) < MIN_EVENTS_TO_SPLIT:
            return [MicroContext.from_events(ordered or events)]

        denoised = _denoise(ordered)
        if len(denoised) < MIN_EVENTS_TO_SPLIT:
            return [MicroContext.from_events(denoised)]

        # Single-pass greedy cluster, structured as two phases per
        # event so we never pay the cost of token expansion when the
        # cheaper domain/path signal already settles the assignment.
        #
        # Phase A — domain/path lookup (O(1) per context, ~30K hash
        #           lookups total for a 5K-event session).
        # Phase B — synonym-expanded token Jaccard. Only fires when
        #           Phase A misses across ALL contexts. In a typical
        #           browsing session this triggers once per topic
        #           pivot, not once per event.
        #
        # Hot-path optimizations:
        #   • The domain + path lookups, the timestamp pull, and the
        #     absorb step are all inlined here. At 5K-event scale,
        #     function-call overhead alone is a measurable fraction
        #     of the perf budget.
        buckets: List[List[Event]] = []
        bucket_state: List[dict] = []

        for ev in denoised:
            payload = ev.payload or {}

            # Inline domain extraction — fast path is just dict-get +
            # lowercase. urlparse fallback only fires when domain is
            # absent (rare; the extension sets it on every event).
            d = payload.get("domain")
            if d:
                ev_domain = d.strip().lower()
            else:
                url = payload.get("url") or ""
                if url:
                    try:
                        ev_domain = (urlparse(url).hostname or "").lower()
                    except Exception:
                        ev_domain = ""
                else:
                    ev_domain = ""

            pp = payload.get("path")
            ev_path = pp.strip().lower() if pp else ""

            ev_ts = ev.ts_epoch()

            # Phase A: cheap structural match.
            direct_idx = -1
            if ev_domain or ev_path:
                for i, st in enumerate(bucket_state):
                    if ev_domain and ev_domain in st["domains"]:
                        direct_idx = i
                        break
                    if ev_path and ev_path in st["paths"]:
                        direct_idx = i
                        break

            if direct_idx >= 0:
                buckets[direct_idx].append(ev)
                st = bucket_state[direct_idx]
                if ev_domain:
                    st["domains"].add(ev_domain)
                if ev_path:
                    st["paths"].add(ev_path)
                if ev_ts > st["last_ts"]:
                    st["last_ts"] = ev_ts
                continue

            # Phase B: expand event tokens (the expensive step) and
            # walk every context for the best Jaccard + temporal hit.
            ev_tokens = _event_tokens_expanded(ev)
            best_idx = -1
            best_aff = 0.0
            if ev_tokens:
                for i, st in enumerate(bucket_state):
                    # Lazy-fill the context's token set on first need.
                    ctx_tokens = st["tokens"]
                    if not ctx_tokens:
                        # Backfill from the events we've absorbed so far.
                        ctx_tokens = set()
                        for past_ev in buckets[i]:
                            ctx_tokens |= _event_tokens_expanded(past_ev)
                        st["tokens"] = ctx_tokens
                    if not ctx_tokens:
                        continue
                    inter = ev_tokens & ctx_tokens
                    if not inter:
                        continue
                    union = ev_tokens | ctx_tokens
                    score = _TOKEN_JACCARD_SCALE * (len(inter) / len(union))
                    dt = ev_ts - st["last_ts"]
                    if dt < _TEMPORAL_NEAR_S:
                        score += _TEMPORAL_NEAR_BONUS
                    elif dt < _TEMPORAL_MID_S:
                        score += _TEMPORAL_MID_BONUS
                    if score > best_aff:
                        best_aff = score
                        best_idx = i

            if best_aff >= _MIN_AFFINITY_TO_JOIN and best_idx >= 0:
                buckets[best_idx].append(ev)
                _absorb_into_state(
                    bucket_state[best_idx], ev,
                    ev_tokens, ev_domain, ev_path,
                )
            elif len(buckets) < MAX_CONTEXTS:
                buckets.append([ev])
                bucket_state.append(
                    _new_state(ev, ev_tokens, ev_domain, ev_path)
                )
            else:
                # At cap — fold into best available even at low affinity.
                if best_idx < 0:
                    best_idx = 0
                buckets[best_idx].append(ev)
                _absorb_into_state(
                    bucket_state[best_idx], ev,
                    ev_tokens, ev_domain, ev_path,
                )

        # Post-pass: merge singletons into nearest multi-event context.
        buckets = _merge_singletons(buckets)

        return [MicroContext.from_events(b) for b in buckets if b]


# --------------------------------------------------------------- helpers


def _domain_of(ev: Event) -> str:
    p = ev.payload or {}
    d = (p.get("domain") or "").strip().lower()
    if d:
        return d
    url = (p.get("url") or "").strip()
    if not url:
        return ""
    try:
        return (urlparse(url).hostname or "").lower()
    except Exception:
        return ""


def _path_of(ev: Event) -> str:
    p = ev.payload or {}
    return (p.get("path") or "").strip().lower()


def _event_tokens_expanded(ev: Event) -> set[str]:
    """Synonym-expanded content tokens from every text-bearing field
    in the event payload. Returned as a set for O(1) intersection."""
    p = ev.payload or {}
    text_parts: list[str] = []
    for k in ("title", "query", "text", "tab_title"):
        v = (p.get(k) or "").strip()
        if v:
            text_parts.append(v)
    path = (p.get("path") or "").strip()
    if path:
        tail = path.split("/")[-1].split("\\")[-1]
        if tail:
            text_parts.append(tail)
    if not text_parts:
        return set()
    base = _content_tokens(" ".join(text_parts))
    return set(_expand_tokens(base))


def _denoise(events: List[Event]) -> List[Event]:
    """Drop reload-duplicates: identical URLs within
    `_DENOISE_WINDOW_S` of each other. Preserves the first
    occurrence; later ones inside the window are skipped."""
    last_seen: dict[str, float] = {}
    out: List[Event] = []
    for ev in events:
        url = (ev.payload.get("url") or "").strip().lower()
        ts = ev.ts_epoch()
        if url:
            prev_ts = last_seen.get(url)
            if prev_ts is not None and (ts - prev_ts) < _DENOISE_WINDOW_S:
                continue
            last_seen[url] = ts
        out.append(ev)
    return out


def _new_state(
    ev: Event,
    tokens: set[str],
    domain: str,
    path: str,
) -> dict:
    """Cached affinity inputs for a context — built once per
    new-context-opening and updated as events are absorbed."""
    return {
        "tokens": set(tokens),
        "domains": {domain} if domain else set(),
        "paths": {path} if path else set(),
        "last_ts": ev.ts_epoch(),
    }


def _absorb_into_state(
    state: dict,
    ev: Event,
    tokens: Optional[set[str]],
    domain: str,
    path: str,
) -> None:
    # `tokens=None` means the caller skipped token expansion entirely
    # (Phase A domain/path hit). The context's token set will be
    # backfilled lazily next time Phase B needs it for *another* event.
    if tokens:
        state["tokens"].update(tokens)
    if domain:
        state["domains"].add(domain)
    if path:
        state["paths"].add(path)
    ts = ev.ts_epoch()
    if ts > state["last_ts"]:
        state["last_ts"] = ts


def _affinity_with_state(
    ev_tokens: set[str],
    ev_domain: str,
    ev_path: str,
    ev_ts: float,
    state: dict,
) -> float:
    """Same affinity formula as the docstring up top, but reading
    pre-computed state for the context instead of iterating events.

    Performance — at session sizes typical for users (50-500 events),
    this is hash lookups + set intersection, well inside the perf
    budget. For pathological 5k-event sessions, we walk MAX_CONTEXTS
    states once per event = ~30k cheap lookups total.
    """
    score = 0.0

    # Domain match wins outright when present.
    if ev_domain and ev_domain in state["domains"]:
        score = _DOMAIN_MATCH_SCORE
    elif ev_path and ev_path in state["paths"]:
        score = _PATH_MATCH_SCORE
    elif ev_tokens and state["tokens"]:
        inter = ev_tokens & state["tokens"]
        if inter:
            union = ev_tokens | state["tokens"]
            score = _TOKEN_JACCARD_SCALE * (len(inter) / len(union))

    # Temporal adjacency layered on top.
    dt = ev_ts - state["last_ts"]
    if dt < _TEMPORAL_NEAR_S:
        score += _TEMPORAL_NEAR_BONUS
    elif dt < _TEMPORAL_MID_S:
        score += _TEMPORAL_MID_BONUS

    return min(1.0, score)


def _merge_singletons(buckets: List[List[Event]]) -> List[List[Event]]:
    """Merge singleton contexts into the temporally-nearest multi-
    event context, but only when the gap is below
    `_SINGLETON_MERGE_GAP_S`. Lone events outside that window are
    kept as their own context (they're real topical pivots that
    happened to produce one event).

    If every bucket is a singleton (a session of one event per topic),
    we keep them all — there's nothing to merge into.
    """
    multi_indices = [i for i, b in enumerate(buckets) if len(b) >= 2]
    if not multi_indices:
        return [b for b in buckets if b]

    keep: List[List[Event]] = [list(b) for b in buckets]
    dropped: set[int] = set()

    for i, ctx in enumerate(buckets):
        if len(ctx) != 1 or i in dropped:
            continue
        ev = ctx[0]
        best_j = -1
        best_dt = float("inf")
        for j in multi_indices:
            if j == i:
                continue
            for target_ev in buckets[j]:
                dt = abs(ev.ts_epoch() - target_ev.ts_epoch())
                if dt < best_dt:
                    best_dt = dt
                    best_j = j
        if best_j >= 0 and best_dt < _SINGLETON_MERGE_GAP_S:
            keep[best_j].append(ev)
            keep[best_j].sort(key=lambda e: e.ts_epoch())
            dropped.add(i)

    return [b for i, b in enumerate(keep) if i not in dropped and b]
