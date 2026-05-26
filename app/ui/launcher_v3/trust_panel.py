"""Phase 6I — TrustPanel.

The footer block of the main column: a single calm row that
restates the boundary at the bottom of every digest scroll.

  ●  Daemon connected     127.0.0.1:4545
  ⌂  Local only           no cloud · no telemetry
  ●  Captured today       248 events

Same vocabulary as the trust strip on the marketing site's
Download section — *Local only · No cloud · No telemetry · Counts
only · Export only* — pared to three lines that fit the column.
"""

from __future__ import annotations

from typing import Optional

from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import QHBoxLayout, QLabel, QVBoxLayout, QWidget

from . import theme as T
from .surfaces import GlassCard, SoftDivider, StatusDot, section_label


def _row(left_dot: QWidget, label: str, detail: str) -> QHBoxLayout:
    layout = QHBoxLayout()
    layout.setSpacing(10)
    layout.addWidget(left_dot)
    lbl = QLabel(label)
    f = QFont()
    f.setPointSizeF(10.5)
    f.setBold(True)
    lbl.setFont(f)
    lbl.setStyleSheet(
        f"color: {T.INK_2}; background: transparent;"
    )
    layout.addWidget(lbl)
    layout.addStretch(1)
    dt = QLabel(detail)
    dt.setStyleSheet(
        f"color: {T.INK_3}; font-size: {T.FS_META}px;"
        f"background: transparent;"
        f"font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;"
    )
    layout.addWidget(dt)
    return layout


class TrustPanel(QWidget):
    """A small panel of three rows the trust footer renders.

    Construct with optional `events_today` + `daemon_connected` to
    drive the right-side detail strings; defaults make the empty
    state honest (no events yet, daemon presumed connected).
    """

    def __init__(
        self,
        *,
        events_today: int = 0,
        daemon_connected: bool = True,
        endpoint: str = "127.0.0.1:4545",
        parent: Optional[QWidget] = None,
    ) -> None:
        super().__init__(parent)

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)
        outer.addWidget(section_label("Trust"))

        card = GlassCard(radius=T.RADIUS_CARD)
        body = QVBoxLayout(card)
        body.setContentsMargins(16, 12, 16, 12)
        body.setSpacing(0)

        body.addLayout(_row(
            StatusDot("ok" if daemon_connected else "warn"),
            "Daemon" if daemon_connected else "Daemon offline",
            endpoint,
        ))
        body.addWidget(SoftDivider(margin_v=6))
        body.addLayout(_row(
            StatusDot("accent"),
            "Local only",
            "no cloud · no telemetry",
        ))
        body.addWidget(SoftDivider(margin_v=6))
        body.addLayout(_row(
            StatusDot("mute" if events_today == 0 else "ok"),
            "Captured today",
            f"{events_today:,} events" if events_today else "—",
        ))

        outer.addWidget(card)


__all__ = ["TrustPanel"]
