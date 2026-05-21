"""Aggregate every imported cohort stats.json into one rollup.

    python apps/admin/merge_stats.py

Walks `apps/admin/imported/<cohort>/*.json` and writes
`apps/admin/aggregate.json` - per-cohort and overall totals. Counts
are summed; rates are averaged; a per-device contribution stays a
single number. No identifiers cross into the aggregate beyond the
cohort id and a device *count*.
"""

from __future__ import annotations

import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
IMPORTED = HERE / "imported"
OUT = HERE / "aggregate.json"

_SUM = {
    "events_total", "investigations_total", "recoveries_shown",
    "recoveries_accepted", "resurface_opened", "browser_events",
    "files_opened",
}
_AVG = {
    "install_age_days", "extension_connected_days", "resume_success_rate",
    "daily_active_days", "weekly_active_days",
}


def _blank() -> dict:
    return {
        "devices": 0,
        # Phase 5B founder additions — derived per device, not summed.
        "returning_installs": 0,
        **{k: 0 for k in _SUM},
        **{k: 0.0 for k in _AVG},
    }


def _fold(acc: dict, metrics: dict) -> None:
    acc["devices"] += 1
    # Phase 5B: "returning installs" — a device that was active in
    # more than one distinct week. The honest cross-device retention
    # signal in a no-telemetry world.
    if int(metrics.get("weekly_active_days", 0) or 0) >= 2:
        acc["returning_installs"] += 1
    for k in _SUM:
        acc[k] += int(metrics.get(k, 0) or 0)
    for k in _AVG:
        acc[k] += float(metrics.get(k, 0) or 0)


def _finalize(acc: dict) -> dict:
    n = max(1, acc["devices"])
    out = {
        "devices": acc["devices"],
        "returning_installs": acc["returning_installs"],
    }
    for k in _SUM:
        out[k] = acc[k]
    for k in _AVG:
        out[k] = round(acc[k] / n, 2)
    # Phase 5B founder derivations — named so the dashboard can read
    # them directly. `resume_sessions` is a relabel of accepted
    # recoveries; `continuity_restored` and `daily_reopen_pct` are
    # the founder-facing versions of the per-device rates.
    out["resume_sessions"] = out.get("recoveries_accepted", 0)
    out["continuity_restored_pct"] = out.get("resume_success_rate", 0.0)
    install_age = out.get("install_age_days", 0)
    active = out.get("daily_active_days", 0)
    out["daily_reopen_pct"] = (
        round(active / install_age, 2) if install_age else 0.0
    )
    return out


def main() -> int:
    cohorts: dict[str, dict] = {}
    overall = _blank()
    device_count = 0

    if IMPORTED.exists():
        for cohort_dir in sorted(p for p in IMPORTED.iterdir() if p.is_dir()):
            acc = _blank()
            for f in sorted(cohort_dir.glob("*.json")):
                try:
                    metrics = json.loads(f.read_text(encoding="utf-8")).get(
                        "metrics", {}
                    )
                except (OSError, ValueError):
                    continue
                _fold(acc, metrics)
                _fold(overall, metrics)
                device_count += 1
            cohorts[cohort_dir.name] = _finalize(acc)

    result = {
        "schema": "recall.aggregate/1",
        "device_count": device_count,
        "cohorts": cohorts,
        "overall": _finalize(overall),
    }
    OUT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")

    if device_count == 0:
        print("  no imported stats yet - aggregate.json written empty.")
        print("  import one first: python apps/admin/import_stats.py ...")
    else:
        print(f"  merged {device_count} device(s) across "
              f"{len(cohorts)} cohort(s) -> aggregate.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
