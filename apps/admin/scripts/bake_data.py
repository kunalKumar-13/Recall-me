"""Bake the 8 control-room data files from a small set of source
inputs the founder actually maintains.

    python apps/admin/scripts/bake_data.py
    # or via the founder CLI:
    python recall.py founder bake

Inputs (founder edits these):
  apps/admin/aggregate.json         (or `merge_stats.py` writes it)
  apps/admin/release_state.json     manual release / GO-NO-GO state
  apps/admin/timeline_input.json    phase roster
  apps/admin/traction_history.json  daily overall snapshots
  apps/admin/cohorts.json           cohort registry (existing)
  apps/admin/alpha/feedback.json    hand-logged feedback inbox
  apps/admin/alpha/notes.json       per-cohort notes
  apps/admin/alpha/users.json       (read for sanity; not exported)

Outputs (the dashboard reads these — no founder edits here):
  apps/admin/data/{health,traction,cohorts,release,trust,
                   feedback,timeline,meta}.json

Local-only by construction: stdlib only, no network call, no
upload. The script never reads anything outside `apps/admin/`.
Missing sources degrade to empty / default outputs — the bake
never raises.
"""

from __future__ import annotations

import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
ADMIN = HERE.parent              # apps/admin/
DATA = ADMIN / "data"
ALPHA = ADMIN / "alpha"


# --------------------------------------------------------------- io


def _read(path: Path, default: Any) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return default


def _write(name: str, payload: Any) -> Path:
    DATA.mkdir(parents=True, exist_ok=True)
    out = DATA / name
    out.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return out


# --------------------------------------------------------------- color rules


def _h(value: float, green: float, yellow: float) -> str:
    """Map a numeric metric to green / yellow / red by two thresholds."""
    if value >= green:
        return "green"
    if value >= yellow:
        return "yellow"
    return "red"


# --------------------------------------------------------------- health


def _bake_health(agg: dict) -> list[dict]:
    o = (agg or {}).get("overall") or {}
    device_count = int((agg or {}).get("device_count") or 0)
    installs_age = float(o.get("install_age_days") or 0)
    ext_days = float(o.get("extension_connected_days") or 0)
    ext_pct = (ext_days / installs_age) if installs_age > 0 else 0.0

    cards = [
        {
            "id": "active_installs", "label": "Active installs",
            "value": device_count, "foot": "devices with imported exports",
            "health": _h(device_count, 25, 5),
        },
        {
            "id": "returning_installs", "label": "Returning installs",
            "value": int(o.get("returning_installs") or 0),
            "foot": "weekly_active_days >= 2",
            "health": _h(int(o.get("returning_installs") or 0), 10, 1),
        },
        {
            "id": "continuity_restored", "label": "Continuity restored",
            "value": f"{int(float(o.get('continuity_restored_pct') or 0) * 100)}%",
            "foot": "avg resume_success_rate",
            "health": _h(float(o.get("continuity_restored_pct") or 0), 0.7, 0.4),
        },
        {
            "id": "resume_sessions", "label": "Resume sessions",
            "value": int(o.get("resume_sessions") or o.get("recoveries_accepted") or 0),
            "foot": "sum of recoveries_accepted",
            "health": _h(int(o.get("resume_sessions") or o.get("recoveries_accepted") or 0), 20, 5),
        },
        {
            "id": "investigations", "label": "Investigations",
            "value": int(o.get("investigations_total") or 0),
            "foot": "sum across cohort exports",
            "health": _h(int(o.get("investigations_total") or 0), 50, 10),
        },
        {
            "id": "extension_connected", "label": "Extension connected",
            "value": f"{int(ext_pct * 100)}%",
            "foot": "extension_connected_days / install_age_days",
            "health": _h(ext_pct, 0.7, 0.4),
        },
    ]
    return cards


# --------------------------------------------------------------- traction


_TRACTION_FIELDS = {
    "install_growth":      ("installs",            "installs"),
    "return_rate":         ("return_rate",         "%"),
    "continuity_restored": ("continuity_restored", "%"),
    "recoveries_accepted": ("recoveries_accepted", "total"),
    "daily_reopen_pct":    ("daily_reopen_pct",    "%"),
    "alpha_growth":        ("alpha_devices",       "devices"),
}

