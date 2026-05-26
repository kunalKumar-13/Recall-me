"""Phase 7B.1 — Launcher Visual Merge · minimal surface.

The launcher rebuilds toward the Stitch reference. Single
white workspace (740×500), the centre carries either a
**document-preview** hero or an *infinity-glyph empty state*,
and the bottom is a single quiet strip with the trust line on
the left and tiny text links on the right.

    +----------------------------------------------------+
    | (warm #F4F1EC page)                                |
    |  +----------------------------------------------+  |
    |  | [ Start typing to recover...   settings × CtrlK ] |  |
    |  |                                              |  |
    |  |   CONTINUE                                   |  |
    |  |   WebSocket retry debugging                  |  |
    |  |   - 2 files                                  |  |
    |  |   - 2 tabs                                   |  |
    |  |   - returned after 2d                        |  |
    |  |                              [ Resume    1 ] |  |
    |  |                                              |  |
    |  |  End-to-end encrypted   Privacy Demo Docs    |  |
    |  +----------------------------------------------+  |
    +----------------------------------------------------+

Pre-7B.1 (the 7B "single root card + dense recovery row +
OTHER WORK list") lives at ``archive/launcher-raycast/`` with
a per-file README.
"""

from __future__ import annotations

from typing import List, Optional

from PyQt6.QtCore import QRectF, Qt, pyqtSignal
from PyQt6.QtGui import QColor, QFont, QPainter, QPainterPath, QPen
from PyQt6.QtWidgets import (
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
    """Hand-drawn magnifying glass — circle + handle."""

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


# ── gear / close glyphs ───────────────────────────────────────────


class _IconButton(QWidget):
    """A small icon button — settings cog or close X."""

    KIND_SETTINGS = "settings"
    KIND_CLOSE = "close"

    clicked = pyqtSignal()

    SIZE = 26

    def __init__(self, kind: str, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self._kind = kind
        self._hover = False
        self.setFixedSize(self.SIZE, self.SIZE)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setAttribute(Qt.WidgetAttribute.WA_Hover, True)

    def enterEvent(self, _e) -> None:  # type: ignore[override]
        self._hover = True
        self.update()

    def leaveEvent(self, _e) -> None:  # type: ignore[override]
        self._hover = False
        self.update()

    def mouseReleaseEvent(self, e) -> None:  # type: ignore[override]
        if e.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit()

    def paintEvent(self, _e) -> None:  # type: ignore[override]
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        if self._hover:
            bg = QPainterPath()
            bg.addRoundedRect(QRectF(self.rect()), 7, 7)
            p.fillPath(bg, QColor("#ECE6DC"))
        pen = QPen(QColor(T.INK_3))
        pen.setWidthF(1.5)
        p.setPen(pen)
        cx, cy = self.SIZE / 2, self.SIZE / 2
        if self._kind == self.KIND_SETTINGS:
            # A small cog — circle + 8 short ticks.
            p.setBrush(Qt.BrushStyle.NoBrush)
            p.drawEllipse(QRectF(cx - 4, cy - 4, 8, 8))
            import math
            for i in range(8):
                a = i * math.pi / 4
                p.drawLine(
                    int(cx + 5 * math.cos(a)), int(cy + 5 * math.sin(a)),
                    int(cx + 7 * math.cos(a)), int(cy + 7 * math.sin(a)),
                )
        elif self._kind == self.KIND_CLOSE:
            # An X.
            p.drawLine(int(cx - 4), int(cy - 4), int(cx + 4), int(cy + 4))
            p.drawLine(int(cx + 4), int(cy - 4), int(cx - 4), int(cy + 4))
        p.end()


# ── search bar ────────────────────────────────────────────────────


class MinimalSearchBar(QWidget):
    """Full-width search row at the top of the workspace. Soft
    border, settings + close on the right, Ctrl K hint chip beside
    them. Placeholder *Start typing to recover…*."""

    query_changed = pyqtSignal(str)
    submit = pyqtSignal(str)
    request_settings = pyqtSignal()
    request_close = pyqtSignal()

    HEIGHT = 52
    RADIUS = 14

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.setFixedHeight(self.HEIGHT)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, False)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 0, 12, 0)
        layout.setSpacing(10)
        layout.addWidget(_SearchIcon(), 0, Qt.AlignmentFlag.AlignVCenter)

        self._input = QLineEdit()
        self._input.setPlaceholderText("Start typing to recover…")
        self._input.setFixedHeight(self.HEIGHT - 2)
        self._input.setStyleSheet(
            f"QLineEdit {{"
            f"  background: transparent;"
            f"  color: {T.INK};"
            f"  border: none;"
            f"  padding: 0;"
            f"  font-size: 14px;"
            f"}}"
        )
        self._input.textChanged.connect(self.query_changed.emit)
        self._input.returnPressed.connect(
            lambda: self.submit.emit(self._input.text())
        )
        self._input.installEventFilter(self)
        layout.addWidget(self._input, 1)

        self._settings_btn = _IconButton(_IconButton.KIND_SETTINGS)
        self._settings_btn.clicked.connect(self.request_settings.emit)
        layout.addWidget(self._settings_btn, 0, Qt.AlignmentFlag.AlignVCenter)

        self._close_btn = _IconButton(_IconButton.KIND_CLOSE)
        self._close_btn.clicked.connect(self.request_close.emit)
        layout.addWidget(self._close_btn, 0, Qt.AlignmentFlag.AlignVCenter)

        # Ctrl K hint chip — sits to the right of the icons, hidden on focus.
        self._hint = QLabel("Ctrl K")
        hf = QFont()
        hf.setPointSizeF(7.5)
        hf.setBold(True)
        self._hint.setFont(hf)
        self._hint.setStyleSheet(
            f"QLabel {{"
            f"  color: {T.INK_4};"
            f"  background: transparent;"
            f"  padding: 2px 6px;"
            f"  border: 1px solid {T.BORDER_RAISED};"
            f"  border-radius: 5px;"
            f"  letter-spacing: 0.8px;"
            f"}}"
        )
        layout.addWidget(self._hint, 0, Qt.AlignmentFlag.AlignVCenter)

        self._focused = False

    def eventFilter(self, obj, event):  # type: ignore[override]
        from PyQt6.QtCore import QEvent
        if obj is self._input:
            if event.type() == QEvent.Type.FocusIn:
                self._focused = True
                self._hint.setVisible(False)
                self.update()
            elif event.type() == QEvent.Type.FocusOut:
                self._focused = False
                self._hint.setVisible(True)
                self.update()
        return super().eventFilter(obj, event)

    def paintEvent(self, _e) -> None:  # type: ignore[override]
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        path = QPainterPath()
        path.addRoundedRect(QRectF(self.rect()), self.RADIUS, self.RADIUS)
        # Soft fill — the search row sits inside the white workspace
        # so a quiet warm-paper fill marks it as the input.
        p.fillPath(path, QColor("#FAF7F1"))
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
    lbl = QLabel(text.upper())
    f = QFont()
    f.setPointSizeF(7.5)
    f.setBold(True)
    lbl.setFont(f)
    lbl.setStyleSheet(
        f"color: {T.INK_3};"
        f"background: transparent;"
        f"letter-spacing: 1.4px;"
        f"padding: 0;"
    )
    return lbl


