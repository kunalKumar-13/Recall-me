"""Phase 6I — InvestigationCardV3 + InvestigationPanel.

The directive's investigation-card spec:

  - title              (15 px, semibold)
  - timeline strip     three mono-font chips: ``yesterday`` ``9:20`` ``11:04``
                       — the last touches inside this thread
  - targets row        the surface-type chips (`tabs` `files` `chats`)
                       capped at 4
  - last-touch label   right-aligned ink-3 time
  - resume-strength    a 4-segment bar reading 0-4 (visual cue
                       paired with the v2 ConfidenceBadge vocabulary)
  - expand             clicking the card raises ``open_thread`` —
                       same signal name as the v2 card
"""

from __future__ import annotations

from typing import List, Optional

from PyQt6.QtCore import Qt, QEvent, pyqtSignal
from PyQt6.QtGui import (
    QColor,
    QFont,
    QPainter,
    QPainterPath,
    QPen,
)
from PyQt6.QtWidgets import (
    QGraphicsDropShadowEffect,
    QHBoxLayout,
    QLabel,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from . import theme as T
from .surfaces import Pill, TimelineChip, section_label


class _ResumeStrength(QWidget):
    """A 4-segment bar that reads from 0 to 4. Maps to the
    InvestigationCard's *resume strength* signal — the directive's
    visual cue paired with the confidence band on the recovery
    card. Pure paint, no animation; the bar is informational."""

    def __init__(self, score: int = 0, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self._score = max(0, min(4, score))
        self.setFixedSize(48, 6)

    def paintEvent(self, _e) -> None:  # type: ignore[override]
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        gap = 2
        w = (self.width() - gap * 3) // 4
        for i in range(4):
            x = i * (w + gap)
            from PyQt6.QtCore import QRectF
            path = QPainterPath()
            path.addRoundedRect(QRectF(x, 0, w, self.height()), 2, 2)
            colour = QColor(T.ACCENT) if i < self._score else QColor(24, 17, 45, 22)
            p.fillPath(path, colour)
        p.end()


class InvestigationCardV3(QWidget):
    """A single ongoing investigation. Title, timeline strip, target
    chips, last-touch, resume-strength bar.

    Emits ``open_thread(thread_id, topic_key, title)``.
    """

    open_thread = pyqtSignal(str, str, str)

    HEIGHT = 96

    def __init__(
        self,
        thread_id: str,
        topic_key: str,
        title: str,
        *,
        timeline: List[str],
        surface_types: List[str],
        last_touch: str = "active",
        strength: int = 2,
        parent: Optional[QWidget] = None,
    ) -> None:
        super().__init__(parent)
        self._tid = thread_id
        self._topic = topic_key
        self._title = title
        # Phase 6N — keep the sort inputs as attributes so the
        # `sort_for_digest()` helper can group cards by rank
        # without re-parsing the visual labels.
        self._last_touch = (last_touch or "").lower()
        self._strength = int(strength)
        self._hover = False
        self._focused = False

        self.setMinimumHeight(self.HEIGHT)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setAttribute(Qt.WidgetAttribute.WA_Hover, True)

        eff = QGraphicsDropShadowEffect(self)
        eff.setBlurRadius(T.SHADOW_SOFT_RADIUS)
        eff.setOffset(0, 2)
        eff.setColor(QColor(0, 0, 0, T.SHADOW_SOFT_ALPHA))
        self.setGraphicsEffect(eff)

        outer = QVBoxLayout(self)
        outer.setContentsMargins(16, 12, 16, 12)
        outer.setSpacing(8)

        # ── title row ──
        title_row = QHBoxLayout()
        title_row.setSpacing(10)

        title_lbl = QLabel(title)
        tf = QFont()
        tf.setPointSizeF(11.5)
        tf.setBold(True)
        title_lbl.setFont(tf)
        title_lbl.setStyleSheet(
            f"color: {T.INK}; background: transparent; padding: 0;"
        )
        title_lbl.setWordWrap(True)
        title_row.addWidget(title_lbl, 1)

        touch = QLabel(last_touch)
        touch.setStyleSheet(
            f"color: {T.INK_3}; font-size: {T.FS_META}px;"
            f"background: transparent;"
        )
        title_row.addWidget(touch)
        outer.addLayout(title_row)

        # ── timeline strip ──
        if timeline:
            strip = QHBoxLayout()
            strip.setSpacing(T.CHIP_GAP)
            for t in timeline[:3]:
                strip.addWidget(TimelineChip(t))
            strip.addStretch(1)
            outer.addLayout(strip)

        # ── target chips + resume-strength ──
        bottom = QHBoxLayout()
        bottom.setSpacing(T.CHIP_GAP)
        for t in surface_types[:4]:
            bottom.addWidget(Pill(t, kind="mute"))
        bottom.addStretch(1)
        bottom.addWidget(_ResumeStrength(score=strength))
        outer.addLayout(bottom)

    def paintEvent(self, _e) -> None:  # type: ignore[override]
        from PyQt6.QtCore import QRectF
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        path = QPainterPath()
        path.addRoundedRect(QRectF(self.rect()), T.RADIUS_CARD, T.RADIUS_CARD)
        # Soft white on the warm-white bg — same alpha as the
        # GlassCard mid level.
        fill = QColor(255, 255, 255, T.SURFACE_ALPHA_MID + 10)
        p.fillPath(path, fill)
        pen = QPen(QColor(T.ACCENT) if self._focused else QColor(24, 17, 45, 22))
        pen.setWidthF(2.0 if self._focused else 1.0)
        p.setPen(pen)
        p.drawPath(path)
        p.end()

    def enterEvent(self, _e: QEvent) -> None:  # type: ignore[override]
        self._hover = True
        self.update()

    def leaveEvent(self, _e: QEvent) -> None:  # type: ignore[override]
        self._hover = False
        self.update()

    def focusInEvent(self, _e) -> None:  # type: ignore[override]
        self._focused = True
        self.update()

    def focusOutEvent(self, _e) -> None:  # type: ignore[override]
        self._focused = False
        self.update()

    def mouseReleaseEvent(self, e) -> None:  # type: ignore[override]
        if e.button() == Qt.MouseButton.LeftButton:
            self.open_thread.emit(self._tid, self._topic, self._title)

    def keyPressEvent(self, e) -> None:  # type: ignore[override]
        if e.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter, Qt.Key.Key_Space):
            self.open_thread.emit(self._tid, self._topic, self._title)
            return
        super().keyPressEvent(e)


class InvestigationPanel(QWidget):
    """Column container for active-investigation cards."""

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self._layout = QVBoxLayout(self)
        self._layout.setContentsMargins(0, 0, 0, 0)
        self._layout.setSpacing(T.CARD_GAP)
        self._header = section_label("Active investigations")
        self._layout.addWidget(self._header)
        self._cards: List[InvestigationCardV3] = []

    def add_card(self, card: InvestigationCardV3) -> None:
        self._cards.append(card)
        self._layout.addWidget(card)

    def clear(self) -> None:
        for c in self._cards:
            c.setParent(None)
        self._cards.clear()


def _digest_rank(card: InvestigationCardV3) -> int:
    """Phase 6N — group investigations by the directive's rank:

      0  unfinished        — high-strength threads still in flight
      1  returned          — last_touch mentions return / revisit
      2  recent            — last_touch is a fresh time label
      3  passive           — everything else

    The launcher's digest sort uses (rank, -strength, title) so
    rank dominates and high-strength threads come first within a
    rank. The function is pure — no I/O, no Qt — so consumers can
    unit-test it in isolation.
    """
    lt = card._last_touch  # noqa: SLF001
    s = card._strength      # noqa: SLF001

    # unfinished — high strength + not explicitly resolved.
    if s >= 3 and not lt.startswith("resolved") and not lt.startswith("done"):
        return 0
    # returned — last_touch carries an explicit return marker.
    if "return" in lt or "revisit" in lt or "back" in lt:
        return 1
    # recent — short relative-time label.
    if lt in ("today", "now", "active") or lt.endswith("h") or (
        lt.endswith("d") and lt[:-1].isdigit() and int(lt[:-1]) <= 3
    ):
        return 2
    return 3


def sort_for_digest(cards: List[InvestigationCardV3]) -> List[InvestigationCardV3]:
    """Order investigation cards for the launcher's digest strip.

    Stable; produces a new list (does not mutate the input). The
    directive's order: **unfinished first · returned second ·
    recent third · passive last**, with high-strength threads
    winning within each rank.
    """
    return sorted(
        cards,
        key=lambda c: (
            _digest_rank(c),
            -c._strength,   # noqa: SLF001  — high strength wins
            c._title.lower() if c._title else "",  # noqa: SLF001
        ),
    )


__all__ = [
    "InvestigationCardV3",
    "InvestigationPanel",
    "sort_for_digest",
]
