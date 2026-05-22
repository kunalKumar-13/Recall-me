# CLAUDE.md — Recall engineering charter

This file is the working contract for anyone (human or model) writing
code in this repository. It is short on purpose. If you disagree with
something written here, write a discussion comment before changing it.

---

## What Recall is

Recall is a **local-first continuity operating system**.

It reconstructs what the user was mentally working on across files,
the browser, chat tools, and time. It is *not* an AI memory assistant,
not a semantic search app, not a productivity dashboard, not a
chatbot, not an agent framework. The product makes one claim:

> A continuity layer for your own thinking is only useful if it stays
> on your machine.

Every architectural decision is in service of that claim.

---

## The sacred hierarchy

These seven layers are the engine. They compose strictly upward.
Each one reads from the one below and never the other way around.
Never collapse them. Never rewrite a stable layer for cosmetic
reasons.

```
events     →  raw capture                     (app/core/events.py)
sessions   →  30-min temporal groupings       (app/core/sessions.py)
contexts   →  topic-coherent sub-blocks       (app/core/microcontexts.py)
resurfacing→  query-time idle surfacing       (app/core/resurfacing.py)
threads    →  persistent topic identity       (app/core/threads.py)
evolution  →  chronological phases of a thread (app/core/evolution.py)
recovery   →  resumable work + one-click       (app/core/recovery.py)
```

A new layer is acceptable only when:

1. It cannot be expressed as a tweak to an existing layer.
2. It is *purely additive* — every downstream artifact keeps working
   if the new layer is deleted.
3. It has its own perf budget, cache strategy, disable flag, and
   architecture doc.

The retrieval pipeline (`/v1/search`) and the launcher idle digest
both read across these layers; they are *consumers*, not part of the
hierarchy.

---

## Global engineering rules

1. **Determinism.** Same events in → same outputs out. No
   randomness, no learned weights, no probabilistic assignment in
   any production path. If you need entropy, derive it from the data.

2. **Local-first.** No cloud, no telemetry, no hidden inference,
   no model-update pings. The only outbound network call is the
   one-time embedding-model download on first run. ChromaDB and
   Hugging Face telemetry are explicitly disabled at boot.

3. **Inspectable.** All artifacts on disk are JSON or JSONL —
   plain text, hand-editable, auditable with `cat`. State lives
   entirely in `~/.recall/`. Deleting the folder is a full reset.

4. **Performance budgets are part of the API.** Every endpoint
   declares its budget; smoke-test sections enforce it.

   | Endpoint | Budget (10K events, server-side median) |
   |---|---|
   | `GET /v1/search` | <100 ms wall, <60 ms server |
   | `GET /v1/resurface/idle` | <25 ms server |
   | `GET /v1/threads/recent` | <50 ms server |
   | `GET /v1/threads/{id}/evolution` | <70 ms server (median) |
   | `GET /v1/recovery/recent` | <80 ms wall (median) |
   | `POST /v1/recovery/{id}/restore` | <10 ms |
   | `POST /v1/events/{kind}` | <2 ms |
   | `POST /v1/replay/day` | <5 ms per file |
   | `GET /v1/health` | <1 ms |

   A regression past the budget is a bug, not a slowdown. Profile
   before you optimize; never optimize from intuition alone.

5. **Calm UX.** No badges, no dopamine mechanics, no notifications,
   no gamification, no auto-playing animation, no dashboards. The
   launcher row sets the visual baseline: a single hairline marker,
   plain text, one dim time label. New surfaces must read as quieter
   than the existing ones, not louder.

6. **Continuity-first.** Optimize for *"what was I mentally working
   on?"* — never for *"what keyword did I type?"* When a feature
   could answer either question, pick the continuity framing.

7. **Reduce complexity.** Prefer heuristics over models. Prefer
   composable pipelines over giant abstractions. Prefer additive
   modules over rewrites. Prefer pure functions over stateful
   objects. Three obvious lines is better than a premature
   abstraction.

8. **Documentation is part of the work.** Every change updates:
   - the code,
   - the relevant `docs/architecture/*.mdx`,
   - the README if it touches the API or the layer hierarchy,
   - the smoke test if it adds a route or a budget,
   - the audit report if it leaves debt.

