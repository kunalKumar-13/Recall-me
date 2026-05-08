"""Text chunking — paragraph-aware with sliding-window fallback, plus a
chunk-quality filter that drops low-information boilerplate.

Embedding quality degrades when chunks are too small (no context) or too
large (one embedding diluted across many topics). We aim for chunks near
`chunk_size` characters, snapping to paragraph boundaries when possible
and overlapping enough to preserve cross-boundary context.

We then filter out chunks that look like noise — typical examples are
import blocks (one identifier repeated many times), license headers,
files of mostly punctuation/symbols, and chunks too short to embed
meaningfully. Without this filter, a code file with hundreds of import
chunks competes with prose at query time and pulls ranking quality down.
"""

from __future__ import annotations

import re
from collections import Counter
from typing import List

_TOKEN_RE = re.compile(r"[A-Za-z][A-Za-z0-9_]+")

_MIN_CHUNK_CHARS = 40
_MIN_TOKENS = 8
_MAX_TOKEN_REPETITION = 0.25   # any single token may not exceed 25% of all tokens
_MIN_ALPHA_RATIO = 0.40        # at least 40% of chars must be letters


def _is_meaningful_chunk(text: str) -> bool:
    """Heuristic filter — returns False for chunks that look like boilerplate.

    Catches:
      - imports (one identifier dominates token frequency)
      - shebang / encoding / pure-symbol headers
      - tables of mostly punctuation
      - chunks too short to carry meaning
    """
    s = text.strip()
    if len(s) < _MIN_CHUNK_CHARS:
        return False

    tokens = _TOKEN_RE.findall(s.lower())
    if len(tokens) < _MIN_TOKENS:
        return False

    most_common_count = Counter(tokens).most_common(1)[0][1]
    if most_common_count > len(tokens) * _MAX_TOKEN_REPETITION:
        return False

    alpha = sum(1 for c in text if c.isalpha())
    if alpha < len(text) * _MIN_ALPHA_RATIO:
        return False

    return True


def chunk_text(text: str, chunk_size: int = 800, overlap: int = 100) -> List[str]:
    if not text or not text.strip():
        return []

    text = text.replace("\r\n", "\n").replace("\r", "\n")
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
    if not paragraphs:
        paragraphs = [text]

    chunks: List[str] = []
    current = ""
    for para in paragraphs:
        if not current:
            current = para
            continue
        if len(current) + len(para) + 2 <= chunk_size:
            current = f"{current}\n\n{para}"
        else:
            chunks.append(current)
            tail = current[-overlap:] if overlap > 0 and len(current) > overlap else ""
            current = f"{tail}\n\n{para}" if tail else para
    if current:
        chunks.append(current)

    final: List[str] = []
    for c in chunks:
        if len(c) <= int(chunk_size * 1.5):
            final.append(c)
            continue
        step = max(1, chunk_size - overlap)
        for i in range(0, len(c), step):
            piece = c[i : i + chunk_size]
            if piece.strip():
                final.append(piece)

    return [c for c in final if _is_meaningful_chunk(c)]
