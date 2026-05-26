"""Phase 6R — Launcher Finalization · minimal surface.

The frozen launcher. **680 × 440**, hard-clamped (min = max).
Warm-paper page (`#F4F1EC`). One column. Five sections:

    +-----------------------------------------------------------+
    |  +-----------------------------------------------------+  |
    |  | Q  Search work...                                    |  |
    |  +-----------------------------------------------------+  |
    |    (20)                                                   |
    |  CONTINUE                                                 |
    |  +-----------------------------------------------------+  |
    |  || WebSocket retry debugging                  HIGH    |  |
    |  ||  2 files  2 tabs  1 search        [ Resume   1 ]   |  |
    |  +-----------------------------------------------------+  |
    |    (16)                                                   |
    |  OTHER WORK                                               |
    |  +-----------------------------------------------------+  |
    |  | .  Healthcare proposal draft                     >  |  |
    |  | .  RLHF notes                                    >  |  |
    |  +-----------------------------------------------------+  |
    |    (12)                                                   |
    |              local only - no cloud                        |
    +-----------------------------------------------------------+

Empty state (no HIGH recovery): the same window paints a
centred stack of *logo · headline · Show example · Start
working*, the buttons live **inside** that stack — no longer
floating page furniture.
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
from .investigation_panel import InvestigationCardV3, InvestigationList
from .recovery_panel import RecoveryCardV3


# ── search-icon glyph ─────────────────────────────────────────────


class _SearchIcon(QWidget):
    """Hand-drawn magnifying glass — circle + handle. Paint, not
    glyph, so the icon renders identically across hosts."""

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
        p.drawEllipse(2, 2, 9, 9)
        p.drawLine(10, 10, 14, 14)
        p.end()


# ── search bar ────────────────────────────────────────────────────


class MinimalSearchBar(QWidget):
    """52-px white card, 2-px warm-grey border, radius 14, soft
    shadow `0 8 24 rgba(0,0,0,.06)`. Lavender focus ring on
    `FocusIn`. Placeholder *Search work…*."""

    query_changed = pyqtSignal(str)

    HEIGHT = 52      # directive: height 52
    RADIUS = 14      # directive: radius 14

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.setFixedHeight(self.HEIGHT)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, False)

        eff = QGraphicsDropShadowEffect(self)
        eff.setBlurRadius(T.SHADOW_SEARCH_RADIUS)
        eff.setOffset(0, T.SHADOW_SEARCH_OFFSET)
        eff.setColor(QColor(0, 0, 0, T.SHADOW_SEARCH_ALPHA))
        self.setGraphicsEffect(eff)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 0, 16, 0)
        layout.setSpacing(10)
        layout.addWidget(_SearchIcon(), 0, Qt.AlignmentFlag.AlignVCenter)

        self._input = QLineEdit()
        self._input.setPlaceholderText("Search work…")
        self._input.setFixedHeight(self.HEIGHT - 2)
        self._input.setStyleSheet(
            f"QLineEdit {{"
            f"  background: transparent;"
            f"  color: {T.INK};"
            f"  border: none;"
            f"  padding: 0;"
            f"  font-size: 13px;"
            f"}}"
        )
        self._input.textChanged.connect(self.query_changed.emit)
        self._input.installEventFilter(self)
        layout.addWidget(self._input, 1)

        self._focused = False

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
        path.addRoundedRect(QRectF(self.rect()), self.RADIUS, self.RADIUS)
        p.fillPath(path, QColor(T.BG_RAISED))
        if self._focused:
            pen = QPen(QColor(T.ACCENT))
            pen.setWidthF(2.0)
        else:
            pen = QPen(QColor(T.BORDER_RAISED_STRONG))
            pen.setWidthF(2.0)
        p.setPen(pen)
        p.drawPath(path)
        p.end()

    def focus(self) -> None:
        self._input.setFocus(Qt.FocusReason.ShortcutFocusReason)
        self._input.selectAll()


# ── section eyebrow ───────────────────────────────────────────────


def _section_label(text: str) -> QLabel:
    lbl = QLabel(text.upper())
    f = QFont()
    f.setPointSizeF(7.5)
    f.setBold(True)
    lbl.setFont(f)
    lbl.setStyleSheet(
        f"color: {T.INK_3};"
        f"background: transparent;"
        f"letter-spacing: 1.3px;"
        f"padding: 0;"
    )
    return lbl


# ── populated body ────────────────────────────────────────────────


class MinimalDigest(QWidget):
    """Search · CONTINUE (hero) · OTHER WORK (vertical list)."""

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Hero slot.
        self._hero_section = QVBoxLayout()
        self._hero_section.setContentsMargins(0, 0, 0, 0)
        self._hero_section.setSpacing(8)
        layout.addLayout(self._hero_section)
        self._hero: Optional[RecoveryCardV3] = None
        self._hero_header: Optional[QLabel] = None

        layout.addSpacing(16)            # directive: hero -> work = 16

        self._other_header = _section_label("Other work")
        layout.addWidget(self._other_header)
        layout.addSpacing(6)
        self._list = InvestigationList()
        layout.addWidget(self._list)
        # Back-compat alias for the live launcher's keyboard layer.
        self.row = self._list

        layout.addStretch(1)

    def populate(
        self,
        *,
        hero: Optional[RecoveryCardV3],
        investigations: List[InvestigationCardV3],
    ) -> None:
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

        self._list.populate(investigations)
        self._other_header.setVisible(bool(investigations))
        self._list.setVisible(bool(investigations))


# ── empty surface ─────────────────────────────────────────────────


class MinimalEmpty(QWidget):
    """Centred onboarding stack: lavender logo · headline · Show
    example · Start working. The two buttons sit **inside** the
    stack — no longer floating page furniture."""

    show_example = pyqtSignal()
    start_normally = pyqtSignal()

    BTN_WIDTH = 200       # the directive doesn't specify; 200 lands
                          # squarely between *too narrow* and *spans
                          # the column*; tested against the 480-px
                          # minimum column width.

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(14)
        outer.addStretch(1)

        # Lavender square — the launcher does not ship a brand
        # glyph yet, the dot is the placeholder. Centred row.
        logo_row = QHBoxLayout()
        logo_row.setSpacing(0)
        logo_row.addStretch(1)
        logo = QLabel()
        logo.setFixedSize(16, 16)
        logo.setStyleSheet(
            f"background: {T.ACCENT}; border-radius: 4px;"
        )
        logo_row.addWidget(logo)
        logo_row.addStretch(1)
        outer.addLayout(logo_row)

        headline = QLabel("Recall notices unfinished work")
        hf = QFont()
        hf.setPointSizeF(16.5)
        hf.setBold(True)
        headline.setFont(hf)
        headline.setStyleSheet(
            f"color: {T.INK}; background: transparent;"
        )
        headline.setAlignment(Qt.AlignmentFlag.AlignCenter)
        outer.addWidget(headline)

        outer.addSpacing(4)

        # Two stacked buttons, centred, equal width.
        primary = self._make_button("Show example", primary=True)
        primary.clicked.connect(self.show_example.emit)
        outer.addWidget(primary, 0, Qt.AlignmentFlag.AlignHCenter)

        secondary = self._make_button("Start working", primary=False)
        secondary.clicked.connect(self.start_normally.emit)
        outer.addWidget(secondary, 0, Qt.AlignmentFlag.AlignHCenter)

        outer.addStretch(2)

    def _make_button(self, label: str, *, primary: bool) -> QPushButton:
        btn = QPushButton(label)
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn.setFixedHeight(38)
        btn.setFixedWidth(self.BTN_WIDTH)
        if primary:
            btn.setStyleSheet(
                f"QPushButton {{"
                f"  background: {T.ACCENT};"
                f"  color: white;"
                f"  border: none;"
                f"  border-radius: 12px;"
                f"  font-size: 13px;"
                f"  font-weight: 600;"
                f"}}"
                f"QPushButton:hover {{ background: #7A6FD4; }}"
            )
        else:
            btn.setStyleSheet(
                f"QPushButton {{"
                f"  background: {T.BG_RAISED};"
                f"  color: {T.INK_2};"
                f"  border: 1px solid {T.BORDER_RAISED};"
                f"  border-radius: 12px;"
                f"  font-size: 13px;"
                f"  font-weight: 500;"
                f"}}"
                f"QPushButton:hover {{ background: #F3F0EC; color: {T.INK}; }}"
            )
        return btn


# ── footer ────────────────────────────────────────────────────────


class _Footer(QLabel):
    """Single-line trust footer: *local only - no cloud*. 10-px
    ink-3, centred. Directive's calm trust marker — no badge,
    no icon, no link."""

    HEIGHT = 18

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__("local only  ·  no cloud", parent)
        self.setFixedHeight(self.HEIGHT)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        f = QFont()
        f.setPointSizeF(7.5)        # ≈ 10 px on a 96-DPI Windows host
        self.setFont(f)
        self.setStyleSheet(
            f"color: {T.INK_3}; background: transparent;"
            f"letter-spacing: 0.4px;"
        )


# ── shell + window ────────────────────────────────────────────────


class MinimalShell(QWidget):
    """The single column. Directive geometry: outer padding 20,
    search → hero = 20, hero → work = 16, work → footer = 12,
    column max 620."""

    MIN_WIDTH = 480
    MAX_WIDTH = 620

    def __init__(
        self,
        center: QWidget,
        *,
        search: Optional[MinimalSearchBar] = None,
        footer: Optional[_Footer] = None,
        parent: Optional[QWidget] = None,
    ) -> None:
        super().__init__(parent)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        outer = QHBoxLayout(self)
        outer.setContentsMargins(20, 20, 20, 20)    # directive: outer padding 20
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
        cl.addSpacing(20)            # directive: search -> hero = 20
        cl.addWidget(center, 1)
        cl.addSpacing(12)            # directive: work -> footer = 12
        self.footer = footer or _Footer()
        cl.addWidget(self.footer, 0, Qt.AlignmentFlag.AlignHCenter)

        outer.addWidget(column)
        outer.addStretch(1)


class MinimalWindow(QWidget):
    """Top-level floating QWidget. **680 × 440 fixed** (the
    directive's *hard clamp · min = max · no resize*). Warm-paper
    page, solid fill, no transparency, no blur."""

    DEFAULT_SIZE = (680, 440)
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
        # The directive's *hard clamp*.
        self.setFixedSize(*self.DEFAULT_SIZE)

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
        m = self.OUTER_MARGIN
        rect = QRectF(m, m, self.width() - 2 * m, self.height() - 2 * m)
        path.addRoundedRect(rect, 22, 22)
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
