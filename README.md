# Recall

### Ask your computer what you forgot.

Recall is a local-first AI memory layer for your laptop. Press
**Ctrl + Space** anywhere, type what you vaguely remember — Recall
recovers the file, the passage, and the connected ideas across your
notes, code, and PDFs.

Everything stays on your device. No accounts. No cloud. No telemetry.

---

## Run from source

```bash
git clone <this repo> recall
cd recall
python -m venv .venv
.venv\Scripts\activate          # Windows
# source .venv/bin/activate     # macOS / Linux
pip install -r requirements.txt
python recall.py
```

The first launch shows a one-page welcome that auto-suggests Documents
and Desktop. Pick folders, click **Start remembering**, and the launcher
is ready as soon as the first batch of memories is captured.

The embedding model (~80 MB) downloads once on first run, then Recall
is fully offline.

---

## Build a standalone .exe (Windows / macOS / Linux)

```bash
pip install pyinstaller
pyinstaller recall.spec
```

Output: `dist/Recall/Recall.exe` (Windows) or `dist/Recall/Recall`
(macOS, Linux). Ship the whole `dist/Recall/` folder — it's
self-contained.

To set an app icon, drop a 256×256 `icon.ico` at `app/assets/icon.ico`
and uncomment the `icon=` line in [recall.spec](recall.spec).

---

## How it works

| Layer | Tech |
|---|---|
| UI | PyQt6 (frameless, translucent, tray-resident) |
| Hotkey | pynput (`Ctrl + Space`) |
| Background watcher | watchdog (incremental re-indexing) |
| Embeddings | sentence-transformers · `all-MiniLM-L6-v2` (offline-first) |
| Vector store | ChromaDB persistent client at `~/.recall/chroma/` |
| Parsers | PDF, Markdown, plain text, 30+ code formats |

State lives at `~/.recall/`. Removing that folder fully resets the app.

---

## Keyboard

| Key | Action |
|---|---|
| `Ctrl + Space` | Toggle the launcher |
| `↑ / ↓` | Move selection |
| `Enter` | Open the memory's file |
| `Ctrl + Enter` | Reveal in Explorer / Finder |
| `Ctrl + C` | Copy the file path |
| `Ctrl + M` | Copy a memory summary (title + why + sources) |
| `Esc` | Hide the launcher |
| `Ctrl + ,` | Open settings |

---

## Boot diagnostics (optional)

If something's off:

```bash
RECALL_DEBUG=1 python recall.py     # env var
python recall.py --debug            # CLI flag
```

You'll see every boot stage with timing. Stages over 1 s are flagged
`[SLOW]` even with debug off.

---

## REPL / CLI (engine-only, no UI)

For ad-hoc retrieval testing without the launcher:

```bash
python -m app.cli add ~/Documents/notes
python -m app.cli index
python -m app.cli repl
recall> the websocket retry thing
```

See [app/cli.py](app/cli.py) for the full set of commands. The same
`Recall` facade is also one-line usable from a Python REPL — see
[app/__init__.py](app/__init__.py).

---

## Privacy

- **No file uploads.** Files are parsed locally.
- **No cloud embeddings.** The model runs on your CPU.
- **No telemetry.** Hugging Face progress bars and ChromaDB telemetry
  are both disabled at boot.
- **No accounts.** There's nothing to sign into.

The only network call ever made is the one-time download of the
embedding model from Hugging Face on first run.
