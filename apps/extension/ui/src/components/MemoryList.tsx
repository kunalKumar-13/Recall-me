import { motion } from "framer-motion";
import { calmFast } from "../lib/motion";
import { openTab } from "../lib/api";
import type { MemoryItem, MemoryKind } from "../lib/types";
import { Icon } from "./icons";

const GROUPS: { kind: MemoryKind; label: string }[] = [
  { kind: "search", label: "Searches" },
  { kind: "tab", label: "Tabs" },
  { kind: "chat", label: "Chats" },
];

function GlyphFor({ kind }: { kind: MemoryKind }) {
  if (kind === "search") return <Icon.search size={14} />;
  if (kind === "chat") return <Icon.chat size={14} />;
  return <Icon.tab size={14} />;
}

/**
 * Recent browser memory, grouped by surface — searches, tabs, chats.
 * This is the quiet "what did I touch" layer, deliberately below the
 * investigation surfaces: it answers a smaller question. Each group
 * shows at most three rows so the popup never turns into a history
 * log.
 */
export function MemoryList({ items }: { items: MemoryItem[] }) {
  const groups = GROUPS.map((g) => ({
    ...g,
    rows: items.filter((it) => it.kind === g.kind).slice(0, 3),
  })).filter((g) => g.rows.length > 0);

  if (groups.length === 0) {
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
      {groups.map((g, gi) => (
        <div key={g.kind}>
          <div
            style={{
              padding: "9px 13px 5px",
              fontSize: 10,
              fontWeight: 600,
              letterSpacing: "0.7px",
              textTransform: "uppercase",
              color: "var(--ink-4)",
              borderTop: gi === 0 ? "none" : "1px solid var(--line)",
            }}
          >
            {g.label}
          </div>
          {g.rows.map((it, i) => (
            <motion.button
              key={`${g.kind}-${i}`}
              className="row-button"
              whileHover={{ x: 1 }}
              transition={calmFast}
              onClick={() => it.url && openTab(it.url)}
              style={{
                display: "flex",
                alignItems: "center",
                gap: 10,
                padding: "8px 13px",
              }}
            >
              <span style={{ flexShrink: 0, color: "var(--ink-3)" }}>
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
      ))}
    </div>
  );
}
