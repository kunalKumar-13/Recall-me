"""Install-side repair + reset + reinstall-check CLI.

Three commands a first user (or a maintainer triaging a tester) can
run from a Command Prompt without launching the desktop app:

    recall repair             Fix common install-side issues in place.
    recall reset              Wipe caches; keep config + events.
    recall reinstall-check    Tell the user whether a reinstall is safe.

All three are local, read-only-by-default reconnaissance plus a small
set of *named* recoveries. Nothing leaves the machine. Nothing in
`~/.recall/events/` or `~/.recall/config.json` is ever touched
unless the user passes `--full` (a `--full` reset is documented as a
data-wipe and prompts for confirmation in interactive mode).

Output is ASCII (Windows cp1252 safe), GREEN / YELLOW / RED, and
echoes the same severity vocabulary as `recall doctor` so a tester
can paste one screenshot of either and the founder reads it the
same way.

CLI:

    recall repair [--dry-run]
    recall reset [--full] [--yes]
    recall reinstall-check
"""

from __future__ import annotations

import json
import os
import shutil
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Optional

from .config import CONFIG_DIR, CONFIG_FILE, EVENTS_DIR

# Severity tokens; same width + meaning as `doctor`'s.
GREEN = "GREEN "
YELLOW = "YELLOW"
RED = "RED   "

# State-store files that are SAFE to delete (engine re-derives them).
# Anything not on this list is user data and is never wiped by
# `repair` or by `reset` without `--full`.
_DERIVED_FILES = (
    "resurfacing.json",   # surfacing counters; re-derive from events
    "threads.json",       # thread identity cache; re-derive
    "evolution.json",     # phase cache; re-derive
    "instance.lock",      # single-instance guard; safe to clear
)

# Things `repair` will offer to do on Windows. Each item is a
# `(name, probe, fix)` triple - `probe` returns a Check result, `fix`
# performs the action and returns a new Check result. `fix` is only
# called when `--dry-run` is absent and probe came back non-GREEN.
@dataclass
class Check:
    name: str
    state: str         # GREEN / YELLOW / RED
    detail: str        # one short line


# --------------------------------------------------------------- helpers


def _pid_alive(pid: int) -> bool:
    """Cross-platform PID liveness, same semantics as
    `doctor._pid_alive` (kept local to avoid a circular import)."""
    try:
        os.kill(pid, 0)
        return True
    except ProcessLookupError:
        return False
    except PermissionError:
        return True
    except OSError as e:
        wer = getattr(e, "winerror", None)
        if wer == 87:
            return False
        if wer == 5:
            return True
        return True


def _read_lock_pid() -> Optional[int]:
    lock = CONFIG_DIR / "instance.lock"
    if not lock.exists():
        return None
    try:
        return int(lock.read_text(encoding="utf-8").strip() or "0") or None
    except (OSError, ValueError):
        return None


# --------------------------------------------------------------- probes + fixes


def _probe_stale_lock() -> Check:
    pid = _read_lock_pid()
    if pid is None:
        return Check("instance lock", GREEN, "no lock file")
    if _pid_alive(pid):
        return Check("instance lock", GREEN, f"held by PID {pid} (alive)")
    return Check("instance lock", YELLOW,
                 f"stale lock (PID {pid} not alive)")


def _fix_stale_lock() -> Check:
    lock = CONFIG_DIR / "instance.lock"
    try:
        if lock.exists():
            lock.unlink()
    except OSError as e:
        return Check("instance lock", RED, f"could not remove lock ({e})")
    return Check("instance lock", GREEN, "stale lock removed")


