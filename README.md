<div align="center">

# Recall

**Computers remember files. Humans remember ideas.**

Recall is a local-first AI memory layer for your laptop. Press **Ctrl + Space**,
type the half-thought you've been carrying, and Recall surfaces the file, the
passage, and the connected ideas — even when you don't remember the filename,
the folder, or the exact words.

Everything stays on your device. No accounts. No cloud. No telemetry.

</div>

---

## The problem

You don't remember filenames. You remember ideas — half-formed, contextual,
connected to what else you were thinking about at the time. Spotlight, Windows
Search, and `grep` all assume you remember a string. Real memory doesn't work
that way.

Recall is built for the way you actually think back: you remember a *healthcare
startup idea from last winter*, not `pitch_deck_v3_final2.pdf`.

---

## Features

### Semantic memory retrieval

Natural-language queries against your local files. Query and chunk both pass
through `all-MiniLM-L6-v2`; results are ranked by cosine similarity with a
0.30 floor that cuts sub-noise matches before they reach you. A small,
capped layer of boosts (filename hits, recency within 30 / 90 days, exact
phrase in the chunk) sits on top of the cosine score — never enough to
override semantic ranking, just enough to break ties between near-equal
results in the way a human would.

### Memory clustering

Related fragments — a pitch deck, the notes you wrote alongside it, the code
you started — surface as one memory card with every source listed underneath.
Cluster heuristic: same parent folder + at least three shared content stems
across chunks.

### Cross-source intelligence

When a memory spans formats (PDF + MD + PY), the preview labels it explicitly:
*Spans PDF, MD, PY — same idea across formats.* The same thought living in
multiple files becomes visible as one thought.

### Memory resurrection

Files older than 90 days that still match your query are tagged on their row:
*resurfaced from Mar 2024.* Old threads return at the right moment without
nagging you the rest of the time.

### Daily memory review

Open the launcher with an empty input and the body is a calm two-section
digest:

- **Recently active** — the last week of memories.
- **Resurfaced this week** — older work, deterministic-shuffled by today's
  date so each day's resurfacing feels different without being arbitrary.

### Live indexing

A `watchdog`-based file watcher runs in the background. Save a file and it's
reindexed within ten seconds. After the first scan, you never click an
"Index now" button again.

### Memory-first vocabulary

Nothing in the UI says *index*, *embedding*, *chunk*, or *similarity floor*.
The product talks about memories, sources, and thoughts. Internal field names
stay technical; user copy stays human.

### Smart actions

- **Enter** — open the file in its native handler.
- **Ctrl + Enter** — reveal in Explorer / Finder.
- **Ctrl + C** — copy the file path.
- **Ctrl + M** — copy a clean memory blob (title + why-matched + sources).

Every action acknowledges itself with a short footer beat (`Opening …`,
`Path copied · …`) so Enter never silently dismisses the launcher.

---

## Architecture

```
┌──────────────────────────────────────────────────────────┐
│                   Recall (tray-resident)                 │
│                                                          │
│   ┌──────────┐     Ctrl+Space     ┌──────────────────┐   │
│   │  Hotkey  │ ──────────────────►│     Launcher     │   │
│   │ (pynput) │                    │     (PyQt6)      │   │
│   └──────────┘                    └────────┬─────────┘   │
│                                            │             │
│                                       query embed        │
│                                            ▼             │
│                                    ┌───────────────┐     │
│                                    │ Search Engine │     │
│                                    │   top-k × 4   │     │
│                                    │   → dedupe    │     │
│                                    └───┬───────┬───┘     │
│                                        ▼       ▼         │
│                                  ┌─────────┐ ┌────────┐  │
│                                  │ChromaDB │ │ MiniLM │  │
│                                  │persisted│ │ model  │  │
│                                  └────┬────┘ └────────┘  │
│                                       ▲                  │
│                                       │ writes           │
│                                  ┌────┴────┐             │
│                                  │ Indexer │             │
│                                  │  (mtime │             │
│                                  │ incremental)│         │
│                                  └────┬────┘             │
│                                       ▲                  │
│                                  ┌────┴────────┐         │
│                                  │File Watcher │         │
│                                  │  (watchdog) │         │
│                                  └─────────────┘         │
└──────────────────────────────────────────────────────────┘
                          │
                          ▼
                ~/Documents, ~/Desktop, ~/code
                  (the folders you choose)
```

