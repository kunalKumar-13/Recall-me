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

from ..core.events import humanize_age
from ..core.microcontexts import MicroContext
from ..core.parsers import CODE_EXTS
from ..core.search import SearchResult
from ..core.sessions import Session, _event_display_text
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

    def show_episodic(self, result, neighbors=None) -> None:
        """Render a tight episodic preview for a selected EpisodicResult.

        Reuses the same content widgets as `update_group()` but with
        episodic-shaped copy: a "Memory" section showing the title,
        subtitle, and URL; an "About" section with a one-line summary;
        an optional "Around the same time" section listing 1-2 events
        that share the session (passed in by the launcher).

        Excerpt + Sources + Related are hidden — episodic moments
        don't have file excerpts or related-folder peers.
        """
        self.empty_placeholder.hide()
        for w in self._content_widgets:
            w.show()

        self.title.setText(result.title)
        # url field gets the shortened URL; full on tooltip.
        url = (result.url or "").strip()
        self.path_lbl.setText(shorten_path(url, max_len=44) if url else "—")
        self.path_lbl.setToolTip(url or "")

        # last_seen label: when this happened.
        ts = result.ts_epoch
        self.last_seen_lbl.setText(
            f"Captured {format_relative_time(ts)}" if ts else ""
        )

        # About — one-line summary derived from kind + subtitle.
        kind_label = {
            "browser_visit": "A page you visited",
            "browser_search": "A search you ran",
            "chat_session": "A chat session you had",
        }.get(result.kind, "A moment from your activity")
        self.about.setText(f"{kind_label}.  {result.subtitle}")

        # Excerpt is hidden for episodic — the title IS the moment.
        self.excerpt.hide()
        # Find the labels we just stripped of meaning by walking
        # _content_widgets and hiding the excerpt label too.
        for w in self._content_widgets:
            # Hide every "preview_section_label" whose text is the
            # excerpt header. Cheap text-match; survives label rewording.
            try:
                if w is self.excerpt:
                    continue
                if (
                    hasattr(w, "objectName")
                    and w.objectName() == "preview_section_label"
                    and w.text() == "Excerpt"
                ):
                    w.hide()
            except Exception:
                pass

        # Sources never apply to episodic.
        self._set_sources([])
        self.sources_header.hide()
        self.sources_subtitle.hide()
        self.sources_container.hide()

        # "Around the same time" — repurpose the related row container.
        nb = list(neighbors or [])
        if nb:
            self._set_episodic_neighbors(nb)
        else:
            self._set_related([])

    def _set_episodic_neighbors(self, events) -> None:
        """Populate the related-rows container with same-session
        neighbors. Borrows the existing layout so we don't have to
        spawn another QWidget hierarchy for an MVP."""
        self._clear(self._related_layout)
        for ev in events:
            payload = ev.payload or {}
            title = (
                payload.get("title")
                or payload.get("query")
                or payload.get("domain")
                or "Untitled moment"
            )
            row = QLabel(f"·  {title}")
            row.setObjectName("preview_related_row")
            self._related_layout.addWidget(row)

    def show_context(self, ctx) -> None:
        """Render a MicroContext in the preview pane.

        Same widget hierarchy as `show_session()`, narrower copy
        because a micro-context is a tighter topical slice — it's
        always a subset of a session, never larger. The pill is
        cyan-tinted in the launcher card; the preview here doesn't
        repeat the tint, it speaks in the same calm voice as every
        other preview state.
        """
        self.empty_placeholder.hide()
        for w in self._content_widgets:
            w.show()

        self.title.setText(ctx.label)
        self.path_lbl.setText(
            f"{ctx.event_count} events  ·  {ctx.time_label}"
        )
        self.path_lbl.setToolTip(ctx.time_label)
        self.last_seen_lbl.setText(f"Topic  ·  {ctx.topic}")

        n_kinds = len(ctx.kinds)
        kind_summary = ", ".join(ctx.kinds[:4])
        self.about.setText(
            f"A topical work block of {ctx.event_count} events "
            f"across {n_kinds} kind(s): {kind_summary}."
        )

        # Excerpt + sources don't apply.
        self.excerpt.hide()
        self.sources_header.hide()
        self.sources_subtitle.hide()
        self.sources_container.hide()

        # Full event list in the related-rows container.
        self._clear(self._related_layout)
        for ev in ctx.events:
            glyph = SessionCard._kind_glyph(ev.kind)
            text = _event_display_text(ev)
            row = QLabel(f"{glyph}  {text}")
            row.setObjectName("preview_related_row")
            row.setToolTip(text)
            self._related_layout.addWidget(row)

    def show_session(self, session) -> None:
        """Render a Session in the preview pane.

        Reuses the same widget hierarchy as `update_group()` but with
        session-shaped copy: the label is the session topic, the path
        line carries the time range + event count, the "About" block
        carries a one-line summary of what kinds of events are in the
        session, and the related-rows container becomes a full event
        list (every event in the session, not just the preview).

        Excerpt + Sources are hidden because sessions don't have
        excerpts or cluster-style file sources.
        """
        self.empty_placeholder.hide()
        for w in self._content_widgets:
            w.show()

        self.title.setText(session.label)
        self.path_lbl.setText(
            f"{session.event_count} events  ·  {session.time_label}"
        )
        self.path_lbl.setToolTip(session.time_label)

        # The "Last seen" line gets the session id — useful when the
        # user wants to inspect the raw log file for this session.
        self.last_seen_lbl.setText(f"Session id  ·  {session.session_id}")

        n_kinds = len(session.kinds)
        kind_summary = ", ".join(session.kinds[:4])
        self.about.setText(
            f"A working session containing {session.event_count} events "
            f"across {n_kinds} kind(s): {kind_summary}."
        )

        # Hide excerpt + sources for sessions.
        self.excerpt.hide()
        self.sources_header.hide()
        self.sources_subtitle.hide()
        self.sources_container.hide()

        # Show every event in the session in the related-rows container.
        self._clear(self._related_layout)
        for ev in session.events:
            kind_glyph = SessionCard._kind_glyph(ev.kind)
            text = _event_display_text(ev)
            row = QLabel(f"{kind_glyph}  {text}")
            row.setObjectName("preview_related_row")
            row.setToolTip(text)
            self._related_layout.addWidget(row)

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


