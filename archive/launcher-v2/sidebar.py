"""Phase 6I — Sidebar.

The left column of the v3 shell. Three stacked groups:

  1. Recall mark + wordmark  (matches the marketing site lockup)
  2. Search input            (rounded, hairline, inline kbd hint)
  3. Section nav             (Continue · Active · Returns · Trust)

The directive's *Linear × Arc × Raycast* visual rules apply here
most strongly: a quiet column, no glow, single accent dot next to
the active row, calm hover.

This module is UI-only. Wiring the search input to the search
engine is not part of Phase 6I; the input emits ``query_changed``
on every keystroke and the live launcher decides what to do with
the signal.
"""

from __future__ import annotations

from typing import Optional

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from . import theme as T
from .surfaces import SoftDivider, StatusDot, section_label


def _wordmark() -> QWidget:
    w = QWidget()
    row = QHBoxLayout(w)
    row.setContentsMargins(0, 0, 0, 0)
    row.setSpacing(10)
    mark = QLabel()
    mark.setFixedSize(12, 12)
    mark.setStyleSheet(
        f"QLabel {{ background: {T.ACCENT}; border-radius: 3px; }}"
    )
    word = QLabel("Recall")
    f = QFont()
    f.setPointSizeF(13)
    f.setBold(True)
    word.setFont(f)
    word.setStyleSheet(
        f"color: {T.INK}; background: transparent; letter-spacing: -0.2px;"
    )
    sub = QLabel("launcher")
    sub.setStyleSheet(
        f"color: {T.INK_3}; background: transparent;"
        f"font-size: 10.5px; letter-spacing: 0.6px; text-transform: uppercase;"
    )
    row.addWidget(mark)
    row.addWidget(word)
    row.addWidget(sub)
    row.addStretch(1)
    return w


class _NavRow(QWidget):
    """A single navigation row. Active row gets the accent dot."""

    def __init__(
        self,
        label: str,
        *,
        active: bool = False,
        kbd: Optional[str] = None,
        parent: Optional[QWidget] = None,
    ) -> None:
        super().__init__(parent)
        self.setFixedHeight(30)
        row = QHBoxLayout(self)
        row.setContentsMargins(8, 0, 8, 0)
        row.setSpacing(10)
        row.addWidget(StatusDot("accent" if active else "mute"))

        text = QLabel(label)
        f = QFont()
        f.setPointSizeF(10.5)
        f.setBold(active)
        text.setFont(f)
        text.setStyleSheet(
            f"color: {T.INK if active else T.INK_2};"
            f"background: transparent;"
        )
        row.addWidget(text, 1)

        if kbd:
            chip = QLabel(kbd)
            chip.setAlignment(Qt.AlignmentFlag.AlignCenter)
            chip.setFixedSize(20, 18)
            chip.setStyleSheet(
                "QLabel {"
                f" background: rgba(255,255,255,160);"
                f" color: {T.INK_3};"
                f" border: 1px solid {T.HAIRLINE};"
                f" border-radius: 5px;"
                f" font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;"
                f" font-size: 10px;"
                f" font-weight: 600;"
                "}"
            )
            row.addWidget(chip)


class Sidebar(QWidget):
    """Left rail of the shell."""

    query_changed = pyqtSignal(str)

    def __init__(
        self,
        *,
        active_section: str = "continue",
        parent: Optional[QWidget] = None,
    ) -> None:
        super().__init__(parent)
        self.setFixedWidth(220)
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Expanding)

        outer = QVBoxLayout(self)
        outer.setContentsMargins(18, 22, 14, 18)
        outer.setSpacing(0)

        outer.addWidget(_wordmark())
        outer.addWidget(SoftDivider(margin_v=12))

        # ── search input ──
        search = QLineEdit()
        search.setPlaceholderText("Search the work you remember…")
        search.setFixedHeight(34)
        search.setStyleSheet(
            f"QLineEdit {{"
            f"  background: {T.BG_RAISED};"
            f"  color: {T.INK};"
            f"  border: 1px solid {T.HAIRLINE};"
            f"  border-radius: 10px;"
            f"  padding: 0 12px;"
            f"  font-size: 12px;"
            f"}}"
            f"QLineEdit:focus {{ border-color: {T.ACCENT_LINE}; }}"
        )
        search.textChanged.connect(self.query_changed.emit)
        outer.addWidget(search)
        outer.addWidget(SoftDivider(margin_v=10))

        outer.addWidget(section_label("Sections"))
        for label, kbd, active in (
            ("Continue", "1", active_section == "continue"),
            ("Active investigations", "2", active_section == "active"),
            ("Recent returns", "3", active_section == "returns"),
            ("Trust", "4", active_section == "trust"),
        ):
            outer.addWidget(_NavRow(label, active=active, kbd=kbd))

        outer.addStretch(1)
        outer.addWidget(SoftDivider(margin_v=8))
        foot = QLabel("⌘K   /   /focus")
        foot.setStyleSheet(
            f"color: {T.INK_4}; font-size: 10.5px;"
            f"font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;"
            f"background: transparent;"
        )
        outer.addWidget(foot)

    def paintEvent(self, _e) -> None:  # type: ignore[override]
        from PyQt6.QtGui import QColor, QPainter, QPainterPath
        from PyQt6.QtCore import QRectF
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        path = QPainterPath()
        path.addRoundedRect(QRectF(self.rect()), T.RADIUS_PANEL, T.RADIUS_PANEL)
        fill = QColor(255, 255, 255, T.SURFACE_ALPHA_HIGH)
        p.fillPath(path, fill)
        p.end()


__all__ = ["Sidebar"]
