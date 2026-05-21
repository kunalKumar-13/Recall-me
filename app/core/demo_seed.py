"""Phase 4B — deterministic event-log seeder for `RECALL_DEMO_MODE=1`.

`RECALL_DEMO=1` (Phase 1A) gives the launcher a curated file-search
dataset. The Phase 4B mode goes further: it also seeds the
event log + the threads / evolution / recovery caches with a
believable, lived-in trace so a fresh install shows the
"Continue where you left off" surface, an active memory thread,
and a recoverable card *immediately*.

Goals:
  • realistic content (no lorem ipsum, no AI fluff)
  • four overlapping life-streams (developer / researcher /
    founder / casual browsing) so any reasonable query lands
  • timestamps anchored to "now" relative to seeding time so
    relative-time labels read "2h ago" / "yesterday" / "3 days
    ago" regardless of when the seed runs
  • completely deterministic — same call always produces the
    same events in the same order
  • idempotent within a single recall-version — calling seed()
    twice does not double the data; the second call detects
    the marker file and skips

The seeder writes to a *dedicated* base dir
(`~/.recall/events-demo/` by default) rather than the user's
real event log. The launcher's `--demo` boot path points the
EventLogger at this directory, so demo mode never overwrites
the user's real history.
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Dict, List, Optional

from .config import CONFIG_DIR
from .events import EventLogger

log = logging.getLogger("recall.core.demo_seed")

# Default demo event directory. Lives alongside the real event
# log but with a distinct name, so the two never collide.
DEMO_EVENTS_DIR: Path = CONFIG_DIR / "events-demo"

# A marker file the seeder drops once the seed completes. Used
# to detect "already seeded" on subsequent boots so the same
# story doesn't get appended again. Versioned so a future
# seed-data refresh forces a re-seed.
_SEED_VERSION = "4E.1"
_MARKER_NAME = ".seeded"


def _marker_for(base_dir: Path) -> Path:
    """Resolve the per-base-dir marker path. Keeping the marker
    *inside* the events-demo directory means a smoke test can
    point the seeder at a temp dir without colliding with the
    user's real `~/.recall/events-demo/.seeded`."""
    return base_dir / _MARKER_NAME


# --------------------------------------------------------------- model


@dataclass
class _DemoEvent:
    """One scripted event in the seed. Times are *relative* — the
    seeder converts `hours_ago` into an absolute timestamp at
    seed time so the trace anchors to "now"."""

    hours_ago: float
    session_id_offset: int  # which session this event belongs to
    kind: str               # browser_visit | browser_search | chat_session | open | query
    payload: Dict


# --------------------------------------------------------------- script


# Sessions are identified by an offset (0..N). The seeder
# allocates concrete `session_id` strings at run time so they
# embed the right date for the 30-min-gap reconstruction logic
# the threads layer relies on.

