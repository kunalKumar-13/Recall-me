# archive/resume-old/

Removed in Phase 6P (Resume Reality). Kept here as a paper trail
of what the pre-6P resume path looked like + why it was deleted.

Nothing in active code paths imports from this directory.

---

## What lived here

### `live._on_restore` (one-line stub)

The pre-6P v3 launcher had this:

```python
def _on_restore(self, candidate_id, title, n_targets):
    try:
        self.api_client.recovery_restore(candidate_id)
    except Exception:
        log.warning("recovery_restore failed for %s", candidate_id)
        return
    log.info("v3 launcher restored %s (%d targets)", title, n_targets)
```

**Why removed.** It looked like restore but did nothing. It called
the API to resolve the plan, then *threw the plan away* and logged
a line. No `os.startfile`, no per-step open, no toast, no feedback.
The user clicked Resume and the launcher silently closed.

**Replacement.** [app/ui/launcher_v3/live.py](app/ui/launcher_v3/live.py)
`_on_preview_accept` walks `plan.steps` in order, opens each
target through `_open_target`, and announces the result via
`RestoreToast`.

### `live._on_demo_resume` (no-op handler)

```python
def _on_demo_resume(self, *_args):
    try:
        from app.core import demo_mode
        demo_mode.dismiss()
    except Exception:
        pass
```

**Why removed.** Replaced by the demo branch inside the unified
`_on_preview_accept` so the demo path runs the same preview →
toast cycle as the live path. One restore implementation, not
two.

### `RecoveryCardV3.restore → APIClient.recovery_restore` direct binding

The pre-6P card-to-engine binding was a single signal:

```python
card.restore.connect(self._on_restore)
```

**Why removed.** A click went straight from the card to the
network call without a preview step. Users had no way to inspect
what was about to happen, no way to cancel, and no feedback when
it failed silently.

**Replacement.** The card's `restore` signal now opens
`ResumePreview` (see [app/ui/launcher_v3/resume_preview.py](app/ui/launcher_v3/resume_preview.py)).
The preview's `accepted` signal triggers the actual restore.

---

## What still lives in active code

The legacy launcher (`app/ui/launcher_legacy.py`) still has its
own `_on_recovery_restore` + `_announce_restoration_result` —
those stay, because they're reachable via the
`RECALL_LAUNCHER=legacy` escape hatch and they actually opened
targets in the pre-6K path. Phase 6P intentionally does NOT
touch the legacy launcher's restore code.

---

## How the v3 path now reads

```
RecoveryCardV3.restore
  → LiveLauncher._open_preview (captures targets)
    → ResumePreview.open
      → ResumePreview.accepted
        → LiveLauncher._on_preview_accept
          → APIClient.recovery_restore
          → per-step _open_target
          → RestoreToast.flash_success / flash_failure
```

Every arrow does real work. None of them are stubs.