# ----------------------------------------------------------------- query row


class QueryRow(QWidget):
    """One row in the launcher's "Lately you searched" digest section.

    Visually quieter than DigestRow (no file-icon glyph; just a small
    lavender dot as a rhythm marker, the query text, and a relative
    timestamp). Click → emits `clicked(query_text)` so the launcher can
    repopulate the input and re-run the search.
    """

    QUERY_ROW_HEIGHT = 30

    clicked = pyqtSignal(str)

    def __init__(self, text: str, ts_epoch: float) -> None:
        super().__init__()
        self.text = text

        layout = QHBoxLayout(self)
        layout.setContentsMargins(14, 4, 14, 4)
        layout.setSpacing(10)

        # Lavender dot — same accent as the digest section labels and
        # the launcher's selection chrome, so the row visually belongs
        # to the same family without needing its own icon system.
        dot = QLabel()
        dot.setFixedSize(6, 6)
        dot.setStyleSheet(
            "background: rgba(181, 168, 255, 0.55);"
            "border-radius: 3px;"
        )

        title = QLabel(text)
        title.setStyleSheet(
            f"color:{TEXT};font-size:11.5px;"
        )
        title.setTextFormat(Qt.TextFormat.PlainText)
        title.setToolTip(text)

        time_lbl = QLabel(humanize_age(ts_epoch))
        time_lbl.setStyleSheet(
            f"color:{TEXT_DIMMER};font-size:10.5px;"
        )

        layout.addWidget(dot, 0, Qt.AlignmentFlag.AlignVCenter)
        layout.addWidget(title, 1)
        layout.addWidget(time_lbl, 0, Qt.AlignmentFlag.AlignVCenter)

    def mousePressEvent(self, event) -> None:  # type: ignore[override]
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit(self.text)
        super().mousePressEvent(event)


# ----------------------------------------------------------------- browser row


class BrowserActivityRow(QWidget):
    """One row in the launcher's "Recent digital activity" digest.

    Mirrors QueryRow's visual rhythm — a single-line, small lavender
    dot, title text, dim relative time on the right — but with the dot
    color encoding the event type:

      • lavender — page visit
      • cyan     — search
      • mint     — chat session

    The row carries the original URL on its `url` attribute and emits
    `clicked(url)` so the launcher can hand it to the OS default
    browser. We do not store the event itself on the row to keep the
    surface narrow.
    """

    ACTIVITY_ROW_HEIGHT = 32

    clicked = pyqtSignal(str)

    # Per-kind tints. Stored as (rgba_hex_alpha, hover_alpha).
    _DOT_COLORS = {
        "browser_visit": "rgba(181, 168, 255, 0.65)",
        "browser_search": "rgba(125, 216, 232, 0.75)",
        "chat_session": "rgba(135, 222, 183, 0.75)",
    }

    def __init__(
        self,
        kind: str,
        title: str,
        subtitle: str,
        ts_epoch: float,
        url: str,
    ) -> None:
        super().__init__()
        self.url = url
        self.kind = kind

        layout = QHBoxLayout(self)
        layout.setContentsMargins(14, 5, 14, 5)
        layout.setSpacing(10)

        dot = QLabel()
        dot.setFixedSize(6, 6)
        dot.setStyleSheet(
            f"background: {self._DOT_COLORS.get(kind, self._DOT_COLORS['browser_visit'])};"
            "border-radius: 3px;"
        )

        # Title column: primary title on top, faint subtitle below.
        title_col = QVBoxLayout()
        title_col.setContentsMargins(0, 0, 0, 0)
        title_col.setSpacing(0)

        title_lbl = QLabel(title)
        title_lbl.setStyleSheet(
            f"color:{TEXT};font-size:11.5px;"
        )
        title_lbl.setTextFormat(Qt.TextFormat.PlainText)
        title_lbl.setToolTip(url or title)

        subtitle_lbl = QLabel(subtitle)
        subtitle_lbl.setStyleSheet(
            f"color:{TEXT_DIMMER};font-size:10px;"
        )
        subtitle_lbl.setTextFormat(Qt.TextFormat.PlainText)

        title_col.addWidget(title_lbl)
        if subtitle:
            title_col.addWidget(subtitle_lbl)

        time_lbl = QLabel(humanize_age(ts_epoch))
        time_lbl.setStyleSheet(
            f"color:{TEXT_DIMMER};font-size:10.5px;"
        )

        layout.addWidget(dot, 0, Qt.AlignmentFlag.AlignTop)
        layout.addLayout(title_col, 1)
        layout.addWidget(time_lbl, 0, Qt.AlignmentFlag.AlignVCenter)

    def mousePressEvent(self, event) -> None:  # type: ignore[override]
        if event.button() == Qt.MouseButton.LeftButton and self.url:
            self.clicked.emit(self.url)
        super().mousePressEvent(event)


# ----------------------------------------------------------------- resurfaced row


