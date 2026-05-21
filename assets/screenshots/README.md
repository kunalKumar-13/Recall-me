# `assets/screenshots`

Product captures for the docs site, marketing site, and README.

## Status — real captures landed (Phase 4L + 5A.1)

These are no longer placeholders. Every PNG below is a **real,
deterministic render** produced by the capture pipeline — same
inputs in, same pixels out — not a hand-grabbed screenshot.

| File | Surface | Captured by |
|---|---|---|
| `launcher-digest.png` | launcher idle digest — recovery, investigations, resurfacing, trust | `infra/scripts/capture/capture_launcher.py` |
| `launcher-loading.png` | launcher skeleton-loading state | `capture_launcher.py` |
| `launcher-empty.png` | launcher empty state ("Recall is ready") | `capture_launcher.py` |
| `launcher-offline.png` | launcher offline state | `capture_launcher.py` |
| `launcher-first-week.png` | first-week "continuity is building" state | `capture_launcher.py` |
| `recovery-card.png` | recovery card, resting | `capture_recovery.py` |
| `recovery-card-focused.png` | recovery card, keyboard-focused (focus ring) | `capture_recovery.py` |
| `extension-connected.png` | extension popup, populated memory surface | `apps/extension/ui/capture_extension.mjs` |
| `extension-missing.png` | extension — Recall never installed (Install CTA) | `capture_extension.mjs` |
| `extension-disconnected.png` | extension — Recall installed, not running | `capture_extension.mjs` |
| `extension-offline.png` | extension — browser offline | `capture_extension.mjs` |
| `extension-loading.png` | extension — first daemon read in flight | `capture_extension.mjs` |
| `settings-dialog.png` | Settings dialog with a default `Config` fixture (Phase 5F) | `infra/scripts/capture/capture_settings.py` |
| `control-room.png` | the founder dashboard (`apps/admin/web/`) at `localhost:3000`, Phase 5G | Edge `--headless=new --screenshot` against `next dev` |
| `doctor-output.png` | the `recall doctor` text output rendered as a terminal panel | `infra/scripts/capture/capture_doctor.py` |
| `installer-flow.png` | the silent-install log's milestone lines (start, root key, install dir, icons, success, close) | `infra/scripts/capture/capture_installer_flow.py` |

## Regenerating

```bash
# launcher + recovery + settings + doctor + installer-flow (offscreen Qt)
python infra/scripts/capture/capture_launcher.py
python infra/scripts/capture/capture_recovery.py
python infra/scripts/capture/capture_settings.py
python infra/scripts/capture/capture_doctor.py
python infra/scripts/capture/capture_installer_flow.py

# extension popup (headless Chromium via Playwright)
cd apps/extension/ui && node capture_extension.mjs

# control room (Edge headless against `next dev`)
cd apps/admin/web && npm run dev &
msedge --headless=new --window-size=1440,2400 \
    --screenshot=assets/screenshots/control-room.png http://localhost:3000
```

The pipeline is documented in
[`infra/scripts/capture/README.md`](../../infra/scripts/capture/README.md).

## Still pending

| Surface | Needs |
|---|---|
| Resume-in-progress moment | a capture against a live restoration (clean-machine run) |
| Light/dark launcher variants | the launcher captures are dark-theme only so far |
| Installer wizard pages | the silent-install log render closes this for Phase 5G; full wizard capture would need UI automation (AutoHotkey / Pywinauto) |

Phase 5G filled the *control room* gap and added *doctor* +
*installer-flow* captures, so the 15-surface checklist from the
directive is closed (modulo the *resume-in-progress* moment, which
needs the clean-machine VM walk to exist).
These are tracked in [`GO_NO_GO.md`](../../docs/release/GO_NO_GO.md) (gate 6).
