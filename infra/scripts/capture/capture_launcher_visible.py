"""Phase 6P.1 — capture the visibility-recovered launcher.

Four PNGs land in ``assets/screenshots/launcher-visible/``:

  - ``hero.png``           populated digest — search + CONTINUE
                           hero + OTHER WORK card
  - ``empty.png``          stacked empty surface — logo + headline
                           + sub + two same-width buttons
  - ``focus.png``          search bar with the lavender focus ring
  - ``investigations.png`` the OTHER WORK card alone, full-width,
                           showing the wrapped row

The captures verify the directive's *Launcher readable from 2
meters away* success criterion: layered white cards on the warm
`#F3F1ED` page, visible borders, fixed-width Resume button (110),
and the soft 4-px lavender accent strip on the hero.

    python infra/scripts/capture/capture_launcher_visible.py
"""

from __future__ import annotations

from _render import render
from app.ui import launcher_v3 as v3


def _populated_window() -> v3.MinimalWindow:
    hero = v3.RecoveryCardV3(
        candidate_id="rc_visible",
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


def _focused_window() -> v3.MinimalWindow:
    """A populated digest with the search bar in its focused state.
    The capture exercises the lavender focus ring + the cleaner card
    fill so the *Search focus* requirement has a visual proof."""
    win = _populated_window()
    win.shell.search._focused = True  # noqa: SLF001
    win.shell.search.update()
    return win


def _investigations_only_window() -> v3.MinimalWindow:
    """A digest with no hero — only the OTHER WORK card. Verifies
    the wrapped-investigations spec independently of the hero."""
    investigations = [
        v3.InvestigationCardV3("t-ws", "ws", "WebSocket"),
        v3.InvestigationCardV3("t-hp", "hp", "Healthcare proposal"),
        v3.InvestigationCardV3("t-rl", "rl", "RLHF"),
    ]
    digest = v3.MinimalDigest()
    digest.populate(hero=None, investigations=investigations)
    return v3.MinimalWindow(digest)


def main() -> None:
    captures = (
        ("hero", _populated_window()),
        ("empty", _empty_window()),
        ("focus", _focused_window()),
        ("investigations", _investigations_only_window()),
    )
    for name, widget in captures:
        widget.resize(*v3.MinimalWindow.DEFAULT_SIZE)
        path = render(widget, name, subdir="launcher-visible")
        print(f"  wrote {path.relative_to(path.parents[3])}")


if __name__ == "__main__":
    main()