# ── digest (centre stack) ─────────────────────────────────────────


class MinimalDigest(QWidget):
    """The centre column when the launcher has a recovery to show.
    Just the hero document. Investigations are removed from the
    visible surface in 7B.1 — single-focus tool."""

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self._hero_section = QVBoxLayout()
        self._hero_section.setContentsMargins(0, 0, 0, 0)
        self._hero_section.setSpacing(10)
        layout.addLayout(self._hero_section)
        self._hero: Optional[RecoveryCardV3] = None

        # The InvestigationList stub stays — kept for the keyboard
        # back-compat (`row._titles` is queried by live.py) but it
        # is never visible in 7B.1. The legacy callers still get
        # an empty list; nothing renders.
        self.row = InvestigationList()
        self.row.setVisible(False)
        layout.addWidget(self.row)

        layout.addStretch(1)

    def populate(
        self,
        *,
        hero: Optional[RecoveryCardV3],
        investigations: List[InvestigationCardV3],  # accepted; ignored in 7B.1
    ) -> None:
        if self._hero is not None:
            self._hero_section.removeWidget(self._hero)
            self._hero.setParent(None)
            self._hero = None
        # 7B.1 — no outer section eyebrow. The Continue document
        # carries its own `CONTINUE` eyebrow inside the card so
        # the centre column stays single-focus.
        if hero is not None:
            self._hero = hero
            self._hero_section.addWidget(hero)
        # Investigations are deliberately dropped — see the
        # phase docstring + the audit file.
        self.row.populate([])


