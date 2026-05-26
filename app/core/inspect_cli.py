"""Investigation inspector — Phase 6Q.

`recall inspect <id>` prints a deterministic ASCII card describing
exactly why the engine surfaced (or didn't surface) a given
candidate. The `id` argument accepts either:

  - a `RecoveryCandidate.id` (`rc_…`)
  - a `Thread.id` / `topic_key` (a substring match is acceptable
    for one-shot debugging)

The output is the **only** sanctioned tool for asking *"why did
Recall show this?"*. It reads from the engine, never the
launcher, never the API — the launcher is a strict consumer of
the engine; the inspector should be too.

Example output:

    ------------------------------------------------------------
      Investigation
    ------------------------------------------------------------

      Title:
        WebSocket retry debugging

      Strength:
        HIGH

      Signals:
        - returned after a multi-day gap
        - unfinished work
        - multiple surfaces engaged
        - 5 targets involved

      Evidence:
        - 2 tabs
        - 2 files
        - 1 search

      Decision:
        SHOW HERO

    ------------------------------------------------------------
"""

from __future__ import annotations

import logging
from typing import List, Optional, Tuple

from .config import EVENTS_DIR
from .events import EventStore
from .recovery import (
    RecoveryCandidate,
    RecoveryEngine,
    _classify_targets,
    explain_signals,
)

log = logging.getLogger("recall.core.inspect_cli")


# Promotion bands — same as the launcher's HIGH-only gate. Kept
# inline here so `recall inspect` runs without importing Qt.
def _band(candidate: RecoveryCandidate) -> str:
    n = len(candidate.suggested_targets)
    if n >= 4:
        base = "HIGH"
    elif n >= 2:
        base = "MED"
    else:
        base = "LOW"
    # Override 1 — unfinished overrides all.
    if any("went quiet" in u for u in candidate.unresolved_signals):
        base = "HIGH"
    # Override 2 — returned_after_gap boosts +1.
    if "gap" in (candidate.preview_caption or ""):
        if base == "MED":
            base = "HIGH"
        elif base == "LOW":
            base = "MED"
    # Override 5 — ledger penalty.
    s = candidate.signals or {}
    if s.get("ledger_flagged", 0.0) >= 1.0:
        if base == "HIGH":
            base = "MED"
        elif base == "MED":
            base = "LOW"
    return base


def _decision(band: str) -> str:
    return {
        "HIGH": "SHOW HERO",
        "MED": "SHOW IN OTHER WORK",
        "LOW": "SUPPRESS",
    }[band]


def _evidence_lines(candidate: RecoveryCandidate) -> List[str]:
    """Bucket the candidate's targets the same way the resume
    preview does. Output is a stable list of `"N tabs"` strings."""
    groups = _classify_targets(candidate.suggested_targets)
    out: list[str] = []
    if groups["files"]:
        n = len(groups["files"])
        out.append(f"{n} file{'s' if n != 1 else ''}")
    if groups["chats"]:
        n = len(groups["chats"])
        out.append(f"{n} chat{'s' if n != 1 else ''}")
    if groups["tabs"]:
        n = len(groups["tabs"])
        out.append(f"{n} tab{'s' if n != 1 else ''}")
    if groups["searches"]:
        n = len(groups["searches"])
        out.append(f"{n} search{'es' if n != 1 else ''}")
    return out


def _format_card(candidate: RecoveryCandidate) -> str:
    rule = "  " + "-" * 60
    band = _band(candidate)
    signals = explain_signals(candidate)
    evidence = _evidence_lines(candidate)
    out: list[str] = []
    out.append("")
    out.append(rule)
    out.append("    Investigation")
    out.append(rule)
    out.append("")
    out.append("    Title:")
    out.append(f"      {candidate.title or '(untitled)'}")
    out.append("")
    out.append("    Strength:")
    out.append(f"      {band}")
    out.append("")
    out.append("    Signals:")
    if signals:
        for s in signals:
            out.append(f"      - {s}")
    else:
        out.append("      (none — too quiet to score)")
    out.append("")
    out.append("    Evidence:")
    if evidence:
        for e in evidence:
            out.append(f"      - {e}")
    else:
        out.append("      (no openable targets)")
    out.append("")
    out.append("    Decision:")
    out.append(f"      {_decision(band)}")
    out.append("")
    out.append(rule)
    out.append("")
    return "\n".join(out)


def _format_not_found(query: str, near_misses: List[Tuple[str, str]]) -> str:
    rule = "  " + "-" * 60
    out: list[str] = []
    out.append("")
    out.append(rule)
    out.append("    Investigation")
    out.append(rule)
    out.append("")
    out.append(f"    No candidate found for: {query!r}")
    out.append("")
    if near_misses:
        out.append("    Recent candidates you could inspect instead:")
        for cid, title in near_misses[:5]:
            out.append(f"      - {cid}   {title}")
    else:
        out.append("    The engine has no candidates above the trust floor.")
        out.append("    See INVESTIGATION_PRINCIPLES.md for the gate list.")
    out.append("")
    out.append(rule)
    out.append("")
    return "\n".join(out)


def _resolve(
    engine: RecoveryEngine, query: str
) -> Tuple[Optional[RecoveryCandidate], List[Tuple[str, str]]]:
    """Try to resolve `query` to a candidate.

    Tries exact `id` first, then exact `thread_id`, then substring
    on title / topic_key. Returns the candidate (or None) and a
    near-miss list for the not-found message."""
    # The engine caps at 3, but the inspector wants visibility into
    # the full candidate pool. We call `recover_recent(n=3)` and
    # then fall back to a candidate-by-thread scan if the id misses.
    candidates = engine.recover_recent(n=3)
    near: list[Tuple[str, str]] = [(c.id, c.title) for c in candidates]
    q = (query or "").strip()
    if not q:
        return None, near
    for c in candidates:
        if q == c.id or q == c.thread_id:
            return c, near
    for c in candidates:
        if q.lower() in (c.title or "").lower():
            return c, near
    # As a deeper fallback try the threads layer directly — the
    # engine can score one specific thread even if the top-3
    # ranking doesn't include it.
    threads = engine.thread_builder.rebuild()
    for t in threads:
        if q == t.id or q == t.topic_key or q.lower() in (t.title or "").lower():
            cand = engine.candidate_for_thread(t.id)
            if cand is not None:
                return cand, near
    return None, near


def run_inspect_cli(argv: list[str]) -> int:
    """Entry point for `recall inspect <id>`. Returns process exit
    code (0 success, 1 not found, 2 usage error)."""
    if not argv or argv[0] in {"-h", "--help"}:
        print("Usage: recall inspect <candidate_id | thread_id | title-substring>")
        print()
        print("Prints a deterministic ASCII summary of why the engine")
        print("surfaced (or didn't surface) the matching candidate.")
        return 2 if not argv else 0
    query = argv[0]
    store = EventStore(EVENTS_DIR)
    engine = RecoveryEngine(store)
    candidate, near = _resolve(engine, query)
    if candidate is None:
        print(_format_not_found(query, near))
        return 1
    print(_format_card(candidate))
    return 0


__all__ = ["run_inspect_cli"]
