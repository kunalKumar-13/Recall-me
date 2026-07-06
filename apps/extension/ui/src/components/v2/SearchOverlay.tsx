import { useEffect, useMemo, useRef, useState } from "react";
import { AnimatePresence, motion } from "framer-motion";
import type { Investigation, MemoryItem, Recovery } from "../../lib/types";
import { calm, calmFast } from "../../lib/motion";
import { openTab, searchDaemon, searchFilesDaemon } from "../../lib/api";
import { Icon } from "../icons";

/**
 * Phase 7A search overlay. Slides in from the top, sits above the
 * page, lists matches across the four corpora the directive names:
 *
 *   - investigations  (Active investigations)
 *   - files           (recovery `path` targets)
 *   - events          (today's timeline)
 *   - returns         (recovery `url` targets)
 *
 * Cmd/Ctrl+K opens; Esc closes. The match is a simple substring
 * filter on the in-memory state — no daemon round-trip, no
 * network. The directive's *Design UI now. Engine later.* rule
 * applies: when a richer search endpoint lands, swap the
 * `useResults` body and keep the UI intact.
 */
export function SearchOverlay({
  open,
  onClose,
  recovery,
  investigations,
  memory,
}: {
  open: boolean;
  onClose: () => void;
  recovery: Recovery | null;
  investigations: Investigation[];
  memory: MemoryItem[];
}) {
  const [q, setQ] = useState("");
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    if (!open) {
      setQ("");
      return;
    }
    // Focus when the overlay enters.
    const t = setTimeout(() => inputRef.current?.focus(), 80);
    return () => clearTimeout(t);
  }, [open]);

  useEffect(() => {
    function onKey(e: KeyboardEvent) {
      if (e.key === "Escape" && open) {
        e.preventDefault();
        onClose();
      }
    }
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [open, onClose]);

  const local = useResults(q, recovery, investigations, memory);

  /* Remote corpus: the daemon's episodic search, debounced. The
   * in-memory matches stay instant; the engine's deeper matches
   * arrive a beat later at the top. */
  const [remote, setRemote] = useState<ResultRow[]>([]);
  const [fileHits, setFileHits] = useState<ResultRow[]>([]);
  useEffect(() => {
    const needle = q.trim();
    if (needle.length < 2) {
      setRemote([]);
      setFileHits([]);
      return;
    }
    let dead = false;
    const t = setTimeout(async () => {
      const [hits, files] = await Promise.all([
        searchDaemon(needle),
        searchFilesDaemon(needle),
      ]);
      if (dead) return;
      setRemote(hits);
      setFileHits(files);
    }, 160);
    return () => {
      dead = true;
      clearTimeout(t);
    };
  }, [q]);

  const results = useMemo<ResultGroupT[]>(() => {
    const groups: ResultGroupT[] = [];
    if (remote.length) groups.push({ label: "From your memory", rows: remote });
    if (fileHits.length) groups.push({ label: "Files on disk", rows: fileHits });
    groups.push(...local);
    return groups;
  }, [remote, fileHits, local]);

  return (
    <AnimatePresence>
      {open && (
        <>
          <motion.div
            key="scrim"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={calmFast}
            onClick={onClose}
            style={{
              position: "absolute",
              inset: 0,
              background: "rgba(27, 26, 24, 0.32)",
              zIndex: 10,
            }}
          />
          <motion.div
            key="overlay"
            role="dialog"
            aria-label="Search"
            initial={{ opacity: 0, y: -12 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -12 }}
            transition={calm}
            style={{
              position: "absolute",
              top: 16,
              left: 16,
              right: 16,
              maxHeight: 560,
              display: "flex",
              flexDirection: "column",
              background: "var(--surface-1)",
              border: "1px solid var(--line)",
              borderRadius: "var(--radius-card)",
              boxShadow: "var(--shadow-elevated)",
              overflow: "hidden",
              zIndex: 11,
            }}
          >
            <div
              style={{
                display: "flex",
                alignItems: "center",
                gap: 10,
                padding: "12px 14px",
                borderBottom: "1px solid var(--line)",
              }}
            >
              <span style={{ color: "var(--ink-3)", display: "flex" }}>
                <Icon.search size={16} />
              </span>
              <input
                ref={inputRef}
                value={q}
                onChange={(e) => setQ(e.target.value)}
                placeholder="Search investigations, files, events, returns…"
                style={{
                  flex: 1,
                  background: "transparent",
                  border: "none",
                  outline: "none",
                  fontSize: 13,
                  color: "var(--ink)",
                  fontFamily: "inherit",
                }}
              />
              <span
                style={{
                  fontSize: 9.5,
                  fontWeight: 700,
                  letterSpacing: "1px",
                  color: "var(--ink-4)",
                }}
              >
                ESC
              </span>
            </div>
            <div className="scroll-area" style={{ maxHeight: 420 }}>
              {results.length === 0 ? (
                <EmptyResults q={q} />
              ) : (
                results.map((g) => (
                  <ResultGroup key={g.label} group={g} />
                ))
              )}
            </div>
          </motion.div>
        </>
      )}
    </AnimatePresence>
  );
}

