# PUBLIC_ALPHA.md — public alpha readiness

The single page a first public-alpha user (and the maintainer
shipping to them) reads. It is the *path*, end to end: install →
first use → trust → uninstall, plus what is honestly not done yet.

It links the deep docs rather than repeating them.

---

## What Recall is (one paragraph)

Recall is a **local-first continuity operating system**. You get
interrupted; the climb back — scattered tabs, the wrong files, a
lost line of thinking — costs more than the interruption did. Recall
captures what you touched and, when you come back, offers the one
investigation you can step straight into. Everything stays on your
machine. No cloud, no telemetry, no account.

---

## 1. Install path

The fast path is [`apps/docs/install-3min.mdx`](../../apps/docs/install-3min.mdx)
— a working launcher in five commands for a technical user.

Outcome to expect: a tray icon, a launcher on **Ctrl + Space**, and
an empty first-run state that reads *"Recall is ready. Work a
little, then come back later."* — not an error, not a blank box.

## 2. First-use path

1. On first launch, onboarding asks for folders to remember
   (Documents and Desktop are pre-checked). Pick at least one.
2. The launcher opens empty. This is correct — there is nothing to
   continue yet.
3. **Work normally for a day or two.** Recall captures in the
   background. Do not expect recovery cards immediately; continuity
   is earned from real activity.
4. Come back. Open the launcher with an empty query. When a real
   interrupted investigation exists, *Continue where you left off*
   shows it.

The five-persona walkthrough of this journey, with the friction
points and fixes, is [`FIRST_USE_AUDIT.md`](FIRST_USE_AUDIT.md).

## 3. Extension setup

The browser extension feeds tabs, searches, and chats into the same
daemon. Build and load it per
[`apps/extension/README.md`](../../apps/extension/README.md):
`cd apps/extension/ui && npm install && npm run build`, then
**Load unpacked** → `apps/extension/`.

Outcome to expect: the toolbar popup shows *Daemon connected* and,
once you have activity, a *Continue* card mirroring the launcher.

## 4. Expected behavior

| You do | Recall does |
|---|---|
| Install, pick folders | indexes them quietly; launcher stays calm |
| Work for 1–2 days | captures events; investigations begin to form |
| Get interrupted mid-task | nothing visible — capture is silent |
| Return, open launcher | offers **one** strong recovery, if one is real |
| Nothing real to recover | says so plainly; shows no fabricated card |

The calibration for "real" vs "noise" is
[`TRUST_FIXTURES.md`](../trust/TRUST_FIXTURES.md) and
[`TRUST_FIXTURES_CONTINUITY.md`](../trust/TRUST_FIXTURES_CONTINUITY.md).

## 5. Trust checks

A user should be able to verify every privacy claim themselves:

- **It is local.** `~/.recall/` holds plain JSON + JSONL. Open it
  with any editor. The only network call ever made is the one-time
  embedding-model download on first run.
- **The bind is the boundary.** The API listens on `127.0.0.1:4545`
  only. The extension's `host_permissions` is exactly that URL.
- **Delete = full reset.** Removing `~/.recall/` removes everything
  Recall knows.
- **It explains itself.** `RECALL_DEBUG=1` and
  `RECALL_EXPLAIN_RECOVERY=1` surface *why* anything was shown.

## 6. Uninstall

A clean, one-minute removal that leaves zero residue is documented
step by step in [`apps/docs/uninstall.mdx`](../../apps/docs/uninstall.mdx).
Recall is safe to try precisely because it is trivial to remove.

## 7. Known limitations (honest list)

The alpha is functional and stable; these are the rough edges:

- **Screenshots in the docs are placeholders.** The deterministic
  capture pipeline is specified but not yet run — see Phase 4J
  notes in [`CHANGELOG.md`](../release/CHANGELOG.md).
- **The launcher digest** is the proven multi-section layout, not
  yet the row-card redesign (RecoveryCard / ThreadCard / …). It is
  calm and correct; it is not the final visual.
- **No demo video** yet (script: `assets/demos/demo-script.md`).
- **The Windows installer is unsigned** — see
  [`RELEASE.md`](../release/RELEASE.md). Expect a SmartScreen prompt.
- **Recovery biases toward silence.** A missed recovery is by
  design preferable to a weak one — early on you may see *nothing*,
  and that is correct, not broken.

## 8. The alpha milestone

Success is one sentence, from a real user:

> They install Recall. They work for two days. They come back, open
> the launcher, get one recovery, and say: *"Wait — it remembered
> that?"*

Everything in this repo is in service of that sentence.