Three layers, hard boundaries:

- **Core** — `config`, `parsers`, `chunker`, `embeddings`, `db.store`,
  `indexer`, `search`, `watcher`, `autostart`. Pure Python, zero Qt imports.
  Importable from a REPL; testable in isolation.
- **UI** — `styles`, `widgets`, `launcher`, `settings`, `onboarding`,
  `hotkey`. Sits on top of the core through two thin classes (`SearchEngine`,
  `Indexer`). UI never reaches into ChromaDB or sentence-transformers
  directly.
- **Process glue** — `main.py` wires Config → Store → Model → Indexer →
  SearchEngine → Launcher → Settings → tray icon → hotkey → file watcher.
  Single-instance lock at `~/.recall/instance.lock`.

State lives entirely in `~/.recall/` — config, vector index, instance lock.
Removing that folder fully resets the app.

---

## Local-first by design

| What stays on your device | What doesn't |
|---|---|
| Your files (read, never copied) | — |
| Embeddings, computed on your CPU | — |
| The vector index (ChromaDB SQLite) | — |
| Search queries | — |
| Settings, folder list, autostart preference | — |
| Memory digest, resurfaced threads | — |

The **only** network call Recall makes is the one-time download of
`all-MiniLM-L6-v2` from Hugging Face on first run (~80 MB). After that, the
loader uses `local_files_only=True` and never touches the network — no
model-update HEAD requests, no telemetry, no analytics. ChromaDB anonymous
telemetry is disabled at boot. Hugging Face progress bars are silenced.

There are no accounts to create, no credentials to manage, no servers to
trust.

---

## Installation

### Prebuilt (recommended)

Download the latest release for your platform and run `Recall.exe` (Windows)
or `Recall` (macOS / Linux). The first launch shows a one-page welcome that
auto-suggests Documents and Desktop. Pick folders, click **Start
remembering**, and you're done — indexing runs in the background while the
launcher becomes immediately usable.

### From source

```bash
git clone https://github.com/yourname/recall.git
cd recall
python -m venv .venv
.venv\Scripts\activate          # Windows
# source .venv/bin/activate     # macOS / Linux
pip install -r requirements.txt
python recall.py
```

Requires Python 3.10+. The first index pass downloads the embedding model
(~80 MB) once into the Hugging Face cache. Subsequent runs are fully offline.

### Try it without indexing — demo mode

Demo mode loads a curated in-memory dataset of ten sample memories spanning
healthcare-startup notes, RL research, websocket production work, and a few
older pitches. No folders are scanned, no embedding model is loaded, no
ChromaDB writes happen — useful for screen recordings, evaluation, or just
seeing what the launcher feels like before pointing it at real files.

```bash
RECALL_DEMO=1 python recall.py        # macOS / Linux
$env:RECALL_DEMO=1; python recall.py  # Windows / PowerShell
# or
python recall.py --demo
```

Try queries like *healthcare startup*, *websocket retry*, *rl reward
shaping*, or *pediatric triage*.

### Boot diagnostics

```bash
RECALL_DEBUG=1 python recall.py       # macOS / Linux
$env:RECALL_DEBUG=1; python recall.py # Windows / PowerShell
# or
python recall.py --debug
```

Emits per-stage `>> name` and `[OK]/[SLOW] name (Nms)` lines so a hang
during boot points at exactly which stage is responsible. In normal mode
only failures and stages slower than one second are printed.

### Build a standalone executable

```bash
pip install pyinstaller
python scripts/build_icon.py     # writes app/assets/icon.ico (optional)
pyinstaller recall.spec
```

