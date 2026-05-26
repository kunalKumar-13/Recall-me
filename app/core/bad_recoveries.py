"""Wrong-recovery ledger — Phase 6Q.

A purely additive layer the launcher writes into when the user
marks a recovery wrong. The ledger lives at
``~/.recall/bad_recoveries.jsonl`` as a JSON-lines file the user
can read with ``cat``.

Three things consume it:

  1. ``recovery.py`` — when a recovery candidate's `thread_id`
     appears in the ledger within the last `_LEDGER_WINDOW_DAYS`,
     its promotion band is demoted one step (HIGH → MED, MED →
     LOW). The override is documented in
     ``docs/product/PROMOTION_THRESHOLDS.md``.
  2. ``recall trust review`` CLI — prints bad % / silence % /
     resume % across the lifetime of the install.
  3. ``app/core/stats.py`` (future hook) — could expose the
     ledger summary in the founder dashboard. Not wired yet.

Determinism: same writes in → same file out (every line is
self-describing). The ledger is *append-only*; we never edit or
delete past entries. A user who wants to forget can `rm` the file
— same contract as every other piece of ``~/.recall/`` state.

Trust contract:

  - **No content.** The ledger stores `thread_id` (a stable
    derived id), `reason` (one of four enums), and `ts` (epoch
    seconds). Never a filename, URL, query, or chat content.
  - **Local-only.** Nothing about the ledger leaves the machine.
  - **Inspectable.** Plain JSONL.

All four ``reason`` values are an explicit closed set; the
launcher's *Wrong recovery* button can only submit one of them:

  - ``wrong_topic``  — *this isn't what I was working on*
  - ``already_done`` — *I'm finished with this*
  - ``noise``        — *too many false-positive surfaces*
  - ``duplicate``    — *I already have this open*
"""

from __future__ import annotations

import json
import logging
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Literal, Optional

from .config import CONFIG_DIR

log = logging.getLogger("recall.core.bad_recoveries")


# The four reasons the launcher's *Wrong recovery* button submits.
# Closed set — any other value is rejected at write time.
ReasonKind = Literal[
    "wrong_topic",
    "already_done",
    "noise",
    "duplicate",
]

_ALLOWED_REASONS: frozenset[str] = frozenset({
    "wrong_topic",
    "already_done",
    "noise",
    "duplicate",
})


LEDGER_PATH: Path = CONFIG_DIR / "bad_recoveries.jsonl"


# How far back the ranking demotion looks. The directive sets this
# to 14 days — short enough that a stale false positive disappears
# once the engine improves, long enough that a topic the user
# *clearly* doesn't want back stays suppressed.
_LEDGER_WINDOW_DAYS: float = 14.0


@dataclass(frozen=True)
class BadRecovery:
    """One ledger line — see the module docstring for trust rules."""

    id: str              # `RecoveryCandidate.id` at the time of the report
    thread_id: str       # `RecoveryCandidate.thread_id` — the ranking key
    reason: ReasonKind
    ts: float            # epoch seconds

    @classmethod
    def from_dict(cls, d: dict) -> Optional["BadRecovery"]:
        reason = d.get("reason")
        if reason not in _ALLOWED_REASONS:
            return None
        try:
            return cls(
                id=str(d.get("id") or ""),
                thread_id=str(d.get("thread_id") or ""),
                reason=reason,  # type: ignore[arg-type]
                ts=float(d.get("ts") or 0.0),
            )
        except (TypeError, ValueError):
            return None

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "thread_id": self.thread_id,
            "reason": self.reason,
            "ts": self.ts,
        }


# ── writes ───────────────────────────────────────────────────────


def record(
    candidate_id: str,
    thread_id: str,
    reason: str,
    *,
    now: Optional[float] = None,
    path: Optional[Path] = None,
) -> bool:
    """Append one entry to the ledger. Returns True on success.

    The launcher calls this from the *Wrong recovery* button. The
    function never raises — a disk-full or permission-denied state
    becomes `False` so the launcher's caller can flash a calm
    message rather than crash.
    """
    if reason not in _ALLOWED_REASONS:
        log.warning("bad_recoveries.record: rejected reason %r", reason)
        return False
    entry = BadRecovery(
        id=(candidate_id or "").strip(),
        thread_id=(thread_id or "").strip(),
        reason=reason,  # type: ignore[arg-type]
        ts=float(now if now is not None else time.time()),
    )
    target = path or LEDGER_PATH
    try:
        target.parent.mkdir(parents=True, exist_ok=True)
        with target.open("a", encoding="utf-8") as f:
            f.write(json.dumps(entry.to_dict(), ensure_ascii=False) + "\n")
        return True
    except OSError as exc:
        log.warning("bad_recoveries.record: write failed (%s)", exc)
        return False


# ── reads ────────────────────────────────────────────────────────


def load_all(path: Optional[Path] = None) -> List[BadRecovery]:
    """Read every ledger line, dropping malformed rows silently
    (the file is hand-editable; a stray edit must not crash the
    engine)."""
    target = path or LEDGER_PATH
    if not target.exists():
        return []
    out: list[BadRecovery] = []
    try:
        with target.open("r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    raw = json.loads(line)
                except (json.JSONDecodeError, UnicodeDecodeError):
                    continue
                entry = BadRecovery.from_dict(raw)
                if entry is not None:
                    out.append(entry)
    except OSError as exc:
        log.warning("bad_recoveries.load_all: read failed (%s)", exc)
        return []
    return out


def thread_is_flagged(
    thread_id: str,
    *,
    now: Optional[float] = None,
    path: Optional[Path] = None,
) -> bool:
    """True iff `thread_id` carries a ledger entry within
    `_LEDGER_WINDOW_DAYS`. The engine's ranking demotion (Override
    5 in PROMOTION_THRESHOLDS.md) consults this."""
    if not thread_id:
        return False
    cutoff = (now if now is not None else time.time()) - _LEDGER_WINDOW_DAYS * 86400
    for entry in load_all(path):
        if entry.thread_id == thread_id and entry.ts >= cutoff:
            return True
    return False


def counts_by_reason(
    *,
    now: Optional[float] = None,
    window_days: Optional[float] = None,
    path: Optional[Path] = None,
) -> Dict[str, int]:
    """Aggregate ledger counts by reason. `window_days = None`
    counts the whole ledger; otherwise restricts to entries within
    the window. Returned dict always carries all four reason keys
    (zero-filled when absent) so consumers can render a stable
    table."""
    out: Dict[str, int] = {r: 0 for r in _ALLOWED_REASONS}
    if window_days is not None:
        cutoff = (now if now is not None else time.time()) - window_days * 86400
    else:
        cutoff = float("-inf")
    for entry in load_all(path):
        if entry.ts < cutoff:
            continue
        out[entry.reason] = out.get(entry.reason, 0) + 1
    return out


def total(
    *,
    now: Optional[float] = None,
    window_days: Optional[float] = None,
    path: Optional[Path] = None,
) -> int:
    """Total ledger entries in the window."""
    return sum(counts_by_reason(now=now, window_days=window_days, path=path).values())


__all__ = [
    "BadRecovery",
    "LEDGER_PATH",
    "ReasonKind",
    "counts_by_reason",
    "load_all",
    "record",
    "thread_is_flagged",
    "total",
]
