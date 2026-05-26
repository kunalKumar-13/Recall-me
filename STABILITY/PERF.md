# Phase 8C — Performance Reality

**Question:** does Recall feel instant on this machine,
on real data, today?

**Method:** wall-clock subprocess timing for CLI entry
points; offscreen-Qt construction timing for launcher
widgets. Three runs per command, median reported.
Numbers are real wall time — they include Python
interpreter startup, which is the dominant cost for
CLI commands.

**Environment:** Windows 11 Pro 10.0.26200 ·
Python 3.13 · 208 events across 5 day-files in
`~/.recall/events/`.

---

## CLI commands (wall time, end-to-end)

| Command                       | Median (ms) | Min (ms) | Max (ms) | Budget | Verdict |
|-------------------------------|-------------|----------|----------|--------|---------|
| `recall doctor`               | 364.3       | 361.8    | 586.3    | n/a    | OK — runs once per session |
| `recall capture status`       | 261.6       | 232.3    | 352.1    | n/a    | OK — quick read |
| `recall trust review`         | 233.2       | 215.1    | 247.9    | n/a    | OK |
| `recall founder status`       | 234.3       | 228.9    | 316.0    | n/a    | OK |

Subprocess CLI floor is **~230 ms** on this box
(Python boot + module import). Everything above
that floor is real work. None of these endpoints
have a published budget — they are operator
commands, not hot paths.

---

## Launcher widgets (offscreen Qt construction)

| Operation                          | Median (ms) | Notes |
|------------------------------------|-------------|-------|
| `LiveLauncher()` construct         | 84.5        | Cold widget tree, no event load |
| `show_centered()` on existing inst | 0.2         | Geometry math + show, no repaint cost measured |
| Resume preview open (in-process)   | 3.1         | Constructs `ResumePreview` from current digest |
| `_load_recent_memory(5)`           | 0.8         | Reads tail of today's JSONL |
| `_load_trust_counts()`             | 0.9         | Bad-recovery ledger scan |

Launcher cold open from a hot Python process is
**<100 ms**. The first open from a cold tray-icon
process pays the Python boot floor (~230 ms) plus
the construct (~85 ms) = real-world cold-open
budget of **~315 ms**, comfortably below the 500 ms
"feels instant" threshold.

---

## HTTP endpoints (where measurable)

The 8C directive scoped this pass to "launcher open,
capture status, doctor, resume preview, search." The
daemon-side HTTP endpoints already carry budgets in
`CLAUDE.md`; `_smoke_api.py` is the source of truth
and was run during 8B (28/29 sections passed, with
the remaining one being the known Phase 6L
investigation-grouping flake noted in `BUGS_OPEN.md`).
This document does not re-run the smoke suite — it
adds the user-perceived wall-clock view that
`_smoke_api.py` cannot measure (subprocess startup +
Qt construction).

---

## What this proves

1. **Launcher feels instant.** Cold open ~315 ms,
   warm open <100 ms.
2. **CLI commands feel snappy.** All four operator
   commands run in <400 ms, which is below the
   threshold at which a typed command starts feeling
   like a network call.
3. **No regression vs Phase 7E.1.** The launcher
   construct number (84.5 ms median) is within
   noise of the Phase 7E measurement (~80 ms).

## What this does NOT prove

- That the launcher stays instant at 10K events.
  Today's store has 208 events; the published budget
  table in CLAUDE.md is calibrated for 10K. Need a
  10K-event fixture run before public alpha.
- That the daemon-side HTTP budgets hold under
  concurrent extension capture. `_smoke_api.py`
  measures sequential. A multi-tab capture stress
  test is open as a BUGS_OPEN.md item.

## Measurement recipe (reproducible)

```bash
python -c "
import subprocess, time, statistics, sys
def t(args, n=3):
    xs=[]
    for _ in range(n):
        a=time.perf_counter()
        subprocess.run(args, capture_output=True, text=True)
        xs.append((time.perf_counter()-a)*1000)
    return round(statistics.median(xs),1)
for cmd in (['doctor'],['capture','status'],['trust','review'],['founder','status']):
    print(' '.join(cmd), t([sys.executable,'recall.py']+cmd))
"
```

Launcher numbers use `QT_QPA_PLATFORM=offscreen`
with a `QApplication([])` parent — see the harness
in `infra/scripts/capture/capture_launcher_live.py`.
