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


# --------------------------------------------------------------- alpha-health (Phase 6E)


def cmd_alpha_health(_argv: list[str]) -> int:
    """`recall founder alpha-health` — the Phase 6E "Alpha Health"
    panel.

    Sister to ``recall founder alpha`` (the baked cohort summary).
    Reads directly from the source-of-truth files —
    ``alpha/users/<cohort>/<handle>/status.json`` and
    ``alpha/recovery_journal.json`` — and emits the five directive
    signals plus the green/yellow/red verdict for each.

    Five signals (named in the directive):

      - installs         total tester records present
      - returning        ≥ 2 of 3 days marked `yes`
      - first recoveries records with `first_recovery` set
      - trust %          (resume_ok + correct_silence) / shown
      - drop reasons     aggregated text + counts

    The verdict per signal is mechanical:

      - **GREEN** signal meets the alpha-001 floor (5 installs, ≥ 2
        returning, ≥ 3 first-recoveries, trust ≥ 80 %, no drop reason
        with count ≥ 2).
      - **YELLOW** signal exists but is short of the floor.
      - **RED** signal is meaningfully wrong (drop reason ≥ 2 of the
        same kind, or trust < 50 % with ≥ 5 shown).
    """
    # `alpha export` already aggregates everything we need from the
    # users tree + recovery_journal. We invoke it as a function call
    # rather than a subprocess so we don't pay process spawn cost.
    from . import alpha_cli

    # Read the same data as cmd_export but keep the numbers; we
    # bypass the JSON print by re-implementing the small aggregation.
    cohorts = alpha_cli._list_cohorts(None)
    installs = returning = recoveries = install_fails = wrong = 0
    drop_reasons: dict[str, int] = {}
    for c in cohorts:
        for folder in alpha_cli._list_testers(c):
            r = alpha_cli._load_status(folder / "status.json")
            if r is None:
                continue
            installs += 1
            if (r.day1, r.day2, r.day3).count("yes") >= 2:
                returning += 1
            if r.first_recovery and r.first_recovery != "none yet":
                recoveries += 1
            if r.install_ok in ("no", "partial"):
                install_fails += 1
            if r.first_resume_ok == "wrong work":
                wrong += 1
            if r.drop_reason and r.drop_reason not in ("n/a", "", None):
                drop_reasons[r.drop_reason] = drop_reasons.get(r.drop_reason, 0) + 1
    trust = alpha_cli._compute_trust_pct()

    # Map each signal onto a green/yellow/red dot. The thresholds
    # are documented above; tweak only if the alpha floor moves.
    def verdict(name: str, value, *, target=None) -> str:
        if name == "installs":
            return "GREEN" if value >= 5 else ("YELLOW" if value >= 1 else "RED")
        if name == "returning":
            return "GREEN" if value >= 2 else ("YELLOW" if value >= 1 else "RED")
        if name == "recoveries":
            return "GREEN" if value >= 3 else ("YELLOW" if value >= 1 else "RED")
        if name == "trust":
            if trust["shown"] == 0:
                return "YELLOW"  # not enough data yet
            pct = trust["pct_correct"] or 0
            if pct >= 80:
                return "GREEN"
            if pct >= 50:
                return "YELLOW"
            return "RED"
        if name == "drops":
            worst = max(drop_reasons.values(), default=0)
            return "RED" if worst >= 2 else ("YELLOW" if worst >= 1 else "GREEN")
        return "YELLOW"

    print()
    print("  Recall - founder alpha-health")
    print()
    print(f"    [{verdict('installs', installs)}]  installs           {installs}")
    print(f"    [{verdict('returning', returning)}]  returning          {returning}  (>=2 of 3 days marked yes)")
    print(f"    [{verdict('recoveries', recoveries)}]  first recoveries   {recoveries}")
    pct = trust["pct_correct"]
    # ASCII only — Windows cp1252 consoles can't encode an em-dash.
    pct_str = f"{pct}%" if pct is not None else "-"
    print(f"    [{verdict('trust', trust)}]  trust %            {pct_str}  ({trust['resume_ok'] + trust['correct_silence']}/{trust['shown']} correct of shown)")
    print(f"    [{verdict('drops', drop_reasons)}]  drop reasons       {sum(drop_reasons.values())}")
    if drop_reasons:
        for reason, n in sorted(drop_reasons.items(), key=lambda x: -x[1]):
            print(f"              {n} x {reason}")
    print()
    print(f"    install_fails: {install_fails}   wrong recoveries: {wrong}")
    print()
    # The directive's alpha-001 success line — print only when at
    # least one tester exists, so a brand-new repo doesn't see a
    # noisy red status panel.
    if installs:
        ok_humans = installs >= 5
        ok_recs = recoveries >= 3
        ok_wow = trust["resume_ok"] >= 1
        ok_fail = sum(drop_reasons.values()) >= 1 or install_fails >= 1
        print(
            f"    directive: "
            f"{'OK' if ok_humans else 'short'} 5 humans, "
            f"{'OK' if ok_recs else 'short'} 3 recoveries, "
            f"{'OK' if ok_wow else 'short'} 1 wow, "
            f"{'OK' if ok_fail else 'short'} 1 failure story"
        )
        print()
    return 0


