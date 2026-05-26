"""Phase 6O — Launcher Reset · 6P.1 — Visibility Recovery.

Single floating surface. **680 × 460**. Paper-warm page, layered
white cards. One column.

    ┌────────────────────────────────────────────┐
    │ ┌────────────────────────────────────────┐ │
    │ │ 🔍 Search investigations…              │ │
    │ └────────────────────────────────────────┘ │
    │                                            │
    │  CONTINUE                                  │
    │ ┌──────────────────────────────────────┐   │
    │ │▎ WebSocket retry debugging  [Resume] │   │
    │ │  2 tabs · 2 files · returned 2d      │   │
    │ └──────────────────────────────────────┘   │
    │                                            │
    │  OTHER WORK                                │
    │ ┌──────────────────────────────────────┐   │
    │ │  WebSocket | Healthcare | RLHF        │   │
    │ └──────────────────────────────────────┘   │
    └────────────────────────────────────────────┘

The 6P.1 visibility pass adds layering: every interactive surface
sits inside a white card with a 1-px border and a soft 0/12/32
shadow, so the launcher reads as a stack of physical objects
against a warmer page (`#F3F1ED`) rather than a flat sheet.
"""

from __future__ import annotations

from typing import List, Optional

from PyQt6.QtCore import QRectF, Qt, pyqtSignal
from PyQt6.QtGui import QColor, QFont, QPainter, QPainterPath, QPen
from PyQt6.QtWidgets import (
    QGraphicsDropShadowEffect,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from . import theme as T
from .investigation_panel import InvestigationCardV3, InvestigationRow
from .recovery_panel import RecoveryCardV3


# ── card wrapper ──────────────────────────────────────────────────


class _LayeredCard(QWidget):
    """A white card with a 1-px warm-grey border and a soft drop
    shadow. The 6P.1 visibility recovery's foundational shape —
    everything interactive in the launcher sits inside one of these
    so the launcher reads as *layered* rather than flat."""

    def __init__(
        self,
        *,
        radius: int = 18,
        parent: Optional[QWidget] = None,
    ) -> None:
        super().__init__(parent)
        self._radius = radius
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, False)
        eff = QGraphicsDropShadowEffect(self)
        eff.setBlurRadius(T.SHADOW_CARD_RADIUS)
        eff.setOffset(0, T.SHADOW_CARD_OFFSET)
        eff.setColor(QColor(0, 0, 0, T.SHADOW_CARD_ALPHA))
        self.setGraphicsEffect(eff)

    def paintEvent(self, _e) -> None:  # type: ignore[override]
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        path = QPainterPath()
        path.addRoundedRect(QRectF(self.rect()), self._radius, self._radius)
        p.fillPath(path, QColor(T.BG_RAISED))
        pen = QPen(QColor(T.BORDER_RAISED))
        pen.setWidthF(1.0)
        p.setPen(pen)
        p.drawPath(path)
        p.end()


# ── search bar ────────────────────────────────────────────────────


class _SearchIcon(QWidget):
    """Hand-drawn magnifying-glass glyph — a circle + handle. The
    offscreen Qt font database doesn't carry `⌕`; drawing it
    explicitly guarantees the search icon renders on every host."""

    SIZE = 16

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.setFixedSize(self.SIZE, self.SIZE)

    def paintEvent(self, _e) -> None:  # type: ignore[override]
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        pen = QPen(QColor(T.INK_3))
        pen.setWidthF(1.6)
        p.setPen(pen)
        p.setBrush(Qt.BrushStyle.NoBrush)
        # circle (the lens)
        p.drawEllipse(2, 2, 9, 9)
        # handle
        p.drawLine(10, 10, 14, 14)
        p.end()


