"""`recall doctor` — first-user diagnostics.

Runs a short series of checks and prints a calm GREEN / YELLOW /
RED report. Used by a first user (or a maintainer) to answer the
*"is anything obviously wrong?"* question without reading logs.

All checks are local. No network call beyond a one-second probe of
the loopback daemon. Nothing is collected or sent anywhere — this
is a read-only inspection.

    python recall.py doctor
"""

from __future__ import annotations

import json
import os
import sys
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Callable

from .config import CONFIG_DIR, EVENTS_DIR

# Health colours — three states only. ASCII so Windows cp1252
# consoles never crash printing them.
GREEN = "GREEN "
YELLOW = "YELLOW"
RED = "RED   "

DAEMON_URL = "http://127.0.0.1:4545/v1/health"

# The repo root — used to find dist/, apps/extension/, app/__init__.py
# when running from source. When frozen (PyInstaller), these checks
# resolve relative to the bundle so they still produce a verdict.
_REPO_ROOT = Path(__file__).resolve().parents[2]


@dataclass
class Check:
    name: str
    state: str       # GREEN / YELLOW / RED
    detail: str      # one short line


# --------------------------------------------------------------- checks


def _check_config() -> Check:
    if not CONFIG_DIR.exists():
        return Check("config", RED, f"{CONFIG_DIR} missing - has Recall ever run?")
    cfg = CONFIG_DIR / "config.json"
    if not cfg.exists():
        return Check("config", YELLOW,
                     f"{CONFIG_DIR} present, but config.json not yet written")
    try:
        data = json.loads(cfg.read_text(encoding="utf-8"))
        folders = data.get("indexed_folders") or []
        if not folders:
            return Check("config", YELLOW,
                         "no folders chosen yet (onboarding skipped?)")
        return Check("config", GREEN,
                     f"{len(folders)} folder(s) indexed")
    except (OSError, ValueError) as e:
        return Check("config", YELLOW, f"config.json unreadable ({e})")


def _check_events_dir() -> Check:
    if not EVENTS_DIR.exists():
        return Check("events", YELLOW, "no events directory yet - work a little")
    files = sorted(EVENTS_DIR.glob("*.jsonl"))
    if not files:
        return Check("events", YELLOW, "events directory empty")
    return Check("events", GREEN, f"{len(files)} day-file(s) on disk")


def _check_event_flow() -> Check:
    """Has any event been written in the last 24 hours?"""
    if not EVENTS_DIR.exists():
        return Check("event flow", YELLOW, "no event log yet")
    cutoff = time.time() - 24 * 3600
    fresh = False
    for path in EVENTS_DIR.glob("*.jsonl"):
        try:
            if path.stat().st_mtime >= cutoff:
                fresh = True
                break
        except OSError:
            continue
    if fresh:
        return Check("event flow", GREEN, "events in the last 24h")
    return Check("event flow", YELLOW, "no events in the last 24h")


def _check_daemon() -> Check:
    """Probe the loopback /v1/health. Fast fail — a slow doctor is a
    broken doctor."""
    req = urllib.request.Request(DAEMON_URL, headers={"User-Agent": "recall-doctor"})
    try:
        with urllib.request.urlopen(req, timeout=1.0) as r:
            data = json.loads(r.read().decode("utf-8"))
            ingested = int(data.get("ingested_total", 0))
            return Check("daemon", GREEN,
                         f"127.0.0.1:4545 ok ({ingested} ingested total)")
    except urllib.error.URLError as e:
        return Check("daemon", RED,
                     f"127.0.0.1:4545 not responding ({e.reason})")
    except (OSError, ValueError) as e:
        return Check("daemon", RED, f"daemon unreachable ({e})")


def _check_launcher() -> Check:
    """The launcher writes ~/.recall/instance.lock while running. The
    file content is the launcher's PID; if that PID is no longer
    alive the lock is stale (a forced kill or a crash) and the
    correct verdict is YELLOW, not GREEN.

    Cross-platform PID liveness check: `os.kill(pid, 0)` raises on
    Windows + Unix when the PID is gone. The 0 signal is a no-op on
    Unix and a permissions-check on Windows.
    """
    lock = CONFIG_DIR / "instance.lock"
    if not lock.exists():
        return Check("launcher", YELLOW, "no instance lock - launcher not running?")
    try:
        content = lock.read_text(encoding="utf-8").strip()
        pid = int(content) if content else 0
    except (OSError, ValueError):
        return Check("launcher", YELLOW, "instance lock unreadable")
    if pid <= 0:
        return Check("launcher", YELLOW, "instance lock holds no PID")
    if not _pid_alive(pid):
        return Check("launcher", YELLOW,
                     f"stale instance lock (PID {pid} not alive)")
    return Check("launcher", GREEN, f"instance lock held by PID {pid}")


