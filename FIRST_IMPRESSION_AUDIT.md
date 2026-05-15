# First-impression audit

A simulated 90-second viewing of `https://recall.computer` +
the GitHub README, from five different reader's seats. Each
persona has a goal, a question they're trying to answer, and
a tolerance for the friction Recall introduces.

This is the document I want a maintainer to re-read every time
a meaningful copy or surface change is proposed. If the change
**breaks** any persona's path through the site, it doesn't
ship.

---

## 1. The Hacker News reader (3 minutes, healthy skepticism)

**Goal:** decide whether this is worth bookmarking before
their attention moves to the next thread.

**Path:**

1. Clicks the HN link, lands on `recall.computer`.
2. **0–8s:** reads the hero headline. *"The continuity layer
   beneath your work."* Hero composition resolves (continuity
   core converges). Reads the mono trust line: `127.0.0.1:4545
   · ~/.recall · MIT`.
3. **8–25s:** scrolls past Architecture and Evolution. Notices
   the six-layer stack. Sees real endpoint names. Notices the
   transition palette is colour-coded against a real product
   shape, not decoration.
4. **25–60s:** scrolls into ContinueWorking. Sees a row
   labelled **Restored**. Sees the `Ctrl + Space` chip in the
   header. Sees the footer line: `/v1/recovery/recent ·
   /v1/threads/recent` and `12 active threads`.
5. **60–90s:** scrolls into the local-first topology card.
   Sees the loopback diagram with `bind: loopback only` mint
   indicator and the JSONL excerpt.
6. **Decision:** "Local-first. Determinism. No LLM noise.
   Code on GitHub. Worth a star."

### Where this persona breaks

- **Trust break:** any sentence that uses *"AI memory"*,
  *"intelligent recall"*, *"AI-powered"*, *"agent"*. They will
  close the tab.
- **Skepticism trigger:** anything that smells like
  cross-device sync. They will check the README for
  contradictions.
- **Confusion point:** if the hero headline doesn't tell them
  what the product IS in the first six words.

### Current status: **clean**. Vocabulary audit (Phase 3C,
Phase 4A) removed every offending term. The trust line is
visible above the fold. Two passes through the docs found no
contradictions.

---

## 2. The YC partner (45 seconds, scanning)

**Goal:** decide whether to flag this for a partner who's
interested in cognitive tools / personal infrastructure.

**Path:**

1. Lands on `recall.computer` via a referred tweet.
2. **0–5s:** hero. *"Local-first continuity operating
   system."* Mental tag: *"infrastructure category, not
   productivity-app category."*
3. **5–20s:** scrolls to Architecture. Sees the layer table.
   Mental tag: *"these are real engineering primitives, not
   marketing buckets."*
4. **20–35s:** ContinueWorking card. Sees the **Restored**
   pill, the count line *"2 tabs · 2 files · 1 chat"*.
   Mental tag: *"there's an actual product loop here."*
5. **35–45s:** scrolls past Features → LocalFirstTopology →
   FAQ. Lands on the FAQ entry *"Is Recall an AI?"* — answer
   *"No."* Mental tag: *"Differentiated. Not generic AI
   wrapper."*
6. **Decision:** flag for review. Or don't, but the surface
   never felt like a YC-shaped pitch deck, which is *good*.

### Where this persona breaks

- **Confusion point:** if the architecture section reads as
  abstract diagrams without product proof. (Mitigated by
  EvolutionTimeline + ContinueWorking sitting between
  Architecture and Features.)
- **Skepticism trigger:** if the local-first claim doesn't
  show its work. (Mitigated by the topology card + JSONL
  excerpt.)

### Current status: **clean**. The narrative arc lands the
*"systems product, not productivity app"* read in under 30
seconds.

---

## 3. The systems engineer (10 minutes, careful)

**Goal:** decide whether the engine is one they'd want to
contribute to or fork. Reads the architecture docs.

**Path:**

1. Lands on docs via the README.
2. Opens `architecture/events.mdx`. Reads the JSONL schema.
   Notes the per-day file pattern. *"Hand-editable. Good."*
3. Opens `architecture/threads.mdx`. Reads the signal table.
   *"Span / density / surface diversity / session diversity /
   recency. Closed-form weights summing to 1.0. Deterministic.
   No probabilities."*
4. Opens `architecture/recovery.mdx`. Reads the
   choreography table (files → chats → tabs → searches) and
   the deterministic preview-caption spec.
5. Opens `architecture/visual-system.mdx`. Notes the
   discipline. *"They wrote down their own tokens. Good
   sign."*
6. Opens `troubleshooting.mdx`. Reads four entries. *"Real
   diagnostic commands, no `please contact support`. Good."*
7. Opens `_smoke_api.py` in the repo. Reads section 1, 6,
   25, 28. Notes 29 sections total with budgets enforced.

### Where this persona breaks

- **Trust break:** any architecture doc that handwaves a
  signal ("we use ML to figure out..."). Every signal in the
  docs needs to be a closed-form heuristic.
- **Confusion point:** if a doc says something the smoke test
  doesn't test, or vice versa.
- **Skepticism trigger:** any TODO/FIXME left in a published
  doc.

### Current status: **clean** but standing items in
`AUDIT_REPORT.md` should be closed before public launch:
- 5 placeholder screenshots in docs (item 3.4) — addressed
  in Phase 4B by `assets/screenshots/README.md` capture
  list; gate is a real product run.
