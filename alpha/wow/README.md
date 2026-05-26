# alpha/wow — verbatim quotes only

When Recall does something *right* — surprisingly,
usefully — paste the quote here.

**Rules:**

1. **Verbatim.** The exact words you would say
   (or did say). No paraphrase. No "the user
   reported that…" framing.
2. **One file per quote.** Filename is
   `YYYY-MM-DD-<short-slug>.md`.
3. **No PII.** No real names, no employer names,
   no project names that identify you. Handles
   (`alpha-001`) are fine; "Maria from Acme"
   is not.
4. **Two-line frontmatter, then the quote.**
   See [`TEMPLATE.md`](TEMPLATE.md).

The `recall alpha review` CLI counts every
`.md` file in this folder (except `README.md`
and `TEMPLATE.md`) as one wow incident.

## What counts as a wow

The product did something you didn't *quite*
expect, and it was useful. Examples (real
shapes, not collected):

> "Closed laptop Friday. Hit Alt+Space Monday
> morning. The four tabs and one local file I
> needed for the bug I was mid-thread on — all
> in one card. I clicked once."

> "I opened the launcher to search for something
> unrelated. The digest showed me a thread I'd
> abandoned two weeks ago. Picked it back up
> the same day."

> "It surfaced a Continue card for a proposal I
> had forgotten was a proposal. Saved me the
> *'wait, what was I writing again'* tax."

What does NOT count:

- "It indexed my files quickly." — that's
  performance, not surprise.
- "The UI is pretty." — that's aesthetics.
- "I love the privacy story." — that's a
  promise we already made.

The wow is about **a moment of recognition** —
the product anticipated something you would
otherwise have spent five minutes reconstructing.

## Why we save them

Three reasons:

1. **They are the success metric.** RC1 ships if
   anyone in the cohort has a real wow. Without
   one, we have a calmly-presented logger.
2. **They are the marketing.** Verbatim cohort
   quotes carry more weight than any tagline
   we'd write. The landing page's eventual
   testimonials come from this folder.
3. **They calibrate the engine.** A wow tells
   us what the recovery engine got *right* —
   useful data for tightening the trust gate.

## Anonymisation

If you write a quote you want to share publicly:

- Strip employer names ("the Acme bug" → "the
  bug")
- Strip teammates' names ("Maria's PR" → "a
  teammate's PR")
- Strip project codenames ("Project Phoenix
  proposal" → "the proposal")

Recall is meant to know what you were working on
without telling anyone else.

## Existing quotes

None yet. The 8E cohort is the founder + 4 open
seats. The first wow is the gate to scale.
