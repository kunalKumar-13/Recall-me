"""Phase 8D — `recall demo` operator CLI.

One-command demo seed + reset, dispatched ahead of
the launcher import in `recall.py` so a tester can
prime a fresh box without booting the Qt UI.

Subcommands:

    recall demo run         seed the deterministic demo event log
                            (idempotent; --force to reseed)
    recall demo reset       remove the demo event log + marker
    recall demo status      print whether the demo is seeded + counts

The seeder writes to `~/.recall/events-demo/`, never
the user's real `~/.recall/events/`. Boundary
enforced by `demo_seed.DEMO_EVENTS_DIR`.
"""

from __future__ import annotations

import argparse
import json
import sys
from typing import Sequence

from . import demo_seed


def _cmd_run(args: argparse.Namespace) -> int:
    base = demo_seed.seed(force=bool(args.force))
    meta_path = base / demo_seed._MARKER_NAME  # type: ignore[attr-defined]
    print(f"demo seeded -> {base}")
    if meta_path.exists():
        try:
            meta = json.loads(meta_path.read_text(encoding="utf-8"))
            print(f"  events  = {meta.get('event_count')}")
            print(f"  sessions= {meta.get('session_count')}")
            print(f"  version = {meta.get('version')}")
        except (OSError, ValueError):
            pass
    print()
    print("Next:")
    print("  set RECALL_DEMO_MODE=1   (PowerShell: $env:RECALL_DEMO_MODE=1)")
    print("  python recall.py         # launcher reads the demo log")
    return 0


def _cmd_reset(_args: argparse.Namespace) -> int:
    demo_seed.reset()
    print(f"demo reset -> {demo_seed.DEMO_EVENTS_DIR} cleared")
    return 0


def _cmd_status(_args: argparse.Namespace) -> int:
    base = demo_seed.DEMO_EVENTS_DIR
    seeded = demo_seed.is_already_seeded(base)
    print(f"demo dir : {base}")
    print(f"seeded   : {seeded}")
    if seeded:
        marker = base / demo_seed._MARKER_NAME  # type: ignore[attr-defined]
        try:
            meta = json.loads(marker.read_text(encoding="utf-8"))
            for k in ("version", "seeded_at", "event_count", "session_count"):
                print(f"  {k:14s}= {meta.get(k)}")
        except (OSError, ValueError):
            pass
    if base.exists():
        files = sorted(base.glob("*.jsonl"))
        print(f"day-files: {len(files)}")
        for f in files:
            try:
                rows = sum(1 for _ in f.read_text(encoding="utf-8").splitlines() if _)
            except OSError:
                rows = 0
            print(f"  {f.name}  {rows} rows")
    return 0


def run_demo_cli(argv: Sequence[str]) -> int:
    parser = argparse.ArgumentParser(
        prog="recall demo",
        description="Seed / reset / inspect Recall's deterministic demo event log.",
    )
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_run = sub.add_parser("run", help="seed the demo event log")
    p_run.add_argument("--force", action="store_true",
                       help="reseed even if the marker file says we're current")
    p_run.set_defaults(func=_cmd_run)

    p_reset = sub.add_parser("reset", help="clear the demo event log + marker")
    p_reset.set_defaults(func=_cmd_reset)

    p_status = sub.add_parser("status", help="print seed status + counts")
    p_status.set_defaults(func=_cmd_status)

    args = parser.parse_args(list(argv))
    return int(args.func(args))


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(run_demo_cli(sys.argv[1:]))
