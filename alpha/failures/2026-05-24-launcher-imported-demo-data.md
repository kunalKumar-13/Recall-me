# Launcher refused to boot: ModuleNotFoundError on demo_data

**Reporter:** alpha-001
**Date:**     2026-05-24
**Severity:** P0 (downgraded P1 after fix; see [`../../BUGS_OPEN.md`](../../docs/engineering/BUGS_OPEN.md) BUG-001)

## What happened

During the Phase 8C stability walk, attempting to
launch the desktop app yielded:

```
[boot] [FAIL] importing app.main
Traceback (most recent call last):
  File "...\recall.py", line 141, in <module>
    from app.main import main
  File "...\app\main.py", line 33, in <module>
    from .core.demo_data import DemoSearchEngine
ModuleNotFoundError: No module named 'app.core.demo_data'
```

The daemon process happened to still be running
from a previous boot, so HTTP endpoints stayed
green throughout. Only fresh launcher invocations
failed.

## What you expected

`python recall.py` boots the launcher, the tray
icon appears within ~3 seconds, and the import
chain resolves cleanly.

## What actually happened

The import chain failed at module load. The
launcher process exited 1 before constructing
the Qt window.

## Repro

1. After Phase 8B's archive sweep:
   `mv app/core/demo_data.py archive/launcher-old/`.
2. Open a fresh shell.
3. `python recall.py`.
4. Observe the traceback above.

## Notes

The 8B audit (`AUDIT/DEAD_CODE.md` +
`AUDIT/DELETE_PLAN.md`) classified
`demo_data.py` as dead based on a grep for
direct user-facing imports. The audit missed the
fact that `app/main.py:33` imports it
unconditionally at module load — only invoking
`DemoSearchEngine()` inside the `if DEMO_MODE`
branch. Lazy-import refactor + restore was the
fix.

**Fix:** Phase 8C restored the file from archive
and moved the import inside the `if DEMO_MODE`
branch in [`app/main.py:392`](../../app/main.py#L392).
Same approach applied to the `styles.py`
transitive (it's imported by live `onboarding.py`
+ `settings.py`).

**Lesson:** the next dead-code audit should grep
for **module-level** imports specifically, not
just call-site references. A function-level import
is dead if the function is dead; a module-level
import is alive whenever the module is loaded.

**Status:** closed. Verified via
`python -c "from app.main import main"` exit 0.
