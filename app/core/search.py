"""Semantic search — query → embedding → top-k chunks → file-level dedupe.

Quality knobs:

- `min_score` floor cuts sub-similarity noise. With normalized embeddings
  and Chroma's cosine distance, scores under ~0.30 are essentially random
  matches; surfacing them dilutes good results.
- Snippet selection windows the chunk text around the densest cluster of
  query-token occurrences, snapping to sentence/word boundaries.
- Ranking applies four small, capped boosts on top of the cosine score:
    * filename_bonus  — query terms appearing in the file name
    * recency_bonus   — files modified within ~30 / 90 days
    * phrase_bonus    — exact query phrase appearing in the chunk
  Each is intentionally small so semantic similarity stays dominant; they
  break ties between near-equal results without overriding strong matches.
- Query is normalized (whitespace collapsed) before embedding so leading
  spaces or duplicated tokens don't pollute the input vector.
"""

from __future__ import annotations

import re
import time
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional

from ..db.store import VectorStore
from .embeddings import EmbeddingModel

DEFAULT_MIN_SCORE = 0.30
SNIPPET_MAX_LEN = 360

# Boost ceilings — small enough that semantic ranking still dominates.
FILENAME_BONUS_PER_TERM = 0.04
FILENAME_BONUS_MAX = 0.12
RECENCY_BONUS_FRESH = 0.025      # within 30 days
RECENCY_BONUS_RECENT = 0.012     # within 90 days
PHRASE_BONUS = 0.04
TOTAL_BOOST_CAP = 0.18

_QUERY_TOKEN_RE = re.compile(r"[A-Za-z][A-Za-z0-9_]+")
_NORMALIZE_RE = re.compile(r"\s+")


def _normalize_query(query: str) -> str:
    """Trim and collapse internal whitespace. The embedding model
    handles case, but normalized whitespace prevents pathological
    queries (multiple spaces, trailing newlines) from shifting the
    embedding subtly."""
    return _NORMALIZE_RE.sub(" ", (query or "").strip())


def _content_terms(query: str) -> list[str]:
    """Lowercase tokens of length >= 3, used for keyword-based boosts."""
    return [t for t in _QUERY_TOKEN_RE.findall(query.lower()) if len(t) >= 3]


_SENTENCE_TERMINATORS = ".!?\n"


def _snap_left(chunk: str, pos: int, max_back: int = 50) -> int:
    """Move `pos` left to the start of a sentence, or to a word boundary."""
    if pos <= 0:
        return 0
    # Prefer sentence terminator just before our anchor
    for i in range(pos, max(0, pos - max_back), -1):
        if i > 0 and chunk[i - 1] in _SENTENCE_TERMINATORS:
            j = i
            while j < len(chunk) and chunk[j].isspace():
                j += 1
            return j
    # Fall back to a word boundary
    while pos > 0 and not chunk[pos - 1].isspace():
        pos -= 1
    return pos


def _snap_right(chunk: str, pos: int, max_fwd: int = 50) -> int:
    """Move `pos` right to the end of a sentence, or to a word boundary."""
    if pos >= len(chunk):
        return len(chunk)
    for i in range(pos, min(len(chunk), pos + max_fwd)):
        if chunk[i] in _SENTENCE_TERMINATORS:
            return min(i + 1, len(chunk))
    while pos < len(chunk) and not chunk[pos].isspace():
        pos += 1
    return pos


