# Resume Flow — Phase 6P

The end-to-end audit of what happens between *user clicks Resume*
and *the work is open in front of them*. This is the document
the next engineer reads before changing anything in the recovery
or restore path.

> Resume is the most load-bearing surface in Recall. Everything
> upstream — events, sessions, contexts, threads, evolution,
> recovery — exists so this one action actually returns the user
> to work.

---

## The pipeline

```
launcher hero
   │  (1) RecoveryCardV3.restore signal — (cid, title, n)
   ▼
LiveLauncher._on_restore
   │  (2) ResumePreview.open() — small overlay sheet
   ▼
preview "Resume now" button
   │  (3) POST /v1/recovery/{cid}/restore
   ▼
RecoveryEngine.candidate_for_thread + plan_for
   │  (4) RestorationPlan(steps=[files, chats, tabs, searches])
   ▼
LiveLauncher._execute_plan
   │  (5) per-step OS open + per-file log_open
   ▼
RestorationResult + RestoreToast
   │  (6) "Restored 4 · backoff.py · client.py · MDN" (3 s)
   ▼
launcher.hide()
```

Each arrow is a real function call. None of them are abstractions
for future use.

---

## Source: which surface fires the signal

| Surface                | Signal                              | Carrier                  |
|------------------------|-------------------------------------|--------------------------|
| `RecoveryCardV3`       | `restore(cid, title, n_targets)`    | mouse, `Enter`/`Space`/`1` |
| `MinimalEmpty`         | — (no restore — empty surface)      | n/a                      |
| Legacy `RecoveryCard`  | `restore_requested(cid, title, n)`  | mouse, `Enter`           |

The v3 path is the default after Phase 6K. The legacy path
exists only via `RECALL_LAUNCHER=legacy`.

---

## Decision: preview before restore

Phase 6P inserts one small sheet between the click and the OS
opens. The user sees:

```
Continue
    WebSocket retry debugging

Will reopen
    · 2 tabs        (browser)
    · 2 files       (editor)
    · 1 search      (browser)

    [ Cancel ]     [ Resume now ]
```

The preview is **light overlay only** — no full dialog, no modal
darkening, no separate window. It paints on top of the digest
inside the same launcher window.

Why a preview at all? Three reasons:

1. **Trust.** The user sees exactly what's about to happen. No
   surprise tabs.
2. **Undo without commit.** Canceling the preview is a no-op —
   no events logged, no OS calls made.
3. **Specificity.** "2 tabs · 2 files · 1 search" is concrete
   evidence the user can verify against memory before they
   accept the action.

The preview content is **derived from the candidate's
`suggested_targets` + `_classify_targets`** — the exact same
buckets the restore plan uses. There is no second source of
truth.

---

## Restore: the order is fixed

The plan walks groups in this order, every time:

```
files     →  ground the work in local artifacts
chats     →  bring back the conversation that informed it
tabs      →  re-anchor reading material
searches  →  re-run the queries the user kept chasing
```

This is `RecoveryEngine.plan_for` in [app/core/recovery.py](app/core/recovery.py#L754).
The order is deterministic — same candidate in, same plan out.

### Why files first

Files are *where the user works*. Opening the editor's file
first gives the user a stable anchor: "I'm in `backoff.py`
again." Reopening browser tabs first would land the user
inside a browser window staring at MDN with no reminder
that this is the *WebSocket retry* investigation.

### Why chats second

Chats encode the *thinking* that informed the work. A user
who returns to a tab without the chat that justified opening
it ends up re-deriving context. Opening the chat after the
file means the user reads the conversation already grounded
in the code it referenced.

### Why tabs third

Tabs are reference material. They support the work; they
aren't the work.

### Why searches last

Searches are the *cheapest* to re-run. They go last because
the user often abandons a restoration mid-sequence ("oh
right, I remember now") — putting searches at the tail
means an abandoned restore still landed the user on files +
chats + tabs.

### Within a group: newest first

The pool of targets the engine surfaces is already
newest-first (see `_suggested_targets`). The plan preserves
that order — the most recent file is the first file opened,
which is almost always the file the user was actively
editing.

---

## Feedback: the toast

After the plan executes, a single 3-second toast appears
at the bottom of the launcher:

```
Restored · backoff.py · client.py · MDN
```

It shows up to **three target names** (filenames or shortened
hosts) so the user gets specific evidence. Nothing else — no
spinner, no progress bar, no checkmarks.

If `restored < requested`, the toast extends:

```
Restored 3 of 4 · backoff.py · client.py · MDN · 1 missing
```

The toast is purely presentational. Nothing leaves the machine.

---

## Failure path

The restore is **best-effort**. One bad target never blocks the
rest.

| Failure                          | What we do                          |
|----------------------------------|-------------------------------------|
| API returns `None` (daemon down) | Toast `Could not reach the engine`; restore is a no-op |
| Plan has no steps                | Toast `Nothing to restore`; close the preview |
| File path doesn't exist          | Skip + count as `missing`; continue |
| `os.startfile` raises            | Skip + count as `error`; continue   |
| All steps fail                   | Toast `Could not reopen any of 4 items · Continue anyway` |

The user is never blocked. The launcher never crashes. A
missing file becomes a one-line toast, not a modal.

When `RECALL_EXPLAIN_RECOVERY=1` is set, the skip list is
printed to the console (the developer-facing path); the user
never sees a traceback.

---

## What's not in the pipeline

- **No telemetry.** Nothing about the restore leaves the machine.
- **No queueing.** The restore runs synchronously on the Qt main
  thread; the longest path (4-5 `os.startfile` calls) is ~50 ms.
- **No retries.** If a file is missing it stays missing.
- **No undo.** Once the OS opens a tab, the launcher has no way
  to walk it back. (The preview *is* the undo.)
- **No background restoration.** Resume is foreground. The user
  is watching.

---

## Files

| File                                                | Role                                |
|-----------------------------------------------------|-------------------------------------|
| [app/core/recovery.py](app/core/recovery.py)        | Engine — scores + plan ordering     |
| [api/services/recovery.py](api/services/recovery.py)| HTTP — surfaces `recover_recent` + `restore` |
| [app/core/api_client.py](app/core/api_client.py)    | Client — `recovery_restore(cid)`    |
| [app/ui/launcher_v3/live.py](app/ui/launcher_v3/live.py) | UI — wires the click through |
| [app/ui/launcher_v3/recovery_panel.py](app/ui/launcher_v3/recovery_panel.py) | Card — emits the `restore` signal |
| [app/ui/launcher_v3/resume_preview.py](app/ui/launcher_v3/resume_preview.py) | Phase 6P — preview overlay |
| [app/ui/launcher_v3/restore_toast.py](app/ui/launcher_v3/restore_toast.py)   | Phase 6P — toast feedback  |

---

## Success criterion

> Click Resume. Actually continue work.

Two halves. Both must be true.
