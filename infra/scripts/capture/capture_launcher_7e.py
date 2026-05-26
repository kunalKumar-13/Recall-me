"""Phase 7E — capture the final-product launcher.

Five PNGs in ``assets/screenshots/launcher-7e/``:

  - ``home.png``       populated digest: hero + recent memory
                       + OTHER WORK + trust row
  - ``high.png``       hero variant: HIGH signal (filled rail)
  - ``med.png``        hero variant: MED signal (soft rail)
  - ``low.png``        hero variant: LOW signal (outline rail)
  - ``no_hero.png``    no recovery — Recent Memory + OTHER
                       WORK carry the surface alone

    python infra/scripts/capture/capture_launcher_7e.py
"""

from __future__ import annotations

from _render import render
from app.ui import launcher_v3 as v3


def _memory_rows() -> list:
    return [
        v3.MemoryRow("21:32", "ChatGPT", "RLHF reward shaping"),
        v3.MemoryRow("21:28", "GitHub", "websocket retry"),
        v3.MemoryRow("21:20", "Stitch", "launcher redesign"),
        v3.MemoryRow("21:11", "Google", "resume flow"),
        v3.MemoryRow("20:55", "Stack", "websocket reconnect"),
    ]


def _investigations() -> list:
    return [
        v3.InvestigationCardV3(
            "t1", "t", "Healthcare proposal draft",
            last_seen="3d", strong=True,
        ),
        v3.InvestigationCardV3(
            "t2", "t", "RLHF reward shaping notes",
            last_seen="5d", strong=False,
        ),
        v3.InvestigationCardV3(
            "t3", "t", "Marketing rewrite",
            last_seen="1w", strong=False,
        ),
    ]


def _hero(signal: str = "high") -> v3.RecoveryCardV3:
    return v3.RecoveryCardV3(
        candidate_id=f"rc_{signal}",
        title="WebSocket retry debugging",
        targets=[
            ("path", "~/code/ws-retry/backoff.py"),
            ("path", "~/code/ws-retry/client.py"),
            ("url", "https://developer.mozilla.org/en-US/docs/Web/API/WebSocket"),
            ("url", "https://stackoverflow.com/q/123"),
        ],
        extra_clause="returned 2d",
        signal=signal,
        n_targets=4,
    )


def _digest_with_hero(signal: str = "high") -> v3.MinimalDigest:
    digest = v3.MinimalDigest()
    digest.populate(
        hero=_hero(signal),
        memory=_memory_rows(),
        investigations=_investigations(),
    )
    return digest


def _digest_no_hero() -> v3.MinimalDigest:
    digest = v3.MinimalDigest()
    digest.populate(
        hero=None,
        memory=_memory_rows(),
        investigations=_investigations(),
    )
    return digest


def _window(digest: v3.MinimalDigest, events: int, investigations: int) -> v3.MinimalWindow:
    win = v3.MinimalWindow(digest)
    win.shell.trust.set_counts(events, investigations)
    return win


def main() -> None:
    captures = (
        ("home", _window(_digest_with_hero("high"), 71, 11)),
        ("high", _window(_digest_with_hero("high"), 71, 11)),
        ("med", _window(_digest_with_hero("med"), 48, 8)),
        ("low", _window(_digest_with_hero("low"), 26, 4)),
        ("no_hero", _window(_digest_no_hero(), 71, 11)),
    )
    for name, widget in captures:
        widget.resize(*v3.MinimalWindow.DEFAULT_SIZE)
        path = render(widget, name, subdir="launcher-7e")
        print(f"  wrote {path.relative_to(path.parents[3])}")


if __name__ == "__main__":
    main()
