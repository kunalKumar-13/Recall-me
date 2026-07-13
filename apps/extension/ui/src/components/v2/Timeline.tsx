import { motion } from "framer-motion";
import type { MemoryItem } from "../../lib/types";
import { calm, staggered } from "../../lib/motion";
import { openTab } from "../../lib/api";
import { SectionLabel } from "./Investigations";

/**
 * Phase 7A Today timeline. Replaces the *"No browser memory
 * captured yet"* prose with a vertical rail:
 *
 *    09:12   ChatGPT          prompt engineering notes
 *    10:41   GitHub           backoff retry article
 *    13:10   StackOverflow    websocket reconnect
 *
 * Each row is one captured event. Clicking re-opens the source
 * URL when one is present.
 */
export function Timeline({ items }: { items: MemoryItem[] }) {
  if (items.length === 0) {
    return (
      <section style={{ margin: "0 var(--pad-edge)" }}>
        <SectionLabel label="Today" />
        <EmptyRail />
      </section>
    );
  }
  // Newest first; capped at the day so the rail stays a *today*
  // surface, not a feed.
  const today = items.slice(0, 8);
  return (
    <section style={{ margin: "0 var(--pad-edge)" }}>
      <SectionLabel label="Today" count={today.length} />
      <div
        style={{
          background: "var(--surface-1)",
          border: "1px solid var(--line)",
          borderRadius: "var(--radius-card)",
          boxShadow: "var(--shadow-soft)",
          padding: "10px 0",
        }}
      >
        {today.map((it, i) => (
          <Row key={`${it.label}-${i}`} item={it} index={i} />
        ))}
      </div>
    </section>
  );
}

function Row({ item, index }: { item: MemoryItem; index: number }) {
  const time = formatTime(item.ts);
  const source = item.detail || sourceFor(item.kind);
  const onClick = item.url
    ? () => openTab(item.url as string)
    : undefined;
  return (
    <motion.div
      initial={{ opacity: 0, y: 4 }}
      animate={{ opacity: 1, y: 0 }}
      transition={staggered(index)}
      onClick={onClick}
      role={onClick ? "button" : undefined}
      tabIndex={onClick ? 0 : undefined}
      style={{
        display: "grid",
        gridTemplateColumns: "44px 88px 1fr",
        alignItems: "center",
        columnGap: 10,
        padding: "8px 16px",
        cursor: onClick ? "pointer" : "default",
        transition: "background var(--motion-fast) var(--motion-ease)",
      }}
      onMouseEnter={(e) =>
        ((e.currentTarget.style.background = "var(--surface-2)"))
      }
      onMouseLeave={(e) =>
        ((e.currentTarget.style.background = "transparent"))
      }
    >
      <span
        style={{
          fontFamily:
            '"Geist Mono", ui-monospace, SFMono-Regular, Menlo, Consolas, monospace',
          fontSize: 11,
          color: "var(--ink-3)",
          letterSpacing: "0.2px",
        }}
      >
        {time}
      </span>
      <span
        style={{
          fontSize: 11,
          fontWeight: 600,
          color: "var(--ink-2)",
          whiteSpace: "nowrap",
          overflow: "hidden",
          textOverflow: "ellipsis",
        }}
      >
        {source}
      </span>
      <span
        style={{
          fontSize: 12,
          color: "var(--ink)",
          whiteSpace: "nowrap",
          overflow: "hidden",
          textOverflow: "ellipsis",
        }}
      >
        {item.label}
      </span>
    </motion.div>
  );
}

function EmptyRail() {
  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={calm}
      style={{
        background: "var(--surface-1)",
        border: "1px dashed var(--line-strong)",
        borderRadius: "var(--radius-card)",
        padding: "22px 16px",
        textAlign: "center",
        color: "var(--ink-3)",
      }}
    >
      <RailGlyph />
      <div
        style={{
          marginTop: 10,
          fontSize: 12,
          fontWeight: 600,
          color: "var(--ink-2)",
        }}
      >
        Today is quiet so far.
      </div>
      <div style={{ marginTop: 4, fontSize: 11, color: "var(--ink-3)" }}>
        Browse normally — Recall fills the rail as you work.
      </div>
    </motion.div>
  );
}

function RailGlyph() {
  return (
    <svg
      width={36}
      height={36}
      viewBox="0 0 36 36"
      fill="none"
      aria-hidden
      style={{ margin: "0 auto", display: "block" }}
    >
      <line
        x1="10"
        y1="6"
        x2="10"
        y2="30"
        stroke="var(--accent-line)"
        strokeWidth={1.5}
        strokeLinecap="round"
      />
      <circle cx="10" cy="10" r="2.4" fill="var(--accent)" />
      <circle cx="10" cy="18" r="2.4" fill="var(--accent)" opacity="0.55" />
      <circle cx="10" cy="26" r="2.4" fill="var(--accent)" opacity="0.32" />
      <line
        x1="16"
        y1="10"
        x2="28"
        y2="10"
        stroke="var(--ink-4)"
        strokeWidth={1.4}
        strokeLinecap="round"
      />
      <line
        x1="16"
        y1="18"
        x2="24"
        y2="18"
        stroke="var(--ink-4)"
        strokeWidth={1.4}
        strokeLinecap="round"
        opacity="0.55"
      />
      <line
        x1="16"
        y1="26"
        x2="26"
        y2="26"
        stroke="var(--ink-4)"
        strokeWidth={1.4}
        strokeLinecap="round"
        opacity="0.32"
      />
    </svg>
  );
}

function formatTime(ts?: number): string {
  if (!ts) return "--:--";
  const d = new Date(ts * 1000);
  const hh = d.getHours().toString().padStart(2, "0");
  const mm = d.getMinutes().toString().padStart(2, "0");
  return `${hh}:${mm}`;
}

function sourceFor(kind: MemoryItem["kind"]): string {
  if (kind === "search") return "Search";
  if (kind === "chat") return "Chat";
  return "Browser";
}