_TRACTION_LABELS = {
    "install_growth":      "Install growth",
    "return_rate":         "Return rate",
    "continuity_restored": "Continuity restored",
    "recoveries_accepted": "Recoveries accepted",
    "daily_reopen_pct":    "Daily reopen %",
    "alpha_growth":        "Alpha cohort growth",
}


def _bake_traction(history: dict) -> list[dict]:
    rows = (history or {}).get("history") or []
    out: list[dict] = []
    for series_id, (field, unit) in _TRACTION_FIELDS.items():
        values = [
            {"d": r.get("d", ""), "v": float(r.get(field) or 0)} for r in rows
        ]
        out.append({
            "id": series_id,
            "label": _TRACTION_LABELS[series_id],
            "unit": unit,
            "values": values,
        })
    return out


# --------------------------------------------------------------- cohorts


def _cohort_health(per: dict) -> str:
    if int(per.get("devices") or 0) == 0:
        return "mute"
    if int(per.get("recoveries_accepted") or 0) == 0:
        return "red"
    if int(per.get("returning_installs") or 0) == 0:
        return "yellow"
    return "green"


def _bake_cohorts(registry: dict, agg: dict, feedback: list[dict],
                  notes: dict) -> list[dict]:
    cohorts_in = (registry or {}).get("cohorts") or []
    per = (agg or {}).get("cohorts") or {}
    notes_map = (notes or {}).get("cohorts") or {}

    fb_counts: dict[str, int] = {}
    for f in feedback:
        c = str(f.get("cohort") or "")
        fb_counts[c] = fb_counts.get(c, 0) + 1

    out: list[dict] = []
    for c in cohorts_in:
        cid = str(c.get("id") or "")
        pm = per.get(cid) or {}
        out.append({
            "id": cid,
            "label": str(c.get("label") or cid),
            "status": str(c.get("status") or "planned"),
            "devices": int(pm.get("devices") or 0),
            "returning": int(pm.get("returning_installs") or 0),
            "feedback_count": int(fb_counts.get(cid, 0)),
            "health": _cohort_health(pm),
            "notes": str(notes_map.get(cid) or c.get("notes") or ""),
        })
    return out


# --------------------------------------------------------------- release


def _bake_release(state: dict) -> dict:
    s = state or {}
    blocked = list(s.get("blocked") or [])
    return {
        "current_version":  str(s.get("current_version") or "0.0.0"),
        "next_milestone":   str(s.get("next_milestone") or "—"),
        "installer":        str(s.get("installer") or "blocked"),
        "mac":              str(s.get("mac") or "source-only"),
        "signing":          str(s.get("signing") or "unsigned"),
        "screenshots":      str(s.get("screenshots") or "missing"),
        "go_no_go":         str(s.get("go_no_go") or "NO-GO"),
        "blocked":          blocked,
    }


# --------------------------------------------------------------- trust


def _bake_trust(agg: dict, feedback: list[dict]) -> list[dict]:
    o = (agg or {}).get("overall") or {}
    shown = int(o.get("recoveries_shown") or 0)
    accepted = int(o.get("recoveries_accepted") or 0)
    rate = (accepted / shown) if shown > 0 else 0.0

    trust_complaints = sum(1 for f in feedback if str(f.get("tag")) == "trust")
    confusion_count = sum(1 for f in feedback if str(f.get("tag")) == "confusion")

    return [
        {
            "id": "recoveries_shown", "label": "Recoveries shown",
            "count": shown, "detail": "across all cohort exports",
            "state": "green" if shown > 0 else "red",
        },
        {
            "id": "recoveries_accepted", "label": "Recoveries accepted",
            "count": accepted,
            "detail": f"{int(rate * 100)}% accept rate",
            "state": "green" if rate >= 0.6 else ("yellow" if rate >= 0.3 else "red"),
        },
        {
            "id": "correct_silence", "label": "Correct silence",
            "count": "high" if rate >= 0.6 else ("ok" if shown > 0 else "—"),
            "detail": "no false-positive trust reports" if trust_complaints == 0 else f"{trust_complaints} trust-tagged feedback",
            "state": "green" if trust_complaints == 0 else "yellow",
        },
        {
            "id": "bad_recoveries", "label": "Bad recoveries",
            "count": trust_complaints,
            "detail": "zero terminal trust events logged" if trust_complaints == 0 else "review trust-tagged feedback",
            "state": "green" if trust_complaints == 0 else "red",
        },
        {
            "id": "extension_offline", "label": "Extension offline incidents",
            "count": confusion_count,
            "detail": "approximated from confusion-tagged feedback",
            "state": "green" if confusion_count <= 1 else "yellow",
        },
        {
            "id": "doctor_failures", "label": "`recall doctor` reds",
            "count": "—",
            "detail": "manual — from cohort check-ins",
            "state": "yellow",
        },
    ]


