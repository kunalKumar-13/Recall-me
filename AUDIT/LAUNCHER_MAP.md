# Launcher Forensics — Phase 8A

The complete wiring map for the launcher. Every signal,
every slot, every public method that crosses a class
boundary. This is the document a future contributor reads
**before** they touch any file under `app/ui/launcher_v3/`.

> Goal: **one launcher only**. The v3 path is the
> launcher; the legacy path is the escape hatch.

---

## Class graph

```
                          app/main.py
                              │
                              ▼ instantiates
                      ┌───────────────────┐
                      │   Launcher        │  (adapter)
                      │   app/ui/launcher.py
                      └───────────────────┘
                              │ RECALL_LAUNCHER == "legacy" ?
                ┌─────────────┴─────────────┐
                ▼ no                         ▼ yes
       ┌───────────────────┐         ┌───────────────────┐
       │  LiveLauncher     │         │  Launcher         │
       │  app/ui/launcher_v3/live.py  │  app/ui/launcher_legacy.py
       └───────────────────┘         └───────────────────┘
                │ owns
                ├─► MinimalSearchBar      (minimal.py)
                ├─► MinimalDigest         (minimal.py)
                │     ├─► RecoveryCardV3  (recovery_panel.py)
                │     ├─► RecentMemoryList (recent_memory.py)
                │     └─► InvestigationList (investigation_panel.py)
                ├─► MinimalEmpty          (minimal.py — stubbed in 7E)
                ├─► MinimalShell          (minimal.py)
                ├─► MinimalWindow         (parent shell)
                ├─► ResumePreview         (resume_preview.py)
                ├─► RestoreToast          (restore_toast.py)
                └─► TrustRow              (minimal.py)
```

---

## `LiveLauncher` — public surface

Defined at [`app/ui/launcher_v3/live.py`](../app/ui/launcher_v3/live.py).

### Signals (emitted up to the host)

| Signal              | Args | Wiring                                             | Status      |
|---------------------|------|----------------------------------------------------|-------------|
| `request_settings`  | —    | forwarded from `self._search.request_settings`     | **stable** (frozen 7E.1) |
| `_request_search`   | `str`| emitted by `_on_query_changed` (which is connected to `self._search.query_changed`) | **stable** (frozen 7E.1) — leading underscore is historical; host treats it as public |

### Methods (called by the host)

| Method                  | Purpose                                          | Status      |
|-------------------------|--------------------------------------------------|-------------|
| `show_centered()`       | Show launcher centred on the active screen       | **stable**  |
| `invalidate_digest()`   | Drop cached digest; next refresh re-fetches      | **stable**  |
| `_refresh_idle_state()` | Recompute empty/digest/demo                      | **stable** (the underscore is historical) |
| `hide()`                | Standard Qt; also fired by `request_close`       | **stable**  |

### Internal slots

| Slot                    | Source signal                                    | Status      |
|-------------------------|--------------------------------------------------|-------------|
| `_on_query_changed`     | `MinimalSearchBar.query_changed`                 | **stable**  |
| `_on_show_example`      | `MinimalEmpty.show_example`                      | **legacy** (empty stubbed in 7E; signal will never fire) |
| `_on_start_normally`    | `MinimalEmpty.start_normally`                    | **legacy** (same) |
| `_on_preview_accept`    | `ResumePreview.accepted`                         | **stable**  |
| `_on_preview_cancel`    | `ResumePreview.cancelled`                        | **stable**  |
| `_on_escape`            | `Esc` QShortcut                                  | **stable**  |
| `_activate_card`        | `1` QShortcut                                    | **stable**  |
| `_open_preview` (closure) | wired per-hero via `_wire_hero_restore` to `RecoveryCardV3.restore` | **stable** |

### State sources

| Field                   | Updated by                                       | Type                              |
|-------------------------|--------------------------------------------------|-----------------------------------|
| `search_engine`         | constructor                                      | `SearchEngine` (or `DemoSearchEngine`) |
| `event_logger`          | constructor                                      | `EventLogger` (or `None`)         |
| `api_client`            | constructor (lazy import)                        | `APIClient` (loopback HTTP)       |
| `_pending_targets`      | `_open_preview` → `_on_preview_accept`           | `List[Tuple[str, str]]`           |
| `_pending_title`        | same                                             | `str`                             |
| `_pending_cid`          | same                                             | `str`                             |
| `_pending_demo`         | same                                             | `bool`                            |

### Keyboard layer (frozen 7E.1)

| Key              | Effect                                                       |
|------------------|--------------------------------------------------------------|
| `Esc`            | Closes the preview overlay if open; otherwise hides launcher |
| `Ctrl+K` / `⌘K`  | Focuses + selects-all the search input                       |
| `1`              | Resumes the visible Continue document                        |

The 2-9 hotkeys from 6R/7B are gone — single-focus surface.

---

## `MinimalSearchBar` — frozen contract (7E.1)

