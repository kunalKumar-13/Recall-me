import { motion } from "framer-motion";
import type { ConnectionState } from "../../lib/types";
import { staggered } from "../../lib/motion";
import { SectionLabel } from "./Investigations";

/**
 * Phase 7A Activity status cards. Two cards side-by-side: Browser
 * (live engine) and Desktop (designed-now, engine-later). Each
 * carries a one-word status pill + a short list of what the layer
 * watches:
 *
 *    +-------------------+   +-------------------+
 *    | BROWSER  capturing |   | DESKTOP  future   |
 *    | - tabs             |   | - files           |
 *    | - navigation       |   | - editors         |
 *    | - returns          |   | - integrations    |
 *    | - searches         |   |                   |
 *    +-------------------+   +-------------------+
 *
 * The directive is explicit: *Design UI now. Engine later.* The
 * Desktop card surfaces the seam without pretending the layer
 * exists.
 */

export type ActivityKind = "capturing" | "idle" | "disconnected" | "future";

const KIND_PALETTE: Record<ActivityKind, { fg: string; bg: string; label: string }> = {
  capturing: { fg: "var(--ok)", bg: "var(--ok-soft)", label: "capturing" },
  idle: { fg: "var(--ink-3)", bg: "var(--surface-2)", label: "idle" },
  disconnected: { fg: "var(--warn)", bg: "var(--warn-soft)", label: "offline" },
  future: { fg: "var(--accent)", bg: "var(--accent-soft)", label: "soon" },
};

export function Activity({
  connection,
  eventsToday,
  desktopApps,
}: {
  connection: ConnectionState;
  eventsToday: number;
  desktopApps: number;
}) {
  const browserKind: ActivityKind =
    connection !== "connected"
      ? "disconnected"
      : eventsToday > 0
        ? "capturing"
        : "idle";

  const desktopKind: ActivityKind =
    connection !== "connected"
      ? "disconnected"
      : desktopApps > 0
        ? "capturing"
        : "future";

  return (
    <section style={{ margin: "0 var(--pad-edge)" }}>
      <SectionLabel label="Activity" />
      <div
        style={{
          display: "grid",
          gridTemplateColumns: "1fr 1fr",
          gap: 10,
        }}
      >
        <ActivityCard
          title="Browser"
          kind={browserKind}
          items={["tabs", "navigation", "returns", "searches"]}
          index={0}
        />
        <ActivityCard
          title="Desktop"
          kind={desktopKind}
          items={["files", "editors", "integrations"]}
          index={1}
        />
      </div>
    </section>
  );
}

function ActivityCard({
  title,
  kind,
  items,
  index,
}: {
  title: string;
  kind: ActivityKind;
  items: string[];
  index: number;
}) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 6 }}
      animate={{ opacity: 1, y: 0 }}
      transition={staggered(index)}
      style={{
        background: "var(--surface-1)",
        border: "1px solid var(--line)",
        borderRadius: "var(--radius-card)",
        boxShadow: "var(--shadow-soft)",
        padding: "12px 14px",
      }}
    >
      <div
        style={{
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
          marginBottom: 10,
        }}
      >
        <span
          style={{
            fontSize: 10,
            fontWeight: 700,
            color: "var(--ink-3)",
            letterSpacing: "1.4px",
            textTransform: "uppercase",
          }}
        >
          {title}
        </span>
        <StatusPill kind={kind} />
      </div>
      <ul
        style={{
          margin: 0,
          padding: 0,
          listStyle: "none",
          display: "flex",
          flexDirection: "column",
          gap: 4,
        }}
      >
        {items.map((it) => (
          <li
            key={it}
            style={{
              display: "flex",
              alignItems: "center",
              gap: 8,
              fontSize: 11.5,
              color: kind === "future" ? "var(--ink-3)" : "var(--ink-2)",
            }}
          >
            <span
              aria-hidden
              style={{
                width: 4,
                height: 4,
                borderRadius: 2,
                background:
                  kind === "future" ? "var(--ink-4)" : "var(--accent)",
                opacity: kind === "future" ? 0.55 : 0.8,
                flexShrink: 0,
              }}
            />
            {it}
          </li>
        ))}
      </ul>
    </motion.div>
  );
}

function StatusPill({ kind }: { kind: ActivityKind }) {
  const p = KIND_PALETTE[kind];
  return (
    <span
      style={{
        display: "inline-flex",
        alignItems: "center",
        height: 16,
        padding: "0 7px",
        borderRadius: 6,
        background: p.bg,
        color: p.fg,
        fontSize: 9,
        fontWeight: 700,
        letterSpacing: "1px",
        textTransform: "uppercase",
      }}
    >
      {p.label}
    </span>
  );
}
