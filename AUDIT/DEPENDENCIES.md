# Dependency Audit — Phase 8A

Every dependency declared across the Recall repo, with
its consumer (or **UNUSED** flag).

> Status legend: **runtime** = imported by production
> code · **dev** = build/test only · **unused** = no
> import found anywhere · **candidate-remove** =
> referenced but the only consumer is dead code.

---

## Python — `requirements.txt`

| Package                  | Pin           | Status     | Evidence                                                       |
|--------------------------|---------------|------------|----------------------------------------------------------------|
| `sentence-transformers`  | `>=2.5.0`     | **runtime**| `app/core/embeddings.py:51` — `from sentence_transformers import SentenceTransformer` |
| `chromadb`               | `>=0.4.22`    | **runtime**| `app/db/store.py:29` — vector store init                       |
| `pypdf`                  | `>=4.0.0`     | **runtime**| `app/core/parsers.py:36` — PDF text extraction                 |
| `PyQt6`                  | `>=6.6.0`     | **runtime**| Across `app/ui/*` + `app/main.py`                              |
| `pynput`                 | `>=1.7.6`     | **runtime**| `app/ui/hotkey.py:37` — global hotkey capture (try/except wrapped) |
| `watchdog`               | `>=3.0.0`     | **runtime**| `app/core/watcher.py` — background file watcher (optional)     |
| `fastapi`                | `>=0.110.0`   | **runtime**| `api/main.py:26`                                               |
| `uvicorn[standard]`      | `>=0.27.0`    | **runtime**| `api/main.py:25` — ASGI server                                 |
| `pydantic`               | `>=2.5.0`     | **runtime**| `api/schemas.py:18`                                             |
| `orjson`                 | `>=3.9.0`     | **runtime**| `app/core/events.py` — conditional import; stdlib `json` fallback |

**Verdict.** All 10 packages are real runtime dependencies.
No unused entries. `pynput` and `watchdog` are wrapped in
`try / except ImportError` blocks for graceful degradation
on hosts that don't have them.

Optional parsers (`python-docx`, `pytesseract`, `Pillow`)
are commented out in `requirements.txt` — fine.

---

## Extension UI — `apps/extension/ui/package.json`

| Package                  | Pin           | Status              | Evidence                                                       |
|--------------------------|---------------|---------------------|----------------------------------------------------------------|
| **dependencies**         |               |                     |                                                                |
| `framer-motion`          | `^11.3.0`     | **runtime**         | `src/App.tsx:2` + multiple `src/components/v2/*`               |
| `react`                  | `^18.3.1`     | **runtime**         | core                                                           |
| `react-dom`              | `^18.3.1`     | **runtime**         | `src/main.tsx:2`                                               |
| `playwright`             | `^1.48.0`     | **candidate-remove** | No `import` found in `src/`. Used by `capture_extension.mjs` (a build-time tool) — belongs in `devDependencies`, not `dependencies`. |
| **devDependencies**      |               |                     |                                                                |
| `@types/chrome`          | `^0.0.270`    | **dev**             | typings only                                                   |
| `@types/react`           | `^18.3.3`     | **dev**             | typings                                                        |
| `@types/react-dom`       | `^18.3.0`     | **dev**             | typings                                                        |
| `@vitejs/plugin-react`   | `^4.3.1`      | **dev**             | Vite plugin                                                    |
| `typescript`             | `^5.5.3`      | **dev**             | compiler                                                       |
| `vite`                   | `^5.4.0`      | **dev**             | build tool                                                     |

**Verdict.** One suspicious entry: `playwright` lives in
`dependencies` instead of `devDependencies` even though
it's only consumed by `capture_extension.mjs`. Moving it
to `devDependencies` would strip it from the
production-bundle install graph.

---

## Admin web — `apps/admin/web/package.json`