class ResurfacedRow(QWidget):
    """One row in the launcher's "Continue where you left off" digest.

    Visually quieter than even the QueryRow — the row gets a single
    hairline-thin dot in `lavender-deep` (no kind colour-coding; this
    is not a feed), a 1-line label, and a dim, *plain-language* time
    span on the right ("yesterday · across 2 days"). No badge, no
    progress chevron, no confidence number — the only state we ever
    surface to the user is "this looks like something you were
    thinking about".

    The full "why am I seeing this?" explanation is wired onto
    `setToolTip` so it appears on hover, but *only when debug mode is
    on at construction time* — production users get no hover at all,
    which is what the brief asks for.

    `target` carries the most-recent openable URL or filesystem path
    (whichever the engine surfaced). Click → emits `clicked(kind,
    target)`; the launcher passes that to the same handler it uses
    for digest rows.
    """

    RESURFACED_ROW_HEIGHT = 32

    # `kind` is "url" or "path"; `target` is what to hand to the OS.
    clicked = pyqtSignal(str, str)

    def __init__(
        self,
        label: str,
        time_label: str,
        kind: str,
        target: str,
        why_lines: List[str] | None = None,
        debug_hover: bool = False,
    ) -> None:
        super().__init__()
        self.kind = kind
        self.target = target

        layout = QHBoxLayout(self)
        layout.setContentsMargins(14, 4, 14, 4)
        layout.setSpacing(10)

        # Single small dot — same lavender as the other digest rows
        # so this section belongs visually without announcing itself.
        dot = QLabel()
        dot.setFixedSize(6, 6)
        dot.setStyleSheet(
            "background: rgba(181, 168, 255, 0.55);"
            "border-radius: 3px;"
        )

        title = QLabel(label or "Untitled")
        title.setStyleSheet(
            f"color:{TEXT};font-size:11.5px;"
        )
        title.setTextFormat(Qt.TextFormat.PlainText)
        # No setToolTip(label) — we reserve hover for the debug "why".

        time_lbl = QLabel(time_label or "")
        time_lbl.setStyleSheet(
            f"color:{TEXT_DIMMER};font-size:10.5px;"
        )

        layout.addWidget(dot, 0, Qt.AlignmentFlag.AlignVCenter)
        layout.addWidget(title, 1)
        layout.addWidget(time_lbl, 0, Qt.AlignmentFlag.AlignVCenter)

        if debug_hover and why_lines:
            # "Why am I seeing this?" — debug-only. The wording is
            # observational, not predictive. Lines come from the
            # engine's `_explain` so we don't fabricate reasons here.
            tip = (
                "Why am I seeing this?\n  · "
                + "\n  · ".join(why_lines)
            )
            self.setToolTip(tip)
            for w in (title, time_lbl, dot):
                w.setToolTip(tip)

    def mousePressEvent(self, event) -> None:  # type: ignore[override]
        if event.button() == Qt.MouseButton.LeftButton and self.target:
            self.clicked.emit(self.kind, self.target)
        super().mousePressEvent(event)


# ----------------------------------------------------------------- recovery row


class RecoveryRow(QWidget):
    """A "continue where you left off" row — the primary launcher
    idle surface (Phase 3B).

    Two visual lines + a stacked target-count strip on the right:

      ┌───────────────────────────────────────────────────────┐
      │ │ WebSocket retry — production rollout                │
      │ │ Last active 2d ago  ·  4 tabs · 2 files · 1 chat   │
      └───────────────────────────────────────────────────────┘

    Click → emits `restore(candidate_id, title, n_targets)`.
    The launcher's handler then calls the API, gets the full
    target list, and opens each via the OS — one-click
    restoration.

    The visual treatment is even quieter than the thread row: no
    confidence number, no momentum bar, no badge. The brief is
    explicit: "calm UI treatment, no dashboard feel, no
    gamification, no productivity score." We comply by refusing
    to add any number except the small mono target-count chip.

    Debug hover (`debug_hover=True`) renders the engine's `why`
    lines and the per-signal contributions — gated on
    `RECALL_DEBUG=1` at launcher construction, off in production.
    """

    RECOVERY_ROW_HEIGHT = 56

    # candidate_id, title, n_targets
    restore = pyqtSignal(str, str, int)

    def __init__(
        self,
        candidate_id: str,
        title: str,
        time_label: str,
        target_counts: List[Tuple[str, int]],  # [("tabs", 3), ("files", 2), ...]
        why_lines: List[str] | None = None,
        debug_hover: bool = False,
        n_targets_total: int = 0,
    ) -> None:
        super().__init__()
        self.candidate_id = candidate_id
        self.title = title
        self.n_targets_total = n_targets_total

        layout = QHBoxLayout(self)
        layout.setContentsMargins(14, 8, 14, 8)
        layout.setSpacing(12)

        # The vertical lavender rail — same widget the thread row
        # uses, so the user reads recovery + threads as siblings.
        rail = QLabel()
        rail.setFixedSize(2, RecoveryRow.RECOVERY_ROW_HEIGHT - 16)
        rail.setStyleSheet(
            "background: rgba(125, 95, 200, 0.75);"
            "border-radius: 1px;"
        )

        text_col = QVBoxLayout()
        text_col.setContentsMargins(0, 0, 0, 0)
        text_col.setSpacing(2)

        title_lbl = QLabel(title or "Untitled thread")
        title_lbl.setStyleSheet(
            f"color:{TEXT};font-size:12.5px;font-weight:500;"
        )
        title_lbl.setTextFormat(Qt.TextFormat.PlainText)

        # Subtitle = time + a compact target-count strip in mono.
        # We avoid icons; the count words ("tabs", "files", "chats")
        # carry the surface kinds without needing colour codes.
        count_parts = [
            f"{count} {label}"
            for label, count in target_counts
            if count > 0
        ]
        if count_parts:
            subtitle = f"{time_label}  ·  {' · '.join(count_parts)}"
        else:
            subtitle = time_label or ""

        subtitle_lbl = QLabel(subtitle)
        subtitle_lbl.setStyleSheet(
            f"color:{TEXT_DIMMER};font-size:10.5px;"
        )

        text_col.addWidget(title_lbl)
        text_col.addWidget(subtitle_lbl)

        # The right-side "restore" hint. Renders as a small mono
        # affordance — not a button, just a label that says what
        # clicking the row does. Calmer than a CTA chip.
        action_lbl = QLabel("Restore →")
        action_lbl.setStyleSheet(
            "color:rgba(125, 95, 200, 0.85);"
            "font-size:10.5px;font-weight:600;"
            "letter-spacing:0.5px;"
        )

        layout.addWidget(rail, 0, Qt.AlignmentFlag.AlignVCenter)
        layout.addLayout(text_col, 1)
        layout.addWidget(action_lbl, 0, Qt.AlignmentFlag.AlignVCenter)

        if debug_hover and why_lines:
            tip = "Why this surface?\n  · " + "\n  · ".join(why_lines)
            self.setToolTip(tip)
            for w in (title_lbl, subtitle_lbl, action_lbl, rail):
                w.setToolTip(tip)

    def mousePressEvent(self, event) -> None:  # type: ignore[override]
        if event.button() == Qt.MouseButton.LeftButton and self.candidate_id:
            self.restore.emit(
                self.candidate_id, self.title, self.n_targets_total
            )
        super().mousePressEvent(event)


# ----------------------------------------------------------------- session timeline card


