# Phase 11B — Landing Wiring

**Status:** complete · files only. No git operations.

**Directive:** wire the loose ends on the Phase 11A
v2 landing. Place placeholder download artifacts.
Build the `/docs` route. Verify footer links
resolve. Ship a brand-aligned 404. No visual
redesign. `apps/web` only.

---

## What shipped

| Path                                                              | Change                          |
|-------------------------------------------------------------------|---------------------------------|
| `apps/web/public/downloads/recall-0.1.0-alpha-placeholder.txt`    | new (placeholder for desktop binary) |
| `apps/web/public/downloads/recall-extension-placeholder.txt`      | new (placeholder for extension zip)  |
| `apps/web/app/components/v2/links.ts`                              | repointed `download` / `extension` to the placeholder paths |
| `apps/web/app/docs/page.tsx`                                       | new — 8-section docs route       |
| `apps/web/app/components/v2/Footer.tsx`                            | "MIT License" link repointed (no LICENSE file at repo root yet — points at the FAQ that documents the claim) |
| `apps/web/app/not-found.tsx`                                       | new — brand-aligned 404          |
| `docs/engineering/PHASE_11B_STATUS.md`                             | new (this file)                  |

**LOC ≈ 850 across 6 new files + 2 edits.**

**Files outside the directive's `apps/web` scope: 1** —
this status doc lives at `docs/engineering/` for
parity with prior phase capstones. Everything else
is strictly inside `apps/web/`.

---

## Task-by-task

### 1. Placeholder downloads

Two text files under `apps/web/public/downloads/`
matching the names the directive specified.
Clicking "Get alpha" / "Download alpha" / "Install
extension" anywhere on the site now triggers a
real download instead of a 404.

The placeholder files explain what they're a
stand-in for and how to build / sideload from
source today. When the production release
pipeline ships real artifacts, the placeholder
names get replaced by the real `.dmg` / `.zip`.

`V2_LINKS` was repointed accordingly:

```diff
- download:  "/downloads/recall-0.1.0-alpha.dmg",
- extension: "/downloads/recall-extension.zip",
+ download:  "/downloads/recall-0.1.0-alpha-placeholder.txt",
+ extension: "/downloads/recall-extension-placeholder.txt",
```

`windowsLite` / `windowsFull` / `macos` (currently
unused on the v2 landing but exposed in the
constants module) also fall back to the desktop
placeholder for now.

### 2. `/docs` route

`apps/web/app/docs/page.tsx` — single long-scroll
page with the eight sections the directive named:

```
01 · What is Recall
02 · How capture works
03 · Investigations
04 · Recovery
05 · Resume
06 · Local-first
07 · Extension
08 · CLI
```

Layout: same v2 dark cinematic palette — **no
visual redesign**. Reuses `Nav`, `Footer`, and the
v2.css tokens directly. Two-column grid:

- **Left rail (240 px, sticky)** — section
  contents list. Active section tracked by
  `IntersectionObserver`; clicking a row scrolls
  smoothly to that section.
- **Right column** — 8 content sections + a
  "next" cross-link block pointing at the alpha
  pack in the repo.

Each section uses small primitive components
defined in the file (`DocsSection`, `Code`,
`CodeBlock`, `Kbdish`, `Pullquote`) so the inline
style stays bounded.

Mobile: the sidebar collapses above the article
under 1000 px (via a scoped `styled-jsx` block).

### 3. Footer link audit

Walked through every `href` in
[`apps/web/app/components/v2/Footer.tsx`](../../apps/web/app/components/v2/Footer.tsx).
Twelve links total across three columns:

| Column         | Label          | Target                                                                  | Resolves? |
|----------------|----------------|-------------------------------------------------------------------------|-----------|
| Product        | Memory OS      | `#v2-window`                                                            | ✅ MemoryOSWindow `id="v2-window"` |
| Product        | Continuity     | `#v2-continuity`                                                        | ✅ ContinuityAnimation `id="v2-continuity"` |
| Product        | Demo           | `#v2-demo`                                                              | ✅ DemoBand `id="v2-demo"` |
| Product        | Download       | `/downloads/recall-0.1.0-alpha-placeholder.txt`                         | ✅ created in task 1 |
| Engineering    | GitHub         | `https://github.com/kunalKumar-13/Recall-me`                            | ✅ external |
| Engineering    | Docs           | `/docs`                                                                 | ✅ created in task 2 |
| Engineering    | Extension      | `/downloads/recall-extension-placeholder.txt`                           | ✅ created in task 1 |
| Engineering    | Audit log      | `${github}/blob/main/AUDIT/REPO_STABILIZATION.md`                       | ✅ file exists in repo |
| Trust          | Local-first    | `#v2-privacy`                                                           | ✅ PrivacyGrid `id="v2-privacy"` |
| Trust          | Resume flow    | `#v2-timeline`                                                          | ✅ ResumeTimeline `id="v2-timeline"` |
| Trust          | Security       | `${github}/security`                                                    | ✅ GitHub auto-route |
| Trust          | MIT License    | `${github}/blob/main/apps/docs/faq.mdx`                                 | ⚠️ workaround — see note |

