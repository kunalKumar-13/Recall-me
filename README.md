<div align="center">

# Recall

**A local-first continuity operating system.**

Get interrupted, and the climb back costs more than the interruption
did — scattered tabs, the wrong files, a lost train of thought. Recall
restores the whole working state in one keystroke: Ctrl + Space, a
half-thought, and the tabs, files, and chats come back in a coherent
sequence. Everything stays on disk. No accounts, no cloud, no
telemetry.

[Install](#installation) · [Architecture](#architecture) · [API](#http-api) ·
[Docs](https://docs.recall.computer) ·
[Stability](docs/engineering/STABILITY.md) ·
[Troubleshooting](apps/docs/troubleshooting.mdx) · [Roadmap](#roadmap)

</div>

---

```text
┌─ Ctrl+Space ─────────────────────────────────────────────────────┐
│  rlhf paper i was reading yesterday                              │
├──────────────────────────────────────────────────────────────────┤
│  ●  Training language models with RLHF — arxiv.org · 14h ago     │
│  ◇  Researching reward shaping · 5 events · yesterday evening    │
│  ✦  Reading about RLHF — 4 visits in one block                   │
│     ~/notes/rlhf-notes.md · 2 days ago                           │
│     ~/papers/rlhf-survey.pdf · 4 days ago                        │
└──────────────────────────────────────────────────────────────────┘
```

The episodic moment, the session, and the micro-context all surface in
one keystroke. The bottom rows are full-text-and-semantic file hits.
That's Recall in twenty seconds — the rest of this page explains *how*
it does that without an LLM, a cloud account, or a single byte of
telemetry.

---

## Why this matters

You don't lose files. You lose **continuity** — the state of mind that
held everything together. Spotlight, Windows Search, and `grep` all
assume you remember a string. Real cognitive restart asks "*what was I
doing*?", "*which conversation was that in*?", "*where did I leave the
implementation*?" Recall is built to answer those, not the keyword
ones.

Three honest claims:

- **You'll re-enter unfinished work in one keystroke.** Open the
  launcher with an empty query — a *Continue where you left off* card
  appears with three or fewer resumable investigations. Click one;
  the files, chats, and browser tabs you were using come back in the
  order that re-grounds the work.
- **The product runs entirely on your machine.** No cloud, no
  telemetry, no LLM in the production path. Everything Recall knows
  about you lives in `~/.recall/` as plain JSON and JSONL — readable
  with `cat`, deletable with `rm`.
- **Same events in → same outputs out.** Every layer of the engine
  is deterministic. No probabilistic ranking, no surprise. The
  35-section smoke test enforces the contract.

If that's interesting, the [three-minute install](apps/docs/install-3min.mdx)
gets you a working launcher in five commands.

### The flow it's built around

1. **Interrupt.** You're mid-task — a websocket bug, a research
   dive — and the day pulls you away.
2. **Leave.** Close the laptop. Recall raises no notification and
   keeps no nagging count.
3. **Return.** A day later, open the launcher on an empty query.
4. **Resume.** *Continue where you left off* offers the one
   investigation worth re-entering. One click reopens its files,
   tabs, and chats in order — you step back in, you don't rebuild.

**Why not an AI chatbot?** A chatbot answers *questions*; it does
not restore *state*. Recall never summarizes your work or talks to
you — it reopens the exact artifacts you had, deterministically,
with no model in the production path. You don't want a conversation
about your work. You want to be back inside it. That is also why
it's **local**: a continuity layer for your own thinking is only
worth trusting if it never leaves your machine.

---

## What it is

Seven layers in one process, each composing on the previous one:

| Layer | Surface | Question it answers |
|---|---|---|
| Events | per-day JSONL under `~/.recall/events/` | *"what did I touch?"* |
| Sessions | 30-min temporal groupings | *"what was I doing in that block of time?"* |
| Micro-contexts | topic-coherent splits of a session | *"what was I mentally working on?"* |
| Resurfacing | quiet idle-launcher digest | *"what should I notice now?"* |
| Threads | persistent topic identity | *"what's the shape of my work over time?"* |
| Evolution | chronological phases inside a thread | *"how did this thread change?"* |
| Recovery | resumable work + one-click restoration | *"what should I open right now to keep going?"* |

A keyboard launcher (`Ctrl + Space`) sits on top, plus an optional
Chrome extension for browser-side capture, and a local HTTP API at
`127.0.0.1:4545` that owns retrieval, reconstruction, replay,
resurfacing, and threads.

Everything is a single Python process. The retrieval engine is small
enough to read in an afternoon, and each layer is replaceable without
rewriting the others.

---

## Architecture

```
            ┌────────────────────────────────────────────────────┐
            │                  Recall (one process)              │
            │                                                    │
   Ctrl+Space│  ┌──────────┐                ┌──────────────────┐ │
  ──────────►│  │ Launcher │ ─── HTTP ────► │  Local API       │ │
            │  │  (PyQt6) │                │  /v1/...         │ │
            │  └────┬─────┘                │  127.0.0.1:4545  │ │
            │       │                      │  (FastAPI)       │ │
            │   writes events              └────────┬─────────┘ │
            │       ▼                               │           │
            │  ┌──────────┐                    reads + scores   │
            │  │ Event    │                         │           │
            │  │ Logger   │                         ▼           │
            │  │ (JSONL)  │                ┌─────────────────┐  │
            │  └────┬─────┘                │  Episodic +     │  │
            │       │                      │  Sessions +     │  │
            │       │                      │  Micro-contexts │  │
            │       │                      └────────┬────────┘  │
            │       ▼                               │           │
            │  ~/.recall/events/                    │           │
            │  YYYY-MM-DD.jsonl                     │           │
            │                                       │           │
            │                                       ▼           │
            │                              ┌─────────────────┐  │
            │                              │  File search    │  │
            │                              │  (ChromaDB +    │  │
            │                              │   MiniLM)       │  │
            │                              └─────────────────┘  │
            │                                                    │
            └────────────────────────────────────────────────────┘
                       ▲                          ▲
                       │ POST /v1/events/*        │ folders you choose
                       │                          │
                 ┌────────────┐
                 │  Chrome    │            ~/Documents, ~/Desktop, ~/code
                 │  extension │
                 └────────────┘
```

Three layers with hard boundaries:

| Layer | Code | Responsibility |
|---|---|---|
| Core | `app/core/` | Parsers, chunker, embeddings, vector store, event log, episodic retrieval, session + micro-context reconstruction. Pure Python; no Qt imports. |
| Service | `api/` | FastAPI + uvicorn. Owns ingest validation, retrieval, replay, and the `/v1/*` HTTP surface. Loopback bind, no auth. |
| UI | `app/ui/` | PyQt6 launcher, settings dialog, tray icon, hotkey. Talks to retrieval only through the HTTP client in `app/core/api_client.py`. |

State lives entirely in `~/.recall/` — config, vector index, instance
lock, event log. Removing that folder is a complete reset.

---

## Features

- **Episodic retrieval** — keyword + recency + kind-hint scoring over
  the local event log. Returns the moments that match a half-thought
  ("that GPT chat about websocket retries", "the Kanye interview I read
  yesterday").
- **Session reconstruction** — groups events by ~30-minute activity
  gaps; surfaces what you were *doing* around the moments that matched.
- **Micro-contexts** — splits long sessions into topic-coherent
  sub-blocks (domain affinity + token overlap). The unit a human
  actually remembers.
- **Passive resurfacing** — open the launcher with an empty query and
  a quiet *"Continue where you left off"* section surfaces unfinished
  threads from earlier this week. Max four items, no badges, no feed.
- **Memory threads** — long-lived topics the user keeps returning to
  across days, sessions, and surfaces, with stable identities and
  confidence that strengthens over time and decays when activity
  stops. *Healthcare startup*, *WebSocket retry logic*, *RLHF research*.
- **Semantic file search** — `all-MiniLM-L6-v2` over your chosen
  folders. Cosine ranking with a small, capped boost layer for
  filename hits and recency. ChromaDB persisted to
  `~/.recall/index/`.
- **Live indexing** — `watchdog` watches your folders. Save a file,
  it's reindexed within ten seconds.
- **Memory digest** — empty-query launcher state surfaces, in order:
  active memory threads, *continue where you left off*, recent
  queries, recent digital activity, recently-active files, and a
  deterministic "resurfaced this week" lane for older work.
- **Browser memory** — a 200-line Chrome extension posts page visits,
  searches, and chat-session entries to the local API. Domains in your
  blocklist are rejected client-side *and* server-side.

---

## Why Recall exists

You don't remember filenames. You remember what you were doing — what
the conversation was about, which paper you had open, what you were
trying to figure out. Spotlight, Windows Search, and `grep` all assume
you remember a string. Real memory doesn't work that way.

Recall is built for the way you actually think back: you remember a
*healthcare startup idea from last winter*, not
`pitch_deck_v3_final2.pdf`. You remember *a thread of research about
RLHF you've been picking at for two weeks*, not the URLs of the seven
arxiv papers that thread is made of.

The product makes one claim and stakes everything on it: a continuity
system for your own thinking is only useful if it stays on your
machine. Cloud sync, accounts, remote inference, and "AI summaries"
would each make the engineering easier and the trust impossible. We
picked the harder side. Recall is local, deterministic, and small
enough to read.

---

## Local-first guarantees

| What stays on your device | What doesn't |
|---|---|
| Your files (read, never copied) | — |
| Embeddings, computed on your CPU | — |
| The vector index (ChromaDB SQLite) | — |
| The event log (JSONL, plain text, auditable) | — |
| Search queries | — |
| Settings, folder list, autostart preference | — |
| Browser visits + searches + chat-session entries | — |
| Reconstructed sessions and micro-contexts | — |

The HTTP API binds to `127.0.0.1` and nothing else. Chrome will refuse
to fetch any other URL from the extension's worker because
`host_permissions` is locked to `http://127.0.0.1:4545/*`. There are
no analytics, no error reporting, no model-update pings. ChromaDB and
Hugging Face telemetry are both disabled at boot.

The **only** outbound network call Recall makes is the one-time download
of the embedding model (~80 MB) on first run. After that, the loader
uses `local_files_only=True`.

There are no accounts to create, no credentials to manage, no servers
to trust.

---

## Installation

### Prebuilt

Download the latest release for your platform and run it. The first
launch shows a one-page welcome that auto-suggests Documents and
Desktop. Pick folders, click **Start remembering**, and indexing runs
in the background.

### From source — single command

```bash
git clone https://github.com/kunalKumar-13/Recall-me.git recall
cd recall

# Windows (PowerShell):
./infra/scripts/dev.ps1

# macOS / Linux:
./infra/scripts/dev.sh
```

The script creates a venv, installs dependencies, runs the API smoke
test, and starts the launcher. Re-run it any time; it's idempotent.

### From source — manual

```bash
python -m venv .venv
source .venv/bin/activate         # macOS / Linux
# .venv\Scripts\activate          # Windows / PowerShell
pip install -r requirements.txt
python recall.py
```

Requires Python 3.10+. The first index pass downloads
`all-MiniLM-L6-v2` once into the Hugging Face cache. Subsequent runs
are fully offline.

### Demo mode (no indexing, no network)

```bash
python recall.py --demo
```

Loads ten in-memory sample memories (healthcare-startup notes, RL
research, websocket production work, …). Useful for screen recordings
and for evaluating the launcher before pointing it at real files.

### Diagnostics

```bash
python recall.py --debug
```

Emits per-stage `>> name` and `[OK]/[SLOW] name (Nms)` lines on boot so
a hang during startup points at the responsible stage.

### Standalone executable

```bash
pip install pyinstaller
python scripts/build_icon.py    # optional: writes app/assets/icon.ico
pyinstaller recall.spec
```

Output: `dist/Recall/Recall.exe` (Windows) or `dist/Recall/Recall`
(macOS / Linux). Ship the entire folder; it's self-contained.

---

## Browser extension

The extension at [`apps/extension/`](apps/extension) captures the title and URL
of completed page loads, the queries you type into search engines, and
the titles of ChatGPT / Claude conversations. It posts each event to
the local API.

Install:

1. Start Recall. The boot sequence prints
   `api.service.start port=4545 …` and the popup confirms
   `Connected · N captured`.
2. Open `chrome://extensions` (or `edge://extensions`).
3. Toggle **Developer mode** (top-right).
4. **Load unpacked** → select [`apps/extension/`](apps/extension).

Visits to `chrome://`, `file://`, incognito tabs, and any domain in
your **Settings → Browser Memory → Domains never captured** list are
dropped client-side *and* server-side (server-side is authoritative).

The manifest's only `host_permissions` entry is
`http://127.0.0.1:4545/*`. Chrome physically refuses to fetch any
other URL from the worker.

To pause without uninstalling: uncheck **Settings → Browser Memory**.
The popup also has a per-browser pause toggle.

---

## HTTP API

The API is hosted in-process at `http://127.0.0.1:4545`. Interactive
docs at `http://127.0.0.1:4545/docs-api`. OpenAPI JSON at
`http://127.0.0.1:4545/openapi.json`.

### Ingest

| Method | Path | Body | Purpose |
|---|---|---|---|
| `POST` | `/v1/events/browser` | `BrowserVisitIn` | Page visit |
| `POST` | `/v1/events/search` | `BrowserSearchIn` | Search-engine query |
| `POST` | `/v1/events/chat` | `ChatSessionIn` | ChatGPT / Claude / etc. session |
| `POST` | `/v1/events/open` | `FileOpenIn` | File open or reveal-in-Finder |
| `POST` | `/v1/events/batch` | `BatchEventsIn` (1–500) | Durable batched ingest — extension outbox, VS Code companion, integrations |
| `POST` | `/events` | `{kind, payload}` | Legacy generic ingest; backward compat |

### Retrieval

| Method | Path | Purpose |
|---|---|---|
| `GET` | `/v1/search?q=…` | Episodic + session + micro-context bundle for a query |
| `GET` | `/v1/search/files?q=…` | Semantic file search over indexed folders (honest `enabled:false` when no index) |
| `GET` | `/v1/events/recent` | Newest-first event stream, filterable by kind |
| `GET` | `/v1/events/today` | Events captured today (UTC), by kind — the capture self-check |
| `GET` | `/v1/queries/recent` | Distinct recent launcher queries |
| `GET` | `/v1/health` | Liveness + counters |

### Cognitive continuity

| Method | Path | Purpose |
|---|---|---|
| `GET` | `/v1/resurface/idle` | "Continue where you left off" cards for the idle digest |
| `POST` | `/v1/resurface/history/clear` | Wipe resurfacing surfacing-counters + muted topics |
| `GET` | `/v1/threads/recent` | Top-N active memory threads, ranked by confidence |
| `GET` | `/v1/threads/{id}` | One thread + reconstructed sessions + contexts + events |
| `GET` | `/v1/threads/{id}/evolution` | Chronological phases inside a thread (research → impl → revisit) |
| `POST` | `/v1/threads/cache/clear` | Wipe `~/.recall/threads.json` |
| `GET` | `/v1/recovery/recent` | Top-N (≤3) resumable work cards for the launcher digest |
| `POST` | `/v1/recovery/{id}/restore` | Return the full target list for one-click restoration |
| `GET` | `/v1/loop/summary` | Daily continuity-loop counters + green/yellow/red verdicts (counts only, never content) |
| `POST` | `/v1/loop/bump` | Launcher-side loop marks — summoned, shown, resumed, resume worked |

The retrieval bundle (`/v1/search`) returns three layers in one
response: episodic moments, the sessions those moments lived inside,
and the micro-contexts within those sessions. The launcher renders the
three with distinct row treatments.

---

## Event pipeline

Capture, write, retrieve. The contract is intentionally narrow.

1. **Capture.** An event is a typed payload posted to
   `/v1/events/{kind}` (extension) or written directly via
   `EventLogger.log_*` (launcher actions). Each event carries `kind`,
   `payload`, a `ts` in UTC ISO 8601, and a `session_id` allocated by
   30-minute gap detection.
2. **Validate.** The `IngestionService` runs URL/scheme blocklists,
   key allow-lists, and field-length caps before any write touches
   disk. Blocked events return a structured `reason` to the client.
3. **Persist.** One JSONL file per day at
   `~/.recall/events/YYYY-MM-DD.jsonl`. Plain text, one event per
   line, auditable with `cat`. "Forget yesterday" is one `rm`.
4. **Retrieve.** `EventStore` walks the per-day files with a short-TTL
   parse cache and mtime invalidation. The episodic retriever scores
   events; the session reconstructor groups by `session_id`; the
   micro-context reconstructor splits by domain + token affinity.

---

## Retrieval pipeline

The launcher hits `/v1/search` with the user's query. The server runs
three layered passes and returns the bundle:

```
query string
   │
   ▼
parse temporal phrases ("yesterday", "this morning", …)
   │
parse kind hint ("chat", "article", "search", "claude", …)
   │
expand content tokens through a small manual synonym map
   │
   ▼
score every event in the 14-day window:
   keyword overlap × title weight
   + kind/platform match bonus
   + exponential recency decay (half-life 3.5 days)
   + session co-occurrence bonus
   │
two-key dedupe (URL + (domain, title-stem))
   │
   ▼
top-N episodic results
   │
   ├──► group by session_id ──► top-N sessions
   │
   └──► split each session by domain + token affinity
                                  ──► top-N micro-contexts
```

No embeddings on the episodic side — the per-day JSONL files are small
enough that a Python scoring loop wins on simplicity and stays under a
100ms budget on 10K-event logs. Embeddings are reserved for the file
search, which has a different scale problem.

---

## Sessions and micro-contexts

A **session** is a contiguous block of activity bounded by ~30 minutes
of silence. The boundary is purely temporal; no clustering. Sessions
answer *what was I doing around the same time as the moment I just
recalled?*

A **micro-context** is what the *user* mentally was doing. Sessions are
often too coarse — a three-hour evening contains several distinct
threads. The reconstructor splits a session into 2–6 micro-contexts by
two passes:

1. **Domain / path affinity** — events touching the same site or the
   same folder cluster together.
2. **Token Jaccard** — events whose title tokens overlap above a
   threshold join the same context.

Each micro-context surfaces in the launcher as a single card listing
its participating events with one **Resume** action.

## Memory threads

A **thread** is an evolving topic the user keeps returning to over
days, sessions, and surfaces. Where a session is a 30-minute window
and a micro-context is a topic-coherent sub-block, a thread is the
*persistent shape* of an ongoing concern — *healthcare startup*,
*WebSocket retry logic*, *RLHF research*.

Threads are the next abstraction layer on top of events / sessions /
contexts / resurfacing. The engine is deterministic — same events in,
same threads out — and uses five heuristic signals (span, density,
surface diversity, session diversity, recency) blended into a single
confidence score in `[0, 1]`. Threads strengthen as they accumulate
events and decay naturally when activity stops.

Identity (id, topic_key, `created_at`, title) is cached at
`~/.recall/threads.json`; state (confidence, event_count, …) is
recomputed from events on every rebuild. Deleting the cache is safe.

The launcher surfaces active threads at the top of the idle digest
under *Active memory threads*. Click a row and the launcher types the
thread's title into the input, firing the existing retrieval pipeline
— that's the open-thread flow: chronological reconstruction through
the sessions and micro-contexts the search endpoint already returns.

See [`docs/architecture/threading.mdx`](apps/docs/architecture/threading.mdx)
for the full lifecycle, signal table, and decay model.

## Thread evolution

Once a thread exists, the next question is *how it changed over
time*. **Evolution** segments a thread's event stream into
chronological phases — `Research` → `Implementation` → `Revisit` —
each labelled with a transition (`initial`, `pivot`, `acceleration`,
`revisit`, `resumption`, `continuation`).

The segmentation is deterministic: temporal gaps, surface-type
shifts (browser → code → docs), and vocabulary Jaccard drops decide
where one phase ends and the next begins. Per-phase
`momentum_score` and `revisit_score` carry the cognitive intensity
and the "have I been here before?" signal.

When you click a thread in the launcher, a single quiet horizontal
strip appears above the search results showing the phases in order.
No dashboard, no chart axes, no badges — the hairline dividers
between pills colour-code the transition, and that's the only
visual encoding.

See [`docs/architecture/evolution.mdx`](apps/docs/architecture/evolution.mdx)
for the full segmentation algorithm and signal table.

## Continuity recovery

The seventh layer answers the question the user actually asks
Monday morning: *what should I open right now to keep going?*

A **recovery candidate** is the minimum coherent context to resume
thinking on one topic. It carries three representative events, a
list of one-click open targets (up to eight URLs and file paths),
and two independent scores: **continuity** (how intact the context
is) and **recovery confidence** (how likely the user wants to
resume). The launcher's idle digest leads with up to three
candidates under *Continue where you left off*; clicking a row
opens every URL and file in sequence — one click, no narration.

The detection heuristic is straightforward: an *abandonment signal*
fires when the last evolution phase carried real momentum, then
went idle for 6 h to 7 days. That's the window of recoverable
attention — long enough to be "interrupted", short enough that the
context is still live in the user's head.

Hard ceilings, enforced at the API layer:

- **Three candidates max.** A list of four is no longer "the next
  thing to do"; it's an inbox.
- **No on-disk cache.** A candidate is the current recoverable
  shape, not history. Stale "restore me" cards are worse than
  no cards.
- **No telemetry on restoration.** The launcher opens the targets
  and forgets about it.

Restoration is **choreographed**, not arbitrary. Files open first
(they ground the work in your local artifacts), chats next (the
conversation that informed the work), then tabs grouped by domain,
then any repeated searches. Each candidate carries a deterministic
`preview_caption` — *"3 tabs · 2 files · 1 chat · last active during
implementation"* — assembled from the same inputs that produced the
candidate. No AI prose, no LLM summary. Same events in, same caption
out, byte for byte.

Set `RECALL_EXPLAIN_RECOVERY=1` to see per-step reasons and skip
explanations in the launcher's restore acknowledgement.

See [`docs/architecture/recovery.mdx`](apps/docs/architecture/recovery.mdx)
for the full signal table, suppression rules, and orchestration
choreography.

---

## Keyboard

| Shortcut | Action |
|---|---|
| `Ctrl + Space` | Toggle the launcher |
| `↑` / `↓` | Move selection |
| `Enter` | Open the file / URL / chat |
| `Ctrl + Enter` | Reveal in Explorer / Finder |
| `Ctrl + C` | Copy the file path |
| `Ctrl + M` | Copy a memory summary (title + why-matched + sources) |
| `Esc` | Hide the launcher |
| `Ctrl + ,` | Open settings |

The launcher is keyboard-first. The mouse exists for the tray icon and
the **Watch again** button.

---

## Performance

Numbers from the in-process smoke test
([`_smoke_api.py`](_smoke_api.py)) on a 10,000-event log:

| Operation | Median | Notes |
|---|---|---|
| `GET /v1/search` (cold) | ~95 ms wall, ~55 ms server | First call pays the JSONL parse |
| `GET /v1/search` (warm) | ~70 ms wall, ~50 ms server | Per-file parse cache + cached searchable text |
| `POST /v1/events/{kind}` | <2 ms | Validate + append |
| `GET /v1/health` | <1 ms | |

Optional dependency `orjson` (in `requirements.txt`) drops the JSONL
parse cost by ~5x; the code falls back to stdlib `json` if it isn't
installed.

---

## Repository structure

```
recall/
├── apps/
│   ├── desktop/               PyQt6 launcher + FastAPI service
│   │                          (Python tree currently at repo root;
│   │                           see apps/desktop/README.md)
│   ├── web/                   Next.js marketing site
│   ├── docs/                  Mintlify documentation site
│   └── extension/             Chrome / Edge MV3 extension (~200 lines)
│
├── packages/
│   ├── shared/                shared constants, vocabulary, helpers
│   ├── design-system/         tokens + UI primitives
│   └── contracts/             API contracts + event schemas
│
├── infra/
│   ├── installers/            installer specs + signing notes
│   ├── release/               release pipeline assets
│   └── scripts/               dev bootstrap + maintenance scripts
│       ├── dev.ps1            Single-command dev (Windows)
│       ├── dev.sh             Single-command dev (macOS / Linux)
│       └── build_icon.py      Icon generator
│
├── assets/
│   ├── screenshots/           product captures (light + dark)
│   ├── branding/              logos, icon sources, brand notes
│   └── demos/                 demo scripts, recording cues
│
├── archive/                   deprecated work kept for context
│
├── ROOT_ARCHITECTURE.md       system boundaries + dependency graph
├── REPO_STRUCTURE.md          why pseudo-monorepo, split criteria
├── CLAUDE.md                  engineering charter
├── README.md, CHANGELOG.md, …
│
└── (Python tree at repo root for now)
    ├── app/                   pure-Python engine + PyQt6 launcher
    │   ├── core/              events, sessions, microcontexts,
    │   │                      resurfacing, threads, evolution,
    │   │                      recovery, episodic, search, …
    │   ├── ui/                launcher, widgets, settings, tray
    │   └── main.py            process wiring
    ├── api/                   FastAPI service (services/, schemas.py)
    ├── recall.py              CLI entry point
    ├── _smoke_api.py          29-section end-to-end test
    ├── recall.spec            PyInstaller spec
    └── requirements.txt
```

The pseudo-monorepo layout above is the **target structure**.
The Python tree currently sits at the repo root because
moving it requires PyInstaller verification on Windows + macOS
+ Linux — see [`apps/desktop/README.md`](apps/desktop/README.md)
for the migration plan and gate.

---

## Roadmap

Actively planned:

- **macOS / Linux launch-on-login** — currently Windows-only via the
  registry. LaunchAgents and `~/.config/autostart` are next.
- **Open-at-match for code files** — shell out to `code -g path:line`
  when VS Code is on PATH.
- **Cross-folder semantic neighbors** — extend *Related* beyond same-
  folder peers.
- **Real Firefox and Safari extensions** — the current extension is
  MV3 (Chrome / Edge / Brave).
- **Memory review dialog** — a weekly surface that complements the
  daily digest.

Deliberately *not* on the roadmap:

- Cloud sync, accounts, multi-user
- LLM chat over your files
- Telemetry of any kind

---

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for setup, conventions, and the
review process. Security disclosures: [SECURITY.md](SECURITY.md).
Community expectations: [CODE_OF_CONDUCT.md](docs/CODE_OF_CONDUCT.md).

Issues, ideas, and pull requests are welcome. The audit at
[AUDIT_REPORT.md](docs/engineering/AUDIT_REPORT.md) lists the current consistency gaps
and good first issues.

---

## License

[MIT](LICENSE).

---

## Acknowledgements

Built on
[sentence-transformers](https://www.sbert.net/),
[ChromaDB](https://www.trychroma.com/),
[FastAPI](https://fastapi.tiangolo.com/),
[PyQt6](https://www.riverbankcomputing.com/software/pyqt/),
[watchdog](https://github.com/gorakhargosh/watchdog), and
[orjson](https://github.com/ijl/orjson). These projects do most of the
work; Recall is mostly composition and taste.