class SessionTimelineCard(QWidget):
    """Phase 3C — the visual language of continuity.

    A compact horizontal strip rendering one thread's evolution
    as a sequence of *active periods* punctuated by *transition
    markers*: pivots, accelerations, revisits, resumptions,
    abandonment gaps.

    The widget is purely visual — no interaction beyond an
    optional debug-mode tooltip per phase. It's drawn entirely
    via labelled rectangles + thin connector segments; nothing
    animates, nothing pulses, nothing decorates. The point is to
    *show the user the shape of their own attention over time*,
    not to entertain them with it.

    Composition:

      ┌───────┐  ━━╲  ┌───────────┐  ━━╱  ┌──────┐  ⋯  ┌──────┐
      │ Reading│      │ Implement.│      │Discuss│      │Revisit│
      └───────┘       └───────────┘       └──────┘      └──────┘
        4d              1d                 1d            today

    The connector slope encodes the transition kind: rising
    (acceleration / momentum increase), falling (winding down),
    flat (continuation), dashed (gap / resumption), dotted
    (pivot). Colours are intentionally muted; the brief is calm.
    """

    CARD_HEIGHT = 72
    PHASE_MIN_W = 84
    PHASE_H = 36

    def __init__(
        self,
        phases: List[dict],
        debug_hover: bool = False,
    ) -> None:
        super().__init__()
        self.setFixedHeight(SessionTimelineCard.CARD_HEIGHT)
        self.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Fixed,
        )
        self._phases = phases or []
        self._debug_hover = debug_hover

        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 8, 12, 8)
        layout.setSpacing(0)

        if not self._phases:
            empty = QLabel("No timeline yet")
            empty.setStyleSheet(
                f"color:{TEXT_DIMMER};font-size:11px;"
                "font-style:italic;"
            )
            layout.addWidget(empty)
            layout.addStretch(1)
            return

        for i, ph in enumerate(self._phases):
            if i > 0:
                connector = self._make_connector(
                    self._phases[i - 1], ph
                )
                layout.addWidget(connector, 0, Qt.AlignmentFlag.AlignVCenter)
            pill = self._make_phase_pill(ph)
            layout.addWidget(pill, 0, Qt.AlignmentFlag.AlignVCenter)
        layout.addStretch(1)

    # -- composition helpers -------------------------------------------

    def _make_phase_pill(self, phase: dict) -> QWidget:
        """Two-line pill: title (top) + relative-time hint (bottom).
        Width scales with the relative length of the phase's
        active window so a one-event phase doesn't look the same as
        a six-event phase."""
        pill = QWidget()
        pill.setMinimumWidth(SessionTimelineCard.PHASE_MIN_W)
        pill.setFixedHeight(SessionTimelineCard.PHASE_H + 12)
        pill.setStyleSheet(
            "QWidget {"
            "  background: rgba(181, 168, 255, 0.10);"
            "  border: 1px solid rgba(181, 168, 255, 0.24);"
            "  border-radius: 6px;"
            "}"
        )
        inner = QVBoxLayout(pill)
        inner.setContentsMargins(8, 4, 8, 4)
        inner.setSpacing(0)
        title = QLabel(phase.get("title", "Phase"))
        title.setStyleSheet(
            f"color:{TEXT};font-size:11px;font-weight:500;"
        )
        sub = QLabel(phase.get("subtitle", ""))
        sub.setStyleSheet(
            f"color:{TEXT_DIMMER};font-size:9.5px;"
            "font-family: ui-monospace, 'SF Mono', Menlo, monospace;"
        )
        inner.addWidget(title)
        inner.addWidget(sub)

        if self._debug_hover and phase.get("why"):
            tip = "Why this phase?\n  · " + "\n  · ".join(phase["why"])
            pill.setToolTip(tip)
            title.setToolTip(tip)
            sub.setToolTip(tip)
        return pill

    def _make_connector(
        self, prev: dict, curr: dict
    ) -> QWidget:
        """A thin horizontal divider between two phases. Style
        encodes the transition kind on `curr`:

          • acceleration → solid mint
          • pivot        → solid cyan
          • revisit      → solid rose
          • resumption   → dashed amber (visualizing the gap)
          • continuation → solid muted grey
        """
        transition = (curr.get("transition") or "continuation").lower()
        colour = _transition_colour(transition)
        # Resumption renders as a dashed connector to imply the
        # gap before the next phase started. Everything else is a
        # solid 1 px line.
        dashed = transition == "resumption"
        connector = QLabel()
        connector.setFixedHeight(2)
        connector.setMinimumWidth(28)
        if dashed:
            connector.setStyleSheet(
                "QLabel {"
                f"  background: transparent;"
                f"  border-top: 1px dashed {colour};"
                "}"
            )
        else:
            connector.setStyleSheet(
                f"QLabel {{ background: {colour}; border-radius: 1px; }}"
            )
        return connector


# ----------------------------------------------------------------- evolution strip


