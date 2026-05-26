"""Capture the Phase 6M.2 compact launcher screens.

Four PNGs land in ``assets/screenshots/launcher-compact/``:

  - ``compact``         single column · 720 × 520 window · the
                        directive's *Raycast / Arc utility* shape
  - ``hero``            hero card alone (the focal point)
  - ``investigations``  4 threads → 3 pills + a ``+1`` overflow chip
  - ``empty``           vertically-centred icon + headline + sub +
                        two buttons

Phase 6M.2 recovery — the previous 6M.1 launcher had regressed to
dashboard-shaped generosity (820 × 640 window, 760-px column,
~120-px hero card). The directive's exact reset:

  - window 720 × 520
  - search-bar capped 640 px wide and centred
  - hero 92 px, 2×2 grid (title / confidence / chips / Resume)
  - 3 investigation pills max + `+N` overflow
  - quiet 2-row returns strip

    python infra/scripts/capture/capture_launcher_compact.py
"""

from __future__ import annotations

from typing import List

from _render import render
from app.ui import launcher_v3 as v3


def _hero(*, focused: bool = False) -> v3.RecoveryCardV3:
    card = v3.RecoveryCardV3(
        candidate_id="rc_compact",
        title="WebSocket retry debugging",
        evidence="2 tabs · 3 files · reopened after a 2-day gap",
        time_label="just now",
        confidence="high",
        n_targets=5,
    )
    if focused:
        card._focused = True  # noqa: SLF001
    return card


def _investigations(n: int = 3) -> List[v3.InvestigationCardV3]:
    titles = [
        ("t-ws", "ws", "WebSocket retries"),
        ("t-pp", "pp", "Proposal draft"),
        ("t-rl", "rl", "RLHF research"),
        ("t-hl", "hl", "Healthcare pitch"),
    ]
    return [
        v3.InvestigationCardV3(
            tid, topic, title,
            timeline=["—"], surface_types=[], last_touch="—",
            strength=2,
        )
        for tid, topic, title in titles[:n]
    ]


def _returns() -> List[tuple[str, str]]:
    return [
        ("yesterday", "picked up WebSocket retries"),
        ("Tuesday", "returned to Proposal draft"),
    ]


def _compact_window() -> v3.MinimalWindow:
    digest = v3.MinimalDigest()
    digest.populate(
        hero=_hero(),
        investigations=_investigations(3),
        returns=_returns(),
    )
    return v3.MinimalWindow(digest)


def _hero_window() -> v3.MinimalWindow:
    """Hero focused inside an otherwise quiet shell — one investigation
    pill so the hero carries the read."""
    digest = v3.MinimalDigest()
    digest.populate(
        hero=_hero(focused=True),
        investigations=[_investigations(1)[0]],
        returns=[],
    )
    return v3.MinimalWindow(digest)


def _investigations_window() -> v3.MinimalWindow:
    """4 threads → strip shows 3 pills + a `+1` overflow chip."""
    digest = v3.MinimalDigest()
    digest.populate(
        hero=_hero(),
        investigations=_investigations(4),
        returns=[],
    )
    return v3.MinimalWindow(digest)


def _empty_window() -> v3.MinimalWindow:
    return v3.MinimalWindow(v3.MinimalEmpty())


def main() -> None:
    captures = (
        ("compact", _compact_window()),
        ("hero", _hero_window()),
        ("investigations", _investigations_window()),
        ("empty", _empty_window()),
    )
    for name, widget in captures:
        widget.resize(*v3.MinimalWindow.DEFAULT_SIZE)
        path = render(widget, name, subdir="launcher-compact")
        print(f"  wrote {path.relative_to(path.parents[3])}")


if __name__ == "__main__":
    main()
