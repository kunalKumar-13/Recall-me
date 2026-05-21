"""`recall founder` — the founder's terminal control room.

Sister to `recall stats` (the user-facing local stats) and `recall
doctor` (the diagnostics). This is the operator surface:

    recall founder status     5-second overview
    recall founder bake       regenerate apps/admin/data/*.json
    recall founder release    readiness + GO/NO-GO + blockers
    recall founder trust      trust cards
    recall founder health     health cards
    recall founder alpha      cohort summary
    recall founder timeline   phase track + done %

Read-only except for `bake`, which writes the dashboard files in
`apps/admin/data/`. No network, no telemetry, no upload. All ASCII
output (Windows cp1252 consoles).
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "apps" / "admin" / "data"
BAKE_SCRIPT = ROOT / "apps" / "admin" / "scripts" / "bake_data.py"


# --------------------------------------------------------------- io


def _read(name: str, default: Any = None) -> Any:
    try:
        return json.loads((DATA / name).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return default


def _bar(score: float, width: int = 20) -> str:
    """An ASCII bar for the readiness score. No unicode block chars
    (cp1252 cannot encode them)."""
    filled = int(round(max(0.0, min(1.0, score)) * width))
    return "[" + "#" * filled + "." * (width - filled) + "]"


# --------------------------------------------------------------- bake


def cmd_bake(_argv: list[str]) -> int:
    if not BAKE_SCRIPT.exists():
        print(f"  bake script missing: {BAKE_SCRIPT}")
        return 1
    print("  recall founder - bake")
    res = subprocess.run(
        [sys.executable, str(BAKE_SCRIPT)],
        capture_output=False, text=True,
    )
    return res.returncode


# --------------------------------------------------------------- status


def cmd_status(_argv: list[str]) -> int:
    """The 5-second view."""
    from . import release_readiness
    r = release_readiness.compute(DATA)
    health = _read("health.json", []) or []
    cohorts = _read("cohorts.json", []) or []
    feedback = _read("feedback.json", []) or []
    timeline = _read("timeline.json", []) or []

    now_phase = next((p for p in timeline if p.get("state") == "now"), None)
    next_phase = next((p for p in timeline if p.get("state") == "next"), None)
    done_count = sum(1 for p in timeline if p.get("state") == "done")

    print()
    print("  Recall - founder status")
    print()
    print(f"    Readiness            {r.state}   {r.score}/100   {_bar(r.score / 100.0)}")
    print(f"    Headline             {r.headline}")
    print()
    print("  Health (top of dashboard):")
    for c in health:
        st = c.get("health", "mute").upper().ljust(6)
        print(f"    [{st}] {str(c.get('label','')).ljust(22)} {c.get('value','')}")
    print()
    print("  Alpha:")
    active_cohorts = [c for c in cohorts if c.get("status") in ("forming", "active")]
    total_devices = sum(int(c.get("devices") or 0) for c in active_cohorts)
    total_returning = sum(int(c.get("returning") or 0) for c in active_cohorts)
    print(f"    cohorts active        {len(active_cohorts)} of {len(cohorts)}")
    print(f"    devices               {total_devices}")
    print(f"    returning             {total_returning}")
    print(f"    feedback (all-time)   {len(feedback)}")
    print()
    print("  Phase:")
    if now_phase:
        print(f"    now    {now_phase.get('name','')}  {now_phase.get('label','')}  ({now_phase.get('done_pct',0)}%)")
    if next_phase:
        print(f"    next   {next_phase.get('name','')}  {next_phase.get('label','')}")
    print(f"    done   {done_count} phases")
    print()
    return 0


# --------------------------------------------------------------- release


def cmd_release(_argv: list[str]) -> int:
    from . import release_readiness
    r = release_readiness.compute(DATA)
    release = _read("release.json", {}) or {}

    print()
    print("  Recall - founder release")
    print()
    print(f"    Overall              {r.state}   {r.score}/100   {_bar(r.score / 100.0)}")
    print(f"    {r.headline}")
    print()
    print(f"    Version              {release.get('current_version','-')}")
    print(f"    Next milestone       {release.get('next_milestone','-')}")
    print(f"    GO/NO-GO             {release.get('go_no_go','NO-GO')}")
    print(f"    Installer            {release.get('installer','-')}")
    print(f"    Signing              {release.get('signing','-')}")
    print(f"    macOS                {release.get('mac','-')}")
    print(f"    Screenshots          {release.get('screenshots','-')}")
    print()
    print("  Readiness breakdown:")
    for d in r.dimensions:
        print(f"    [{d.state.ljust(6)}] {d.label.ljust(13)} "
              f"{int(d.score * 100):3d}% (weight {d.weight}) - {d.detail}")
    print()
    if r.blockers:
        print(f"  Blocked items ({len(r.blockers)}):")
        for b in r.blockers:
            print(f"    - {b}")
        print()
    return 0


# --------------------------------------------------------------- trust


def cmd_trust(_argv: list[str]) -> int:
    cards = _read("trust.json", []) or []
    print()
    print("  Recall - founder trust")
    print()
    if not cards:
        print("    no trust.json yet - run `recall founder bake`")
        print()
        return 1
    for c in cards:
        st = str(c.get("state", "mute")).upper().ljust(6)
        print(f"    [{st}] {str(c.get('label','')).ljust(26)} {str(c.get('count',''))}")
        print(f"             {c.get('detail','')}")
    print()
    return 0


# --------------------------------------------------------------- health


def cmd_health(_argv: list[str]) -> int:
    cards = _read("health.json", []) or []
    print()
    print("  Recall - founder health")
    print()
    if not cards:
        print("    no health.json yet - run `recall founder bake`")
        print()
        return 1
    for c in cards:
        st = str(c.get("health", "mute")).upper().ljust(6)
        print(f"    [{st}] {str(c.get('label','')).ljust(22)} {c.get('value','')}")
        if c.get("foot"):
            print(f"             {c['foot']}")
    print()
    return 0


# --------------------------------------------------------------- alpha


def cmd_alpha(_argv: list[str]) -> int:
    cohorts = _read("cohorts.json", []) or []
    print()
    print("  Recall - founder alpha")
    print()
    if not cohorts:
        print("    no cohorts.json yet - run `recall founder bake`")
        print()
        return 1
    for c in cohorts:
        st = str(c.get("health", "mute")).upper().ljust(6)
        devices = int(c.get("devices") or 0)
        returning = int(c.get("returning") or 0)
        ret_pct = f"{int(returning / devices * 100)}%" if devices > 0 else "-"
        print(f"    [{st}] {str(c.get('id','')).ljust(12)} {str(c.get('status','')).ljust(8)} "
              f"devices={devices:>3}  returning={returning:>3} ({ret_pct})  "
              f"feedback={int(c.get('feedback_count') or 0):>2}")
        if c.get("notes"):
            print(f"             {c['notes']}")
    print()
    return 0


# --------------------------------------------------------------- timeline


def cmd_timeline(_argv: list[str]) -> int:
    phases = _read("timeline.json", []) or []
    print()
    print("  Recall - founder timeline")
    print()
    if not phases:
        print("    no timeline.json yet - run `recall founder bake`")
        print()
        return 1
    for p in phases:
        state = str(p.get("state", "")).upper().ljust(7)
        name = str(p.get("name", "")).ljust(7)
        label = str(p.get("label", "")).ljust(28)
        pct = int(p.get("done_pct") or 0)
        print(f"    [{state}] {name} {label} {pct:3d}%")
    done = sum(1 for p in phases if p.get("state") == "done")
    now = next((p for p in phases if p.get("state") == "now"), None)
    nxt = next((p for p in phases if p.get("state") == "next"), None)
    print()
    print(f"    {done} phases done"
          + (f", now: {now.get('name')} ({now.get('done_pct')}%)" if now else "")
          + (f", next: {nxt.get('name')}" if nxt else ""))
    print()
    return 0


# --------------------------------------------------------------- help


def cmd_help(_argv: list[str] | None = None) -> int:
    print()
    print("  recall founder - the founder's terminal control room.")
    print()
    print("  commands:")
    print("    status       5-second overview (readiness + health + alpha + phase)")
    print("    bake         regenerate apps/admin/data/*.json from sources")
    print("    release      readiness + GO/NO-GO + blocked items")
    print("    trust        trust cards (recoveries shown / accepted / silence)")
    print("    health       health cards (active installs / returning / ...)")
    print("    alpha        cohort summary (devices / returning / feedback)")
    print("    timeline     phase track + done %")
    print()
    print("  all read from apps/admin/data/; `bake` writes it.")
    print("  no network, no auth, no upload - same contract as `recall stats`.")
    print()
    return 0


# --------------------------------------------------------------- dispatch


_COMMANDS = {
    "status":   cmd_status,
    "bake":     cmd_bake,
    "release":  cmd_release,
    "trust":    cmd_trust,
    "health":   cmd_health,
    "alpha":    cmd_alpha,
    "timeline": cmd_timeline,
    "help":     cmd_help,
    "--help":   cmd_help,
    "-h":       cmd_help,
}


def run_founder_cli(argv: list[str]) -> int:
    if not argv:
        return cmd_help()
    cmd = argv[0]
    fn = _COMMANDS.get(cmd)
    if fn is None:
        print(f"  unknown command: {cmd!r}")
        cmd_help()
        return 2
    return fn(argv[1:])