# --------------------------------------------------------------- feedback


def _bake_feedback(feedback_in: dict) -> list[dict]:
    items = (feedback_in or {}).get("items") or []
    items_sorted = sorted(items, key=lambda f: str(f.get("date") or ""), reverse=True)
    return items_sorted


# --------------------------------------------------------------- timeline


def _bake_timeline(tin: dict) -> list[dict]:
    return list((tin or {}).get("phases") or [])


# --------------------------------------------------------------- meta


def _bake_meta(source_files: list[str]) -> dict:
    return {
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
        "source_note": (
            "Baked from " + ", ".join(source_files) + ". "
            "Re-run `python apps/admin/scripts/bake_data.py` to refresh."
        ),
    }


# --------------------------------------------------------------- pipeline


def main() -> int:
    t0 = time.perf_counter()
    warnings: list[str] = []

    # Read all sources. Each missing source is a warning, not an error.
    sources = {
        "aggregate.json":         ADMIN / "aggregate.json",
        "release_state.json":     ADMIN / "release_state.json",
        "timeline_input.json":    ADMIN / "timeline_input.json",
        "traction_history.json":  ADMIN / "traction_history.json",
        "cohorts.json":           ADMIN / "cohorts.json",
        "alpha/feedback.json":    ALPHA / "feedback.json",
        "alpha/notes.json":       ALPHA / "notes.json",
    }
    payload = {}
    for name, path in sources.items():
        payload[name] = _read(path, {})
        if not path.exists():
            warnings.append(f"missing source: {name}")

    feedback_items = (payload["alpha/feedback.json"] or {}).get("items") or []

    # Bake each output.
    health   = _bake_health(payload["aggregate.json"])
    traction = _bake_traction(payload["traction_history.json"])
    cohorts  = _bake_cohorts(
        payload["cohorts.json"], payload["aggregate.json"],
        feedback_items, payload["alpha/notes.json"],
    )
    release  = _bake_release(payload["release_state.json"])
    trust    = _bake_trust(payload["aggregate.json"], feedback_items)
    feedback = _bake_feedback(payload["alpha/feedback.json"])
    timeline = _bake_timeline(payload["timeline_input.json"])
    meta     = _bake_meta(sorted(sources.keys()))

    # Cheap validation: warn on obvious empties.
    if not health:    warnings.append("health.json baked empty")
    if not traction:  warnings.append("traction.json has no series")
    if not timeline:  warnings.append("timeline.json baked empty")

    # Write outputs.
    written = [
        _write("health.json", health),
        _write("traction.json", traction),
        _write("cohorts.json", cohorts),
        _write("release.json", release),
        _write("trust.json", trust),
        _write("feedback.json", feedback),
        _write("timeline.json", timeline),
        _write("meta.json", meta),
    ]

    elapsed_ms = (time.perf_counter() - t0) * 1000
    print(f"  baked {len(written)} files in {elapsed_ms:.0f} ms")
    for p in written:
        print(f"    wrote {p.relative_to(ADMIN.parent.parent)}")
    if warnings:
        print(f"  {len(warnings)} warning(s):")
        for w in warnings:
            print(f"    - {w}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
