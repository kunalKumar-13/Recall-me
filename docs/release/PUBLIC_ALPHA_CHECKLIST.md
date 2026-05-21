# PUBLIC_ALPHA_CHECKLIST.md — what must be true before tag

A pre-flight checklist for the **`0.2.0` public alpha** tag. Every
row needs evidence in the *Status* column. This file is the
"are we ready?" view; the gate that turns into release is
[`GO_NO_GO.md`](GO_NO_GO.md).

A check is only green if it was *run*, not if it *should* work.

---

## The kit

| # | Artefact / proof | Status | Where the evidence lives |
|---|---|---|---|
| 1 | **Installer — `Recall-Setup.exe`** | ⛔ NO | needs Inno Setup on a build machine; PyInstaller stage proven (`INSTALL_VALIDATION_WINDOWS.md` § stage 1) |
| 2 | **Clean-machine install ≤ 3 min** | ⛔ unrun | `INSTALL_VALIDATION_WINDOWS.md` § checklist rows 1-13 |
| 3 | **Screenshots — launcher** | ✅ real | `assets/screenshots/launcher-*.png` (Phase 4L, deterministic) |
| 4 | **Screenshots — recovery card** | ✅ real | `assets/screenshots/recovery-card*.png` (Phase 4L) |
| 5 | **Screenshots — extension** | ✅ real | `assets/screenshots/extension-*.png` (Phase 5A.1, six states + Phase 5C onboarding empty) |
| 6 | **Screenshots — settings dialog** | ⚠️ partial | `capture_settings.py` pending (needs `Config` fixture) |
| 7 | **Screenshots — resume moment** | ⛔ unrun | needs a live restoration on a populated install |
| 8 | **Docs — install + downloads + supported** | ✅ done | `INSTALL.md`, `DOWNLOADS.md`, `SUPPORTED_PLATFORMS.md` |
| 9 | **Docs — first-week + trust + limits** | ✅ done | `FIRST_WEEK.md`, `TRUST_MOMENTS.md`, `TRUST_LEDGER.md`, `KNOWN_LIMITATIONS.md` |
| 10 | **Recovery verified on real install** | ⛔ unrun | engine smoke ✅ (§ 25-29); end-to-end on fresh install pending |
| 11 | **Extension paired with daemon, live** | ⛔ unrun | popup states ✅ (`EXTENSION_VALIDATION.md`); live transition needs Chrome + daemon together |
| 12 | **`recall doctor` runs clean** | ✅ verified | Phase 5C — runs against real `~/.recall/` |
| 13 | **`recall stats` + export round-trip** | ✅ verified | end-to-end import / merge / cohort summary tested (Phase 5E.1) |
| 14 | **macOS status — honestly stated** | ✅ done | `MAC_BUILD_STATUS.md` (Preview, not pretended Supported) |
| 15 | **Known issues — honestly listed** | ✅ done | `KNOWN_LIMITATIONS.md` |
| 16 | **Release notes drafted** | ✅ done | `releases/RELEASE_NOTES_v0.2.0.md` |
| 17 | **Checksums tool runs** | ✅ verified | `releases/make_checksums.py` (Phase 5A.1) |
| 18 | **Cohort alpha-001 enrolled** | ⛔ NO | gated on rows 1–2 — invites go out once a signed installer exists |

Legend: ✅ done · ⚠️ partial · ⛔ blocker.

## Current state

Most of the kit is **green**. The two **red** rows are the same
ones in [`GO_NO_GO.md`](GO_NO_GO.md): a verified installer (rows 1
+ 2) and the cohort opening (row 18). They are not independent —
row 18 is gated on rows 1-2.

The path between here and `0.2.0`:

1. Install Inno Setup on the Windows build machine.
2. Run `pwsh infra/packaging/windows/build.ps1` → real `Recall-Setup.exe`.
3. Stage it into `releases/windows/`; `python releases/make_checksums.py`.
4. Walk every row of `INSTALL_VALIDATION_WINDOWS.md` § checklist on
   a clean Windows VM, timed.
5. Capture rows 6, 7 (settings + resume) from that same fresh install.
6. Send `Recall-Setup.exe` to alpha-001.

After step 6, the success criterion is the one from `FIRST_WEEK.md`:
the cohort member, with no founder in the room, installs, uses it
for three days, gets a recovery, and keeps Recall.

## What this checklist is *not*

It is not the *roadmap* (see [`ROADMAP_LIVE.md`](../founder/ROADMAP_LIVE.md))
and not the *phase tracker* (see [`PHASE_TRACKER.md`](../founder/PHASE_TRACKER.md)).
It is one focused list: the minimum proof that the first stranger
to install Recall will not be left holding a broken thing.
