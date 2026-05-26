# SCREEN_INDEX — frozen capture set for v0.1.0-rc1

The single source of truth for which screenshots
ship with RC1, what each one shows, and where to
find it.

**Freeze rule (RC1):** any new capture added to
`assets/screenshots/` must land inside one of the
four directories below. Anything else gets
archived to `archive/screenshots-history-rc/`.

---

## The frozen four

`assets/screenshots/` now contains exactly four
subdirectories:

| Directory       | What it captures                                  | Phase that froze it |
|-----------------|---------------------------------------------------|---------------------|
| `launcher-7e/`  | The live PyQt6 launcher (formerly *launcher-live* in directive vocabulary) | 7E.1 |
| `extension-7a/` | The live Chrome MV3 extension popup               | 7A |
| `alpha/`        | The alpha cohort control-room reference shots     | 5K |
| `demo/`         | The demo-mode populated state                     | 6D / 8D |

Total: **4 dirs, 19 PNGs.** Down from 8 dirs +
11 root orphans at the close of 8C.

---

## What got archived in 8D

Moved to `archive/screenshots-history-rc/`:

| Item                                  | Why archived |
|---------------------------------------|--------------|
| `extension-v2/` (5 PNGs)              | Superseded by `extension-7a/` |
| `launcher-v2/` (7 PNGs)               | Pre-7E launcher iteration     |
| `launcher-v3/` (5 PNGs)               | Pre-7E launcher iteration     |
| `root-orphans/` (11 PNGs)             | Loose root-level captures, no parent dir |

Nothing deleted. Every PNG is recoverable from
the archive folder if needed.

---

## Coverage map — every required RC1 screen

The 8D directive named six required surfaces.
This table maps each one to its capture file:

| Required surface | File                                              | Status |
|------------------|---------------------------------------------------|--------|
| **hero**         | `launcher-7e/home.png`                            | ✅ live |
| **empty**        | `launcher-7e/no_hero.png` + `demo/demo-extension-empty.png` | ✅ live |
| **resume**       | `launcher-7e/high.png` + `extension-7a/resume.png` | ✅ live |
| **capture**      | `extension-7a/capturing.png`                      | ✅ live |
| **extension**    | `extension-7a/active.png` + `extension-7a/search.png` | ✅ live |
| **control room** | `alpha/alpha-control-room.png`                    | ⚠️ stand-in — see note below |

The `alpha/alpha-control-room.png` is the closest
existing capture of the admin web app. A
dedicated `control-room-7c/` capture set is open
as a follow-up; it doesn't block RC1 because the
landing page links to `alpha/` for now and the
control room itself ships from `apps/admin/web/`
with documentation in
[`STABILITY/CONTROL.md`](STABILITY/CONTROL.md).

---

## Per-directory inventory

### `launcher-7e/` (5 files)

| File          | Captures                              |
|---------------|---------------------------------------|
| `home.png`    | Populated digest — the canonical hero shot |
| `high.png`    | HIGH-trust recovery card present      |
| `med.png`     | MEDIUM-trust recovery card            |
| `low.png`     | LOW-trust recovery card               |
| `no_hero.png` | Empty / first-run state, no recovery  |

Provenance:
[`infra/scripts/capture/capture_launcher_v3.py`](infra/scripts/capture/capture_launcher_v3.py)
runs the deterministic offscreen pipeline against
a seeded event store. Re-running the script
overwrites these files in place.

### `extension-7a/` (7 files)

| File             | Captures                              |
|------------------|---------------------------------------|
| `active.png`     | Populated, healthy daemon             |
| `capturing.png`  | `capturing` state                     |
| `demo.png`       | `demo` state                          |
| `empty.png`      | `empty` state                         |
| `offline.png`    | `offline` state                       |
| `resume.png`     | `recovery` state with hero card       |
| `search.png`     | Search overlay open                   |

Provenance: Playwright capture against the Vite
build at `apps/extension/popup/`. The two
transient states (`loading`, `reconnecting`) are
intentionally not captured — see
[`STABILITY/EXTENSION.md`](STABILITY/EXTENSION.md).

### `alpha/` (3 files)

| File                       | Captures                                  |
|----------------------------|-------------------------------------------|
| `alpha-control-room.png`   | The admin web app's overview              |
| `alpha-empty.png`          | A control-room empty-state surface        |
| `alpha-status.png`         | The cohort status block                   |

### `demo/` (4 files)

| File                          | Captures                                  |
|-------------------------------|-------------------------------------------|
| `demo-launcher.png`           | The launcher populated by the demo trace  |
| `demo-extension.png`          | The extension popup against the demo state |
| `demo-extension-empty.png`    | The extension before demo seed runs       |
| `demo-transition.png`         | The moment the demo overlay transitions out |

---

## Where the landing page reads from

`apps/web/public/screens/` mirrors the asset
folders the marketing site needs:

```
apps/web/public/screens/
├── launcher/    (pre-7E shots; needs update to launcher-7e/)
├── extension/   (pre-7A shots; needs update to extension-7a/)
├── alpha/       (current)
└── demo/        (current)
```

**Known drift:** the web site still references
`/screens/launcher/launcher-digest.png` and
`/screens/extension/extension-home.png`, which
are the pre-7E/7A files. These are visual-only
and don't block the RC1 ship gate, but a future
phase should mirror the latest captures into
`apps/web/public/screens/launcher/` and
`apps/web/public/screens/extension/`. See the
landing-check section of
[`docs/engineering/PHASE_8D_STATUS.md`](docs/engineering/PHASE_8D_STATUS.md).

---

## How to add a new capture

1. Decide which of the four directories it
   belongs in.
2. If none fits, **don't add it** — open a
   directive instead. The freeze is the freeze.
3. Use the matching harness:
   `infra/scripts/capture/capture_launcher_v3.py`
   for launcher; the extension's Playwright
   harness for the popup.
4. Keep file names short and intentional. No
   timestamps in filenames.
5. Update this index in the same commit.

---

## How to retire a capture

If a phase changes the visual surface and an old
capture becomes wrong:

1. Move the old file to
   `archive/screenshots-history-rc/<dir>/`.
2. Re-run the relevant capture harness to
   regenerate.
3. Update this index.

Never overwrite an old capture in-place if the
intent is "show how this used to look" — archive
instead.

---

## Verification

After any change to `assets/screenshots/`:

```bash
ls assets/screenshots/
# Should output exactly: README.md alpha demo extension-7a launcher-7e
```

If anything else appears, the freeze is broken
and the rogue file/dir needs to land in an
archive folder before the RC tag.
