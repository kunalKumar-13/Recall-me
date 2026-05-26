# Capture Flow — Phase 7D

How a single browser action becomes a launcher card. This is
the document the next engineer reads when *Recall didn't
remember* — every arrow below is a real call site you can
breakpoint or `print`.

> **Success criterion:** open ChatGPT / GitHub / StackOverflow
> / Google → leave → return → confirm the work appears in the
> launcher. Anywhere the chain breaks, fix the pipeline.

---

## The seven hops

```
┌─────────────────────────────────────────────────────────────────┐
│ 1. BROWSER          tab open · navigation · title change ·     │
│                     search · return after gap                  │
└─────────────────────────────────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────┐
│ 2. EXTENSION        background.js / content scripts emit       │
│                     POST http://127.0.0.1:4545/v1/events/*     │
└─────────────────────────────────────────────────────────────────┘
                                 │ HTTP loopback
                                 ▼
┌─────────────────────────────────────────────────────────────────┐
│ 3. DAEMON           api/main.py:ingest_{browser,search,chat,…} │
│                     → IngestionService.ingest_typed            │
└─────────────────────────────────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────┐
│ 4. EVENT STORE      EventLogger.log appends one JSONL line to  │
│                     ~/.recall/events/YYYY-MM-DD.jsonl          │
└─────────────────────────────────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────┐
│ 5. INVESTIGATION    ThreadBuilder.rebuild groups events by     │
│                     topic_key → ~/.recall/threads.json         │
└─────────────────────────────────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────┐
│ 6. RECOVERY         RecoveryEngine.recover_recent scores       │
│                     threads → returns top candidates           │
└─────────────────────────────────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────┐
│ 7. LAUNCHER         LiveLauncher._populate_digest → renders    │
│                     the Continue document                      │
└─────────────────────────────────────────────────────────────────┘
```

Each hop has a file path, a function name, and a CLI you can
run to confirm the data made it.

---

## Hop-by-hop

### 1. Browser

The extension runs three observers:

| Observer                | Fires                              | Source                          |
|-------------------------|-------------------------------------|---------------------------------|
| `chrome.tabs.onUpdated` | navigation + title-change events    | `apps/extension/background.js`  |
| `chrome.tabs.onCreated` | tab-open                            | same                            |
| URL pattern matcher     | search-engine queries (Google, DDG) | content script                  |
| Chat-host pattern       | ChatGPT / Claude / Gemini sessions  | content script                  |

A 30-minute idle on a tab + a re-visit = a *return after gap*.
The daemon detects this on ingest via
[`app.core.daily_loop.mark_event`](../../app/core/daily_loop.py).

### 2. Extension → daemon

The extension speaks loopback only:

```
POST http://127.0.0.1:4545/v1/events/browser
POST http://127.0.0.1:4545/v1/events/search
POST http://127.0.0.1:4545/v1/events/chat
POST http://127.0.0.1:4545/v1/events/open
POST http://127.0.0.1:4545/v1/events/desktop
```

The bind to `127.0.0.1` IS the security boundary — no external
origin can reach the daemon. Pydantic models in
[`api/schemas.py`](../../api/schemas.py) reject any field
outside the closed whitelist.

### 3. Daemon receive

Routes in [`api/main.py`](../../api/main.py):

```python
@app.post("/v1/events/browser", response_model=IngestResponse)
async def ingest_browser(ev: BrowserVisitIn, deps: AppDeps = Depends(get_deps)):
    ok, reason = await run_in_threadpool(
        deps.ingestion.ingest_typed, "browser_visit", ev.model_dump()
    )
    _post_ingest_hook(ok)
    return IngestResponse(received=1, ingested=1 if ok else 0, reason=reason)
```

`_post_ingest_hook` runs two side-effects on a successful
ingest:

- `daily_loop.mark_event(ts)` — increments the daily counter
  and detects the return-after-gap signal.
- `demo_mode.mark_real_activity()` — flips the demo overlay
  to `dismissed` so the launcher stops showing the demo
  payload the moment real events start arriving.

### 4. Event store

[`app.core.events.EventLogger.log`](../../app/core/events.py)
appends one JSONL line to today's file:

```
~/.recall/events/2026-05-24.jsonl
```

Format:

```json
{
  "ts": "2026-05-24T21:40:59Z",
  "session_id": "s_20260524_211231_482103",
  "kind": "browser_visit",
  "payload": {
    "url": "https://stitch.withgoogle.com/projects/...",
    "domain": "stitch.withgoogle.com",
    "title": "Stitch - Projects"
  }
}
```

The line is the contract. Anyone with `cat` can audit
exactly what was captured.

### 5. Investigation build

[`app.core.threads.ThreadBuilder.rebuild`](../../app/core/threads.py)
groups events by `topic_key` (a deterministic stem from the
URL/title/path) and writes
[`~/.recall/threads.json`](../../app/core/threads.py). A
thread with ≥ 4 events and ≥ 2 distinct surfaces becomes an
**investigation**.

The 7-rule contract for what becomes an investigation lives
in [`INVESTIGATION_PRINCIPLES.md`](INVESTIGATION_PRINCIPLES.md).

