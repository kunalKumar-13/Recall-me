# Recall — Stabilization Audit

This audit was produced during the Phase-2A → stabilization handover. The
goal is not to redesign; it is to surface the seams that accumulated while
the product was finding its shape, so the next pass starts from a coherent
base.

Findings are grouped by area. Each finding carries a **severity**:

- **Critical** — silently wrong behavior, broken contract, or developer
  trust hazard. Fix before any external launch.
- **High** — works today, but the next change in this area will hit it.
- **Medium** — visible inconsistency or documentation drift.
- **Low** — cosmetic / nice-to-have.

Items marked **[FIXED]** at the end of a finding were resolved in the same
commit as this report.

---

## Phase 4C resolution pass (2026-05-15)

Items below were closed as part of the Phase 4C stability + sharpness
pass. The original findings remain in place for context; this section
is the running ledger of what each subsequent cycle landed.

| Item | Status |
|---|---|
| 6.1 — Unused `SearchResult` import | **NOT a bug** — verified in Phase 4A; the import is used by `_SearchWorker`. Closed without changes. |
| 7.4 — `prefers-reduced-motion` audit on continuous animations | **[FIXED]** — Phase 3A `ContinuityCore` gates its ambient drift on `useReducedMotion()`; the audit confirmed no other continuous animations exist. |
| 10.3 — Capture five real launcher screenshots | **Deferred** with named gate ([`PHASE_4A_STATUS.md`](../archive/old-docs/PHASE_4A_STATUS.md), [`assets/screenshots/README.md`](../../assets/screenshots/README.md)). Replaced placeholder captions in
   the docs with a "screenshot coming" treatment. |
| 8 — Documentation reorganization | **[FIXED]** — `STABILITY.md` added; `ROOT_ARCHITECTURE.md` + `REPO_STRUCTURE.md` added in Phase 4B; troubleshooting + FAQ + install-validation + 3-min install all live under `apps/docs/`. |
| 6 — Dead code | **[PARTIALLY FIXED]** — ten unused web components moved to `archive/web-components/` (Phase 4C). The Python `IngestServer` removal (item 1.2) remains gated on the validator extraction. |

New Phase 4C items (resolved in the same pass):

### 4C.1 Recovery confidence floor too lenient — *High* **[FIXED]**

The Phase-3B floor of 0.40 (raised to 0.45 in Phase 3C) still let
single-flick recoveries through when a thread's latest event was
recent but its last *coherent block of work* (its last evolution
phase) had ended weeks ago.

**Fix:** raised `_MIN_CONFIDENCE` to 0.50 and added a new
`_LAST_PHASE_RECENCY_DAYS = 10.0` guard inside
`RecoveryEngine._score_thread`. Smoke section 25 still passes at
conf ≈ 0.74; section 29 (shallow-browsing suppression) is
unaffected.

### 4C.2 Corrupt JSONL line could mask the rest of the file — *Medium* **[FIXED]**

`EventStore._cached_or_parse()`'s per-line `except _JSON_DECODE_ERRORS`
caught the common cases (truncated lines, plain garbage) but not
the long tail: non-dict top-level JSON (`"some string"`),
`UnicodeDecodeError` on the file read, or any other exception thrown
between `_loads()` and `Event()` construction.

**Fix:** broadened the file-read except to `(OSError,
UnicodeDecodeError)`, and added a fallback `except Exception` inside
the per-line loop. Smoke section 31 verifies a 7-line file with 4
broken lines + 3 good lines parses to exactly the 3 good events.

### 4C.3 Demo seeder not deterministic across base directories — *Medium* **[FIXED]**

The module-level `_SEED_MARKER = DEMO_EVENTS_DIR / ".seeded"` meant
`demo_seed.seed(base_dir=...)` with a non-default directory wrote the
events to the test dir but the marker to the user's real
`~/.recall/events-demo/.seeded`. The smoke test caught this when the
real path didn't exist on the CI machine.

**Fix:** marker path now derives from `base_dir` via
`_marker_for(base_dir)`. Smoke section 30 exercises the determinism
guarantee (same `now` → byte-identical files).

---

## 1. Architecture seams

### 1.1 `IngestServer` type leaks through Settings — *Critical* [FIXED]