class MinimalSearchBar(_LayeredCard):
    """A search input wrapped in a layered card. Hand-drawn search
    glyph + QLineEdit + lavender focus ring. The card is the
    full-width chrome the directive's *Search: white card · same
    border · same shadow* spec asks for."""

    query_changed = pyqtSignal(str)

    HEIGHT = 56     # 6P.1: card height (was 44 bare input)

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(radius=14, parent=parent)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.setFixedHeight(self.HEIGHT)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 0, 16, 0)
        layout.setSpacing(10)

        icon = _SearchIcon()
        layout.addWidget(icon, 0, Qt.AlignmentFlag.AlignVCenter)

        self._input = QLineEdit()
        self._input.setPlaceholderText("Search investigations…")
        self._input.setFixedHeight(self.HEIGHT - 2)
        self._input.setStyleSheet(
            f"QLineEdit {{"
            f"  background: transparent;"
            f"  color: {T.INK};"
            f"  border: none;"
            f"  padding: 0;"
            f"  font-size: {T.FS_BODY}px;"
            f"}}"
        )
        self._input.textChanged.connect(self.query_changed.emit)
        self._input.installEventFilter(self)
        layout.addWidget(self._input, 1)

        self._focused = False

    # The card paints itself; on focus we redraw with a lavender ring.
    def eventFilter(self, obj, event):  # type: ignore[override]
        from PyQt6.QtCore import QEvent
        if obj is self._input:
            if event.type() == QEvent.Type.FocusIn:
                self._focused = True
                self.update()
            elif event.type() == QEvent.Type.FocusOut:
                self._focused = False
                self.update()
        return super().eventFilter(obj, event)

    def paintEvent(self, _e) -> None:  # type: ignore[override]
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        path = QPainterPath()
        path.addRoundedRect(QRectF(self.rect()), self._radius, self._radius)
        # 6P.1: inactive cards sit at 0.85 opacity so the focused card
        # always reads as the foreground element.
        if self._focused:
            p.fillPath(path, QColor(T.BG_RAISED))
        else:
            fill = QColor(T.BG_RAISED)
            fill.setAlpha(int(255 * 0.96))   # slight veil when unfocused
            p.fillPath(path, fill)
        if self._focused:
            pen = QPen(QColor(T.ACCENT))
            pen.setWidthF(2.0)
        else:
            pen = QPen(QColor(T.BORDER_RAISED))
            pen.setWidthF(1.0)
        p.setPen(pen)
        p.drawPath(path)
        p.end()

    def focus(self) -> None:
        self._input.setFocus(Qt.FocusReason.ShortcutFocusReason)
        self._input.selectAll()


# ── section eyebrow ───────────────────────────────────────────────


def _section_label(text: str) -> QLabel:
    """The directive's *Section: 11 uppercase*."""
    lbl = QLabel(text.upper())
    f = QFont()
    f.setPointSizeF(8.0)
    f.setBold(True)
    lbl.setFont(f)
    lbl.setStyleSheet(
        f"color: {T.INK_3};"
        f"background: transparent;"
        f"letter-spacing: 1.4px;"
        f"padding: 0;"
    )
    return lbl


# ── investigations card wrapper ───────────────────────────────────


class _InvestigationsCard(_LayeredCard):
    """A white card that wraps the `InvestigationRow`. The directive's
    *Wrap inside card. NOT floating pills.* rule — the row stops
    looking like text adrift on the page."""

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(radius=18, parent=parent)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 14, 16, 14)
        layout.setSpacing(0)
        self.row = InvestigationRow()
        layout.addWidget(self.row, 1)

    def populate(self, items: List[InvestigationCardV3]) -> None:
        self.row.populate(items)


# ── populated body ────────────────────────────────────────────────


