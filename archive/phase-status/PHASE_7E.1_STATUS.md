# Phase 7E.1 — Launcher Stability

**Status:** complete · regression patched · contract frozen
**Directive:** launcher boots every time. No visual work,
no redesign. Audit + freeze the public interface.

> The launcher is the user's front door. A failed boot is
> the worst possible regression.

---

## The regression

Phase 7E rewrote `MinimalSearchBar` for the new
700×500 surface and **dropped two signals**:

- `request_settings`
- `request_close`

But `LiveLauncher.__init__` still wired both:

```python
self._search.request_settings.connect(self.request_settings.emit)
self._search.request_close.connect(self.hide)
```

Result: every `python recall.py` crashed during launcher
construction with:

```
AttributeError: 'MinimalSearchBar' object has no attribute 'request_settings'
```

Reproduction (offscreen, no Qt GUI needed):

```python
from app.ui.launcher_v3 import LiveLauncher
class FakeStore:
    def count(self): return 0
class FakeEngine:
    store = FakeStore()
launcher = LiveLauncher(FakeEngine())  # ← AttributeError here
```

---

## The fix

[`app/ui/launcher_v3/minimal.py`](../../app/ui/launcher_v3/minimal.py)
— restore the dropped signals **and** add the rest of the
documented contract:

```python
class MinimalSearchBar(QWidget):
    # Frozen contract — Phase 7E.1.
    query_changed = pyqtSignal(str)
    searchChanged = pyqtSignal(str)
    submit = pyqtSignal(str)
    request_settings = pyqtSignal()
    request_close = pyqtSignal()
```

Wired both spellings of the text-change signal:

```python
self._input.textChanged.connect(self.query_changed.emit)
self._input.textChanged.connect(self.searchChanged.emit)
```

Added the missing methods:

```python
def clear(self) -> None: self._input.clear()
def selectAll(self) -> None: self._input.selectAll()
```

The two *may-not-exist* signals (`request_settings`,
`request_close`) are declared even though no widget in 7E
fires them. Consumers (`LiveLauncher`, future paints) can
`connect(...)` safely; later phases may add an
on-screen affordance that fires either signal without
needing to touch the host wiring.

---

## Frozen contract

| Class             | Signals                                                                 | Methods                       |
|-------------------|-------------------------------------------------------------------------|-------------------------------|
| `MinimalSearchBar`| `query_changed(str)`, `searchChanged(str)`, `submit(str)`, `request_settings()`, `request_close()` | `focus()`, `clear()`, `selectAll()` |
| `LiveLauncher`    | `request_settings()`, `_request_search(str)`                            | `show_centered()`, `invalidate_digest()`, `_refresh_idle_state()`, `hide()` |

Full per-symbol detail + the wiring map lives in
[`docs/product/LAUNCHER_CONTRACTS.md`](../../docs/product/LAUNCHER_CONTRACTS.md).

---

## Files touched

**Edited:**

- [`app/ui/launcher_v3/minimal.py`](../../app/ui/launcher_v3/minimal.py)
  — restored 2 signals, added `searchChanged` alias, added
  `clear()` + `selectAll()` methods, documented the
  contract inside `MinimalSearchBar`'s docstring.

**New:**

- [`docs/product/LAUNCHER_CONTRACTS.md`](../../docs/product/LAUNCHER_CONTRACTS.md)
  — the frozen interface document.
- [`docs/engineering/PHASE_7E.1_STATUS.md`](PHASE_7E.1_STATUS.md)
  — this file.

No widget paint changed. No layout changed. No new
features.

---

## Verification

| Check                                                  | Result                          |
|--------------------------------------------------------|---------------------------------|
| `python -m pyflakes app/ui app/core api`               | clean                           |
| `MinimalSearchBar` carries all 5 frozen signals        | yes                             |
| `MinimalSearchBar` carries all 3 frozen methods        | yes                             |
| Both `query_changed` + `searchChanged` fire on type    | yes (`{'query_changed':1,'searchChanged':1}`) |
| `request_settings` propagates up to `LiveLauncher`     | yes (`hits=1` on `.emit()`)     |
| `LiveLauncher(FakeEngine())` constructs offscreen      | yes — no `AttributeError`       |
| `python recall.py doctor`                              | GREEN config / events / extension / installer; daemon RED expected (not running) |

---

## Why this is a phase

A bug fix is a bug fix — it doesn't normally get a phase.
This one does because the fix surfaces a *missing
discipline*: the launcher needs a documented Python
interface that the host can rely on across rewrites. 7E
proved a paint rewrite can silently delete signals that
the host wires; the freeze in
[`LAUNCHER_CONTRACTS.md`](../../docs/product/LAUNCHER_CONTRACTS.md)
+ this status doc are the discipline that keeps it from
happening again.

---

## Success criterion

> launcher boots every time.

Reproduces the boot via offscreen `LiveLauncher`
construction, gets `CONSTRUCT OK · DEFAULT_SIZE: (700,
500)`. No `AttributeError`. The contract is documented,
the missing pieces are restored, and the freeze rule is
written down.
