# Stability

This document records what Recall *guarantees*, what it *does
not* guarantee, and how it behaves when things go wrong. It is
the contract the engine signs with the user — the thing they
should be able to trust when they leave the launcher running
all day for years.

For *why* the system is shaped the way it is, see
[`CLAUDE.md`](../../CLAUDE.md). For the architecture map, see
[`ROOT_ARCHITECTURE.md`](ROOT_ARCHITECTURE.md). This file is
narrowly about reliability and trust.

---

## What Recall guarantees

### 1. Determinism

Same events in → same outputs out, always.

Every engine layer (`events / sessions / contexts / resurfacing
/ threads / evolution / recovery`) is a pure function of the
event log plus the small identity caches at `~/.recall/`.
There is no:

- learned weighting
- probabilistic ranking
- LLM in the production path
- randomization
- non-determinism dependent on wall-clock time *except* the
  recency decays, which are pure functions of `now` and the
  event timestamps

You can reproduce any output by running the smoke test against
the same seed. The smoke test in
[`_smoke_api.py`](../../_smoke_api.py) is the executable form of
this contract.

### 2. Local-first

No outbound network call beyond:

- a single embedding-model download (`all-MiniLM-L6-v2`,
  ~80 MB) on first run, after which `local_files_only=True` is
  set on the loader for the lifetime of the install

No telemetry, no analytics, no error reporting, no model-update
pings. ChromaDB's anonymous telemetry is explicitly disabled at
boot. Hugging Face's update-check telemetry is explicitly
disabled at boot.

The HTTP API binds to `127.0.0.1:4545` exclusively. The Chrome
extension's `host_permissions` is locked to that single URL.
Pulling the network cable after first run leaves the product
fully functional.

### 3. Inspectability

Every artefact Recall produces is plain text:

- `~/.recall/events/YYYY-MM-DD.jsonl` — append-only JSONL, one
  event per line, no binary framing
- `~/.recall/threads.json` — pretty-printed JSON
- `~/.recall/evolution.json` — pretty-printed JSON
- `~/.recall/resurfacing.json` — pretty-printed JSON
- `~/.recall/config.json` — pretty-printed JSON
- `~/.recall/version.json` — pretty-printed JSON

You can `cat` any of them, edit any of them, and delete any of
them. The engine re-derives caches from events; deleting events
loses history but the rest keeps working.

The ChromaDB index is the only non-text artefact, and it's
re-creatable from your indexed folders.

### 4. Performance budgets

Each public endpoint declares its budget. A regression past
the budget is a bug, not a slowdown:

| Endpoint | Budget (10K events, p50) |
|---|---|
| `GET /v1/search` | <100 ms wall, <60 ms server |
| `GET /v1/resurface/idle` | <25 ms server (warm) |
| `GET /v1/threads/recent` | <75 ms server-side (warm) |
| `GET /v1/threads/{id}/evolution` | <70 ms server (median) |
| `GET /v1/recovery/recent` | <80 ms wall (best-of-3) |
| `POST /v1/recovery/{id}/restore` | <10 ms |
| `POST /v1/events/{kind}` | <2 ms |
| `GET /v1/health` | <1 ms |

The smoke test asserts every one of these. A pull request that
moves a budget number requires the same scrutiny as one that
changes an HTTP route.

These budgets assume a **warm parse cache** for every query after
the first of a session. [`PERF.md`](PERF.md) documents the
benchmark methodology, the profiled hot paths, the parse-cache
freshness model, and how performance regressions are isolated
from environment variance.

### 5. Backward compatibility

- `/v1/*` HTTP routes keep their request + response shapes
  across a major version. Additive fields are allowed; removing
  or repurposing a field requires `/v2/`.
- The five canonical event `kind` values (`browser_visit`,
  `browser_search`, `chat_session`, `open`, `query`) and their
  payload shapes are stable across a major. Optional fields can
  be added; existing fields keep their names and types.
- Launcher keybindings (`Ctrl+Space`, `Ctrl+Enter`, `Ctrl+C`,
  `Ctrl+M`, `Esc`, `Ctrl+,`) keep their meaning across a major.

Everything else — internal class names, cache file formats
other than `events/`, Settings copy, motion timings — is
below the stability line. Caches can change shape between
minors; users keep working because the engine always
re-derives.

See [`VERSIONING.md`](../release/VERSIONING.md) for the full policy.

---

## Failure philosophy

Recall's failure model is **quiet graceful degradation**. A
user who left the launcher running for six months and then
finds their laptop's disk full should still be able to open
Ctrl+Space; the launcher should still appear; the recovery
section should be empty; nothing should crash.

The rules:

### The logger must never raise

`EventLogger.log()` swallows every `OSError` it touches. A
write to a full disk silently drops the event. A write to a
read-only filesystem silently drops the event. The launcher
keeps running.

This is the strongest guarantee in the codebase. It is
enforced by:

- A blanket `except OSError` in `EventLogger.log()`'s file-
  append path
