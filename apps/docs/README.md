# Recall — documentation

Mintlify-based docs for the Recall local-first memory layer.

Everything in this folder is deploy-ready. Mintlify reads `mint.json`
at the root of this directory; every `.mdx` file referenced in the
`navigation` array of that config becomes a page.

## Local preview

```bash
# one-time
npm install -g mintlify

# in this directory
mintlify dev
```

The dev server runs on `http://localhost:3000` with hot reload.

## Deploy

The fastest path is the Mintlify cloud:

1. Sign in at <https://mintlify.com>.
2. Connect this repo (or just this `/docs` subdirectory).
3. Mintlify auto-deploys on push and gives you a `*.mintlify.app`
   subdomain you can map to a custom domain.

For self-hosting see the Mintlify docs at
<https://mintlify.com/docs/self-host>.

## Folder layout

```
docs/
├── mint.json                      # site config — colours, nav, search
├── favicon.svg
├── logo/                          # light + dark wordmark
├── images/                        # screenshots referenced by pages
├── introduction.mdx               # "why Recall exists"
├── self-hosting.mdx
├── roadmap.mdx
├── philosophy/
│   ├── local-first.mdx
│   └── episodic-memory.mdx
├── architecture/
│   ├── events.mdx
│   ├── sessions.mdx
│   ├── micro-contexts.mdx
│   └── retrieval-pipeline.mdx
├── features/
│   ├── browser-memory.mdx
│   ├── resume-context.mdx
│   └── privacy.mdx
├── api/
│   ├── introduction.mdx
│   ├── events.mdx
│   └── search.mdx
├── sdk/
│   └── introduction.mdx
└── extensions/
    └── chrome-extension.mdx
```

## Screenshots

The `/images` directory holds PNG screenshots referenced from
several pages. The repository ships with placeholder filenames so
the pages render even when no real screenshots exist yet — replace
them with actual captures from the launcher when ready:

| File | Used by |
|---|---|
| `images/launcher-results.png` | `architecture/retrieval-pipeline.mdx`, `features/browser-memory.mdx` |
| `images/launcher-session.png` | `architecture/sessions.mdx` |
| `images/launcher-context.png` | `architecture/micro-contexts.mdx` |
| `images/launcher-digest.png`  | `introduction.mdx`, `features/resume-context.mdx` |
| `images/settings-browser.png` | `features/browser-memory.mdx`, `features/privacy.mdx` |

PNGs around 1600px wide at 2× render cleanly in both light and
dark themes.

## Editorial tone

- Calm. Infrastructure-grade. Technical.
- No "AI-powered", no "next-generation", no exclamation marks.
- Code blocks are plain. Mermaid diagrams describe shapes, not
  marketing flows.
- If a sentence reads like a product brochure, it gets rewritten.
