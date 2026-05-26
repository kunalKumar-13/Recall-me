"""Run Recall: `python recall.py`.

For boot diagnostics, set `RECALL_DEBUG=1` or pass `--debug`.
Import-phase failures always print a traceback regardless of the flag.
"""

from __future__ import annotations

import os
import sys
import time
import traceback


_DEBUG = (
    os.environ.get("RECALL_DEBUG", "").strip().lower() in {"1", "true", "yes", "on"}
    or "--debug" in sys.argv
)


def _log(msg: str) -> None:
    if _DEBUG:
        print(f"[boot] {msg}", file=sys.stderr, flush=True)


# Make stderr unicode-safe on Windows (cp1252 default would crash logging
# any time a path or traceback contains non-ASCII).
try:
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")  # type: ignore[attr-defined]
except (AttributeError, ValueError):
    pass


_log(f"recall.py starting (python {sys.version.split()[0]} on {sys.platform})")

# Fast path: `recall stats` is a local, read-only counts report
# (Phase 5E.1). It must not pay the cost of importing the launcher /
# recovery / UI stack, so it is dispatched before `app.main`.
if len(sys.argv) > 1 and sys.argv[1] == "stats":
    try:
        from app.core.stats import run_stats_cli
    except BaseException:
        print("[boot] [FAIL] importing app.core.stats", file=sys.stderr)
        traceback.print_exc(file=sys.stderr)
        sys.exit(1)
    raise SystemExit(run_stats_cli(sys.argv[2:]))

# Same fast path for `recall doctor` (Phase 5C) — local diagnostics.
if len(sys.argv) > 1 and sys.argv[1] == "doctor":
    try:
        from app.core.doctor import run_doctor_cli
    except BaseException:
        print("[boot] [FAIL] importing app.core.doctor", file=sys.stderr)
        traceback.print_exc(file=sys.stderr)
        sys.exit(1)
    raise SystemExit(run_doctor_cli(sys.argv[2:]))

# Same fast path for `recall founder` (Phase 5E.3) — operator CLI.
if len(sys.argv) > 1 and sys.argv[1] == "founder":
    try:
        from app.core.founder_cli import run_founder_cli
    except BaseException:
        print("[boot] [FAIL] importing app.core.founder_cli", file=sys.stderr)
        traceback.print_exc(file=sys.stderr)
        sys.exit(1)
    raise SystemExit(run_founder_cli(sys.argv[2:]))

# Phase 5J install-repair triad. `repair` / `reset` / `reinstall-check`
# all live in `app.core.install_repair` and are dispatched here so a
# tester can run them from a Command Prompt without booting the
# launcher.
if len(sys.argv) > 1 and sys.argv[1] in {"repair", "reset", "reinstall-check"}:
    try:
        from app.core.install_repair import (
            cli_repair,
            cli_reset,
            cli_reinstall_check,
        )
    except BaseException:
        print("[boot] [FAIL] importing app.core.install_repair", file=sys.stderr)
        traceback.print_exc(file=sys.stderr)
        sys.exit(1)
    _sub = sys.argv[1]
    _rest = sys.argv[2:]
    if _sub == "repair":
        raise SystemExit(cli_repair(_rest))
    if _sub == "reset":
        raise SystemExit(cli_reset(_rest))
    raise SystemExit(cli_reinstall_check(_rest))

# Phase 6Q — Continuity Truth. `recall inspect <id>` prints the
# deterministic ASCII summary of why the engine surfaced (or didn't
# surface) a given candidate. Read-only; no daemon required.
if len(sys.argv) > 1 and sys.argv[1] == "inspect":
    try:
        from app.core.inspect_cli import run_inspect_cli
    except BaseException:
        print("[boot] [FAIL] importing app.core.inspect_cli", file=sys.stderr)
        traceback.print_exc(file=sys.stderr)
        sys.exit(1)
    raise SystemExit(run_inspect_cli(sys.argv[2:]))

# Phase 6Q — `recall trust review` prints the bad-recovery ledger
# summary alongside the resume / silence rates. Local-only.
if len(sys.argv) > 1 and sys.argv[1] == "trust":
    try:
        from app.core.trust_cli import run_trust_cli
    except BaseException:
        print("[boot] [FAIL] importing app.core.trust_cli", file=sys.stderr)
        traceback.print_exc(file=sys.stderr)
        sys.exit(1)
    raise SystemExit(run_trust_cli(sys.argv[2:]))

# Phase 7D — `recall capture status` + `recall capture tail`. Two
# read-only audit commands; verify the capture pipeline is actually
# remembering events end-to-end. Local-only; daemon not required.
if len(sys.argv) > 1 and sys.argv[1] == "capture":
    try:
        from app.core.capture_cli import run_capture_cli
    except BaseException:
        print("[boot] [FAIL] importing app.core.capture_cli", file=sys.stderr)
        traceback.print_exc(file=sys.stderr)
        sys.exit(1)
    raise SystemExit(run_capture_cli(sys.argv[2:]))

# Phase 5K cohort CLI. `recall alpha create / status / report` writes
# to the repo-tracked `alpha/users/` tree; metadata only, never
# content (boundary in `alpha/users/README.md`).
if len(sys.argv) > 1 and sys.argv[1] == "alpha":
    try:
        from app.core.alpha_cli import run_alpha_cli
    except BaseException:
        print("[boot] [FAIL] importing app.core.alpha_cli", file=sys.stderr)
        traceback.print_exc(file=sys.stderr)
        sys.exit(1)
    raise SystemExit(run_alpha_cli(sys.argv[2:]))

_t0 = time.time()
_log(">> importing app.main")
try:
    from app.main import main
except BaseException:
    # Always loud on import failure — otherwise the user sees nothing.
    print("[boot] [FAIL] importing app.main", file=sys.stderr, flush=True)
    traceback.print_exc(file=sys.stderr)
    sys.stderr.flush()
    sys.exit(1)
_log(f"[OK] app.main imported ({int((time.time() - _t0) * 1000)}ms)")


if __name__ == "__main__":
    sys.exit(main())