class EvolutionStrip(QWidget):
    """A horizontal chronology of one thread's phases.

    Visually a thin strip — each phase is a small pill labelled with
    its title and a brief date hint. Phases are joined by a hairline
    that reads as a timeline; *not* a dashboard, *not* a chart. The
    brief asks for a Linear / Raycast aesthetic; we comply by
    refusing to add chrome.

    The strip is *display-only* in v1 — pills are not clickable. The
    open-thread flow already typed the thread title into the input,
    so the search results below already reflect the topic; clicking a
    phase pill would only narrow the same data without adding a real
    affordance. Keeping it passive avoids inventing UI that doesn't
    earn its weight yet.

    Transition labels (`acceleration`, `revisit`, `pivot`, …) ride as
    a subtle colour cue on the dividers, not as their own widgets.
    """

    STRIP_HEIGHT = 56
    PILL_MIN_WIDTH = 96
    PILL_HEIGHT = 36

    def __init__(
        self,
        phases: List[dict],          # list of {"title", "subtitle", "transition", "why"}
        debug_hover: bool = False,
    ) -> None:
        super().__init__()
        self.setFixedHeight(EvolutionStrip.STRIP_HEIGHT)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(14, 8, 14, 8)
        layout.setSpacing(6)

        if not phases:
            empty = QLabel("No evolution yet")
            empty.setStyleSheet(
                f"color:{TEXT_DIMMER};font-size:11px;"
                "font-style:italic;"
            )
            layout.addWidget(empty)
            layout.addStretch(1)
            return

        # Header label so the strip is self-identifying.
        head = QLabel("Evolution")
        head.setStyleSheet(
            f"color:{TEXT_DIM};"
            "font-size:10px;"
            "font-weight:600;"
            "letter-spacing:1.2px;"
            "text-transform:uppercase;"
        )
        layout.addWidget(head, 0, Qt.AlignmentFlag.AlignVCenter)

        for i, ph in enumerate(phases):
            if i > 0:
                # Hairline divider — transition colour-coded.
                div = QLabel()
                div.setFixedSize(14, 1)
                div.setStyleSheet(
                    "background: "
                    + _transition_colour(ph.get("transition", "continuation"))
                    + ";"
                )
                layout.addWidget(div, 0, Qt.AlignmentFlag.AlignVCenter)

            pill = QLabel(ph.get("title", "Phase"))
            pill.setAlignment(Qt.AlignmentFlag.AlignCenter)
            pill.setMinimumWidth(EvolutionStrip.PILL_MIN_WIDTH)
            pill.setFixedHeight(EvolutionStrip.PILL_HEIGHT)
            pill.setStyleSheet(
                f"color:{TEXT};"
                "font-size:11px;font-weight:500;"
                "padding: 4px 10px;"
                "border-radius: 6px;"
                "background: rgba(181, 168, 255, 0.10);"
                "border: 1px solid rgba(181, 168, 255, 0.22);"
            )
            subtitle = ph.get("subtitle", "")
            if subtitle:
                pill.setText(f"{ph.get('title', 'Phase')}\n{subtitle}")
                # Two-line — bump the height a touch so the second
                # line reads without crowding.
                pill.setFixedHeight(EvolutionStrip.PILL_HEIGHT + 4)
            if debug_hover and ph.get("why"):
                tip = "Why this phase?\n  · " + "\n  · ".join(ph["why"])
                pill.setToolTip(tip)
            layout.addWidget(pill, 0, Qt.AlignmentFlag.AlignVCenter)

        layout.addStretch(1)


def _transition_colour(transition: str) -> str:
    """Map a phase transition to a hairline-divider colour. Kept
    deliberately muted — these aren't status badges."""
    if transition == "acceleration":
        return "rgba(135, 222, 183, 0.55)"     # mint (forward energy)
    if transition == "pivot":
        return "rgba(125, 216, 232, 0.55)"     # cyan (direction change)
    if transition == "revisit":
        return "rgba(214, 120, 150, 0.45)"     # rose (returning)
    if transition == "resumption":
        return "rgba(199, 151, 60, 0.45)"      # amber (came back)
    # initial / continuation
    return "rgba(160, 150, 180, 0.30)"


# ----------------------------------------------------------------- thread row


class ThreadRow(QWidget):
    """One row in the launcher's "Active memory threads" digest.

    Two lines, hairline density — title on top, dim timeline summary
    underneath ("Started 2w ago · 4 sessions · 12 events"). No badge,
    no progress chevron, no confidence number, no surface icons.
    The brief asks for an infrastructure aesthetic; we comply by
    refusing to add chrome.

    Click → emits `clicked(thread_id, topic_key, title)`. The launcher
    uses the topic to trigger a search (which is the open-thread flow:
    chronological reconstruction via existing sessions + contexts).

    Debug hover ("Why am I seeing this?") only when `debug_hover=True`,
    which the launcher gates on the `RECALL_DEBUG` env var.
    """

    THREAD_ROW_HEIGHT = 42

    clicked = pyqtSignal(str, str, str)  # thread_id, topic_key, title

    def __init__(
        self,
        thread_id: str,
        topic_key: str,
        title: str,
        timeline_summary: str,
        why_lines: List[str] | None = None,
        debug_hover: bool = False,
    ) -> None:
        super().__init__()
        self.thread_id = thread_id
        self.topic_key = topic_key
        self.title = title

        layout = QHBoxLayout(self)
        layout.setContentsMargins(14, 6, 14, 6)
        layout.setSpacing(10)

        # A single hairline-thin marker keeps the row visually anchored
        # without a feed-like icon. Same lavender as every other
        # digest row so the section reads as part of the same family.
        rail = QLabel()
        rail.setFixedSize(2, ThreadRow.THREAD_ROW_HEIGHT - 12)
        rail.setStyleSheet(
            "background: rgba(181, 168, 255, 0.55);"
            "border-radius: 1px;"
        )

        text_col = QVBoxLayout()
        text_col.setContentsMargins(0, 0, 0, 0)
        text_col.setSpacing(1)

        title_lbl = QLabel(title or "Untitled thread")
        title_lbl.setStyleSheet(
            f"color:{TEXT};font-size:12px;font-weight:500;"
        )
        title_lbl.setTextFormat(Qt.TextFormat.PlainText)

        summary_lbl = QLabel(timeline_summary or "")
        summary_lbl.setStyleSheet(
            f"color:{TEXT_DIMMER};font-size:10.5px;"
        )

        text_col.addWidget(title_lbl)
        text_col.addWidget(summary_lbl)

        layout.addWidget(rail, 0, Qt.AlignmentFlag.AlignVCenter)
        layout.addLayout(text_col, 1)

        if debug_hover and why_lines:
            tip = (
                "Why am I seeing this?\n  · "
                + "\n  · ".join(why_lines)
            )
            self.setToolTip(tip)
            for w in (title_lbl, summary_lbl, rail):
                w.setToolTip(tip)

    def mousePressEvent(self, event) -> None:  # type: ignore[override]
        if event.button() == Qt.MouseButton.LeftButton and self.thread_id:
            self.clicked.emit(self.thread_id, self.topic_key, self.title)
        super().mousePressEvent(event)


# ----------------------------------------------------------------- episodic card


