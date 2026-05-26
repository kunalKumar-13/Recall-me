# Day 1 — the real test

Yesterday you installed and browsed. Today is
the first time the product can show you what it
actually does.

**Goal for today:** open the launcher *once* —
on purpose — when you sit down. See what's
there. Decide if it knows you.

---

## The exact ritual

1. Open your laptop.
2. **Before** you open your browser, your IDE,
   or your email — press **Alt+Space**.

That's it. That's the moment.

---

## What you should see

One of three things:

### A. A Continue card at the top

Headline like *"Continue: WebSocket retry"* with
a count like *"5 tabs · 2 files"*. One click
reopens those tabs and files.

**If you see this:** that's the wow moment.
Click it. See if the right tabs come up. Write
down what happened in [FEEDBACK.md](FEEDBACK.md)
— verbatim, no paraphrase. We collect these in
`alpha/wow/` and they're how we decide RC1 was
worth shipping.

### B. A populated digest, no Continue card

Headline says *"On your radar"* with 3-5 recent
memories and 1-3 investigation threads. No
Continue card means yesterday's activity didn't
cross the recovery trust gate — usually because
no single topic hit ≥4 events with a recent
"interrupted" signal.

**If you see this:** that's also fine. The
product is being honest — it had nothing
confident to offer. Skim the digest. Recognise
anything?

### C. Empty state

A single line of copy. No data.

**If you see this:** either yesterday's capture
didn't fire, or the daemon was off. Run:

```
python recall.py capture status
```

If events_today is zero, the extension lost its
pairing. Reload it from `chrome://extensions` and
file a quick note in
[`../failures/`](../failures/README.md).

---

## What "knowing you" should feel like

The product is good if the digest reads like
*"yes, that's what I was doing."* Not *"how
clever, it indexed everything."* The right
emotion is **recognition**, not **surprise**.

The product is wrong if:

- The Continue card points at the wrong work
  ("I wasn't doing that yesterday")
- Investigation threads merge unrelated topics
- The recent memories are dominated by passive
  browsing (banking, streaming, etc.) instead
  of the thing you were actually working on

**Either way, write it down.** A failure is just
as useful as a wow — see
[`../failures/`](../failures/README.md) for the
template.

---

## What to try mid-day

Some time later, after you've worked for a few
hours, **open the launcher again**.

- Did the digest update?
- Did a Continue card appear that wasn't there
  this morning?
- Did anything you closed yesterday come back
  into view?

This is the second-order question — Recall as a
*live* surface, not just a return-from-sleep one.

---

## What NOT to do

- Don't sit and watch the launcher refresh. It
  doesn't auto-refresh visibly. Open it, look,
  close it.
- Don't search for keywords as a way to test it.
  That's a different product. The launcher's
  job is the **digest**, not search.
- Don't compare it to Rewind or Recall.ai. They
  capture screen contents. This captures
  *intent* (URLs, files, sessions).

---

## What to write down

After your second open, take 60 seconds and
answer:

1. What did the launcher show you?
2. Was it right? Was it useful?
3. What did you expect that wasn't there?
4. Did anything feel slow or weird?

Drop your answer into
[FEEDBACK.md](FEEDBACK.md). Don't worry about
form. We want raw.

---

## What you do next

| When         | Open                          |
|--------------|-------------------------------|
| Tomorrow     | Just keep using it. No ritual. |
| 3 days in    | [DAY3.md](DAY3.md)            |
| Found a bug  | [`../failures/`](../failures/README.md) |
| Found a wow  | [`../wow/`](../wow/README.md) |