### 6. Recovery scoring

[`app.core.recovery.RecoveryEngine.recover_recent`](../../app/core/recovery.py)
scores the top-N threads against the 9 trust-floor gates +
the `_MIN_RESUME_INTENT` threshold + the `bad_recoveries`
ledger. The top candidate is what the launcher shows.

The promotion bands (LOW / MED / HIGH) + the 5 overrides are
documented in
[`PROMOTION_THRESHOLDS.md`](PROMOTION_THRESHOLDS.md).

### 7. Launcher display

[`LiveLauncher._populate_digest`](../../app/ui/launcher_v3/live.py)
calls `api_client.recovery_recent(n=1)`. The HIGH-only gate
(targets ≥ 4) decides whether the Continue document renders
or the empty workspace shows.

---

## Verification commands

The two new Phase 7D CLIs are the spine of the audit.

### `recall capture status`

Read-only ASCII summary of today's pipeline state:

```
  ------------------------------------------------------------
    Capture status - today
  ------------------------------------------------------------

    events today        71
      tabs                 64  (browser_visit)
      chats                 7  (chat_session)

    returns (>= 30 min gap)   3
    investigations            11
    last event                21:40:59 UTC  (1h ago)
                              kind = browser_visit

  ------------------------------------------------------------
```

What each number proves:

| Field                  | What it confirms                                 |
|------------------------|--------------------------------------------------|
| `events today`         | Hops 1-4 are working (extension → store)         |
| Per-kind breakdown     | Each event kind has reached the store today      |
| `returns (>= 30 min)`  | Session-gap detection (`daily_loop.mark_event`)  |
| `investigations`       | Hop 5 (`threads.json` is being written)          |
| `last event`           | The pipeline is currently warm                   |

If `events today == 0` the CLI prints three remediation
hints (run the daemon, check the extension is paired, or run
the demo).

### `recall capture tail`

Live `tail -f` of today's event log:

```
  ------------------------------------------------------------
    Capture tail
  ------------------------------------------------------------
    watching ~/.recall/events/2026-05-24.jsonl

  21:36:59  browser_visit   stitch.withgoogle.com   Stitch - Design with AI
  21:37:39  browser_visit   stitch.withgoogle.com   Stitch - Design with AI
  21:38:33  browser_visit   stitch.withgoogle.com   Stitch - Projects
  21:40:59  browser_visit   stitch.withgoogle.com   Stitch - Docs

  (waiting for new events - Ctrl+C to exit)
```

Run this in a terminal, then drive the browser. Each new
event lands inside ~500 ms. Watching the line print is the
most direct possible proof that hops 1-4 are warm.

`recall capture tail --once` prints the existing day's events
then exits (useful for scripting / piping).

---

## The scripted walk (Phase 7D verification)

1. **Start the daemon.**
   ```powershell
   python recall.py
   ```

2. **Open `recall capture tail` in another terminal.**
   ```powershell
   python recall.py capture tail
   ```

3. **Open four sites in your browser** (one tab each):
   - `https://chat.openai.com`
   - `https://github.com`
   - `https://stackoverflow.com`
   - `https://google.com/search?q=websocket+backoff`

   Watch `capture tail` print four `browser_visit` rows (the
   ChatGPT row arrives as `chat_session` after the content
   script flips its kind).

4. **Leave** for ≥ 30 minutes. Do something else.

5. **Return.** Reopen `chat.openai.com`. The tail should print
   one more `browser_visit` row; `capture status` should now
   show `returns >= 1`.

6. **Open the launcher.** The Continue document should
   surface naming the strongest of the four investigations
   (typically the one with the most depth events + multiple
   surfaces). If `n_targets < 4` the launcher will sit on
   the empty workspace — that's expected; only HIGH
   recoveries earn the hero (Phase 6O HIGH-only gate).

7. **Confirm via the inspector.**
   ```
   recall inspect <topic-substring>
   ```
   Should print `Strength: HIGH` and `Decision: SHOW HERO`.

If any of those six steps fails, the audit's
*Hop-by-hop* section names the exact file + function to fix
next.

---

## What the audit does NOT do

- **No UI work** — this is engine + CLI + docs only.
- **No new event kinds** — the 7-kind whitelist
  (`browser_visit`, `browser_search`, `chat_session`,
  `open`, `reveal`, `desktop_window`, `query`) is the
  contract; the audit verifies what already ships.
- **No telemetry.** Both CLIs read local-only state. The
  audit's output never leaves the machine.

---

## See also

- [`app/core/capture_cli.py`](../../app/core/capture_cli.py)
  — both CLIs.
- [`app/core/events.py`](../../app/core/events.py) — the
  store + the logger.
- [`api/main.py`](../../api/main.py) — the ingest endpoints.
- [`INVESTIGATION_PRINCIPLES.md`](INVESTIGATION_PRINCIPLES.md)
  — the 7 rules that decide what becomes an investigation.
- [`PROMOTION_THRESHOLDS.md`](PROMOTION_THRESHOLDS.md) — the
  LOW / MED / HIGH bands + the 5 overrides.

> Recall truly remembers — and now you can prove it.
