"""Capture the Phase 6L minimal launcher screens.

Four PNGs land in ``assets/screenshots/launcher-minimal/``:

  - ``hero``           single-column with Continue hero + horizontal
                       investigations strip + recent returns
  - ``empty``          first-run empty surface (Show example /
                       Start normally + trust line)
  - ``investigations`` populated digest with three investigation
                       pills + recent returns row — Continue hero
                       elided so the strip carries the frame
  - ``resume``         the same hero card focused (accent ring),
                       paired with a single investigation pill;
                       the user has hit ``1`` and is about to
                       press Enter

No three-column shell, no context column, no sidebar nav — the
directive's *single floating surface* rule is the binding
constraint.

    python infra/scripts/capture/capture_launcher_minimal.py
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
        candidate_id="rc_minimal",
        title="WebSocket retry debugging",
        evidence="2 tabs · 3 files · reopened after a 2-day gap",
        time_label="just now",
        confidence="high",
        n_targets=5,
    )
    if focused:
        card._focused = True  # noqa: SLF001
    return card


def _investigations() -> List[v3.InvestigationCardV3]:
    return [
        v3.InvestigationCardV3(
            "t-ws", "ws", "WebSocket retries",
            timeline=["09:20"], surface_types=[], last_touch="2h",
            strength=4,
        ),
        v3.InvestigationCardV3(
            "t-pp", "pp", "Proposal draft",
            timeline=["yesterday"], surface_types=[], last_touch="1d",
            strength=3,
        ),
        v3.InvestigationCardV3(
            "t-rl", "rl", "RLHF research",
            timeline=["1w"], surface_types=[], last_touch="3d",
            strength=2,
        ),
        v3.InvestigationCardV3(
            "t-hl", "hl", "Healthcare pitch",
            timeline=["Mon"], surface_types=[], last_touch="3d",
            strength=2,
        ),
    ]


def _returns() -> List[tuple[str, str]]:
    return [
        ("yesterday", "picked up WebSocket retries"),
        ("Tuesday", "returned to Proposal draft"),
        ("Monday", "RLHF research"),
    ]


# ── window builders ───────────────────────────────────────────────


def _hero_window() -> v3.MinimalWindow:
    digest = v3.MinimalDigest()
    digest.populate(
        hero=_hero(),
        investigations=_investigations(),
        returns=_returns(),
    )
    return v3.MinimalWindow(digest)


def _empty_window() -> v3.MinimalWindow:
    return v3.MinimalWindow(v3.MinimalEmpty())


def _investigations_window() -> v3.MinimalWindow:
    """Populated digest emphasising the strip — a smaller, low-
    confidence hero so the eye lands on the active investigations
    row first."""
    quiet_hero = v3.RecoveryCardV3(
        candidate_id="rc_quiet",
        title="Proposal draft revisions",
        evidence="2 files · reopened after a 5-day gap",
        time_label="just now",
        confidence="medium",
        n_targets=3,
    )
    digest = v3.MinimalDigest()
    digest.populate(
        hero=quiet_hero,
        investigations=_investigations(),
        returns=_returns(),
    )
    return v3.MinimalWindow(digest)


def _resume_window() -> v3.MinimalWindow:
    """Focus state — the user pressed ``1`` and the hero card is
    selected. Single investigation pill kept so the surface stays
    *about the resume*."""
    digest = v3.MinimalDigest()
    digest.populate(
        hero=_hero(focused=True),
        investigations=[_investigations()[0]],
        returns=[("today", "started WebSocket retries")],
    )
    return v3.MinimalWindow(digest)


def main() -> None:
    captures = (
        ("hero", _hero_window()),
        ("empty", _empty_window()),
        ("investigations", _investigations_window()),
        ("resume", _resume_window()),
    )
    for name, widget in captures:
        widget.resize(920, 720)
        path = render(widget, name, subdir="launcher-minimal")
        print(f"  wrote {path.relative_to(path.parents[3])}")


if __name__ == "__main__":
    main()
