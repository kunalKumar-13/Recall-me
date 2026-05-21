"""Import a user's voluntary stats.json into the cohort store.

    python apps/admin/import_stats.py <stats.json> <cohort-id> <user-id>

A cohort member runs `recall stats --export` on their machine and
*chooses* to send the founder the resulting `stats.json`. This
script files that export under `apps/admin/imported/<cohort>/`.

It is a gate, not a pipe: the file is **rejected** unless it is a
counts-only `recall.stats/1` export. If anything that looks like
content (a string where a number belongs, an unexpected key) is
present, the import fails loudly rather than letting it through.
There is no network here - this reads a file the founder already
has in hand.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
IMPORTED = HERE / "imported"

# The only keys allowed in a `metrics` block - every one a count or
# a rate. Mirrors app/core/stats.py. A key outside this set, or a
# non-numeric value, means the file is not a clean export.
_ALLOWED_METRICS = {
    "install_age_days", "events_total", "investigations_total",
    "recoveries_shown", "recoveries_accepted", "resurface_opened",
    "extension_connected_days", "browser_events", "files_opened",
    "resume_success_rate", "daily_active_days", "weekly_active_days",
}


def validate(payload: dict) -> list[str]:
    """Return a list of problems; empty list means the file is a
    clean, counts-only export safe to import."""
    problems: list[str] = []
    if payload.get("schema") != "recall.stats/1":
        problems.append("not a recall.stats/1 export")
    metrics = payload.get("metrics")
    if not isinstance(metrics, dict):
        problems.append("missing `metrics` block")
        return problems
    for key, value in metrics.items():
        if key not in _ALLOWED_METRICS:
            problems.append(f"unexpected metric key: {key!r}")
        if not isinstance(value, (int, float)) or isinstance(value, bool):
            problems.append(f"metric {key!r} is not a number ({value!r})")
    return problems


def main(argv: list[str]) -> int:
    if len(argv) != 3:
        print(__doc__)
        return 2
    src, cohort, user = Path(argv[0]), argv[1], argv[2]
    if not src.exists():
        print(f"  no such file: {src}")
        return 1
    try:
        payload = json.loads(src.read_text(encoding="utf-8"))
    except (OSError, ValueError) as e:
        print(f"  could not read {src}: {e}")
        return 1

    problems = validate(payload)
    if problems:
        print(f"  REJECTED {src.name} - not a clean counts-only export:")
        for p in problems:
            print(f"    - {p}")
        return 1

    dest_dir = IMPORTED / cohort
    dest_dir.mkdir(parents=True, exist_ok=True)
    dest = dest_dir / f"{user}.json"
    # Re-serialise only the validated payload - never copy raw bytes.
    dest.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(f"  imported -> imported/{cohort}/{user}.json")
    print(f"  ({len(payload['metrics'])} metrics, counts only)")
    print("  next: python apps/admin/merge_stats.py")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
