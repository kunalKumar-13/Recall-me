"""Capture the launcher idle digest.

Renders the Phase 4K card set (recovery, investigations,
resurfacing, trust) as the launcher's idle digest, plus the
skeleton-loading and empty/offline/first-week states, to
deterministic PNGs.

Phase 6B writes into `assets/screenshots/launcher-v2/` (warm-white
identity captures) so the historical dark-theme PNGs at
`assets/screenshots/launcher-*.png` stay as the *before* set
referenced by older docs. The new captures are the *after* the
launcher theme swap.

    python infra/scripts/capture/capture_launcher.py
"""

from __future__ import annotations

from PyQt6.QtWidgets import QLabel, QVBoxLayout, QWidget

from _render import Panel, render
from app.ui.cards import (
    EmptyCard,
    InvestigationCard,
    RecoveryCard,
    ResurfaceCard,
    SkeletonCard,
    TrustCard,
)
from app.ui.styles import TEXT_DIMMER

PANEL_W = 460


def _section(text: str) -> QLabel:
    lbl = QLabel(text.upper())
    lbl.setFixedHeight(30)
    f = lbl.font()
    f.setPointSizeF(7.4)
    f.setBold(True)
    lbl.setFont(f)
    lbl.setStyleSheet(
        f"color:{TEXT_DIMMER};letter-spacing:1.3px;"
        "background:transparent;padding:12px 16px 4px 16px;"
    )
    return lbl


def _panel(*children: QWidget, top: int = 10, bottom: int = 14) -> Panel:
    """A launcher-coloured panel sized to its content by `render()`."""
    panel = Panel()
    panel.setFixedWidth(PANEL_W)
    col = QVBoxLayout(panel)
    col.setContentsMargins(8, top, 8, bottom)
    col.setSpacing(0)
    for c in children:
        col.addWidget(c)
    return panel


def _digest() -> QWidget:
    """The normal idle digest — the milestone surface."""
    return _panel(
        _section("Continue where you left off"),
        RecoveryCard(
            "rc_demo", "WebSocket retry debugging",
            "2 tabs · 2 files · reopened after a 2-day gap",
            "2d ago", confidence="high", n_targets=5,
        ),
        _section("Active investigations"),
        InvestigationCard(
            "t1", "t1", "RLHF reward shaping",
            "Started 1w ago · 4 sessions · 18 events", "5h ago",
        ),
        InvestigationCard(
            "t2", "t2", "Healthcare startup research",
            "Started 2w ago · 6 sessions · 31 events", "3d ago",
        ),
        _section("On your radar"),
        ResurfaceCard(
            "Postgres index tuning", "noticed across 2 days",
            "yesterday", "url", "https://example.com",
        ),
        _section("Trust"),
        TrustCard(connected=True, events_today=128),
    )


def _loading() -> QWidget:
    return _panel(
        _section("Continue where you left off"),
        SkeletonCard(),
        SkeletonCard(),
        SkeletonCard(),
    )


def _state(kind: str) -> QWidget:
    card = {
        "empty": EmptyCard.empty,
        "offline": EmptyCard.offline,
        "first_week": EmptyCard.first_week,
    }[kind]()
    return _panel(card, top=14)


def main() -> None:
    for name, widget in (
        ("launcher-digest", _digest()),
        ("launcher-loading", _loading()),
        ("launcher-empty", _state("empty")),
        ("launcher-offline", _state("offline")),
        ("launcher-first-week", _state("first_week")),
    ):
        # Phase 6B - write to assets/screenshots/launcher-v2/ so the
        # new warm-white captures sit alongside the historical dark
        # ones rather than overwriting them. The directive named
        # this directory explicitly.
        path = render(widget, name, subdir="launcher-v2")
        print(f"  wrote {path.relative_to(path.parents[3])}")


if __name__ == "__main__":
    main()