def _probe_protocol() -> Check:
    """Is the `recall://` URL scheme registered on Windows?"""
    if sys.platform != "win32":
        return Check("recall:// protocol", YELLOW,
                     f"registration unverified on {sys.platform}")
    try:
        import winreg  # type: ignore[import-not-found]
    except ImportError:
        return Check("recall:// protocol", YELLOW, "winreg unavailable")
    try:
        with winreg.OpenKey(
            winreg.HKEY_CURRENT_USER, r"Software\Classes\recall"
        ):
            return Check("recall:// protocol", GREEN, "handler registered")
    except OSError:
        return Check("recall:// protocol", YELLOW,
                     "not registered (extension Open won't deep-link)")


def _fix_protocol() -> Check:
    """Register `recall://` against the running launcher's executable.

    Writes the same four registry values the installer's
    `[Registry]` section writes - just from a running install,
    in case the installer's section was not present at install time
    or got cleared.
    """
    if sys.platform != "win32":
        return Check("recall:// protocol", YELLOW,
                     f"cannot register on {sys.platform}")
    try:
        import winreg  # type: ignore[import-not-found]
    except ImportError:
        return Check("recall:// protocol", RED, "winreg unavailable")

    # Where Recall.exe lives. For a PyInstaller-frozen build that is
    # sys.executable; for a source run we fall back to a marker that
    # makes the protocol useful only after a real install.
    if getattr(sys, "frozen", False):
        exe = sys.executable
    else:
        # Source-tree runs can't reasonably register a protocol that
        # routes back to the same Python invocation. The right place
        # for that is the installer, not the running source.
        return Check("recall:// protocol", YELLOW,
                     "source-tree run; registration is the installer's job")

    quoted = f'"{exe}" "%1"'
    try:
        # HKCU\Software\Classes\recall  (URL handler root)
        with winreg.CreateKey(
            winreg.HKEY_CURRENT_USER, r"Software\Classes\recall"
        ) as k:
            winreg.SetValueEx(k, "", 0, winreg.REG_SZ, "URL:Recall protocol")
            winreg.SetValueEx(k, "URL Protocol", 0, winreg.REG_SZ, "")
        with winreg.CreateKey(
            winreg.HKEY_CURRENT_USER, r"Software\Classes\recall\DefaultIcon"
        ) as k:
            winreg.SetValueEx(k, "", 0, winreg.REG_SZ, f"{exe},0")
        with winreg.CreateKey(
            winreg.HKEY_CURRENT_USER,
            r"Software\Classes\recall\shell\open\command",
        ) as k:
            winreg.SetValueEx(k, "", 0, winreg.REG_SZ, quoted)
    except OSError as e:
        return Check("recall:// protocol", RED,
                     f"registry write failed ({e})")
    return Check("recall:// protocol", GREEN,
                 "handler registered (HKCU)")


def _probe_autostart() -> Check:
    """Is Recall set to launch on login on Windows?"""
    try:
        from . import autostart  # type: ignore[attr-defined]
    except ImportError:
        return Check("autostart", YELLOW, "autostart module unavailable")
    if not autostart.is_supported():
        return Check("autostart", YELLOW,
                     f"not wired on {sys.platform}")
    try:
        on = autostart.is_enabled()
    except OSError as e:
        return Check("autostart", YELLOW, f"could not query ({e})")
    if on:
        return Check("autostart", GREEN, "HKCU Run key set")
    # Either the installer's Startup shortcut or the Settings toggle
    # would normally set autostart; doctor surfaces both. For repair
    # we only ever write the Run key (the user-overridable surface).
    if sys.platform == "win32":
        startup = (
            Path.home()
            / "AppData" / "Roaming" / "Microsoft" / "Windows"
            / "Start Menu" / "Programs" / "Startup" / "Recall.lnk"
        )
        if startup.exists():
            return Check("autostart", GREEN,
                         "Startup-folder shortcut present (installer)")
    return Check("autostart", YELLOW, "off (no Run key, no shortcut)")


