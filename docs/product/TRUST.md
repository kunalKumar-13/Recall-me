# TRUST.md — the public trust statement

The five rules Recall makes to every person who installs it. They
appear on the marketing site
([`Privacy` section](../../apps/web/app/components/Privacy.tsx))
verbatim; this file is the more detailed version, with the
on-disk contract that backs each rule.

Pairs with the engineering boundary doc
[`TRUST_LEDGER.md`](../engineering/TRUST_LEDGER.md). The
difference: that one is *what an engineer needs to know*; this
one is *what a tester needs to know*.

---

## The five rules

### 1. Local only

Every capture, every reconstruction, every recovery decision
happens on this device. No remote service holds your data, ever,
in any form. There is no "anonymous version" of your work that
lives somewhere else.

**On-disk contract**

- Capture writes to `~/.recall/events/YYYY-MM-DD.jsonl`.
- Indexes write to `~/.recall/chroma/`.
- The HTTP service binds to `127.0.0.1:4545` only. The bind is
  the boundary; remote callers cannot physically reach it.

### 2. No cloud

Recall never syncs your data, never backs it up, never offers a
"sign in and pick up where you left off" cross-device path. If
you lose the laptop, you lose the cache — that is by design.

**On-disk contract**

- There is **no** account.
- There is **no** sync engine.
- There is **no** backup-to-cloud feature.
- The *one* outbound network call Recall makes is the embedding-
  model download on first run — and that is documented openly in
  [`STABILITY.md`](../engineering/STABILITY.md) § *Outbound
  network*.

### 3. No telemetry

Zero tracking. Zero analytics. Zero usage pings — including
"anonymous" or "aggregate" ones. The product knows nothing about
you between sessions on different machines.

**On-disk contract**

- ChromaDB telemetry: explicitly disabled at boot
  (`anonymized_telemetry=False`).
- Hugging Face telemetry: explicitly disabled at boot
  (`HF_HUB_DISABLE_TELEMETRY=1`).
- There is **no** error reporting service. A crash logs to
  `~/.recall/recall.log` and nowhere else.
- There is **no** update server pinging *you*; you check the
  GitHub releases page yourself, when you choose to.

### 4. Counts only

If you ever choose to share anything with us — to help the
alpha-001 cohort, for example — what you share is **counts**.
Number of recoveries shown. Number you accepted. Number that
fired on a return after a 30-minute gap. Never URLs. Never
filenames. Never queries. Never chat content.

**On-disk contract**

- `recall stats --export` produces a redacted JSON file with
  counts only. Inspect it before you send.
- `~/.recall/daily_loop.jsonl` is the source — also counts only,
  one JSON line per local day, human-readable.
- `alpha/recovery_journal.json` (cohort-side, in the repo) is
  hand-edited by the founder. Per-row `investigation` is the
  launcher *title only* — never the underlying URLs / files.

### 5. Export only

The data is yours, on your machine, in plain text. You can take
it anywhere. You can delete it anywhere. Recall has no claim on
it.

**On-disk contract**

- Every artifact on disk is JSON or JSONL — `cat`-able,
  hand-editable.
- Deleting `~/.recall/` is a full reset — no shadow state on
  the OS, no registry crumbs (Windows installer cleans up on
  uninstall, per
  [`docs/trust/CLEAN_MACHINE_RUN.md`](../trust/CLEAN_MACHINE_RUN.md)).
- The codebase is MIT-licensed
  ([`LICENSE`](../../LICENSE)). You can fork the engine, audit
  the on-disk format, run it yourself.

---

## What Recall WILL ask for, and what it won't

| Will ask for | Won't ask for |
|---|---|
| Permission to read folders you point it at | Your email |
| Permission to install a Chrome / Edge extension | Your name |
| A founder-assigned tester handle (cohort-only) | Telemetry opt-in |
| A weekly cohort form (alpha-001 only, optional) | Cloud sync opt-in |

The cohort form is the *only* moment a tester shares anything
with the founder. The form ships in
[`alpha/ALPHA_FEEDBACK_V2.md`](../../alpha/ALPHA_FEEDBACK_V2.md);
nothing in it asks for content. The founder redacts before
saving.

---

## What happens if I uninstall

- Windows: the Inno Setup uninstaller removes
  `Program Files\Recall\`. `~/.recall/` stays (your data is
  yours; we don't auto-delete it). Delete it manually for a
  full wipe.
- macOS preview: drag `Recall.app` to Trash. Same `~/.recall/`
  rule.
- The browser extension: uninstall via the extension page in
  your browser. Capture stops the moment the extension is gone.

---

## Where the rules are enforced

The five rules above are not aspirational — they live in the
code as testable invariants:

- **`api/main.py`** binds to `127.0.0.1` (rule 1).
- **`app/core/config.py`** disables Chroma + HF telemetry at
  module load (rule 3).
- **`app/core/stats.py`** is the only path that produces an
  exportable JSON; its schema is counts-only (rule 4).
- **`alpha/users/README.md`** carries the grep-enforceable
  no-content invariants (rule 4 again, for the cohort side).
- **`docs/engineering/TRUST_LEDGER.md`** is the master document
  every engineering surface refers back to.

If you find any path that contradicts one of these rules,
open an issue with the title prefix `[TRUST]`. It will be
treated as the highest-priority class of bug.
