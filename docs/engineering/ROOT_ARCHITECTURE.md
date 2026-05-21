# Root architecture

This document is the **map** of how Recall's pieces fit together
across the repository. It is the answer to *"what runs where, and
what depends on what?"* — read it before reading any individual
subdirectory's source.

For *why* the repo is shaped this way, see
[`REPO_STRUCTURE.md`](REPO_STRUCTURE.md). For the engineering
charter and decision rules, see [`CLAUDE.md`](../../CLAUDE.md).

## Runtime topology

What's actually running when a user uses Recall:

```
┌────────────────────────────────────────────────────────────────┐
│                       USER'S MACHINE                           │
│                                                                │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Recall desktop process  (apps/desktop, Python)          │  │
│  │                                                          │  │
│  │   ┌───────────────┐    ┌──────────────────────────────┐  │  │
│  │   │  Launcher     │───▶│  Local memory API            │  │  │
│  │   │  (PyQt6,      │    │  (FastAPI on 127.0.0.1:4545) │  │  │
│  │   │   Ctrl+Space) │    │                              │  │  │
│  │   └───────────────┘    │  routes:                     │  │  │
│  │                        │   /v1/events/* (ingest)      │  │  │
│  │                        │   /v1/search                 │  │  │
│  │                        │   /v1/sessions/recent        │  │  │
│  │                        │   /v1/contexts/recent        │  │  │
│  │                        │   /v1/resurface/idle         │  │  │
│  │                        │   /v1/threads/recent         │  │  │
│  │                        │   /v1/threads/{id}/evolution │  │  │
│  │                        │   /v1/recovery/recent        │  │  │
│  │                        │   /v1/recovery/{id}/restore  │  │  │
│  │                        └──────┬───────────────────────┘  │  │
│  │                               │ reads/writes              │  │
│  │                               ▼                           │  │
│  │                        ┌──────────────────────────┐       │  │
│  │                        │   ~/.recall/             │       │  │
│  │                        │     events/*.jsonl        │       │  │
│  │                        │     threads.json          │       │  │
│  │                        │     evolution.json        │       │  │
│  │                        │     resurfacing.json      │       │  │
│  │                        │     chroma/               │       │  │
│  │                        │     config.json           │       │  │
│  │                        │     version.json          │       │  │
│  │                        └──────────────────────────┘       │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                ▲                               │
│                                │ POST /v1/events/*             │
│                                │ (loopback only)               │
│   ┌────────────────────────────┴────────────────────┐          │
│   │ Chrome / Edge (apps/extension, JS, MV3)         │          │
│   │   • content scripts capture page metadata       │          │
│   │   • service worker POSTs to 127.0.0.1:4545      │          │
│   │   • host_permissions locked to that one URL     │          │
│   └─────────────────────────────────────────────────┘          │
└────────────────────────────────────────────────────────────────┘

                          (no outbound)
```

**Three runtime processes, all local.** The desktop process and
the browser extension run on the user's machine; the launcher
binds the local API; the extension talks only to that one URL.
There is no fourth process, no cloud service, no shared
backend.

The **marketing site** (`apps/web`) and the **documentation
site** (`apps/docs`) are static deploys — they don't run on the
user's machine and don't talk to Recall in any way.

## System boundaries

| Boundary | Crosses | Stability |
|---|---|---|
| `/v1/*` HTTP API | Launcher ↔ extension (extension → API); future plugins | Versioned; semver-protected per [`VERSIONING.md`](../release/VERSIONING.md) |
| Event log JSONL schema | Engine layers + the user (file is hand-editable) | Versioned; the five canonical `kind` values + their payloads are stable |
| Launcher keybindings | User ↔ launcher | Stable per major version |
| `~/.recall/*.json` caches | Engine internals only | Best-effort across minors; safe to delete any time |
| Settings dialog labels | User ↔ launcher | Soft contract; can change wording, can't change behaviour silently |

## Dependency graph (current monorepo)

