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
  search as searchEngine,
  openTarget,
  resizeHeight,
} from "./api";
import type { RecoveryCandidate, SearchResponse } from "./types";

type Status = "loading" | "ready" | "empty" | "offline";
type Layer = "moment" | "session" | "context";

interface ResultRow {
  key: string;
  layer: Layer;
  title: string;
  caption: string;
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
  const [query, setQuery] = useState("");
  const [bundle, setBundle] = useState<SearchResponse | null>(null);
  const [searching, setSearching] = useState(false);
  const [selected, setSelected] = useState(0);
  const [restoring, setRestoring] = useState(false);
  const rootRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  const searchMode = query.trim() !== "";

  // ---- recovery: the resting state, loaded from the live engine ----
  const load = useCallback(async () => {
    try {
      await engineHealth();
    } catch {
      setStatus("offline");
      return;
    }
    try {
      const res = await recoveryRecent(3);
      const cands = res.candidates ?? [];
      setCandidates(cands);
      setStatus(cands.length ? "ready" : "empty");
    } catch {
      setStatus("offline");
    }
  }, []);

  useEffect(() => {
    void load();
  }, [load]);

  // ---- search: opt-in once the user types (debounced) ----
  useEffect(() => {
    const q = query.trim();
    if (q === "") {
      setBundle(null);
      setSelected(0);
      return;
    }
    let cancelled = false;
    setSearching(true);
    const t = setTimeout(async () => {
      try {
        const res = await searchEngine(q);
        if (!cancelled) {
          setBundle(res);
          setSelected(0);
        }
      } catch {
        if (!cancelled) setBundle(null);
      } finally {
        if (!cancelled) setSearching(false);
      }
    }, 130);
    return () => {
      cancelled = true;
      clearTimeout(t);
    };
  }, [query]);

  // Flatten the search bundle onto one keyboard-navigable spine, each
  // row tagged with its layer so the node takes the right hue.
  const results = useMemo<ResultRow[]>(() => {
    if (!bundle) return [];
    const rows: ResultRow[] = [];
    bundle.episodic.forEach((e, i) => {
      rows.push({
        key: `m${i}`,
        layer: "moment",
        title: e.title || e.subtitle || e.url,
        caption: e.subtitle || e.kind,
        target: e.url ? { kind: "url", target: e.url } : undefined,
      });
    });
    bundle.sessions.forEach((s, i) => {
      rows.push({
        key: `s${i}`,
        layer: "session",
        title: s.label || s.topic,
        caption: `${s.time_label} · ${s.event_count} events`,
        target: s.openable_targets[0],
      });
    });
    bundle.contexts.forEach((c, i) => {
      rows.push({
        key: `c${i}`,
        layer: "context",
        title: c.label || c.topic,
        caption: `${c.time_label} · ${c.event_count} events`,
        target: c.openable_targets[0],
      });
    });
    return rows;
  }, [bundle]);

  const activeLen = searchMode ? results.length : candidates.length;

  // ---- content-fit: window height tracks rendered content (Raycast-like) ----
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
  }, [status, candidates.length, searchMode, results.length]);

  const hide = useCallback(() => {
    void getCurrentWindow().hide();
  }, []);

  // Refocus the field each time the panel is summoned; clear the query
  // on dismiss so every summon is a fresh surface (Raycast-like).
  useEffect(() => {
    const win = getCurrentWindow();
    const unlisten = win.onFocusChanged(({ payload: focused }) => {
      if (focused) {
        inputRef.current?.focus();
        inputRef.current?.select();
      } else {
        setQuery("");
        setSelected(0);
      }
    });
    return () => {
      void unlisten.then((f) => f());
    };
  }, []);

  const restoreSelected = useCallback(async () => {
    const c = candidates[selected];
    if (!c || restoring) return;
    setRestoring(true);
    try {
      await recoveryRestore(c.id); // Rust opens targets in choreographed order
    } finally {
      setRestoring(false);
      hide();
    }
  }, [candidates, selected, restoring, hide]);

  const openSelected = useCallback(async () => {
    const row = results[selected];
    if (!row || !row.target) return;
    try {
      await openTarget(row.target.kind, row.target.target);
    } finally {
      hide();
    }
  }, [results, selected, hide]);

  // ---- keyboard-first navigation ----
  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      if (e.key === "Escape") {
        e.preventDefault();
        if (searchMode) {
          setQuery("");
          setSelected(0);
        } else {
          hide();
        }
      } else if (e.key === "ArrowDown") {
        e.preventDefault();
        setSelected((i) => Math.min(i + 1, Math.max(0, activeLen - 1)));
      } else if (e.key === "ArrowUp") {
        e.preventDefault();
        setSelected((i) => Math.max(i - 1, 0));
      } else if (e.key === "Enter") {
        e.preventDefault();
        if (searchMode) void openSelected();
        else void restoreSelected();
      }
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [searchMode, activeLen, openSelected, restoreSelected, hide]);

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

      {!searchMode && (
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

          {status === "ready" && (
            <div className="thread">
              {candidates.map((c, i) => {
                const sel = i === selected;
                const caption = c.preview_caption || relTime(c.last_active_at);
                return (
                  <div className={`row${sel ? " sel" : ""}`} key={c.id}>
                    <div className="node-col">
                      <span className="node moment" />
                    </div>
                    <div className="row-main">
                      <div className="row-title">{c.title}</div>
                      <div className="row-caption mono">{caption}</div>
                    </div>
                    <div className="row-hint mono">{sel ? "↵ resume" : ""}</div>
                  </div>
                );
              })}
            </div>
          )}
        </>
      )}

      {searchMode &&
        (results.length > 0 ? (
          <div className="thread">
            {results.map((r, i) => {
              const sel = i === selected;
              return (
                <div className={`row${sel ? " sel" : ""}`} key={r.key}>
                  <div className="node-col">
                    <span className={`node ${r.layer}`} />
                  </div>
                  <div className="row-main">
                    <div className="row-title">{r.title}</div>
                    <div className="row-caption mono">{r.caption}</div>
                  </div>
                  <div className="row-hint mono">
                    {sel && r.target ? "↵ open" : ""}
                  </div>
                </div>
              );
            })}
          </div>
        ) : (
          <div className="state">
            <div className="state-title">
              {searching ? "Searching…" : "No matches"}
            </div>
            <div className="state-sub mono">
              {searching ? query : "try a different word"}
            </div>
          </div>
        ))}

      <div className="footer mono">
        <span>↑↓ move</span>
        <span>{searchMode ? "↵ open" : "↵ resume"}</span>
        <span>{searchMode ? "esc clear" : "esc close"}</span>
      </div>
    </div>
  );
}