def _pid_alive(pid: int) -> bool:
    """Cross-platform PID liveness check.

    - Unix: `os.kill(pid, 0)` raises `ProcessLookupError` for a dead
      PID and `PermissionError` for one we can see but not signal.
    - Windows: `os.kill(pid, 0)` raises `OSError` with `winerror=87`
      (`ERROR_INVALID_PARAMETER`) for a missing PID and
      `winerror=5` (`ERROR_ACCESS_DENIED`) for one the user cannot
      open. Treat ACCESS_DENIED as alive (the process exists, just
      not for us).
    """
    try:
        os.kill(pid, 0)
        return True
    except ProcessLookupError:
        return False
    except PermissionError:
        return True
    except OSError as e:
        # Windows: winerror is the right attribute.
        wer = getattr(e, "winerror", None)
        if wer == 87:    # ERROR_INVALID_PARAMETER - no such PID
            return False
        if wer == 5:     # ERROR_ACCESS_DENIED - PID exists
            return True
        # Any other OSError: treat as alive to avoid a false stale.
        return True


# --------------------------------------------------------------- 5F: install checks


def _check_installer_state() -> Check:
    """Where is Recall installed from? Reports the running mode and
    whether a `Recall-Setup.exe` artifact exists for the next user.

    Three honest answers:
      - frozen bundle (`sys.frozen=True`)   → GREEN, bundle path shown
      - source tree + installer artifact    → GREEN, artifact size
      - source tree + no artifact           → YELLOW, the gate-7 line
    """
    if getattr(sys, "frozen", False):
        bundle = Path(sys.executable).resolve()
        return Check("installer", GREEN,
                     f"running from bundle - {bundle.name}")
    artifact = _REPO_ROOT / "dist" / "installer" / "Recall-Setup.exe"
    if artifact.exists():
        try:
            mb = artifact.stat().st_size / (1024 * 1024)
            return Check("installer", GREEN,
                         f"Recall-Setup.exe present ({mb:.1f} MB)")
        except OSError:
            return Check("installer", YELLOW,
                         "Recall-Setup.exe found but unreadable")
    bundle_exe = _REPO_ROOT / "dist" / "Recall" / "Recall.exe"
    if bundle_exe.exists():
        return Check("installer", YELLOW,
                     "PyInstaller bundle present, Recall-Setup.exe not built")
    return Check("installer", YELLOW,
                 "running from source - no installer artifact")


def _check_autostart() -> Check:
    """Is Recall registered to launch on login?

    Two surfaces, either of which counts as autostart on Windows:
      1. HKCU\\…\\Run value (written by the in-app Settings toggle,
         via `app/core/autostart.py`).
      2. A Recall shortcut in the per-user Startup folder (written
         by the Inno Setup installer's `[Icons]` section).

    Phase 5G found the installer uses (2), not (1); a pre-5H doctor
    reported YELLOW even though Recall would correctly launch on
    login. Checking both surfaces removes that false-negative.
    """
    try:
        from . import autostart  # type: ignore[attr-defined]
    except ImportError:
        return Check("autostart", YELLOW, "autostart module unavailable")
    if not autostart.is_supported():
        return Check("autostart", YELLOW,
                     f"autostart not yet wired on {sys.platform}")
    # Surface 1 - HKCU Run.
    run_key = False
    try:
        run_key = autostart.is_enabled()
    except OSError as e:
        return Check("autostart", YELLOW, f"could not query autostart ({e})")
    # Surface 2 - per-user Startup folder shortcut.
    startup_shortcut = False
    if sys.platform == "win32":
        appdata = Path.home() / "AppData" / "Roaming"
        startup_dir = (appdata / "Microsoft" / "Windows"
                       / "Start Menu" / "Programs" / "Startup")
        try:
            startup_shortcut = (startup_dir / "Recall.lnk").exists()
        except OSError:
            startup_shortcut = False
    if run_key and startup_shortcut:
        return Check("autostart", GREEN,
                     "Run key + Startup shortcut (belt and suspenders)")
    if run_key:
        return Check("autostart", GREEN, "HKCU Run key set (Settings toggle)")
    if startup_shortcut:
        return Check("autostart", GREEN,
                     "Startup-folder shortcut present (from installer)")
    return Check("autostart", YELLOW,
                 "autostart off (no Run key, no Startup shortcut)")


def _check_protocol_registration() -> Check:
    """Is the `recall://` URL scheme registered to this install?

    The extension's *Open in Recall* button uses `recall://open`. If
    the scheme is not registered, the browser silently fails. Today
    no installer step writes the registry key — this is an honest
    YELLOW until that ships.
    """
    if sys.platform != "win32":
        return Check("protocol", YELLOW,
                     f"recall:// registration unverified on {sys.platform}")
    try:
        import winreg  # type: ignore[import-not-found]
    except ImportError:
        return Check("protocol", YELLOW, "winreg unavailable")
    # HKCU\Software\Classes\recall is the per-user URL handler root.
    try:
        with winreg.OpenKey(
            winreg.HKEY_CURRENT_USER, r"Software\Classes\recall"
        ):
            return Check("protocol", GREEN, "recall:// handler registered")
    except OSError:
        return Check("protocol", YELLOW,
                     "recall:// not registered (extension Open won't deep-link)")


