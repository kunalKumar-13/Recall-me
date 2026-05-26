"""Phase 6I — Shell.

The three-column composition the directive names:

    ┌────────────┬──────────────────────────────┬──────────────┐
    │  Sidebar   │  DigestColumn / SearchPanel   │  ContextCol  │
    │   220 px   │   flex (clamped 520-720)      │    240 px    │
    └────────────┴──────────────────────────────┴──────────────┘

The shell composes its children but does not own data. Callers pass
in the populated DigestColumn (or EmptyDigest) and a small context
widget — the right column is small enough that we build it
in-place here from a few stats the caller hands in.
"""

from __future__ import annotations

from typing import Optional

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QColor, QPainter, QPainterPath
from PyQt6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from . import theme as T
from .sidebar import Sidebar
from .surfaces import GlassCard, SoftDivider, StatusDot, section_label


def _stat_row(label: str, value: str, dot: str = "mute") -> QHBoxLayout:
    row = QHBoxLayout()
    row.setSpacing(10)
    row.addWidget(StatusDot(dot))
    lbl = QLabel(label)
    f = QFont()
    f.setPointSizeF(10.5)
    f.setBold(True)
    lbl.setFont(f)
    lbl.setStyleSheet(f"color: {T.INK_2}; background: transparent;")
    row.addWidget(lbl)
    row.addStretch(1)
    v = QLabel(value)
    v.setStyleSheet(
        f"color: {T.INK_3}; font-size: {T.FS_META}px;"
        f"font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;"
        f"background: transparent;"
    )
    row.addWidget(v)
    return row


class ContextColumn(QWidget):
    """Right column. Carries the small *Today / Doctor / Version*
    block the directive names. Stats are passed in by the caller —
    the widget does not read from the engine."""

    def __init__(
        self,
        *,
        events_today: int = 0,
        doctor_state: str = "GREEN",
        extension_state: str = "connected",
        protocol_state: str = "registered",
        version: str = "0.2.0",
        parent: Optional[QWidget] = None,
    ) -> None:
        super().__init__(parent)
        self.setFixedWidth(240)
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Expanding)

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(T.SECTION_GAP)

        # ── TODAY block ──
        outer.addWidget(section_label("Today"))
        today = GlassCard(radius=T.RADIUS_CARD)
        body = QVBoxLayout(today)
        body.setContentsMargins(16, 12, 16, 12)
        body.setSpacing(0)
        body.addLayout(_stat_row("Events", f"{events_today:,}", "ok" if events_today else "mute"))
        body.addWidget(SoftDivider(margin_v=6))
        body.addLayout(_stat_row("Extension", extension_state,
                                 "ok" if extension_state == "connected" else "warn"))
        body.addWidget(SoftDivider(margin_v=6))
        body.addLayout(_stat_row("Protocol", protocol_state,
                                 "ok" if protocol_state == "registered" else "warn"))
        outer.addWidget(today)

        # ── DOCTOR block ──
        outer.addWidget(section_label("Doctor"))
        doc = GlassCard(radius=T.RADIUS_CARD)
        b2 = QVBoxLayout(doc)
        b2.setContentsMargins(16, 12, 16, 12)
        b2.setSpacing(8)
        dot = StatusDot({
            "GREEN": "ok", "YELLOW": "warn", "RED": "danger",
        }.get(doctor_state, "mute"))
        row = QHBoxLayout()
        row.setSpacing(10)
        row.addWidget(dot)
        state_lbl = QLabel(doctor_state)
        f = QFont()
        f.setPointSizeF(11)
        f.setBold(True)
        state_lbl.setFont(f)
        state_lbl.setStyleSheet(
            f"color: {T.INK}; background: transparent;"
        )
        row.addWidget(state_lbl)
        row.addStretch(1)
        hint = QLabel("recall doctor")
        hint.setStyleSheet(
            f"color: {T.INK_3}; font-size: 10.5px;"
            f"font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;"
            f"background: transparent;"
        )
        row.addWidget(hint)
        b2.addLayout(row)
        outer.addWidget(doc)

        # ── VERSION ──
        outer.addStretch(1)
        v = QLabel(f"v{version}")
        v.setStyleSheet(
            f"color: {T.INK_4}; font-size: 10px;"
            f"font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;"
            f"background: transparent;"
        )
        outer.addWidget(v, alignment=Qt.AlignmentFlag.AlignRight)

    def paintEvent(self, _e) -> None:  # type: ignore[override]
        from PyQt6.QtCore import QRectF
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        path = QPainterPath()
        path.addRoundedRect(QRectF(self.rect()), T.RADIUS_PANEL, T.RADIUS_PANEL)
        fill = QColor(255, 255, 255, T.SURFACE_ALPHA_HIGH)
        p.fillPath(path, fill)
        p.end()


class Shell(QWidget):
    """Three-column composition. Pass the centre widget (DigestColumn,
    EmptyDigest, or SearchPanel) and the shell wraps it with the
    sidebar + context column."""

    def __init__(
        self,
        center: QWidget,
        *,
        sidebar: Optional[Sidebar] = None,
        context: Optional[ContextColumn] = None,
        parent: Optional[QWidget] = None,
    ) -> None:
        super().__init__(parent)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(T.GUTTER, T.GUTTER, T.GUTTER, T.GUTTER)
        layout.setSpacing(T.GUTTER)

        layout.addWidget(sidebar or Sidebar())
        # Centre column: clamp the max width so it floats inside the
        # window rather than stretching edge-to-edge.
        center_wrap = QWidget()
        center_wrap.setMinimumWidth(420)
        center_wrap.setMaximumWidth(720)
        cl = QVBoxLayout(center_wrap)
        cl.setContentsMargins(0, 0, 0, 0)
        cl.setSpacing(0)
        cl.addWidget(center)
        layout.addWidget(center_wrap, 1)
        layout.addWidget(context or ContextColumn())


__all__ = ["Shell", "ContextColumn"]
