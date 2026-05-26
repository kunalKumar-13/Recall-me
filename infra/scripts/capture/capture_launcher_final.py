"""Phase 6R — capture the frozen launcher.

Four PNGs in ``assets/screenshots/launcher-final/``:

  - ``hero.png``        populated digest — search + CONTINUE
                        hero (title + 3 chips + Resume 112) +
                        OTHER WORK vertical list (2 rows) +
                        footer
  - ``empty.png``       stacked onboarding — logo + headline +
                        Show example + Start working (both
                        inside the stack, not floating)
  - ``focus.png``       search bar with the lavender focus ring
  - ``overflow.png``    deliberately long title — verifies the
                        hero's title elider + the OTHER WORK
                        row's title elider both paint `...`

    python infra/scripts/capture/capture_launcher_final.py
"""

from __future__ import annotations

from _render import render
from app.ui import launcher_v3 as v3


def _populated_window() -> v3.MinimalWindow:
    hero = v3.RecoveryCardV3(
        candidate_id="rc_final",
        title="WebSocket retry debugging",
        targets=[
            ("path", "~/code/ws-retry/backoff.py"),
            ("path", "~/code/ws-retry/client.py"),
            ("url", "https://developer.mozilla.org/en-US/docs/Web/API/WebSocket"),
            ("url", "https://stackoverflow.com/q/123"),
            ("url", "https://google.com/search?q=websocket"),
        ],
        n_targets=5,
    )
    investigations = [
        v3.InvestigationCardV3("t-hp", "hp", "Healthcare proposal draft"),
        v3.InvestigationCardV3("t-rl", "rl", "RLHF notes"),
    ]
    digest = v3.MinimalDigest()
    digest.populate(hero=hero, investigations=investigations)
    return v3.MinimalWindow(digest)


def _empty_window() -> v3.MinimalWindow:
    return v3.MinimalWindow(v3.MinimalEmpty())


def _focus_window() -> v3.MinimalWindow:
    win = _populated_window()
    win.shell.search._focused = True  # noqa: SLF001
    win.shell.search.update()
    return win


def _overflow_window() -> v3.MinimalWindow:
    """Title overflow probe — the deliberately long string must
    elide with `...` rather than overflow into the Resume button."""
    hero = v3.RecoveryCardV3(
        candidate_id="rc_overflow",
        title=(
            "An investigation title that is intentionally far too "
            "long to fit inside the launcher's column"
        ),
        targets=[
            ("path", "/a"), ("path", "/b"),
            ("url", "https://x"), ("url", "https://y"),
        ],
        n_targets=4,
    )
    investigations = [
        v3.InvestigationCardV3(
            "t-long", "long",
            "Another investigation whose title also exceeds the "
            "column's natural width by a wide margin",
        ),
        v3.InvestigationCardV3("t-mid", "mid", "Medium-length investigation"),
        v3.InvestigationCardV3("t-rl", "rl", "RLHF"),
    ]
    digest = v3.MinimalDigest()
    digest.populate(hero=hero, investigations=investigations)
    return v3.MinimalWindow(digest)


def main() -> None:
    captures = (
        ("hero", _populated_window()),
        ("empty", _empty_window()),
        ("focus", _focus_window()),
        ("overflow", _overflow_window()),
    )
    for name, widget in captures:
        widget.resize(*v3.MinimalWindow.DEFAULT_SIZE)
        path = render(widget, name, subdir="launcher-final")
        print(f"  wrote {path.relative_to(path.parents[3])}")


if __name__ == "__main__":
    main()
