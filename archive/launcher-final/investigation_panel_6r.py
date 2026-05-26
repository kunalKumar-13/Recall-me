"""Phase 6R — Launcher Finalization · OTHER WORK list.

Vertical list. Each row 44 px tall: small lavender dot + title +
quiet right arrow. Max 3 rows. **No** pills, **no** bubbles,
**no** horizontal row, **no** overflow chip.

  +------------------------------------------------+
  |  .   WebSocket retry debugging              >  |
  |  .   Healthcare proposal draft              >  |
  |  .   RLHF notes                             >  |
  +------------------------------------------------+

The horizontal row (6O) read as *adrift text* at arm's length;
the vertical list reads as *a list of things you can click*.

Pre-6R variant lives at `archive/launcher-debt/investigation_panel_6o.py`.
"""

from __future__ import annotations

from typing import List, Optional

from PyQt6.QtCore import QRectF, Qt, pyqtSignal
from PyQt6.QtGui import QColor, QFont, QFontMetrics, QPainter, QPainterPath, QPen
from PyQt6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from . import theme as T


class _Dot(QWidget):
    """A 6-px lavender dot painted at the left of the row. Constant
    size, fixed colour — the marker, not a state indicator."""

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
    """A small right-pointing chevron in ink-3. Painted (not text)
    so the row stays consistent across hosts whose fonts may or
    may not carry the `›` glyph."""

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
    Enter / Space. Hover changes the title colour from `INK_2` →
    `INK` (the only allowed motion).
    """

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
        layout.setContentsMargins(14, 0, 14, 0)
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
        # Elide the title to fit between the dot + arrow.
        # The available width is the label's own width minus a
        # small inset; QFontMetrics handles the cut.
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
    Anything past the third is dropped — directive's max 3."""

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

    def paintEvent(self, _e) -> None:  # type: ignore[override]
        # Card chrome: white fill + warm-grey hairline border, radius
        # 16. Rows sit edge-to-edge; a 1-px divider is painted
        # between consecutive rows so the list reads as a list.
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        path = QPainterPath()
        path.addRoundedRect(QRectF(self.rect()), 16, 16)
        p.fillPath(path, QColor(T.BG_RAISED))
        pen = QPen(QColor(T.BORDER_RAISED))
        pen.setWidthF(1.0)
        p.setPen(pen)
        p.drawPath(path)
        # Inter-row dividers.
        if len(self._rows) > 1:
            divider = QPen(QColor(T.BORDER_RAISED))
            divider.setWidthF(1.0)
            p.setPen(divider)
            for i, row in enumerate(self._rows[:-1]):
                y = row.geometry().bottom()
                p.drawLine(14, y, self.width() - 14, y)
        p.end()


# Back-compat aliases — the prior surface exposed `InvestigationRow`;
# the live launcher still imports under that name in one place.
InvestigationRow = InvestigationList


__all__ = [
    "InvestigationCardV3",
    "InvestigationList",
    "InvestigationRow",
]
