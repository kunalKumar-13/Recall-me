"""Local stats — Phase 5E.1 (Local Observability).

`recall stats` prints a **counts-only** health summary computed
entirely from local state in `~/.recall/`. `recall stats --export`
writes an anonymous `stats.json` the user may *choose* to share
with the founder dashboard.

This is the opt-in, no-telemetry input to the operator dashboard:

  • nothing here runs in the background — the user runs it by hand;
  • nothing is uploaded — `--export` writes a file, the user decides
    what to do with it;
  • nothing here is content — never a filename, URL, query, or
    title. Only counts, day-granularity, and derived rates.

What can leave the machine is exactly what `build_export()`
produces, and nothing else. The boundary is enumerated in
`TRUST_LEDGER.md`.
"""

from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Optional

from .config import CONFIG_DIR, EVENTS_DIR
from .events import EventStore

log = logging.getLogger("recall.core.stats")

# Counter file — UI interactions the event log does not capture
# (a recovery being *shown*, a Resume being *clicked*). Distinct
# from the export file, which is named `stats.json`.
_COUNTERS_PATH: Path = CONFIG_DIR / "counters.json"

# The interaction counters the launcher bumps. Counts only.
_COUNTER_KEYS = (
    "recovery_shown",
    "recovery_accepted",
    "resume_ok",
    "resume_fail",
    "resurface_opened",
)

_BROWSER_KINDS = frozenset({"browser_visit", "browser_search", "chat_session"})
_FILE_KINDS = frozenset({"open", "reveal"})

# Lookback for the event scan. Wide enough to cover an install's
# whole life without being unbounded.
_LOOKBACK_DAYS = 400


# --------------------------------------------------------------- counters


class StatsCounters:
    """A tiny JSON-backed counter store at `~/.recall/counters.json`.

    Phase 5B — counters are **date-bucketed**:

        { "2026-05-20": {"recovery_shown": 3, ...},
          "2026-05-19": {"recovery_shown": 1, ...}, ... }

    `bump()` writes to today's bucket; `snapshot()` sums across
    every bucket (cumulative — what `compute_stats` uses); `today()`
    returns just today's bucket (what `compute_today` uses for the
    local-only daily continuity score). A pre-5B flat counters file
    is read as a single legacy bucket so no count is lost.

    Like `EventLogger`, never raises — a missing or corrupt counter
    file degrades to zeroes, never to a crash.
    """

    _LEGACY_KEY = "_pre_5b"

    def __init__(self, path: Optional[Path] = None) -> None:
        self.path = path or _COUNTERS_PATH

    def _read(self) -> Dict[str, Dict[str, int]]:
        try:
            data = json.loads(self.path.read_text(encoding="utf-8"))
        except (OSError, ValueError, TypeError):
            return {}
        if not isinstance(data, dict):
            return {}
        # Pre-5B format: a flat {key: count} dict. Wrap it as a
        # single legacy bucket so the count is preserved.
        if any(k in data for k in _COUNTER_KEYS):
            return {self._LEGACY_KEY: {
                k: int(data.get(k, 0) or 0) for k in _COUNTER_KEYS
            }}
        # New format: {date: {key: count}}.
        out: Dict[str, Dict[str, int]] = {}
        for date, bucket in data.items():
            if not isinstance(bucket, dict):
                continue
            out[date] = {
                k: int(bucket.get(k, 0) or 0) for k in _COUNTER_KEYS
            }
        return out

    def _write(self, buckets: Dict[str, Dict[str, int]]) -> None:
        try:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            self.path.write_text(
                json.dumps(buckets, indent=2, sort_keys=True) + "\n",
                encoding="utf-8",
            )
        except (OSError, ValueError):
            pass

    @staticmethod
    def _today_key() -> str:
        return datetime.now(timezone.utc).strftime("%Y-%m-%d")

    def snapshot(self) -> Dict[str, int]:
        """Sum across every date bucket — the cumulative view."""
        totals = {k: 0 for k in _COUNTER_KEYS}
        for bucket in self._read().values():
            for k in _COUNTER_KEYS:
                totals[k] += int(bucket.get(k, 0) or 0)
        return totals

    def today(self) -> Dict[str, int]:
        """Just today's bucket — never exported (Phase 5B daily score)."""
        return self._read().get(self._today_key(), {k: 0 for k in _COUNTER_KEYS})

    def bump(self, key: str, n: int = 1) -> None:
        """Increment a counter in today's bucket. Silent on failure."""
        if key not in _COUNTER_KEYS:
            return
        try:
            buckets = self._read()
            d = self._today_key()
            bucket = buckets.get(d) or {k: 0 for k in _COUNTER_KEYS}
            bucket[key] = bucket.get(key, 0) + int(n)
            buckets[d] = bucket
            self._write(buckets)
        except (OSError, ValueError):
            pass


