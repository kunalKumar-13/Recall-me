"""Capture the Phase 6O reset launcher.

Two PNGs land in ``assets/screenshots/launcher-reset/``:

  - ``populated.png``  the HIGH-recovery path — search + CONTINUE
                       hero (100 px fixed) + OTHER WORK (3 titles)
  - ``empty.png``      no HIGH recovery — search + centred headline +
                       two-line body + two buttons

Nothing else. No returns row. No trust line. No preview card. No
confidence sentence. No status indicators. The directive's reset
contract is enforced by the widgets themselves.

    python infra/scripts/capture/capture_launcher_reset.py
"""

from __future__ import annotations

from _render import render
from app.ui import launcher_v3 as v3


def _populated_window() -> v3.MinimalWindow:
    hero = v3.RecoveryCardV3(
        candidate_id="rc_reset",
        title="WebSocket retry debugging",
        meta="2 tabs · 2 files · returned after 2d",
        n_targets=4,
    )
    investigations = [
        v3.InvestigationCardV3("t-ws", "ws", "WebSocket"),
        v3.InvestigationCardV3("t-hp", "hp", "Healthcare proposal"),
        v3.InvestigationCardV3("t-rl", "rl", "RLHF"),
    ]
    digest = v3.MinimalDigest()
    digest.populate(hero=hero, investigations=investigations)
    return v3.MinimalWindow(digest)


def _empty_window() -> v3.MinimalWindow:
    return v3.MinimalWindow(v3.MinimalEmpty())


def main() -> None:
    captures = (
        ("populated", _populated_window()),
        ("empty", _empty_window()),
    )
    for name, widget in captures:
        widget.resize(*v3.MinimalWindow.DEFAULT_SIZE)
        path = render(widget, name, subdir="launcher-reset")
        print(f"  wrote {path.relative_to(path.parents[3])}")


if __name__ == "__main__":
    main()
