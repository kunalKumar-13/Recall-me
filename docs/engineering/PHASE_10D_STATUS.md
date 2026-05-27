# Phase 10D — Launcher Showcase Polish

**Status:** complete · launcher prepared for demo +
interview. Files only — no commits.

**Directive:** reduce visual noise. Strengthen hero
+ preview hierarchy. Keep recovery card LEFT/RIGHT
shape. Cap Other work at 3 rows. Search stays
Raycast-style. Empty stays bloom-centred. Generate
fresh captures.

**Allowed scope:** `app/ui/launcher_v3/*`,
`assets/screenshots/launcher-showcase/*`, this
status doc.

**Touched outside that scope:** none.

---

## What changed

### Hero (Task 1)

| Aspect                          | Phase 10B           | Phase 10D          |
|---------------------------------|---------------------|--------------------|
| Title size (`FS_HERO_TITLE`)    | 22                  | **23**             |
| Serif accent size               | `+3` (25)           | `+3` (26)          |
| Title letter-spacing            | -2.2 sans / -2.0 serif | -2.4 sans / -2.0 serif |
| Hero card padding               | 18 / 16             | **22 / 20**        |
| Title → chips gap               | 14                  | **16**             |
| `last_active` mono microtext on actions row | shown   | **removed**        |

The eyebrow `"CONTINUE · Returned after 2 days"`
already carries the temporal metadata. The
bottom-right `"last active · implementation"` mono
line on the action row repeated it in a less
useful form. Removed.

The title-size bump is intentionally modest (22 →
23, not 22 → 25 as initially attempted): the
hero column is `1fr` of a `1fr / 220px` grid
inside a 760-px frame, and at 25 px the title
clipped against the preview card. 23 reads as a
clear page-headline weight without breaking
layout.

`RecoveryProps.last_active` remains in the
dataclass so callers don't break, but it is no
longer rendered. Future phases may surface it via
a different affordance.

### Preview card hierarchy (Task 2)

| Aspect                          | Phase 10B           | Phase 10D          |
|---------------------------------|---------------------|--------------------|
| Eyebrow text                    | `"PREVIEW · RELATED"`| **`"PREVIEW"`**    |
| Eyebrow weight                  | regular             | **bold**           |
| Eyebrow letter-spacing          | 14.0                | **18.0**           |
| PDF filename weight             | regular 10          | **bold 10**        |
| Highlight marker opacity        | 0.22                | **0.26**           |
| Card outer padding              | 14 / 14             | 14 / 14            |
| Card inner spacing              | 10                  | **11**             |

The eyebrow drops the redundant `"· RELATED"` and
gains weight + letter-spacing so it reads as a
section label rather than a tooltip. The PDF
filename goes bold so the eye lands there first.
The highlighted phrase (`assist healthcare
teams`) gets a slightly stronger lavender wash
(0.22 → 0.26) so it anchors the excerpt.

Left/right layout shape preserved exactly: hero
in `1fr`, PreviewCard in fixed 220-px right
column, both inside the Recovery state's content
area.

### Other work (Task 3)

| Aspect                          | Phase 10B           | Phase 10D          |
|---------------------------------|---------------------|--------------------|
| Max rows                        | 3 (`other_work[:3]`)| 3 (unchanged)      |
| Count text                      | `"3 of 14"` (synthetic) | **`"3 active"`** |
| Hover glow                      | `T.CARD_HOVER` fill | unchanged          |
| Strength dot                    | lavender / mid / dim| unchanged          |
| Time-ago column                 | mono, right-aligned | unchanged          |

The synthetic `"of 14"` denominator implied a
queue that doesn't exist. The 3-row cap is the
contract — there is no longer queue. The count
now reads `"3 active"`.

Hover glow + strength dot + time-ago column were
already correct; no change needed.

### Search (Task 4)

Visual surface from Phase 10A unchanged. The four
groups (Investigation / Files / Returns / Events),
the selected-row accent rail, the mini preview
pane, the `11 results` mono microtext, and the
`⌃K` hint are all already Raycast-shaped. The
showcase capture re-renders the same surface
deterministically.

