# Recall — Design Brief

*Hand this to a designer whole. It is the product, the brand, the
surfaces, the rules, and the deliverables. Everything in here is
true of the shipped software — nothing is aspirational copy.*

---

## 1 · What Recall is (say it in one breath)

**Recall is a local-first continuity OS.** It quietly captures the
*shape* of your work — the pages you visit, the searches you run, the
AI chats you have, the files you open, how long your attention stays —
and reconstructs what you were mentally working on. When you come back
after an interruption, one keystroke (⌃Space) hands the whole thing
back: the files, the chats, the tabs, reopened in the right order.

The tagline: **Never lose the thread.**

The one claim everything serves: *a continuity layer for your own
thinking is only useful if it stays on your machine.* 100% local. No
cloud, no accounts, no telemetry. Plain text files in one folder
(`~/.recall/`) — delete the folder and it never happened.

**What Recall is NOT** (and must never look like): an AI memory
assistant, a chatbot, a productivity dashboard, a recommendation feed,
a surveillance tool that screenshots your screen. The words "AI-powered",
"smart memory", "intelligent recall", "neural" are banned from every
surface.

## 2 · Who it's for and how it should feel

Developers, founders, researchers — people whose day is fifty open
loops, who get pulled away mid-implementation and come back to a clean
desk and an empty head. Skeptical, privacy-literate, allergic to hype.
They will read the code (it's open source) and check every claim.

The product should feel like **critical infrastructure you'd leave
running for years**: quiet, inevitable, minimal, precise. Aesthetic
lineage: Stripe, Linear, Raycast, Tailscale, SQLite. The site should
feel like it was drafted on a drafting table by someone who measures
twice. Never generic AI SaaS, never crypto-glow, never dashboard-y.

## 3 · How it works (the honest mental model)

```
capture sources          the engine (local daemon)         surfaces
─────────────────        ──────────────────────────        ────────────────
Chrome/Edge/Arc/Brave →                                  → Launcher (⌃Space)
VS Code companion     →   127.0.0.1:4545                 → Extension popup
macOS desktop focus   →   seven deterministic layers:    → Console (browser
git hooks · CLI       →   events → sessions → contexts     ↔ local daemon)
                          → resurfacing → threads →
                          evolution → recovery
```

- **Deterministic**: same events in → same memory out. No learned
  weights, no probabilistic guessing. Heuristics you can read.
- **Inspectable**: every artifact is JSON/JSONL on disk, auditable
  with `cat`, deletable with `rm`.
- **Budgeted**: every endpoint has a performance budget enforced by
  tests (search <60ms, writes <2ms, resurfacing <25ms). Budgets are
  content — we print them on the site.
- **The loop grades itself**: Recall counts (counts only, never
  content) whether its own loop closes — did you come back, did it
  surface your work, did you resume, did the resume work. Green /
  yellow / red verdicts, shown honestly even when red.

## 4 · The surfaces (each has ONE job)

1. **macOS launcher** (Tauri, borderless dark-vibrancy panel,
   summoned by ⌃Space): *continue where you left off.* Recovery
   hero → active threads → "on your radar". Typing searches memory +
   files on one thread-spine with per-layer node hues. Enter restores
   work in choreographed order (files → chats → tabs by domain →
   searches, 140ms stagger). ⌘, opens settings (live hotkey
   re-record, start at login).
2. **Browser extension** (440×640 popup, "the instrument"): glance
   and act. Hairline regions, bracket labels: `[ continue ]` with the
   real restoration plan inline, `[ today ]` with a 24-hour rhythm
   histogram, `[ threads ]`, `[ tail ]` (live last moments), a mono
   trust foot (`local only · 0 uploads · daemon ok`). ⌘K search
   overlay. Settings with REAL controls: per-kind capture toggles,
   pause-for-an-hour, private-sites exclusion list.
3. **The website** (Next.js, the drafting frame): make a skeptic
   download it. Chapters: hero spread → stats band → the film (scroll
   scrubs a live-DOM re-enactment of losing and recovering a day) →
   capabilities bento (art = the product drawn honestly) →
   architecture beams → extension chapter → local-first/privacy →
   the honest comparison table → built-in-the-open band → FAQ →
   closer. Giant evolving footer wordmark.
4. **The console** (`/console` — hosted page, but every request goes
   browser → the visitor's OWN daemon on 127.0.0.1:4545; zero
   proxying): the engine room for power users. One full-viewport
   cockpit: rail (seven-layer meter, vitals, the loop verdicts),
   stage (command search + today's 24h histogram), side (continue
   with the real plan, threads, radar), footer (live tail + perf
   pulse vs budgets). Read-only by design.

## 5 · Feature inventory (all real, all shipped)

**Capture**: page visits · searches (Google/DDG/Bing/Kagi/Perplexity)
· AI chats (ChatGPT/Claude/Gemini/Copilot/Grok/DeepSeek/Poe) · SPA
route changes · attention dwell with work-block hints (8s minimum,
30min cap, new block after 5min silence) · VS Code file opens/saves ·
macOS app focus (opt-in) · git hooks + open API for anything else ·
durable offline outbox (daemon down = queued, never lost) · incognito
never captured · DOM/page content never read.

**Memory**: 30-min sessions · topic-coherent micro-contexts ·
persistent threads across weeks · evolution phases inside a thread
(research → implementation → revisit) · idle resurfacing ("on your
radar") · recovery candidates with confidence + honest captions
("2 tabs · 1 file · returned to this 3× · last active during
implementation").

**Retrieval & action**: episodic search + semantic file search in one
query, <100ms · one-keystroke choreographed restore · per-step
restoration plan you can inspect · self-check endpoint ("N events
today, by kind").

**Trust**: everything above + pause + exclusions + `0 uploads` counts
+ the daily loop grading itself + full source on GitHub.

## 6 · Brand foundations (already established — refine, don't replace)

**Logo/mark**: the wordmark "Recall" with a red node as the period;
the mark is a single thread finding its node (a drawn S-curve ending
in a dot). The thread is the brand: memory as a thread you never
lose, events as nodes along it.

**Color** — light ("porcelain") is primary, dark ("ink night") is a
first-class equal, switched by channel tokens:
- Porcelain paper `#fbfbfa` · ink `#171613` · card white `#ffffff`
- Ink night: charcoal `#131210` · bone `#f0eee9` · card `#1c1a17`
- **The red thread** `#bf3b2b` (light) / ember `#d24b35` (dark) — the
  ONLY accent. Spend it on: the thread, live dots, selected states,
  one word per section. Status colors (green `#4fa784` / amber
  `#d09a2e`) exist only for verdicts, never decoration.
- Hairlines at ink-12% / ink-7%. Shadows stay warm-black in both themes.

**Type** (all self-hosted, zero network fonts):
- **Geist Sans** — display + body. Headlines 600 weight, tight
  (−0.03em), huge (up to ~9.6rem in the hero spread).
- **Instrument Serif italic** — exactly one editorial phrase per
  headline ("Never lose / *the thread.*", "Total recall, *without the
  surveillance.*"). It is the human voice inside the engineering.
- **Geist Mono** — all provenance: timestamps, paths, budgets, counts,
  eyebrows, key hints. If a number means something, it's mono +
  `tabular-nums`.

**Recurring motifs** (the visual vocabulary — use them everywhere):
- The **drafting frame**: two hairline rails at the content edges run
  the full page; chapters rule across full-bleed; a small `+` sits on
  every rule×rail intersection.
- **Bracket eyebrows**: `[ 03 ] ARCHITECTURE` — mono, letter-spaced,
  numbered.
- **The thread**: draws itself (stroke-dashoffset), weaves through
  compositions, drops nodes, ends in the pulsing node. Footer
  wordmark: outlined letters fill solid as the thread passes.
- **Hairline cells, not cards**: bento grids and consoles are one
  surface divided by 1px lines. No floating rounded-card soup, no
  glassmorphism, no gradients-as-decoration.
- **24-hour histograms** (the day's rhythm, current hour in red),
  **keycap glyphs** (⌃ + space with a press animation), **dot grids**,
  **live pills** (`● LOCAL`, `● daemon ok`), **kind chips**
  (`browser_visit` in red mono).

**Motion** (one easing family: `cubic-bezier(0.16, 1, 0.3, 1)`):
words settle out of a slight blur; threads draw in; bars grow; beams
travel along wires; keycaps press; marquees drift and pause on hover.
Nothing bounces, nothing spins, nothing glows. Every animation has a
`prefers-reduced-motion` fallback showing the final state.

**Voice**: plain, checkable, quietly confident. Every claim is
auditable ("every claim above is checkable — the code is public and
the files are yours"). Numbers over adjectives. Honest even when
unflattering (the loop shows RED verdicts publicly). Sentence-case
headlines. Vocabulary is fixed: *moment / memory / session / thread /
resurfacing / recovery / restoration / continuity* — never "AI
memory".

**Copy bank** (in use, keep or improve): "Never lose the thread." ·
"Continue where you left off" · "Your mind, rethreaded." · "Total
recall, without the surveillance." · "One engine, every surface." ·
"Everything you need. Nothing watching you." · "delete the folder, it
never happened" · "loopback is the boundary" · "counts only, never
content" · "A quiet witness, watching for you" · "Watch the thread
break, then come back."

## 7 · Hard rules (the charter, distilled — non-negotiable)

1. Calm UX: no badges, no notifications, no streaks, no gamification,
   no autoplaying video, no dopamine mechanics.
2. Local-first is the story: every surface must whisper it (trust
   pills, `127.0.0.1:4545`, `0 uploads`, file paths).
3. Honesty: empty states earn copy; nothing pretends; disabled ≠
   hidden; demo data is labeled demo.
4. One accent, spent deliberately. If red is everywhere it's nowhere.
5. Real content only in mockups — real thread titles, real captions,
   real budgets. Never lorem, never fake "98% productivity" numbers.
6. Both themes are first-class; design them together.
7. Self-contained assets: fonts bundled, no CDN anything.
8. New surfaces must read *quieter* than existing ones, not louder.

## 8 · References / anti-references

**Study**: beta.spoo.me (grade of polish, framed canvas, motion
restraint) · Linear (dark, type discipline) · Stripe docs (honest
tables) · Raycast (launcher language) · Tailscale (trust voice) ·
teenage engineering + Braun/Rams (instrument panels, for the console).

**Refuse**: purple-to-blue AI gradients · glassmorphism · neon glow ·
emoji section markers · rounded-card grids with drop shadows
everywhere · mascots · dashboard KPI tiles · anything that smells like
a crypto landing page.

## 9 · Deliverables

1. **Brand kit**: refined mark + wordmark (the thread/node concept),
   lockups, clearspace, app icon (macOS), extension icons 16/32/48/128,
   favicon, OG/social images (site + GitHub preview), README banner.
2. **Website**: polish/evolve the existing chapter system (desktop +
   mobile, light + dark, motion spec per section, hero spread
   composition, film player chrome, bento art refinement, footer
   wordmark moment).
3. **Console**: the cockpit as the flagship power surface — rail /
   stage / side / footer, data-viz language (histogram, meter, pulse),
   empty + demo + connected states.
4. **Product UI**: launcher panel states (resting / searching /
   detail / settings / restoring), extension popup + options page +
   search overlay + settings, all states (loading / offline /
   disconnected / empty / paused / demo).
5. **Motion spec**: named curves, durations, choreography per surface,
   reduced-motion equivalents.
6. **Launch assets**: 5–8 marketing screenshots (real data styling),
   .dmg installer background, one 30–60s product film storyboard
   (can reuse the site's film beats: deep in it → the day happens →
   come back to nothing → one keystroke, all of it, back).

**Definition of done**: a stranger lands, and within 10 seconds knows
(a) it brings your work back with one keystroke, (b) it never leaves
your machine, (c) it's serious software built by people who measure.
And every pixel would survive the owner's test: *"would someone trust
this enough to leave it running all day for years?"*