class EpisodicCard(QWidget):
    """A single episodic moment row in the launcher results list.

    Visually distinct from `ResultItemWidget` (file rows) so users
    read the list as two layers: "memory" (past moments) on top,
    "files" (current memory layer) below. The badge uses a pill of
    text rather than a colored dot so the row carries its own
    typographic identity even when the colored dot would compete with
    the lavender selection chrome.
    """

    EPISODIC_ROW_HEIGHT = 52

    # Maps the kind to a (label, fg, bg, border) badge style.
    _KIND_STYLES: dict[str, tuple[str, str, str, str]] = {
        "browser_visit": (
            "PAGE",
            "#8B7FE3",
            "rgba(181, 168, 255, 0.18)",
            "rgba(181, 168, 255, 0.36)",
        ),
        "browser_search": (
            "SEARCH",
            "#3FB1C9",
            "rgba(125, 216, 232, 0.20)",
            "rgba(125, 216, 232, 0.40)",
        ),
        "chat_session": (
            "CHAT",
            "#42B384",
            "rgba(135, 222, 183, 0.20)",
            "rgba(135, 222, 183, 0.40)",
        ),
    }

    def __init__(self) -> None:
        super().__init__()
        self.kind: str = ""
        self.title_text: str = ""
        self.subtitle_text: str = ""
        self.url: str = ""
        self._build()

    def _build(self) -> None:
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 7, 10, 7)
        layout.setSpacing(10)

        self.badge = QLabel()
        self.badge.setFixedHeight(20)
        self.badge.setAlignment(Qt.AlignmentFlag.AlignCenter)

        text_col = QVBoxLayout()
        text_col.setContentsMargins(0, 0, 0, 0)
        text_col.setSpacing(2)

        self.title = QLabel("")
        self.title.setStyleSheet(
            f"color:{TEXT};font-size:12.5px;font-weight:600;"
        )
        self.title.setTextFormat(Qt.TextFormat.PlainText)

        self.subtitle = QLabel("")
        self.subtitle.setStyleSheet(
            f"color:{TEXT_DIM};font-size:10.5px;"
        )
        self.subtitle.setTextFormat(Qt.TextFormat.PlainText)

        text_col.addWidget(self.title)
        text_col.addWidget(self.subtitle)

        layout.addWidget(self.badge, 0, Qt.AlignmentFlag.AlignTop)
        layout.addLayout(text_col, 1)

    def update_result(self, result) -> None:  # `EpisodicResult` (avoid circular import)
        self.kind = result.kind
        self.url = result.url
        self.title_text = result.title
        self.subtitle_text = result.subtitle

        label, fg, bg, border = self._KIND_STYLES.get(
            result.kind, self._KIND_STYLES["browser_visit"]
        )
        self.badge.setText(label)
        # Per-instance stylesheet so the kind tint stays visible even
        # when the row is selected (the QListWidget item background
        # change would otherwise wash this out).
        self.badge.setStyleSheet(
            f"background:{bg};"
            f"color:{fg};"
            f"border:1px solid {border};"
            "border-radius:6px;"
            "padding:0 7px;"
            "font-size:9px;"
            "font-weight:700;"
            "letter-spacing:0.15em;"
        )
        fm = self.badge.fontMetrics()
        self.badge.setFixedWidth(fm.horizontalAdvance(label) + 18)

        # Truncate title with elide so long page titles never push
        # the row past the list width.
        title_fm: QFontMetrics = self.title.fontMetrics()
        elided = title_fm.elidedText(
            result.title, Qt.TextElideMode.ElideRight, 240
        )
        self.title.setText(elided)
        self.title.setToolTip(result.title)
        self.subtitle.setText(result.subtitle)


def make_episodic_item() -> QListWidgetItem:
    item = QListWidgetItem()
    item.setSizeHint(QSize(0, EpisodicCard.EPISODIC_ROW_HEIGHT))
    return item


# ----------------------------------------------------------------- session card