# --------------------------------------------------------------- compute


def compute_stats(
    now: Optional[float] = None,
    event_store: Optional[EventStore] = None,
    counters: Optional[StatsCounters] = None,
) -> Dict[str, object]:
    """Build the counts-only stats dict from local state.

    Deterministic w.r.t. the event log + counters. Never reads,
    records, or returns any event *content*.
    """
    if now is None:
        now = datetime.now(timezone.utc).timestamp()
    store = event_store or EventStore(EVENTS_DIR)
    ctr = (counters or StatsCounters()).snapshot()

    events_total = 0
    browser_events = 0
    files_opened = 0
    earliest = None
    active_days: set[str] = set()
    active_weeks: set[str] = set()
    extension_days: set[str] = set()

    for ev in store.iter_events(days=_LOOKBACK_DAYS):
        ts = ev.ts_epoch()
        if ts <= 0:
            continue
        events_total += 1
        if earliest is None or ts < earliest:
            earliest = ts
        d = datetime.fromtimestamp(ts, timezone.utc).date()
        active_days.add(d.isoformat())
        iso = d.isocalendar()
        active_weeks.add(f"{iso[0]}-W{iso[1]:02d}")
        if ev.kind in _BROWSER_KINDS:
            browser_events += 1
            extension_days.add(d.isoformat())
        elif ev.kind in _FILE_KINDS:
            files_opened += 1

    install_age_days = (
        int((now - earliest) / 86400.0) if earliest is not None else 0
    )

    # Investigations — the thread count, via the same builder the
    # launcher uses. Imported lazily so `recall stats` stays light.
    try:
        from .threads import ThreadBuilder

        investigations_total = len(ThreadBuilder(store).rebuild(now=now))
    except Exception:  # pragma: no cover - defensive
        investigations_total = 0

    accepted = ctr["recovery_accepted"]
    resume_total = ctr["resume_ok"] + ctr["resume_fail"]
    resume_success_rate = (
        round(ctr["resume_ok"] / resume_total, 3) if resume_total else 0.0
    )

    return {
        "install_age_days": install_age_days,
        "events_total": events_total,
        "investigations_total": investigations_total,
        "recoveries_shown": ctr["recovery_shown"],
        "recoveries_accepted": accepted,
        "resurface_opened": ctr["resurface_opened"],
        "extension_connected_days": len(extension_days),
        "browser_events": browser_events,
        "files_opened": files_opened,
        "resume_success_rate": resume_success_rate,
        "daily_active_days": len(active_days),
        "weekly_active_days": len(active_weeks),
    }


# --------------------------------------------------------------- daily score
#
# Phase 5B — a *local-only* continuity score. Computed on demand,
# shown only to the user, never folded into `build_export()`. It is
# the answer to "did Recall help me return today?" — kept private so
# it never becomes a productivity metric for someone else to watch.


def compute_today(
    counters: Optional[StatsCounters] = None,
) -> Dict[str, object]:
    """Today's continuity score. Local-only — never exported."""
    bucket = (counters or StatsCounters()).today()
    shown = int(bucket.get("recovery_shown", 0))
    accepted = int(bucket.get("recovery_accepted", 0))
    ok = int(bucket.get("resume_ok", 0))
    fail = int(bucket.get("resume_fail", 0))
    resurface = int(bucket.get("resurface_opened", 0))

    restored_pct = round(ok / shown, 3) if shown else 0.0
    success_rate = round(ok / (ok + fail), 3) if (ok + fail) else 0.0

    return {
        "recoveries_shown_today": shown,
        "recoveries_accepted_today": accepted,
        "resurface_opened_today": resurface,
        "interrupted_work_recovered": ok,
        "continuity_restored_pct": restored_pct,
        "resume_success_rate_today": success_rate,
    }