Output: `dist/Recall/Recall.exe` (Windows) or `dist/Recall/Recall` (macOS,
Linux). Ship the entire `dist/Recall/` folder — it's self-contained. The spec
auto-detects the icon if present and silently builds without it if not.

### Engine-only (no UI)

For programmatic retrieval testing:

```bash
python -m app.cli add ~/Documents/notes
python -m app.cli index
python -m app.cli repl
recall> the websocket retry thing
```

Same `Recall` facade is one-line usable from a Python REPL — see
`app/__init__.py`.

---

## Keyboard

| Shortcut | Action |
|---|---|
| `Ctrl + Space` | Toggle the launcher |
| `↑` / `↓` | Move selection |
| `Enter` | Open the memory's file |
| `Ctrl + Enter` | Reveal in Explorer / Finder |
| `Ctrl + C` | Copy the file path |
| `Ctrl + M` | Copy a memory summary |
| `Esc` | Hide the launcher |
| `Ctrl + ,` | Open settings |

The launcher is keyboard-first. The mouse exists for the tray icon and a
single **Watch again** button; every other action is reachable from the home
row.

---

## Tech stack

| Layer | Tech | Why |
|---|---|---|
| UI | PyQt6 | Native frameless windows, real tray, mature on Windows |
| Hotkey | pynput | Cross-platform global hotkey without admin rights |
| File watcher | watchdog | Standard library for filesystem events |
| Embeddings | sentence-transformers · `all-MiniLM-L6-v2` | ~80 MB, runs on CPU, normalized vectors |
| Vector store | ChromaDB (persistent) | Cosine HNSW, embeds + metadata, telemetry off |
| Parsers | pypdf, plain text, 30+ code formats | Lazy imports — missing optional deps shrink the supported set, never crash |
| Packaging | PyInstaller | Standalone executable per platform |

No LangChain. No agent framework. No vector database server. No cloud
infrastructure.

---

## Roadmap

Actively planned:

- **macOS / Linux launch-on-login** — currently Windows-only via the
  registry. LaunchAgents and `~/.config/autostart` are next.
- **Open-at-match for code** — detect VS Code on PATH, shell out with
  `code -g path:line` so the cursor lands on the matched chunk.
- **Cross-folder semantic neighbors** — the *Related* section currently uses
  same-folder peers. An embedding-based query would surface conceptually
  related work across the whole index.
- **Memory review dialog** — a dedicated weekly review surface to complement
  the daily digest.
- **OCR refinement** — current OCR works but indexing every image quadruples
  first-run time. Needs a smarter trigger (screenshots-only, e.g.).

Deliberately *not* on the roadmap: cloud sync, accounts, multi-user,
browser extensions, mobile app, LLM chat over your files.

---

## Philosophy

A few principles, written down so they don't drift:

**One magical interaction beats fifty features.** The launcher does one thing
well: recover a memory from a half-thought. Everything else is in service of
that.

**Local-first is not a marketing posture.** It's an architectural commitment.
The product cannot depend on the network for any user-facing operation. Every
feature gets evaluated against this rule before it ships.

**Memory, not search.** The vocabulary matters. Files become memories. Chunks
become passages. Indexing becomes remembering. The words a product uses shape
how its users think about it — and how its developers think about adding to
it.

**Restraint is the feature.** No chat layer. No agent loop. No telemetry. No
accounts. Adding things is easy; the discipline is in what you choose not to
add.

**The engine is small enough to read.** The retrieval core (config, parsers,
chunker, embeddings, store, indexer, search, watcher) fits in an afternoon
of careful reading. That's not an accident — it's a constraint.

---

## License

MIT.

---

## Acknowledgements

Built on the shoulders of
[sentence-transformers](https://www.sbert.net/),
[ChromaDB](https://www.trychroma.com/),
[PyQt6](https://www.riverbankcomputing.com/software/pyqt/), and
[watchdog](https://github.com/gorakhargosh/watchdog). These projects do most
of the work; Recall is mostly composition and taste.