type ResultRow = { label: string; detail?: string; url?: string };
type ResultGroupT = { label: string; rows: ResultRow[] };

function useResults(
  q: string,
  recovery: Recovery | null,
  investigations: Investigation[],
  memory: MemoryItem[],
): ResultGroupT[] {
  return useMemo(() => {
    const needle = q.trim().toLowerCase();
    const match = (s: string) =>
      needle === "" || s.toLowerCase().includes(needle);

    const investigationRows: ResultRow[] = investigations
      .filter((i) => match(i.title) || match(i.summary))
      .slice(0, 6)
      .map((i) => ({ label: i.title, detail: i.summary }));

    const eventRows: ResultRow[] = memory
      .filter((m) => match(m.label) || match(m.detail))
      .slice(0, 8)
      .map((m) => ({
        label: m.label,
        detail: m.detail,
        url: m.url,
      }));

    const fileRows: ResultRow[] = recovery
      ? recovery.urls
          .filter((u) => /\.(py|md|ts|tsx|js|jsx|rs|go|java|sql)$/i.test(u))
          .filter((u) => match(u))
          .slice(0, 6)
          .map((u) => ({ label: basename(u), detail: u }))
      : [];

    const returnRows: ResultRow[] = recovery
      ? recovery.urls
          .filter((u) => /^https?:\/\//.test(u))
          .filter((u) => match(u))
          .slice(0, 6)
          .map((u) => ({ label: hostname(u), detail: u, url: u }))
      : [];

    const groups: ResultGroupT[] = [];
    if (investigationRows.length)
      groups.push({ label: "Investigations", rows: investigationRows });
    if (fileRows.length) groups.push({ label: "Files", rows: fileRows });
    if (returnRows.length) groups.push({ label: "Returns", rows: returnRows });
    if (eventRows.length) groups.push({ label: "Events", rows: eventRows });
    return groups;
  }, [q, recovery, investigations, memory]);
}

function ResultGroup({ group }: { group: ResultGroupT }) {
  return (
    <div style={{ padding: "8px 0" }}>
      <div
        style={{
          padding: "4px 14px 6px",
          fontSize: 9.5,
          fontWeight: 700,
          letterSpacing: "1.4px",
          textTransform: "uppercase",
          color: "var(--ink-3)",
        }}
      >
        {group.label}
      </div>
      {group.rows.map((r, i) => (
        <button
          key={`${r.label}-${i}`}
          onClick={() => r.url && openTab(r.url)}
          disabled={!r.url}
          style={{
            display: "block",
            width: "100%",
            textAlign: "left",
            padding: "8px 14px",
            background: "transparent",
            cursor: r.url ? "pointer" : "default",
            transition: "background var(--motion-fast) var(--motion-ease)",
          }}
          onMouseEnter={(e) =>
            ((e.currentTarget.style.background = "var(--surface-2)"))
          }
          onMouseLeave={(e) =>
            ((e.currentTarget.style.background = "transparent"))
          }
        >
          <div
            style={{
              fontSize: 12.5,
              color: "var(--ink)",
              fontWeight: 500,
              whiteSpace: "nowrap",
              overflow: "hidden",
              textOverflow: "ellipsis",
            }}
          >
            {r.label}
          </div>
          {r.detail && (
            <div
              style={{
                fontSize: 10.5,
                color: "var(--ink-3)",
                whiteSpace: "nowrap",
                overflow: "hidden",
                textOverflow: "ellipsis",
                marginTop: 2,
              }}
            >
              {r.detail}
            </div>
          )}
        </button>
      ))}
    </div>
  );
}

function EmptyResults({ q }: { q: string }) {
  const hasQuery = q.trim().length > 0;
  return (
    <div
      style={{
        padding: "26px 16px",
        textAlign: "center",
        color: "var(--ink-3)",
        fontSize: 12,
      }}
    >
      {hasQuery
        ? `No matches for "${q.slice(0, 32)}".`
        : "Type to search investigations, files, events, or returns."}
    </div>
  );
}

function basename(path: string): string {
  const cleaned = path.replace(/\\/g, "/").replace(/\/+$/, "");
  return cleaned.split("/").pop() || cleaned;
}

function hostname(url: string): string {
  try {
    const u = new URL(url);
    return u.hostname.replace(/^www\./, "");
  } catch {
    return url;
  }
}
