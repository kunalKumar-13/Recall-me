import { useCallback, useEffect, useLayoutEffect, useRef, useState } from "react";
import { getCurrentWindow } from "@tauri-apps/api/window";
import { engineHealth, recoveryRecent, recoveryRestore, resizeHeight } from "./api";
import type { RecoveryCandidate } from "./types";

type Status = "loading" | "ready" | "empty" | "offline";

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
  const [selected, setSelected] = useState(0);
  const [restoring, setRestoring] = useState(false);
  const rootRef = useRef<HTMLDivElement>(null);

  // ---- load the real recovery surface from the live engine ----
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
      setSelected(0);
      setStatus(cands.length ? "ready" : "empty");
    } catch {
      setStatus("offline");
    }
  }, []);

  useEffect(() => {
    void load();
  }, [load]);

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
  }, [status, candidates.length]);

  const hide = useCallback(() => {
    void getCurrentWindow().hide();
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

  // ---- keyboard-first navigation ----
  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      if (e.key === "Escape") {
        e.preventDefault();
        hide();
      } else if (e.key === "ArrowDown") {
        e.preventDefault();
        setSelected((i) => Math.min(i + 1, Math.max(0, candidates.length - 1)));
      } else if (e.key === "ArrowUp") {
        e.preventDefault();
        setSelected((i) => Math.max(i - 1, 0));
      } else if (e.key === "Enter") {
        e.preventDefault();
        void restoreSelected();
      }
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [candidates.length, restoreSelected, hide]);

  return (
    <div className="panel" ref={rootRef}>
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
                  <span className="node" />
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

      <div className="footer mono">
        <span>↑↓ move</span>
        <span>↵ resume</span>
        <span>esc close</span>
      </div>
    </div>
  );
}
