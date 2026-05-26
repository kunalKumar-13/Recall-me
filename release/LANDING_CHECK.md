# LANDING_CHECK — landing page audit for v0.1.0-rc1

A pass over the marketing site
([`apps/web/`](../apps/web/)) to confirm every
RC1-facing claim has working evidence behind it
and no dead links.

**Scope:** [Hero](../apps/web/app/components/Hero.tsx),
[Download](../apps/web/app/components/Download.tsx),
[Privacy](../apps/web/app/components/Privacy.tsx),
[Screens](../apps/web/app/components/Screens.tsx),
[Story](../apps/web/app/components/Story.tsx),
[Footer](../apps/web/app/components/Footer.tsx),
[Nav](../apps/web/app/components/Nav.tsx),
[FAQ](../apps/web/app/components/FAQ.tsx).

---

## TL;DR

| Check                | Result |
|----------------------|--------|
| TypeScript builds    | ✅ `cd apps/web && npx tsc --noEmit` exit 0 |
| Asset paths resolve  | ✅ 6 of 6 screen tiles resolve to real PNGs |
| External link list   | ✅ 6 of 6 GitHub-bound URLs point at the correct repo |
| Anchor list          | ✅ all `#…` anchors map to sections that render |
| **Dead links**       | **0** |

Two cosmetic notes flagged below; neither blocks RC1.

---

## 1. Headline