# --------------------------------------------------------------- daily-loop (Phase 6F)


def cmd_daily_loop(_argv: list[str]) -> int:
    """`recall founder daily-loop` — the Phase 6F operator panel.

    Reads ``~/.recall/daily_loop.jsonl`` (the per-day counter log)
    directly. No bake step. Prints today + yesterday + the 7-day
    window aggregate, plus the three derived signals — *continuity
    restored* / *return rate* / *resume quality* — with the
    green/yellow/red verdict from :func:`app.core.daily_loop.summary`.

    Thresholds (single source of truth — match the in-source
    verdict() in `daily_loop.py`):

      - **continuity_restored**: GREEN >= 60 %, YELLOW >= 25 %, else RED
      - **return_rate**:         GREEN >= 30 %, YELLOW >= 10 %, else RED
      - **resume_quality**:      GREEN >= 80 %, YELLOW >= 50 %, else RED

    Honest empty: a fresh install with zero events prints `YELLOW`
    on every signal (not enough data), not RED — silence is silence.
    """
    from . import daily_loop
    days = 7
    s = daily_loop.summary(days=days)

    def _row(label: str, rec: dict) -> str:
        return (
            f"    {label.ljust(12)}  "
            f"started={int(rec.get('day_started', 0)):>2}  "
            f"shown={int(rec.get('recoveries_shown', 0)):>2}  "
            f"used={int(rec.get('recoveries_used', 0)):>2}  "
            f"success={int(rec.get('resume_success', 0)):>2}  "
            f"returns={int(rec.get('returns', 0)):>2}  "
            f"investig={int(rec.get('investigations_opened', 0)):>2}"
        )

    print()
    print("  Recall - founder daily-loop")
    print()
    print(_row("today", s["today"]))
    print(_row("yesterday", s["yesterday"]))
    print(_row(f"{days}d window", s["window"]))
    print(f"    days with any activity: {s['days_with_any_activity']} of {days}")
    print()

    sig = s["signals"]
    ryg = s["green_yellow_red"]

    def _signal(name: str, label: str) -> str:
        pct = sig.get(name)
        pct_str = f"{pct}%" if pct is not None else "-"
        return f"    [{ryg[name].ljust(7)}] {label.ljust(22)} {pct_str}"

    print(_signal("continuity_restored", "continuity restored"))
    print(_signal("return_rate", "return rate"))
    print(_signal("resume_quality", "resume quality"))
    print()
    # The directive's success line: someone uses Recall twice
    # voluntarily. The closest counter is "day_started>=2 in the 7d
    # window AND returns>=1". Print only when meaningful.
    if int(s["window"].get("day_started", 0)) >= 1:
        repeat = int(s["window"].get("day_started", 0)) >= 2
        returned = int(s["window"].get("returns", 0)) >= 1
        resumed = int(s["window"].get("recoveries_used", 0)) >= 1
        print(
            "    directive: "
            f"{'OK' if repeat else 'short'} repeat-use, "
            f"{'OK' if returned else 'short'} 1+ return, "
            f"{'OK' if resumed else 'short'} 1+ resume"
        )
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
    print("    alpha-health Phase 6E green/yellow/red panel (live read of alpha/)")
    print("    daily-loop   Phase 6F today/yesterday/7d + 3 signals (continuity / return / resume)")
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
    "alpha-health": cmd_alpha_health,
    "daily-loop": cmd_daily_loop,
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
