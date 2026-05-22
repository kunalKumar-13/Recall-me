"""Launcher digest constants + label helpers.

Phase 5J launcher-split phase 2 — the *digest* slice. Holds the
limits and labels for the idle digest's seven sections (recovery,
investigations, resurface, recent queries, recent activity,
recently-active files, resurfaced files) and the time-of-day
label function. Pure module-level values + one stdlib-only
function; nothing here owns Qt widgets.

Kept as a sibling of `launcher.py` (not under `app/ui/launcher/`)
so every `from app.ui.launcher import Launcher` keeps working
unchanged. The eventual `app/ui/launcher/digest.py` package layout
is a single atomic refactor (the `.cards` / `.widgets` / `.styles`
relative imports inside the 2.5 KLOC file flip from `.X` to `..X`)
deferred to a follow-up phase. The directive's "Keep imports
stable" rule is the binding constraint here.
"""

from __future__ import annotations

from datetime import datetime


# ── digest section caps ─────────────────────────────────────────
#
# Each cap controls one digest section's row count. The brief
# named these explicitly: a quiet surface, never a feed; the
# launcher should read as a few calm zones rather than a wall of
# data. Bumping these makes the digest louder.

# Phase 1B: the original digest. Recently-active files + the
# rotating "resurfaced this week" pair.
DIGEST_RECENT_MAX = 4
DIGEST_RESURFACED_MAX = 2
RESURFACED_MIN_AGE_DAYS = 30

# Phase 1B: the *lately you searched* / *recent digital activity*
# pair under the same digest.
DIGEST_RECENT_QUERIES_MAX = 4
DIGEST_RECENT_ACTIVITY_MAX = 3

# Phase 2B resurfacing — hard ceiling matches the engine's own
# cap. Anything higher would push the digest past one screenful
# and turn a quiet section into a feed.
DIGEST_CONTINUE_MAX = 4

# Phase 2C: memory threads. The brief asks for an infrastructure
# aesthetic — show fewer than a dashboard would, even though the
# engine supports up to 20. Five is the sweet spot.
DIGEST_THREADS_MAX = 5

# Phase 3B: continuity recovery. The brief's ceiling is three;
# the launcher honours it. Recovery is the *primary* idle
# surface, but fewer is better — three resumable threads on top
# is plenty.
DIGEST_RECOVERY_MAX = 3


# ── time-of-day labels ──────────────────────────────────────────


def digest_labels() -> dict[str, str]:
    """Recovery + threads section headers by time of day. Calm
    shifts only — never a notification, never a streak.

    Morning leads with *Continue today* (offer the next step);
    evening with *You paused here* (the things to come back to);
    midday keeps *Continue where you left off* on the recovery
    section. The investigations section uses *Active investigations*
    in the morning and *Still active* otherwise.

    Stdlib only; the launcher calls this on every digest paint so
    the surface stays in sync with the user's clock.
    """
    hour = datetime.now().hour
    if hour < 12:
        return {
            "recovery": "Continue today",
            "threads": "Active investigations",
        }
    if hour >= 18:
        return {
            "recovery": "You paused here",
            "threads": "Still active",
        }
    return {
        "recovery": "Continue where you left off",
        "threads": "Still active",
    }
