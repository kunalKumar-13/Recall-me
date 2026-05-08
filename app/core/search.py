"""Semantic search — query → embedding → top-k chunks → file-level dedupe.

Quality knobs:

- `min_score` floor cuts sub-similarity noise. With normalized embeddings
  and Chroma's cosine distance, scores under ~0.30 are essentially random
  matches; surfacing them dilutes good results.
- Snippet selection windows the chunk text around the first occurrence of
  a query token, so the displayed text contains the relevant region even
  for chunks longer than the snippet budget.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional

from ..db.store import VectorStore
from .embeddings import EmbeddingModel

DEFAULT_MIN_SCORE = 0.30
SNIPPET_MAX_LEN = 360

_QUERY_TOKEN_RE = re.compile(r"[A-Za-z][A-Za-z0-9_]+")


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
        query = query.strip()
        if not query:
            return []

        floor = DEFAULT_MIN_SCORE if min_score is None else float(min_score)

        emb = self.model.encode_one(query)
        # Over-fetch when deduping so we still surface enough distinct files,
        # and so the floor doesn't strand us with too few results.
        n = top_k * 4 if dedupe_by_file else top_k
        raw = self.store.query(emb, n_results=n)

        seen: set[str] = set()
        out: List[SearchResult] = []
        for r in raw:
            meta = r.get("metadata") or {}
            path = meta.get("path", "")
            if not path or (dedupe_by_file and path in seen):
                continue
            score = max(0.0, 1.0 - float(r.get("distance", 1.0)))
            if score < floor:
                continue
            seen.add(path)
            chunk = r.get("document") or ""
            out.append(
                SearchResult(
                    path=path,
                    name=meta.get("name") or Path(path).name,
                    snippet=_select_snippet(chunk, query),
                    chunk=chunk,
                    score=score,
                    ext=meta.get("ext", ""),
                    chunk_index=int(meta.get("chunk_index") or 0),
                )
            )
            if len(out) >= top_k:
                break
        return out