def _select_snippet(chunk: str, query: str, max_len: int = SNIPPET_MAX_LEN) -> str:
    """Return up to ~`max_len` chars of `chunk` windowed around the densest
    cluster of query-token occurrences. Window edges are snapped to
    sentence or word boundaries so the snippet reads as a clean fragment.
    """
    chunk = (chunk or "").strip()
    if len(chunk) <= max_len:
        return chunk

    tokens = [t.lower() for t in _QUERY_TOKEN_RE.findall(query) if len(t) >= 3]
    if not tokens:
        return chunk[:max_len].rstrip() + "…"

    text_lower = chunk.lower()
    positions: list[int] = []
    for tok in tokens:
        idx = 0
        while True:
            j = text_lower.find(tok, idx)
            if j < 0:
                break
            positions.append(j)
            idx = j + len(tok)

    if not positions:
        return chunk[:max_len].rstrip() + "…"

    # Center the window on the densest cluster: the position whose
    # neighborhood (of size max_len) contains the most other matches.
    best_anchor = positions[0]
    best_count = 0
    for p in positions:
        count = sum(1 for q in positions if abs(q - p) < max_len)
        if count > best_count:
            best_count = count
            best_anchor = p

    raw_start = max(0, best_anchor - max_len // 3)
    raw_end = min(len(chunk), raw_start + max_len)
    if raw_end == len(chunk):
        raw_start = max(0, raw_end - max_len)

    start = _snap_left(chunk, raw_start)
    end = _snap_right(chunk, raw_end)

    body = chunk[start:end].strip()
    prefix = "…" if start > 0 else ""
    suffix = "…" if end < len(chunk) else ""
    return f"{prefix}{body}{suffix}"


@dataclass
class SearchResult:
    path: str
    name: str
    snippet: str
    chunk: str          # full chunk text — used by the preview pane
    score: float
    ext: str
    chunk_index: int

    @property
    def folder(self) -> str:
        try:
            return str(Path(self.path).parent)
        except Exception:
            return ""


class SearchEngine:
    def __init__(self, store: VectorStore, model: EmbeddingModel) -> None:
        self.store = store
        self.model = model

    def search(
        self,
        query: str,
        top_k: int = 8,
        min_score: Optional[float] = None,
        dedupe_by_file: bool = True,
    ) -> List[SearchResult]:
        query = _normalize_query(query)
        if not query:
            return []

        floor = DEFAULT_MIN_SCORE if min_score is None else float(min_score)

        emb = self.model.encode_one(query)
        # Over-fetch when deduping so we still surface enough distinct files,
        # and so the floor doesn't strand us with too few results.
        n = top_k * 4 if dedupe_by_file else top_k
        raw = self.store.query(emb, n_results=n)

        # Pre-compute the keyword-boost inputs once per query.
        qterms = _content_terms(query)
        qphrase = query.lower() if " " in query else None
        now = time.time()

        # First pass: dedupe by path (best chunk per file) and apply boosts.
        seen: set[str] = set()
        candidates: List[SearchResult] = []
        for r in raw:
            meta = r.get("metadata") or {}
            path = meta.get("path", "")
            if not path or (dedupe_by_file and path in seen):
                continue
            base = max(0.0, 1.0 - float(r.get("distance", 1.0)))
            if base < floor:
                continue
            seen.add(path)

            chunk = r.get("document") or ""
            name = meta.get("name") or Path(path).name

            # Filename boost — small per matched term, capped.
            filename_bonus = 0.0
            if qterms:
                lname = name.lower()
                hits = sum(1 for t in qterms if t in lname)
                filename_bonus = min(FILENAME_BONUS_MAX, hits * FILENAME_BONUS_PER_TERM)

            # Recency boost — fresher files get a small nudge.
            recency_bonus = 0.0
            mtime = meta.get("mtime")
            if mtime:
                try:
                    age_days = (now - float(mtime)) / 86400.0
                    if age_days < 30:
                        recency_bonus = RECENCY_BONUS_FRESH
                    elif age_days < 90:
                        recency_bonus = RECENCY_BONUS_RECENT
                except (TypeError, ValueError):
                    pass

            # Exact-phrase boost — only meaningful for multi-word queries.
            phrase_bonus = 0.0
            if qphrase and qphrase in chunk.lower():
                phrase_bonus = PHRASE_BONUS

            total_boost = min(
                TOTAL_BOOST_CAP,
                filename_bonus + recency_bonus + phrase_bonus,
            )
            boosted = min(1.0, base + total_boost)

            candidates.append(
                SearchResult(
                    path=path,
                    name=name,
                    snippet=_select_snippet(chunk, query),
                    chunk=chunk,
                    score=boosted,
                    ext=meta.get("ext", ""),
                    chunk_index=int(meta.get("chunk_index") or 0),
                )
            )

        # Re-sort by boosted score and trim — without this the boosts only
        # change displayed scores, not actual ranking.
        candidates.sort(key=lambda r: r.score, reverse=True)
        return candidates[:top_k]
