"""Phase 7B — capture the production-frozen launcher.

Five PNGs in ``assets/screenshots/launcher-ship/``:

  - ``hero.png``         populated digest (canonical WebSocket
                         recovery + 2 OTHER WORK rows)
  - ``empty.png``        stacked onboarding inside the root card
  - ``focus.png``        search bar with the lavender focus ring
  - ``demo.png``         the directive's canonical demo trio
                         (WebSocket retry debugging · proposal
                         draft · RLHF notes)
  - ``overflow.png``     long titles in both hero + OTHER WORK
                         elide with `...`

DPI scaling: every widget uses point-based typography so
Windows 100 % / 125 % / 150 % render at the same logical
geometry. The audit document
[`LAUNCHER_SHIP_AUDIT.md`](../../docs/product/LAUNCHER_SHIP_AUDIT.md)
covers the DPI contract; the offscreen capture pipeline keeps
DPI fixed by design, so scale-factor PNGs would lie about the
real Windows behaviour and aren't generated here.

    python infra/scripts/capture/capture_launcher_ship.py
"""

from __future__ import annotations

from _render import render
from app.ui import launcher_v3 as v3


def _populated_window() -> v3.MinimalWindow:
    hero = v3.RecoveryCardV3(
        candidate_id="rc_ship",
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
    win.shell.search._hint.setVisible(False)  # noqa: SLF001
    win.shell.search.update()
    return win


def _demo_window() -> v3.MinimalWindow:
    """The 7B-canonical demo trio."""
    hero = v3.RecoveryCardV3(
        candidate_id="rc_demo",
        title="WebSocket retry debugging",
        targets=[
            ("path", "~/code/ws-retry/backoff.py"),
            ("path", "~/code/ws-retry/client.py"),
            ("url", "https://developer.mozilla.org/en-US/docs/Web/API/WebSocket"),
            ("url", "https://stackoverflow.com/q/123"),
        ],
        n_targets=4,
    )
    investigations = [
        v3.InvestigationCardV3("t-prop", "prop", "Healthcare pitch — proposal draft"),
        v3.InvestigationCardV3("t-rl",   "rl",   "RLHF reward shaping notes"),
    ]
    digest = v3.MinimalDigest()
    digest.populate(hero=hero, investigations=investigations)
    return v3.MinimalWindow(digest)


def _overflow_window() -> v3.MinimalWindow:
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
        ("demo", _demo_window()),
        ("overflow", _overflow_window()),
    )
    for name, widget in captures:
        widget.resize(*v3.MinimalWindow.DEFAULT_SIZE)
        path = render(widget, name, subdir="launcher-ship")
        print(f"  wrote {path.relative_to(path.parents[3])}")


if __name__ == "__main__":
    main()
