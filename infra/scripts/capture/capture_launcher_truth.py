"""Phase 6Q — capture the Continuity Truth surfaces.

Four PNGs land in ``assets/screenshots/launcher-truth/``:

  - ``hero_with_why.png`` populated digest — the hero now carries
                          a *Why this?* link on the right of its
                          meta row
  - ``why_sheet.png``     the WhyThisSheet open with the canonical
                          WebSocket signals
  - ``showcase.png``      three-investigation showcase — one HIGH
                          hero, two MED rows; verifies the *only
                          one hero* invariant
  - ``ledger_demoted.png`` the same WebSocket recovery after a
                          ledger flag — hero is suppressed, only
                          OTHER WORK remains

    python infra/scripts/capture/capture_launcher_truth.py
"""

from __future__ import annotations

from _render import render
from app.ui import launcher_v3 as v3


_DEMO_SIGNALS = [
    "unfinished work",
    "returned after a 2-day gap",
    "5 targets involved",
    "multiple surfaces engaged",
]


def _hero_with_why() -> v3.MinimalWindow:
    hero = v3.RecoveryCardV3(
        candidate_id="rc_truth",
        title="WebSocket retry debugging",
        meta="2 tabs - 2 files - reopened 2d ago",
        n_targets=5,
        signals=_DEMO_SIGNALS,
    )
    investigations = [
        v3.InvestigationCardV3("t-ws", "ws", "WebSocket"),
        v3.InvestigationCardV3("t-hp", "hp", "Healthcare proposal"),
        v3.InvestigationCardV3("t-rl", "rl", "RLHF"),
    ]
    digest = v3.MinimalDigest()
    digest.populate(hero=hero, investigations=investigations)
    return v3.MinimalWindow(digest)


def _why_sheet_open() -> v3.MinimalWindow:
    """The hero + the *Why this?* sheet, painted in the centre of
    the launcher. We re-use the populated window and reposition
    the sheet for a clean composite capture."""
    win = _hero_with_why()
    sheet = v3.WhyThisSheet(win)
    sheet.open(_DEMO_SIGNALS)
    sheet.adjustSize()
    win.resize(*v3.MinimalWindow.DEFAULT_SIZE)
    # Centre the sheet inside the window.
    x = (win.width() - sheet.width()) // 2
    y = (win.height() - sheet.height()) // 2
    sheet.move(x, y)
    return win


def _showcase_window() -> v3.MinimalWindow:
    """The directive's *Showcase Reality*: three investigations
    (proposal draft, RLHF notes, WebSocket issue), one HIGH hero,
    the other two as MED rows. Verifies *only one hero* invariant
    visually."""
    hero = v3.RecoveryCardV3(
        candidate_id="rc_websocket",
        title="WebSocket retry debugging",
        meta="2 tabs - 2 files - reopened 2d ago",
        n_targets=5,
        signals=_DEMO_SIGNALS,
    )
    investigations = [
        v3.InvestigationCardV3("t-prop", "prop", "Healthcare proposal draft"),
        v3.InvestigationCardV3("t-rlhf", "rlhf", "RLHF notes"),
        v3.InvestigationCardV3("t-ws",   "ws",   "WebSocket retry debugging"),
    ]
    digest = v3.MinimalDigest()
    digest.populate(hero=hero, investigations=investigations)
    return v3.MinimalWindow(digest)


def _ledger_demoted_window() -> v3.MinimalWindow:
    """Same three investigations but the WebSocket hero is
    suppressed (ledger flag) — only OTHER WORK survives."""
    investigations = [
        v3.InvestigationCardV3("t-prop", "prop", "Healthcare proposal draft"),
        v3.InvestigationCardV3("t-rlhf", "rlhf", "RLHF notes"),
        v3.InvestigationCardV3("t-ws",   "ws",   "WebSocket retry debugging"),
    ]
    digest = v3.MinimalDigest()
    digest.populate(hero=None, investigations=investigations)
    return v3.MinimalWindow(digest)


def main() -> None:
    captures = (
        ("hero_with_why", _hero_with_why()),
        ("why_sheet", _why_sheet_open()),
        ("showcase", _showcase_window()),
        ("ledger_demoted", _ledger_demoted_window()),
    )
    for name, widget in captures:
        widget.resize(*v3.MinimalWindow.DEFAULT_SIZE)
        path = render(widget, name, subdir="launcher-truth")
        print(f"  wrote {path.relative_to(path.parents[3])}")


if __name__ == "__main__":
    main()