- A blanket `except OSError` in `EventLogger._save()` for the
  persistence helpers in `ResurfacingHistory`,
  `ThreadStore`, and `ThreadEvolutionStore`
- A test in `_smoke_api.py` § *Section 7* that verifies a
  malformed payload returns `{"ingested": 0, "reason": …}`
  rather than raising

### The reader must never raise on malformed input

`EventStore._cached_or_parse()` skips lines that fail to
parse, rather than aborting the file. A hand-edit that leaves
a truncated JSON line at the end of a per-day file produces
one fewer event in the read; the rest of the file still
parses.

Similarly:

- `ResurfacingHistory._load()`, `ThreadStore._load()`,
  `ThreadEvolutionStore._load()` all fall back to an empty
  in-memory state on parse failure rather than crashing
- The episodic retriever skips events with missing `ts` or
  malformed timestamps (they get `ts_epoch == 0.0` and fall
  into "ancient")
- The threads engine skips identity rows that fail to decode

### The API must never 500 silently

Every `/v1/*` route either:
- returns its declared response shape, or
- returns `4xx` with a typed `reason` body

A 5xx never leaves the FastAPI handler. The single exception
is `/v1/recovery/{id}/restore` returning 404 when the
candidate id is unknown — that is the *correct* response, not
a failure.

The Pydantic `extra="ignore"` policy on all `_StrictModel`
inputs means a client sending an unknown field gets a
successful response with the unknown field silently dropped,
not a 422. This is intentional: the contract is "we'll write
the fields we know about and ignore the rest", which gives
clients room to grow.

### The launcher must never crash on user-visible actions

The brief from Phase 4A § rule 15: *"errors are quiet
recoverable states, never raw tracebacks."*

Specific commitments:

- A missing file passed to `_open_path_and_hide()` produces a
  footer flash (`Couldn't open · …`) rather than a Qt
  exception dialog
- A failed restoration step is recorded in the
  `RestorationResult.skipped` list and surfaced in the
  completion flash (`Restored N of M · K skipped`); the other
  steps continue
- A transient HTTP failure on `APIClient.search()` returns
  `None`, which the launcher interprets as "show empty
  results"; the launcher does not crash
- A failed Settings save logs to stderr and surfaces a status
  line in the dialog rather than dismissing it

### The single audible failure mode

The one thing the launcher *does* loudly is import failure at
boot. `recall.py`'s `try / except BaseException` around the
top-level `from app.main import main` prints a traceback and
exits with code 1. Rationale: if the launcher can't import
its own engine, there is no quiet state to degrade to — the
process can't run at all, and the user needs to see why.

---

## Degradation philosophy

Recall is built to degrade in layers. Each layer's failure
disables only that layer's surface; everything else keeps
working.

### If the event log is empty or unreadable

- `iter_events()` returns an empty iterator
- Resurfacing, threads, evolution, recovery all surface empty
- File search keeps working (it reads its own ChromaDB index,
  not the event log)
- The launcher's idle digest renders the *first-week hint*
  ("Capture builds quietly…")

### If `~/.recall/threads.json` is corrupt or missing

- `ThreadStore._load()` falls back to empty state
- The next `ThreadBuilder.rebuild()` re-derives thread ids
  from the event log
- Identity stability is lost for one cycle (existing thread
  ids may change), but the user-facing surface keeps working

### If `~/.recall/evolution.json` is corrupt or missing

- `ThreadEvolutionStore._load()` falls back to empty state
- Evolution is re-derived from events on demand
- The launcher pays one cold-cache call per thread; warm path
  recovers immediately

### If `~/.recall/resurfacing.json` is corrupt or missing

- `ResurfacingHistory._load()` falls back to empty state
- The resurfacing engine treats every topic as fresh (no
  fatigue downweight)
- The first idle render may surface more cards than usual;
  the surfacing-counter rebuilds across subsequent renders

### If the FastAPI service fails to start

- `app/main.py`'s `_step("start local memory API…")` logs the
  failure but the launcher boot continues
- The launcher falls back to its in-process retrievers
  (`EventStore`, `EpisodicRetriever`, …) for digest reads
- The extension's popup reads as *"Recall daemon not
  responding"*; the user can still launch from Ctrl+Space
- Restoration via `/v1/recovery/{id}/restore` fails (returns
  `None` from `APIClient.recovery_restore`); the launcher
  surfaces *"Nothing to restore · …"*

### If the browser extension is uninstalled, paused, or
disconnected

- The desktop API keeps running
- `ingested_total` stays flat
- The launcher's digest gradually narrows as browser events
  age out
- The user sees no error; the absence is the signal

### If a file referenced by a recovery target no longer exists

- `_on_recovery_restore()` pre-checks `Path(target).exists()`
  before logging an open event
- Missing files are recorded in `RestorationResult.skipped`
  with reason `"file no longer exists"`
- The completion flash reports the skip count: *"Restored 4
  of 5 · 1 skipped"*
- The other targets restore normally

---

## Deterministic principles

These are *invariants* the codebase enforces. Each one is
something that must be true of every PR that touches the
engine.