class SessionCard(QWidget):
    """A reconstructed working session, rendered as a single
    expandable row in the launcher's results list.

    Two states:
      • Collapsed (default) — single header line with topic + time +
        event count. Compact (~30 px tall).
      • Expanded — adds up to N event sublines and a "Continue this
        session" button. Taller (~180 px) but still single-card.

    Keyboard contract from the launcher's perspective:
      • Selection lands on the card normally.
      • Enter on a collapsed card → expand (handled by the card).
      • Enter on an expanded card → emit `continue_clicked(session)`
        so the launcher can reopen everything in the session and hide.

    The card emits two signals:
      • expanded_changed(bool)         — internal state change
      • continue_clicked(Session)      — the user wants to continue
    """

    SESSION_COLLAPSED_HEIGHT = 38
    SESSION_EXPANDED_HEIGHT = 196
    PREVIEW_LINE_HEIGHT = 22

    expanded_changed = pyqtSignal(bool)
    continue_clicked = pyqtSignal(object)

    def __init__(self) -> None:
        super().__init__()
        self.session: Session | None = None
        self._expanded: bool = False
        self._build()

    def _build(self) -> None:
        outer = QVBoxLayout(self)
        outer.setContentsMargins(10, 6, 10, 6)
        outer.setSpacing(4)

        # ── Header line: lavender chevron + topic + time + counter
        header = QHBoxLayout()
        header.setContentsMargins(0, 0, 0, 0)
        header.setSpacing(8)

        self.chevron = QLabel("›")
        self.chevron.setStyleSheet(
            "color:#A99CF7;font-size:14px;font-weight:700;"
        )
        self.chevron.setFixedWidth(10)

        # Compact "session" pill so the card type reads at a glance
        # alongside the file rows above and below it.
        self.kind_pill = QLabel("SESSION")
        self.kind_pill.setStyleSheet(
            "background:rgba(169, 156, 247, 0.18);"
            "color:#8B7FE3;"
            "border:1px solid rgba(169, 156, 247, 0.36);"
            "border-radius:6px;"
            "padding:0 7px;"
            "font-size:9px;"
            "font-weight:700;"
            "letter-spacing:0.15em;"
        )
        self.kind_pill.setFixedHeight(20)

        self.label = QLabel("")
        self.label.setStyleSheet(
            f"color:{TEXT};font-size:12.5px;font-weight:600;"
        )
        self.label.setTextFormat(Qt.TextFormat.PlainText)

        self.time_label = QLabel("")
        self.time_label.setStyleSheet(
            f"color:{TEXT_DIM};font-size:10.5px;"
        )

        self.count_label = QLabel("")
        self.count_label.setStyleSheet(
            f"color:{TEXT_DIMMER};font-size:10.5px;"
        )

        header.addWidget(self.chevron, 0, Qt.AlignmentFlag.AlignVCenter)
        header.addWidget(self.kind_pill, 0, Qt.AlignmentFlag.AlignVCenter)
        header.addWidget(self.label, 1, Qt.AlignmentFlag.AlignVCenter)
        header.addWidget(self.time_label, 0, Qt.AlignmentFlag.AlignVCenter)
        header.addWidget(self.count_label, 0, Qt.AlignmentFlag.AlignVCenter)

        # ── Body container — created hidden, shown when expanded
        self.body = QWidget()
        body_layout = QVBoxLayout(self.body)
        body_layout.setContentsMargins(20, 4, 4, 0)
        body_layout.setSpacing(2)
        self._event_lines: list[QLabel] = []
        for _ in range(6):
            row = QLabel("")
            row.setStyleSheet(
                f"color:{TEXT_DIM};font-size:11px;"
            )
            row.setTextFormat(Qt.TextFormat.PlainText)
            row.setFixedHeight(self.PREVIEW_LINE_HEIGHT)
            row.hide()
            body_layout.addWidget(row)
            self._event_lines.append(row)

        # ── Continue button — lives at the bottom of the body
        button_row = QHBoxLayout()
        button_row.setContentsMargins(0, 6, 0, 0)
        button_row.setSpacing(0)
        self.continue_btn = QLabel("↵  Continue this session")
        self.continue_btn.setStyleSheet(
            "color:#8B7FE3;"
            "font-size:11px;"
            "font-weight:600;"
            "padding:4px 10px;"
            "border:1px solid rgba(169, 156, 247, 0.40);"
            "border-radius:6px;"
            "background:rgba(169, 156, 247, 0.10);"
        )
        self.continue_btn.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.continue_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        button_row.addStretch(1)
        button_row.addWidget(self.continue_btn)
        body_layout.addLayout(button_row)

        self.body.hide()

        outer.addLayout(header)
        outer.addWidget(self.body)

    # -- public API -----------------------------------------------------

    def update_session(self, session: Session) -> None:
        self.session = session
        self.label.setText(session.label)
        self.label.setToolTip(session.label)
        self.time_label.setText(session.time_label)
        n = session.event_count
        plural = "event" if n == 1 else "events"
        self.count_label.setText(f"{n} {plural}")

        previews = session.preview_events()
        for i, line in enumerate(self._event_lines):
            if i < len(previews):
                ev = previews[i]
                kind_glyph = self._kind_glyph(ev.kind)
                text = _event_display_text(ev)
                # Truncate per row so the line doesn't overflow.
                line.setText(f"{kind_glyph}  {text}")
                line.setToolTip(text)
                # Each row should also visually elide if too long
                fm: QFontMetrics = line.fontMetrics()
                elided = fm.elidedText(
                    line.text(), Qt.TextElideMode.ElideRight, 280
                )
                line.setText(elided)
                if self._expanded:
                    line.show()
            else:
                line.hide()

    def set_expanded(self, expanded: bool) -> None:
        if self._expanded == expanded:
            return
        self._expanded = expanded
        self.chevron.setText("⌄" if expanded else "›")
        self.body.setVisible(expanded)
        # Reapply the per-line visibility because hiding `body` doesn't
        # propagate to the labels we kept hidden by default.
        if self.session is not None:
            previews_count = len(self.session.preview_events())
            for i, line in enumerate(self._event_lines):
                if expanded and i < previews_count:
                    line.show()
                else:
                    line.hide()
        self.expanded_changed.emit(expanded)

    @property
    def expanded(self) -> bool:
        return self._expanded

    @property
    def desired_height(self) -> int:
        return (
            self.SESSION_EXPANDED_HEIGHT if self._expanded
            else self.SESSION_COLLAPSED_HEIGHT
        )

    # -- click routing --------------------------------------------------

    def mousePressEvent(self, event) -> None:  # type: ignore[override]
        if event.button() == Qt.MouseButton.LeftButton:
            # Continue button is a click target when expanded.
            if self._expanded and self.continue_btn.geometry().contains(
                self.continue_btn.mapFromParent(event.position().toPoint())
                if hasattr(event, "position") else event.pos()
            ):
                if self.session is not None:
                    self.continue_clicked.emit(self.session)
                    return
            # Otherwise toggle expansion.
            self.set_expanded(not self._expanded)
        super().mousePressEvent(event)

    @staticmethod
    def _kind_glyph(kind: str) -> str:
        # Single-character glyphs so the per-event line stays one visual unit.
        # Picked from a small set so users can scan the session quickly.
        return {
            "browser_visit": "◌",
            "browser_search": "⌕",
            "chat_session": "◇",
            "open": "▢",
            "reveal": "▢",
            "query": "·",
        }.get(kind, "·")


def make_session_item() -> QListWidgetItem:
    item = QListWidgetItem()
    item.setSizeHint(QSize(0, SessionCard.SESSION_COLLAPSED_HEIGHT))
    return item


# ----------------------------------------------------------------- context card