9. **Every phase ships with:**
   - smoke-test coverage (`_smoke_api.py`),
   - perf budget assertion,
   - edge-case handling (empty input, transport failure, disable
     flag, missing identity, OS error),
   - anti-noise protections (thresholds, dedupe, max counts),
   - disable + clear flows surfaced in Settings,
   - debug-only explanation surfaces (`why` lines, signals dict,
     gated on `RECALL_DEBUG` or — for restoration specifically —
     `RECALL_EXPLAIN_RECOVERY`).

10. **Aesthetic references:** Stripe, Linear, Raycast, Tailscale,
    SQLite. Never generic AI SaaS, never crypto, never dashboard
    product.

11. **Product direction.** Recall evolves toward an *operating layer
    for unfinished thought*. Not another assistant.

12. **Decision gate for any new feature:**
    - Does this improve continuity?
    - Does this improve inevitability?
    - Does this preserve calmness?
    - Does this preserve trust?
    - Does this preserve speed?

    If the answer to any of those is no, **do not build it**.

13. **Maintenance is part of the role.** Refactor when systems
    drift. Delete dead code when it stops earning its weight. Tighten
    wording when terminology splits.
    [AUDIT_REPORT.md](docs/engineering/AUDIT_REPORT.md) tracks the standing list of
    cleanups — work through it the same way you work through tickets.

14. **Build like Recall could become critical cognitive
    infrastructure.** Quiet, inevitable, minimal, precise,
    long-lived.

15. **Productize, don't prototype.** Phase 4A onward, every
    change carries the question: *"Would someone trust this
    enough to leave it running all day for years?"* If not,
    don't ship it. Concretely:
    - Errors are *quiet recoverable states*, never raw
      tracebacks. The launcher must never crash on a missing
      file, a port collision, or a stale extension.
    - Empty states earn copy. A blank header strip is worse
      than a one-line explanation of why it's empty.
    - Trust surfaces explain themselves. Every active engine
      offers a *why am I seeing this?* path (`RECALL_DEBUG=1`
      hover overlays, `RECALL_EXPLAIN_RECOVERY=1` for the
      restoration path).
    - Settings labels are honest about *what* and *why* — never
      "Enable AI memory", always "Capture browser activity to
      ~/.recall/events".
    - The release ladder (stable / preview / nightly) lives in
      [`RELEASE.md`](docs/release/RELEASE.md). Don't ship a feature with
      undeclared rollout discipline.

---

## Things we will not build

These are not on the roadmap and PRs adding them will be declined:

- LLM chat over your files.
- Cloud sync. Multi-user. Remote inference.
- A recommendation feed.
- Analytics, telemetry, error reporting, model-update pings.
- Notification spam ("you have N unfinished threads!").
- Auth on the loopback API. The bind is the boundary.
- Embeddings on any layer above events (file search is the *only*
  embeddings path, and it stays that way).

If a contributor is uncertain whether something is in scope, open a
discussion before writing code.

---

## Repository map

```
recall/
├── apps/
│   ├── desktop/               (target home — Python tree currently
│   │                           at repo root; see
│   │                           apps/desktop/README.md)
│   ├── web/                   Next.js marketing site
│   ├── docs/                  Mintlify docs site
│   └── extension/             Chrome / Edge MV3 extension
│
├── packages/
│   ├── shared/                shared constants + vocabulary
│   ├── design-system/         tokens + UI primitives
│   └── contracts/             API + event schemas
│
├── infra/
│   ├── installers/            installer specs + signing notes
│   ├── release/               release pipeline assets
│   └── scripts/               dev.ps1 / dev.sh / build_icon.py
│
├── assets/                    screenshots / branding / demos
├── archive/                   deprecated work
│
├── ROOT_ARCHITECTURE.md       system boundaries + dependency graph
├── REPO_STRUCTURE.md          why pseudo-monorepo + split criteria
└── …
```

The Python desktop tree currently lives at the **repo root**
(migrating under `apps/desktop/` once cross-platform PyInstaller
verification is performed — see
[`apps/desktop/README.md`](apps/desktop/README.md)):