def _fix_autostart() -> Check:
    try:
        from . import autostart
    except ImportError:
        return Check("autostart", RED, "autostart module unavailable")
    if not autostart.is_supported():
        return Check("autostart", YELLOW,
                     f"not wired on {sys.platform}")
    ok = autostart.set_enabled(True)
    if ok:
        return Check("autostart", GREEN, "enabled (HKCU Run)")
    return Check("autostart", RED, "OS rejected the autostart write")


def _probe_config_dir() -> Check:
    if not CONFIG_DIR.exists():
        return Check("config dir", YELLOW, f"{CONFIG_DIR} missing")
    return Check("config dir", GREEN, str(CONFIG_DIR))


def _fix_config_dir() -> Check:
    try:
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        EVENTS_DIR.mkdir(parents=True, exist_ok=True)
    except OSError as e:
        return Check("config dir", RED, f"could not create ({e})")
    return Check("config dir", GREEN, f"{CONFIG_DIR} created")


# --------------------------------------------------------------- repair


_REPAIR_STEPS: list[tuple[
    Callable[[], Check], Optional[Callable[[], Check]]
]] = [
    (_probe_config_dir, _fix_config_dir),
    (_probe_stale_lock, _fix_stale_lock),
    (_probe_protocol, _fix_protocol),
    (_probe_autostart, _fix_autostart),
]


def _print_check(c: Check) -> None:
    print(f"  {c.state}  {c.name.ljust(22)}  {c.detail}")


def repair(dry_run: bool = False) -> int:
    """`recall repair` - probe each step, fix the non-GREEN ones.

    Returns 0 if all checks ended GREEN after repair; 1 otherwise.
    Never raises.
    """
    print()
    print("  Recall - repair" + ("  (dry run)" if dry_run else ""))
    print()
    worst = GREEN

    def _bump(state: str) -> None:
        nonlocal worst
        if state == RED or (state == YELLOW and worst == GREEN):
            worst = state

    for probe, fix in _REPAIR_STEPS:
        try:
            c = probe()
        except Exception as e:  # noqa: BLE001 - never raise out of repair
            c = Check(probe.__name__[7:], RED, f"probe crashed: {e}")
        _print_check(c)
        if c.state == GREEN:
            continue
        if dry_run or fix is None:
            # No fix attempted - the probe verdict is what we report.
            _bump(c.state)
            continue
        # Non-GREEN and we have a fix - run it.
        try:
            after = fix()
        except Exception as e:  # noqa: BLE001
            after = Check(c.name, RED, f"fix crashed: {e}")
        print(f"         ->  {after.state}  {after.detail}")
        _bump(after.state)
    print()
    if worst == GREEN:
        print("  All install-side checks GREEN.")
    elif worst == YELLOW:
        print("  Yellow rows remain. See the line above each.")
    else:
        print("  RED rows remain. Reinstall may be the fastest path.")
    print()
    return 0 if worst == GREEN else 1


# --------------------------------------------------------------- reset


def _confirm(prompt: str) -> bool:
    if not sys.stdin.isatty():
        return False
    try:
        ans = input(prompt + " [y/N] ").strip().lower()
    except (EOFError, KeyboardInterrupt):
        return False
    return ans in {"y", "yes"}