**Note on the MIT License link.** The repo has no
`LICENSE` file at root today, so the prior
`/blob/main/LICENSE` URL would 404. The
`apps/docs/faq.mdx` file does explain the MIT
licensing claim, so the link points there in the
interim. When a real `LICENSE` lands at the repo
root, one line in `Footer.tsx` flips back to the
canonical path.

### 4. Brand-aligned 404

`apps/web/app/not-found.tsx` — Next.js App Router
picks this up automatically for any unmatched
route. Reuses the v2 design language without
introducing new tokens:

- Atmosphere — same dual radial-gradient bloom
  as the hero, dimmed.
- Bloom mark — concentric lavender rings with
  the same radial-gradient centre as the
  launcher's empty state.
- Eyebrow: `404 · this memory never landed`.
- Headline: two-line title with a serif-italic
  gradient second line.
- CTAs — three buttons matching the primary /
  ghost / text hierarchy used elsewhere: **Back
  to landing**, **Open the docs**, **Browse the
  repo**.
- A small mono "debug" line at the bottom —
  `GET · 404 · NO RESUMABLE WORK AT THIS PATH`
  — winks at the local-first audience without
  drifting from the brand.
- Footer microline echoes the main footer's
  bottom row.

No new aesthetic. All visual primitives are
already defined in `v2.css` or imported from
`components/v2/icons.tsx`.

### 5. Visual redesign

None. Per directive.

### 6. Git

None. Per directive + the persistent
[`no-auto-commit`](file:///c%3A/Users/kunal/.claude/projects/c--Users-kunal-Desktop-recall-me/memory/feedback_no_auto_commit.md)
memory rule. No `git status`, `git add`,
`git commit`, `git push`, `git tag`,
`git merge`, `git rebase`.

---

## How to preview locally

```bash
cd apps/web
npm install
npx next dev
```

| URL                                                                | Should serve |
|--------------------------------------------------------------------|--------------|
| `http://localhost:3000`                                            | Phase 11A landing (unchanged visually) |
| `http://localhost:3000/docs`                                       | new 8-section docs page |
| `http://localhost:3000/anything-else`                              | new branded 404 |
| `http://localhost:3000/downloads/recall-0.1.0-alpha-placeholder.txt` | downloadable placeholder |
| `http://localhost:3000/downloads/recall-extension-placeholder.txt` | downloadable placeholder |

Every footer link is now click-tested against the
list above. The two ⚠️ flags from earlier (`/docs`
and `/downloads/*` 404) are both cleared.

---

## What's NOT touched

- `app/` (engine, core, UI launcher). Untouched.
- `api/`. Untouched.
- `apps/extension/`. Untouched.
- `apps/admin/`. Untouched.
- `apps/docs/`. Untouched (the Mintlify site stays where it is).
- `infra/`. Untouched.
- `archive/`. Untouched.
- The v2 design tokens (`v2.css`). Untouched.
- The 11 v2 section components. Untouched.

The only file inside `apps/web/app/components/v2/`
that was edited is `links.ts` (repointed download
paths) and `Footer.tsx` (one MIT-License URL
flip). No section component was touched. The
Phase 11A visual surface ships forward
bit-identical.

---

## Honest residuals

| Item                                                                                    | Severity | Resolution path                                          |
|-----------------------------------------------------------------------------------------|----------|----------------------------------------------------------|
| `LICENSE` missing at repo root                                                          | P2       | Drop a real LICENSE file at root in a future phase (out of `apps/web` scope) |
| `/downloads/*` paths serve text placeholders, not real installers                      | P1       | Wire the production release pipeline to drop the real artifacts at the same names |
| `next/font/google` Geist/Geist Mono/Instrument Serif fallback on Next 14.2.x           | P2       | Either upgrade to Next 15 (re-enable `next/font`) or self-host the TTFs under `public/fonts/` |
| Demo modal video poster is a stage-cycling mock, not a real recorded clip               | P2       | Record + upload a 44-second screen capture; replace `ModalLauncher` with a `<video>` element |
| Old Phase 6G landing components in `apps/web/app/components/*` remain unreferenced     | P2       | Move to `archive/web-pre-v2/` per the Phase 10C audit recommendation |

None of these block the landing's "real launch
site" usefulness — every CTA on the page now
fires a real action.

---

## No git operations performed

Per the directive's final clause and the standing
memory rule. Files exist on disk; you pick the
staging surface from here.