```
├── app/
│   ├── core/                  Pure-Python engine — *no Qt imports*
│   │   ├── config.py          ~/.recall/ paths + Config dataclass
│   │   ├── events.py          EventLogger + EventStore (JSONL)
│   │   ├── episodic.py        Keyword + recency + kind-hint scorer
│   │   ├── sessions.py        Session reconstructor
│   │   ├── microcontexts.py   Micro-context reconstructor
│   │   ├── resurfacing.py     Idle-launcher continuity surface
│   │   ├── threads.py         Persistent topic identity
│   │   ├── evolution.py       Chronological phases inside a thread
│   │   ├── recovery.py        Resumable work + one-click restoration
│   │   ├── demo_seed.py       Deterministic demo-mode seeder
│   │   ├── parsers/chunker/embeddings/db/indexer/search.py
│   │   ├── ingest.py          Ingest validators (shared with api/)
│   │   └── api_client.py      Stdlib-urllib client used by the launcher
│   ├── ui/                    PyQt6 launcher + settings + widgets + tray
│   └── main.py                Process wiring (single-instance lock)
├── api/                       FastAPI service (Phase 2A+)
│   ├── main.py                create_app + APIService
│   ├── schemas.py             Pydantic request/response models
│   ├── logging_config.py      Structured logging
│   └── services/              ingestion / retrieval / reconstruction /
│                              resurfacing / threads / evolution /
│                              recovery / storage
├── _smoke_api.py              29-section end-to-end test + perf budgets
├── recall.py                  CLI entry point
├── recall.spec                PyInstaller spec
└── requirements.txt
```

State lives in `~/.recall/`:

| File / directory | Purpose | Safe to delete? |
|---|---|---|
| `events/YYYY-MM-DD.jsonl` | Append-only event log | Loses history |
| `chroma/` | Vector index | Re-indexes from folders |
| `config.json` | Folder list + toggles | Resets settings |
| `resurfacing.json` | Surfacing counters | Yes |
| `threads.json` | Thread identity cache | Yes (ids re-derive) |
| `evolution.json` | Phase cache | Yes |
| (no recovery file) | Recovery is derived on demand | n/a |
| `instance.lock` | Single-instance guard | Yes |

---

## Conventions

### Python

- `from __future__ import annotations` at the top of every module.
- Type-annotate public functions. Internal helpers may skip
  annotations only if they obscure intent.
- Underscore-prefix anything not part of the module's public
  surface.
- Comments explain *why*, never *what*. Code already tells you
  what. Comments rot; intent does not.
- No `print()` in production paths. Use
  `logging.getLogger("recall.…")`. The launcher's boot diagnostics
  are the only exception.
- Logger must never raise. Wrap all I/O. The product runs even when
  the disk is full.
- Prefer dataclasses over dicts for typed structs.
- `os.environ.get(...)` is read at *module load* if the result is
  static (e.g., `RECALL_DEBUG`). Never on the hot path.

### Commits

Imperative, lowercase after the type tag:

```
feat: add /v1/threads/{id}/evolution
fix: avoid double-scoring the event log in /v1/search
docs: rewrite api/introduction for the real endpoint set
perf: cache searchable_text per Event
chore: bump fastapi to 0.115
```

One logical change per commit. If a change touches code + docs +
tests, that's one commit, not three.

### Pull requests

- Reference the audit-report item or issue number.
- Run `python _smoke_api.py` and confirm all sections pass.
- Touch the relevant docs in the same PR.
- For perf-sensitive work, paste the measured numbers in the PR.

---

## Verifying changes

```bash
# Full end-to-end test (29 sections, ~5s)
python _smoke_api.py

# Single-command dev bootstrap
./infra/scripts/dev.ps1      # Windows / PowerShell
./infra/scripts/dev.sh       # macOS / Linux

# Boot diagnostics (per-stage timing)
python recall.py --debug

# Demo mode (no model download, no real indexing)
python recall.py --demo
```

`_smoke_api.py` is the source of truth for endpoint behavior. If you
change an endpoint and the smoke test still passes, you didn't change
the endpoint enough; if you add an endpoint without a smoke section,
you didn't add the endpoint.

Perf assertions are intentionally tight. A failing perf section is a
real regression — fix the code, not the budget.

---

## Naming and terminology

Pick one word per concept. The current mapping:

