import {
  useCallback,
  useEffect,
  useLayoutEffect,
  useMemo,
  useRef,
  useState,
} from "react";
import { getCurrentWindow } from "@tauri-apps/api/window";
import {
  engineHealth,
  recoveryRecent,
  recoveryRestore,
  resurfaceIdle,
  search as searchEngine,
  searchFiles,
  threadsRecent,
  threadEvolution,
  openTarget,
  resizeHeight,
} from "./api";
import type {
  FileHit,
  RecoveryCandidate,
  ResurfacedContext,
  SearchResponse,
  Thread,
  ThreadEvolutionResponse,
} from "./types";

type Status = "loading" | "ready" | "empty" | "offline";
type Mode = "list" | "detail";
type Layer = "moment" | "session" | "context" | "file";
type Action = "restore" | "open" | "detail" | "none";

interface Row {
  key: string;
  layer: Layer;
  title: string;
  caption: string;
  action: Action;
  hint: string;
  group?: "recovery" | "thread" | "radar";
  threadId?: string;
  recoveryId?: string;
  target?: { kind: string; target: string };
}

function relTime(epoch: number): string {
  if (!epoch) return "";
  const s = Math.max(0, Math.floor(Date.now() / 1000 - epoch));
  if (s < 90) return "just now";
  const m = Math.floor(s / 60);
  if (m < 60) return `${m}m ago`;
  const h = Math.floor(m / 60);
  if (h < 36) return `${h}h ago`;
  return `${Math.floor(h / 24)}d ago`;
}

