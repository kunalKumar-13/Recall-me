"""Memory cards, preview pane, and presentation helpers.

The product is framed as a memory layer, not a file search. Every card
shows a *memory title* (humanized filename, or a Markdown heading / code
definition picked from the chunk), a one-line "why this matched"
summary, a relevance pill, and — when applicable — a "+N sources" badge
indicating that several files cluster together as one memory.

Engine layer is untouched. Clustering and titling are pure UI heuristics
operating on the SearchResults the engine returns.
"""

from __future__ import annotations

import re
import time
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Iterable, List, Tuple

from PyQt6.QtCore import QRect, Qt, QSize, pyqtSignal
from PyQt6.QtGui import (
    QColor,
    QFont,
    QFontMetrics,
    QPainter,
    QPainterPath,
    QPen,
    QPixmap,
)
from PyQt6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QListWidgetItem,
    QScrollArea,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from ..core.parsers import CODE_EXTS
from ..core.search import SearchResult
from .styles import (
    HIGHLIGHT,
    TEXT,
    TEXT_DIM,
    TEXT_DIMMER,
)

# ----------------------------------------------------------------- ext labels

EXT_LABELS: dict[str, Tuple[str, str]] = {
    ".pdf": ("PDF", "#ef4444"),
    ".docx": ("DOC", "#3b82f6"),
    ".doc": ("DOC", "#3b82f6"),
    ".txt": ("TXT", "#9ca3af"),
    ".md": ("MD",  "#8b5cf6"),
    ".markdown": ("MD", "#8b5cf6"),
    ".rst": ("RST", "#8b5cf6"),
    ".py": ("PY",  "#3b82f6"),
    ".js": ("JS",  "#eab308"),
    ".ts": ("TS",  "#3b82f6"),
    ".tsx": ("TSX", "#06b6d4"),
    ".jsx": ("JSX", "#06b6d4"),
    ".json": ("JSON", "#10b981"),
    ".yaml": ("YML", "#f59e0b"),
    ".yml": ("YML", "#f59e0b"),
    ".toml": ("TOM", "#f59e0b"),
    ".html": ("HTM", "#ef4444"),
    ".css": ("CSS", "#06b6d4"),
    ".scss": ("CSS", "#06b6d4"),
    ".go": ("GO",  "#06b6d4"),
    ".rs": ("RS",  "#f97316"),
    ".java": ("JAVA", "#ef4444"),
    ".c": ("C",   "#3b82f6"),
    ".cpp": ("CPP", "#3b82f6"),
    ".png": ("IMG", "#10b981"),
    ".jpg": ("IMG", "#10b981"),
    ".jpeg": ("IMG", "#10b981"),
    ".sql": ("SQL", "#f59e0b"),
    ".log": ("LOG", "#9ca3af"),
    ".csv": ("CSV", "#10b981"),
    ".sh": ("SH",  "#9ca3af"),
    ".ps1": ("PS",  "#3b82f6"),
}
_DEFAULT_LABEL = ("FILE", "#9ca3af")


def label_for(ext: str) -> Tuple[str, str]:
    return EXT_LABELS.get((ext or "").lower(), _DEFAULT_LABEL)


# ----------------------------------------------------------------- file icon

# Cached painted icons keyed by (ext, size). The painter draws a unified
# "page with folded corner" template tinted by the file's accent color,
# with the type label rendered inside. Same recognisable silhouette
# across all types so the visual feel is consistent rather than random.

_ICON_CACHE: dict[Tuple[str, int], QPixmap] = {}


