"""Trust CLI — Phase 6Q.

`recall trust review` prints the live ledger of bad recoveries
alongside the resume / silence rates from `StatsCounters`. Three
rates, one ASCII card:

    ------------------------------------------------------------
      Trust review - last 14 days
    ------------------------------------------------------------

      bad recoveries     3
        wrong_topic        2
        already_done       0
        noise              1
        duplicate          0

      bad %               6.5    (3 of 46 shown)
      silence %          21.7    (10 of 46 cleanly suppressed)
      resume %           71.7    (33 of 46 actually resumed)

    ------------------------------------------------------------

Every number above is computed from `~/.recall/bad_recoveries.jsonl`
+ `~/.recall/counters.json` and nothing else. No network, no
content, no telemetry.
"""

from __future__ import annotations

import logging

from . import bad_recoveries
from .stats import StatsCounters

log = logging.getLogger("recall.core.trust_cli")


# Default lookback window for the rates. Matches the ledger's own
# 14-day demotion window so the surfaces tell the same story.
_WINDOW_DAYS: float = 14.0


def _safe_pct(n: int, d: int) -> float:
    if d <= 0:
        return 0.0
    return round(100.0 * n / d, 1)


def _format_review(window_days: float = _WINDOW_DAYS) -> str:
    rule = "  " + "-" * 60
    counts = bad_recoveries.counts_by_reason(window_days=window_days)
    bad_total = sum(counts.values())

    # Pull resume / silence aggregates from the counters file. The
    # counters are cumulative across the install lifetime; we use
    # them as the *denominator pool*. The directive's *bad %* is
    # `bad / shown`, *resume %* is `accepted / shown`, *silence %*
    # is `(shown - accepted - flagged_as_bad) / shown`.
    snap = StatsCounters().snapshot()
    shown = int(snap.get("recovery_shown", 0) or 0)
    accepted = int(snap.get("recovery_accepted", 0) or 0)

    bad_pct = _safe_pct(bad_total, shown)
    resume_pct = _safe_pct(accepted, shown)
    # Silence is everything that was shown, neither resumed nor
    # marked bad. Floor at 0 in case counters drift.
    silence = max(0, shown - accepted - bad_total)
    silence_pct = _safe_pct(silence, shown)

    out: list[str] = []
    out.append("")
    out.append(rule)
    out.append(f"    Trust review - last {int(window_days)} days")
    out.append(rule)
    out.append("")
    out.append(f"    bad recoveries     {bad_total}")
    for reason in ("wrong_topic", "already_done", "noise", "duplicate"):
        out.append(f"      {reason:<16} {counts.get(reason, 0)}")
    out.append("")
    out.append(
        f"    bad %              {bad_pct:>5}    "
        f"({bad_total} of {shown} shown)"
    )
    out.append(
        f"    silence %          {silence_pct:>5}    "
        f"({silence} of {shown} cleanly suppressed)"
    )
    out.append(
        f"    resume %           {resume_pct:>5}    "
        f"({accepted} of {shown} actually resumed)"
    )
    out.append("")
    if shown == 0:
        out.append("    No recoveries have been shown yet - the rates")
        out.append("    will appear once the launcher starts surfacing")
        out.append("    real candidates.")
        out.append("")
    out.append(rule)
    out.append("")
    return "\n".join(out)


def run_trust_cli(argv: list[str]) -> int:
    """Entry point for `recall trust <subcommand>`.

    Subcommands:

      review            print the 14-day ledger summary
      review --days N   override the window
    """
    if not argv or argv[0] in {"-h", "--help"}:
        print("Usage: recall trust review [--days N]")
        print()
        print("Prints the bad-recovery ledger + resume/silence rates")
        print("computed from local state. No network, no telemetry.")
        return 2 if not argv else 0
    sub = argv[0]
    if sub != "review":
        print(f"unknown subcommand: {sub}")
        return 2
    window = _WINDOW_DAYS
    if "--days" in argv:
        idx = argv.index("--days")
        try:
            window = float(argv[idx + 1])
        except (IndexError, ValueError):
            print("`--days` expects a number")
            return 2
    print(_format_review(window))
    return 0


__all__ = ["run_trust_cli"]
