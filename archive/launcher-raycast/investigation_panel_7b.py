"""Phase 7B — Launcher Production Freeze · OTHER WORK list.

Vertical list of up to **3** rows sitting *directly* on the
white root card. Each row is 44 px tall: small lavender dot +
title + quiet right chevron. **No** wrapping card chrome — only
1-px hairline dividers between rows.

  .  WebSocket retry debugging                              >
  .  Healthcare proposal draft                              >
  .  RLHF notes                                             >

Pre-7B variant (wrapped in a white card with border + shadow)
lives at ``archive/launcher-final/investigation_panel_6r.py``.
"""

from __future__ import annotations

from typing import List, Optional

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QColor, QFont, QFontMetrics, QPainter, QPen
from PyQt6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from . import theme as T


class _Dot(QWidget):
    """A 6-px lavender dot painted at the left of the row."""

    SIZE = 6

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.setFixedSize(self.SIZE + 2, self.SIZE + 2)

    def paintEvent(self, _e) -> None:  # type: ignore[override]
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(QColor(T.ACCENT))
        p.drawEllipse(1, 1, self.SIZE, self.SIZE)
        p.end()


class _Arrow(QWidget):
    """A small right-pointing chevron in ink-3."""

    SIZE = 10

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.setFixedSize(self.SIZE, self.SIZE)

    def paintEvent(self, _e) -> None:  # type: ignore[override]
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        pen = QPen(QColor(T.INK_3))
        pen.setWidthF(1.5)
        p.setPen(pen)
        p.drawLine(2, 1, 7, 5)
        p.drawLine(7, 5, 2, 9)
        p.end()


class InvestigationCardV3(QWidget):
    """One row of the OTHER WORK list. 44 px tall.

    Emits ``open_thread(thread_id, topic_key, title)`` on click /
    Enter / Space."""

    open_thread = pyqtSignal(str, str, str)

    HEIGHT = 44

    def __init__(
        self,
        thread_id: str,
        topic_key: str,
        title: str,
        parent: Optional[QWidget] = None,
    ) -> None:
        super().__init__(parent)
        self._tid = thread_id
        self._topic = topic_key
        self._title = title
        self._hover = False

        self.setFixedHeight(self.HEIGHT)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setAttribute(Qt.WidgetAttribute.WA_Hover, True)

        layout = QHBoxLayout(self)
        # No internal left/right padding — the root card's padding
        # already provides the row's gutter. The dot anchors the
        # left edge; the chevron anchors the right.
        layout.setContentsMargins(2, 0, 4, 0)
        layout.setSpacing(12)
        layout.addWidget(_Dot(), 0, Qt.AlignmentFlag.AlignVCenter)

        self._title_lbl = QLabel(title)
        f = QFont()
        f.setPointSizeF(11.5)
        self._title_lbl.setFont(f)
        self._title_lbl.setStyleSheet(
            f"color: {T.INK_2}; background: transparent; padding: 0;"
        )
        self._title_lbl.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred
        )
        layout.addWidget(self._title_lbl, 1)

        layout.addWidget(_Arrow(), 0, Qt.AlignmentFlag.AlignVCenter)

    def _refresh_title_colour(self) -> None:
        colour = T.INK if self._hover else T.INK_2
        self._title_lbl.setStyleSheet(
            f"color: {colour}; background: transparent; padding: 0;"
        )

    def resizeEvent(self, e) -> None:  # type: ignore[override]
        super().resizeEvent(e)
        fm = QFontMetrics(self._title_lbl.font())
        avail = max(0, self._title_lbl.width() - 4)
        elided = fm.elidedText(self._title, Qt.TextElideMode.ElideRight, avail)
        if elided != self._title_lbl.text():
            self._title_lbl.setText(elided)

    def enterEvent(self, _e) -> None:  # type: ignore[override]
        self._hover = True
        self._refresh_title_colour()

    def leaveEvent(self, _e) -> None:  # type: ignore[override]
        self._hover = False
        self._refresh_title_colour()

    def mouseReleaseEvent(self, e) -> None:  # type: ignore[override]
        if e.button() == Qt.MouseButton.LeftButton:
            self.open_thread.emit(self._tid, self._topic, self._title)

    def keyPressEvent(self, e) -> None:  # type: ignore[override]
        if e.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter, Qt.Key.Key_Space):
            self.open_thread.emit(self._tid, self._topic, self._title)
            return
        super().keyPressEvent(e)


class InvestigationList(QWidget):
    """A vertical list of up to **three** investigation rows.
    **No wrapping card** — paints 1-px hairline dividers between
    consecutive rows directly on the root card."""

    activated = pyqtSignal(str, str, str)
    MAX_VISIBLE = 3

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, False)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        self._layout = layout
        self._rows: List[InvestigationCardV3] = []

    @property
    def _titles(self) -> List[InvestigationCardV3]:
        """Back-compat alias the live launcher's keyboard layer
        references."""
        return self._rows

    def populate(self, items: List[InvestigationCardV3]) -> None:
        while self._layout.count():
            it = self._layout.takeAt(0)
            w = it.widget()
            if w is not None:
                w.setParent(None)
        self._rows.clear()
        for row in items[: self.MAX_VISIBLE]:
            row.open_thread.connect(self.activated.emit)
            self._rows.append(row)
            self._layout.addWidget(row)
        self.update()

    def paintEvent(self, _e) -> None:  # type: ignore[override]
        # 1-px hairline dividers between rows — no wrapping card.
        if len(self._rows) <= 1:
            return
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing, False)
        pen = QPen(QColor(T.BORDER_RAISED))
        pen.setWidthF(1.0)
        p.setPen(pen)
        for row in self._rows[:-1]:
            y = row.geometry().bottom()
            p.drawLine(0, y, self.width(), y)
        p.end()


# Back-compat alias — earlier phases imported `InvestigationRow`.
InvestigationRow = InvestigationList


__all__ = [
    "InvestigationCardV3",
    "InvestigationList",
    "InvestigationRow",
]