1. **No randomness in production paths.** A grep for
   `random.` in `app/core/` should return zero hits inside
   functions that contribute to a `/v1/*` response. The one
   permitted exception is `app/core/microcontexts.py`'s
   tie-breaking, which is seeded from event timestamps (still
   deterministic w.r.t. inputs).

2. **No reliance on `time.time()` inside scoring loops.** All
   recency math takes `now` as a parameter so tests can
   reproduce. The wall clock is consulted exactly once per
   request, at the top of the handler.

3. **No mutable module-level state across requests.** Caches
   live on `EventStore` instances and are scoped to a single
   `APIService`. Two `APIService` instances in the same
   process see independent caches.

4. **No hidden import-time work.** Module imports do not
   touch the network, the disk, or the system clock. The
   single exception is `app/core/events.py`'s `_loads` /
   `_JSON_DECODE_ERRORS` resolution, which dispatches on
   whether `orjson` is importable.

5. **Stable ids derive from stable inputs.** Thread ids are
   `sha1(topic_key)[:8]`. Evolution phase ids are
   `sha1(thread_id + slot + start_ts)[:8]`. Recovery
   candidate ids are `sha1(thread_id + last_active_day)[:10]`.
   None of these change unless the underlying input changes.

---

## Recovery guarantees

Recovery is the user-facing surface where trust matters most
— clicking a card opens five tabs and four files, and the
user needs to know it will produce the same result as the
preview promised.

The guarantees:

- A recovery candidate's `suggested_targets` list is **fully
  deterministic** w.r.t. the events at the time the candidate
  was scored. Two `recover_recent()` calls within the same
  cache window return identical target lists.
- `RestorationPlan` ordering is also fully deterministic. The
  same plan replayed produces the same step sequence.
- A target that's been missing since capture is **never**
  silently dropped from the plan; it's surfaced as a `skipped`
  entry in the `RestorationResult` with reason `"file no
  longer exists"`.
- A target that opens successfully is logged as an `open`
  event in the user's real event store. The next recovery
  rebuild sees the restoration as activity. This is the only
  side-effect the restore path has on the event log; it is
  intentional and documented in [`docs/architecture/
  recovery.mdx`](../../apps/docs/architecture/recovery.mdx) §
  *One-click restoration*.
- The launcher hides itself **after** the first successful
  target opens, not before. A user who watches the launcher
  for the acknowledgement gets a footer flash; a user who
  Alt-Tabs away gets the same restoration behaviour.

What recovery does *not* guarantee:

- That the targets will *still open the way they did when
  captured*. URLs can 404; files can move; chats can be
  deleted. Recovery surfaces what the user touched; it does
  not promise that touching it again produces the same
  experience.
- That the same candidate will appear tomorrow. The
  `RecoveryCandidate.id` is derived from
  `(thread_id, last_active_day)`. A new event in the thread
  the next day produces a new id, by design. Recovery is
  *current state*, not history.
- That restored items appear in the order the user originally
  visited them. The plan order is `files → chats → tabs →
  searches`, regardless of capture order, because that's the
  order that produces the cleanest re-entry into the mental
  room. See [`docs/architecture/recovery.mdx`](../../apps/docs/architecture/recovery.mdx)
  § *Restoration choreography*.

---

## How to verify a Recall install is stable

Run the verification checklist in
[`apps/docs/install-validation.mdx`](../../apps/docs/install-validation.mdx).
Each step exercises one of the guarantees above. If all six
steps pass, the install is honoring this document.

For ongoing health, the launcher's `--debug` boot diagnostics
print per-stage timing; values inside the budgets in
[`CLAUDE.md`](../../CLAUDE.md) § *Performance budgets* indicate the
engine is running as designed.

---

## The thing this document is the contract for

> *"I trust this enough to leave running for years."*

Every guarantee in this file is a promise we keep that makes
that sentence true. If you find a place in the codebase where
one of these promises is broken in practice, that is a
**stability bug**, not a feature request — and it goes to the
top of [`AUDIT_REPORT.md`](AUDIT_REPORT.md).

---

## Per-surface stability reports

This document is the contract; the detailed per-surface
measurement reports (formerly the top-level `STABILITY/` folder,
consolidated here) live alongside it under
[`stability/`](stability/):

- [`stability/CAPTURE.md`](stability/CAPTURE.md) — event-store coverage by site
- [`stability/CONTROL.md`](stability/CONTROL.md) — admin routes + loaders
- [`stability/EXTENSION.md`](stability/EXTENSION.md) — popup state machine + bundle health
- [`stability/LAUNCHER.md`](stability/LAUNCHER.md) — frozen widget tree + cold-construct timing
- [`stability/PERF.md`](stability/PERF.md) — wall-clock timings for launcher + CLI + daemon
- [`stability/RESUME.md`](stability/RESUME.md) — recovery pipeline + restore-plan invariants
- [`stability/TRACK_A_REPORT.md`](stability/TRACK_A_REPORT.md) — Track A consolidation report