`app/ui/settings.py:35,71` imports and annotates `ingest_server:
Optional[IngestServer]`. At runtime the caller in `app/main.py` constructs
`APIService` (the Phase-2A replacement) and passes it in. The code only
keeps working because `APIService` ducks the old surface (`set_enabled`,
`set_excluded_domains`, `excluded_domains`, `ingested_total`,
`dropped_total`). A type checker would catch this; a future refactor of
`IngestServer` would silently break Settings.

**Fix:** annotate as `APIService` (or a `Protocol` covering the surface).
Remove the `from ..core.ingest import IngestServer` import once Settings
no longer references the class.

### 1.2 Pre-2A `IngestServer` class is dead — *High*

`app/core/ingest.py` still defines `IngestServer`, `IngestHTTPServer`,
`_IngestRequestHandler`. Phase-2A moved network I/O to `api/main.py`. The
only remaining importer is Settings (see 1.1). The shared validators
(`ALLOWED_KINDS`, `SCHEME_BLOCKLIST`, `_ALLOWED_KEYS`, `_FIELD_LIMITS`,
`_sanitize_payload`) are imported by `api/services/ingestion.py` and *do*
need to stay.

**Fix:** extract the validators into `app/core/ingest_rules.py` (or
`api/services/_rules.py`); delete the HTTP server classes and `IngestServer`
wrapper. Update both importers in one commit.

### 1.3 Launcher writes events through one path, reads through another — *High*

`app/ui/launcher.py` constructs both `EventLogger` *and* `APIClient`, and
keeps a local `EventStore` as a "digest fallback". Writes go straight to
disk via `event_logger.log_*`; reads for the live query go over HTTP;
reads for the idle digest fall through to the local store when the API
client returns nothing. Three paths for one resource.

This is defensible for latency (a hotkey-driven action should not pay an
HTTP roundtrip to log itself) but it should be *intentional*, not
incidental. The code does not say so.

**Fix:** document the rule at the top of `Launcher.__init__`: writes go
local; reads go HTTP; the `EventStore` fallback exists only for offline
demo mode. Optionally: gate the fallback behind `if self._demo_mode`.

### 1.4 Port `4545` is hardcoded in five files — *Medium*

`app/core/config.py`, `app/core/ingest.py`, `extension/background.js`,
`extension/popup.js`, `app/ui/launcher.py`. Changing the bind port today
means touching five files in lockstep.

**Fix:** introduce `RECALL_API_PORT` env var read by `Config`. Extension
can keep `4545` as the default and read from `chrome.storage.local` for
override; that's the only client that can't import from `app/core/config`.

### 1.5 Two `SearchResponse` types with the same name — *Medium*

`api/schemas.py` defines `SearchResponse` (pydantic, HTTP payload).
`app/core/api_client.py` defines `SearchResponse` (dataclass, decoded
form). Both are imported as `SearchResponse`; cross-module reading is
confusing.

**Fix:** rename the client-side type to `SearchBundle` or
`ClientSearchResponse`. The server-side name belongs to the API contract.

---

## 2. Naming and terminology drift

### 2.1 Memory / moment / event / card used interchangeably — *Medium*

Same concept, four words depending on which file you open:

- "memory" — user-facing copy (README, web, docs)
- "moment" — episodic.py docstrings, launcher comments
- "event" — disk format, API routes, retrieval pool
- "card" — UI widgets only (`EpisodicCard`, `SessionCard`, `ContextCard`)

The split is not arbitrary — "event" is the unit of capture; "moment"
and "memory" are the same thing from inside vs outside the system; "card"
is the rendered surface. But this is not written down anywhere.

**Fix:** add a one-page glossary to `docs/architecture/` or to the top of
`AUDIT_REPORT.md`. Once written, do a single pass with `rg` to remove
stragglers ("memory" in core code, "event" in user copy).

### 2.2 "Ingest" vs "capture" — *Low*

