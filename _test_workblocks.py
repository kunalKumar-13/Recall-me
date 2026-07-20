"""Deterministic tests for the pure work-blocks derivation (Capture C5).

Run: python _test_workblocks.py

No daemon, no disk, no clock — `workblocks` is a pure function of the
event timestamps and captured dwell spans, which is exactly why the
riskiest continuity logic is verifiable in isolation.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

from app.core.events import Event
from app.core.workblocks import (
    BEHAVIOURAL_IDLE_SECONDS,
    describe_blocks,
    group_work_blocks,
)

_BASE = datetime(2026, 7, 20, 9, 0, 0, tzinfo=timezone.utc)

n = 0


def ok(msg: str) -> None:
    global n
    n += 1
    print(f"  [ok] {msg}")


def ev(offset_s: float, kind: str = "browser_visit", **payload) -> Event:
    """An event `offset_s` seconds after the base moment."""
    ts = (_BASE + timedelta(seconds=offset_s)).strftime("%Y-%m-%dT%H:%M:%SZ")
    return Event(ts=ts, session_id="s_test", kind=kind, payload=payload)


# --- empty + trivial ---------------------------------------------------
assert group_work_blocks([]) == []
assert describe_blocks([]) == ""
ok("empty stream → no blocks, no description")

single = [ev(0), ev(60), ev(120)]
blocks = group_work_blocks(single)
assert len(blocks) == 1, blocks
# a single block with no dwell signal stays quiet — the clock label covers it
assert describe_blocks(blocks) == ""
ok("tight clicks with no dwell → one block, no clause")

# --- the split the clock can't see -------------------------------------
# Two five-minute bursts 15 minutes apart. The 30-minute clock lumps
# them into ONE session; behaviourally they're two attention islands.
scattered = [
    ev(0), ev(120), ev(240),                       # burst 1  (0–4 min)
    ev(240 + 15 * 60), ev(240 + 15 * 60 + 120),    # burst 2, 15-min gap
]
blocks = group_work_blocks(scattered)
assert len(blocks) == 2, f"expected 2 blocks, got {len(blocks)}"
assert len(blocks[0]) == 3 and len(blocks[1]) == 2
ok("15-min silence inside one clock session → two work-blocks")

# --- dwell bridges a gap the idle rule would split ---------------------
# A gap longer than the idle threshold, but a dwell event whose span
# reaches back across it — the user was present the whole time.
gap = BEHAVIOURAL_IDLE_SECONDS + 120        # over the idle threshold
bridged = [
    ev(0),
    ev(gap, kind="browser_focus", dwell_ms=(gap + 30) * 1000, block="wb-1"),
]
blocks = group_work_blocks(bridged)
assert len(blocks) == 1, f"dwell should bridge the gap, got {len(blocks)}"
ok("long gap covered by a dwell span → stays one block")

# a dwell too short to bridge does NOT rescue the gap
not_bridged = [
    ev(0),
    ev(gap, kind="browser_focus", dwell_ms=9000, block="wb-1"),
]
assert len(group_work_blocks(not_bridged)) == 2
ok("sub-threshold dwell across a long gap → two blocks")

# --- shared extension block id bridges ---------------------------------
same_block = [
    ev(0, kind="browser_focus", dwell_ms=30000, block="wb-9"),
    ev(gap, kind="browser_focus", dwell_ms=9000, block="wb-9"),
]
assert len(group_work_blocks(same_block)) == 1
ok("same extension work-block id bridges a long gap")

# --- order independence ------------------------------------------------
shuffled = [scattered[3], scattered[0], scattered[4], scattered[2], scattered[1]]
assert len(group_work_blocks(shuffled)) == 2
ok("result is independent of input order (stable sort)")

# --- descriptions ------------------------------------------------------
focus_hour = [
    ev(0, kind="browser_focus", dwell_ms=47 * 60 * 1000, block="wb-1"),
]
assert describe_blocks(group_work_blocks(focus_hour)) == "one 47-minute focus block"
ok("single long dwell → 'one 47-minute focus block'")

multi = group_work_blocks([
    ev(0, kind="browser_focus", dwell_ms=20 * 60 * 1000, block="wb-1"),
    ev(240 + 15 * 60, kind="browser_focus", dwell_ms=15 * 60 * 1000, block="wb-2"),
    ev(240 + 40 * 60, kind="browser_focus", dwell_ms=10 * 60 * 1000, block="wb-3"),
])
desc = describe_blocks(multi)
assert desc.startswith("3 attention blocks"), desc
assert "focused" in desc
ok(f"three blocks with dwell → '{desc}'")

print(f"\n{n} work-block checks passed")
