# First-use audit — the five-minute post-install journey

This document is the companion to
[`FIRST_IMPRESSION_AUDIT.md`](FIRST_IMPRESSION_AUDIT.md). The
first-impression audit simulates five personas evaluating the
landing page and deciding whether to install. This audit picks
up after install — what happens in the first five minutes a
real user spends with the launcher running.

The goal is the brief's stated outcome for Phase 4D:

> *"I installed this for curiosity. I kept it because it
> reduced cognitive restart friction."*

If a persona below uninstalls within five minutes, we have a
trust break to fix. Each section names the moment of trust,
the moment of doubt, and the concrete fix.

The audit is **deliberately critical** — the personas voice the
sharpest skepticism a real user of that archetype would carry.
If a fix below already shipped in an earlier phase, the row
notes the resolved status; everything else is an open item
that flows into [`AUDIT_REPORT.md`](../engineering/AUDIT_REPORT.md).

---

## Persona 1 — *The systems engineer*

**Profile.** Senior infra eng, runs Linux at home, prefers
tools they can read in an afternoon. Found Recall via Hacker
News. Installed from source.

### First five minutes

1. `git clone` → `./infra/scripts/dev.sh` → smoke runs → launcher pops up. ✓
2. `Ctrl + Space` → empty digest with the "Recall is ready" copy. ✓
3. `Ctrl + ,` → Settings opens. *"What's all this?"* — they
   want to know what each toggle does **before** flipping it.

### Trust moments

- The boot trace lines (`>> initialize event logger` etc.)
  read like an old SysV init log. Trust earned.
- The first-week hint copy ("Capture builds quietly…") tells
  them something *real* about the engine's behavior. Trust
  earned.

### Doubt moments

- The Settings dialog has four sections: Episodic Memory,
  Browser Memory, Resurfacing, Memory Threads. Each has its
  own toggle. **No "what does this collect?" link per
  section.** A privacy-aware user wants to see the on-disk
  shape of each before enabling it.
- The "Browser Memory" section asks for the extension
  install. The user has not installed it. There's no "Install
  the extension first" hint above the section — it just
  silently does nothing.

### Fixes

| Friction | Fix | Status |
|---|---|---|
| Settings sections lack a "see what this captures" link | Add a small mono `~/.recall/events/*.jsonl` link in each section that opens the events folder in Explorer/Finder | **Open** — small Settings change |
| Browser Memory section silent on extension status | Add a status line above the toggle: *"Extension not yet installed — see Install steps"* with link to docs | **Open** |
| `~/.recall/version.json` not mentioned anywhere visible | Settings → About should print version + channel + smoke-test-passed-at | **Open** |

---

## Persona 2 — *The privacy-conscious developer*

**Profile.** Writes auth services for a living. Mistrusts
anything that asks for filesystem access. Found Recall via a
friend's recommendation, came skeptical.

### First five minutes

1. Reads the README's *Why this matters* before installing. ✓
   The three honest claims pass their sniff test.
2. Installs from source. Runs smoke. Notices the `[OK] start
   local memory API · 127.0.0.1:4545` line. *"Bound to
   loopback. Good."*
3. Opens Settings. Pauses on *Browser Memory*. Their first
   action is to add `mail.google.com`, `accounts.*`, and
   `bank.com` to the **Domains never captured** list before
   ever installing the extension.

### Trust moments

- The Settings → Browser Memory section has a "Domains never
  captured" list and the extension popup confirms
  *server-side rejection*. Verifies on the extension popup
  that visits to those domains don't increment `captured`. ✓
- `cat ~/.recall/events/2026-05-15.jsonl` shows exactly the
  events they expected. Trust massively earned.

### Doubt moments

- No mention of **uninstall** anywhere they look. They want
  to know they can leave with zero residue before they fully
  commit.
- *What about the embedding model download?* The first-run
  download isn't named anywhere they can find before it
  happens. They check Wireshark; the connection goes to
  `huggingface.co`. They're satisfied, but they had to verify
  externally rather than from the docs.

### Fixes

