"""`recall alpha` — cohort management CLI for the alpha-001 era.

Three subcommands, all stdlib only, all writing to the
repo-tracked `alpha/users/` tree:

    recall alpha create <handle> --cohort <name>
    recall alpha status [--cohort <name>]
    recall alpha report [--cohort <name>]

The boundary is the same as
[`alpha/users/README.md`](../../alpha/users/README.md): the tree
holds **metadata only** — install date, platform, day-by-day
flags, drop reason. **Never URLs, filenames, queries, chat
content.** No automated push from a tester machine to this tree;
every entry is written by the founder running this CLI (or by
hand-editing the JSON).

ASCII-only output (Windows cp1252 safe). Never raises out: a
malformed status.json prints as YELLOW, never as a traceback.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Optional


# Layout. `_REPO_ROOT/alpha/users/` is the cohort tree.
_REPO_ROOT = Path(__file__).resolve().parents[2]
_USERS_DIR = _REPO_ROOT / "alpha" / "users"
_STATUS_TEMPLATE = _USERS_DIR / "_TEMPLATE" / "status.json"


# Five canonical cohorts. The CLI rejects anything outside this
# set so a typo doesn't silently create a sixth folder.
COHORTS = ("alpha-001", "alpha-002", "friends", "builders", "students")


# Status JSON fields the report knows how to surface.
@dataclass
class TesterRecord:
    handle: str
    cohort: str
    install_date: Optional[str]
    platform: Optional[str]
    install_ok: Optional[str]
    install_minutes: Optional[float]
    # Phase 6E adds three directive-named fields. Existing records
    # don't carry them — the loader defaults to None, so old
    # status.json files keep working without migration.
    installer_version: Optional[str]
    extension: Optional[str]
    day1: Optional[str]
    day2: Optional[str]
    day3: Optional[str]
    first_recovery: Optional[str]
    first_resume_ok: Optional[str]
    kept_using: Optional[str]
    wow_moment: Optional[str]
    confusion: Optional[str]
    drop_reason: Optional[str]
    feedback_returned: bool
    notes: str


# Field names the `update` subcommand will accept. Centralised so the
# CLI doesn't allow arbitrary writes and so the help text stays in
# sync with what the loader actually reads.
_UPDATABLE_FIELDS = (
    "platform",
    "installer",
    "installer_version",
    "extension",
    "install_ok",
    "install_minutes",
    "day1",
    "day2",
    "day3",
    "first_recovery",
    "first_resume_ok",
    "kept_using",
    "wow_moment",
    "confusion",
    "drop_reason",
    "feedback_returned",
    "notes",
)


def _load_status(path: Path) -> Optional[TesterRecord]:
    """Read a tester `status.json` into a TesterRecord, or None on
    parse failure (never raises)."""
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None
    if not isinstance(data, dict):
        return None
    g = data.get
    return TesterRecord(
        handle=str(g("handle") or ""),
        cohort=str(g("cohort") or ""),
        install_date=g("install_date"),
        platform=g("platform"),
        install_ok=g("install_ok"),
        install_minutes=g("install_minutes"),
        installer_version=g("installer_version"),
        extension=g("extension"),
        day1=g("day1"),
        day2=g("day2"),
        day3=g("day3"),
        first_recovery=g("first_recovery"),
        first_resume_ok=g("first_resume_ok"),
        kept_using=g("kept_using"),
        wow_moment=g("wow_moment"),
        confusion=g("confusion"),
        drop_reason=g("drop_reason"),
        feedback_returned=bool(g("feedback_returned") or False),
        notes=str(g("notes") or ""),
    )


def _list_cohorts(filter_cohort: Optional[str] = None) -> list[str]:
    if filter_cohort:
        return [filter_cohort] if filter_cohort in COHORTS else []
    if not _USERS_DIR.exists():
        return []
    return [c for c in COHORTS if (_USERS_DIR / c).exists()]


def _list_testers(cohort: str) -> list[Path]:
    """Folders inside a cohort dir that look like tester records
    (have a status.json). Sorted by folder name."""
    base = _USERS_DIR / cohort
    if not base.exists():
        return []
    out: list[Path] = []
    for child in sorted(base.iterdir()):
        if not child.is_dir():
            continue
        if (child / "status.json").exists():
            out.append(child)
    return out


# --------------------------------------------------------------- create


def cmd_create(argv: list[str]) -> int:
    """`recall alpha create <handle> --cohort <name>`.

    Copies the status.json template into
    `alpha/users/<cohort>/<handle>/`, fills `handle`,
    `cohort`, and `install_date: <today>`, leaves everything else
    null. Refuses to overwrite an existing tester folder.
    """
    if not argv or argv[0].startswith("-"):
        print("  usage: recall alpha create <handle> --cohort <name>")
        return 1
    handle = argv[0]
    cohort = _flag_value(argv, "--cohort")
    if not cohort:
        print("  --cohort required.  one of: " + ", ".join(COHORTS))
        return 1
    if cohort not in COHORTS:
        print(f"  unknown cohort '{cohort}'.  one of: " + ", ".join(COHORTS))
        return 1
    if not _STATUS_TEMPLATE.exists():
        print(f"  template not found: {_STATUS_TEMPLATE}")
        return 1
    if not _handle_ok(handle):
        print("  handle must be founder-assigned (e.g. tester-12); never PII.")
        return 1

    dest = _USERS_DIR / cohort / handle
    if dest.exists():
        print(f"  refusing to overwrite existing folder: {dest}")
        return 1

    try:
        dest.mkdir(parents=True, exist_ok=False)
    except OSError as e:
        print(f"  could not create {dest} ({e})")
        return 1

    try:
        template_data = json.loads(_STATUS_TEMPLATE.read_text(encoding="utf-8"))
    except (OSError, ValueError) as e:
        print(f"  could not read template ({e})")
        return 1

    template_data["handle"] = handle
    template_data["cohort"] = cohort
    template_data["install_date"] = date.today().isoformat()
    template_data.pop("_comment", None)

    status_path = dest / "status.json"
    try:
        status_path.write_text(
            json.dumps(template_data, indent=2) + "\n", encoding="utf-8"
        )
    except OSError as e:
        print(f"  could not write {status_path} ({e})")
        return 1

    print()
    print(f"  Created  {status_path.relative_to(_REPO_ROOT)}")
    print(f"  Cohort   {cohort}")
    print(f"  Handle   {handle}")
    print(f"  Today    {template_data['install_date']}")
    print()
    print("  Next:    fill in platform / install_ok / install_minutes as")
    print("           the tester reports.  Hand-edit the JSON or use")
    print("           `recall alpha status` to see the row.")
    print()
    return 0


# --------------------------------------------------------------- status


def cmd_status(argv: list[str]) -> int:
    """`recall alpha status [--cohort <name>]`.

    Prints a table of every known tester. Calm, one row per
    record, day-by-day flags shown as a short string like
    `YYY|R3` (day1+2+3 yes, first recovery Day 3). Returns 0
    even when no testers exist - the empty table is the right
    answer for an empty cohort.
    """
    cohort_filter = _flag_value(argv, "--cohort")
    cohorts = _list_cohorts(cohort_filter)
    print()
    print("  Recall - alpha status")
    if cohort_filter:
        print(f"  cohort: {cohort_filter}")
    print()

    total = 0
    returning = 0
    recoveries = 0
    drops = 0

    for cohort in cohorts:
        testers = _list_testers(cohort)
        if not testers:
            continue
        print(f"  {cohort}:")
        for folder in testers:
            r = _load_status(folder / "status.json")
            if r is None:
                print(f"    {folder.name.ljust(16)}  (status.json unreadable)")
                continue
            total += 1
            if (r.day1, r.day2, r.day3).count("yes") >= 2:
                returning += 1
            if r.first_recovery and r.first_recovery != "none yet":
                recoveries += 1
            if r.drop_reason and r.drop_reason not in ("n/a", "", None):
                drops += 1
            print(f"    {r.handle.ljust(16)}  {_format_row(r)}")
        print()

    if total == 0:
        print("  No testers recorded yet.")
        print("  Create one with:  recall alpha create <handle> --cohort <name>")
        print()
        return 0

    print(f"  Total testers:     {total}")
    print(f"  Returning (>=2 of 3 days): {returning}")
    print(f"  First-recovery seen:       {recoveries}")
    print(f"  Drops:                     {drops}")
    print()
    return 0


def _format_row(r: TesterRecord) -> str:
    """One-line summary of a tester. Compact, ASCII only."""

    def flag(v: Optional[str]) -> str:
        return {"yes": "Y", "no": ".", "unknown": "?"}.get(v or "", "-")

    days = flag(r.day1) + flag(r.day2) + flag(r.day3)
    first_rec = (r.first_recovery or "-")[:10]
    install = (r.install_ok or "-")[:7].ljust(7)
    plat = (r.platform or "-")[:14].ljust(14)
    feedback = "Y" if r.feedback_returned else "-"
    return (
        f"{plat}  install:{install}  days:{days}  "
        f"first-rec:{first_rec.ljust(10)}  feedback:{feedback}"
    )


# --------------------------------------------------------------- report


def cmd_report(argv: list[str]) -> int:
    """`recall alpha report [--cohort <name>]`.

    Aggregate counts across every tester record. The five
    directive-named outputs:

      - users
      - returning
      - recoveries
      - issues (= drops + install-fails + wrong recoveries)
      - blockers (= textual list of distinct drop_reason values)
    """
    cohort_filter = _flag_value(argv, "--cohort")
    cohorts = _list_cohorts(cohort_filter)

    users = 0
    returning = 0
    recoveries = 0
    install_fails = 0
    wrong_recoveries = 0
    drop_reasons: dict[str, int] = {}
    platforms: dict[str, int] = {}

    for cohort in cohorts:
        for folder in _list_testers(cohort):
            r = _load_status(folder / "status.json")
            if r is None:
                continue
            users += 1
            if (r.day1, r.day2, r.day3).count("yes") >= 2:
                returning += 1
            if r.first_recovery and r.first_recovery != "none yet":
                recoveries += 1
            if r.install_ok in ("no", "partial"):
                install_fails += 1
            if r.first_resume_ok == "wrong work":
                wrong_recoveries += 1
            if r.drop_reason and r.drop_reason not in ("n/a", "", None):
                drop_reasons[r.drop_reason] = drop_reasons.get(r.drop_reason, 0) + 1
            if r.platform:
                platforms[r.platform] = platforms.get(r.platform, 0) + 1

    issues = install_fails + wrong_recoveries + sum(drop_reasons.values())

    print()
    print("  Recall - alpha report")
    if cohort_filter:
        print(f"  cohort: {cohort_filter}")
    print()
    print(f"    users                    {users}")
    print(f"    returning (>=2 of 3 d)   {returning}")
    print(f"    first-recovery seen      {recoveries}")
    print(f"    issues                   {issues}")
    print(f"      install fails              {install_fails}")
    print(f"      wrong recoveries           {wrong_recoveries}")
    print(f"      drops (any drop_reason)    {sum(drop_reasons.values())}")
    print()
    if drop_reasons:
        print("    blockers (drop_reason counts):")
        for reason, n in sorted(drop_reasons.items(), key=lambda x: -x[1]):
            print(f"      {n} x {reason}")
        print()
    if platforms:
        print("    platforms:")
        for p, n in sorted(platforms.items(), key=lambda x: -x[1]):
            print(f"      {n} x {p}")
        print()

    # The five-humans / three-recoveries success line from the
    # directive. Print only when meaningful (>=1 user).
    if users:
        print(
            f"    directive target check:  "
            f"{'OK' if users >= 5 else 'short'} >=5 users, "
            f"{'OK' if recoveries >= 3 else 'short'} >=3 recoveries, "
            f"{'OK' if returning >= 2 else 'short'} >=2 returning"
        )
        print()
    return 0


# --------------------------------------------------------------- update


def cmd_update(argv: list[str]) -> int:
    """`recall alpha update <handle> --field value [--field value ...]`.

    Hand-applies the founder's latest read of a tester record. The
    accepted fields are listed in :data:`_UPDATABLE_FIELDS`; anything
    else is rejected (so a typo doesn't quietly write a sixth field
    that the report never sees).

    Lookup is cross-cohort by handle — the CLI walks every cohort
    folder until it finds a `<handle>/status.json`. The `--cohort`
    flag remains supported for cohort-ambiguous handles.

    Notable validations:
      - `install_minutes` is coerced to float (raises on bad input).
      - `feedback_returned` accepts `true` / `false` / `1` / `0`.
      - Empty-string values become `null` so the founder can clear
        a field they wrote yesterday.
    """
    if not argv or argv[0].startswith("-"):
        print("  usage: recall alpha update <handle> --field value [...]")
        print("  fields: " + ", ".join(_UPDATABLE_FIELDS))
        return 1

    handle = argv[0]
    cohort_filter = _flag_value(argv, "--cohort")
    folder = _find_tester(handle, cohort_filter)
    if folder is None:
        print(f"  tester not found: {handle}")
        print("  try: recall alpha status")
        return 1
    status_path = folder / "status.json"

    # Collect every --field value pair from the rest of argv.
    updates: dict[str, object] = {}
    i = 1
    while i < len(argv):
        token = argv[i]
        if token == "--cohort":
            i += 2  # already consumed by _flag_value
            continue
        if not token.startswith("--"):
            print(f"  unexpected token '{token}' — expected --field")
            return 1
        # Support `--field=value` and `--field value`.
        if "=" in token:
            name, _, value = token[2:].partition("=")
            i += 1
        else:
            name = token[2:]
            if i + 1 >= len(argv):
                print(f"  --{name} expects a value")
                return 1
            value = argv[i + 1]
            i += 2

        if name not in _UPDATABLE_FIELDS:
            print(f"  unknown field '{name}'")
            print("  fields: " + ", ".join(_UPDATABLE_FIELDS))
            return 1

        coerced = _coerce(name, value)
        if coerced is _COERCE_ERROR:
            print(f"  invalid value for --{name}: {value!r}")
            return 1
        updates[name] = coerced

    if not updates:
        print("  nothing to update (provide at least one --field value)")
        return 1

    try:
        data = json.loads(status_path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as e:
        print(f"  could not read {status_path} ({e})")
        return 1

    data.update(updates)
    try:
        status_path.write_text(
            json.dumps(data, indent=2) + "\n", encoding="utf-8"
        )
    except OSError as e:
        print(f"  could not write {status_path} ({e})")
        return 1

    print()
    print(f"  Updated  {status_path.relative_to(_REPO_ROOT)}")
    for k, v in updates.items():
        print(f"    {k.ljust(16)} = {v!r}")
    print()
    return 0


# --------------------------------------------------------------- export


def cmd_export(argv: list[str]) -> int:
    """`recall alpha export [--cohort <name>]`.

    JSON dump of the same metrics ``report`` prints in human form.
    Designed for the founder dashboard (or any consumer that wants
    the numbers in a machine-readable shape). The five directive
    fields ship as top-level keys:

      ``installs`` ``returning`` ``recoveries`` ``issues`` ``trust``

    Plus a ``drop_reasons`` map and a ``cohorts`` array of per-cohort
    summaries. **Counts only** — never URLs, filenames, queries, or
    any field the boundary rejects.
    """
    cohort_filter = _flag_value(argv, "--cohort")
    cohorts = _list_cohorts(cohort_filter)

    installs = 0
    returning = 0
    recoveries = 0
    install_fails = 0
    wrong_recoveries = 0
    drop_reasons: dict[str, int] = {}
    per_cohort: list[dict] = []

    for cohort in cohorts:
        c_installs = 0
        c_returning = 0
        c_recoveries = 0
        c_drops = 0
        for folder in _list_testers(cohort):
            r = _load_status(folder / "status.json")
            if r is None:
                continue
            installs += 1
            c_installs += 1
            if (r.day1, r.day2, r.day3).count("yes") >= 2:
                returning += 1
                c_returning += 1
            if r.first_recovery and r.first_recovery != "none yet":
                recoveries += 1
                c_recoveries += 1
            if r.install_ok in ("no", "partial"):
                install_fails += 1
            if r.first_resume_ok == "wrong work":
                wrong_recoveries += 1
            if r.drop_reason and r.drop_reason not in ("n/a", "", None):
                drop_reasons[r.drop_reason] = drop_reasons.get(r.drop_reason, 0) + 1
                c_drops += 1
        if c_installs:
            per_cohort.append({
                "cohort": cohort,
                "installs": c_installs,
                "returning": c_returning,
                "first_recoveries": c_recoveries,
                "drops": c_drops,
            })

    issues = install_fails + wrong_recoveries + sum(drop_reasons.values())

    # Trust % — the share of recovery_journal entries the founder
    # marked as "correct" (Resume opened the right work). Read from
    # the shared journal next to the cohort tree.
    trust = _compute_trust_pct()

    payload = {
        "schema": "alpha-export-v1",
        "generated_at": _today_iso(),
        "cohort_filter": cohort_filter,
        "installs": installs,
        "returning": returning,
        "recoveries": recoveries,
        "issues": issues,
        "trust": trust,
        "install_fails": install_fails,
        "wrong_recoveries": wrong_recoveries,
        "drop_reasons": drop_reasons,
        "cohorts": per_cohort,
    }
    print(json.dumps(payload, indent=2))
    return 0


def _compute_trust_pct() -> dict:
    """Read `alpha/recovery_journal.json` and aggregate the six
    directive-named outcomes. Returns a dict with the per-outcome
    counts + a single `pct_correct` percentage (0-100 or None if
    no data). All-local, never crashes."""
    journal_path = _REPO_ROOT / "alpha" / "recovery_journal.json"
    counts = {
        "shown": 0,
        "accepted": 0,
        "ignored": 0,
        "correct_silence": 0,
        "bad_recovery": 0,
        "resume_ok": 0,
    }
    try:
        data = json.loads(journal_path.read_text(encoding="utf-8"))
        entries = data.get("entries", [])
    except (OSError, ValueError):
        entries = []

    for e in entries:
        # Phase 6E ledger entries are tagged with one of six
        # vocabulary `kind` values. Pre-6E entries used the
        # `accepted` / `wrong` booleans; we map them onto the
        # new vocabulary so the older entries still count.
        kind = e.get("kind")
        if isinstance(kind, str) and kind in counts:
            counts[kind] = counts[kind] + 1
            continue
        # Legacy mapping.
        if e.get("accepted") is True and e.get("wrong") is True:
            counts["bad_recovery"] += 1
            counts["shown"] += 1
        elif e.get("accepted") is True and e.get("wrong") is False:
            counts["resume_ok"] += 1
            counts["accepted"] += 1
            counts["shown"] += 1
        elif e.get("accepted") is False:
            counts["ignored"] += 1
            counts["shown"] += 1

    total = counts["shown"]
    correct = counts["resume_ok"] + counts["correct_silence"]
    pct = int(correct / total * 100) if total > 0 else None
    return {**counts, "pct_correct": pct}


# --------------------------------------------------------------- replay (Phase 6F)


def cmd_replay(argv: list[str]) -> int:
    """`recall alpha replay <handle> [--cohort <name>]`.

    Print a calm event-only timeline for a single tester. Compiles
    three sources:

      1. ``status.json``         — install / day1-3 / first_recovery /
                                   first_resume_ok / wow_moment /
                                   confusion / drop_reason.
      2. ``recovery_journal.json`` — every per-Resume entry for this
                                   handle (kind / date / return_after_gap /
                                   time_to_resume / notes).
      3. (informational) the daily-loop summary the tester would
         have produced *if* this CLI lived on their machine — but
         only the founder's own machine has that data, so we never
         try to read it remotely.

    **No content** ever appears in the output. URLs, filenames,
    queries, and chat content are out of scope by contract; the
    timeline shows only event *kinds*, dates, and the
    handle-assigned label.
    """
    if not argv or argv[0].startswith("-"):
        print("  usage: recall alpha replay <handle> [--cohort <name>]")
        return 1

    handle = argv[0]
    cohort_filter = _flag_value(argv, "--cohort")
    folder = _find_tester(handle, cohort_filter)
    if folder is None:
        print(f"  tester not found: {handle}")
        print("  try: recall alpha status")
        return 1

    r = _load_status(folder / "status.json")
    if r is None:
        print(f"  status.json unreadable for {handle}")
        return 1

    timeline = _build_replay_timeline(handle, r)

    print()
    print(f"  Recall - alpha replay  ({handle}, cohort {r.cohort})")
    print()
    if not timeline:
        print("    (no recorded events for this tester yet)")
        print()
        return 0

    for entry in timeline:
        when = entry["date"].ljust(10)
        label = entry["label"]
        meta = entry.get("meta") or ""
        print(f"    {when}  {label.ljust(20)}  {meta}")
    print()
    # Quick verdict so the founder can scan one tester quickly.
    has_install = any(e["kind"] == "install" for e in timeline)
    has_activity = any(e["kind"] == "activity" for e in timeline)
    has_recovery = any(e["kind"] in ("recovery", "resume") for e in timeline)
    has_resume = any(e["kind"] == "resume" for e in timeline)
    has_return = any(e["kind"] == "return" for e in timeline)
    has_wow = any(e["kind"] == "wow" for e in timeline)
    print(
        "    coverage: "
        f"{'OK' if has_install else 'no'} install, "
        f"{'OK' if has_activity else 'no'} activity, "
        f"{'OK' if has_recovery else 'no'} recovery, "
        f"{'OK' if has_resume else 'no'} resume, "
        f"{'OK' if has_return else 'no'} return, "
        f"{'OK' if has_wow else 'no'} wow"
    )
    print()
    return 0


def _build_replay_timeline(handle: str, r: "TesterRecord") -> list[dict]:
    """Compose the per-tester replay rows. Pure projection — no
    content, just dates + event kinds + the handle's own labels.
    """
    rows: list[dict] = []

    def push(date_str: Optional[str], kind: str, label: str, meta: str = "") -> None:
        if not date_str or date_str in ("none yet", "n/a", ""):
            return
        rows.append({"date": date_str, "kind": kind, "label": label, "meta": meta})

    # 1. install
    if r.install_date:
        platform = r.platform or "-"
        push(r.install_date, "install", "install",
             f"{platform} ({r.install_ok or 'unknown'})")

    # 2. day-by-day activity flags
    for d_field, day_value in (("day1", r.day1), ("day2", r.day2), ("day3", r.day3)):
        if day_value == "yes":
            push(r.install_date, "activity", d_field, "kept_using=yes")

    # 3. first recovery (date is the recovery date, not install date)
    if r.first_recovery and r.first_recovery != "none yet":
        push(r.first_recovery, "recovery", "first recovery",
             f"resume={r.first_resume_ok or 'unknown'}")

    # 4. first resume — only if first_resume_ok is "yes"
    if r.first_resume_ok == "yes":
        push(r.first_recovery, "resume", "first resume", "")

    # 5. wow moment (Phase 6E)
    if r.wow_moment:
        push(r.install_date, "wow", "wow moment", r.wow_moment[:60])

    # 6. recovery_journal entries — every Resume decision the tester
    #    has reported. Honours the 6E vocabulary + the 6F additions
    #    (return_after_gap, time_to_resume).
    journal_path = _REPO_ROOT / "alpha" / "recovery_journal.json"
    try:
        data = json.loads(journal_path.read_text(encoding="utf-8"))
        entries = data.get("entries", [])
    except (OSError, ValueError):
        entries = []
    for e in entries:
        if e.get("tester") != handle:
            continue
        kind = str(e.get("kind") or "shown")
        # The replay flattens the six ledger kinds into three event
        # types — `recovery` (shown / ignored / correct_silence /
        # bad_recovery / accepted), `resume` (resume_ok), and
        # `return` (return_after_gap=true).
        if kind == "resume_ok":
            label = "resume_ok"
            etype = "resume"
        elif e.get("return_after_gap") is True:
            label = f"return -> {kind}"
            etype = "return"
        else:
            label = kind
            etype = "recovery"
        meta_parts: list[str] = []
        if e.get("recovered"):
            meta_parts.append(str(e["recovered"]))
        if e.get("time_to_resume") is not None:
            meta_parts.append(f"t2r={e['time_to_resume']}s")
        meta = " · ".join(meta_parts)
        push(e.get("date"), etype, label, meta)

    # Stable chronological order. None dates are filtered by push().
    rows.sort(key=lambda x: x["date"])
    return rows


# --------------------------------------------------------------- helpers

_COERCE_ERROR = object()


def _coerce(field: str, value: str):
    """Type-coerce a CLI string into the value shape `status.json`
    wants for `field`. Returns :data:`_COERCE_ERROR` on bad input
    instead of raising so the caller can print a friendly message."""
    if value == "":
        return None
    if field == "install_minutes":
        try:
            return float(value)
        except ValueError:
            return _COERCE_ERROR
    if field == "feedback_returned":
        v = value.strip().lower()
        if v in ("true", "1", "yes", "y"):
            return True
        if v in ("false", "0", "no", "n"):
            return False
        return _COERCE_ERROR
    # All other accepted fields are short strings.
    return value


def _find_tester(handle: str, cohort: Optional[str]) -> Optional[Path]:
    """Locate a tester folder by handle. When `cohort` is given the
    lookup is constrained; otherwise every cohort is searched in
    canonical order. Returns the folder path or None."""
    cohorts = _list_cohorts(cohort)
    for c in cohorts:
        candidate = _USERS_DIR / c / handle
        if (candidate / "status.json").exists():
            return candidate
    return None


def _today_iso() -> str:
    return date.today().isoformat()


def _flag_value(argv: list[str], flag: str) -> Optional[str]:
    """Read `--flag value` or `--flag=value`, return None if absent."""
    for i, a in enumerate(argv):
        if a == flag and i + 1 < len(argv):
            return argv[i + 1]
        if a.startswith(flag + "="):
            return a[len(flag) + 1:]
    return None


def _handle_ok(handle: str) -> bool:
    """A simple sanity check: handles are short, lowercase-ish, no
    PII-shaped strings. We reject @-signs (emails), dots that look
    like first.last, and obvious common-first-names heuristics is
    out of scope here; the founder is the second filter."""
    if not handle or len(handle) > 24:
        return False
    if "@" in handle or " " in handle:
        return False
    # Allow letters / digits / dashes / underscores only.
    return all(c.isalnum() or c in "-_" for c in handle)


# --------------------------------------------------------------- entry


def cmd_help(_argv: list[str]) -> int:
    print()
    print("  recall alpha - cohort management CLI")
    print()
    print("    create <handle> --cohort <name>            add a tester record")
    print("    update <handle> --<field> <value> ...      hand-apply latest read")
    print("    status [--cohort <name>]                   one row per tester")
    print("    report [--cohort <name>]                   aggregate counts (human)")
    print("    export [--cohort <name>]                   same counts as JSON")
    print("    replay <handle> [--cohort <name>]          per-tester event timeline (no content)")
    print()
    print("  Cohorts: " + ", ".join(COHORTS))
    print()
    print("  Updatable fields:")
    print("    " + ", ".join(_UPDATABLE_FIELDS))
    print()
    print("  Storage: alpha/users/<cohort>/<handle>/status.json")
    print("  Boundary: metadata only - never URLs / filenames / queries.")
    print()
    return 0


_COMMANDS = {
    "create": cmd_create,
    "update": cmd_update,
    "status": cmd_status,
    "report": cmd_report,
    "export": cmd_export,
    "replay": cmd_replay,
    "help": cmd_help,
    "--help": cmd_help,
    "-h": cmd_help,
}


def run_alpha_cli(argv: list[str]) -> int:
    """Entry point: argv excludes `recall alpha` (matches founder_cli style)."""
    if not argv:
        return cmd_help(argv)
    sub = argv[0]
    fn = _COMMANDS.get(sub)
    if fn is None:
        print(f"  unknown subcommand '{sub}'.")
        print("  try: recall alpha help")
        return 1
    return fn(argv[1:])