class MinimalDigest(QWidget):
    """Search · CONTINUE (hero) · OTHER WORK (titles, wrapped in
    card). Each section is layered against the warm page so the
    launcher reads as a stack of physical objects."""

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Hero slot — `populate` swaps in a RecoveryCardV3.
        self._hero_section = QVBoxLayout()
        self._hero_section.setContentsMargins(0, 0, 0, 0)
        self._hero_section.setSpacing(10)
        layout.addLayout(self._hero_section)
        self._hero: Optional[RecoveryCardV3] = None
        self._hero_header: Optional[QLabel] = None

        layout.addSpacing(22)            # 6P.1: a little more breathing room

        # OTHER WORK section.
        self._other_header = _section_label("Other work")
        layout.addWidget(self._other_header)
        layout.addSpacing(8)
        self._investigations = _InvestigationsCard()
        layout.addWidget(self._investigations)
        # `row` is preserved on the digest so `LiveLauncher`'s
        # keyboard layer (hotkeys 2-4 cycle the title focus) still
        # reaches into the underlying titles unchanged.
        self.row = self._investigations.row

        layout.addStretch(1)

    def populate(
        self,
        *,
        hero: Optional[RecoveryCardV3],
        investigations: List[InvestigationCardV3],
    ) -> None:
        # Hero swap.
        if self._hero is not None:
            self._hero_section.removeWidget(self._hero)
            self._hero.setParent(None)
            self._hero = None
        if self._hero_header is not None:
            self._hero_section.removeWidget(self._hero_header)
            self._hero_header.setParent(None)
            self._hero_header = None

        if hero is not None:
            self._hero_header = _section_label("Continue")
            self._hero_section.addWidget(self._hero_header)
            self._hero = hero
            self._hero_section.addWidget(hero)

        self._investigations.populate(investigations)


# ── empty surface ─────────────────────────────────────────────────


class MinimalEmpty(QWidget):
    """Vertically-centred empty. Stacked: lavender dot · headline ·
    subtext · buttons row. The 6P.1 stack ordering follows the
    directive's exact *logo · headline · subtext · buttons row* spec
    with a fixed 16-px gap between everything."""

    show_example = pyqtSignal()
    start_normally = pyqtSignal()

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(16)             # 6P.1: directive's *gap: 16*
        outer.addStretch(1)

        # Tiny accent "logo" mark — a 14-px lavender square. The
        # launcher doesn't ship a brand glyph yet; the square is the
        # placeholder. The directive asks for a `logo` row, not a
        # particular asset.
        logo_row = QHBoxLayout()
        logo_row.setSpacing(0)
        logo_row.addStretch(1)
        logo = QLabel()
        logo.setFixedSize(14, 14)
        logo.setStyleSheet(
            f"background: {T.ACCENT}; border-radius: 4px;"
        )
        logo_row.addWidget(logo)
        logo_row.addStretch(1)
        outer.addLayout(logo_row)

        headline = QLabel("Recall notices unfinished work")
        hf = QFont()
        hf.setPointSizeF(T.FS_HERO)         # 20
        hf.setBold(True)
        headline.setFont(hf)
        headline.setStyleSheet(
            f"color: {T.INK}; background: transparent;"
        )
        headline.setAlignment(Qt.AlignmentFlag.AlignCenter)
        outer.addWidget(headline)

        sub = QLabel("Work normally.\nReturn later.")
        sub.setStyleSheet(
            f"color: {T.INK_2}; background: transparent;"
            f"font-size: {T.FS_BODY}px;"
        )
        sub.setAlignment(Qt.AlignmentFlag.AlignCenter)
        sub.setWordWrap(True)
        outer.addWidget(sub)

        buttons = QHBoxLayout()
        buttons.setSpacing(12)
        buttons.addStretch(1)

        # 6P.1 — *Buttons: same width 140, center aligned*.
        BTN_W = 140
        primary = QPushButton("Show example")
        primary.setCursor(Qt.CursorShape.PointingHandCursor)
        primary.setFixedHeight(38)
        primary.setFixedWidth(BTN_W)
        primary.setStyleSheet(
            f"QPushButton {{"
            f"  background: {T.ACCENT};"
            f"  color: white;"
            f"  border: none;"
            f"  border-radius: 12px;"
            f"  font-size: {T.FS_BODY}px;"
            f"  font-weight: 600;"
            f"}}"
            f"QPushButton:hover {{ background: #7A6FD4; }}"
        )
        primary.clicked.connect(self.show_example.emit)
        secondary = QPushButton("Start normally")
        secondary.setCursor(Qt.CursorShape.PointingHandCursor)
        secondary.setFixedHeight(38)
        secondary.setFixedWidth(BTN_W)
        secondary.setStyleSheet(
            f"QPushButton {{"
            f"  background: {T.BG_RAISED};"
            f"  color: {T.INK_2};"
            f"  border: 1px solid {T.BORDER_RAISED};"
            f"  border-radius: 12px;"
            f"  font-size: {T.FS_BODY}px;"
            f"  font-weight: 500;"
            f"}}"
            f"QPushButton:hover {{ background: #F3F0EC; color: {T.INK}; }}"
        )
        secondary.clicked.connect(self.start_normally.emit)
        buttons.addWidget(primary)
        buttons.addWidget(secondary)
        buttons.addStretch(1)
        outer.addLayout(buttons)

        outer.addStretch(2)


