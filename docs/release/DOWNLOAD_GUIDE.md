# DOWNLOAD_GUIDE.md — the alpha download paths

The four artifacts Recall ships, what each one is for, and the
install steps for each. Sister doc to
[`docs/install-validation.mdx`](../../apps/docs/install-validation.mdx)
(the rigorous post-install validation) and
[`docs/trust/CLEAN_MACHINE_RUN.md`](../trust/CLEAN_MACHINE_RUN.md)
(the maintainer-run install matrix).

This guide is what a *real tester* reads on the marketing site's
`Download` section. If the website wording and this guide drift,
this guide wins — the marketing site is the front door, this
file is the on-disk source.

---

## The four artifacts

| Artifact | Platform | Size | Status | Best for |
|---|---|---:|---|---|
| **`Recall-Setup-lite.exe`** | Windows 10 / 11 | ≈ 216 MB | recommended | almost everyone |
| **`Recall-Setup-full.exe`** | Windows 10 / 11 | ≈ 261 MB | available | environments that forbid runtime dependency pruning |
| **`Recall.app` (preview)** | macOS Intel / Silicon | ≈ 220 MB | unsigned preview | maintainers + early Mac alpha |
| **Browser extension** | Chrome / Edge / Arc | — | bundled / sideload | every tester (pairs with either Windows or macOS) |

Every artifact lives on the
[GitHub releases page](https://github.com/kunalKumar-13/Recall-me/releases/latest).
The marketing site routes all four download buttons there so the
artifact source-of-truth is one place.

---

## Windows — Lite installer (default path)

The Phase 5J **lite** build is what almost every tester wants.

```
1. Download Recall-Setup-lite.exe from the releases page.
2. Double-click. Inno Setup runs; no admin prompt is required.
3. Wait ~30 seconds. The launcher icon appears in the system tray.
4. Press Ctrl + Space to open the launcher. The empty card shows
   "Recall notices unfinished work." with a Show example / Start
   normally button pair.
5. Install the browser extension — bundled inside the installer,
   or sideload from the unpacked folder per the README.
6. Browse normally. Within a few minutes, `~/.recall/events/`
   starts filling.
```

A SmartScreen warning will appear on first launch until the
signing-key path closes (gate 7 in the
[`PUBLIC_ALPHA.md`](../founder/PUBLIC_ALPHA.md) checklist).
Click *More info* → *Run anyway*. The installer is open source
and you can verify the binary against the GitHub releases SHA.

---

## Windows — Full installer

Identical product, larger bundle. The Phase 5J shrink trimmed
PyQt6 deps that the lite build's runtime hook prunes anyway;
the full build is the unmodified PyInstaller output for
environments that disallow the runtime hook.

Install steps are identical to the lite path above. Choose this
only if your environment specifically rejects the lite build.

---

## macOS — preview build

The Mac path is gated on a maintainer with the right hardware
running the
[`MAC_OWNER_NEEDED.md`](MAC_OWNER_NEEDED.md) verification script.
Until then the available macOS bundle is a **preview**:

- It is **unsigned**. Gatekeeper will refuse to open it on first
  launch.
- It is shipped as an **ad-hoc DMG**. Drag `Recall.app` to
  `/Applications`. Right-click → *Open* and confirm the
  Gatekeeper warning the first time.
- It runs the same engine as the Windows build. The on-disk
  layout under `~/.recall/` is identical.
- The `recall://` protocol handler is **not registered** on
  macOS until the maintainer pass lands. The extension's
  *Open Recall* button uses the loopback HTTP path instead.

Promotion from preview → supported happens when
[`MAC_VERIFICATION.md`](MAC_VERIFICATION.md) gains its first GO
row.

---

## Browser extension

The popup that lives next to the browser address bar — the same
one the
[`assets/screenshots/extension-v2/`](../../assets/screenshots/extension-v2)
captures show. Two paths to install:

### Path A — bundled (preferred)

The Windows installer **ships the extension folder inside
`Program Files\Recall\extension\`**. After the desktop install:

1. Open Chrome / Edge / Arc.
2. `chrome://extensions/` (or equivalent).
3. Enable *Developer mode* (top right).
4. *Load unpacked* → select `Program Files\Recall\extension\`.
5. The extension's popup opens green-dot connected. Done.

### Path B — sideload from the repo

If you cloned the repo instead of running the installer:

1. Open `chrome://extensions/`.
2. Enable *Developer mode*.
3. *Load unpacked* → `apps/extension/popup/` (the built output).
4. The popup's *Open Recall* button assumes a desktop daemon at
   `127.0.0.1:4545`; install the desktop build alongside or run
   `python recall.py` from the repo.

The extension's manifest only requests `127.0.0.1` host
permission. It cannot reach any other origin.

---

## First-run validation

After installing the desktop + extension, in this order:

1. Open the launcher (`Ctrl + Space`). The empty card should
   read *"Recall notices unfinished work."*.
2. Click *Show example*. The demo overlay appears with a
   trust banner + WebSocket recovery card + three
   investigation rows. This proves the engine is alive.
3. Click *Dismiss* on the demo banner. The empty card returns.
4. Browse a real site for 2 minutes. Reopen the launcher;
   the demo is gone and the digest now reads real events.
5. Run `recall doctor` from a terminal. Expected: 3+ GREEN
   rows, no REDs. The protocol / autostart YELLOWs are
   first-launch normal.

Steps 1-5 take ~5 minutes. If any of them fails, the
[`docs/troubleshooting.mdx`](../../apps/docs/troubleshooting.mdx)
page has the per-failure paths.

---

## Uninstall

Restated from
[`docs/product/TRUST.md`](../product/TRUST.md) so the download
guide carries the whole loop:

- **Windows**: Settings → Apps → Recall → *Uninstall*. The
  desktop binary goes; `~/.recall/` stays. Delete it manually
  for a full wipe.
- **macOS preview**: drag `Recall.app` to Trash. Same `~/.recall/`
  rule.
- **Extension**: from the browser's extension page, *Remove*.

Recall's data is *yours*. The uninstaller refuses to delete
`~/.recall/` so you don't lose work by accident.

---

## Related

- [`docs/release/RELEASE.md`](RELEASE.md) — release-channel
  discipline (stable / preview / nightly).
- [`docs/release/VERSIONING.md`](VERSIONING.md) — semver for
  the artifacts above.
- [`docs/install-validation.mdx`](../../apps/docs/install-validation.mdx)
  — the post-install validation checklist for the cohort.
- [`docs/trust/CLEAN_MACHINE_RUN.md`](../trust/CLEAN_MACHINE_RUN.md)
  — the maintainer's clean-VM install protocol that produces
  the install-matrix rows.
- [`PUBLIC_ALPHA.md`](../founder/PUBLIC_ALPHA.md) — the
  public-alpha readiness path.
