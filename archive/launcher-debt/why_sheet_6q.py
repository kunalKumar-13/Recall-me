"""Phase 6Q — *Why this?* overlay.

A tiny sheet the user opens by clicking the *Why this?* link on
the hero card. Lists the engine's signals verbatim — no prose, no
AI text, no scoring numbers.

    +----------------------------+
    |  SHOWN BECAUSE             |
    |                            |
    |    - unfinished work       |
    |    - returned after 2 days |
    |    - 4 targets involved    |
    |                            |
    |              [ Close ]     |
    +----------------------------+

The lines come from `recovery.explain_signals(candidate)`, which
is deterministic — same candidate in, same lines out.
"""

from __future__ import annotations

from typing import List, Optional

from PyQt6.QtCore import QRectF, Qt, pyqtSignal
from PyQt6.QtGui import QColor, QFont, QPainter, QPainterPath, QPen
from PyQt6.QtWidgets import (
    QGraphicsDropShadowEffect,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from . import theme as T


class WhyThisSheet(QWidget):
    """The overlay. Host calls `open(signals)` to populate + show;
    the user closes via the Close button or Esc.

    Emits `closed()` when dismissed."""

    closed = pyqtSignal()

    WIDTH = 320

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        self.setFixedWidth(self.WIDTH)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, False)

        eff = QGraphicsDropShadowEffect(self)
        eff.setBlurRadius(T.SHADOW_CARD_RADIUS)
        eff.setOffset(0, T.SHADOW_CARD_OFFSET)
        eff.setColor(QColor(0, 0, 0, T.SHADOW_CARD_ALPHA))
        self.setGraphicsEffect(eff)

        outer = QVBoxLayout(self)
        outer.setContentsMargins(20, 16, 20, 14)
        outer.setSpacing(8)

        eyebrow = QLabel("SHOWN BECAUSE")
        ef = QFont()
        ef.setPointSizeF(8.0)
        ef.setBold(True)
        eyebrow.setFont(ef)
        eyebrow.setStyleSheet(
            f"color: {T.INK_3}; background: transparent;"
            f"letter-spacing: 1.4px;"
        )
        outer.addWidget(eyebrow)

        self._rows_holder = QVBoxLayout()
        self._rows_holder.setContentsMargins(0, 0, 0, 0)
        self._rows_holder.setSpacing(4)
        outer.addLayout(self._rows_holder)

        outer.addSpacing(6)

        buttons = QHBoxLayout()
        buttons.setSpacing(0)
        buttons.addStretch(1)
        close_btn = QPushButton("Close")
        close_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        close_btn.setFixedHeight(30)
        close_btn.setStyleSheet(
            f"QPushButton {{"
            f"  background: transparent;"
            f"  color: {T.INK_2};"
            f"  border: 1px solid {T.BORDER_RAISED};"
            f"  border-radius: 9px;"
            f"  padding: 0 14px;"
            f"  font-size: {T.FS_BODY}px;"
            f"  font-weight: 500;"
            f"}}"
            f"QPushButton:hover {{ background: #F3F0EC; color: {T.INK}; }}"
        )
        close_btn.clicked.connect(self._on_close)
        buttons.addWidget(close_btn)
        outer.addLayout(buttons)

        self.hide()

    # ── public ──────────────────────────────────────────────────────

    def open(self, signals: List[str]) -> None:
        self._populate(signals)
        self.show()
        self.raise_()
        self.setFocus(Qt.FocusReason.PopupFocusReason)

    def close_sheet(self) -> None:
        """Hide without firing `closed` — used by the host when
        the launcher itself is dismissed."""
        self.hide()

    # ── populate ────────────────────────────────────────────────────

    def _populate(self, signals: List[str]) -> None:
        while self._rows_holder.count():
            it = self._rows_holder.takeAt(0)
            w = it.widget()
            if w is not None:
                w.setParent(None)
        if not signals:
            empty = QLabel("no specific signal")
            empty.setStyleSheet(
                f"color: {T.INK_3}; background: transparent;"
                f"font-size: {T.FS_BODY}px;"
            )
            self._rows_holder.addWidget(empty)
            return
        for line in signals:
            row = QLabel(f"-  {line}")
            row.setStyleSheet(
                f"color: {T.INK_2}; background: transparent;"
                f"font-size: {T.FS_BODY}px;"
                f"padding-left: 4px;"
            )
            self._rows_holder.addWidget(row)

    # ── paint ───────────────────────────────────────────────────────

    def paintEvent(self, _e) -> None:  # type: ignore[override]
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        path = QPainterPath()
        path.addRoundedRect(QRectF(self.rect()), 14, 14)
        p.fillPath(path, QColor(T.BG_RAISED))
        pen = QPen(QColor(T.BORDER_RAISED))
        pen.setWidthF(1.0)
        p.setPen(pen)
        p.drawPath(path)
        p.end()

    # ── interaction ─────────────────────────────────────────────────

    def keyPressEvent(self, e) -> None:  # type: ignore[override]
        if e.key() == Qt.Key.Key_Escape:
            self._on_close()
            return
        super().keyPressEvent(e)

    def _on_close(self) -> None:
        self.hide()
        self.closed.emit()


__all__ = ["WhyThisSheet"]