_SCRIPT: List[_DemoEvent] = [
    # ─────────────────────────────────────────────────────────
    # Story 1 — WebSocket retry debugging (the strong RECOVERY
    # candidate; spans 4 days, multiple sessions, mixed surfaces,
    # ends with a recent revisit so abandonment fires)
    # ─────────────────────────────────────────────────────────

    # Day -3 — initial research session
    _DemoEvent(72.0, 0, "browser_search", {
        "url": "https://www.google.com/search?q=websocket+reconnect+exponential+backoff",
        "query": "websocket reconnect exponential backoff",
        "engine": "google",
        "domain": "google.com",
        "browser": "chrome",
    }),
    _DemoEvent(71.9, 0, "browser_visit", {
        "url": "https://stackoverflow.com/questions/57294879/websocket-retry-on-disconnect-best-practices",
        "title": "WebSocket retry on disconnect — best practices",
        "domain": "stackoverflow.com",
        "browser": "chrome",
    }),
    _DemoEvent(71.7, 0, "browser_visit", {
        "url": "https://developer.mozilla.org/en-US/docs/Web/API/WebSocket",
        "title": "WebSocket — Web APIs · MDN",
        "domain": "developer.mozilla.org",
        "browser": "chrome",
    }),
    _DemoEvent(71.5, 0, "browser_visit", {
        "url": "https://github.com/websockets/ws/issues/2050",
        "title": "Reconnect logic on abrupt disconnect · ws #2050",
        "domain": "github.com",
        "browser": "chrome",
    }),

    # Day -2 — implementation burst (file opens; abandonment
    # candidate phase has high momentum)
    _DemoEvent(46.5, 1, "open", {
        "path": "~/code/ws-retry/client.py",
        "title": "client.py",
    }),
    _DemoEvent(46.4, 1, "open", {
        "path": "~/code/ws-retry/backoff.py",
        "title": "backoff.py",
    }),
    _DemoEvent(46.3, 1, "open", {
        "path": "~/code/ws-retry/client.py",
        "title": "client.py",
    }),
    _DemoEvent(46.0, 1, "browser_visit", {
        "url": "https://stackoverflow.com/questions/57294879/websocket-retry-on-disconnect-best-practices",
        "title": "WebSocket retry on disconnect — best practices",
        "domain": "stackoverflow.com",
        "browser": "chrome",
    }),

    # Day -1 — chat-session pivot (Claude conversation about backoff)
    _DemoEvent(22.0, 2, "chat_session", {
        "url": "https://claude.ai/chat/2f8e4b1d",
        "title": "Backoff with jitter — implementation review",
        "platform": "claude",
        "domain": "claude.ai",
        "browser": "chrome",
    }),
    _DemoEvent(21.7, 2, "open", {
        "path": "~/code/ws-retry/backoff.py",
        "title": "backoff.py",
    }),

    # Today, ~8 hours ago — revisit (triggers recovery's revisit
    # transition + the user's "I need to come back to this"
    # signal that the recovery engine grades highly)
    _DemoEvent(8.0, 3, "browser_visit", {
        "url": "https://stackoverflow.com/questions/57294879/websocket-retry-on-disconnect-best-practices",
        "title": "WebSocket retry on disconnect — best practices",
        "domain": "stackoverflow.com",
        "browser": "chrome",
    }),
    _DemoEvent(7.9, 3, "query", {
        "text": "websocket retry the part about jitter",
        "result_count": 4,
    }),
    # ...and reopened the implementation file — the interruption
    # lands mid-edit, which is exactly the moment recovery is for.
    _DemoEvent(7.8, 3, "open", {
        "path": "~/code/ws-retry/backoff.py",
        "title": "backoff.py",
    }),

    # ─────────────────────────────────────────────────────────
    # Story 2 — RLHF research (older but multi-day; flows
    # through resurfacing as "on your radar" rather than
    # recovery because the depth-event count is lower)
    # ─────────────────────────────────────────────────────────

    _DemoEvent(168.0, 4, "browser_search", {
        "url": "https://www.google.com/search?q=rlhf+reward+shaping",
        "query": "rlhf reward shaping",
        "engine": "google",
        "domain": "google.com",
        "browser": "chrome",
    }),
    _DemoEvent(167.9, 4, "browser_visit", {
        "url": "https://arxiv.org/abs/2203.02155",
        "title": "Training language models to follow instructions with human feedback",
        "domain": "arxiv.org",
        "browser": "chrome",
    }),
    _DemoEvent(167.5, 4, "browser_visit", {
        "url": "https://huggingface.co/blog/rlhf",
        "title": "Illustrating Reinforcement Learning from Human Feedback (RLHF)",
        "domain": "huggingface.co",
        "browser": "chrome",
    }),

    _DemoEvent(120.0, 5, "browser_visit", {
        "url": "https://arxiv.org/abs/2203.02155",
        "title": "Training language models to follow instructions with human feedback",
        "domain": "arxiv.org",
        "browser": "chrome",
    }),
    _DemoEvent(119.8, 5, "browser_visit", {
        "url": "https://www.alignmentforum.org/posts/RLHF-reward-hacking",
        "title": "RLHF reward hacking — Alignment Forum",
        "domain": "alignmentforum.org",
        "browser": "chrome",
    }),

    _DemoEvent(54.0, 6, "browser_search", {
        "url": "https://www.google.com/search?q=rlhf+kl+penalty+tuning",
        "query": "rlhf kl penalty tuning",
        "engine": "google",
        "domain": "google.com",
        "browser": "chrome",
    }),
    _DemoEvent(53.9, 6, "browser_visit", {
        "url": "https://huggingface.co/blog/rlhf",
        "title": "Illustrating Reinforcement Learning from Human Feedback (RLHF)",
        "domain": "huggingface.co",
        "browser": "chrome",
    }),

    # ─────────────────────────────────────────────────────────
    # Story 3 — healthcare-agents startup (the long-arc thread;
    # spans ~10 days, mixed surfaces, dormant for a few days
    # — the resurfacing engine's classic case)
    # ─────────────────────────────────────────────────────────

    _DemoEvent(240.0, 7, "open", {
        "path": "~/Documents/healthcare-startup/pitch_deck_v3.pdf",
        "title": "pitch_deck_v3.pdf",
    }),
    _DemoEvent(239.7, 7, "open", {
        "path": "~/Documents/healthcare-startup/market-sizing.xlsx",
        "title": "market-sizing.xlsx",
    }),
    _DemoEvent(239.3, 7, "chat_session", {
        "url": "https://claude.ai/chat/8a1f0c3d",
        "title": "Pediatric triage routing — model assumptions",
        "platform": "claude",
        "domain": "claude.ai",
        "browser": "chrome",
    }),

    _DemoEvent(192.0, 8, "browser_visit", {
        "url": "https://www.cdc.gov/nchs/fastats/physician-visits.htm",
        "title": "Physician Office Visits · CDC",
        "domain": "cdc.gov",
        "browser": "chrome",
    }),
    _DemoEvent(191.6, 8, "open", {
        "path": "~/Documents/healthcare-startup/notes.md",
        "title": "notes.md",
    }),

    _DemoEvent(96.0, 9, "open", {
        "path": "~/Documents/healthcare-startup/pitch_deck_v3.pdf",
        "title": "pitch_deck_v3.pdf",
    }),
    _DemoEvent(95.7, 9, "browser_visit", {
        "url": "https://www.ycombinator.com/companies/industry/healthcare",
        "title": "Y Combinator — Healthcare companies",
        "domain": "ycombinator.com",
        "browser": "chrome",
    }),

    # ─────────────────────────────────────────────────────────
    # Story 4 — casual browsing (depth-event poor; resurfacing
    # may catch it, recovery will correctly suppress it via the
    # Phase 3C depth filter)
    # ─────────────────────────────────────────────────────────

    _DemoEvent(50.0, 10, "browser_visit", {
        "url": "https://www.theatlantic.com/magazine/archive/2023/kanye-interview",
        "title": "What I Saw in Kanye's Studio — The Atlantic",
        "domain": "theatlantic.com",
        "browser": "chrome",
    }),
    _DemoEvent(49.7, 10, "browser_visit", {
        "url": "https://en.wikipedia.org/wiki/Discography_of_Kanye_West",
        "title": "Kanye West discography — Wikipedia",
        "domain": "en.wikipedia.org",
        "browser": "chrome",
    }),
    _DemoEvent(15.0, 11, "browser_visit", {
        "url": "https://www.theatlantic.com/magazine/archive/2023/kanye-interview",
        "title": "What I Saw in Kanye's Studio — The Atlantic",
        "domain": "theatlantic.com",
        "browser": "chrome",
    }),
]


