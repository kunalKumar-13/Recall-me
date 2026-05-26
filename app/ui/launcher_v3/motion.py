"""Phase 6I — motion timings + helper factories.

The directive's vocabulary:

    fast:    120 ms — hover, focus ring fade
    normal:  180 ms — section reveal, card lift
    slow:    240 ms — full surface state crossfade

Allowed: ``fade`` · ``slide`` · ``expand``.
Banned: bounce, spring, overshoot.

The launcher's existing module ``app/ui/styles.py`` already exports
``MOTION_FAST_MS / NORMAL_MS / SLOW_MS`` for v2. The v3 set
re-anchors to the directive's values (fast 120 instead of 100,
slow 240 instead of 280) so the rebuild reads slightly calmer
than the v2 surface it replaces. Phase 9 re-tightens slow from
260 → 240 to match the visual-refresh spec.
"""

from __future__ import annotations

from typing import Optional

from PyQt6.QtCore import (
    QEasingCurve,
    QPropertyAnimation,
    QObject,
    QVariantAnimation,
)


# Public timings — milliseconds. The trio 120 / 180 / 240 is
# the Phase 9 visual-refresh contract.
FAST_MS = 120
NORMAL_MS = 180
SLOW_MS = 240

# The launcher's calm-out easing. Matches the v2 launcher so cards
# crossfading between the live and v3 surfaces don't read as a
# different product.
EASE = QEasingCurve.Type.OutCubic


def fade(
    target: QObject,
    *,
    start: float,
    end: float,
    duration: int = NORMAL_MS,
    parent: Optional[QObject] = None,
) -> QVariantAnimation:
    """A simple opacity tween that animates a `QGraphicsOpacityEffect`
    `opacity` property. Caller owns the effect — this returns the
    animation only."""
    anim = QPropertyAnimation(target, b"opacity", parent)
    anim.setDuration(duration)
    anim.setEasingCurve(EASE)
    anim.setStartValue(float(start))
    anim.setEndValue(float(end))
    return anim


def slide_y(
    target: QObject,
    prop: bytes,
    *,
    start: float,
    end: float,
    duration: int = NORMAL_MS,
    parent: Optional[QObject] = None,
) -> QPropertyAnimation:
    """Translate a numeric property along the Y axis. The directive's
    *slide* primitive — a card sliding in 4-8 px on first appear."""
    anim = QPropertyAnimation(target, prop, parent)
    anim.setDuration(duration)
    anim.setEasingCurve(EASE)
    anim.setStartValue(float(start))
    anim.setEndValue(float(end))
    return anim


def expand(
    target: QObject,
    prop: bytes,
    *,
    start: int,
    end: int,
    duration: int = SLOW_MS,
    parent: Optional[QObject] = None,
) -> QPropertyAnimation:
    """Animate a `maximumHeight` value over `duration`. Caller is
    responsible for pinning `minimumHeight` so the layout
    interpolates rather than collapsing on the first frame."""
    anim = QPropertyAnimation(target, prop, parent)
    anim.setDuration(duration)
    anim.setEasingCurve(EASE)
    anim.setStartValue(int(start))
    anim.setEndValue(int(end))
    return anim


__all__ = [
    "FAST_MS",
    "NORMAL_MS",
    "SLOW_MS",
    "EASE",
    "fade",
    "slide_y",
    "expand",
]
