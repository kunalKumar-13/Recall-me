"""Phase 6O — Launcher Reset.

A bare-text *OTHER WORK* row. No pill chrome, no accent dot,
no surface chips, no overflow chip. Just up to **three titles**
in a single row, equal width.

The pre-reset module shipped status dots, soft-rounded pill
shells, a `sort_for_digest` priority sorter (unfinished /
returned / recent / passive), and a `+N more` dashed-border
overflow chip. The reset directive deletes all of it.

The pre-reset module lives at
``archive/launcher-overbuild/investigation_panel.py``.
"""

from __future__ import annotations

from typing import List, Optional

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QSizePolicy,
    QWidget,
)

from . import theme as T


class InvestigationCardV3(QLabel):
    """A single investigation title. Bare text — no border, no
    background, no dot, no count chip.

    Emits ``open_thread(thread_id, topic_key, title)`` on click
    or `Enter`/`Space`.
    """

    open_thread = pyqtSignal(str, str, str)

    def __init__(
        self,
        thread_id: str,
        topic_key: str,
        title: str,
        parent: Optional[QWidget] = None,
    ) -> None:
        super().__init__(title, parent)
        self._tid = thread_id
        self._topic = topic_key
        self._title = title
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        f = QFont()
        f.setPointSizeF(T.FS_BODY)              # 13
        self.setFont(f)
        self.setStyleSheet(self._stylesheet(hover=False))

    @staticmethod
    def _stylesheet(*, hover: bool) -> str:
        # Hover-only motion (the directive's allowed list).
        color = T.INK if hover else T.INK_2
        return (
            f"QLabel {{"
            f"  color: {color};"
            f"  background: transparent;"
            f"  padding: 0;"
            f"}}"
        )

    def enterEvent(self, _e) -> None:  # type: ignore[override]
        self.setStyleSheet(self._stylesheet(hover=True))

    def leaveEvent(self, _e) -> None:  # type: ignore[override]
        self.setStyleSheet(self._stylesheet(hover=False))

    def mouseReleaseEvent(self, e) -> None:  # type: ignore[override]
        if e.button() == Qt.MouseButton.LeftButton:
            self.open_thread.emit(self._tid, self._topic, self._title)

    def keyPressEvent(self, e) -> None:  # type: ignore[override]
        if e.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter, Qt.Key.Key_Space):
            self.open_thread.emit(self._tid, self._topic, self._title)
            return
        super().keyPressEvent(e)


class InvestigationRow(QWidget):
    """A single equal-width row of up to **three** investigation
    titles. Anything past the third is dropped — no overflow chip,
    no scroll, no animation. The directive's *max 3 · single row ·
    equal width · no overflow animations* rule lands here."""

    activated = pyqtSignal(str, str, str)
    MAX_VISIBLE = 3

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(T.CARD_GAP)
        self._layout = layout
        self._titles: List[InvestigationCardV3] = []

    def populate(self, items: List[InvestigationCardV3]) -> None:
        # Drain prior widgets (titles + spacers).
        while self._layout.count():
            item = self._layout.takeAt(0)
            w = item.widget()
            if w is not None:
                w.setParent(None)
        self._titles.clear()
        for t in items[: self.MAX_VISIBLE]:
            t.open_thread.connect(self.activated.emit)
            self._titles.append(t)
            self._layout.addWidget(t, 1)
        # Pad with spacers if fewer than MAX_VISIBLE so the
        # remaining titles still distribute equally.
        for _ in range(self.MAX_VISIBLE - len(self._titles)):
            spacer = QWidget()
            spacer.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
            self._layout.addWidget(spacer, 1)


__all__ = [
    "InvestigationCardV3",
    "InvestigationRow",
]