def _paint_file_icon(ext: str, size: int) -> QPixmap:
    label, color_hex = label_for(ext)
    pix = QPixmap(size, size)
    pix.fill(Qt.GlobalColor.transparent)
    p = QPainter(pix)
    p.setRenderHint(QPainter.RenderHint.Antialiasing)

    color = QColor(color_hex)
    fill = QColor(color)
    fill.setAlpha(40)
    border = QColor(color)
    border.setAlpha(180)

    pad = 5
    rx, ry = pad, pad
    rw, rh = size - 2 * pad, size - 2 * pad
    fold = max(8, rw // 4)
    radius = 4

    path = QPainterPath()
    path.moveTo(rx + radius, ry)
    path.lineTo(rx + rw - fold, ry)
    path.lineTo(rx + rw, ry + fold)
    path.lineTo(rx + rw, ry + rh - radius)
    path.quadTo(rx + rw, ry + rh, rx + rw - radius, ry + rh)
    path.lineTo(rx + radius, ry + rh)
    path.quadTo(rx, ry + rh, rx, ry + rh - radius)
    path.lineTo(rx, ry + radius)
    path.quadTo(rx, ry, rx + radius, ry)
    path.closeSubpath()

    p.setBrush(fill)
    p.setPen(QPen(border, 1.2))
    p.drawPath(path)

    # Folded corner triangle, slightly more saturated
    fold_path = QPainterPath()
    fold_path.moveTo(rx + rw - fold, ry)
    fold_path.lineTo(rx + rw - fold, ry + fold)
    fold_path.lineTo(rx + rw, ry + fold)
    fold_path.closeSubpath()
    fold_color = QColor(color)
    fold_color.setAlpha(80)
    p.setBrush(fold_color)
    p.setPen(QPen(border, 1.0))
    p.drawPath(fold_path)

    # Label
    p.setPen(color)
    font_size = 8 if len(label) <= 3 else 7
    p.setFont(QFont("Segoe UI", font_size, QFont.Weight.Bold))
    text_rect = QRect(rx, ry + fold, rw, rh - fold)
    p.drawText(text_rect, Qt.AlignmentFlag.AlignCenter, label)

    p.end()
    return pix


def file_icon(ext: str, size: int = 40) -> QPixmap:
    key = ((ext or "").lower(), size)
    if key not in _ICON_CACHE:
        _ICON_CACHE[key] = _paint_file_icon(key[0], size)
    return _ICON_CACHE[key]


# ----------------------------------------------------------------- relevance

# Compact one-word labels so the relevance pill recedes into metadata
# rather than competing with the title. The hover tooltip on the chip
# still names the underlying score band for users who need it.
RELEVANCE_HIGH = ("High", "#10b981")
RELEVANCE_MID = ("Match", "#8b9bff")
RELEVANCE_LOW = ("Maybe", "#9ca3af")


def relevance_label(score: float) -> Tuple[str, str]:
    if score >= 0.65:
        return RELEVANCE_HIGH
    if score >= 0.45:
        return RELEVANCE_MID
    return RELEVANCE_LOW


# ----------------------------------------------------------------- text helpers

_STOPWORDS = frozenset("""
the a an and or but of in to for from with by on at as is are was were be been being
have has had do does did this that these those it its they them their there here
not no yes if then else when where while what who which how why something some any all
about over under into onto more less most least very can could should would may might
""".split())

_WORD_RE = re.compile(r"[A-Za-z][A-Za-z0-9_]+")
_SENT_SPLIT = re.compile(r"(?<=[.!?])\s+")


def humanize_filename(name: str) -> str:
    """`reward_grading_pipeline.py` → `Reward grading pipeline`.

    Acronyms up to 4 chars stay uppercase (`API_docs.md` → `API docs`).
    """
    stem = Path(name).stem
    cleaned = re.sub(r"[_\-.]+", " ", stem).strip()
    if not cleaned:
        return name
    words = cleaned.split()
    out = []
    for i, w in enumerate(words):
        if w.isupper() and len(w) <= 4:
            out.append(w)
        elif i == 0:
            out.append(w[:1].upper() + w[1:])
        else:
            out.append(w.lower())
    return " ".join(out)


def derive_memory_title(result: SearchResult) -> str:
    """Pick a memory-feeling title. Heading-aware for Markdown, def/class
    -aware for code, humanized-filename otherwise."""
    chunk = result.chunk or result.snippet or ""
    ext = (result.ext or "").lower()

    if ext in {".md", ".markdown", ".rst"}:
        for line in chunk.splitlines():
            stripped = line.strip()
            if stripped.startswith("#"):
                title = stripped.lstrip("#").strip()
                if 4 <= len(title) <= 80:
                    return title

    if ext in CODE_EXTS:
        for raw in chunk.splitlines():
            line = raw.strip()
            for prefix in ("async def ", "def ", "class ", "function "):
                if line.startswith(prefix):
                    cleaned = line.split("(")[0].split(":")[0].strip()
                    if 4 <= len(cleaned) <= 80:
                        return cleaned
                    break

    return humanize_filename(result.name)


def explain_match(query: str, chunk: str) -> str:
    """One-line "why matched" — same algorithm as before."""
    q_terms: list[str] = []
    seen_q: set[str] = set()
    for tok in _WORD_RE.findall(query.lower()):
        if len(tok) < 3 or tok in _STOPWORDS or tok in seen_q:
            continue
        seen_q.add(tok)
        q_terms.append(tok)

    if not q_terms:
        return "Possible thematic match."

    chunk_lower = chunk.lower()
    matched: list[str] = []
    seen_m: set[str] = set()
    for term in q_terms:
        stem = term[:5]
        m = re.search(rf"\b[a-z]*{re.escape(stem)}[a-z]*\b", chunk_lower)
        if m:
            form = m.group()
            if form not in seen_m:
                seen_m.add(form)
                matched.append(form)

    if not matched:
        return "Possible thematic match."

    terms = matched[:3]
    if len(terms) == 1:
        return f"Mentions {terms[0]}."
    if len(terms) == 2:
        return f"Discusses {terms[0]} and {terms[1]}."
    return f"Covers {terms[0]}, {terms[1]}, and {terms[2]}."


def memory_summary(query: str, chunk: str) -> str:
    """Picks the most query-relevant sentence from the chunk — the
    user's own words about this idea. Used as the "About this" line in
    the preview pane."""
    if not chunk:
        return ""
    sentences = [
        s.strip() for s in _SENT_SPLIT.split(chunk)
        if 24 <= len(s.strip()) <= 220
    ]
    if not sentences:
        sentences = [chunk[:200].strip()]

    pattern = _build_highlight_pattern(query)
    if pattern is None:
        return sentences[0]

    best = sentences[0]
    best_score = -1
    for s in sentences:
        n = len(pattern.findall(s))
        if n > best_score:
            best_score = n
            best = s
    return best


def format_relative_time(mtime: float, now: float | None = None) -> str:
    """Humanize a unix timestamp into something memory-shaped:

      seconds → "moments ago"
      minutes → "12m ago"
      hours   → "3h ago"
      < 7d    → "yesterday" / "5d ago"
      < 30d   → "2w ago"
      < 365d  → "Mar 2024"   (calendar-anchored — feels like a memory)
      ≥ 365d  → "2y ago"
    """
    if not mtime:
        return ""
    if now is None:
        now = time.time()
    delta = now - mtime
    if delta < 0:
        return "just now"
    if delta < 60:
        return "moments ago"
    if delta < 3600:
        return f"{int(delta // 60)}m ago"
    if delta < 86400:
        return f"{int(delta // 3600)}h ago"
    days = delta / 86400
    if days < 2:
        return "yesterday"
    if days < 7:
        return f"{int(days)}d ago"
    if days < 30:
        weeks = max(1, int(days // 7))
        return f"{weeks}w ago"
    if days < 365:
        return datetime.fromtimestamp(mtime).strftime("%b %Y")
    years = int(days // 365)
    return f"{years}y ago" if years > 1 else "1y ago"


def safe_mtime(path: str) -> float:
    try:
        return Path(path).stat().st_mtime
    except OSError:
        return 0.0


RESURRECTION_DAYS = 90


def shorten_path(path: str, max_len: int = 60) -> str:
    p = Path(path)
    full = str(p)
    if len(full) <= max_len:
        return full
    parts = p.parts
    if len(parts) <= 3:
        return full
    sep = "\\" if "\\" in full else "/"
    return f"{parts[0]}{sep}…{sep}{parts[-2]}{sep}{parts[-1]}"


def format_snippet(text: str, max_len: int = 200) -> str:
    s = " ".join((text or "").split())
    if len(s) > max_len:
        s = s[: max_len - 1].rstrip() + "…"
    return s


_ESCAPE_TABLE = {ord("&"): "&amp;", ord("<"): "&lt;", ord(">"): "&gt;"}


def _escape_html(s: str) -> str:
    return s.translate(_ESCAPE_TABLE)


def _build_highlight_pattern(query: str) -> re.Pattern[str] | None:
    parts: list[str] = []
    for tok in _WORD_RE.findall(query):
        if len(tok) < 3:
            continue
        stem = re.escape(tok[:5])
        parts.append(rf"\b{stem}\w*")
    if not parts:
        return None
    return re.compile("|".join(parts), re.IGNORECASE)


def render_snippet_html(snippet: str, query: str) -> str:
    plain = format_snippet(snippet)
    escaped = _escape_html(plain)
    pattern = _build_highlight_pattern(query)
    if pattern is None:
        return escaped
    return pattern.sub(
        lambda m: f"<b style='color:{HIGHLIGHT}'>{m.group(0)}</b>",
        escaped,
    )


def render_excerpt_html(chunk: str, query: str, max_len: int = 800) -> str:
    text = (chunk or "").strip()
    if len(text) > max_len:
        text = text[:max_len].rstrip() + "…"
    escaped = _escape_html(text).replace("\n", "<br>")
    pattern = _build_highlight_pattern(query)
    if pattern is None:
        return escaped
    return pattern.sub(
        lambda m: f"<b style='color:{HIGHLIGHT}'>{m.group(0)}</b>",
        escaped,
    )


# ----------------------------------------------------------------- clustering


@dataclass
class MemoryGroup:
    """A memory card — one or more files that share a theme."""
    primary: SearchResult
    others: List[SearchResult] = field(default_factory=list)

    @property
    def is_cluster(self) -> bool:
        return bool(self.others)

    @property
    def all_paths(self) -> List[str]:
        return [self.primary.path] + [r.path for r in self.others]

    @property
    def all_names(self) -> List[str]:
        return [self.primary.name] + [r.name for r in self.others]

    @property
    def best_score(self) -> float:
        scores = [self.primary.score] + [r.score for r in self.others]
        return max(scores) if scores else 0.0

    @property
    def file_types(self) -> List[str]:
        exts = {self.primary.ext}
        exts.update(r.ext for r in self.others)
        exts.discard("")
        return sorted(exts)

    @property
    def is_cross_source(self) -> bool:
        return len(self.file_types) > 1 and self.is_cluster


def _content_keywords(text: str) -> set[str]:
    """5-char stems of meaningful tokens, used for cluster overlap."""
    out: set[str] = set()
    for tok in _WORD_RE.findall((text or "").lower()):
        if len(tok) < 4 or tok in _STOPWORDS:
            continue
        out.add(tok[:5])
    return out


def cluster_results(
    results: List[SearchResult], min_shared: int = 3
) -> List[MemoryGroup]:
    """Group results that share a parent folder AND `min_shared` content
    words. Conservative — only obvious clusters are merged so unrelated
    files in the same folder don't get smushed together.
    """
    if not results:
        return []

    keywords_by_path: dict[str, set[str]] = {
        r.path: _content_keywords(r.chunk or r.snippet) for r in results
    }

    groups: List[MemoryGroup] = []
    assigned: set[str] = set()
    for i, r in enumerate(results):
        if r.path in assigned:
            continue
        peers: list[SearchResult] = []
        r_parent = str(Path(r.path).parent)
        r_kw = keywords_by_path[r.path]
        for j, other in enumerate(results):
            if i == j or other.path in assigned:
                continue
            if str(Path(other.path).parent) != r_parent:
                continue
            shared = r_kw & keywords_by_path[other.path]
            if len(shared) >= min_shared:
                peers.append(other)
                assigned.add(other.path)
        assigned.add(r.path)
        groups.append(MemoryGroup(primary=r, others=peers))
    return groups


# ----------------------------------------------------------------- pill / badge


class _Pill(QLabel):
    """Tiny relevance chip — restrained to a single short word so it
    reads as metadata, not a button. Border is barely-there at 1px with
    low alpha so the pill recedes; the colored fill is enough signal."""

    def __init__(self) -> None:
        super().__init__()
        self.setFixedHeight(15)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._color = ""
        self.update_pill("Possible match", "#9ca3af")

    def update_pill(self, text: str, color: str) -> None:
        self.setText(text)
        if color != self._color:
            self.setStyleSheet(
                f"background:{color}1e;"
                f"color:{color};"
                f"border:1px solid {color}33;"
                "border-radius:7px;"
                "padding:0 6px;"
                "font-size:9px;"
                "font-weight:600;"
                "letter-spacing:0.2px;"
            )
            self._color = color
        fm = self.fontMetrics()
        self.setFixedWidth(fm.horizontalAdvance(text) + 18)


class _ClusterBadge(QLabel):
    """Small "+N" indicator that this card represents multiple files."""

    def __init__(self) -> None:
        super().__init__()
        self.setFixedHeight(15)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setStyleSheet(
            "background:rgba(139,155,255,24);"
            "color:#a4b3ff;"
            "border:1px solid rgba(139,155,255,60);"
            "border-radius:7px;"
            "padding:0 5px;"
            "font-size:9px;"
            "font-weight:600;"
        )
        self.hide()

    def update_count(self, n_others: int) -> None:
        if n_others <= 0:
            self.hide()
            return
        self.setText(f"+{n_others}")
        fm = self.fontMetrics()
        self.setFixedWidth(fm.horizontalAdvance(self.text()) + 14)
        self.show()


# ----------------------------------------------------------------- result row


class ResultItemWidget(QWidget):
    """Memory card. Holds title + why + pill + optional cluster badge.

    Sizing is tuned for command-bar restraint: 56 px tall (down from 84),
    smaller icon, tighter padding. The title and "why" lines drive the
    perceived information density — keeping them at 12.5 / 10.5 px is
    the calmest pairing that still reads at glance distance.
    """

    ROW_HEIGHT = 56
    # Title elision is generous because the title is the primary
    # identifier; the bottom row gets a tighter cap because it has to
    # share width with the cluster badge and relevance pill.
    _TITLE_MAX_W = 220
    _WHY_MAX_W = 150

    def __init__(self) -> None:
        super().__init__()
        self.group: MemoryGroup | None = None
        self._build()

    def _build(self) -> None:
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 7, 10, 7)
        layout.setSpacing(10)

        self.icon = QLabel()
        self.icon.setFixedSize(28, 28)
        self.icon.setAlignment(Qt.AlignmentFlag.AlignCenter)

        text_col = QVBoxLayout()
        text_col.setContentsMargins(0, 0, 0, 0)
        text_col.setSpacing(2)

        self.title = QLabel("")
        self.title.setStyleSheet(
            f"color:{TEXT};font-size:12.5px;font-weight:600;"
        )
        self.title.setTextFormat(Qt.TextFormat.PlainText)

        bottom_row = QHBoxLayout()
        bottom_row.setContentsMargins(0, 0, 0, 0)
        bottom_row.setSpacing(6)

        self.why = QLabel("")
        self.why.setStyleSheet(
            f"color:{TEXT_DIM};font-size:10.5px;"
        )
        self.why.setTextFormat(Qt.TextFormat.PlainText)

        self.cluster_badge = _ClusterBadge()
        self.pill = _Pill()

        bottom_row.addWidget(self.why, 1)
        bottom_row.addWidget(self.cluster_badge, 0, Qt.AlignmentFlag.AlignVCenter)
        bottom_row.addWidget(self.pill, 0, Qt.AlignmentFlag.AlignVCenter)

        text_col.addWidget(self.title)
        text_col.addLayout(bottom_row)

        layout.addWidget(self.icon, 0, Qt.AlignmentFlag.AlignTop)
        layout.addLayout(text_col, 1)

    def update_group(self, group: MemoryGroup, query: str) -> None:
        self.group = group
        primary = group.primary

        # Icon — the painted file icon is rasterised at 28 px to match
        # the slot. The cache is keyed on (ext, size) so rendering at
        # this smaller size doesn't fight with any other call site.
        self.icon.setPixmap(file_icon((primary.ext or "").lower(), 28))

        # Title — humanized memory title (heading or def-aware)
        title = derive_memory_title(primary)
        fm: QFontMetrics = self.title.fontMetrics()
        elided = fm.elidedText(title, Qt.TextElideMode.ElideRight, self._TITLE_MAX_W)
        self.title.setText(elided)
        self.title.setToolTip(title)

        # Why-matched, with optional resurrection note for old memories
        why = explain_match(query, primary.chunk or primary.snippet)
        mtime = safe_mtime(primary.path)
        if mtime:
            age_days = (time.time() - mtime) / 86400
            if age_days >= RESURRECTION_DAYS:
                why = f"{why}  ·  resurfaced from {format_relative_time(mtime)}"
        # Explicit fontMetrics elision keeps the bottom row stable when
        # results swap in mid-typing — QLabel's default clipping can
        # briefly cause layout jitter at the pill boundary.
        why_fm: QFontMetrics = self.why.fontMetrics()
        elided_why = why_fm.elidedText(
            why, Qt.TextElideMode.ElideRight, self._WHY_MAX_W
        )
        self.why.setText(elided_why)
        self.why.setToolTip(why)

        # Pill — relevance from best score in the group
        text, color = relevance_label(group.best_score)
        self.pill.update_pill(text, color)

        # Cluster badge
        self.cluster_badge.update_count(len(group.others))


def make_result_item() -> QListWidgetItem:
    item = QListWidgetItem()
    item.setSizeHint(QSize(0, ResultItemWidget.ROW_HEIGHT))
    return item


# ----------------------------------------------------------------- preview pane


class PreviewPane(QWidget):
    """Memory preview — what the user is recovering, not just the file."""

    def __init__(self) -> None:
        super().__init__()
        self.setObjectName("preview_pane")
        self._build()

    def _build(self) -> None:
        # Outer layout — holds the single scroll area that wraps the whole
        # preview. Earlier versions tried to scroll only the excerpt and
        # let everything else size naturally; that broke down when sources
        # or related grew tall. One outer scroll keeps the launcher's
        # bounds stable regardless of how much memory content is showing.
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)

        self._scroll = QScrollArea()
        self._scroll.setObjectName("preview_scroll")
        self._scroll.setFrameShape(QFrame.Shape.NoFrame)
        self._scroll.setWidgetResizable(True)
        self._scroll.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )
        # Transparent so the parent #preview_pane background shows through.
        self._scroll.setStyleSheet(
            "QScrollArea { background: transparent; border: none; }"
        )
        self._scroll.viewport().setAutoFillBackground(False)
        outer.addWidget(self._scroll)

        content = QWidget()
        content.setObjectName("preview_content")
        content.setStyleSheet("background: transparent;")
        content.setAutoFillBackground(False)
        self._scroll.setWidget(content)

        root = QVBoxLayout(content)
        # Tighter than before (was 20,18,20,18 with 10-spacing). The
        # preview should feel like contextual support beside the list,
        # not a second-class workspace with its own breathing room.
        root.setContentsMargins(14, 12, 14, 12)
        root.setSpacing(6)

        memory_label = QLabel("Memory")
        memory_label.setObjectName("preview_section_label")

        self.title = QLabel("")
        self.title.setObjectName("preview_filename")
        self.title.setWordWrap(True)
        self.title.setTextFormat(Qt.TextFormat.PlainText)

        self.path_lbl = QLabel("")
        self.path_lbl.setObjectName("preview_path")
        self.path_lbl.setWordWrap(False)
        self.path_lbl.setTextFormat(Qt.TextFormat.PlainText)

        self.last_seen_lbl = QLabel("")
        self.last_seen_lbl.setObjectName("preview_last_seen")
        self.last_seen_lbl.setTextFormat(Qt.TextFormat.PlainText)

        d1 = self._divider()

        about_label = QLabel("About")
        about_label.setObjectName("preview_section_label")

        self.about = QLabel("")
        self.about.setObjectName("preview_why")
        self.about.setWordWrap(True)

        d2 = self._divider()

        excerpt_label = QLabel("Excerpt")
        excerpt_label.setObjectName("preview_section_label")

        # Excerpt is now a plain word-wrapping QLabel — no inner scroll.
        # Long passages grow the content; the outer scroll handles overflow.
        self.excerpt = QLabel("")
        self.excerpt.setObjectName("preview_excerpt")
        self.excerpt.setWordWrap(True)
        self.excerpt.setTextFormat(Qt.TextFormat.RichText)
        self.excerpt.setAlignment(
            Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft
        )
        self.excerpt.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred
        )

        # Sources (cluster only)
        self.sources_header = QLabel("Sources")
        self.sources_header.setObjectName("preview_section_label")
        self.sources_subtitle = QLabel("")
        self.sources_subtitle.setObjectName("preview_cross_source")
        self.sources_subtitle.hide()
        self.sources_container = QWidget()
        self.sources_container.setStyleSheet("background: transparent;")
        self._sources_layout = QVBoxLayout(self.sources_container)
        self._sources_layout.setContentsMargins(0, 0, 0, 0)
        self._sources_layout.setSpacing(3)

        d3 = self._divider()

        related_header = QLabel("Related")
        related_header.setObjectName("preview_section_label")

        self.related_container = QWidget()
        self.related_container.setStyleSheet("background: transparent;")
        self._related_layout = QVBoxLayout(self.related_container)
        self._related_layout.setContentsMargins(0, 0, 0, 0)
        self._related_layout.setSpacing(3)

        root.addWidget(memory_label)
        root.addWidget(self.title)
        root.addWidget(self.path_lbl)
        root.addWidget(self.last_seen_lbl)
        root.addWidget(d1)
        root.addWidget(about_label)
        root.addWidget(self.about)
        root.addWidget(d2)
        root.addWidget(excerpt_label)
        root.addWidget(self.excerpt)
        root.addWidget(self.sources_header)
        root.addWidget(self.sources_subtitle)
        root.addWidget(self.sources_container)
        root.addWidget(d3)
        root.addWidget(related_header)
        root.addWidget(self.related_container)

        # Empty-state placeholder — single calm line shown when no memory
        # is selected. Without this, show_empty() would leave every
        # section label and divider on screen with empty bodies between
        # them, which read as a broken layout rather than a blank slate.
        self.empty_placeholder = QLabel("Select a memory to preview")
        self.empty_placeholder.setObjectName("preview_empty")
        self.empty_placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.empty_placeholder.setWordWrap(True)
        self.empty_placeholder.hide()
        root.addWidget(self.empty_placeholder)

        # Stretch keeps the content top-anchored when it's shorter than the
        # viewport — otherwise it would centre vertically.
        root.addStretch(1)

        # Track every "real content" widget in one list so show_empty()
        # can hide them as a single group (and update_group can restore
        # them) without iterating over the layout itself. Order doesn't
        # matter — only membership does.
        self._content_widgets = [
            memory_label,
            self.title,
            self.path_lbl,
            self.last_seen_lbl,
            d1,
            about_label,
            self.about,
            d2,
            excerpt_label,
            self.excerpt,
            self.sources_header,
            self.sources_subtitle,
            self.sources_container,
            d3,
            related_header,
            self.related_container,
        ]

        # Sources are only shown for clusters — start hidden
        self.sources_header.hide()
        self.sources_container.hide()

    @staticmethod
    def _divider() -> QFrame:
        d = QFrame()
        d.setObjectName("preview_divider")
        d.setFrameShape(QFrame.Shape.HLine)
        d.setFixedHeight(1)
        return d

    def show_empty(self, msg: str = "Select a memory to preview") -> None:
        # Replace the entire "section labels + dividers + empty bodies"
        # arrangement with a single centred placeholder line. This is
        # what the user sees if a query returns nothing or before any
        # selection is made — it should read as intentional blankness,
        # not as a half-rendered card.
        self.empty_placeholder.setText(msg)
        self.empty_placeholder.show()
        for w in self._content_widgets:
            w.hide()

    def update_group(
        self,
        group: MemoryGroup,
        query: str,
        related_paths: Iterable[str],
    ) -> None:
        # Restore the full preview layout. Sources/cross-source visibility
        # is then re-resolved below based on whether this group is a
        # cluster — which is why we don't track those flags via the
        # placeholder's show/hide.
        self.empty_placeholder.hide()
        for w in self._content_widgets:
            w.show()

        primary = group.primary
        chunk = primary.chunk or primary.snippet

        self.title.setText(derive_memory_title(primary))
        # Tightened to fit the now-narrower preview width (~300 px) at
        # the path label's 10.5 px font. Full path on tooltip so nothing
        # is hidden, just compacted to one tidy line.
        self.path_lbl.setText(shorten_path(primary.path, max_len=44))
        self.path_lbl.setToolTip(primary.path)

        mtime = safe_mtime(primary.path)
        self.last_seen_lbl.setText(
            f"Last seen {format_relative_time(mtime)}" if mtime else ""
        )

        self.about.setText(memory_summary(query, chunk))
        self.excerpt.setText(render_excerpt_html(chunk, query))

        # Sources + cross-source subtitle — only for clusters
        if group.is_cluster:
            self._set_sources(group.all_names)
            self.sources_header.show()
            self.sources_container.show()
            if group.is_cross_source:
                types = ", ".join(t.lstrip(".").upper() for t in group.file_types)
                self.sources_subtitle.setText(f"Spans {types} — same idea across formats.")
                self.sources_subtitle.show()
            else:
                self.sources_subtitle.hide()
        else:
            self._set_sources([])
            self.sources_header.hide()
            self.sources_container.hide()
            self.sources_subtitle.hide()

        self._set_related(list(related_paths))

    def _set_sources(self, names: List[str]) -> None:
        self._clear(self._sources_layout)
        for n in names:
            row = QLabel(f"·  {n}")
            row.setObjectName("preview_related_row")
            self._sources_layout.addWidget(row)

    def _set_related(self, paths: List[str]) -> None:
        self._clear(self._related_layout)
        if not paths:
            empty = QLabel("(no neighbors in the same folder)")
            empty.setObjectName("preview_related_empty")
            self._related_layout.addWidget(empty)
            return
        for p in paths:
            row = QLabel(f"·  {Path(p).name}")
            row.setObjectName("preview_related_row")
            row.setToolTip(p)
            self._related_layout.addWidget(row)

    @staticmethod
    def _clear(layout: QVBoxLayout) -> None:
        while layout.count():
            item = layout.takeAt(0)
            w = item.widget()
            if w is not None:
                w.deleteLater()


