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
