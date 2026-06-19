# GO_NO_GO.md — the public-alpha gate

One question: **is Recall ready to hand to someone with no founder
in the room?**

The bar is not "the code works." It is the success condition of
Phase 5A.1: *you hand someone a laptop, they install Recall, it
works, and you are not there to help.* Until every gate below is
**GO**, the answer is **NO-GO** — and `0.2 public alpha` does not
ship.

This is a checklist, not a vibe. A gate flips to GO only with
evidence linked beside it.

---

## The gate

| # | Gate | Status | Evidence |
|---|---|---|---|
| 1 | **Install in under 3 minutes** | ⏳ PARTIAL | Phase 5G ran a silent install on the build machine: **66.0 s** wall (well under 3 min), exit 0, all artifacts created. The *clean-machine* leg (fresh Windows VM, 0-of-3 runs filled) is still NO-GO — see `CLEAN_MACHINE_RUN.md` |
| 2 | **Extension pairing works** | ⏳ PARTIAL | popup states verified; live pair with the daemon unrun — `EXTENSION_VALIDATION.md` |
| 3 | **First recovery works** | ⏳ PARTIAL | engine verified by smoke (§25); requires multi-day real activity — `alpha_report.md` Q3 awaiting cohort |
| 4 | **Resume works** | ⏳ PARTIAL | restore path smoke-tested (§26); end-to-end resume needs a real recovery card to act on — same blocker as gate 3 |
| 5 | **Docs complete** | ✅ GO | `INSTALL` / `DOWNLOADS` / `SUPPORTED_PLATFORMS` / `PUBLIC_ALPHA` / `MAC_VERIFICATION` / `MAC_OWNER_NEEDED` / `INSTALL_METRICS` plus the `alpha/` packet (`INSTALL` / `SAMPLE_WORKFLOW` / `TRUST` / `LIMITATIONS` / `FEEDBACK` / `alpha_report`) all landed by Phase 5G |
| 6 | **Screenshots are real** | ✅ GO | 15 of 15 surfaces captured: launcher (5) + recovery (2) + extension (6) + settings + **control-room** + **doctor-output** + **installer-flow** — see `assets/screenshots/README.md`. Only resume-in-progress moment remains, gated on a real install |
| 7 | **Installer verified** | ⏳ PARTIAL | Phase 5F: artifact built (`Recall-Setup.exe`, SHA-256 `7AFA5349…75FD975`, 260.8 MB). Phase 5G: silent install + launch + doctor + uninstall verified on the build machine. Code-signing still NO-GO (no EV cert) — SmartScreen warns on first run |

Legend: GO ✅ · PARTIAL ⏳ · NO-GO ⛔.

## Verdict

**NO-GO.** Phase 5G turned three gates from PARTIAL → richer
PARTIAL or GO: gate 6 (screenshots) is now GO with all 15
surfaces captured; gate 1 has its first real evidence (one ▲ row
on the build machine); gate 7 has end-to-end run-evidence on top
of the build artifact. The hard blockers now are:

- **Gate 1**: zero of three clean-VM runs in
  [`CLEAN_MACHINE_RUN.md`](../trust/CLEAN_MACHINE_RUN.md). Build
  machine ≠ clean machine.
- **Gate 7's second half**: installer is unsigned; SmartScreen
  blocks first-run.
- **Gates 3 + 4**: need a real cohort's recovery to verify; tracked
  in [`alpha_report.md`](../../alpha/alpha_report.md), currently
  *awaiting cohort data*.

## What turns this GO

In dependency order:

1. ~~Install Inno Setup~~ → done Phase 5F (winget).
2. ~~Run `build.ps1` → `Recall-Setup.exe`~~ → done Phase 5F.
3. ~~Run silent install on the build machine and prove the
   end-to-end loop (install → launch → daemon → doctor →
   uninstall) works~~ → done Phase 5G. See
   [`CLEAN_MACHINE_RUN.md`](../trust/CLEAN_MACHINE_RUN.md) Run 1 (▲).
4. **Three clean-machine runs.** Each on a different Windows VM
   that has never seen Recall, rows 1-11 of CLEAN_MACHINE_RUN.md
   walked. *Three* because one is anecdote and the directive's
   floor for gate 1 is *3 successful installs*.
5. **Code-sign the installer** with an EV certificate so
   SmartScreen stops warning. Closes Gate 7's second half.
6. **Alpha-001 enrolment.** Five testers receive the
   [`alpha/`](../../alpha) packet; first recoveries and trust
   reports land via [`alpha_report.md`](../../alpha/alpha_report.md).
   Closes Gates 3 + 4.
7. **macOS verification.** A maintainer with a Mac runs
   [`MAC_OWNER_NEEDED.md`](MAC_OWNER_NEEDED.md). Promotes macOS
   from Preview to Supported.

Only when all seven gates are ✅ does `0.2 public alpha` tag.

## Why a gate, not a launch date

A continuity tool earns trust on first contact or never. Shipping an
installer that SmartScreen-blocks, or a launcher that opens empty
with no explanation, spends that trust before the product gets a
word in. The gate exists so the first impression is never an
accident.

> Cross-referenced by [`PHASE_TRACKER.md`](../founder/PHASE_TRACKER.md) and
> [`PUBLIC_ALPHA.md`](../founder/PUBLIC_ALPHA.md).
