"""Capture the Phase 6M.1 refined launcher screens.

Five PNGs land in ``assets/screenshots/launcher-refined/``:

  - ``hero``           single column · Continue hero with bottom-
                       aligned Resume CTA · 4 equal-width investigation
                       pills · trust line
  - ``empty``          vertically-centred icon + headline + sub +
                       two buttons (no card wrapper — the Phase 6L
                       *GlassCard* wrap is gone)
  - ``investigations`` populated digest with 6 threads → 4 pills
                       + a ``+2 more`` overflow chip
  - ``resume``         single hero centred + a focus-glow ring;
                       the user has hit ``1`` and is about to
                       press Enter
  - ``focused``        the digest with the hero focused + the
                       first investigation pill highlighted —
                       shows the keyboard nav at rest

No three-column shell, no context column, no sidebar nav, no
translucent paint — the directive's *refinement* rules are the
binding constraint.

    python infra/scripts/capture/capture_launcher_refined.py
"""

from __future__ import annotations

from typing import List

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QHBoxLayout, QVBoxLayout, QWidget

from _render import Panel, render
from app.ui import launcher_v3 as v3


# ── fixtures ──────────────────────────────────────────────────────


def _hero(*, focused: bool = False) -> v3.RecoveryCardV3:
    card = v3.RecoveryCardV3(
        candidate_id="rc_refined",
        title="WebSocket retry debugging",
        evidence="2 tabs · 3 files · reopened after a 2-day gap",
        time_label="just now",
        confidence="high",
        n_targets=5,
    )
    if focused:
        card._focused = True  # noqa: SLF001
    return card


def _investigations(n: int = 4) -> List[v3.InvestigationCardV3]:
    titles = [
        ("t-ws", "ws", "WebSocket retries"),
        ("t-pp", "pp", "Proposal draft"),
        ("t-rl", "rl", "RLHF research"),
        ("t-hl", "hl", "Healthcare pitch"),
        ("t-ds", "ds", "Daily-loop counters"),
        ("t-st", "st", "Stack Overflow follow-ups"),
    ]
    return [
        v3.InvestigationCardV3(
            tid, topic, title,
            timeline=["—"], surface_types=[], last_touch="—",
            strength=2,
        )
        for tid, topic, title in titles[:n]
    ]


def _hero_window() -> v3.MinimalWindow:
    digest = v3.MinimalDigest()
    digest.populate(
        hero=_hero(),
        investigations=_investigations(4),
        returns=[],
    )
    return v3.MinimalWindow(digest)


def _empty_window() -> v3.MinimalWindow:
    return v3.MinimalWindow(v3.MinimalEmpty())


def _investigations_window() -> v3.MinimalWindow:
    """Six threads → strip shows 4 pills + a `+2 more` overflow chip."""
    digest = v3.MinimalDigest()
    digest.populate(
        hero=_hero(),
        investigations=_investigations(6),
        returns=[],
    )
    return v3.MinimalWindow(digest)


def _resume_window() -> v3.MinimalWindow:
    """Focus state — the user pressed ``1`` and the hero card is
    selected (accent ring). One investigation pill so the surface
    stays *about the resume*."""
    digest = v3.MinimalDigest()
    digest.populate(
        hero=_hero(focused=True),
        investigations=[_investigations(1)[0]],
        returns=[],
    )
    return v3.MinimalWindow(digest)


def _focused_window() -> v3.MinimalWindow:
    """Hero focused + a fully populated pill row. Documents the
    keyboard-nav at rest."""
    digest = v3.MinimalDigest()
    digest.populate(
        hero=_hero(focused=True),
        investigations=_investigations(4),
        returns=[],
    )
    return v3.MinimalWindow(digest)


def main() -> None:
    captures = (
        ("hero", _hero_window()),
        ("empty", _empty_window()),
        ("investigations", _investigations_window()),
        ("resume", _resume_window()),
        ("focused", _focused_window()),
    )
    for name, widget in captures:
        widget.resize(*v3.MinimalWindow.DEFAULT_SIZE)
        path = render(widget, name, subdir="launcher-refined")
        print(f"  wrote {path.relative_to(path.parents[3])}")


if __name__ == "__main__":
    main()
