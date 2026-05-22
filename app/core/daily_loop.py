"""Phase 6F — daily continuity loop.

Tracks **counts only** about Recall's *own* surfaces (not the user's
work). Six bins per local day, one append-only JSONL line per local
day, stored at ``~/.recall/daily_loop.jsonl``.

The point of this layer is to prove that the recovery loop is
*used*, not just *captured*. Recall already knows how many events
landed in the user's day — that's `~/.recall/events/`. What it
doesn't track yet is how often the user came back, opened an
investigation, accepted a recovery, or watched a Resume actually
work. That signal is the heart of *repeat use*, and Phase 6F is
the layer that names it.

Six counters per day:

    day_started              the user opened the launcher at least once
    investigations_opened    a launcher click on an InvestigationCard
    recoveries_shown         the launcher surfaced a recovery card
    recoveries_used          the user clicked Resume on one
    returns                  a return after a >= 30-minute idle gap
    resume_success           a Resume that the user did not undo

Plus three derived signals (computed at read time, never stored):

    continuity_restored      recoveries_used / recoveries_shown
    return_rate              returns / day_started
    resume_quality           resume_success / recoveries_used

No content ever crosses this boundary. No URLs, no filenames, no
queries, no chat content, no titles. Counts only.

This module also owns the **return detector**: every ingest path
calls :func:`mark_event` with the event's timestamp, and the
detector decides whether it crossed a return threshold and bumps
the ``returns`` bin. The threshold is configurable; the default
(:data:`RETURN_GAP_MIN_SECONDS` = 1800 s = 30 min) matches the
session reconstructor's 30-minute gap.

Performance budget: each ``mark_*`` call is one ``json.loads`` on
a single line plus one append-write. The line cardinality is one
per local day, so the file stays small (< 1 KB / month) and the
on-disk read fits a single page. The whole layer is *purely
additive* — deleting ``app/core/daily_loop.py`` removes the
counters without breaking any downstream artifact.

Disable: set ``RECALL_DAILY_LOOP=off`` in the environment to make
every ``mark_*`` call a no-op.
"""

from __future__ import annotations

import json
import logging
import os
import time
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Dict, List, Optional

from .config import CONFIG_DIR

log = logging.getLogger("recall.core.daily_loop")

# One-line-per-day JSONL. Tiny, hand-inspectable, deletable.
LOG_FILE: Path = CONFIG_DIR / "daily_loop.jsonl"

# Session-state file for the return detector — `last_event_ts` and the
# `last_return_ts`. Re-derived from `events/` on first call when
# missing; not load-bearing, just a fast path.
STATE_FILE: Path = CONFIG_DIR / "daily_loop_state.json"

# A return is *only* counted when the gap is at least this many
# seconds. Matches the session reconstructor's 30-min idle break so
# the two layers agree on what "left the desk" means.
RETURN_GAP_MIN_SECONDS = 30 * 60

_COUNTER_BINS = (
    "day_started",
    "investigations_opened",
    "recoveries_shown",
    "recoveries_used",
    "returns",
    "resume_success",
)


def _enabled() -> bool:
    """Module-level disable flag. Module-level read on every call —
    cheap; the env-var lookup is one dict hit, no I/O."""
    return os.environ.get("RECALL_DAILY_LOOP", "on").strip().lower() != "off"


# --------------------------------------------------------------- I/O


def _read_state() -> Dict[str, float]:
    try:
        return json.loads(STATE_FILE.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}


def _write_state(state: Dict[str, float]) -> None:
    try:
        STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
        tmp = STATE_FILE.with_suffix(".json.tmp")
        tmp.write_text(json.dumps(state, indent=2), encoding="utf-8")
        tmp.replace(STATE_FILE)
    except OSError as e:
        log.warning("daily_loop: state persist failed (%s)", e)


def _read_log() -> List[Dict]:
    """Stream-parse the per-day records. Bad lines are skipped, never
    raised — the layer must never break the API process."""
    if not LOG_FILE.exists():
        return []
    out: List[Dict] = []
    try:
        with LOG_FILE.open("r", encoding="utf-8") as f:
            for raw in f:
                raw = raw.strip()
                if not raw:
                    continue
                try:
                    rec = json.loads(raw)
                except ValueError:
                    continue
                if isinstance(rec, dict) and "date" in rec:
                    out.append(rec)
    except OSError:
        pass
    return out


def _write_day(records: List[Dict]) -> None:
    """Rewrite the whole file with `records`. Cheap because the file
    is one line per local day — even a year of use is < 400 lines."""
    try:
        LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
        tmp = LOG_FILE.with_suffix(".jsonl.tmp")
        with tmp.open("w", encoding="utf-8") as f:
            for rec in records:
                f.write(json.dumps(rec, ensure_ascii=False))
                f.write("\n")
        tmp.replace(LOG_FILE)
    except OSError as e:
        log.warning("daily_loop: log persist failed (%s)", e)


def _today_iso(*, when: Optional[float] = None) -> str:
    if when is None:
        when = time.time()
    return date.fromtimestamp(when).isoformat() if hasattr(date, "fromtimestamp") else (
        datetime.fromtimestamp(when, tz=timezone.utc).date().isoformat()
    )


# --------------------------------------------------------------- counter API


def _bump(bin_name: str, *, when: Optional[float] = None) -> None:
    """Add one to `bin_name` on today's record. Reads + rewrites the
    whole file because it's one line per local day."""
    if not _enabled():
        return
    if bin_name not in _COUNTER_BINS:
        raise ValueError(f"unknown bin: {bin_name}")
    today = _today_iso(when=when)
    records = _read_log()
    found = False
    for rec in records:
        if rec.get("date") == today:
            rec[bin_name] = int(rec.get(bin_name, 0)) + 1
            found = True
            break
    if not found:
        new = {"date": today}
        for b in _COUNTER_BINS:
            new[b] = 1 if b == bin_name else 0
        records.append(new)
    _write_day(records)