| Word | Meaning | Where it lives |
|---|---|---|
| **event** | One captured action | JSONL log, API, scoring code |
| **moment** | An event from the user's mental POV | docstrings, episodic results |
| **memory** | A moment from the user's mental POV in user-facing copy | UI strings, marketing, docs |
| **session** | 30-min temporal grouping | sessions.py, sessions API |
| **micro-context** | Topic-coherent slice of a session | microcontexts.py, contexts API |
| **resurfacing** | Idle-time surfacing of unfinished work | resurfacing.py, digest section ("On your radar") |
| **thread** | Persistent topic identity over time | threads.py, threads API |
| **phase** / **evolution** | A coherent period inside a thread | evolution.py, evolution API |
| **recovery** | Resumable work + one-click restoration | recovery.py, recovery API, "Continue where you left off" |
| **restoration** | The act of opening a recovery candidate's targets | launcher restore handler, `RestorationPlan` |
| **continuity** | The user-facing umbrella for the whole stack | positioning (README, landing) |
| **digest** | The empty-input launcher state | launcher.py |
| **resume** / **continue** | User action returning to past work | UI strings |

Avoid: *AI memory*, *smart memory*, *intelligent recall*, *AI-powered*,
*neural search*. None of those describe what's happening.

---

## Architecture pointers

- [docs/architecture/events.mdx](apps/docs/architecture/events.mdx)
- [docs/architecture/sessions.mdx](apps/docs/architecture/sessions.mdx)
- [docs/architecture/micro-contexts.mdx](apps/docs/architecture/micro-contexts.mdx)
- [docs/architecture/retrieval-pipeline.mdx](apps/docs/architecture/retrieval-pipeline.mdx)
- [docs/architecture/threading.mdx](apps/docs/architecture/threading.mdx)
- [docs/architecture/evolution.mdx](apps/docs/architecture/evolution.mdx)
- [docs/architecture/recovery.mdx](apps/docs/architecture/recovery.mdx)
- [docs/architecture/visual-system.mdx](apps/docs/architecture/visual-system.mdx)
- [docs/troubleshooting.mdx](apps/docs/troubleshooting.mdx)
- [docs/faq.mdx](apps/docs/faq.mdx)
- [docs/install-validation.mdx](apps/docs/install-validation.mdx)
- [RELEASE.md](docs/release/RELEASE.md), [VERSIONING.md](docs/release/VERSIONING.md), [CHANGELOG.md](docs/release/CHANGELOG.md)
- [STABILITY.md](docs/engineering/STABILITY.md) — guarantees + failure philosophy
- [PERF.md](docs/engineering/PERF.md) — benchmark methodology, hot paths, cache model
- [TRUST_FIXTURES.md](docs/trust/TRUST_FIXTURES.md) — continuity-trust calibration fixtures
- [TRUST_FIXTURES_CONTINUITY.md](docs/trust/TRUST_FIXTURES_CONTINUITY.md) — investigation-grouping fixtures
- [CONTINUITY_LANGUAGE.md](docs/product/CONTINUITY_LANGUAGE.md) — canonical user-facing vocabulary
- [SURFACE_MAP.md](docs/product/SURFACE_MAP.md) — one job per surface
- [MOTION.md](docs/product/MOTION.md) — the cross-surface motion contract
- [PUBLIC_ALPHA.md](docs/founder/PUBLIC_ALPHA.md) — public-alpha readiness path
- [TRUST_LEDGER.md](docs/engineering/TRUST_LEDGER.md) — what Recall sees / never sees / can export
- [PHASE_TRACKER.md](docs/founder/PHASE_TRACKER.md), [ROADMAP_LIVE.md](docs/founder/ROADMAP_LIVE.md) — build state + roadmap
- [ROOT_ARCHITECTURE.md](docs/engineering/ROOT_ARCHITECTURE.md), [REPO_STRUCTURE.md](docs/engineering/REPO_STRUCTURE.md)

Each page documents its layer's lifecycle, signal table, decay
model (where applicable), API, and performance budget. Read the page
before changing the layer.

---

## How to approach a new task

1. Decide whether the task is a *new layer*, a *retrieval
   consumer*, or *maintenance*. Most tasks are the third.
2. Find the smallest layer that already answers the question. The
   answer is usually one heuristic deeper than you initially think.
3. Sketch the perf budget before you write the code. If you can't
   fit, the design is wrong, not the implementation.
4. Write the engine first, then the service, then the API, then the
   UI, then the smoke test, then the docs. In that order — the
   docs catch the design gaps the code didn't.
5. Run the smoke test. Run it five times. If perf is on the edge,
   profile and fix; don't lower the budget.
6. Open the PR. List the audit-report items it closes.

When in doubt: the layer below is probably the right home for the
change. Recall accumulates downward, not outward.

---

*This file is the working contract. Update it when reality drifts.*