# ── empty surface ─────────────────────────────────────────────────


class _InfinityGlyph(QWidget):
    """The empty-state icon. A single horizontal infinity lemniscate
    painted via two overlapping cubic curves — calm, lavender,
    self-contained. Replaces the prior lavender square."""

    SIZE = 76

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.setFixedSize(self.SIZE, self.SIZE)

    def paintEvent(self, _e) -> None:  # type: ignore[override]
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        # Soft halo behind the curve so the glyph reads as a
        # focal point rather than an isolated outline.
        halo = QPainterPath()
        halo.addEllipse(8, 18, 60, 40)
        p.fillPath(halo, QColor(T.ACCENT_SOFT))
        # Lemniscate curve.
        pen = QPen(QColor(T.ACCENT))
        pen.setWidthF(2.4)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        p.setPen(pen)
        p.setBrush(Qt.BrushStyle.NoBrush)
        path = QPainterPath()
        # Two overlapping ellipses approximate the ∞ shape.
        path.addEllipse(14, 26, 26, 24)
        path.addEllipse(36, 26, 26, 24)
        p.drawPath(path)
        p.end()


class MinimalEmpty(QWidget):
    """Empty workspace. Centred stack: infinity glyph · 26-pt
    headline · 14-pt sub · Show example + Start working. The
    directive's *Looks like product. Not utility.* north star
    lands here first — this is the launcher's first impression."""

    show_example = pyqtSignal()
    start_normally = pyqtSignal()

    BTN_WIDTH = 200

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(14)
        outer.addStretch(1)

        # Infinity glyph.
        glyph_row = QHBoxLayout()
        glyph_row.setSpacing(0)
        glyph_row.addStretch(1)
        glyph_row.addWidget(_InfinityGlyph())
        glyph_row.addStretch(1)
        outer.addLayout(glyph_row)

        outer.addSpacing(4)

        headline = QLabel("Everything you’ve seen, searchable.")
        hf = QFont()
        hf.setPointSizeF(20.0)            # 26-pt logical via Qt sizing
        hf.setBold(True)
        headline.setFont(hf)
        headline.setStyleSheet(
            f"color: {T.INK}; background: transparent;"
            f"letter-spacing: -0.2px;"
        )
        headline.setAlignment(Qt.AlignmentFlag.AlignCenter)
        outer.addWidget(headline)

        sub = QLabel("Your digital continuity layer.")
        sub.setStyleSheet(
            f"color: {T.INK_3}; background: transparent;"
            f"font-size: 14px;"
        )
        sub.setAlignment(Qt.AlignmentFlag.AlignCenter)
        outer.addWidget(sub)

        outer.addSpacing(10)

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
        btn.setFixedHeight(36)
        btn.setFixedWidth(self.BTN_WIDTH)
        if primary:
            btn.setStyleSheet(
                f"QPushButton {{"
                f"  background: {T.ACCENT};"
                f"  color: white;"
                f"  border: none;"
                f"  border-radius: 10px;"
                f"  font-size: 13px;"
                f"  font-weight: 600;"
                f"}}"
                f"QPushButton:hover {{ background: #7A6FD4; }}"
            )
        else:
            btn.setStyleSheet(
                f"QPushButton {{"
                f"  background: transparent;"
                f"  color: {T.INK_2};"
                f"  border: 1px solid {T.BORDER_RAISED};"
                f"  border-radius: 10px;"
                f"  font-size: 13px;"
                f"  font-weight: 500;"
                f"}}"
                f"QPushButton:hover {{ background: #ECE6DC; color: {T.INK}; }}"
            )
        return btn


