"""Phase 7E — Launcher Final Product Pass · minimal surface.

720 × 460 hard-clamped. Warm `#F5F2ED` page outside; one
white inner card with radius 24 + 24-px padding inside. Five
content regions stack inside the card with no nested chrome:

    +---------------------------------------------------+
    | (warm #F5F2ED page)                               |
    | +-----------------------------------------------+ |
    | | [Q Search investigations...           Ctrl K] | |
    | | Recall noticed unfinished work                | |
    | |                                               | |
    | | CONTINUE                                      | |
    | | | WebSocket retry debugging          [Resume] | |
    | |  2 files - 2 tabs - returned 2d        HIGH   | |
    | |                                               | |
    | | RECENT MEMORY                                 | |
    | | 21:32  ChatGPT     RLHF reward shaping        | |
    | | 21:28  GitHub      websocket retry            | |
    | | 21:20  Stitch      launcher redesign          | |
    | | 21:11  Google      resume flow                | |
    | | 20:55  StackOverf  websocket reconnect        | |
    | |                                               | |
    | | OTHER WORK                                    | |
    | | o Healthcare proposal draft              3d   | |
    | | o RLHF reward shaping notes              5d   | |
    | | o Marketing rewrite                      1w   | |
    | |                                               | |
    | | LOCAL  NO CLOUD  71 EVENTS  11 INVESTIGATIONS | |
    | +-----------------------------------------------+ |
    +---------------------------------------------------+

Pre-7E (Stitch single-document workspace, no memory list)
lives at ``archive/launcher-7b1/``.
"""



from __future__ import annotations

from typing import List, Optional

from PyQt6.QtCore import QRectF, Qt, pyqtSignal
from PyQt6.QtGui import QColor, QFont, QPainter, QPainterPath, QPen
from PyQt6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from . import theme as T
from .investigation_panel import InvestigationCardV3, InvestigationList
from .recent_memory import MemoryRow, RecentMemoryList
from .recovery_panel import RecoveryCardV3


# ── search-icon glyph ─────────────────────────────────────────────


class _SearchIcon(QWidget):
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
    """52-px search row inside the inner card. Soft warm-paper
    fill, hand-drawn glyph, lavender focus ring, Ctrl K hint
    chip auto-hidden on focus. Placeholder *Search investigations…*.

    **Public contract (Phase 7E.1 — frozen).** See
    ``docs/product/LAUNCHER_CONTRACTS.md``. Future launcher
    phases may *add* to this surface; they **must not remove
    or rename** the symbols below.

    Signals
        - ``query_changed(str)`` — fires on every text change.
        - ``searchChanged(str)`` — alias of ``query_changed``;
          the documented contract name.
        - ``submit(str)`` — fires on Return.
        - ``request_settings()`` — emitted by an optional
          settings affordance. None in 7E; declared so host
          wiring (`LiveLauncher.__init__`) stays valid even
          when no widget fires it.
        - ``request_close()`` — same reason: declared so the
          host's `connect(...)` doesn't `AttributeError`.

    Methods
        - ``focus()`` — move keyboard focus to the input.
        - ``clear()`` — empty the input.
        - ``selectAll()`` — select the input's full text.
    """

    # Frozen contract — Phase 7E.1.
    query_changed = pyqtSignal(str)
    searchChanged = pyqtSignal(str)
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
        self._input.setPlaceholderText("Search investigations…")
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
        # Fire both contract names from the same textChanged so a
        # consumer can subscribe to either spelling.
        self._input.textChanged.connect(self.query_changed.emit)
        self._input.textChanged.connect(self.searchChanged.emit)
        self._input.returnPressed.connect(
            lambda: self.submit.emit(self._input.text())
        )
        self._input.installEventFilter(self)
        layout.addWidget(self._input, 1)

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

    def clear(self) -> None:  # noqa: D401  (contract method)
        """Empty the input — part of the frozen contract."""
        self._input.clear()

    def selectAll(self) -> None:  # noqa: N802  (Qt method casing)
        """Select the input's full text — frozen contract."""
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