```
                 ┌──────────────────────┐
                 │  apps/extension      │  (MV3, JS)
                 └──────────┬───────────┘
                            │ HTTP POST
                            ▼
        ┌──────────────────────────────────────────┐
        │            apps/desktop                   │
        │                                           │
        │   recall.py                               │
        │     └─▶ app.main                          │
        │            ├─▶ app.core (events,          │
        │            │   sessions, microcontexts,   │
        │            │   resurfacing, threads,      │
        │            │   evolution, recovery,       │
        │            │   episodic, search, …)       │
        │            ├─▶ app.ui (launcher,          │
        │            │   widgets, settings)         │
        │            └─▶ api (services + main)      │
        │                                           │
        │   _smoke_api.py  ─▶ uses the same imports │
        └───────────────────────────────────────────┘

   apps/web        (Next.js — static, no engine deps)
   apps/docs       (Mintlify — static, no engine deps)
   infra/scripts   (dev bootstrap → calls apps/desktop)
   infra/installers (PyInstaller spec → builds apps/desktop)
```

**No cross-app Python imports.** `apps/desktop` imports only its
own `app.*` and `api.*` packages. `apps/web` and `apps/docs`
import nothing from the desktop tree; they are pure
documentation-and-marketing surfaces. `apps/extension` runs in
the browser sandbox and talks to the desktop only through the
HTTP API.

The runtime dependency direction is **always outward from the
engine**: extension → API → engine. The engine never reaches
into the extension or the browser.

## Engine layer hierarchy (inside `apps/desktop`)

The seven engine layers, in composition order, with their
location:

```
events       app.core.events          ~/.recall/events/*.jsonl
sessions     app.core.sessions        derived, no on-disk cache
contexts     app.core.microcontexts   derived, no on-disk cache
resurfacing  app.core.resurfacing     ~/.recall/resurfacing.json
threads      app.core.threads         ~/.recall/threads.json
evolution    app.core.evolution       ~/.recall/evolution.json
recovery     app.core.recovery        (derived, no cache)
```

Each layer reads only from layers below it. The composition
rule is sacred — see [`CLAUDE.md`](../../CLAUDE.md) § *"The sacred
hierarchy"*.

The HTTP API services (`api/services/*.py`) are thin facades
around the engine layers; they add HTTP-shaped methods + timing
logs and nothing else.

## Release ownership

| Subdirectory | Released when | By whom |
|---|---|---|
| `apps/desktop` | A signed tag on `main` (`vMAJOR.MINOR.PATCH`) | Release engineer, via the checklist in [`RELEASE.md`](../release/RELEASE.md) |
| `apps/extension` | Released in lockstep with `apps/desktop` until repo split (the `host_permissions` lockstep with `127.0.0.1:4545` makes independent releases unsafe). | Same |
| `apps/web` | Continuously deploys from `main` | Marketing surface; web maintainer |
| `apps/docs` | Continuously deploys from `main` | Docs maintainer |
| `infra/installers` | Re-runs on every `apps/desktop` tag | Release engineer |
| `infra/release` | Static; updated when the channel architecture changes | Release engineer |
| `infra/scripts` | Untagged; just the dev-bootstrap surface | Anyone |
| `packages/*` | Currently empty; release per-package once populated and extracted | TBD per package |

## Future extraction paths

The pseudo-monorepo is designed to split cleanly. Each
directory's extraction target is documented in
[`REPO_STRUCTURE.md`](REPO_STRUCTURE.md); the summary:

| Today | Future repo | Gate to split |
|---|---|---|
| `apps/desktop` + parts of `infra/installers` | `recall-core` | Launcher + extension shipping on independent cycles, or external embedders consuming `/v1/*` as a library |
| `apps/extension` | `recall-extension` | Firefox / Safari ports start shipping with separate review cycles |
| `apps/web` | `recall-web` | Marketing team becomes a separate contributor pool |
| `apps/docs` | `recall-docs` | Docs PR cadence drifts from engine cadence |
| `packages/*` | each its own published library | An external consumer needs a versioned dependency |

The day a directory needs its own repo, `git filter-repo` plus
the documented boundary is sufficient. No structural rewrites
required.

## Adding a new app or package

Before adding a new top-level directory:

1. Confirm it doesn't fit under an existing one. (Most things
   that feel like new apps are actually new modules under
   `apps/desktop/app/`.)
2. Read the [`CLAUDE.md`](../../CLAUDE.md) decision gate. If the
   proposed addition fails one of *continuity / inevitability /
   calmness / trust / speed*, it does not earn a directory.
3. If it survives, add a `README.md` to the new directory
   describing its responsibility, dependencies, and release
   cadence. Add a row to this file's tables.
4. Open the PR with a one-paragraph rationale.