# ── bottom strip ──────────────────────────────────────────────────


class _BottomStrip(QWidget):
    """Single horizontal row pinned at the bottom of the workspace.
    Trust line on the left, tiny text links on the right.

    Per directive: *End-to-end encrypted. Local storage only.* on
    the left, *Privacy · Demo · Docs · Browser* on the right.
    """

    HEIGHT = 22

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.setFixedHeight(self.HEIGHT)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        trust = QLabel("End-to-end encrypted. Local storage only.")
        tf = QFont()
        tf.setPointSizeF(7.5)
        trust.setFont(tf)
        trust.setStyleSheet(
            f"color: {T.INK_3}; background: transparent;"
            f"letter-spacing: 0.2px;"
        )
        layout.addWidget(trust, 0, Qt.AlignmentFlag.AlignVCenter)
        layout.addStretch(1)

        for label in ("Privacy", "Demo", "Docs", "Browser"):
            link = QLabel(label)
            lf = QFont()
            lf.setPointSizeF(7.5)
            link.setFont(lf)
            link.setStyleSheet(
                f"color: {T.INK_3}; background: transparent;"
                f"padding: 0 8px;"
            )
            link.setCursor(Qt.CursorShape.PointingHandCursor)
            layout.addWidget(link, 0, Qt.AlignmentFlag.AlignVCenter)


# ── shell + window ────────────────────────────────────────────────


class MinimalShell(QWidget):
    """The single column inside the workspace. 24-px padding on
    every edge; the centre stack flexes; the bottom strip pins."""

    MIN_WIDTH = 540
    MAX_WIDTH = 680

    def __init__(
        self,
        center: QWidget,
        *,
        search: Optional[MinimalSearchBar] = None,
        bottom: Optional[_BottomStrip] = None,
        parent: Optional[QWidget] = None,
    ) -> None:
        super().__init__(parent)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        outer = QHBoxLayout(self)
        outer.setContentsMargins(24, 20, 24, 16)
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
        cl.addSpacing(20)
        cl.addWidget(center, 1)
        cl.addSpacing(10)
        self.bottom = bottom or _BottomStrip()
        cl.addWidget(self.bottom)

        outer.addWidget(column)
        outer.addStretch(1)


class MinimalWindow(QWidget):
    """Top-level workspace. **740 × 500 fixed**. Warm-paper page
    (`#F4F1EC`) with a **single white workspace** floating inside
    at a 16-px gutter, radius 22, soft drop shadow."""

    DEFAULT_SIZE = (740, 500)
    OUTER_MARGIN = 16
    ROOT_RADIUS = 22

    def __init__(
        self,
        center: QWidget,
        *,
        search: Optional[MinimalSearchBar] = None,
        parent: Optional[QWidget] = None,
    ) -> None:
        super().__init__(parent)
        self.setObjectName("launcher_v3_window")
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
        # Step 1 — warm-paper page.
        p.fillRect(self.rect(), QColor(T.BG))
        # Step 2 — single white workspace inside the outer margin.
        m = self.OUTER_MARGIN
        rect = QRectF(m, m, self.width() - 2 * m, self.height() - 2 * m)
        # Soft drop shadow (manual paint, no QGraphicsDropShadowEffect).
        shadow = QPainterPath()
        shadow.addRoundedRect(
            rect.adjusted(0, 4, 0, 4), self.ROOT_RADIUS, self.ROOT_RADIUS,
        )
        p.fillPath(shadow, QColor(0, 0, 0, 20))
        body = QPainterPath()
        body.addRoundedRect(rect, self.ROOT_RADIUS, self.ROOT_RADIUS)
        p.fillPath(body, QColor(T.BG_RAISED))
        pen = QPen(QColor(T.BORDER_RAISED))
        pen.setWidthF(1.0)
        p.setPen(pen)
        p.drawPath(body)
        p.end()


__all__ = [
    "MinimalSearchBar",
    "MinimalDigest",
    "MinimalEmpty",
    "MinimalShell",
    "MinimalWindow",
]