Defined at [`app/ui/launcher_v3/minimal.py`](../app/ui/launcher_v3/minimal.py).
The full contract lives in
[`docs/product/LAUNCHER_CONTRACTS.md`](../docs/product/LAUNCHER_CONTRACTS.md);
mirrored here for completeness.

### Signals

| Signal              | Args | Fires when                                           | Status      |
|---------------------|------|------------------------------------------------------|-------------|
| `query_changed`     | `str`| every `QLineEdit.textChanged`                        | **stable**  |
| `searchChanged`     | `str`| same source — contract alias                         | **stable**  |
| `submit`            | `str`| Return / Enter inside the input                      | **stable**  |
| `request_settings`  | —    | (declared; no widget in 7E fires it)                 | **stable** (declared for forward-compat) |
| `request_close`     | —    | (declared; no widget in 7E fires it)                 | **stable** (declared for forward-compat) |

### Methods

| Method      | Purpose                                                |
|-------------|--------------------------------------------------------|
| `focus()`   | Move keyboard focus to the input                        |
| `clear()`   | Empty the input                                         |
| `selectAll()` | Select the input's full text                          |

### Stable attributes

| Attribute        | Value | Why it matters                                     |
|------------------|-------|----------------------------------------------------|
| `HEIGHT`         | `52`  | Read by capture scripts + the inner-card layout    |
| `RADIUS`         | `14`  | Same                                               |

---

## `RecoveryCardV3` — hero contract

Defined at [`app/ui/launcher_v3/recovery_panel.py`](../app/ui/launcher_v3/recovery_panel.py).

### Signals

| Signal      | Args                  | Fires when                                |
|-------------|-----------------------|-------------------------------------------|
| `restore`   | `(str, str, int)`     | Enter / Space / `1` / mouse-release        |

### Constructor

```python
RecoveryCardV3(
    candidate_id: str,
    title: str,
    *,
    targets: Optional[List[Tuple[str, str]]] = None,
    extra_clause: Optional[str] = None,
    signal: Signal = "high",          # "high" | "med" | "low"
    n_targets: int = 0,
    parent: Optional[QWidget] = None,
)
```

### Stable attributes

| Attribute        | Value | Why it matters                                     |
|------------------|-------|----------------------------------------------------|
| `HEIGHT`         | `110` | Hero row geometry                                   |
| `ACCENT_STRIP_W` | `6`   | Lavender left rail                                  |
| `Signal`         | Literal["high", "med", "low"] | exported as a type alias     |

---

## `InvestigationCardV3` + `InvestigationList`

Defined at [`app/ui/launcher_v3/investigation_panel.py`](../app/ui/launcher_v3/investigation_panel.py).

### Signals

| Class              | Signal           | Args                  | Notes                                |
|--------------------|------------------|-----------------------|--------------------------------------|
| `InvestigationCardV3` | `open_thread`  | `(str, str, str)`     | thread_id, topic_key, title         |
| `InvestigationList` | `activated`     | `(str, str, str)`     | forwarded from any row's `open_thread` |

### Constructor

```python
InvestigationCardV3(
    thread_id: str,
    topic_key: str,
    title: str,
    *,
    last_seen: str = "",
    strong: bool = False,
)
```

### Stable attributes

| Attribute      | Value | Why it matters                              |
|----------------|-------|---------------------------------------------|
| `HEIGHT`       | `36`  | Compact OTHER WORK row                       |
| `MAX_VISIBLE`  | `3`   | List cap                                     |
| `InvestigationRow` | `= InvestigationList` | back-compat alias the live launcher's keyboard layer reads (`row._titles`) |

---

## `RecentMemoryList` + `MemoryRow`

Defined at [`app/ui/launcher_v3/recent_memory.py`](../app/ui/launcher_v3/recent_memory.py).

### Public types

```python
@dataclass(frozen=True)
class MemoryRow:
    time: str       # HH:MM
    source: str     # short bold platform/host label
    label: str      # event title
```

### Methods

| Method                    | Purpose                              |
|---------------------------|--------------------------------------|
| `populate(items: List[MemoryRow])` | Replaces the rendered rows |

### Stable attributes

| Attribute      | Value | Why it matters         |
|----------------|-------|------------------------|
| `MAX_VISIBLE`  | `5`   | List cap                |

---

## `ResumePreview` + `RestoreToast` (Phase 6P)

Defined at [`app/ui/launcher_v3/resume_preview.py`](../app/ui/launcher_v3/resume_preview.py)
and [`app/ui/launcher_v3/restore_toast.py`](../app/ui/launcher_v3/restore_toast.py).

| Class            | Signals                                      | Methods                                   |
|------------------|----------------------------------------------|-------------------------------------------|
| `ResumePreview`  | `accepted(str, str)`, `cancelled()`         | `open(cid, title, targets)`, `close_preview()` |
| `RestoreToast`   | (no signals — fire-and-forget)               | `flash_success(names, *, requested, missing)`, `flash_failure(missing)`, `flash_no_engine()` |

---

## `TrustRow`

Defined at [`app/ui/launcher_v3/minimal.py`](../app/ui/launcher_v3/minimal.py).