| Friction | Fix | Status |
|---|---|---|
| No uninstall doc | Add `apps/docs/uninstall.mdx` covering: stop the process, remove `~/.recall/`, uninstall the extension, optionally delete the cloned repo | **[FIXED]** — this phase |
| Embedding-model download not surfaced before it happens | The `apps/docs/install-3min.mdx` doc mentions it under *Prerequisites* but the `--debug` boot trace doesn't print the URL. Add `[boot] downloading all-MiniLM-L6-v2 from huggingface.co …` to the first-run path | **Open** — small launcher change |
| Domains-blocklist defaults | Default blocklist could include `mail.*`, `accounts.*`, `*.bank.com` patterns on first run. Currently empty. Tension: defaults are paternalistic. Recommend: not changing, but adding a *"Suggested patterns"* helper next to the Add button | **Open** — Settings UX, low priority |

---

## Persona 3 — *The researcher*

**Profile.** Reads 10 arxiv papers a week, has 60 Chrome tabs
open at any moment, lost a chat with Claude about a paper
last Tuesday and is *still* trying to find it. Closest user to
the brief's intended audience.

### First five minutes

1. Installs from a downloaded binary (future state) or
   `./infra/scripts/dev.sh` (today).
2. Installs the extension. Realises page captures are
   happening. Surveys a few papers.
3. Closes the laptop. Comes back the next day. Opens
   Ctrl+Space with an empty query.

### Trust moments

- The next-day digest shows *Lately you searched* with their
  recent queries. They didn't ask Recall to track those — it
  already had them. Trust earned through *demonstrated
  capture* rather than *promised capture*.
- Two days later, *Active memory threads* surfaces the topic
  they've been picking at. Trust massively earned.

### Doubt moments

- The first *Continue where you left off* card appears on day
  three. They want it earlier — on day one if possible.
- The recovery card opens five Chrome tabs at once. **Chrome
  briefly stalls.** They worry that Recall has just thrashed
  their browser.

### Fixes

| Friction | Fix | Status |
|---|---|---|
| Recovery doesn't surface until day three | This is by design — the engine refuses to surface unverified work. Document the tradeoff prominently: *"a quiet first 48 hours is the cost of never seeing fabricated cards"* | **[FIXED]** — already covered in the FAQ and the launcher's "first-week hint" copy; could be more visible in onboarding |
| Five-tab restoration stalls Chrome | The restoration handler should pace browser opens by ~80 ms between targets, OR open them with `--new-window` so Chrome batches them | **Open** — small launcher change in `_on_recovery_restore` |
| Restoration footer doesn't say *what's opening* during the open | Footer flash already shows the count + caption; could *show each target name* as it opens | **Open** — low priority, may add noise |

---

## Persona 4 — *The founder*

**Profile.** Three-week-old startup. Pitch deck, market
sizing, three Claude chats deep on go-to-market, no time. Saw
Recall on Twitter and installed because the demo GIF (when it
exists) showed *"the healthcare-startup thread"* and felt
recognised.

### First five minutes

1. Installs in two minutes. Doesn't read the docs. Doesn't
   install the extension yet.
2. Skips Settings entirely. Opens Ctrl + Space.
3. Empty digest. *"Where's the magic?"*

### Trust moments

- The launcher's idle hint ("Capture builds quietly…") tells
  them why the digest is empty without making them feel like
  they did something wrong. Trust *salvaged*.
- The next day, after browsing for an hour, the digest has
  three rows. They click one. Their pitch deck PDF opens.
  Their notes.md opens. The Claude chat opens.
- They sit back. *"Oh."*

### Doubt moments

- They never installed the extension. After three days they
  notice all the digest activity is from file opens; their
  browser is invisible. They go looking for the extension
  install step. **It's two clicks deep in Settings.**
- The recovery card title is *"pitch_deck_v3.pdf"* —
  technically correct but emotionally flat. They'd love it to
  read *"Your healthcare-startup thread"*.

### Fixes