# ----------------------------------------------------------------- digest row


class DigestRow(QWidget):
    """Compact ambient row used in the daily digest panel.

    Click → emits `clicked(path)`. Keyboard navigation is delegated to
    the surrounding QListWidget when these are wrapped in items.
    Sized for restraint (36 px tall, 22 px icon) — the digest is
    background context, not the primary surface.
    """

    clicked = pyqtSignal(str)

    def __init__(self, path: str, mtime: float) -> None:
        super().__init__()
        self.path = path
        ext = Path(path).suffix.lower()

        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 4, 12, 4)
        layout.setSpacing(10)

        icon = QLabel()
        icon.setFixedSize(22, 22)
        icon.setPixmap(file_icon(ext, 22))

        title = QLabel(humanize_filename(Path(path).name))
        title.setStyleSheet(
            f"color:{TEXT};font-size:11.5px;font-weight:500;"
        )
        title.setTextFormat(Qt.TextFormat.PlainText)
        title.setToolTip(path)

        time_lbl = QLabel(format_relative_time(mtime))
        time_lbl.setStyleSheet(
            f"color:{TEXT_DIMMER};font-size:10.5px;"
        )

        layout.addWidget(icon)
        layout.addWidget(title, 1)
        layout.addWidget(time_lbl)

    DIGEST_ROW_HEIGHT = 36

    def mousePressEvent(self, event) -> None:  # type: ignore[override]
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit(self.path)
        super().mousePressEvent(event)