# --------------------------------------------------------------- seeder


def is_already_seeded(base_dir: Optional[Path] = None) -> bool:
    """Cheap check the boot path can call before doing the work."""
    marker = _marker_for(base_dir or DEMO_EVENTS_DIR)
    if not marker.exists():
        return False
    try:
        meta = json.loads(marker.read_text(encoding="utf-8"))
        return meta.get("version") == _SEED_VERSION
    except (OSError, ValueError):
        return False


def seed(
    base_dir: Optional[Path] = None,
    *,
    now: Optional[datetime] = None,
    force: bool = False,
) -> Path:
    """Write the demo event-log + caches.

    Returns the base directory the seed wrote into. Callers
    (typically `app.main`) point an `EventLogger` at this dir
    when `RECALL_DEMO_MODE=1` is set so the seeded trace
    surfaces in the launcher.

    `force=True` reseeds even if the marker file says we're
    current — useful for `RECALL_DEMO_RESEED=1` workflows where
    the user wants a fresh capture every time.
    """
    base_dir = base_dir or DEMO_EVENTS_DIR
    base_dir.mkdir(parents=True, exist_ok=True)
    marker = _marker_for(base_dir)

    if not force and is_already_seeded(base_dir):
        log.info("demo seed: already current (version=%s)", _SEED_VERSION)
        return base_dir

    # Wipe any stale demo events from a previous seed version.
    for old in base_dir.glob("*.jsonl"):
        try:
            old.unlink()
        except OSError:
            pass

    if now is None:
        now = datetime.now(timezone.utc)

    # Per-session id strings, allocated deterministically from
    # each session's anchor timestamp. Sessions 0..N map to
    # distinct concrete ids.
    session_ids: Dict[int, str] = {}

    # Group events by absolute timestamp + per-day file.
    for ev in _SCRIPT:
        ts = now - timedelta(hours=ev.hours_ago)
        sid = session_ids.get(ev.session_id_offset)
        if sid is None:
            sid = (
                "s_"
                + ts.strftime("%Y%m%d_%H%M%S_%f")
            )
            session_ids[ev.session_id_offset] = sid
        record = {
            "ts": ts.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "session_id": sid,
            "kind": ev.kind,
            "payload": ev.payload,
        }
        day_file = base_dir / f"{ts.date().isoformat()}.jsonl"
        # Append rather than overwrite — within one seed pass
        # we want events accumulated in chronological order per
        # day file. The pre-clear above guarantees we start
        # from empty, so the appends here build the file from
        # scratch.
        with day_file.open("a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False))
            f.write("\n")

    # Drop the marker so subsequent boots detect "already
    # seeded" and skip the writes.
    try:
        marker.write_text(
            json.dumps({
                "version": _SEED_VERSION,
                "seeded_at": now.strftime("%Y-%m-%dT%H:%M:%SZ"),
                "event_count": len(_SCRIPT),
                "session_count": len(session_ids),
            }, indent=2),
            encoding="utf-8",
        )
    except OSError:
        # Best-effort persistence — events are already on disk.
        pass
    log.info(
        "demo seed: wrote %d events across %d sessions",
        len(_SCRIPT),
        len(session_ids),
    )
    return base_dir


def reset(base_dir: Optional[Path] = None) -> None:
    """Tear down the demo event store. Used by recapture
    workflows (`infra/scripts/build_screenshots.py` once that
    lands) so each capture starts from a known empty state."""
    base_dir = base_dir or DEMO_EVENTS_DIR
    if not base_dir.exists():
        return
    for f in base_dir.glob("*.jsonl"):
        try:
            f.unlink()
        except OSError:
            pass
    try:
        _marker_for(base_dir).unlink()
    except OSError:
        pass


def event_logger_for_demo() -> EventLogger:
    """Convenience constructor — returns an `EventLogger`
    pointed at the demo dir. `app.main` calls this when the
    `RECALL_DEMO_MODE=1` env var is set."""
    seed()
    return EventLogger(base_dir=DEMO_EVENTS_DIR, enabled=True)
