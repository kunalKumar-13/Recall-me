"""Capture truth audit CLI — Phase 7D.

Two read-only commands that confirm Recall is actually
remembering what the user does:

  recall capture status
      ASCII status card: events today (per-kind breakdown),
      returns (30-min-gap reopens), investigation count,
      and the most recent event's timestamp + age.

  recall capture tail
      `tail -f`-style live inspector for the daily JSONL
      file at ``~/.recall/events/YYYY-MM-DD.jsonl``. New
      events print as one short line each as they land,
      so the user can watch the pipeline land events in
      real time.

Both commands are local-only — they read ``~/.recall/`` and
never touch the network. Neither requires the daemon to be
running; both work straight off the event log on disk.

The CLIs are dispatched from ``recall.py``'s fast path before
``app.main`` imports so they're cheap even without Qt.
"""

from __future__ import annotations

import logging
import sys
import time
from datetime import datetime, timezone
from typing import Iterable, Optional, Tuple

from .config import EVENTS_DIR
from .events import Event, EventStore, humanize_age, _loads, _JSON_DECODE_ERRORS

log = logging.getLogger("recall.core.capture_cli")


_RULE = "  " + "-" * 60


# ── status ────────────────────────────────────────────────────────


# Each row in the status table maps a `kind` to the human label the
# capture audit displays. Keeping this in one place means a future
# event kind (e.g. `paste`, `clipboard`) gains a row by editing one
# tuple.
_KIND_TABLE: Tuple[Tuple[str, str], ...] = (
    ("browser_visit",   "tabs"),
    ("browser_search",  "searches"),
    ("chat_session",    "chats"),
    ("open",            "files (open)"),
    ("reveal",          "files (reveal)"),
    ("desktop_window",  "desktop"),
    ("query",           "launcher queries"),
)


def _today_filename(now: Optional[float] = None) -> str:
    ts = datetime.fromtimestamp(now if now is not None else time.time(), tz=timezone.utc)
    return ts.strftime("%Y-%m-%d") + ".jsonl"


def _today_events(store: EventStore) -> Iterable[Event]:
    """Yield only today's events from the per-day log."""
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    yield from store.iter_events_for_date(today)


def _count_returns_today(store: EventStore) -> int:
    """Count gap-crossings >= 30 minutes today. Mirrors what
    ``daily_loop.mark_event`` would record at ingest, computed
    from the event log directly so the status surface works
    even when the daemon (and its `daily_loop` write path)
    isn't running."""
    SESSION_GAP_SECONDS = 30 * 60
    events = list(_today_events(store))
    if len(events) < 2:
        return 0
    # `iter_events_for_date` yields chronological order.
    returns = 0
    for prev, cur in zip(events, events[1:]):
        gap = cur.ts_epoch() - prev.ts_epoch()
        if gap >= SESSION_GAP_SECONDS:
            returns += 1
    return returns


def _last_event(store: EventStore) -> Optional[Event]:
    """The most recent event in the last 7 days. `iter_events`
    yields newest-first, so the first yield is the answer."""
    for ev in store.iter_events(days=7):
        return ev
    return None


def _investigation_count() -> int:
    """Cached thread count without booting the engine. Returns 0
    when the threads cache isn't on disk yet (a fresh install or
    a paused engine)."""
    try:
        from .config import CONFIG_DIR
        import json
        path = CONFIG_DIR / "threads.json"
        if not path.exists():
            return 0
        data = json.loads(path.read_text(encoding="utf-8"))
        threads = data.get("threads") or []
        return len(threads)
    except (OSError, ValueError, TypeError):
        return 0


def _format_status() -> str:
    store = EventStore(EVENTS_DIR)
    today = list(_today_events(store))

    # Per-kind tally for today.
    tally: dict[str, int] = {kind: 0 for kind, _ in _KIND_TABLE}
    other = 0
    for ev in today:
        if ev.kind in tally:
            tally[ev.kind] += 1
        else:
            other += 1

    total_today = sum(tally.values()) + other
    returns_today = _count_returns_today(store)
    investigations = _investigation_count()
    last = _last_event(store)

    out: list[str] = []
    out.append("")
    out.append(_RULE)
    out.append("    Capture status - today")
    out.append(_RULE)
    out.append("")
    out.append(f"    events today        {total_today}")
    for kind, label in _KIND_TABLE:
        if tally[kind] == 0:
            continue
        out.append(f"      {label:<18} {tally[kind]:>4}  ({kind})")
    if other:
        out.append(f"      other              {other:>4}")
    out.append("")
    out.append(f"    returns (>= 30 min gap)   {returns_today}")
    out.append(f"    investigations            {investigations}")
    if last is None:
        out.append("    last event                (none captured yet)")
    else:
        ts = datetime.fromtimestamp(last.ts_epoch(), tz=timezone.utc)
        age = humanize_age(last.ts_epoch())
        out.append(
            f"    last event                {ts.strftime('%H:%M:%S')} UTC  ({age})"
        )
        out.append(f"                              kind = {last.kind}")
    out.append("")
    if total_today == 0:
        out.append("    No events captured today.")
        out.append("    - Is the daemon running?    `python recall.py`")
        out.append("    - Is the extension paired?  open chrome://extensions")
        out.append("    - Or run the demo:          press *Show example*")
        out.append("")
    out.append(_RULE)
    out.append("")
    return "\n".join(out)


