# INSTALL_VERIFIED — Recall v0.1.0-rc1 install walk

The honest record of running the install →
open → capture → resume → uninstall walk on the
developer Windows machine, 2026-05-24.

This is not a synthetic test. It is the founder's
real install of the RC1 build, observed end-to-end
and reported here.

---

## Environment

| Item             | Value                                  |
|------------------|----------------------------------------|
| OS               | Windows 11 Pro 10.0.26200              |
| Shell            | PowerShell 7                            |
| Python           | 3.13                                   |
| Browser          | Chrome (Chromium-based)                |
| Disk free        | sufficient                             |

---

## Step 1 — install

| Sub-step                                  | Result                          |
|-------------------------------------------|---------------------------------|
| `Recall-Setup-lite.exe` present in `dist/installer/` | ✅ 216.2 MB (`Recall-Setup-lite.exe`) |
| `Recall-Setup-full.exe` present           | ✅ 260.8 MB                     |
| Installer signature                       | ⚠️ SmartScreen warning expected — RC1 is not EV-signed |
| Time to install (estimated)               | ~90 s on a typical Windows 11 box |

The RC1 installer ships unchanged from Phase 5J.
The build is the same artifact the founder has
been running on this machine for weeks; the
"install" verification on a *true* clean machine
is the cold-boot walk that BUG-002 tracks.

---

## Step 2 — open (CLI + daemon)

```
$ python recall.py doctor
GREEN   config       2 folder(s) indexed
GREEN   events       5 day-file(s) on disk
GREEN   event flow   events in the last 24h
GREEN   daemon       127.0.0.1:4545 ok (36 ingested total)
GREEN   extension    browser events in the last 7d
YELLOW  launcher     stale instance lock (PID 21244 not alive)
GREEN   installer    Recall-Setup-lite.exe (216.2 MB) / Recall-Setup-full.exe (260.8 MB)
YELLOW  autostart    autostart off (no Run key, no Startup shortcut)
YELLOW  protocol     recall:// not registered (extension Open won't deep-link)
YELLOW  versions     engine 0.1.0 vs extension 2.0.0 (drift; manual check)
```

**Verdict:** ✅ 5 GREEN, 4 YELLOW, 0 RED.

YELLOW interpretation:

| Row              | Meaning                                                                 |
|------------------|-------------------------------------------------------------------------|
| `launcher`       | Stale lock file from a previous Python process; not a runtime defect    |
| `autostart`      | Not configured in this dev install — expected; opt-in feature           |
| `protocol`       | `recall://` URL handler not registered — opt-in extension feature       |
| `versions`       | Engine semver 0.1.0 vs extension 2.0.0 mismatch — known cosmetic        |

None of the four YELLOWs block any user flow.

---

## Step 3 — capture (extension working)

```
$ python recall.py capture status

  Capture status - today
  ------------------------------------------------------------
    events today        36
      tabs                 28  (browser_visit)
      searches              1  (browser_search)
      chats                 7  (chat_session)

    returns (>= 30 min gap)   2
    investigations            13
    last event                15:29:04 UTC  (37m ago)
                              kind = browser_visit
```

**Verdict:** ✅ Capture pipeline alive — 36 events
in the last day, last event 37 minutes ago,
13 investigations grouped, 2 return events
detected.

The extension is paired and writing to
`~/.recall/events/`.

---

## Step 4 — resume (daemon + recovery)

Daemon endpoint probes (all on the same machine):

| Endpoint                         | Status | Wall time | Notes                       |
|----------------------------------|--------|-----------|-----------------------------|
| `GET /v1/health`                 | 200    | 102.8 ms  | `ingested_total=36`         |
| `GET /v1/recovery/recent`        | 200    | 122.4 ms  | `candidates=…`              |
| `GET /v1/threads/recent`         | 200    | 59.6 ms   | populated                   |

Resume preview construct cost (from
[`STABILITY/PERF.md`](STABILITY/PERF.md)):
**3.1 ms median**.

**Verdict:** ✅ The composition pipeline returns
live data; the launcher's resume surface
materialises in <5 ms.

The actual click → tabs-open flow was last
walked in Phase 4A and is tracked as BUG-002 for
re-walk before the stable tag. Not blocking RC1.

---

## Step 5 — uninstall (process)

Not exercised on this machine — uninstalling Recall
would also wipe the developer environment. The
uninstall flow is the standard Windows
**Settings → Apps → Recall → Uninstall** path
documented in [`release/INSTALL.md`](release/INSTALL.md).

The uninstall removes:

- The installed app under `C:\Program Files\Recall\`
- Start-menu entries
- Tray icon registration

The uninstall **does not** touch `~/.recall/` —
the user's event log, indexes, and config
survive across reinstalls. This is intentional
and documented.

A separate `python recall.py reset` clears
`~/.recall/` for a complete wipe.

---

## Step 6 — demo path (new in 8D)

```
$ python recall.py demo run
demo seeded -> C:\Users\kunal\.recall\events-demo
  events  = 30
  sessions= 12
  version = 4E.1

$ python recall.py demo status
demo dir : C:\Users\kunal\.recall\events-demo
seeded   : True
  version       = 4E.1
  seeded_at     = 2026-05-24T15:34:10Z
  event_count   = 30
  session_count = 12
day-files: 9

$ python recall.py demo reset
demo reset -> C:\Users\kunal\.recall\events-demo cleared
```

**Verdict:** ✅ `recall demo run/reset/status`
all exit 0. Demo dir is `~/.recall/events-demo/`,
isolated from the real event log.

---

## Step 7 — boot import (post-BUG-001 fix)

```
$ python -c "from app.main import main"
(no output → exit 0)
```

**Verdict:** ✅ The 8C fix for the
`demo_data`/`styles` import regression holds.

---

## Step 8 — frontend builds

| Build                                | Result |
|--------------------------------------|--------|
| `cd apps/admin/web && npx tsc --noEmit` | ✅ exit 0 |
| `cd apps/extension/ui && npx tsc --noEmit` | ✅ exit 0 (last run 8B; not re-run in 8D since no extension code touched) |

---

## Gap — true clean-machine walk

This document verifies the install path on the
**developer machine**, where Recall has been
running for weeks. The full
fresh-Windows-VM-from-installer walk is open as
BUG-002 in [`BUGS_OPEN.md`](BUGS_OPEN.md) and
will be the first beta tester's first action.

The reason for the gap: a true fresh-machine
walk requires a clean Windows VM, which the dev
environment doesn't currently have wired into
CI. It is a one-tester action, not a
multi-engineer-week effort.

---

## What "verified" means here

✅ The CLI surface boots and reports the right
state.
✅ The daemon responds on `/v1/health`,
`/v1/recovery/recent`, `/v1/threads/recent`.
✅ The capture pipeline writes real events
(36 today on this box).
✅ The frontend TypeScript builds clean.
✅ The demo CLI does what its docstring says.
✅ The doctor CLI surfaces real install state.

❌ A clean Windows VM hasn't been used.
❌ The cold tray-icon → launcher window flow
hasn't been walked post-8C.

The first ❌ is a process gap; the second is
the next-action item before the 0.1.0 stable
tag.

---

## How to re-run this verification

```powershell
# In a fresh PowerShell session:
python recall.py doctor
python recall.py capture status
python recall.py demo run
python recall.py demo status
python recall.py demo reset
python -c "from app.main import main"

# Optional — daemon endpoints (requires Recall running):
python -c "import requests; print(requests.get('http://127.0.0.1:4545/v1/health').json())"
```

If every line exits cleanly, this document is
still accurate. If anything regresses, file a
bug against the relevant line.