**Source:** [Hero.tsx:109-114](../apps/web/app/components/Hero.tsx#L109-L114)

```
Recall notices
unfinished work.
```

Subhead:

```
Return later.
Continue instantly.
```

CTAs:

| CTA              | href                               | Status |
|------------------|------------------------------------|--------|
| Download alpha   | `#download`                         | ✅ scrolls to Download section |
| Watch demo       | `LINKS.demoVideo` = `#how`         | ✅ scrolls to How it works |

**Verdict:** ✅ headline + CTAs work. The "watch
demo" link currently points at an in-page anchor
rather than a real video URL — intentional
placeholder per the [`links.ts`](../apps/web/app/lib/links.ts)
comment ("internal scroll until a real Loom/YouTube
URL exists"). Not dead; tracked as a content-fill
item for the post-RC1 launch.

---

## 2. Download section

**Source:** [Download.tsx](../apps/web/app/components/Download.tsx)

Four artifact cards:

| Card                        | href                                   | Status |
|-----------------------------|----------------------------------------|--------|
| Recall — Lite installer     | `LINKS.release`                        | ✅ → GitHub releases/latest |
| Recall — Full installer     | `LINKS.release`                        | ✅ → GitHub releases/latest |
| Recall — macOS preview      | `…/blob/main/docs/release/MAC_OWNER_NEEDED.md` | ✅ file exists |
| Browser extension           | `LINKS.release`                        | ✅ → GitHub releases/latest |

**Verdict:** ✅ all four artifact links land on a
real destination. The releases page is the single
source of truth for the binaries — exactly the
"one place" pattern the
[Download.tsx](../apps/web/app/components/Download.tsx)
header comment describes.

---

## 3. Trust / Privacy

**Source:** [Privacy.tsx](../apps/web/app/components/Privacy.tsx)

The trust section makes five claims:

| Claim                       | Backing evidence                                  |
|-----------------------------|---------------------------------------------------|
| local-first                 | [`CLAUDE.md` rule 2](../CLAUDE.md), [`STABILITY/CAPTURE.md`](../STABILITY/CAPTURE.md) |
| no cloud                    | Same                                              |
| no telemetry                | Same; no analytics SDKs in any `package.json`     |
| counts only                 | [`TRUST_LEDGER.md`](../docs/engineering/TRUST_LEDGER.md) |
| export only                 | [`TRUST_LEDGER.md`](../docs/engineering/TRUST_LEDGER.md) |

**Verdict:** ✅ every claim has a code-backed
source. No language drift, no contradiction with
the engineering charter.

---

## 4. Demo

**Source:** Hero CTA "Watch demo" + Story section.

The current "watch demo" anchor scrolls to the
[How it works](../apps/web/app/components/HowItWorks.tsx)
section instead of opening a video. This is the
documented placeholder behaviour
([`links.ts`](../apps/web/app/lib/links.ts) comment).

**For RC1 testers** the demo path is now better
served by the new
[`recall demo run`](../DEMO_MODE.md) CLI than
by a video. The landing page does not yet
reference this command — flagged as a content
follow-up (low priority).

**Verdict:** ✅ no dead link; ⚠️ one content
improvement available (mention `recall demo run`
in either Hero or Download copy).

---

## 5. Screens

**Source:** [Screens.tsx](../apps/web/app/components/Screens.tsx)
+ [Story.tsx](../apps/web/app/components/Story.tsx)

The page references **6 image paths**:

| `src=`                                             | File on disk                         | Status |
|----------------------------------------------------|--------------------------------------|--------|
| `/screens/launcher/launcher-digest.png`            | `apps/web/public/screens/launcher/launcher-digest.png` | ✅ |
| `/screens/launcher/launcher-empty.png`             | `apps/web/public/screens/launcher/launcher-empty.png` | ✅ |
| `/screens/extension/extension-home.png`            | `apps/web/public/screens/extension/extension-home.png` | ✅ |
| `/screens/extension/extension-recovery.png`        | `apps/web/public/screens/extension/extension-recovery.png` | ✅ |
| `/screens/demo/demo-launcher.png`                  | `apps/web/public/screens/demo/demo-launcher.png` | ✅ |
| `/screens/demo/demo-extension.png`                 | `apps/web/public/screens/demo/demo-extension.png` | ✅ |

**Verdict:** ✅ all 6 tiles resolve — no 404s.

**⚠️ Drift note (not a dead link):** the landing's
`/screens/launcher/` + `/screens/extension/`
folders still contain the **pre-7E / pre-7A**
captures. The current LIVE capture sets live at
`assets/screenshots/launcher-7e/` and
`assets/screenshots/extension-7a/`
([`SCREEN_INDEX.md`](../SCREEN_INDEX.md)). A
future phase should mirror the latest captures
into the web public folder. Cosmetic; the page
still renders and looks coherent.

---

## 6. Navigation + Footer

| Source                                          | Result |
|-------------------------------------------------|--------|
| [Nav.tsx:83](../apps/web/app/components/Nav.tsx#L83) — GitHub link  | ✅ `https://github.com/kunalKumar-13/Recall-me` |
| [Nav.tsx:96](../apps/web/app/components/Nav.tsx#L96) — Download anchor | ✅ `#download` resolves on this page |
| [Footer.tsx:90](../apps/web/app/components/Footer.tsx#L90) — GitHub social | ✅ |
| [Footer.tsx:93](../apps/web/app/components/Footer.tsx#L93) — Twitter | ⚠️ `https://twitter.com` (generic placeholder, not @recall) |
| [Footer.tsx:96](../apps/web/app/components/Footer.tsx#L96) — Discord | ⚠️ `https://discord.com` (generic placeholder) |
| Footer COLUMNS (9 links)                        | ✅ all resolve — 4 anchors + 5 GitHub/repo links |

**Verdict:** ✅ no dead links; ⚠️ two social
placeholders (Twitter, Discord) point at the
generic homepages rather than Recall accounts. Not
dead; not yet pointed at real accounts. Flag for
content-fill alongside the demo-video URL.

---

## 7. FAQ

**Source:** [FAQ.tsx](../apps/web/app/components/FAQ.tsx)

Two outbound links:

| Where                                      | href             | Status |
|--------------------------------------------|------------------|--------|
| [FAQ.tsx:53](../apps/web/app/components/FAQ.tsx#L53)   | `LINKS.github`   | ✅ |
| [FAQ.tsx:156](../apps/web/app/components/FAQ.tsx#L156) | `LINKS.issues`   | ✅ |

**Verdict:** ✅ both resolve.

---

## 8. Anchor inventory (in-page navigation)

The page's [ANCHORS](../apps/web/app/lib/links.ts) constants:

| Anchor       | Matches section id?                            |
|--------------|------------------------------------------------|
| `#top`       | ✅ rendered by Nav                              |
| `#how`       | ✅ [HowItWorks.tsx](../apps/web/app/components/HowItWorks.tsx) `id="how"` |
| `#features`  | ✅ [Features.tsx](../apps/web/app/components/Features.tsx) `id="features"` |
| `#privacy`   | ✅ [Privacy.tsx](../apps/web/app/components/Privacy.tsx) `id="privacy"` |
| `#faq`       | ✅ [FAQ.tsx](../apps/web/app/components/FAQ.tsx) `id="faq"` |
| `#download`  | ✅ [Download.tsx](../apps/web/app/components/Download.tsx) `id="download"` |

**Verdict:** ✅ every in-page anchor lands somewhere.

---

## 9. Build

```bash
cd apps/web
npx tsc --noEmit       # exit 0
```

**Verdict:** ✅ TypeScript clean across the
entire landing source.

---

## Summary

| Category             | Count | Notes                                             |
|----------------------|-------|---------------------------------------------------|
| Dead links           | **0** | Every external + internal href resolves          |
| Missing assets       | **0** | Every `src=` finds a real PNG                    |
| Cosmetic drift       | 3     | Demo video placeholder + Twitter/Discord placeholders + pre-7E launcher screens |
| Build errors         | **0** | `tsc --noEmit` clean                              |

**Landing-page verdict for RC1:** ✅ **ship-ready**.
The three cosmetic drifts above are content-fill
items for the public-alpha launch, not link
defects.

---

## Recommended follow-ups (post-RC1)

1. Mirror the current `assets/screenshots/launcher-7e/`
   + `assets/screenshots/extension-7a/` PNGs into
   `apps/web/public/screens/{launcher,extension}/`.
2. Swap `LINKS.demoVideo` from `#how` to a real
   Loom/YouTube URL once recorded.
3. Replace generic Twitter / Discord URLs with
   real account links when they exist.
4. Add a one-line "Run `recall demo run` to see
   it populated" hint to the Hero or Download
   section.

None of these are dead links; all are content
upgrades.