# ── shell + window ────────────────────────────────────────────────


class MinimalShell(QWidget):
    """The single-column shell. Search on top, body below.

    Directive geometry: outer padding 24, search→body 16,
    column max width 620.
    """

    MIN_WIDTH = 480
    MAX_WIDTH = 620

    def __init__(
        self,
        center: QWidget,
        *,
        search: Optional[MinimalSearchBar] = None,
        parent: Optional[QWidget] = None,
    ) -> None:
        super().__init__(parent)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        outer = QHBoxLayout(self)
        outer.setContentsMargins(24, 22, 24, 22)
        outer.setSpacing(0)
        outer.addStretch(1)

        column = QWidget()
        column.setMinimumWidth(self.MIN_WIDTH)
        column.setMaximumWidth(self.MAX_WIDTH)
        cl = QVBoxLayout(column)
        cl.setContentsMargins(0, 0, 0, 0)
        cl.setSpacing(0)

        self.search = search or MinimalSearchBar()
        cl.addWidget(self.search)
        cl.addSpacing(18)                # 6P.1: a touch more between search and body
        cl.addWidget(center, 1)

        outer.addWidget(column)
        outer.addStretch(1)


class MinimalWindow(QWidget):
    """Top-level floating QWidget. Warm-paper page with a visible
    outer frame: 12-px margin · inner radius 24 · subtle border. The
    launcher should feel like an *object*, not a layer of paint."""

    DEFAULT_SIZE = (680, 460)
    OUTER_MARGIN = 12

    def __init__(
        self,
        center: QWidget,
        *,
        search: Optional[MinimalSearchBar] = None,
        parent: Optional[QWidget] = None,
    ) -> None:
        super().__init__(parent)
        self.setObjectName("launcher_v3_window")
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.resize(*self.DEFAULT_SIZE)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(
            self.OUTER_MARGIN, self.OUTER_MARGIN,
            self.OUTER_MARGIN, self.OUTER_MARGIN,
        )
        layout.setSpacing(0)
        self._shell = MinimalShell(center, search=search)
        layout.addWidget(self._shell)

    @property
    def shell(self) -> MinimalShell:
        return self._shell

    def paintEvent(self, _e) -> None:  # type: ignore[override]
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        path = QPainterPath()
        # Inset the painted rect by the outer margin so the launcher
        # has a visible frame between the painted page and the
        # window edge.
        m = self.OUTER_MARGIN
        rect = QRectF(m, m, self.width() - 2 * m, self.height() - 2 * m)
        path.addRoundedRect(rect, 24, 24)
        p.fillPath(path, QColor(T.BG))
        pen = QPen(QColor(T.BORDER_RAISED))
        pen.setWidthF(1.0)
        p.setPen(pen)
        p.drawPath(path)
        p.end()


__all__ = [
    "MinimalSearchBar",
    "MinimalDigest",
    "MinimalEmpty",
    "MinimalShell",
    "MinimalWindow",
]