def record_day_started() -> None:
    """The user opened the launcher (or the popup made a first
    /v1/health call today). One per day, but idempotency is the
    *caller's* job: this just bumps the counter."""
    _bump("day_started")


def record_investigation_opened() -> None:
    """User clicked an InvestigationCard."""
    _bump("investigations_opened")


def record_recovery_shown() -> None:
    """The launcher rendered a RecoveryCard. One per surface, not
    per render."""
    _bump("recoveries_shown")


def record_recovery_used() -> None:
    """User clicked Resume on a RecoveryCard."""
    _bump("recoveries_used")


def record_resume_success() -> None:
    """The Resume click actually opened the right work (no immediate
    follow-up dismiss / close)."""
    _bump("resume_success")


def record_return(*, gap_seconds: float) -> None:
    """The detector decided the user came back after a gap. Stored
    bin: `returns`. The gap value itself is not stored — counts only."""
    if gap_seconds < RETURN_GAP_MIN_SECONDS:
        return
    _bump("returns")


# --------------------------------------------------------------- return detector


def mark_event(ts_epoch: float) -> Optional[float]:
    """Called by the ingest path on every successful event. If the
    gap since the previous event crosses :data:`RETURN_GAP_MIN_SECONDS`,
    bump the ``returns`` counter and return the gap (so the API can
    log it). Otherwise return ``None``.

    State is persisted at :data:`STATE_FILE` so the detector survives
    process restarts.
    """
    if not _enabled() or ts_epoch <= 0:
        return None
    state = _read_state()
    last = float(state.get("last_event_ts") or 0.0)
    if last <= 0:
        # First event ever — record it but don't count a return.
        state["last_event_ts"] = ts_epoch
        _write_state(state)
        return None
    gap = ts_epoch - last
    state["last_event_ts"] = ts_epoch
    if gap >= RETURN_GAP_MIN_SECONDS:
        state["last_return_ts"] = ts_epoch
        state["last_return_gap_s"] = gap
        _write_state(state)
        record_return(gap_seconds=gap)
        return gap
    _write_state(state)
    return None


# --------------------------------------------------------------- summary


def _empty_record(d: str) -> Dict:
    rec = {"date": d}
    for b in _COUNTER_BINS:
        rec[b] = 0
    return rec


def summary(*, days: int = 7) -> Dict:
    """Aggregate the last `days` records. Returns a flat dict with:

      - ``today``     — today's counters
      - ``yesterday`` — yesterday's counters
      - ``window``    — total over the last `days` days
      - ``signals``   — three derived signals (continuity_restored
        %, return_rate %, resume_quality %) over the window
      - ``green_yellow_red`` — verdict per signal

    Empty days fold in as zeros so the percentage denominators are
    honest (a zero-recovery week reads as "no data", not as a
    division by zero).
    """
    records_by_day = {r["date"]: r for r in _read_log() if "date" in r}
    today = date.today()
    yest = today - timedelta(days=1)

    today_rec = records_by_day.get(today.isoformat()) or _empty_record(today.isoformat())
    yest_rec = records_by_day.get(yest.isoformat()) or _empty_record(yest.isoformat())

    window: Dict[str, int] = {b: 0 for b in _COUNTER_BINS}
    days_with_any = 0
    for offset in range(days):
        d = (today - timedelta(days=offset)).isoformat()
        rec = records_by_day.get(d)
        if not rec:
            continue
        if any(int(rec.get(b, 0)) > 0 for b in _COUNTER_BINS):
            days_with_any += 1
        for b in _COUNTER_BINS:
            window[b] = window[b] + int(rec.get(b, 0))

    def _pct(num: int, den: int) -> Optional[int]:
        return int(round(100.0 * num / den)) if den > 0 else None

    signals = {
        "continuity_restored": _pct(window["recoveries_used"], window["recoveries_shown"]),
        "return_rate": _pct(window["returns"], max(window["day_started"], 1)),
        "resume_quality": _pct(window["resume_success"], window["recoveries_used"]),
    }

    # GREEN / YELLOW / RED thresholds. Documented in DAILY_LOOP.md
    # so the math has a single source of truth.
    def _verdict(name: str, pct: Optional[int]) -> str:
        if pct is None:
            return "YELLOW"  # not enough data; never a hard fail
        if name == "continuity_restored":
            return "GREEN" if pct >= 60 else "YELLOW" if pct >= 25 else "RED"
        if name == "return_rate":
            return "GREEN" if pct >= 30 else "YELLOW" if pct >= 10 else "RED"
        if name == "resume_quality":
            return "GREEN" if pct >= 80 else "YELLOW" if pct >= 50 else "RED"
        return "YELLOW"

    green_yellow_red = {
        name: _verdict(name, pct) for name, pct in signals.items()
    }

    return {
        "today": today_rec,
        "yesterday": yest_rec,
        "window": window,
        "window_days": days,
        "days_with_any_activity": days_with_any,
        "signals": signals,
        "green_yellow_red": green_yellow_red,
    }


__all__ = [
    "LOG_FILE",
    "STATE_FILE",
    "RETURN_GAP_MIN_SECONDS",
    "record_day_started",
    "record_investigation_opened",
    "record_recovery_shown",
    "record_recovery_used",
    "record_resume_success",
    "record_return",
    "mark_event",
    "summary",
]
