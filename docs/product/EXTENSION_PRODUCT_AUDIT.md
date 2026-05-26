# Extension Product Audit — Phase 7A

The frozen-product checklist for the Recall browser extension.
Every state the user can land in is listed below with: the
condition that produces it, the capture proving it, and the
contract every region must satisfy.

> **Success criterion:** *open the extension → immediately
> understand: Recall remembered work · Recall can continue it ·
> Recall is running.*

---

## Global layout

Six fixed-position regions in a single **440 × 640** popup
(`body { width: 440px; height: 640px; overflow: hidden; }`):

```
+--------------------------------------+
|  Header                              |   56 px
+--------------------------------------+
|                                      |
|  Continue hero (when one exists)     |  110 px max
|                                      |
|  Active investigations               |  up to 4 × 48
|                                      |
|  Today timeline                      |  up to 8 rows
|                                      |
|  Activity (Browser + Desktop)        |  2 columns
|                                      |
+--------------------------------------+
|  Trust strip                         |   ~40 px
+--------------------------------------+
```

The main column is scrollable when the body exceeds the page;
the header + trust strip are pinned.

---

## Paint contract

| Token              | Value                              |
|--------------------|------------------------------------|
| Page               | `#F5F2ED` (warm paper)             |
| Card surface       | `#FFFFFF`                          |
| Sunken hover       | `#F0ECE5`                          |
| Hairline           | `#E6DED4`                          |
| Strong hairline    | `#D9CEBA`                          |
| Accent             | `#8B7FE3` (lavender)               |
| Accent soft        | `#EDE9FB`                          |
| Card shadow        | `0 12 32 rgba(0,0,0,.06)`          |
| Lift shadow        | `0 20 56 rgba(0,0,0,.12)` (search) |
| Card radius        | 20 px                              |
| Row radius         | 14 px                              |

**Forbidden.** Glass, blur, neon, gradient *AI* energy, drop
shadows >.10 alpha. The page reads as warm paper, not as a
translucent overlay.

---

## Motion contract

Phase 7A's exact directive: **120 / 180 / 240**.

| Token             | ms  | Used for                                  |
|-------------------|-----|-------------------------------------------|
| `--motion-fast`   | 120 | hover background fades, button press      |
| `--motion-normal` | 180 | section enter, search-overlay scrim       |
| `--motion-slow`   | 240 | view transitions, settings slide          |

One easing curve everywhere: `cubic-bezier(0.32, 0.72, 0, 1)`.
No bounce, no spring, no rotate.

---

## State catalogue

Each row below maps a `PopupState` (see `derivePopupState` in
[`App.tsx`](../../apps/extension/ui/src/App.tsx)) to its
capture + the conditions that produce it.

| State        | Condition                                          | Capture                                                                        |
|--------------|----------------------------------------------------|--------------------------------------------------------------------------------|
| `empty`      | daemon healthy, 0 events, no demo                  | [`empty.png`](../../assets/screenshots/extension-7a/empty.png)                 |
| `capturing`  | daemon healthy, events arriving, no recovery yet   | [`capturing.png`](../../assets/screenshots/extension-7a/capturing.png)         |
| `active`*    | investigations exist, no recovery                  | [`active.png`](../../assets/screenshots/extension-7a/active.png)               |
| `resume`*    | recovery exists (HIGH-confidence)                  | [`resume.png`](../../assets/screenshots/extension-7a/resume.png)               |
| `offline`    | `navigator.onLine === false`                       | [`offline.png`](../../assets/screenshots/extension-7a/offline.png)             |
| `search`     | Ctrl/Cmd+K opens the overlay                       | [`search.png`](../../assets/screenshots/extension-7a/search.png)               |
| `demo`       | engine empty, `demo_mode.state === "active"`       | [`demo.png`](../../assets/screenshots/extension-7a/demo.png)                   |

\* *`active` and `resume` share the same `PopupState`
machinery (`investigations` and `recovery` respectively); the
audit names them separately because their visible hero
behaviour differs.*

---

## Per-region contract

### 1. Header

Left: 26-px lavender Recall mark + small breathing daemon dot
+ subtitle. Right: Search button + Settings button.

| What                       | Value                                  |
|----------------------------|----------------------------------------|
| Mark size                  | 26 × 26, radius 8, gradient lavender   |
| Daemon dot                 | 7 px; breathes at 1.6 s when connected |
| Subtitle (connected)       | `Connected locally`                    |
| Subtitle (reconnecting)    | `Reconnecting…`                        |
| Subtitle (disconnected)    | `Daemon not running`                   |
| Subtitle (offline)         | `Browser is offline`                   |
| Subtitle (loading)         | `Connecting…`                          |
| Header buttons             | 30 × 30, radius 9, ink-2 stroke icons  |

**Removed from 6C/6D:** event-count badge, desktop badge, wrench
icon (those moved into the new Activity cards + the daemon dot).

### 2. Continue hero

Full-width white card with a 6-px lavender accent rail. Capped at
**110 px** tall. Single hero, ever.

| What                       | Value                                  |
|----------------------------|----------------------------------------|
| Margin                     | 0 var(--pad-edge) (18 px)              |
| Padding                    | 14 16 14 22 (left clears rail)         |
| Eyebrow                    | `CONTINUE` — 9 px, ink-3, tracked      |
| Confidence badge           | `HIGH` — accent-soft pill              |
| Title                      | 14 px / 600, one line, elided          |
| Chips                      | up to **3**, derived from caption       |
| Resume button              | 30 px tall, accent fill, `1` key chip  |