- Five live retrieval endpoints undocumented (item 3.3) —
  the FAQ + install-validation now cover them.

---

## 4. The privacy-focused developer (5 minutes, paranoid)

**Goal:** verify that "local-first" means what they think it
means. Will close the tab on the first contradiction.

**Path:**

1. Reads the hero. Trust line is `127.0.0.1:4545 · ~/.recall
   · MIT`. *Good start.*
2. Scrolls to LocalFirstTopology. Reads the three-column
   footer: `outbound: one model download on first run only`
   / `telemetry: none` / `auth: none — the bind is the
   boundary`.
3. Opens `apps/extension/manifest.json` on GitHub. Confirms
   `host_permissions` is locked to `http://127.0.0.1:4545/*`
   and nothing else.
4. Opens `docs/faq.mdx`. Reads *"Does Recall send any data
   anywhere?"* Answer: *"No."* Reads the embedding-model
   download paragraph carefully.
5. Opens `docs/architecture/events.mdx`. Confirms the JSONL
   files are at `~/.recall/events/` and inspects an example
   one in the install-validation page.
6. **Decision:** clones the repo, runs the smoke test
   locally, and checks the network panel during the demo to
   confirm zero outbound connections after the first model
   download.

### Where this persona breaks

- **Hard fail:** any docstring or page that says *"send..."*,
  *"sync..."*, *"cloud..."*, *"backend..."*, *"upload..."*
  in any non-negating context. They will assume the worst.
- **Hard fail:** any feature toggle that's "on by default"
  for telemetry/analytics. We have none and shouldn't.
- **Confusion point:** if the embedding-model download isn't
  named explicitly. (Mitigated by the FAQ entry that names
  the model and the once-per-install behavior.)

### Current status: **clean**. The most pedantic privacy
audit finds the loopback bind, the host_permissions lock,
the local_files_only embedder, and the JSONL store all
matching their docs.

---

## 5. The productivity-tool enthusiast (3 minutes, looking for "their next app")

**Goal:** decide whether Recall fits in their daily workflow
alongside Notion / Obsidian / Raycast.

**Path:**

1. Lands on the hero. Headline + body copy land them in
   "this is for me" territory: *captures what you touched ·
   reconstructs threads of thought · one click brings the
   work back*.
2. Scrolls into ContinueWorking. Sees the keyboard hint
   chip. **Captures their interest.** *"I can just press
   Ctrl+Space?"*
3. Scrolls to Features. Reads the six cards. Mental tags:
   "Continuity search ✓, sessions and micro-contexts ✓,
   threads + evolution ✓". They've used adjacent tools so
   the vocabulary lands.
4. Scrolls to FAQ. Reads *"Does it have accounts? Sync?"* —
   answer is *"No."* They feel a small tension here.
5. Reads the next FAQ entry: *"Can I use Recall on multiple
   machines?"* — explanation lands honestly.
6. **Decision:** install on one laptop. Decide later if
   they want to install on both.

### Where this persona breaks

- **Soft friction:** the "no sync" decision is a real
  tradeoff for this persona. The FAQ entry needs to be both
  honest and reassuring. (Mitigated by framing: *"a
  continuity layer for your own thinking is only useful if
  it stays on the machine."*)
- **Confusion point:** if Recall reads as overlapping with
  their existing notes tool. (Mitigated by EvolutionTimeline
  + ContinueWorking showing a *workflow* shape Notion /
  Obsidian don't offer.)

### Current status: **clean** with one soft note: the
single-machine constraint will lose this persona to *some*
fraction of competitors that offer cross-device sync. That
is the right tradeoff for the product's thesis, and the FAQ
is written to defend it without apologising.

---

## Cross-persona findings

| Finding | Status |
|---|---|
| AI-language audit clean across landing + docs | ✓ (Phase 3C + 4A) |
| Trust-line above the fold | ✓ |
| Architecture story before product features | ✓ (page narrative: Hero → Architecture → Evolution → ContinueWorking → Features → LocalFirstTopology → FAQ) |
| FAQ answers the five hardest questions a sceptic asks | ✓ |
| Real endpoint names in marketing surfaces | ✓ (Phase 3C added `/v1/recovery/recent` to ContinueWorking footer) |
| Real screenshots in docs | ✗ — deferred, see `assets/screenshots/README.md` |
| Demo video | ✗ — script ready (`assets/demos/demo-script.md`), capture deferred |
| Issue labels + good-first-issues | ✗ — covered by `CONTRIBUTING.md` text, GitHub-side setup deferred to public launch |

## What the audit changed in this pass

- **None of the personas above tripped on a vocabulary
  break.** The vocabulary audit from Phase 3C onward held
  up to the simulation.
- The single soft friction is the cross-device tradeoff for
  Persona 5. The FAQ entry was already calibrated; no copy
  change is needed.
- The two open `AUDIT_REPORT.md` items that this audit
  surfaces (screenshots, demo video) were already named
  deferrals in `PHASE_4A_STATUS.md`. The gate conditions
  (a maintainer running the launcher and capturing) are
  unchanged.

## Re-running the audit

When a meaningful copy or surface change lands, the
maintainer should re-walk this document mentally:

1. Read each persona's "Path" section as if they were doing
   it right now on the current state of the site.
2. Check the "Where this persona breaks" list against the
   change.
3. If any break fires, the change is incomplete.

The audit is a tool, not a ceremony. The personas are
representative but not exhaustive — if a real reader
surfaces a sixth persona's break, add the row.
