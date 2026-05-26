# Launcher Contracts — Phase 7E.1

The launcher's **frozen Python interface**. Every symbol
listed below is consumed by code outside `app/ui/launcher_v3/`
— removing or renaming any of them silently breaks
`python recall.py`.

> No future launcher phase may remove a public signal or
> rename a public method on these classes. Phases may **add**
> to the surface; they may not subtract.

This document was written after the **Phase 7E regression**:
the 7E rewrite of `MinimalSearchBar` dropped
`request_settings` while `LiveLauncher.__init__` still
called `self._search.request_settings.connect(...)`. The
launcher crashed with `AttributeError` on every boot. 7E.1
restores the contract and freezes it.

---

## How regressions like this happen

A pure-paint rewrite changes the visible surface but does
not change the *interface*. The launcher's host
(`app/main.py`, the tray, the global hotkey) speaks to the
launcher through a small set of signals + methods that
have nothing to do with paint. When the paint rewrite
drops a widget that was emitting one of those signals, the
*declaration* of the signal often goes with it — and the
host's `connect(...)` line breaks at construction.

The fix: **the contract is a separate concern from the
paint**. Signals + methods on the contract surface should
be declared even when no widget currently fires them.
Adding a paint affordance later wires up an existing
contract symbol; removing a paint affordance does not
require removing the contract symbol.

---

## Frozen contracts

### `MinimalSearchBar`

Lives in
[`app/ui/launcher_v3/minimal.py`](../../app/ui/launcher_v3/minimal.py).

#### Signals (all `pyqtSignal`)

| Name                  | Args  | Fires when                                               |
|-----------------------|-------|----------------------------------------------------------|
| `query_changed`       | `str` | every `QLineEdit.textChanged`                            |
| `searchChanged`       | `str` | every `QLineEdit.textChanged` (alias of `query_changed`) |
| `submit`              | `str` | `Return` / `Enter` pressed inside the input              |
| `request_settings`    | —     | a settings affordance is activated (may not exist in current paint) |
| `request_close`       | —     | a close affordance is activated (may not exist in current paint) |

The two *may-not-exist* signals are declared even when no
widget currently fires them. Consumers (`LiveLauncher`,
`app/main.py`) `connect(...)` to them regardless; the
launcher must boot whether or not the affordance is on
screen.

#### Methods

| Name          | Purpose                                            |
|---------------|----------------------------------------------------|
| `focus()`     | Move keyboard focus to the input.                  |
| `clear()`     | Empty the input.                                   |
| `selectAll()` | Select the input's full text.                      |

#### Stable attributes

`MinimalSearchBar.HEIGHT` and `MinimalSearchBar.RADIUS` are
read by capture scripts; treat them as part of the contract.

---

### `LiveLauncher`

Lives in
[`app/ui/launcher_v3/live.py`](../../app/ui/launcher_v3/live.py).

#### Constructor

```python
LiveLauncher(
    search_engine,
    event_logger: Optional[EventLogger] = None,
    parent: Optional[QWidget] = None,
)
```

The first two positional arguments are how `app/main.py`
constructs the launcher; they must remain.

#### Public signals

| Name              | Args  | Forwarded from                              |
|-------------------|-------|---------------------------------------------|
| `request_settings`| —     | `self._search.request_settings`             |
| `_request_search` | `str` | derived from `self._search.query_changed`   |

`_request_search` is named with a leading underscore for
historical reasons (the legacy launcher uses the same
name); `app/main.py` consumes it as part of the public
contract and the underscore stays for back-compat.

#### Methods

| Name                    | Purpose                                                     |
|-------------------------|-------------------------------------------------------------|
| `show_centered()`       | Show the launcher centred on the active screen.             |
| `invalidate_digest()`   | Drop any cached digest so the next refresh re-fetches.      |
| `_refresh_idle_state()` | Recompute the idle surface (empty vs digest vs demo).       |
| `hide()`                | Standard Qt — used by Esc and `request_close` propagation.  |

#### Keyboard shortcuts (frozen)

| Key              | Effect                                                   |
|------------------|----------------------------------------------------------|
| `Esc`            | Closes the resume preview if open; otherwise hides.       |
| `Ctrl+K` / `⌘K`  | Focuses + selects-all on the search input.                |
| `1`              | Resumes the visible Continue document (if any).           |

The 2-9 hotkeys from 6R/7B are gone — single-focus surface,
nothing to navigate.

---

## Wiring map

What `app/main.py` (and the host harness) speaks to:

```
        +----------------------------+
        |  app/main.py / tray / kbd  |
        +----------------------------+
                     │
                     ▼
        +----------------------------+
        |  LiveLauncher              |  ← .show_centered()
        |    .request_settings ────► |     listens for Settings open
        |    ._request_search ────►  |     listens for inline-search requests
        |    .hide()                 |     standard Qt
        +----------------------------+
                     │ owns
                     ▼
        +----------------------------+
        |  MinimalSearchBar          |
        |    .query_changed     ───► |  LiveLauncher._on_query_changed
        |    .searchChanged     ───► |  same source — alias signal
        |    .submit            ───► |  reserved (no consumer yet)
        |    .request_settings  ───► |  LiveLauncher.request_settings.emit
        |    .request_close     ───► |  LiveLauncher.hide
        |    .focus / clear /        |
        |     selectAll              |
        +----------------------------+
```

Any future paint rewrite must keep this map valid.

---

## Verification

The launcher boots cleanly:

```
$ python recall.py
[boot] [SLOW] initialize VectorStore (1898ms)
…  recall.api.app api.service.start
```

And the doctor reports the engine surfaces are alive:

```
$ python recall.py doctor
  GREEN   config       2 folder(s) indexed
  GREEN   events       4 day-file(s) on disk
  GREEN   event flow   events in the last 24h
  …
```

The Phase 7E.1 smoke test (`PHASE_7E.1_STATUS.md`)
constructs `LiveLauncher(FakeEngine())` offscreen and walks
every contract symbol. It runs cleanly inside the dev
environment without booting Qt's GUI loop.

---

## The freeze

> No future launcher phase may remove a public signal or
> rename a public method on these classes.

Adding a new signal or method is fine — the contract grows.
Removing one — even when no widget currently fires it —
breaks the host's `connect(...)` and crashes the launcher
on next boot.

If a contract symbol *must* be removed (a major version
break), the steps are:

1. Update `app/main.py` first to drop its `connect(...)`.
2. Wait one release.
3. Remove the symbol from the widget class.
4. Update this document to reflect the new contract.

The slow path exists because the launcher is the user's
front door. A failed boot is the worst possible regression.
