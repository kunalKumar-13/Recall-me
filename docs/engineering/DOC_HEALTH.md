# DOC_HEALTH.md — documentation system metrics

Measured at the close of Phase 5D.1 (the documentation
consolidation). One page, real numbers, no rounding up. Tracked so
a future hygiene pass can see whether the system is growing
healthily or sprawling again.

Pairs with [`../DOC_INDEX.md`](../DOC_INDEX.md) (the full doc
roster) and [`REPO_HEALTH.md`](REPO_HEALTH.md) (the code-side
counterpart).

---

## Headline metrics

| Metric | Before 5D.1 | After 5D.1 |
|---|---|---|
| `.md` files at repo root | **45** | **5** (`README`, `CLAUDE`, `CONTRIBUTING`, `SECURITY`, `CODE_OF_CONDUCT`) |
| `.md` files under `docs/` | 0 | **42** (40 moved + `DOC_INDEX.md` + this file) |
| Docs archived under `docs/archive/old-docs/` | — | **1** (`PHASE_4A_STATUS.md`) |
| Cross-reference broken links across the repo | unmeasured | **0** — verified end-to-end |
| Orphan docs (in `docs/` but not linked from any live doc) | — | see audit below |
| Top-level dirs at repo root | 12 | 12 (no churn — `docs/` already counted) |

## Folder distribution

| Folder | Docs | What lives here |
|---|---|---|
| `docs/product/` | 6 | what Recall *is*, in user words |
| `docs/founder/` | 9 | running the project (phase, roadmap, users) |
| `docs/engineering/` | 11 | how it works technically (perf, stability, audits) |
| `docs/release/` | 9 | what ships when (changelog, install, gates) |
| `docs/trust/` | 5 | keeping the surfaces honest (fixtures + validations) |
| `docs/archive/old-docs/` | 1 | preserved-but-frozen |
| `docs/` (root index) | 1 | `DOC_INDEX.md` |
| **total** | **42** | |

## How the link-health number was produced

Every `.md` and `.mdx` link target across the repo was resolved
against the filesystem (skipping `node_modules`, `.next`, `venv`,
`build`, `dist`, `.git`). The same script is checked in as the
audit recipe in [`DEAD_CODE_AUDIT.md`](DEAD_CODE_AUDIT.md):

```python
import re, pathlib
link_re = re.compile(r'!?\[[^\]]*\]\(([^)]+)\)')
broken = []
for p in pathlib.Path('.').rglob('*.md'):
    if any(x in p.parts for x in ('node_modules','.next','venv','.venv','build','dist','.git')):
        continue
    for m in link_re.finditer(p.read_text(encoding='utf-8', errors='replace')):
        t = m.group(1).split('#')[0].split('?')[0]
        if not t or t.startswith(('http','mailto:','#')): continue
        if not t.endswith(('.md','.mdx')): continue
        if not (p.parent / t).resolve().exists():
            broken.append((str(p), m.group(1)))
print(broken)
```

Result at the close of Phase 5D.1: `[]` — zero entries.

## Orphan check

A doc is *orphan* if no other live doc links to it. After the
consolidation:

| Doc | Status |
|---|---|
| every doc in `docs/{product,founder,engineering,release,trust}/` | linked from at least one of `/README.md`, `/CLAUDE.md`, `DOC_INDEX.md`, or another live doc |
| `docs/archive/old-docs/PHASE_4A_STATUS.md` | intentionally archived; not linked from live docs |
| `docs/DOC_INDEX.md` | linked from `/README.md`, `/CLAUDE.md`, and this file |

No live orphans — every doc in `docs/` is reachable from the front
door in at most two hops.

## What changed in Phase 5D.1

| Action | Volume |
|---|---|
| Root `.md` files moved into `docs/<area>/` | 40 |
| Cross-references rewritten inside moved docs | 35 |
| Cross-references fixed outside `docs/` (the README/CLAUDE pair, `.github/*.md`, `releases/*.md`, `infra/**/README.md`, `apps/admin/*.md`, `assets/screenshots/README.md`, the capture-pipeline README, `apps/desktop/README.md`) | 15 |
| Stragglers fixed by hand | 4 (archive READMEs + 3 in the archived `PHASE_4A_STATUS.md`) |
| Broken links remaining | **0** |
| Behaviour changes | **0** — pure file moves + link rewrites |

The web build was not affected (no `.md` references in
`apps/web/`); the smoke test was not affected (it never reads
docs). The consolidation is a docs-only operation by construction.

## Tracked over time

| Date | Root `.md` | `docs/` `.md` | Archived | Broken |
|---|---|---|---|---|
| Pre-5D.1 | 45 | 0 | 0 | unmeasured |
| 2026-05-20 (5D.1) | 5 | 42 | 1 | 0 |

Update by running the broken-link script above, plus:

```bash
ls *.md | wc -l                    # root .md count
find docs -name "*.md" | wc -l     # docs/ .md count
find docs/archive -name "*.md" | wc -l   # archived .md count
```

## The hygiene rule going forward

A new `.md` lands in `docs/<area>/`, never at the repo root, unless
it is one of the five whitelisted root files. Adding a doc means
adding a row to [`../DOC_INDEX.md`](../DOC_INDEX.md) in the same
PR — otherwise it is, by definition, an orphan.