| Method                                     | Purpose                                    |
|--------------------------------------------|--------------------------------------------|
| `set_counts(events_today, investigations)` | Update the two live-count pills (indexes 2 + 3) |

`LiveLauncher._populate_digest` calls this after every
refresh with values from `_load_trust_counts()` (which
reads `EventStore.iter_events_for_date(today)` +
`~/.recall/threads.json` length).

---

## `MinimalWindow` — top-level

Defined at [`app/ui/launcher_v3/minimal.py`](../app/ui/launcher_v3/minimal.py).

| Attribute        | Value     | Notes                                  |
|------------------|-----------|----------------------------------------|
| `DEFAULT_SIZE`   | `(700, 500)` | Frozen 7E                            |
| `OUTER_MARGIN`   | `12`      | Gutter between window edge + inner card |
| `ROOT_RADIUS`    | `24`      | Inner card radius                      |
| `shell` (property) | `MinimalShell` | Live-launcher reads `.trust` off this to update the trust row |

---

## Wiring map — every `.connect(...)` in `LiveLauncher.__init__`

| Line | Connection                                                                       |
|------|----------------------------------------------------------------------------------|
| 296  | `self._search.query_changed.connect(self._on_query_changed)`                     |
| 302  | `self._search.request_settings.connect(self.request_settings.emit)` (frozen 7E.1) |
| 303  | `self._search.request_close.connect(self.hide)` (frozen 7E.1)                    |
| 307  | `self._empty.show_example.connect(self._on_show_example)`                        |
| 308  | `self._empty.start_normally.connect(self._on_start_normally)`                    |
| 327  | `self._preview.accepted.connect(self._on_preview_accept)`                        |
| 328  | `self._preview.cancelled.connect(self._on_preview_cancel)`                       |
| 573  | (closure) `card.restore.connect(_open_preview)` — wired per-hero in `_wire_hero_restore` |

Plus 3 QShortcuts: `Esc` / `Ctrl+K` / `Meta+K` / `1`.

---

## State-flow per refresh

```
LiveLauncher._refresh_idle_state()
  │
  ├── self.search_engine.store.count() == 0 ?
  │     ├── yes + no demo_mode.is_active() → self._show_empty()  (center stack index 0)
  │     └── otherwise → self._populate_digest()
  │
  └── self._populate_digest()
        │
        ├── demo_mode.is_active() ? → self._populate_demo()
        │     └── synthesises hero + memory_rows + inv_cards from demo_mode.demo_payload()
        │
        ├── api_client.recovery_recent(n=1) → recoveries
        ├── api_client.threads_recent(n=3)  → threads
        ├── _load_recent_memory(max_rows=5)  → memory_rows
        ├── _load_trust_counts()              → (events_today, investigations)
        │
        ├── if HIGH + not ledger-flagged → hero = _recovery_to_v3(c)
        │
        ├── self._digest.populate(hero=hero, memory=memory_rows, investigations=inv_cards)
        ├── self._shell_widget.trust.set_counts(events_today, investigations)
        └── self._show_digest()  (center stack index 1)
```

---

## Anti-rules (frozen)

These are what *must not change* without superseding
`LAUNCHER_CONTRACTS.md`:

1. **`MinimalSearchBar`'s 5 signals + 3 methods.** Adding
   is fine; removing breaks the host.
2. **`LiveLauncher.request_settings` + `_request_search`
   signals.** Same rule.
3. **`LiveLauncher(search_engine, event_logger=None,
   parent=None)` constructor.** `app/main.py` constructs
   the launcher this way; the positional order is part
   of the contract.
4. **`RecoveryCardV3.restore(str, str, int)` signature.**
   Closure-bound to the preview-open path.
5. **`InvestigationList._titles` property.** The live
   launcher's keyboard layer reads it.
6. **The `Esc / Ctrl+K / Meta+K / 1` hotkey set.**
   Users + docs depend on them.

The freeze rule from
[`LAUNCHER_CONTRACTS.md`](../docs/product/LAUNCHER_CONTRACTS.md)
applies: *future launcher phases may **add** to the
surface; they **must not remove or rename** the symbols
above*.

---

## Goal — one launcher

Today: **two**.

- `app/ui/launcher_v3/` is the live path (default).
- `app/ui/launcher_legacy.py` is the env-var escape hatch.

To collapse to one launcher would require:

1. Confirm nothing in the alpha / installer / smoke-test
   path depends on the legacy launcher.
2. Run `_smoke_api.py` + `recall.py doctor` with the v3
   path forced.
3. Remove `RECALL_LAUNCHER=legacy` handling from
   `app/ui/launcher.py`.
4. Delete `app/ui/launcher_legacy.py` and the 7 LEGACY
   files in `app/ui/` (`cards.py`, `widgets.py`,
   `styles.py`, `launcher_anims.py`, `launcher_digest.py`,
   `demo_data.py`, `ceremonies.py`).

That is **not** done in 8A — this audit is
classification, not deletion.
