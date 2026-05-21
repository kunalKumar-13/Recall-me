"""Capture the recovery card in isolation — Phase 4L.

The recovery card is the product's milestone surface ("Wait — it
remembered that?"), so it gets its own captures: the resting state
and the keyboard-focused state, side by side, to verify the focus
ring and the three-zone anatomy.

    python infra/scripts/capture/capture_recovery.py
"""

from __future__ import annotations

from PyQt6.QtWidgets import QVBoxLayout

from _render import Panel, app, render
from app.ui.cards import RecoveryCard


def _card() -> RecoveryCard:
    return RecoveryCard(
        "rc_demo",
        "WebSocket retry debugging",
        "2 tabs · 2 files · reopened after a 2-day gap",
        "2d ago",
        high_trust=True,
        n_targets=5,
    )


def _panel(focused: bool) -> Panel:
    panel = Panel()
    panel.setFixedWidth(440)
    col = QVBoxLayout(panel)
    col.setContentsMargins(8, 10, 8, 10)
    card = _card()
    col.addWidget(card)
    if focused:
        app().processEvents()
        card.setFocus()
        app().processEvents()
    return panel


def main() -> None:
    for name, focused in (
        ("recovery-card", False),
        ("recovery-card-focused", True),
    ):
        path = render(_panel(focused), name)
        print(f"  wrote {path.relative_to(path.parents[2])}")


if __name__ == "__main__":
    main()