def reset(full: bool = False, yes: bool = False) -> int:
    """`recall reset` - clear derived caches, keeping config + events.

    `--full` adds events + config + chroma to the wipe (an effective
    factory reset; equivalent to `rm -rf ~/.recall/` but performed
    item-by-item with a confirmation prompt unless `--yes`).
    """
    print()
    print("  Recall - reset" + ("  (full)" if full else "  (caches only)"))
    print()
    if not CONFIG_DIR.exists():
        print(f"  Nothing to reset. {CONFIG_DIR} does not exist.")
        print()
        return 0

    if full and not yes:
        if not _confirm(
            f"This will delete everything under {CONFIG_DIR} "
            "(events, config, chroma, derived caches). Continue?"
        ):
            print("  Cancelled.")
            print()
            return 1

    removed: list[str] = []
    skipped: list[str] = []
    for name in _DERIVED_FILES:
        p = CONFIG_DIR / name
        if not p.exists():
            continue
        try:
            p.unlink()
            removed.append(name)
        except OSError as e:
            skipped.append(f"{name} ({e})")

    if full:
        # Wipe events/, chroma/, config.json.
        for name in ("events", "chroma"):
            p = CONFIG_DIR / name
            if not p.exists():
                continue
            try:
                shutil.rmtree(p, ignore_errors=False)
                removed.append(f"{name}/")
            except OSError as e:
                skipped.append(f"{name}/ ({e})")
        cfg = CONFIG_FILE
        if cfg.exists():
            try:
                cfg.unlink()
                removed.append("config.json")
            except OSError as e:
                skipped.append(f"config.json ({e})")

    if removed:
        print("  Removed:")
        for r in removed:
            print(f"    {r}")
    else:
        print("  Nothing to remove.")
    if skipped:
        print()
        print("  Could not remove:")
        for r in skipped:
            print(f"    {r}")
    print()
    return 0 if not skipped else 1


# --------------------------------------------------------------- reinstall-check


def reinstall_check() -> int:
    """`recall reinstall-check` - is a reinstall safe?

    A read-only verdict. Names what will survive a reinstall (events,
    config, indexed-folder list), what will not (caches), and the
    single thing the user could optionally back up before running an
    upgrade installer.
    """
    print()
    print("  Recall - reinstall-check")
    print()
    if not CONFIG_DIR.exists():
        print(f"  {CONFIG_DIR} does not exist. Reinstall is a fresh install.")
        print()
        return 0

    events_dir = EVENTS_DIR
    events_files = (
        list(events_dir.glob("*.jsonl")) if events_dir.exists() else []
    )
    chroma = CONFIG_DIR / "chroma"
    chroma_exists = chroma.exists()

    cfg_summary: str
    folders: list[str] = []
    if CONFIG_FILE.exists():
        try:
            data = json.loads(CONFIG_FILE.read_text(encoding="utf-8"))
            folders = list(data.get("indexed_folders") or [])
            cfg_summary = f"present ({len(folders)} folder(s) indexed)"
        except (OSError, ValueError) as e:
            cfg_summary = f"present but unreadable ({e})"
    else:
        cfg_summary = "absent (default settings will apply)"

    survives = [
        f"{len(events_files)} day file(s) in {events_dir}",
        f"config.json - {cfg_summary}",
    ]
    if chroma_exists:
        survives.append(
            "chroma/ index (will be re-validated on first launch)"
        )

    print("  Will survive a reinstall:")
    for s in survives:
        print(f"    GREEN  {s}")
    print()

    will_not = [
        "instance.lock (always recreated)",
        "resurfacing.json / threads.json / evolution.json (derived caches; re-built)",
    ]
    print("  Will be re-derived on first launch:")
    for s in will_not:
        print(f"    .....  {s}")
    print()

    print("  Optional manual backup (for the paranoid):")
    print(f"    cp -r {CONFIG_DIR} {CONFIG_DIR}.bak")
    print()

    if folders:
        print("  Indexed folders (the only ones Recall reads from):")
        for f in folders[:8]:
            print(f"    -  {f}")
        if len(folders) > 8:
            print(f"    ... +{len(folders) - 8} more")
        print()

    print("  Verdict:  Safe to reinstall. ~/.recall/ is yours; the installer")
    print("            never deletes it. Doctor + repair after the reinstall.")
    print()
    return 0


# --------------------------------------------------------------- CLI entry


def cli_repair(argv: list[str]) -> int:
    return repair(dry_run="--dry-run" in argv)


def cli_reset(argv: list[str]) -> int:
    return reset(full="--full" in argv, yes="--yes" in argv)


def cli_reinstall_check(argv: list[str]) -> int:
    _ = argv  # no flags today
    return reinstall_check()