# ── tail ──────────────────────────────────────────────────────────


def _format_event_line(ev: Event) -> str:
    """One compact, scannable line per event for the tail view."""
    ts = datetime.fromtimestamp(ev.ts_epoch(), tz=timezone.utc)
    payload = ev.payload or {}
    # Pick a *short* description appropriate for the kind.
    if ev.kind == "browser_visit":
        detail = str(payload.get("domain") or payload.get("url") or "")
        title = str(payload.get("title") or "")
    elif ev.kind == "browser_search":
        detail = str(payload.get("engine") or payload.get("domain") or "")
        title = str(payload.get("query") or "")
    elif ev.kind == "chat_session":
        detail = str(payload.get("platform") or payload.get("domain") or "")
        title = str(payload.get("title") or "")
    elif ev.kind in ("open", "reveal"):
        path = str(payload.get("path") or "")
        detail = "file"
        title = path.rsplit("/", 1)[-1].rsplit("\\", 1)[-1] or path
    elif ev.kind == "desktop_window":
        detail = str(payload.get("app") or "")
        title = str(payload.get("title") or "")
    elif ev.kind == "query":
        detail = "launcher"
        title = str(payload.get("text") or "")
    else:
        detail = ""
        title = ""
    title = title[:64]
    detail = detail[:24]
    return (
        f"  {ts.strftime('%H:%M:%S')}  "
        f"{ev.kind:<14}  {detail:<22}  {title}"
    )


def _parse_jsonl_line(line: str) -> Optional[Event]:
    line = line.strip()
    if not line:
        return None
    try:
        d = _loads(line)
    except _JSON_DECODE_ERRORS:
        return None
    if not isinstance(d, dict):
        return None
    try:
        return Event(
            ts=str(d.get("ts", "")),
            session_id=str(d.get("session_id", "")),
            kind=str(d.get("kind", "")),
            payload=dict(d.get("payload") or {}),
        )
    except (TypeError, ValueError):
        return None


def _run_tail(follow: bool = True) -> int:
    """Print every existing event in today's file, then stream
    new lines as they're appended. Ctrl+C exits cleanly."""
    today_path = EVENTS_DIR / _today_filename()
    print("")
    print(_RULE)
    print("    Capture tail")
    print(_RULE)
    print(f"    watching {today_path}")
    print("")

    pos = 0
    if today_path.exists():
        try:
            with today_path.open("rb") as f:
                # Stream existing contents first so the user sees
                # context, then keep reading from EOF onward.
                for raw in f:
                    ev = _parse_jsonl_line(raw.decode("utf-8", errors="replace"))
                    if ev is not None:
                        print(_format_event_line(ev))
                pos = f.tell()
        except OSError as exc:
            print(f"  error reading log: {exc}")
            return 1

    if not follow:
        print("")
        return 0

    print("")
    print("  (waiting for new events - Ctrl+C to exit)")
    print("")
    try:
        while True:
            time.sleep(0.5)
            # New files may have rolled over to tomorrow; reopen
            # by date on every tick so the tail survives midnight.
            current_path = EVENTS_DIR / _today_filename()
            if current_path != today_path:
                today_path = current_path
                pos = 0
                if today_path.exists():
                    pos = today_path.stat().st_size
                print(f"  -- rolled to {today_path.name}")
                continue
            if not today_path.exists():
                continue
            try:
                size = today_path.stat().st_size
            except OSError:
                continue
            if size < pos:
                # File truncated or rotated under us. Restart from 0.
                pos = 0
            if size == pos:
                continue
            try:
                with today_path.open("rb") as f:
                    f.seek(pos)
                    chunk = f.read()
                    pos = f.tell()
            except OSError:
                continue
            for raw in chunk.splitlines():
                ev = _parse_jsonl_line(raw.decode("utf-8", errors="replace"))
                if ev is not None:
                    print(_format_event_line(ev), flush=True)
    except KeyboardInterrupt:
        print("")
        return 0


# ── entry point ───────────────────────────────────────────────────


def run_capture_cli(argv: list[str]) -> int:
    """Entry point for ``recall capture <subcommand>``.

    Subcommands:
      status            print today's capture summary
      tail              `tail -f` the daily event log
      tail --once       print existing events then exit
    """
    if not argv or argv[0] in {"-h", "--help"}:
        print("Usage: recall capture <status | tail [--once]>")
        print()
        print("  status     ASCII capture summary (read-only).")
        print("  tail       Live inspector. Ctrl+C exits.")
        print("  tail --once  Print existing events then exit.")
        return 2 if not argv else 0
    sub = argv[0]
    if sub == "status":
        sys.stdout.write(_format_status())
        sys.stdout.flush()
        return 0
    if sub == "tail":
        follow = "--once" not in argv[1:]
        return _run_tail(follow=follow)
    print(f"unknown subcommand: {sub}")
    return 2


__all__ = ["run_capture_cli"]
