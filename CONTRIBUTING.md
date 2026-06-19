# Contributing to Recall

Thanks for considering a contribution. Recall is a small project with a
narrow scope; the rules below exist to keep it that way.

## What we're optimizing for

- **Local-first stays absolute.** No telemetry, no analytics, no
  "phone home" features, no third-party endpoints outside the
  one-time embedding-model download. A PR that violates this gets
  declined regardless of merit.
- **Readability over cleverness.** The retrieval engine should remain
  readable in an afternoon. Prefer obvious code; resist abstractions
  designed for hypothetical future requirements.
- **Restraint.** Adding things is easy. The discipline is choosing
  what not to add. PRs that broaden scope (LLM chat, cloud sync,
  multi-user, online indexing) will be declined.

The [audit report](docs/engineering/AUDIT_REPORT.md) and the
[roadmap](README.md#roadmap) are the right places to find work that's
in scope.

## Local dev — one command

```powershell
# Windows / PowerShell
./infra/scripts/dev.ps1
```

```bash
# macOS / Linux
./infra/scripts/dev.sh
```

The script creates a venv, installs `requirements.txt`, runs the smoke
test, and launches the desktop app. It's idempotent — re-run any time.

Manual setup:

```bash
python -m venv .venv
source .venv/bin/activate          # or .venv\Scripts\activate on Windows
pip install -r requirements.txt
python _smoke_api.py                # API + perf check (~5 sec)
python recall.py                    # launches the app
```

Python 3.10+ is required. The first run downloads the embedding model
(~80 MB) into the Hugging Face cache. Subsequent runs are fully
offline.

### Demo mode (no indexing, no model download)

```bash
python recall.py --demo
```

Loads ten in-memory sample memories. Useful for working on the
launcher UI without touching real files.

### Boot diagnostics

```bash
python recall.py --debug
```

Per-stage timing on startup. Use this to find the slow step.

## Where things live

| Path | Purpose |
|---|---|
| `app/core/` | Pure-Python engine. No Qt imports here. |
| `app/ui/` | PyQt6 launcher + settings. Reads retrieval through the HTTP client only. |
| `api/` | FastAPI service (Phase 2A). Owns `/v1/*`. |
| `apps/extension/` | Chrome / Edge browser extension (MV3). |
| `apps/docs/` | Mintlify docs site (`docs.recall.computer`). |
| `apps/web/` | Next.js marketing site (`recall.computer`). |
| `infra/scripts/` | Dev bootstrap helpers (`dev.ps1`, `dev.sh`). |
| `packages/` | Shared internal libraries (currently empty by design — see `REPO_STRUCTURE.md`). |
| `assets/` | Screenshots, branding, demo scripts. |
| `scripts/` | Dev + build helpers. |
| `_smoke_api.py` | End-to-end API test. Run before any PR. |

## Conventions

### Python

- `from __future__ import annotations` at the top of every module.
- Type-annotate public functions and classes. Internal helpers can
  skip annotations if they obscure the code.
- Underscore-prefix anything not part of the module's public surface.
- Prefer dataclasses over dictionaries for typed structs.
- Logging via `logging.getLogger("recall.…")`. Never `print()` in
  production paths; the launcher's boot diagnostics are the
  exception.
- No comments that restate what the code does. Comments explain
  *why* — a constraint, a perf incident, a non-obvious tradeoff.

### Commit messages

Imperative present tense, lowercase first word after the type tag:

```
feat: add /v1/replay/day endpoint
fix: avoid double-scoring the event log in /v1/search
docs: rewrite api/introduction for the real endpoint set
chore: bump fastapi to 0.115
perf: cache searchable_text per Event
```

One change per commit. If a change requires updating docs + tests +
code, that's one commit, not three.

### Pull requests

- Reference the audit-report item or the issue number you're
  addressing.
- Run `python _smoke_api.py` and confirm all 12 sections pass.
- Touch the docs in the same PR if you changed user-visible
  behavior or an HTTP route.
- One PR per logical change. Don't mix a refactor with a feature.

## Testing

Recall does not have a unit-test suite yet — every change is
validated end-to-end through `_smoke_api.py`. That's the right shape
for a project this size; large refactors should expand the smoke
test rather than introducing a parallel `tests/` tree.

Specifically:

- **Smoke test must pass.** All 12 sections, perf budget green.
- **Visual changes** require a screenshot or a screen capture in the
  PR description. The reviewer should not have to run the app to
  see the result.
- **Performance-sensitive changes** require a measurement in the PR.
  See section 11 of `_smoke_api.py` for the existing 10K-event
  benchmark.

## What we won't merge

- Telemetry, analytics, error reporting, model-update pings, or any
  outbound network call outside the documented embedding-model
  download.
- Authentication layers for the loopback API. The bind is the
  boundary.
- LLM-chat-over-your-files. Recall is a memory layer, not an
  agentic system.
- Cloud sync, multi-user, or remote indexing.
- A new dependency that solves a problem you could have solved in
  100 lines of Python.

## Disclosure

Security issues: see [SECURITY.md](SECURITY.md). Don't open public
GitHub issues for security findings — email first.

## Code of conduct

See [CODE_OF_CONDUCT.md](docs/CODE_OF_CONDUCT.md).

---

Thanks for reading this far. If you're unsure whether something is
in scope, open a discussion before you start coding.