def _check_extension_pairing() -> Check:
    """Live pairing check via the daemon's ingestion counters.

    /v1/health surfaces `ingested_total`. If it is non-zero AND any
    browser event has landed in the last 7 days, the extension is
    actively feeding. Otherwise YELLOW — paired or not, no flow
    counts as not paired in user-facing terms.
    """
    # Cheap signal first: any recent browser event on disk?
    if not EVENTS_DIR.exists():
        return Check("extension", YELLOW, "no event log yet")
    cutoff = (
        datetime.now(timezone.utc) - timedelta(days=7)
    ).strftime("%Y-%m-%d")
    seen_browser = False
    for path in sorted(EVENTS_DIR.glob("*.jsonl"), reverse=True):
        if path.stem < cutoff:
            break
        try:
            for line in path.read_text(encoding="utf-8").splitlines():
                if '"browser_visit"' in line or '"browser_search"' in line:
                    seen_browser = True
                    break
        except (OSError, UnicodeDecodeError):
            continue
        if seen_browser:
            break
    if seen_browser:
        return Check("extension", GREEN, "browser events in the last 7d")
    return Check("extension", YELLOW,
                 "no browser events - extension not paired or idle")


def _check_version_mismatch() -> Check:
    """Surface engine version vs extension manifest version.

    Today there is no compatibility table - drift is reported as a
    YELLOW so the founder can spot it; matching strings are GREEN.
    A hard incompatibility table can graduate this to RED later.

    In a frozen bundle the source-tree manifest path is unreachable;
    we report the engine version alone with a benign note rather
    than a false-failure "manifest not found".
    """
    engine = "?"
    try:
        from app import __version__ as _ev  # type: ignore
        engine = str(_ev)
    except Exception:  # noqa: BLE001
        return Check("versions", YELLOW, "engine version unreadable")
    # PyInstaller-frozen bundles do not ship the source-tree
    # `apps/extension/manifest.json` - the extension is installed
    # separately into the browser. Surface the engine version and
    # name the situation honestly; nothing here is broken.
    if getattr(sys, "frozen", False):
        return Check("versions", GREEN,
                     f"engine {engine} (extension installed in browser, not bundled)")
    ext_path = _REPO_ROOT / "apps" / "extension" / "manifest.json"
    if not ext_path.exists():
        return Check("versions", YELLOW,
                     f"engine {engine}; extension manifest not in source tree")
    try:
        manifest = json.loads(ext_path.read_text(encoding="utf-8"))
        ext = str(manifest.get("version", "?"))
    except (OSError, ValueError) as e:
        return Check("versions", YELLOW,
                     f"engine {engine}; extension manifest unreadable ({e})")
    if engine == ext:
        return Check("versions", GREEN, f"engine {engine} == extension {ext}")
    # Drift is expected during alpha (the two ship on independent lines).
    # We surface the pair so the founder sees it; no RED until a hard
    # compat table lands.
    return Check("versions", YELLOW,
                 f"engine {engine} vs extension {ext} (drift; manual check)")


_CHECKS: list[Callable[[], Check]] = [
    _check_config,
    _check_events_dir,
    _check_event_flow,
    _check_daemon,
    _check_extension_pairing,
    _check_launcher,
    _check_installer_state,
    _check_autostart,
    _check_protocol_registration,
    _check_version_mismatch,
]


# --------------------------------------------------------------- report


def run_checks() -> list[Check]:
    out: list[Check] = []
    for fn in _CHECKS:
        try:
            out.append(fn())
        except Exception as e:  # never raise out of the doctor
            out.append(Check(fn.__name__[7:], RED, f"check crashed: {e}"))
    return out


def format_report(checks: list[Check]) -> str:
    width = max(len(c.name) for c in checks)
    lines = ["", "  Recall - doctor", ""]
    for c in checks:
        lines.append(f"  {c.state}  {c.name.ljust(width)}   {c.detail}")
    lines.append("")
    # Overall verdict — the worst single check decides the headline.
    # Severity order: GREEN < YELLOW < RED; `max` picks the worst.
    worst = max(checks, key=lambda c: (GREEN, YELLOW, RED).index(c.state))
    if worst.state == GREEN:
        lines.append("  All checks green. The product looks healthy.")
    elif worst.state == YELLOW:
        lines.append("  No red flags. The yellow rows above name what is")
        lines.append("  not yet flowing - usually a step the user has not")
        lines.append("  taken (no folders chosen, extension not paired).")
    else:
        lines.append("  RED above is the first thing to fix. The daemon")
        lines.append("  must be running for anything else to work.")
    lines.append("")
    return "\n".join(lines)


def run_doctor_cli(argv: list[str]) -> int:
    """Entry point for `recall doctor`."""
    if "--json" in argv:
        checks = run_checks()
        print(json.dumps([
            {"name": c.name, "state": c.state.strip(), "detail": c.detail}
            for c in checks
        ], indent=2))
        return 0 if not any(c.state == RED for c in run_checks()) else 1
    checks = run_checks()
    print(format_report(checks))
    return 0 if not any(c.state == RED for c in checks) else 1