### 3. Active investigations

Vertical stack of 48-px rows inside a single white card. Each
row: strength dot + title (elided) + last-seen caption + chevron.

| What                       | Value                                  |
|----------------------------|----------------------------------------|
| Row height                 | 48 px                                  |
| Max visible without scroll | 4                                      |
| Strength dot               | 8 px, accent or ink-4                  |
| Title                      | 12.5 px / 600                          |
| Subtitle (last-seen)       | 10.5 px ink-3                          |
| Inter-row divider          | 1 px hairline                          |

### 4. Today timeline

Three-column grid: `time` (mono) / `source` (bold) / `label`.

| What                       | Value                                  |
|----------------------------|----------------------------------------|
| Time column                | 44 px wide, mono 11 px, ink-3          |
| Source column              | 88 px wide, 11 px / 600, ink-2         |
| Label column               | flex, 12 px ink                        |
| Row padding                | 8 16 (8 vertical, 16 horizontal)       |
| Empty rail                 | dashed `var(--line-strong)` border    |
|                            | + 36-px rail-glyph illustration        |

The empty rail replaces the prior *"No browser memory
captured yet"* prose with a visual that reads as *the
timeline is waiting*, not *nothing exists*.

### 5. Activity status cards

Two side-by-side white cards: Browser (live) + Desktop
(future). Each card lists what its layer watches + a one-word
status pill (`capturing` / `idle` / `offline` / `soon`).

Browser status logic:

| Connection | Events today  | Pill         |
|------------|---------------|--------------|
| connected  | > 0           | capturing    |
| connected  | = 0           | idle         |
| any other  | —             | offline      |

Desktop status logic:

| Connection | Apps today    | Pill         |
|------------|---------------|--------------|
| connected  | > 0           | capturing    |
| connected  | = 0           | soon         |
| any other  | —             | offline      |

The Desktop card surfaces the seam the directive names —
*Design UI now. Engine later.* — without lying about what
exists.

### 6. Trust strip

Single horizontal row at the bottom. Four tiny pills:

```
LOCAL ONLY   NO CLOUD   0 UPLOADS   DAEMON OK
```

| What                       | Value                                  |
|----------------------------|----------------------------------------|
| Pill height                | 18 px                                  |
| Pill radius                | 999 (round)                            |
| Font                       | 9.5 px / 700, tracked, uppercase       |
| Daemon pill colour         | OK green / WARN amber / muted          |

Replaces the prior `TrustSurface` section (~140 px tall) with
~40 px of pinned footer.

### 7. Search overlay

Ctrl/Cmd+K slides a 16-px-inset card down from the top with a
search input + groupings for **investigations / files / events
/ returns**. Esc closes. Click outside (scrim) closes.

| What                       | Value                                  |
|----------------------------|----------------------------------------|
| Trigger                    | Ctrl+K · Cmd+K · the header search btn |
| Source                     | in-memory filter (engine swap later)   |
| Groups                     | Investigations · Files · Returns · Events |
| Empty hint                 | "Type to search …" / "No matches for …"|
| Shadow                     | `var(--shadow-elevated)`               |

The corpus is in-memory for now (the directive: *Design UI
now. Engine later.*). When a unified search endpoint lands,
swap the `useResults` body and keep the UI intact.

---

## Capture architecture

| Layer       | What we capture today               | Future layer                       |
|-------------|-------------------------------------|------------------------------------|
| Browser     | tabs · title changes · revisit gaps · search pages · active windows | — |
| Desktop     | — (Activity card surfaces the seam) | VSCode · local files · desktop apps |

The Desktop card's `SOON` pill is the explicit promise — when
the engine lands, the card switches to `CAPTURING` without a UI
change.

---

## Verification matrix

| Check                                       | Result        |
|---------------------------------------------|---------------|
| `npx tsc --noEmit`                          | clean         |
| `npx vite build`                            | clean (~293 KB)|
| `node capture_extension.mjs`                | clean, 21 PNGs|
| Empty surface has stacked Show example + Start working | yes      |
| Capturing surface has Today rail + Activity cards | yes      |
| Resume surface shows hero with accent rail + Resume 112 | yes |
| Search overlay opens on Ctrl+K, lists 4 groupings | yes      |
| Trust strip pinned at bottom on every surface | yes         |
| Header daemon dot breathes when connected   | yes (CSS animation) |

---

## What did NOT change

- **The launcher.** Frozen in 6R; this phase is extension-only.
- **The control room.** Untouched.
- **The recovery engine + ranking.** Untouched.
- **The founder tooling / alpha dashboards.** Untouched.
- **The API surface.** `/v1/health`, `/v1/recovery/recent`,
  `/v1/threads/recent`, `/v1/events/recent`, `/v1/demo/*` —
  same endpoints, same payloads.

---

## What the user sees

Open the extension. Three things land in one glance:

1. **Recall remembered work** — the hero card (if work was
   recoverable) and the investigations list both name *what*
   was in flight.
2. **Recall can continue it** — the Resume button on the hero
   carries the `1` shortcut chip; clicking restores the
   targets via the same pipeline the launcher uses.
3. **Recall is running** — the breathing daemon dot in the
   header + the trust strip's `DAEMON OK` pill at the bottom.

If any of those three is unclear at a glance, treat it as a
regression. Fix the popup, never the engine.
