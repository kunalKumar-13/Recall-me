# Phase 6P — Resume Reality

**Status:** complete  
**Directive:** Click Resume. Actually continue work.  
**Scope:** restore flow only. No UI redesign, no launcher
geometry changes, no control room work.

---

## What shipped

### Real OS opens behind the Resume button

The v3 launcher's `_on_restore` was a one-line stub that called
the API to resolve a `RestorationPlan` and then dropped the plan
on the floor. The user clicked Resume and the launcher silently
closed.

The new pipeline:

```
RecoveryCardV3.restore
  → LiveLauncher._open_preview     (captures targets, opens overlay)
    → ResumePreview.accepted
      → LiveLauncher._on_preview_accept
        → APIClient.recovery_restore   (resolves plan)
        → per-step _open_target        (files first, then chats, tabs, searches)
        → RestoreToast.flash_success   (3 names, 3 s, then launcher.hide)
```

Each arrow is a real call. The plan order
(`RecoveryEngine.plan_for` in [app/core/recovery.py:754](../../docs/engineering/app/core/recovery.py#L754))
is preserved: files → chats → tabs → searches.

### Preview overlay

[app/ui/launcher_v3/resume_preview.py](../../docs/engineering/app/ui/launcher_v3/resume_preview.py)
— a light overlay that floats on top of the digest. Shows the
title + a count breakdown (`2 files · 2 tabs · 1 search`) and
two buttons (Cancel / Resume now).

No modal darkening, no separate window. Esc/Cancel closes
without firing any OS open.

### Restore-feedback toast

[app/ui/launcher_v3/restore_toast.py](../../docs/engineering/app/ui/launcher_v3/restore_toast.py)
— a small pill that pins to the bottom of the launcher for 3
seconds:

- Success: `Restored · backoff.py · client.py · MDN`
- Partial: `Restored 3 of 5 · backoff.py · client.py · MDN · 2 missing`
- Failure: `Could not reopen 1 item · Continue anyway`
- No engine: `Could not reach the engine · try again`

### Failure handling

Best-effort: a missing file or a failed `os.startfile` is
counted as `skipped` and the remaining steps still run. The
launcher never crashes, never raises, never modals.

| Failure                          | Result                                  |
|----------------------------------|-----------------------------------------|
| API returns `None`               | toast *Could not reach the engine*      |
| Plan has no steps                | toast *Nothing to restore*              |
| File path missing                | skip + count; continue                  |
| `os.startfile` raises            | skip + count; continue                  |
| All steps fail                   | toast *Could not reopen N items · Continue anyway* |

### Documentation

| File                                                   | Role                                      |
|--------------------------------------------------------|-------------------------------------------|
| [docs/product/RESUME_FLOW.md](../../docs/product/RESUME_FLOW.md) | End-to-end pipeline + order rationale     |
| [docs/product/SHOWCASE_RUN.md](../../docs/product/SHOWCASE_RUN.md) | Demo verification + failure injection     |
| [archive/resume-old/README.md](../resume-old/README.md) | What was deleted + why                    |

---

## Files touched

- [app/ui/launcher_v3/resume_preview.py](../../app/ui/launcher_v3/resume_preview.py) — new
- [app/ui/launcher_v3/restore_toast.py](../../app/ui/launcher_v3/restore_toast.py) — new
- [app/ui/launcher_v3/live.py](../../app/ui/launcher_v3/live.py) — rewrote restore path
- [app/ui/launcher_v3/__init__.py](../../app/ui/launcher_v3/__init__.py) — exports
- [docs/product/RESUME_FLOW.md](../../docs/product/RESUME_FLOW.md) — new
- [docs/product/SHOWCASE_RUN.md](../../docs/product/SHOWCASE_RUN.md) — new
- [archive/resume-old/README.md](../resume-old/README.md) — new

---

## Verification matrix

| Check                                          | Result   |
|------------------------------------------------|----------|
| `python -m pyflakes app/ui/launcher_v3`        | clean    |
| `import app.ui.launcher_v3 as v3`              | 22 exports |
| `_classify_counts` returns correct buckets     | yes      |
| `_name_for` shortens paths + URLs              | yes      |
| Preview overlay paints + dismisses cleanly     | yes      |
| Toast respects 3-name cap                      | yes      |
| Plan order: files → chats → tabs → searches    | yes (engine) |
| `RECALL_EXPLAIN_RECOVERY=1` prints skip list   | yes      |

---

## Success criterion

> Resume feels real.

Two halves both pass:

1. **Click Resume.** The card emits `restore`; the preview
   opens with the actual target counts the engine would open.
2. **Actually continue work.** Click *Resume now* and 5 OS opens
   happen in the documented order, then the launcher hides and
   the user is in their editor with the files open.

Pre-6P, only half-1 happened. Half-2 was silent.