export default function App() {
  const [status, setStatus] = useState<Status>("loading");
  const [candidates, setCandidates] = useState<RecoveryCandidate[]>([]);
  const [threads, setThreads] = useState<Thread[]>([]);
  const [radar, setRadar] = useState<ResurfacedContext[]>([]);
  const [query, setQuery] = useState("");
  const [bundle, setBundle] = useState<SearchResponse | null>(null);
  const [files, setFiles] = useState<FileHit[]>([]);
  const [searching, setSearching] = useState(false);
  const [mode, setMode] = useState<Mode>("list");
  const [detail, setDetail] = useState<ThreadEvolutionResponse | null>(null);
  const [detailTitle, setDetailTitle] = useState("");
  const [detailLoading, setDetailLoading] = useState(false);
  const [selected, setSelected] = useState(0);
  const [restoringId, setRestoringId] = useState<string | null>(null);
  const rootRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  const searchMode = query.trim() !== "";

  // ---- resting state: recovery + active threads, from the live engine ----
  const load = useCallback(async () => {
    try {
      await engineHealth();
    } catch {
      setStatus("offline");
      return;
    }
    try {
      const [rec, thr, rad] = await Promise.all([
        recoveryRecent(3),
        threadsRecent(6).catch(() => ({ threads: [], elapsed_ms: 0 })),
        resurfaceIdle(3).catch(() => ({ contexts: [], enabled: false, elapsed_ms: 0 })),
      ]);
      const cands = rec.candidates ?? [];
      setCandidates(cands);
      setThreads(thr.threads ?? []);
      setRadar(rad.enabled ? rad.contexts ?? [] : []);
      setStatus(cands.length ? "ready" : "empty");
    } catch {
      setStatus("offline");
    }
  }, []);

  useEffect(() => {
    void load();
  }, [load]);

  // ---- search: opt-in once the user types (debounced) ----
  // Two corpora in parallel: the episodic bundle and the semantic
  // file index. Files failing (older daemon, no index) never blocks
  // the memory results.
  useEffect(() => {
    const q = query.trim();
    if (q === "") {
      setBundle(null);
      setFiles([]);
      setSelected(0);
      return;
    }
    let cancelled = false;
    setSearching(true);
    const t = setTimeout(async () => {
      const [res, fh] = await Promise.all([
        searchEngine(q).catch(() => null),
        searchFiles(q, 4).catch(() => null),
      ]);
      if (cancelled) return;
      setBundle(res);
      setFiles(fh && fh.enabled ? fh.results : []);
      setSelected(0);
      setSearching(false);
    }, 130);
    return () => {
      cancelled = true;
      clearTimeout(t);
    };
  }, [query]);

  // ---- row models, one per surface, all navigated the same way ----

  const restingRows = useMemo<Row[]>(() => {
    const rows: Row[] = [];
    if (status === "ready") {
      candidates.forEach((c) => {
        rows.push({
          key: `rec-${c.id}`,
          layer: "moment",
          title: c.title,
          caption: c.preview_caption || relTime(c.last_active_at),
          action: "restore",
          hint: "↵ resume",
          group: "recovery",
          recoveryId: c.id,
          threadId: c.thread_id,
        });
      });
    }
    threads.forEach((t) => {
      rows.push({
        key: `thr-${t.id}`,
        layer: "session",
        title: t.title,
        caption: t.timeline_summary || `${t.event_count} events`,
        action: "detail",
        hint: "↵ phases",
        group: "thread",
        threadId: t.id,
      });
    });
    // On your radar — topics set aside long enough to have cooled.
    // Anything already shown as a thread stays a thread; the radar
    // only carries what would otherwise be forgotten.
    const threadTitles = new Set(threads.map((t) => t.title));
    radar
      .filter((r) => !threadTitles.has(r.label || r.topic))
      .slice(0, 3)
      .forEach((r, i) => {
        const target = r.openable_targets[0];
        rows.push({
          key: `rad-${i}`,
          layer: "context",
          title: r.label || r.topic,
          caption: `${r.time_label} · set aside`,
          action: target ? "open" : "none",
          hint: "↵ open",
          group: "radar",
          target,
        });
      });
    return rows;
  }, [status, candidates, threads, radar]);

  const searchRows = useMemo<Row[]>(() => {
    if (!bundle && files.length === 0) return [];
    const rows: Row[] = [];
    if (!bundle) {
      files.forEach((f, i) =>
        rows.push({
          key: `f${i}`,
          layer: "file",
          title: f.name,
          caption: f.path.replace(/^\/Users\/[^/]+/, "~"),
          action: "open",
          hint: "↵ open",
          target: { kind: "path", target: f.path },
        }),
      );
      return rows;
    }
    bundle.episodic.forEach((e, i) =>
      rows.push({
        key: `m${i}`,
        layer: "moment",
        title: e.title || e.subtitle || e.url,
        caption: e.subtitle || e.kind,
        action: e.url ? "open" : "none",
        hint: "↵ open",
        target: e.url ? { kind: "url", target: e.url } : undefined,
      }),
    );
    bundle.sessions.forEach((s, i) =>
      rows.push({
        key: `s${i}`,
        layer: "session",
        title: s.label || s.topic,
        caption: `${s.time_label} · ${s.event_count} events`,
        action: s.openable_targets[0] ? "open" : "none",
        hint: "↵ open",
        target: s.openable_targets[0],
      }),
    );
    bundle.contexts.forEach((c, i) =>
      rows.push({
        key: `c${i}`,
        layer: "context",
        title: c.label || c.topic,
        caption: `${c.time_label} · ${c.event_count} events`,
        action: c.openable_targets[0] ? "open" : "none",
        hint: "↵ open",
        target: c.openable_targets[0],
      }),
    );
    files.forEach((f, i) =>
      rows.push({
        key: `f${i}`,
        layer: "file",
        title: f.name,
        caption: f.path.replace(/^\/Users\/[^/]+/, "~"),
        action: "open",
        hint: "↵ open",
        target: { kind: "path", target: f.path },
      }),
    );
    return rows;
  }, [bundle, files]);

  const detailRows = useMemo<Row[]>(() => {
    if (!detail) return [];
    return detail.phases.map((p, i) => ({
      key: `p${i}`,
      layer: "context",
      title: p.title,
      caption: `${p.transition || p.dominant_surface} · ${p.event_count} events`,
      action: p.representative_targets[0] ? "open" : "none",
      hint: "↵ open",
      target: p.representative_targets[0],
    }));
  }, [detail]);

  const activeRows =
    mode === "detail" ? detailRows : searchMode ? searchRows : restingRows;

  // ---- content-fit: window height tracks rendered content ----
  useLayoutEffect(() => {
    const el = rootRef.current;
    if (!el) return;
    let frame = 0;
    const fit = () => {
      cancelAnimationFrame(frame);
      frame = requestAnimationFrame(() => {
        const h = Math.ceil(el.getBoundingClientRect().height);
        if (h > 0) void resizeHeight(h);
      });
    };
    fit();
    const ro = new ResizeObserver(fit);
    ro.observe(el);
    return () => {
      ro.disconnect();
      cancelAnimationFrame(frame);
    };
  }, [status, mode, searchMode, activeRows.length]);

  const hide = useCallback(() => {
    void getCurrentWindow().hide();
  }, []);

  const backToList = useCallback(() => {
    setMode("list");
    setDetail(null);
    setSelected(0);
  }, []);

  // Every summon is a fresh surface: refocus the field, reset to the
  // resting list, clear the query (Raycast-like).
  useEffect(() => {
    const win = getCurrentWindow();
    const unlisten = win.onFocusChanged(({ payload: focused }) => {
      if (focused) {
        inputRef.current?.focus();
        inputRef.current?.select();
      } else {
        setQuery("");
        setSelected(0);
        setMode("list");
        setDetail(null);
      }
    });
    return () => {
      void unlisten.then((f) => f());
    };
  }, []);

  const openDetail = useCallback(
    async (threadId: string, title: string) => {
      setMode("detail");
      setDetailTitle(title);
      setDetail(null);
      setDetailLoading(true);
      setSelected(0);
      try {
        const evo = await threadEvolution(threadId);
        setDetail(evo);
      } catch {
        setDetail({
          thread_id: threadId,
          phases: [],
          span_start: 0,
          span_end: 0,
          elapsed_ms: 0,
        });
      } finally {
        setDetailLoading(false);
      }
    },
    [],
  );

  const perform = useCallback(
    async (row: Row | undefined) => {
      if (!row) return;
      if (row.action === "detail" && row.threadId) {
        void openDetail(row.threadId, row.title);
      } else if (row.action === "restore" && row.recoveryId) {
        if (restoringId) return;
        setRestoringId(row.recoveryId);
        try {
          // The Rust command walks the engine's plan in order with a
          // stagger; the panel hides itself the moment the first
          // target takes focus. By the time this resolves the work
          // is back on screen.
          await recoveryRestore(row.recoveryId);
        } finally {
          setRestoringId(null);
          hide();
        }
      } else if (row.action === "open" && row.target) {
        try {
          await openTarget(row.target.kind, row.target.target);
        } finally {
          hide();
        }
      }
    },
    [openDetail, restoringId, hide],
  );

  // ---- keyboard-first navigation ----
  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      const len = activeRows.length;
      if (e.key === "Escape") {
        e.preventDefault();
        if (mode === "detail") backToList();
        else if (searchMode) {
          setQuery("");
          setSelected(0);
        } else hide();
      } else if (e.key === "ArrowLeft") {
        if (mode === "detail") {
          e.preventDefault();
          backToList();
        }
      } else if (e.key === "ArrowRight") {
        const row = activeRows[selected];
        if (mode !== "detail" && row?.threadId) {
          e.preventDefault();
          void openDetail(row.threadId, row.title);
        }
      } else if (e.key === "ArrowDown") {
        e.preventDefault();
        setSelected((i) => Math.min(i + 1, Math.max(0, len - 1)));
      } else if (e.key === "ArrowUp") {
        e.preventDefault();
        setSelected((i) => Math.max(i - 1, 0));
      } else if (e.key === "Enter") {
        e.preventDefault();
        void perform(activeRows[selected]);
      }
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [
    mode,
    searchMode,
    activeRows,
    selected,
    openDetail,
    perform,
    backToList,
    hide,
  ]);

  const renderRows = (rows: Row[], offset = 0) => (
    <div className="thread">
      {rows.map((r, i) => {
        const sel = offset + i === selected;
        const busy = r.recoveryId != null && r.recoveryId === restoringId;
        return (
          <div className={`row${sel ? " sel" : ""}`} key={r.key}>
            <div className="node-col">
              <span className={`node ${r.layer}`} />
            </div>
            <div className="row-main">
              <div className="row-title">{r.title}</div>
              <div className="row-caption mono">
                {busy ? "reopening your work…" : r.caption}
              </div>
            </div>
            <div className="row-hint mono">
              {busy ? "…" : sel && r.action !== "none" ? r.hint : ""}
            </div>
          </div>
        );
      })}
    </div>
  );

  // ---- detail view: one thread's evolution ----
  if (mode === "detail") {
    return (
      <div className="panel" ref={rootRef}>
        <div className="header detail-header">← {detailTitle || "Thread"}</div>
        {detailLoading ? (
          <div className="thread" />
        ) : detailRows.length > 0 ? (
          renderRows(detailRows)
        ) : (
          <div className="state">
            <div className="state-title">No phases yet</div>
            <div className="state-sub mono">
              this thread hasn't split into phases
            </div>
          </div>
        )}
        <div className="footer mono">
          <span>↑↓ move</span>
          <span>← back</span>
          <span>esc close</span>
        </div>
      </div>
    );
  }

  // ---- list view: search field + (recovery + threads | search results) ----
  return (
    <div className="panel" ref={rootRef}>
      <div className="searchbar">
        <span className="search-icon mono" aria-hidden>
          ⌕
        </span>
        <input
          ref={inputRef}
          className="search-input"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Search your memory…"
          autoFocus
          spellCheck={false}
          autoComplete="off"
        />
      </div>

      {searchMode ? (
        searchRows.length > 0 ? (
          renderRows(searchRows)
        ) : (
          <div className="state">
            <div className="state-title">
              {searching ? "Searching…" : "No matches"}
            </div>
            <div className="state-sub mono">
              {searching ? query : "try a different word"}
            </div>
          </div>
        )
      ) : (
        <>
          <div className="header">Continue where you left off</div>
          {status === "loading" && <div className="thread" />}
          {status === "offline" && (
            <div className="state">
              <div className="state-title">Engine offline</div>
              <div className="state-sub mono">start Recall · 127.0.0.1:4545</div>
            </div>
          )}
          {status === "empty" && (
            <div className="state">
              <div className="state-title">Nothing to resume yet</div>
              <div className="state-sub mono">
                unfinished work surfaces here as you go
              </div>
            </div>
          )}
          {status === "ready" &&
            renderRows(restingRows.filter((r) => r.group === "recovery"))}

          {threads.length > 0 && (
            <>
              <div className="header">Active threads</div>
              {renderRows(
                restingRows.filter((r) => r.group === "thread"),
                restingRows.filter((r) => r.group === "recovery").length,
              )}
            </>
          )}

          {restingRows.some((r) => r.group === "radar") && (
            <>
              <div className="header">On your radar</div>
              {renderRows(
                restingRows.filter((r) => r.group === "radar"),
                restingRows.filter((r) => r.group !== "radar").length,
              )}
            </>
          )}
        </>
      )}

      <div className="footer mono">
        <span>↑↓ move</span>
        <span>{searchMode ? "↵ open" : "↵ open · → phases"}</span>
        <span>{searchMode ? "esc clear" : "esc close"}</span>
      </div>
    </div>
  );
}