# ── sub-tagline (under search) ───────────────────────────────────


class _Tagline(QLabel):
    """*Recall noticed unfinished work* — 13-px muted lavender
    line that lives directly under the search row."""

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__("Recall noticed unfinished work", parent)
        f = QFont()
        f.setPointSizeF(9.0)
        self.setFont(f)
        self.setStyleSheet(
            f"color: {T.ACCENT};"
            f"background: transparent;"
            f"font-weight: 600;"
            f"letter-spacing: 0.1px;"
        )


# ── trust row (footer) ───────────────────────────────────────────


class TrustRow(QWidget):
    """Four tiny pinned pills carrying live trust + capture
    counts: LOCAL · NO CLOUD · `N` EVENTS · `M` INVESTIGATIONS.
    The two count pills are populated by `LiveLauncher` from the
    same disk reads the Phase 7D `recall capture status` CLI
    uses, so the pill values match the CLI's report."""

    HEIGHT = 22

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.setFixedHeight(self.HEIGHT)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(6)
        layout.addStretch(1)
        self._pills: List[QLabel] = []
        for label in ("LOCAL", "NO CLOUD", "0 EVENTS", "0 INVESTIGATIONS"):
            pill = self._make_pill(label, accent=False)
            self._pills.append(pill)
            layout.addWidget(pill)
        layout.addStretch(1)

    def _make_pill(self, text: str, *, accent: bool) -> QLabel:
        pill = QLabel(text)
        pill.setFixedHeight(18)
        pill.setAlignment(Qt.AlignmentFlag.AlignCenter)
        f = QFont()
        f.setPointSizeF(7.0)
        f.setBold(True)
        pill.setFont(f)
        if accent:
            pill.setStyleSheet(
                f"QLabel {{"
                f"  color: {T.ACCENT};"
                f"  background: {T.ACCENT_SOFT};"
                f"  border-radius: 9px;"
                f"  padding: 0 8px;"
                f"  letter-spacing: 1.0px;"
                f"}}"
            )
        else:
            pill.setStyleSheet(
                f"QLabel {{"
                f"  color: {T.INK_3};"
                f"  background: {T.BG};"
                f"  border: 1px solid {T.BORDER_RAISED};"
                f"  border-radius: 9px;"
                f"  padding: 0 8px;"
                f"  letter-spacing: 1.0px;"
                f"}}"
            )
        return pill

    def set_counts(self, events_today: int, investigations: int) -> None:
        """Update the live-count pills (indexes 2 + 3). Called by
        `LiveLauncher._populate_digest` after every refresh."""
        self._pills[2].setText(f"{events_today} EVENTS TODAY")
        self._pills[3].setText(f"{investigations} INVESTIGATIONS")


# ── populated body ────────────────────────────────────────────────