| Package                  | Pin            | Status     | Evidence                              |
|--------------------------|----------------|------------|---------------------------------------|
| **dependencies**         |                |            |                                       |
| `next`                   | `^14.2.18`     | **runtime**| Next.js framework                     |
| `react`                  | `^18.3.1`      | **runtime**| core                                  |
| `react-dom`              | `^18.3.1`      | **runtime**| SSR/hydration                         |
| **devDependencies**      |                |            |                                       |
| `@types/node`            | `^20.14.0`     | **dev**    | typings                               |
| `@types/react`           | `^18.3.3`      | **dev**    | typings                               |
| `@types/react-dom`       | `^18.3.0`      | **dev**    | typings                               |
| `typescript`             | `^5.5.3`       | **dev**    | compiler                              |

**Verdict.** Minimal, clean dependency set. No unused
packages.

---

## Marketing web — `apps/web/package.json`

| Package                  | Pin            | Status              | Evidence                                                  |
|--------------------------|----------------|---------------------|-----------------------------------------------------------|
| **dependencies**         |                |                     |                                                           |
| `clsx`                   | `^2.1.1`       | **unused**          | No `clsx(` usage anywhere in `app/`                       |
| `framer-motion`          | `^11.11.0`     | **runtime**         | `app/components/Hero.tsx:3` etc                           |
| `lucide-react`           | `^1.14.0`      | **unused**          | No imports detected in source tree                        |
| `next`                   | `^14.2.15`     | **runtime**         | framework                                                 |
| `react`                  | `^18.3.1`      | **runtime**         | core                                                      |
| `react-dom`              | `^18.3.1`      | **runtime**         | SSR/hydration                                             |
| `tailwind-merge`         | `^3.5.0`       | **unused**          | No `twMerge(` calls anywhere                              |
| **devDependencies**      |                |                     |                                                           |
| `@types/node`            | `^20.16.10`    | **dev**             | typings                                                   |
| `@types/react`           | `^18.3.11`     | **dev**             | typings                                                   |
| `@types/react-dom`       | `^18.3.0`      | **dev**             | typings                                                   |
| `autoprefixer`           | `^10.4.20`     | **dev**             | PostCSS plugin (Tailwind)                                 |
| `eslint`                 | `^8.57.1`      | **dev**             | linter                                                    |
| `eslint-config-next`     | `^14.2.15`     | **dev**             | Next ESLint config                                        |
| `postcss`                | `^8.4.47`      | **dev**             | CSS processor                                             |
| `tailwindcss`            | `^3.4.13`      | **dev**             | utility-first CSS                                         |
| `typescript`             | `^5.6.2`       | **dev**             | compiler                                                  |

**Verdict.** Three unused dependencies in
`apps/web/package.json`: `clsx`, `lucide-react`,
`tailwind-merge`. These are remnants from earlier UI
iterations (component-library scaffolding). Safe to
remove after one more grep confirms zero usage.

---

## Docs site (`apps/docs/`)

The docs site uses Mintlify CLI as a separate process,
no `package.json` in the source tree. No dependency
audit applicable here.

---

## Summary

| Manifest                              | Total | runtime | dev | unused | candidate-remove |
|---------------------------------------|-------|---------|-----|--------|------------------|
| `requirements.txt`                    | 10    | 10      | 0   | 0      | 0                |
| `apps/extension/ui/package.json`      | 10    | 3       | 6   | 0      | 1 (`playwright`) |
| `apps/admin/web/package.json`         | 7     | 3       | 4   | 0      | 0                |
| `apps/web/package.json`               | 16    | 4       | 9   | 3      | 0                |
| **Total**                             | **43**| **20**  | **19**| **3** | **1**            |

---

## Recommendations (NOT actioned in 8A)

**`apps/web/package.json` — remove 3 unused**:
- `clsx`
- `lucide-react`
- `tailwind-merge`

**`apps/extension/ui/package.json` — move 1**:
- `playwright` → `devDependencies`

**Re-verify with `npm ls`** before either change — the
auditor's grep can miss transitive uses (e.g., a peer
dep of a CSS plugin). The current 8A audit is a *prompt*
to verify, not a directive to delete.