### Empty (Task 5)

Visual surface from Phase 10A unchanged. Centred
bloom mark, `"Everything you leave"` headline,
serif-italic gradient accent `"becomes
searchable."`, sub copy, two CTAs (Show example +
Start working). The polish targets named in the
directive (centre bloom, headline, serif accent,
2 CTAs) all already match.

### Captures (Task 6)

Four PNGs in
[`assets/screenshots/launcher-showcase/`](../../assets/screenshots/launcher-showcase/):

| File           | State                | What it shows                              |
|----------------|----------------------|--------------------------------------------|
| `empty.png`    | `STATE_EMPTY`        | bloom + headline + serif gradient + 2 CTAs |
| `recovery.png` | `STATE_RECOVERY`     | polished hero + preview + 3-row Other work |
| `search.png`   | `STATE_SEARCH`       | grouped result list + mini preview pane    |
| `resume.png`   | `STATE_RESUME`       | check disc + RESTORED + 5-row restored list |

Rendered against a 920×640 dark backdrop with the
violet bloom (matches the design pack's
`<Stage>` wrapper). The launcher pixmap itself is
760×520, centred at `(80, 60)` inside the
backdrop.

These four are the **demo / interview surface**.
The previous capture sets remain:

- `launcher-final/` — Phase 10A design-
  conformance captures (bare `DarkLauncher`)
- `launcher-live-final/` — Phase 10B production
  captures (via `Launcher()` with engine fixtures)
- `launcher-showcase/` — Phase 10D polish set
  (this directive)

---

## Files touched

| Path                                                       | Change                                           |
|------------------------------------------------------------|--------------------------------------------------|
| `app/ui/launcher_v3/theme.py`                              | `FS_HERO_TITLE` 22 → 23 (1 line)                  |
| `app/ui/launcher_v3/darkframe.py`                          | `HeroRecovery` polish (padding, gap, drop `last_active` line); `PreviewCard` polish (eyebrow, badge weight, highlight opacity); Other-work count text |
| `assets/screenshots/launcher-showcase/empty.png`           | new                                              |
| `assets/screenshots/launcher-showcase/recovery.png`        | new                                              |
| `assets/screenshots/launcher-showcase/search.png`          | new                                              |
| `assets/screenshots/launcher-showcase/resume.png`          | new                                              |
| `docs/engineering/PHASE_10D_STATUS.md`                     | new (this file)                                  |

**Files outside the directive's allowlist: 0.**

No engine, no recovery logic, no capture code, no
admin, no extension, no landing-page work. The
public `DarkLauncher` API surface is unchanged —
`RecoveryProps.last_active` stays defined for
back-compat even though it no longer renders.

---

## Verification

| Check                                                                | Result   |
|----------------------------------------------------------------------|----------|
| `DarkLauncher()` constructs                                          | ✅       |
| `set_state(STATE_EMPTY)`                                             | ✅       |
| `set_state(STATE_RECOVERY, recovery=RecoveryProps(), preview=PreviewProps())` | ✅ |
| `set_state(STATE_SEARCH)`                                            | ✅       |
| `set_state(STATE_RESUME)`                                            | ✅       |
| 4 PNGs in `assets/screenshots/launcher-showcase/`                    | ✅       |
| Title no longer clips against preview column                         | ✅       |
| Preview filename, badge, excerpt all visible (`pitch_healthcare_v3.pdf`) | ✅    |
| Other-work header reads `"3 active"`, not `"3 of 14"`                | ✅       |
| Eyebrow reads `"PREVIEW"`, not `"PREVIEW · RELATED"`                 | ✅       |
| No `last active · implementation` microtext on the actions row       | ✅       |

---

## Success criterion

> Prepare launcher for demo + interview.

Met. The four showcase captures are the artifact
the directive asked for — each is a clean,
single-frame view of one state, free of duplicate
metadata, with a stronger preview hierarchy and
the cleaner Other work count.

---

## No git operations performed

Per the directive's final clause: "No commits. No
push. No git. Stop after files only."

Files exist on disk. `git status` not run, `git
add` not run, no commit, no push. The user picks
the staging surface from here.