# --------------------------------------------------------------- export


def build_export(
    stats: Dict[str, object], recall_version: str = "0.1.0"
) -> Dict[str, object]:
    """The anonymous aggregate the user may choose to share.

    Counts and rates only. No identifiers, no device id, no hashes,
    no path or content of any kind, and no timestamp finer than the
    day. This dict is the *entire* exportable surface — if a field
    is not here, it does not leave the machine.
    """
    return {
        "schema": "recall.stats/1",
        "recall_version": recall_version,
        "exported_on": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
        "metrics": dict(stats),
    }


# --------------------------------------------------------------- cli


_LABELS = {
    "install_age_days": "Install age (days)",
    "events_total": "Events captured",
    "investigations_total": "Investigations",
    "recoveries_shown": "Recoveries shown",
    "recoveries_accepted": "Recoveries accepted",
    "resurface_opened": "Resurface opened",
    "extension_connected_days": "Extension-connected days",
    "browser_events": "Browser events",
    "files_opened": "Files opened",
    "resume_success_rate": "Resume success rate",
    "daily_active_days": "Daily-active days",
    "weekly_active_days": "Weekly-active weeks",
}


def format_report(stats: Dict[str, object]) -> str:
    """Human-readable `recall stats` output. Calm, aligned, counts."""
    width = max(len(v) for v in _LABELS.values())
    lines = ["", "  Recall - local stats  (counts only, never content)", ""]
    for key, label in _LABELS.items():
        val = stats.get(key, 0)
        if key == "resume_success_rate":
            val = f"{float(val) * 100:.0f}%" if val else "-"
        lines.append(f"    {label.rjust(width)}   {val}")
    lines.append("")
    lines.append("  Share these numbers? `recall stats --export` writes")
    lines.append("  stats.json - anonymous, counts only. Nothing is sent.")
    lines.append("")
    return "\n".join(lines)


def format_today_report(today: Dict[str, object]) -> str:
    """Today's continuity score, shown only to the user."""
    shown = int(today.get("recoveries_shown_today", 0))
    accepted = int(today.get("recoveries_accepted_today", 0))
    recovered = int(today.get("interrupted_work_recovered", 0))
    restored = float(today.get("continuity_restored_pct", 0.0))
    success = float(today.get("resume_success_rate_today", 0.0))
    resurface = int(today.get("resurface_opened_today", 0))

    def pct(v: float) -> str:
        return f"{v * 100:.0f}%" if v else "-"

    lines = [
        "",
        "  Recall - today  (local only, never exported)",
        "",
        f"    Recoveries shown            {shown}",
        f"    Recoveries accepted         {accepted}",
        f"    Interrupted work recovered  {recovered}",
        f"    Resurface opened            {resurface}",
        f"    Continuity restored         {pct(restored)}",
        f"    Resume success rate         {pct(success)}",
        "",
        "  These numbers are computed from today's bucket only and",
        "  are not part of `recall stats --export` - they stay here.",
        "",
    ]
    return "\n".join(lines)


def run_stats_cli(argv: list[str]) -> int:
    """Entry point for `recall stats [--today | --export [PATH]]`.

    Read-only and fast: it touches the event log + caches and
    nothing else. Returns a process exit code.
    """
    if "--today" in argv:
        print(format_today_report(compute_today()))
        return 0

    stats = compute_stats()

    if "--export" in argv:
        # Optional explicit path after --export; default ./stats.json.
        idx = argv.index("--export")
        rest = [a for a in argv[idx + 1:] if not a.startswith("-")]
        out = Path(rest[0]) if rest else Path("stats.json")
        try:
            version = "0.1.0"
            try:
                from app import __version__ as version  # type: ignore
            except Exception:
                pass
            payload = build_export(stats, recall_version=version)
            out.write_text(
                json.dumps(payload, indent=2) + "\n", encoding="utf-8"
            )
        except OSError as e:
            print(f"  could not write {out}: {e}")
            return 1
        print(f"  wrote {out}  (anonymous aggregate — counts only)")
        return 0

    print(format_report(stats))
    return 0
