# ROADMAP — Recall v2 launcher

The v2 launcher is a **thin Tauri client** over the existing Python engine +
FastAPI service at `127.0.0.1:4545`. The engine and its seven layers are the
core IP and are **not** rewritten here (see [V2_BRIEF.md](V2_BRIEF.md) and
[apps/launcher/DESIGN.md](apps/launcher/DESIGN.md)). Recovery is the hero;
search is secondary.

Each phase ends with a **local commit** (never push; no AI attribution).
These checkboxes are the source of truth for where we are — update them as
phases land so any session resumes from the right place.

- [x] **Phase 0 — Foundations.** Engine running, capture live, CI green, repo clean.
- [ ] **Phase 1 — Launcher foundation** *(in progress)*. Tauri panel on
      Ctrl+Space, Recovery hero on real `/v1/recovery/recent` data,
      hide-on-blur, content-fit resize, vibrancy.
- [x] **Phase 2 — Search surface.** Persistent search field at the top
      (Raycast-style); empty = the Recovery hero, typing renders the
      episodic + session + micro-context bundle on the thread spine with
      per-layer node hues (moment/session/context), keyboard-first (↑↓
      move, ↵ open, esc clear). Backed by the live `/v1/search`; Enter
      opens the selected result via the `open_target` command.
      *Code-complete + type/compile-checked; visual verification in-app
      pending (needs a real window + captured data).*
- [ ] **Phase 3 — Threads & evolution.** Open a thread to see its phases
      (research → impl → revisit).
- [ ] **Phase 4 — Restore choreography.** Enter on a candidate reopens the
      work in order (files → chats → tabs by domain → searches).
- [ ] **Phase 5 — Settings & polish.** Configurable hotkey, folder picker,
      tray, onboarding, launch-on-login UX.
- [ ] **Phase 6 — Ship.** Signed + notarized `.dmg`, clean install, demo
      script on real sessions.

---

## Capture track — make capture real, clean, and scalable

The launcher is only as good as the event log behind it. This track is the
**gate**: a continuity surface with an empty `~/.recall/events/` is empty no
matter how polished. Capture runs through the MV3 extension
(`apps/extension/background.js`) → `127.0.0.1:4545` → the seven-layer engine.
Charter holds: local-first, deterministic, additive, no DOM scraping, no
telemetry. See the capture audit for the full diagnosis.

- [x] **Capture C0 — Audit.** Root cause of the empty hero pinned: the
      extension was not loaded (reserved-underscore filename blocked Chrome,
      now removed), capture used a fire-and-forget sender with no queue, and
      only 2 stale test events were on disk.
- [ ] **Capture C1 — Make capture real & verifiable** *(in progress)*. Load
      the extension; confirm organic `browser`/`search`/`chat` events reach
      the engine; surface an honest "events captured today" self-check. Fix
      the build/doc drift the audit found (stale committed popup bundle,
      README/architecture component-name mismatch).
- [x] **Capture C2 — Refactor core (modular + tested).** `background.js`
      split into `capture/sources.js` (listeners + title-settle),
      `capture/normalize.js` (pure `(url,title)→{kind,payload}`, node-tested
      via `capture/normalize.test.js`), and `capture/outbox.js` (delivery).
      ES-module service worker; no behaviour change to what lands on disk.
- [x] **Capture C3 — Robust capture (zero loss).** Persistent outbox in
      `chrome.storage.local`; batched POST to **`/v1/events/batch`** with
      `chrome.alarms` retry (survives MV3 worker eviction *and* daemon
      downtime); `webNavigation.onHistoryStateUpdated` for SPA-route capture;
      capture-time `ts` preserved through delayed flushes. Server side:
      `POST /v1/events/batch` shipped (smoke §34). *Code-complete; the
      remaining open item is C1 — load the extension and confirm organic
      events flow end-to-end (only reproducible in a real browser).*
- [ ] **Capture C4 — Work-session signal (the moat).** Capture focus/dwell/
      active-tab context and a client work-session hint, so the engine can
      group *work-blocks* behaviourally, not just by 30-minute clock windows.
