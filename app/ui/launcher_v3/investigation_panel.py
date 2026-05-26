"""Phase 7E — Launcher Final Product Pass · OTHER WORK list.

OTHER WORK is back from its 7B.1 stub. Compact 36-px rows
inside the inner white card with 1-px hairline dividers
between consecutive rows:

  o  Healthcare proposal draft                        3d
  o  RLHF reward shaping notes                        5d
  o  Marketing rewrite                                1w

Strength dot (lavender or muted), title (elided), last-seen
caption right-aligned. Max 3 visible. **No** wrapping card.

Pre-7E variant (zero-height stub) lives at
``archive/launcher-7b1/investigation_panel_7b1.py``.
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
    """6-px lavender dot painted at the left of the row. Strong
    when the thread spans ≥ 3 surfaces, muted otherwise."""

    SIZE = 6

    def __init__(self, strong: bool, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self._strong = strong
        self.setFixedSize(self.SIZE + 2, self.SIZE + 2)

    def paintEvent(self, _e) -> None:  # type: ignore[override]
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(QColor(T.ACCENT) if self._strong else QColor(T.INK_4))
        p.drawEllipse(1, 1, self.SIZE, self.SIZE)
        p.end()


class InvestigationCardV3(QWidget):
    """One row of the OTHER WORK list. 36 px tall.

    Emits ``open_thread(thread_id, topic_key, title)`` on click /
    Enter / Space."""

    open_thread = pyqtSignal(str, str, str)

    HEIGHT = 36

    def __init__(
        self,
        thread_id: str,
        topic_key: str,
        title: str,
        *,
        last_seen: str = "",
        strong: bool = False,
        parent: Optional[QWidget] = None,
    ) -> None:
        super().__init__(parent)
        self._tid = thread_id
        self._topic = topic_key
        self._title = title
        self._last_seen = last_seen
        self._hover = False

        self.setFixedHeight(self.HEIGHT)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setAttribute(Qt.WidgetAttribute.WA_Hover, True)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(2, 0, 2, 0)
        layout.setSpacing(10)
        layout.addWidget(_Dot(strong), 0, Qt.AlignmentFlag.AlignVCenter)

        self._title_lbl = QLabel(title)
        f = QFont()
        f.setPointSizeF(10.5)
        self._title_lbl.setFont(f)
        self._title_lbl.setStyleSheet(
            f"color: {T.INK_2}; background: transparent; padding: 0;"
        )
        self._title_lbl.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred
        )
        layout.addWidget(self._title_lbl, 1)

        if last_seen:
            ls = QLabel(last_seen)
            lf = QFont()
            lf.setPointSizeF(9.0)
            ls.setFont(lf)
            ls.setStyleSheet(
                f"color: {T.INK_4}; background: transparent;"
                f"font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;"
                f"letter-spacing: 0.2px;"
            )
            layout.addWidget(ls, 0, Qt.AlignmentFlag.AlignVCenter)

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
    Rows paint directly on the inner card with 1-px hairline
    dividers between."""

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


InvestigationRow = InvestigationList


__all__ = [
    "InvestigationCardV3",
    "InvestigationList",
    "InvestigationRow",
]
