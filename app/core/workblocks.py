"""Work-blocks — behavioural grouping of a session's events (Capture C5).

The `session` layer groups events by a 30-minute *clock* gap, stamped
at capture time. That's a good first cut, but the clock lies in two
directions: it **over-merges** two scattered five-minute bursts that
happened to fall inside one half-hour window, and it can't tell an
hour of unbroken focus from an hour with the tab left open.

The browser extension already captures the missing signal: every
`browser_focus` event carries how long attention actually stayed on a
page (`dwell_ms`) and a work-block id (`block`, `wb-<epoch>`) that the
extension derived from focus runs and five-minute silences. This
module reads that signal back and regroups a session's events into
*work-blocks* — periods of continuous attention.

Design rules (charter):

  • **Deterministic.** Same events in → same blocks out. No clocks
    read here, no randomness; every boundary is a pure function of
    the event timestamps and the captured dwell spans.
  • **Additive.** This never touches `session_id` or the events on
    disk. It's a read-time derivation the session layer *describes*
    with; delete this file and sessions still reconstruct.
  • **Honest when the signal is absent.** With no `browser_focus`
    events (a day of pure clicks), it falls back to a plain idle-gap
    split — still useful, never wrong.

The one number this earns: a session that reads "one 47-minute focus
block" is a very different memory from one that reads "four scattered
blocks across the afternoon", and only attention can tell them apart.
"""

from __future__ import annotations

from typing import List

from .events import Event

# A behavioural boundary is shorter than the 30-minute clock session:
# ten minutes of true silence (no event, no dwell bridging it) ends a
# work-block. Deliberately below SESSION_GAP_SECONDS so a single clock
# session can still split into several attention blocks.
BEHAVIOURAL_IDLE_SECONDS = 10 * 60

# A dwell shorter than this doesn't count as attention that can bridge
# a gap — it's passing through, matching the extension's own floor.
_MIN_BRIDGE_DWELL_MS = 8_000


def _dwell_span_start(ev: Event) -> float | None:
    """For a `browser_focus` event, the epoch second attention began —
    i.e. `ts - dwell_ms`. The event lands when focus *leaves* a page,
    so its dwell reaches backward in time and can bridge a preceding
    gap. Returns None for any event without a usable dwell."""
    if ev.kind != "browser_focus":
        return None
    dwell = ev.payload.get("dwell_ms")
    if not isinstance(dwell, (int, float)) or dwell < _MIN_BRIDGE_DWELL_MS:
        return None
    return ev.ts_epoch() - (dwell / 1000.0)


def _block_hint(ev: Event) -> str | None:
    if ev.kind != "browser_focus":
        return None
    block = ev.payload.get("block")
    return block if isinstance(block, str) and block else None


def group_work_blocks(
    events: List[Event],
    *,
    idle_gap_s: float = BEHAVIOURAL_IDLE_SECONDS,
) -> List[List[Event]]:
    """Split a chronological event list into behavioural work-blocks.

    A new block starts when the gap from the previous event exceeds
    `idle_gap_s` **and** nothing bridges it. Two things bridge a gap:

      1. This event is a dwell whose attention span (`ts - dwell_ms`)
         reaches back to the previous event — the user was present the
         whole time.
      2. This and the previous browser-focus event share the same
         extension work-block id — the extension already judged them
         one continuous run.

    Input need not be pre-sorted; a stable sort by timestamp is applied
    so the result is order-independent. Empty in → empty out.
    """
    if not events:
        return []

    ordered = sorted(events, key=lambda e: e.ts_epoch())
    blocks: List[List[Event]] = [[ordered[0]]]
    prev_ts = ordered[0].ts_epoch()
    prev_block = _block_hint(ordered[0])

    for ev in ordered[1:]:
        ts = ev.ts_epoch()
        gap = ts - prev_ts

        bridged = False
        if gap <= idle_gap_s:
            bridged = True
        else:
            span_start = _dwell_span_start(ev)
            if span_start is not None and span_start <= prev_ts:
                bridged = True
            else:
                hint = _block_hint(ev)
                if hint is not None and hint == prev_block:
                    bridged = True

        if bridged:
            blocks[-1].append(ev)
        else:
            blocks.append([ev])

        prev_ts = ts
        this_block = _block_hint(ev)
        if this_block is not None:
            prev_block = this_block

    return blocks


def describe_blocks(blocks: List[List[Event]]) -> str:
    """One quiet clause naming a session's attention shape. Empty
    string when there's nothing worth saying (a single trivial block
    with no dwell signal — the clock label already covers it)."""
    n = len(blocks)
    if n == 0:
        return ""

    total_dwell_ms = 0.0
    for blk in blocks:
        for ev in blk:
            dwell = ev.payload.get("dwell_ms")
            if ev.kind == "browser_focus" and isinstance(dwell, (int, float)):
                total_dwell_ms += float(dwell)

    if n == 1:
        if total_dwell_ms >= 60_000:
            return f"one {_mins(total_dwell_ms)} focus block"
        return ""  # single block, no real attention signal — say nothing

    if total_dwell_ms >= 60_000:
        return f"{n} attention blocks · {_mins(total_dwell_ms)} focused"
    return f"{n} attention blocks"


def _mins(ms: float) -> str:
    m = int(round(ms / 60_000.0))
    if m < 1:
        return "under a minute of"
    if m < 60:
        return f"{m}-minute"
    h = m // 60
    rem = m % 60
    return f"{h}h{rem:02d}m" if rem else f"{h}-hour"
