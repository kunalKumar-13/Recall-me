# DEPENDENCIES.md — what Recall pulls in, classified

Three dependency manifests, one product. Each row classified by
role so a reader can see what is shipped at runtime vs. what is
only on a build machine.

Pairs with [`DEAD_CODE_AUDIT.md`](DEAD_CODE_AUDIT.md) and the
charter rule that the only outbound network call Recall makes is
the one-time embedding-model download on first run
([`CLAUDE.md`](../../CLAUDE.md) § *Global engineering rules*).

---

## Python — `requirements.txt`

| Package | Role | Required by | Class |
|---|---|---|---|
| `sentence-transformers >= 2.5.0` | embedding model loader | `app/core/embeddings.py` | **runtime** |
| `chromadb >= 0.4.22` | local vector store | `app/db/store.py` | **runtime** |
| `pypdf >= 4.0.0` | PDF text extraction | `app/core/parsers.py` | **runtime** |
| `PyQt6 >= 6.6.0` | launcher window | `app/ui/*.py` | **runtime** |
| `pynput >= 1.7.6` | global hotkey | `app/ui/hotkey.py` | **runtime** |
| `watchdog >= 3.0.0` | folder watcher | `app/core/watcher.py` | **runtime** |
| `fastapi >= 0.110.0` | local API service | `api/*` | **runtime** |
| `uvicorn[standard] >= 0.27.0` | ASGI server | `api/main.py` | **runtime** |
| `pydantic >= 2.5.0` | API schemas | `api/schemas.py` | **runtime** |
| `orjson >= 3.9.0` | fast JSONL parse (perf budget) | `app/core/events.py` | **runtime** |

**Commented (opt-in, not installed by default):**

| Package | Why opt-in |
|---|---|
| `python-docx` | only needed for `.docx` parsing |
| `pytesseract`, `Pillow` | OCR — needs Tesseract installed system-wide |
| `pyinstaller >= 6.0.0` | **build-only** — uncomment when running `infra/packaging/windows/build.ps1` |

**Test dependencies:** none. The test runner is `python _smoke_api.py` — stdlib only; the FastAPI `TestClient` ships in `fastapi`.

## Web — `apps/web/package.json`

Built with Next.js 14 (app router), TypeScript, Tailwind, Framer Motion.

| Class | Packages |
|---|---|
| **runtime** | `next`, `react`, `react-dom`, `framer-motion`, `tailwindcss`, `postcss`, `autoprefixer` |
| **dev** | `@types/*`, `eslint`, `eslint-config-next`, `typescript` |
| **docs** | — (the marketing site has no doc deps) |

All standard for a Next.js project. No analytics SDK; no telemetry
script; no third-party tracker. Confirm by grepping
`apps/web/app/` for any `<script src=` — there is none.

## Extension popup — `apps/extension/ui/package.json`

Built with Vite + React + TypeScript + Framer Motion.

| Class | Packages |
|---|---|
| **runtime** (shipped in the popup bundle) | `react`, `react-dom`, `framer-motion` |
| **build** | `vite`, `@vitejs/plugin-react`, `typescript` |
| **types (dev)** | `@types/chrome`, `@types/react`, `@types/react-dom` |
| **capture tooling (dev)** | `playwright` |

> **Hygiene note (Phase 5D):** `playwright` is currently listed
> under `dependencies` (alongside `react` / `framer-motion`) — it
> should be a `devDependency` because it is used only by
> `capture_extension.mjs` for screenshot generation, never inside
> the popup bundle. The popup runtime bundle (89 KB gzipped) does
> not include Playwright; the `dependencies` placement is a
> declaration drift, not a shipping problem. Moving it is a
> follow-up correctness fix.

## Extension worker (hand-written)

`apps/extension/background.js` and `apps/extension/manifest.json`
are **plain JavaScript / JSON** — no build, no dependencies. The
only thing they pull in is Chrome's MV3 runtime via the manifest.

## Where everything lands at install time

- **Windows / macOS installer:** the PyInstaller bundle includes
  every *runtime* row in the Python table above plus the embedding
  model loader (model itself downloads once on first run, cached
  locally — never re-fetched once `local_files_only=True` is in
  effect).
- **Web:** static Next.js build, no install side effects.
- **Extension:** the built `popup/` is React + Framer Motion only;
  no Playwright, no test-runner, no Vite.

## Audit findings — none of these are runtime risks

| Finding | Action |
|---|---|
| `playwright` in extension `dependencies` (should be `devDependencies`) | move to `devDependencies` in a follow-up PR — does not affect the shipped bundle |
| `requirements.txt` is unpinned (`>=` ranges) | acceptable for a development charter; pinning happens at release-build time via the PyInstaller bundle, which freezes the resolved versions |
| Optional parsers commented | working as designed — opt-in |
| No `requirements-dev.txt` | the project intentionally has no extra dev dependencies — `_smoke_api.py` uses stdlib + the runtime FastAPI |

The dependency surface is small on purpose — fewer rows, fewer
update treadmills, fewer transitive-supply-chain surprises.
