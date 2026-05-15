# `apps/desktop` — the Recall desktop application

This directory is the **target home** for the Recall desktop
tree: the Python `app/` engine, the FastAPI `api/` service, the
launcher entry point (`recall.py`), the smoke test
(`_smoke_api.py`), and the PyInstaller spec (`recall.spec`).

## Current state — Phase 4B

The Python tree currently lives **at the repository root** and is
not yet relocated under this directory. This is deliberate. See
[REPO_STRUCTURE.md](../../REPO_STRUCTURE.md) §
*"Why the Python tree is still at the root"* for the rationale
and the migration plan.

### Why

The brief that introduced the pseudo-monorepo refactor said two
things at once:

> *"Preserve all existing functionality. Do NOT rewrite working
> systems unnecessarily."*
> *"Preserve release simplicity. One command should still run
> the product."*

Moving the Python tree under `apps/desktop/` requires
co-ordinated updates to:

- the PyInstaller spec's relative paths (`app/assets/icon.ico`,
  data files, hidden imports)
- the dev scripts' `cd` targets
- every doc that references a Python file by path
- the smoke test's working-directory assumptions

…and verifying the result on Windows + macOS + Linux against a
working PyInstaller build (which the unit smoke test doesn't
exercise). That cross-platform verification is the gate; it is
not safe to perform in a single landing pass.

### What's in this directory today

Just this README and (eventually) a small set of files that don't
need to wait for the Python move:

- migration notes once the move starts
- per-OS build instructions when they diverge

### Migration plan

When the Python tree relocates:

1. `git mv app apps/desktop/app`
2. `git mv api apps/desktop/api`
3. `git mv recall.py apps/desktop/recall.py`
4. `git mv _smoke_api.py apps/desktop/_smoke_api.py`
5. `git mv recall.spec apps/desktop/recall.spec`
6. `git mv requirements.txt apps/desktop/requirements.txt`
7. Update `apps/desktop/recall.spec` to use `SPECPATH` for
   spec-relative paths.
8. Update `infra/scripts/dev.ps1` and `dev.sh` to `cd
   apps/desktop` before invoking Python.
9. Update README + CLAUDE.md repo map to point at the new paths.
10. Run `python apps/desktop/_smoke_api.py` and confirm all 29
    sections pass.
11. Build `pyinstaller apps/desktop/recall.spec` on at least one
    of the three target OSs and confirm the executable boots.

The migration is mechanical once the gate (cross-platform
PyInstaller verification) is cleared.