class MinimalDigest(QWidget):
    """Search · tagline · CONTINUE · RECENT MEMORY · OTHER WORK
    · trust row. All five sections stack directly on the inner
    white card."""

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Hero (with eyebrow).
        self._hero_eyebrow = _section_label("Continue")
        layout.addWidget(self._hero_eyebrow)
        layout.addSpacing(6)
        self._hero_holder = QVBoxLayout()
        self._hero_holder.setContentsMargins(0, 0, 0, 0)
        self._hero_holder.setSpacing(0)
        layout.addLayout(self._hero_holder)
        self._hero: Optional[RecoveryCardV3] = None

        layout.addSpacing(16)

        # Recent memory.
        self._memory_eyebrow = _section_label("Recent memory")
        layout.addWidget(self._memory_eyebrow)
        layout.addSpacing(8)
        self._memory = RecentMemoryList()
        layout.addWidget(self._memory)

        layout.addSpacing(12)

        # Other work.
        self._other_eyebrow = _section_label("Other work")
        layout.addWidget(self._other_eyebrow)
        layout.addSpacing(6)
        self._list = InvestigationList()
        layout.addWidget(self._list)
        # back-compat alias the live launcher's keyboard layer
        # reads.
        self.row = self._list

        layout.addStretch(1)

    def populate(
        self,
        *,
        hero: Optional[RecoveryCardV3],
        memory: List[MemoryRow],
        investigations: List[InvestigationCardV3],
    ) -> None:
        # Hero swap.
        if self._hero is not None:
            self._hero_holder.removeWidget(self._hero)
            self._hero.setParent(None)
            self._hero = None
        if hero is not None:
            self._hero = hero
            self._hero_holder.addWidget(hero)
        # Hide the eyebrow when there's no hero so the section
        # stays calm.
        self._hero_eyebrow.setVisible(hero is not None)

        # Memory list.
        self._memory.populate(memory)
        has_memory = bool(memory)
        self._memory.setVisible(has_memory)
        self._memory_eyebrow.setVisible(has_memory)

        # Investigations list.
        self._list.populate(investigations)
        has_invs = bool(investigations)
        self._list.setVisible(has_invs)
        self._other_eyebrow.setVisible(has_invs)


# ── empty surface (kept as the API contract, but degraded) ───────


class MinimalEmpty(QWidget):
    """7E removes the dedicated empty surface — the launcher
    always shows *something* memory-shaped (the daemon is the
    source of truth, not a single boolean flag).

    This class survives at a thin stub so the legacy `setView`
    swap in `live.py` doesn't break. The two signals are
    preserved; the widget renders a calm short line so the
    swap is safe."""

    show_example = pyqtSignal()
    start_normally = pyqtSignal()

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addStretch(1)
        lbl = QLabel("Recall is listening. Work normally — memory builds up.")
        f = QFont()
        f.setPointSizeF(10.5)
        lbl.setFont(f)
        lbl.setStyleSheet(
            f"color: {T.INK_3}; background: transparent;"
        )
        lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(lbl)
        layout.addStretch(2)


# ── shell + window ────────────────────────────────────────────────


class MinimalShell(QWidget):
    """The single column inside the inner card. 24-px padding on
    every edge per the 7E directive. Hosts the search bar at
    the top, the body (digest or empty) in the middle, and the
    trust row at the bottom."""

    def __init__(
        self,
        center: QWidget,
        *,
        search: Optional[MinimalSearchBar] = None,
        tagline: Optional[_Tagline] = None,
        trust: Optional[TrustRow] = None,
        parent: Optional[QWidget] = None,
    ) -> None:
        super().__init__(parent)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        outer = QVBoxLayout(self)
        # 7E directive: card padding 24. Tightened to 20-side /
        # 16-vertical so the five sections fit at the directive's
        # 720×460 hard clamp.
        outer.setContentsMargins(20, 16, 20, 14)
        outer.setSpacing(0)

        self.search = search or MinimalSearchBar()
        outer.addWidget(self.search)
        outer.addSpacing(6)
        self.tagline = tagline or _Tagline()
        outer.addWidget(self.tagline)
        outer.addSpacing(12)

        outer.addWidget(center, 1)

        outer.addSpacing(8)
        self.trust = trust or TrustRow()
        outer.addWidget(self.trust)


class MinimalWindow(QWidget):
    """Top-level launcher. **720 × 460** hard clamp (no resize).
    Warm `#F5F2ED` page outside; one white inner card with
    radius 24 inside a 12-px outer gutter; soft manual drop
    shadow."""

    DEFAULT_SIZE = (720, 460)
    OUTER_MARGIN = 12
    ROOT_RADIUS = 24

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
        # 1. Warm-paper page.
        p.fillRect(self.rect(), QColor(T.BG))
        # 2. Manual soft shadow + white inner card.
        m = self.OUTER_MARGIN
        rect = QRectF(m, m, self.width() - 2 * m, self.height() - 2 * m)
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
    "TrustRow",
]
