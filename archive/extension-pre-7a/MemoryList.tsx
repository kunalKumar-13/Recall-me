import { motion } from "framer-motion";
import { calmFast } from "../lib/motion";
import { openTab } from "../lib/api";
import type { MemoryItem, MemoryKind } from "../lib/types";
import { Icon } from "./icons";


/**
 * Phase 6C - kind glyph for the activity rail. Same vocabulary as
 * the launcher digest: a small stroked icon, not a filled badge.
 */
function GlyphFor({ kind }: { kind: MemoryKind }) {
  if (kind === "search") return <Icon.search size={12} />;
  if (kind === "chat") return <Icon.chat size={12} />;
  return <Icon.tab size={12} />;
}


function _kindLabel(kind: MemoryKind): string {
  if (kind === "search") return "Search";
  if (kind === "chat") return "Chat";
  return "Tab";
}


/**
 * Phase 6C — HH:MM time stamp in local time. Pure display: the API
 * provides epoch seconds on `ts`; we never invent one. If `ts` is
 * absent the row is dropped silently (no placeholder).
 */
function _hhmm(ts: number): string {
  const d = new Date(ts * 1000);
  const h = String(d.getHours()).padStart(2, "0");
  const m = String(d.getMinutes()).padStart(2, "0");
  return `${h}:${m}`;
}


/**
 * Phase 6C Activity rail. A single chronological vertical timeline
 * of the day's captured surfaces — searches, tabs, chats — sorted
 * newest first. Replaces the prior grouped layout (Searches / Tabs
 * / Chats). The timeline answers "what did I touch today?" in the
 * same shape as the launcher digest: small marker, mono time stamp,
 * one short label per row.
 *
 * Rows without a real timestamp are dropped — the popup never
 * invents one.
 */
export function MemoryList({ items }: { items: MemoryItem[] }) {
  const dated = items
    .filter((it) => typeof it.ts === "number")
    .sort((a, b) => (b.ts ?? 0) - (a.ts ?? 0))
    .slice(0, 8);

  if (dated.length === 0) {
    return (
      <div
        className="card"
        style={{
          padding: "14px 14px",
          fontSize: 12,
          color: "var(--ink-3)",
        }}
      >
        No browser memory captured yet.
      </div>
    );
  }

  return (
    <div className="card" style={{ overflow: "hidden" }}>
      <div style={{ position: "relative", padding: "8px 0 8px" }}>
        {/* the vertical hairline that ties the rail together */}
        <span
          aria-hidden
          style={{
            position: "absolute",
            left: 22,
            top: 8,
            bottom: 8,
            width: 1,
            background: "var(--line)",
          }}
        />
        {dated.map((it, i) => (
          <motion.button
            key={`${it.kind}-${i}-${it.ts}`}
            className="row-button"
            whileHover={{ x: 1 }}
            transition={calmFast}
            onClick={() => it.url && openTab(it.url)}
            style={{
              display: "flex",
              alignItems: "center",
              gap: 10,
              padding: "6px 13px",
              width: "100%",
              textAlign: "left",
              background: "transparent",
              border: "none",
            }}
          >
            <span
              style={{
                flexShrink: 0,
                width: 42,
                fontSize: 10.5,
                color: "var(--ink-4)",
                fontFamily:
                  "ui-monospace, SFMono-Regular, Menlo, Consolas, monospace",
              }}
            >
              {_hhmm(it.ts as number)}
            </span>
            <span
              aria-hidden
              style={{
                flexShrink: 0,
                width: 18,
                height: 18,
                borderRadius: 9,
                background: "var(--surface-1)",
                border: "1px solid var(--line)",
                display: "inline-flex",
                alignItems: "center",
                justifyContent: "center",
                color: "var(--ink-3)",
                zIndex: 1,
              }}
            >
              <GlyphFor kind={it.kind} />
            </span>
            <span style={{ minWidth: 0, flex: 1 }}>
              <span
                style={{
                  display: "block",
                  fontSize: 12.5,
                  color: "var(--ink)",
                  whiteSpace: "nowrap",
                  overflow: "hidden",
                  textOverflow: "ellipsis",
                }}
              >
                <span style={{ color: "var(--ink-3)", marginRight: 6 }}>
                  {_kindLabel(it.kind)}
                </span>
                {it.label}
              </span>
              {it.detail && (
                <span
                  style={{
                    display: "block",
                    fontSize: 10.5,
                    color: "var(--ink-4)",
                    whiteSpace: "nowrap",
                    overflow: "hidden",
                    textOverflow: "ellipsis",
                  }}
                >
                  {it.detail}
                </span>
              )}
            </span>
          </motion.button>
        ))}
      </div>
    </div>
  );
}
