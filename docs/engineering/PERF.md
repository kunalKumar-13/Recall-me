# PERF.md — performance discipline

Recall is meant to be left running permanently. That only works if
it stays fast under *sustained* use, not just on a cold benchmark.
This file is the contract for that: how performance is measured,
what the budgets are, where the hot paths sit, and how regressions
are caught.

It was written in Phase 4F (Trust + Responsiveness) after a real
profiling pass; the numbers below are measured, not estimated.

---

## Benchmark methodology

**Rules.**

1. **Measure the warm path and the cold path separately.** They are
   different products. A cold path runs once per launcher session;
   a warm path runs on every keystroke-debounced query. Reporting a
   single blended number hides which one regressed.
2. **Report a distribution, never one sample.** Minimum five runs;
   quote p50 and p90. A single timing sample on a loaded developer
   machine has ±2× variance — enough to flip any pass/fail gate.
3. **Profile before optimizing.** `cProfile` sorted by `tottime`
   finds the hot function; `tottime` excludes called-function cost
   so it points at the real work. Never optimize from intuition.
4. **cProfile distorts wall time.** Millions of instrumented calls
   add 8–12× overhead and, worse, can push a single call past a
   cache TTL that it would have hit unprofiled. Use cProfile to
   find *where* time goes; use `time.perf_counter()` loops to
   measure *how much*.
5. **Determinism is a perf property.** Same events in must give the
   same surface out *and* the same cache-hit pattern. A
   non-deterministic cache key is a latent perf regression.

**Standard fixture.** 10,000 `browser_visit` events across 10
topics / 10 domains, one per-day JSONL file — the same fixture
`_smoke_api.py` section 11 seeds. It is the reference load for
every budget in the table below.

---

## Performance budgets

These are part of the API contract. `_smoke_api.py` enforces every
one; a regression past a budget is a bug, not a slowdown.

| Endpoint | Budget (10K events) | Measured (warm, p50) |
|---|---|---|
| `GET /v1/search` | <100 ms wall | ~67 ms |
| `GET /v1/resurface/idle` | <25 ms server | within |
| `GET /v1/threads/recent` | <75 ms server | within |
| `GET /v1/threads/{id}/evolution` | <70 ms server (median) | within |
| `GET /v1/recovery/recent` | <80 ms wall (median) | within |
| `POST /v1/recovery/{id}/restore` | <10 ms | within |
| `POST /v1/events/{kind}` | <2 ms | within |
| `GET /v1/health` | <1 ms | within |

The budgets assume a **warm parse cache** for everything except the
first query of a session — see the next section for why that
distinction is the whole game.

---

## Hot paths

Profiled in Phase 4F on the standard 10K-event fixture.

### 1. Event-log parse — the dominant cost

Parsing one 10K-event JSONL day file into `Event` objects costs
**~78 ms**: `read_text().splitlines()`, then 10K × `orjson.loads`,
then 10K × `Event` construction. This is the single largest cost
in the entire retrieval pipeline.

It is paid **once per cold cache**, never per query — *if* the
parse cache is working. See cache behavior below.

### 2. Retrieval scoring — the warm path

With the parse cache warm, `EpisodicRetriever.search()` over 10K
events is **~11–20 ms** (p50 ~13 ms). The work is a keyword /
recency / kind-hint scan; `_quick_token_overlap` is the inner
loop. Per-`Event` searchable-text views are themselves cached on
the instance (`_build_search_cache`), so a warm scoring pass does
no string rebuilding.

### 3. `/v1/search` end to end

Episodic + session reconstruction + context reconstruction,
warm: **~67 ms wall, ~50 ms server**. Reconstruction shares the
single episodic scan via `episodic_search_with_pool` rather than
scoring the log twice.

---

## Cache behavior

`EventStore` keeps a per-day-file parse cache: a parsed
`list[Event]` reused across reads of the same file.

**Freshness key (Phase 4F): `(mtime, size)`.** Every write the
system makes is an *append* through `EventLogger`, and an append
always grows the file — so the size check alone detects every
real write immediately. A 60-second TTL is a paranoia backstop for
the one pathological case `(mtime, size)` cannot see: an in-place,
same-length overwrite that also preserves mtime. The logger never
does this, and hand-edits change mtime, so the backstop effectively
never fires.

**Why this matters — the Phase 4F finding.** The TTL was
originally **0.5 s**, tuned to "cover one launcher request". That
made the TTL load-bearing for correctness *and* far too short for
reuse: two launcher searches more than half a second apart each
re-parsed the entire log (~80 ms). Profiling confirmed it — a
search 0.45 s after a warm-up measured 224 ms; 1.0 s after,
171 ms. This was the cause of the `_smoke_api.py` section-11
budget failure, and a real responsiveness bug under daily use.
Moving correctness onto `(mtime, size)` freed the TTL to be a 60 s
backstop, and sustained interactive use now stays on the warm
~13 ms path.

**Per-`Event` caches.** `ts_epoch()` and the three
`searchable_*()` views are memoized on each `Event` instance.
Because the parse cache returns the *same* `Event` objects across
reads, these instance caches survive between queries too — the
second query reuses both the parse and the derived views.

**Eviction.** The parse cache holds at most 32 files (FIFO). A
query touches at most ~14 day-files, so eviction is rare.

---

## Known scaling characteristics

- **Parse is linear in events**, and per-day. The cost is bounded
  by the largest single day-file, not the whole log — a year of
  history is still parsed one day at a time.
- **Scoring is linear in events within the retrieval window** (the
  default look-back). It does not grow with total history.
- **The parse cache is the scaling lever.** As long as it stays
  warm, query cost is flat in total history and linear only in the
  active window. A cold cache pays the parse once.
- **Memory** is one `list[Event]` per cached day-file. At 10K
  events/day and 32 cached files that is a few tens of MB — bounded
  and reclaimed by FIFO eviction. Recall does not accumulate
  unbounded state across a long-running session.

---

## Regression detection philosophy

- **The smoke test is the gate.** `_smoke_api.py` has a perf
  assertion per budgeted endpoint. A failing perf section is a
  real regression — fix the code, never the budget.
- **A single failing sample warrants investigation, not a verdict.**
  Re-run; if it fails on a distribution, it is real. The Phase 4F
  section-11 failure was confirmed by reproducing it on clean
  `HEAD` and then root-causing it — not by adjusting the threshold.
- **Isolate regression from environment.** `git stash` the change
  and re-run; if clean `HEAD` fails identically, the regression
  predates the change (or the machine is loaded). Phase 4F used
  exactly this to prove the section-11 failure was a pre-existing
  cache-TTL issue, not new work.
- **Watch the warm/cold split.** Most perf regressions are not
  "scoring got slower" — they are "something started missing the
  cache". Check cache-hit behavior before profiling arithmetic.

---

*Update this file whenever a budget moves, a hot path shifts, or a
new caching layer is added.*