API + service names say *ingest* (`/v1/events/*`, `IngestionService`,
`ingested_total`). UI copy says *capture* ("captured by the Recall
browser extension", "Connected · N captured"). The user never sees
"ingest" and the developer rarely sees "capture", so this is fine — but
the popup shows `ingested_total` as "captured", which is a small lie of
omission. Worth aligning.

### 2.3 "Memory blob" vs "memory summary" — *Low*

README + docs say "copy a memory blob". The launcher method is
`_copy_memory_summary`. Both refer to the same Ctrl+M output. Pick one
in user copy.

---

## 3. API surface vs documentation

### 3.1 Docs claim retrieval endpoints don't exist — *Critical* [FIXED]

`docs/api/introduction.mdx` and `docs/api/search.mdx` describe the API
as ingest-only and label `/v1/search` as *planned*. The endpoint has
been shipped since Phase 2A and is the launcher's primary read path.

**Fix:** rewrite `docs/api/introduction.mdx` to list the real endpoint
set. Convert `docs/api/search.mdx` from "planned" to "live".

### 3.2 `docs/api/events.mdx` only covers the legacy `/events` route — *High* [FIXED]

The four `/v1/events/{browser,search,chat,open}` endpoints — the actual
write path used by the extension and the launcher — are undocumented.

**Fix:** rewrite the page to lead with `/v1/events/{kind}`, demote
`/events` to a backward-compatibility note.

### 3.3 Five live endpoints undocumented — *High*

`GET /v1/sessions/recent`, `/v1/contexts/recent`, `/v1/events/recent`,
`/v1/queries/recent`, `POST /v1/replay/day`. All four serve real
launcher use cases. None appear in the docs.

**Fix:** add a `docs/api/retrieval.mdx` page that documents the read
surface in one place.

### 3.4 Five placeholder screenshots labeled "Replace with real screenshot" — *Medium*

In `introduction.mdx`, `browser-memory.mdx`, `sessions.mdx`,
`micro-contexts.mdx`, `retrieval-pipeline.mdx`. The placeholder caption
itself is what's shipped. Worse than no image.

**Fix:** capture five real launcher screenshots, drop them into
`docs/images/`. If unwilling to commit screenshots yet, remove the
captioned placeholders entirely until they exist.

---

## 4. Phase-number leakage into user-facing surfaces

### 4.1 `docs/sdk/introduction.mdx` annotates imports with Phase tags — *High* [FIXED]

```python
from app.core.episodic import EpisodicRetriever      # Phase 1C
from app.core.sessions import SessionReconstructor   # Phase 1E
```

Phase tags are project-internal milestones. They are meaningless to a
new reader and become misleading the moment a phase is renamed or
collapsed.

**Fix:** strip phase tags from all user-facing docs. Keep them in source
docstrings *only when they refer to a specific perf incident or
algorithmic decision worth recovering*.

### 4.2 Phase tags in source comments — *Low*

`app/core/episodic.py:1-12`, `app/core/sessions.py:3-31`,
`app/ui/launcher.py:99,105,124,201`, `app/ui/settings.py:84,139,174,182`,
`api/main.py:1,459`. Read fine as legacy markers; not worth a code edit,
but worth a once-over the next time those files are touched.

---

## 5. Keyboard shortcuts

### 5.1 Ctrl+Enter reveal — *Verified working*

The README claims Ctrl+Enter reveals in Explorer/Finder. The exploration
agent flagged this as missing; on inspection it *is* wired up, just via a
modifier check inside `_open_path_and_hide` rather than as a top-level
binding. No fix needed.

### 5.2 Two keyboard handlers — *Low*

`_InputKeyFilter.eventFilter` and `Launcher.keyPressEvent` implement the
same shortcuts. The docstring on `keyPressEvent` explains this is
deliberate (defense-in-depth for the case where focus leaves the input).
Keep, but consider extracting the shared logic so the two stay in sync
under future edits.

---

## 6. Dead code and stale comments

### 6.1 Unused import `SearchResult` in `app/ui/launcher.py:70` — *Low*

Drop it.

### 6.2 Settings tooltip implies launcher writes events directly — *Low*

`app/ui/settings.py:153,191` describes the activity log as if Settings
owns it. With Phase 2A, the API service owns the writes. Reword.

### 6.3 Duplicate time-formatting helpers — *Low*

`humanize_age` (core/events.py) vs `format_relative_time` (ui/widgets.py).
Both lowercase relative-time strings; the second one branches on long
ranges differently. Pick one and re-export. Not worth a commit on its
own.

---

## 7. Visual / marketing site

The web exploration agent's verdict was that the site already leans
Raycast/Linear, not "AI startup". A small set of fixes will compound:

### 7.1 `MemoryCore` rotation — *Low* [FIXED]

`web/app/components/MemoryVisualization.tsx` rotates the inner glint
once every 28 seconds. The motion is so slow it reads as "something is
loading" rather than "something is alive". Static is calmer.

### 7.2 Triple-stacked radial gradients on `MemoryCore` — *Low* [FIXED]

The orb stacks three radial gradients to produce its glow. Two would
read identical at this size. The third paints over half-pixels and
slightly muddies the edge.

### 7.3 H2 size drift across sections — *Low* [FIXED]

`HowItWorks` uses `text-[30px] md:text-[40px]`; `Privacy`, `Features`,
`MemoryVisualization` use `text-[32px] md:text-[44px]`. Standardize.

### 7.4 Continuous animations not audited for `prefers-reduced-motion` — *Medium*

The page respects `prefers-reduced-motion` for *most* `motion.div`
elements via Framer's defaults but not for the manual `animate={{ rotate
}}` on the memory core. Either remove (see 7.1) or gate.

---

## 8. Open-source readiness

### 8.1 No CONTRIBUTING.md — *High* [FIXED]

### 8.2 No SECURITY.md (esp. for a local-first product with a loopback HTTP server) — *High* [FIXED]

### 8.3 No CODE_OF_CONDUCT.md — *Medium* [FIXED]

### 8.4 No issue / PR templates — *Medium* [FIXED]

### 8.5 No single-command dev script — *Medium* [FIXED]

`scripts/dev.ps1` and `scripts/dev.sh` added. Both run venv create →
pip install → smoke test → launcher in one invocation.

### 8.6 No `.env.example` — *Low*

Recall has no required env vars (it's local-first). The optional ones
(`RECALL_DEMO`, `RECALL_DEBUG`, `RECALL_API_PORT`, `RECALL_LOG_FORMAT`)
are documented in the README and in `docs/self-hosting.mdx`. An empty
`.env.example` would be ceremony. Skipping.

---

## 9. Quick wins

The items below take less than ten minutes each. Bundle them.

1. Drop the unused `SearchResult` import in `launcher.py:70`.
2. Annotate `SettingsDialog.ingest_server` as `APIService`, drop the
   `IngestServer` import.
3. Search-and-replace "memory blob" → "memory summary" in README + docs
   for consistency with the source method.
4. Strip "Phase 1B" / "Phase 1A" tags from `app/ui/settings.py` section
   comments — they neither help nor hurt, and remove a question new
   readers ask.
5. Standardize H2 sizes in web/ to `text-[32px] md:text-[44px]`.

## 10. Long-term cleanup

The items below are real but expensive — schedule explicitly, don't
incrementally retry.

1. Delete `IngestServer` and the surrounding stdlib HTTP code from
   `app/core/ingest.py`. Move the four validator helpers to a small
   `ingest_rules.py` module that both Phase 2A code and any future
   importer can use. (~1 day, including tests.)
2. Extract a `Protocol` covering the IngestServer-compatible surface so
   `APIService` and any future replacement can satisfy it explicitly,
   instead of relying on duck typing in Settings.
3. Capture five real launcher screenshots and remove the placeholder
   captions from the docs.
4. Write the one-page Recall glossary that locks in
   *memory* / *moment* / *event* / *card* semantics and link to it from
   the README and from `docs/architecture/`.
5. Replace the duplicate time-formatting helpers with one canonical
   `humanize_age` re-exported from `app.core.events`.

## 11. Recommended next milestone

Stop adding features. Spend one cycle on the items above; ship a
**Recall 0.2** that consists of nothing but coherence:

- Phase tags removed from user-facing surfaces.
- API docs match the real surface.
- Settings types match runtime types.
- Five real screenshots in the docs.
- One glossary, one set of names.

After that, the next *product* milestone — whatever shape it takes —
will land on a base a new contributor can understand in an afternoon.
That is the precondition for any serious open-source launch.
