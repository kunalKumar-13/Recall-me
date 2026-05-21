"""Print the cohort rollup - the founder's terminal read.

    python apps/admin/cohort_summary.py

Reads `aggregate.json` (produced by `merge_stats.py`) and prints a
per-cohort summary plus the Health Overview signal (green / yellow
/ red) the dashboard uses. Counts only; nothing here is a user.
"""

from __future__ import annotations

import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
AGG = HERE / "aggregate.json"


def health_signal(m: dict) -> str:
    """Green / yellow / red - the same rule the dashboard renders.

    red    - devices exist but no recovery was ever shown
    yellow - recoveries shown, but the extension barely connects
    green  - installs work, recoveries flow
    """
    if m.get("devices", 0) == 0:
        return "-  no data yet"
    if m.get("recoveries_shown", 0) == 0:
        return "RED  - installs run, but no recovery ever surfaced"
    if m.get("extension_connected_days", 0) < 1:
        return "YELLOW  - recoveries flow, but the extension is absent"
    return "GREEN  - installs work, recoveries flow"


def _print_block(name: str, m: dict) -> None:
    print(f"  {name}")
    print(f"    devices                  {m.get('devices', 0)}")
    print(f"    events captured          {m.get('events_total', 0)}")
    print(f"    investigations           {m.get('investigations_total', 0)}")
    print(f"    recoveries shown         {m.get('recoveries_shown', 0)}")
    print(f"    recoveries accepted      {m.get('recoveries_accepted', 0)}")
    rate = m.get("resume_success_rate", 0)
    print(f"    resume success rate      "
          f"{rate * 100:.0f}%" if rate else "    resume success rate      -")
    print(f"    avg daily-active days    {m.get('daily_active_days', 0)}")
    print(f"    health                   {health_signal(m)}")
    print()


def main() -> int:
    if not AGG.exists():
        print("  no aggregate.json - run: python apps/admin/merge_stats.py")
        return 1
    try:
        data = json.loads(AGG.read_text(encoding="utf-8"))
    except (OSError, ValueError) as e:
        print(f"  could not read aggregate.json: {e}")
        return 1

    print()
    print("  Recall - cohort summary  (counts only, voluntary imports)")
    print()
    _print_block("OVERALL", data.get("overall", {}))
    for name, m in sorted(data.get("cohorts", {}).items()):
        _print_block(f"cohort: {name}", m)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
