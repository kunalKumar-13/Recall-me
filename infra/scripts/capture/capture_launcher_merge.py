"""Phase 7B.1 — capture the visual-merge launcher.

Five PNGs in ``assets/screenshots/launcher-merge/``:

  - ``empty.png``      empty workspace (infinity glyph +
                       *"Everything you've seen, searchable."*)
  - ``active.png``     populated workspace (Continue document)
  - ``resume.png``     same workspace with the hero focused
                       (lavender ring on the Continue document)
  - ``demo.png``       canonical demo (WebSocket retry)
  - ``overflow.png``   long title — Continue document elides

The directive's five screens land verbatim: empty · active ·
resume · demo · overflow.

    python infra/scripts/capture/capture_launcher_merge.py
"""

from __future__ import annotations

from _render import render
from app.ui import launcher_v3 as v3


def _populated_window() -> v3.MinimalWindow:
    hero = v3.RecoveryCardV3(
        candidate_id="rc_merge",
        title="WebSocket retry debugging",
        targets=[
            ("path", "~/code/ws-retry/backoff.py"),
            ("path", "~/code/ws-retry/client.py"),
            ("url", "https://developer.mozilla.org/en-US/docs/Web/API/WebSocket"),
            ("url", "https://stackoverflow.com/q/123"),
        ],
        extra_clause="returned after 2d",
        n_targets=4,
    )
    digest = v3.MinimalDigest()
    digest.populate(hero=hero, investigations=[])
    return v3.MinimalWindow(digest)


def _empty_window() -> v3.MinimalWindow:
    return v3.MinimalWindow(v3.MinimalEmpty())


def _resume_window() -> v3.MinimalWindow:
    """Same active digest but the hero is keyboard-focused, so
    the lavender ring + brighter rail land in the capture."""
    win = _populated_window()
    hero = win.shell.findChild(v3.RecoveryCardV3)
    if hero is not None:
        hero._focused = True  # noqa: SLF001
        hero.update()
    return win


def _demo_window() -> v3.MinimalWindow:
    """The directive's canonical demo: WebSocket retry debugging
    with the 2-day return clause."""
    hero = v3.RecoveryCardV3(
        candidate_id="rc_demo",
        title="WebSocket retry debugging",
        targets=[
            ("path", "~/code/ws-retry/backoff.py"),
            ("path", "~/code/ws-retry/client.py"),
            ("url", "https://developer.mozilla.org/en-US/docs/Web/API/WebSocket"),
            ("url", "https://stackoverflow.com/q/123"),
        ],
        extra_clause="returned after 2d",
        n_targets=4,
    )
    digest = v3.MinimalDigest()
    digest.populate(hero=hero, investigations=[])
    return v3.MinimalWindow(digest)


def _overflow_window() -> v3.MinimalWindow:
    hero = v3.RecoveryCardV3(
        candidate_id="rc_overflow",
        title=(
            "An investigation title that is intentionally far too "
            "long to fit on a single line of the document"
        ),
        targets=[
            ("path", "/a"), ("path", "/b"),
            ("url", "https://x"), ("url", "https://y"),
        ],
        extra_clause="returned after 5d",
        n_targets=4,
    )
    digest = v3.MinimalDigest()
    digest.populate(hero=hero, investigations=[])
    return v3.MinimalWindow(digest)


def main() -> None:
    captures = (
        ("empty", _empty_window()),
        ("active", _populated_window()),
        ("resume", _resume_window()),
        ("demo", _demo_window()),
        ("overflow", _overflow_window()),
    )
    for name, widget in captures:
        widget.resize(*v3.MinimalWindow.DEFAULT_SIZE)
        path = render(widget, name, subdir="launcher-merge")
        print(f"  wrote {path.relative_to(path.parents[3])}")


if __name__ == "__main__":
    main()