| Friction | Fix | Status |
|---|---|---|
| Extension install is hidden in Settings | First-week hint should say: *"Install the browser extension to capture browsing"* with a one-click link | **Open** — small launcher copy change |
| Recovery title is filename-shaped not human-shaped | The thread title derivation already prefers the most-common substantive title across events. For threads where the only signal is filenames, derive from folder + content keywords. Tradeoff: deterministic vs friendly | **Open** — needs careful determinism-preserving design |
| Onboarding doesn't show example use cases | The introduction.mdx should list the *kind* of thread the user might form ("a healthcare startup thread", "a debugging session", "a paper-reading arc") — same examples the demo seeder uses | **Open** — doc update |

---

## Persona 5 — *The productivity skeptic*

**Profile.** Installs ten "memory" / "knowledge" / "second
brain" tools per year. Uninstalls nine of them in the first
week because each demands daily curation effort. Skeptical
that Recall isn't another one.

### First five minutes

1. Reads the README's *"Why this matters"* section. Sees the
   third honest claim: *"Same events in → same outputs out."*
   Decides to give it ten minutes.
2. Installs. No tags to create. No folders to organise. No
   notebooks. No daily review prompts. *"Wait, that's it?"*
3. Looks for the inevitable "create a daily journal" prompt.
   Doesn't find one.

### Trust moments

- No setup ceremony. No "create your first note." No
  "configure your daily review." Recall just... runs.
- After a week of use, they realise the launcher hasn't asked
  them to do anything beyond "press Ctrl + Space when you
  want to find something." Trust earned through *absence*
  rather than *presence*.

### Doubt moments

- *"What's the catch?"* They keep waiting for the upgrade
  prompt. The premium tier email. The "share your second
  brain" feature. None arrive.
- After a month, they want to see *what they've forgotten*.
  Recall's surfacing surfaces *what they're returning to*,
  not *what they've abandoned*. They want a separate "your
  archived threads" view. The brief explicitly excludes this
  (it would become a dashboard). The skeptic sighs but trusts
  the restraint.

### Fixes

| Friction | Fix | Status |
|---|---|---|
| Looking for "the catch" | The README should make the *"this is the catch"* explicit: *"There is no premium tier. There is no team plan. There is no upgrade prompt. The MIT licence is the offer."* | **[FIXED]** — README's *Final CTA* and the *No accounts* framing carry this | 
| Wants an "abandoned threads" view | Brief explicitly excludes dashboards. Document the *why* in the FAQ: continuity is forward-facing; archival is its own product | **Open** — FAQ entry |
| No way to tell Recall *"I'm done with this thread, archive it"* | The "muted" flag on threads already exists internally. Could surface as a *Hide this thread* action on the row. Adding requires care: muting is silent (the row just disappears), not a feature to celebrate | **Open** — small Settings + row affordance |

---

## Recurring observations

Across the five personas, three patterns recur and represent
the highest-leverage Phase 4D items:

### 1. The first-week silence is a trust gate

Every persona spends day one wondering whether the engine is
working. The first-week hint copy (added in Phase 4A) helps,
but isn't visible enough. **Recommendation:** the launcher's
empty-state copy should explicitly name *when* the digest
expects to start populating ("usually within 24 hours of
normal browsing").

### 2. The extension is the hidden critical path

Every persona either delayed installing the extension or
forgot it entirely. The single most impactful UX fix for new
users is making the extension install a **first-class step in
the onboarding sequence**, not a Settings-deep affordance.

### 3. Restoration is the wow moment, but it has rough edges

Personas 3 and 4 reach the "oh" moment through restoration,
but the simultaneous five-tab open is jarring on slow
browsers. Pacing the orchestration plan by 80 ms per step is
the cheapest fix and preserves the deterministic-plan
contract.

---

## How to re-run this audit

This document should be re-walked any time a user-facing
surface changes — Settings copy, launcher row treatment,
boot-trace lines, README opening. The structure:

1. For each persona, do the *first five minutes* journey
   from the perspective of that archetype.
2. Note **one trust moment** and **one doubt moment** per
   persona.
3. Convert each doubt moment into a concrete fix with a
   status. Each fix either lands this cycle (**[FIXED]**) or
   flows into [`AUDIT_REPORT.md`](../engineering/AUDIT_REPORT.md) as an
   open item.

The audit is honest only if it stays critical. A persona who
never disagrees with the product is not auditing — they're
endorsing.