class ContextCard(QWidget):
    """A topical micro-context inside a temporal session.

    Sits between the EpisodicCard layer (single moments) and the
    SessionCard layer (broader temporal blocks). Visually tighter
    than SessionCard because micro-contexts are more abundant — the
    launcher may surface two of these alongside one session card.

    Same two-state shape as SessionCard:
      • Collapsed (~32 px): pill + label + time + event count.
      • Expanded (~160 px): up to 5 event sublines + Resume button.

    Signals:
      • expanded_changed(bool)            — internal toggle
      • resume_clicked(MicroContext)      — user wants to resume context
    """

    CONTEXT_COLLAPSED_HEIGHT = 34
    CONTEXT_EXPANDED_HEIGHT = 168
    PREVIEW_LINE_HEIGHT = 21

    expanded_changed = pyqtSignal(bool)
    resume_clicked = pyqtSignal(object)

    def __init__(self) -> None:
        super().__init__()
        self.context: MicroContext | None = None
        self._expanded: bool = False
        self._build()

    def _build(self) -> None:
        outer = QVBoxLayout(self)
        outer.setContentsMargins(10, 5, 10, 5)
        outer.setSpacing(3)

        # ── Header line: chevron + CONTEXT pill + label + time + count
        header = QHBoxLayout()
        header.setContentsMargins(0, 0, 0, 0)
        header.setSpacing(8)

        self.chevron = QLabel("›")
        self.chevron.setStyleSheet(
            "color:#A99CF7;font-size:13px;font-weight:700;"
        )
        self.chevron.setFixedWidth(10)

        # Cyan-tinted pill so the row reads as visually distinct from
        # the lavender SessionCard pill — micro-contexts are tighter,
        # cyan suggests "thread of attention".
        self.kind_pill = QLabel("CONTEXT")
        self.kind_pill.setStyleSheet(
            "background:rgba(125, 216, 232, 0.20);"
            "color:#3FB1C9;"
            "border:1px solid rgba(125, 216, 232, 0.40);"
            "border-radius:6px;"
            "padding:0 7px;"
            "font-size:9px;"
            "font-weight:700;"
            "letter-spacing:0.15em;"
        )
        self.kind_pill.setFixedHeight(18)

        self.label = QLabel("")
        self.label.setStyleSheet(
            f"color:{TEXT};font-size:12px;font-weight:600;"
        )
        self.label.setTextFormat(Qt.TextFormat.PlainText)

        self.time_label = QLabel("")
        self.time_label.setStyleSheet(
            f"color:{TEXT_DIM};font-size:10px;"
        )

        self.count_label = QLabel("")
        self.count_label.setStyleSheet(
            f"color:{TEXT_DIMMER};font-size:10px;"
        )

        header.addWidget(self.chevron, 0, Qt.AlignmentFlag.AlignVCenter)
        header.addWidget(self.kind_pill, 0, Qt.AlignmentFlag.AlignVCenter)
        header.addWidget(self.label, 1, Qt.AlignmentFlag.AlignVCenter)
        header.addWidget(self.time_label, 0, Qt.AlignmentFlag.AlignVCenter)
        header.addWidget(self.count_label, 0, Qt.AlignmentFlag.AlignVCenter)

        # ── Body — five event preview rows + Resume affordance
        self.body = QWidget()
        body_layout = QVBoxLayout(self.body)
        body_layout.setContentsMargins(18, 3, 4, 0)
        body_layout.setSpacing(1)
        self._event_lines: list[QLabel] = []
        for _ in range(5):
            row = QLabel("")
            row.setStyleSheet(
                f"color:{TEXT_DIM};font-size:10.5px;"
            )
            row.setTextFormat(Qt.TextFormat.PlainText)
            row.setFixedHeight(self.PREVIEW_LINE_HEIGHT)
            row.hide()
            body_layout.addWidget(row)
            self._event_lines.append(row)

        button_row = QHBoxLayout()
        button_row.setContentsMargins(0, 5, 0, 0)
        self.resume_btn = QLabel("↵  Resume context")
        self.resume_btn.setStyleSheet(
            "color:#3FB1C9;"
            "font-size:11px;"
            "font-weight:600;"
            "padding:3px 10px;"
            "border:1px solid rgba(125, 216, 232, 0.45);"
            "border-radius:6px;"
            "background:rgba(125, 216, 232, 0.10);"
        )
        self.resume_btn.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.resume_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        button_row.addStretch(1)
        button_row.addWidget(self.resume_btn)
        body_layout.addLayout(button_row)

        self.body.hide()

        outer.addLayout(header)
        outer.addWidget(self.body)

    # -- public API -----------------------------------------------------

    def update_context(self, ctx: MicroContext) -> None:
        self.context = ctx
        self.label.setText(ctx.label)
        self.label.setToolTip(ctx.label)
        self.time_label.setText(ctx.time_label)
        n = ctx.event_count
        plural = "event" if n == 1 else "events"
        self.count_label.setText(f"{n} {plural}")

        previews = ctx.preview_events(max_n=5)
        for i, line in enumerate(self._event_lines):
            if i < len(previews):
                ev = previews[i]
                glyph = SessionCard._kind_glyph(ev.kind)
                text = _event_display_text(ev)
                line.setText(f"{glyph}  {text}")
                line.setToolTip(text)
                fm: QFontMetrics = line.fontMetrics()
                elided = fm.elidedText(
                    line.text(), Qt.TextElideMode.ElideRight, 280
                )
                line.setText(elided)
                if self._expanded:
                    line.show()
            else:
                line.hide()

    def set_expanded(self, expanded: bool) -> None:
        if self._expanded == expanded:
            return
        self._expanded = expanded
        self.chevron.setText("⌄" if expanded else "›")
        self.body.setVisible(expanded)
        if self.context is not None:
            previews_count = len(self.context.preview_events(max_n=5))
            for i, line in enumerate(self._event_lines):
                if expanded and i < previews_count:
                    line.show()
                else:
                    line.hide()
        self.expanded_changed.emit(expanded)

    @property
    def expanded(self) -> bool:
        return self._expanded

    @property
    def desired_height(self) -> int:
        return (
            self.CONTEXT_EXPANDED_HEIGHT if self._expanded
            else self.CONTEXT_COLLAPSED_HEIGHT
        )

    def mousePressEvent(self, event) -> None:  # type: ignore[override]
        if event.button() == Qt.MouseButton.LeftButton:
            if self._expanded and self.resume_btn.geometry().contains(
                self.resume_btn.mapFromParent(event.position().toPoint())
                if hasattr(event, "position") else event.pos()
            ):
                if self.context is not None:
                    self.resume_clicked.emit(self.context)
                    return
            self.set_expanded(not self._expanded)
        super().mousePressEvent(event)


def make_context_item() -> QListWidgetItem:
    item = QListWidgetItem()
    item.setSizeHint(QSize(0, ContextCard.CONTEXT_COLLAPSED_HEIGHT))
    return item


# ------------------------------------------------- activity helpers


def _activity_display(ev_kind: str, payload: dict) -> tuple[str, str]:
    """Return (title, subtitle) suitable for a BrowserActivityRow.

    Each kind has its own preferred display:
      • browser_visit  → page title (or domain), subtitle = domain
      • browser_search → "<query>", subtitle = engine name
      • chat_session   → page title (or platform), subtitle = platform
    """
    if ev_kind == "browser_search":
        query = (payload.get("query") or "").strip() or "(empty search)"
        engine = (payload.get("engine") or "search").strip()
        return f"“{query}”", engine

    if ev_kind == "chat_session":
        title = (payload.get("title") or "").strip()
        platform = (payload.get("platform") or "chat").strip()
        if not title:
            title = platform
        return title, platform

    # default: browser_visit
    title = (payload.get("title") or payload.get("tab_title") or "").strip()
    domain = (payload.get("domain") or "").strip()
    if not title:
        title = domain or (payload.get("url") or "untitled page")
    return title, domain
