"""Capture the Phase 6N recovery-precision screens.

Five PNGs land in ``assets/screenshots/launcher-recovery/``:

  - ``high.png``    HIGH-signal hero — accent fill, *Resume* pill,
                    *Recall thinks this was interrupted work* line
  - ``medium.png``  MED-signal hero — lighter fill, *Continue*
                    pill, *Seen again after return* line
  - ``low.png``     LOW-signal hero — plain fill, ghost *Review*
                    pill, *Weak signal — review first* line
  - ``empty.png``   empty surface with the preview card landed
                    between the sub-headline and the buttons
  - ``resume.png``  HIGH hero focused (the user has hit ``1``)

The captures use the same widgets the live launcher composes —
including the sort helper, the chip cap, and the confidence
sentence row. Deterministic offscreen Qt, no engine call.

    python infra/scripts/capture/capture_launcher_recovery.py
"""

from __future__ import annotations

from typing import List

from _render import render
from app.ui import launcher_v3 as v3


def _hero(*, signal: str, focused: bool = False) -> v3.RecoveryCardV3:
    titles = {
        "high":   "WebSocket retry debugging",
        "medium": "Healthcare pitch draft",
        "low":    "Casual research session",
    }
    evidences = {
        "high":   "2 tabs · 3 files · reopened after a 2-day gap",
        "medium": "2 files · reopened after a 5-day gap",
        "low":    "1 tab",
    }
    confidences = {"high": "high", "medium": "medium", "low": "low"}
    n_targets = {"high": 5, "medium": 3, "low": 1}
    card = v3.RecoveryCardV3(
        candidate_id=f"rc_{signal}",
        title=titles[signal],
        evidence=evidences[signal],
        time_label="just now",
        confidence=confidences[signal],
        signal=signal,
        n_targets=n_targets[signal],
    )
    if focused:
        card._focused = True  # noqa: SLF001
    return card


def _investigations() -> List[v3.InvestigationCardV3]:
    return v3.sort_for_digest([
        v3.InvestigationCardV3(
            "t-rl", "rl", "RLHF research",
            timeline=["-"], surface_types=[], last_touch="today",
            strength=2,
        ),
        v3.InvestigationCardV3(
            "t-pp", "pp", "Proposal draft",
            timeline=["-"], surface_types=[], last_touch="returned 2d",
            strength=2,
        ),
        v3.InvestigationCardV3(
            "t-ws", "ws", "WebSocket retries",
            timeline=["-"], surface_types=[], last_touch="2h",
            strength=4,
        ),
    ])


def _window_for(signal: str, *, focused: bool = False) -> v3.MinimalWindow:
    digest = v3.MinimalDigest()
    digest.populate(
        hero=_hero(signal=signal, focused=focused),
        investigations=_investigations(),
        returns=[],
    )
    return v3.MinimalWindow(digest)


def _empty_window() -> v3.MinimalWindow:
    return v3.MinimalWindow(v3.MinimalEmpty())


def main() -> None:
    captures = (
        ("high", _window_for("high")),
        ("medium", _window_for("medium")),
        ("low", _window_for("low")),
        ("empty", _empty_window()),
        ("resume", _window_for("high", focused=True)),
    )
    for name, widget in captures:
        widget.resize(*v3.MinimalWindow.DEFAULT_SIZE)
        path = render(widget, name, subdir="launcher-recovery")
        print(f"  wrote {path.relative_to(path.parents[3])}")


if __name__ == "__main__":
    main()
