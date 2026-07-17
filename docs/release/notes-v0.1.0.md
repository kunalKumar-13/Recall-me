# Recall v0.1.0 — first public alpha

**Never lose the thread.** Recall reconstructs what you were working
on — the tabs, the files, the half-finished chat — and hands it back
in one keystroke. 100% local: no cloud, no accounts, no telemetry.
Everything lives in plain files in `~/.recall/`; delete the folder
and it never happened.

This is an early alpha for people comfortable running things from
source. It's honest software: every claim below is in the repo.

## What's in the box

**The launcher** (`Recall_0.1.0_aarch64.dmg`, ~2.4 MB, Apple Silicon)
- ⌃Space summons a borderless panel over any app
- Continue where you left off: recovery candidates with honest
  captions ("2 tabs · 1 file · returned 3× · last active during
  implementation")
- One keystroke restores work in order — files → chats → tabs by
  domain → searches, gently staggered
- Search memory and disk together (episodic + semantic file search)
- Active threads with evolution phases, "on your radar" resurfacing
- ⌘, settings: re-record the hotkey live, start at login

**The browser extension** (Chrome · Edge · Brave · Arc, load unpacked
from `apps/extension/`)
- Quiet capture: pages, searches, AI chats, SPA routes, attention
  dwell with work-block hints — titles and URLs only, never page
  content, never incognito
- Durable offline outbox: daemon down means queued, never lost
- The popup instrument: continue + restoration plan, today's
  24-hour rhythm, threads, live tail — ⌘K to search
- Real controls: per-kind capture toggles, pause-for-an-hour,
  one-click private-sites exclusion

**The engine** (runs from the repo for now)
- Seven deterministic layers: events → sessions → contexts →
  resurfacing → threads → evolution → recovery
- Performance budgets enforced by a 37-section test suite
  (search <60 ms, writes <2 ms)
- The daily continuity loop: Recall grades itself — returns,
  resumes, verdicts. Counts only, never content.

**The console** — open `/console` on the site (or locally): a
read-only engine room that talks to your daemon from your own
browser. Zero proxying; your data never touches a server.

## Install (the honest version)

1. **The engine first** (the .dmg is the launcher shell; the engine
   ships from source in this alpha):
   ```bash
   git clone https://github.com/kunalKumar-13/Recall-me && cd Recall-me
   pip install -r requirements.txt
   python recall.py
   ```
2. **The launcher**: open the `.dmg`, drag Recall to Applications.
   It's ad-hoc signed — right-click → Open the first time.
3. **The extension**: `chrome://extensions` → Developer mode →
   Load unpacked → select `apps/extension/`.
4. Work normally. Next interruption, press **⌃Space**.

## Known edges

- macOS Apple Silicon only; Windows/Linux are on the roadmap
- Unsigned build (Gatekeeper warning is expected; notarization
  lands with a paid certificate)
- The engine requires Python 3.12+ until the bundled build ships
- Desktop app-focus capture is opt-in (`desktop_capture_enabled`)

Delete `~/.recall/` at any time — that is the full reset, and the
only uninstall step besides dragging the app to the trash.
