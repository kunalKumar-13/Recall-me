"""Launcher animations - the first slice extracted from launcher.py.

Phase 5I begins the split of `app/ui/launcher.py` (2.5 KLOC) into
focused modules. This file is the *animations* slice - currently
just the one-shot stagger-reveal that fades the digest sections
in top-down on the first show per launcher instance.

The directive's eventual layout was named as
`app/ui/launcher/{window, digest, cards, animations, state,
recovery}.py`. This module is the standalone *animations* file;
the rest of the split is deferred (per the directive's "move
only one slice; no massive rewrite" rule). Future slices either
import from here or live next to it as siblings.

Module-level functions take the `Launcher` instance and read its
attributes; the launcher method becomes a one-line wrapper. The
inversion keeps `Launcher` cohesive while moving real code out.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from PyQt6.QtCore import QEasingCurve, QPropertyAnimation, QTimer
from PyQt6.QtWidgets import QGraphicsOpacityEffect

from .styles import MOTION_NORMAL_MS

if TYPE_CHECKING:
    # Type-only; avoids a circular import at runtime.
    from .launcher import Launcher


# 60 ms between sections - calm enough to read top-down, fast
# enough that the whole digest is visible inside ~600 ms.
_STAGGER_GAP_MS = 60


def play_digest_stagger_reveal(launcher: Launcher) -> None:
    """One-shot fade-in cascade across the visible digest sections.

    Guarded by `launcher._digest_stagger_played` so a re-show after
    the first cascade does not re-animate (the Phase 4I calm rule:
    motion is for first contact, not for every reopen).

    Effects + animations are stored on the launcher instance so
    Qt's GC does not eat them mid-flight (a finished
    QPropertyAnimation can be dropped; while running it must stay
    alive).
    """
    if getattr(launcher, "_digest_stagger_played", False):
        return
    launcher._digest_stagger_played = True

    sections = (
        launcher.recovery_header, launcher.recovery_list,
        launcher.threads_header, launcher.threads_list,
        launcher.resurface_header, launcher.resurface_list,
        launcher.recent_queries_header, launcher.recent_queries_list,
        launcher.recent_activity_header, launcher.recent_activity_list,
        launcher.resurfaced_header, launcher.resurfaced_list,
    )
    visible = [w for w in sections if w.isVisible()]

    effects: list[QGraphicsOpacityEffect] = []
    animations: list[QPropertyAnimation] = []
    for i, w in enumerate(visible):
        eff = QGraphicsOpacityEffect(w)
        eff.setOpacity(0.0)
        w.setGraphicsEffect(eff)
        effects.append(eff)

        anim = QPropertyAnimation(eff, b"opacity", launcher)
        anim.setDuration(MOTION_NORMAL_MS)
        anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        anim.setStartValue(0.0)
        anim.setEndValue(1.0)
        QTimer.singleShot(i * _STAGGER_GAP_MS, anim.start)
        animations.append(anim)

    # Stash on the launcher instance for the duration of the
    # cascade. They're not used elsewhere - this is just a GC pin.
    launcher._stagger_effects = effects
    launcher._stagger_animations = animations
