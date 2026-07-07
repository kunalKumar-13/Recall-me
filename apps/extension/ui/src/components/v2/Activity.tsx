import { motion } from "framer-motion";
import type { ConnectionState, TodaySummary } from "../../lib/types";
import { staggered } from "../../lib/motion";
import { SectionLabel } from "./Investigations";

/**
 * Activity status cards — live numbers, never vibes. Two cards
 * side-by-side, both driven by the `/v1/events/today` per-kind
 * tally (the same ground truth as the trust-strip pill):
 *
 *    +--------------------+   +--------------------+
 *    | BROWSER  capturing |   | DESKTOP     off    |
 *    | 46  pages          |   | 12  app focus      |
 *    |  2  searches       |   |  3  file opens     |
 *    |  3  chats          |   |     opt-in · app   |
 *    |  9  dwells         |   |                    |
 *    +--------------------+   +--------------------+
 *
 * A layer that captured nothing today says 0 (or "off" for the
 * opt-in desktop watcher) — it never pretends, in either direction.
 */

export type ActivityKind = "capturing" | "idle" | "disconnected" | "off";

const KIND_PALETTE: Record<ActivityKind, { fg: string; bg: string; label: string }> = {
  capturing: { fg: "var(--ok)", bg: "var(--ok-soft)", label: "capturing" },
  idle: { fg: "var(--ink-3)", bg: "var(--surface-2)", label: "idle" },
  disconnected: { fg: "var(--warn)", bg: "var(--warn-soft)", label: "offline" },
  off: { fg: "var(--ink-3)", bg: "var(--surface-2)", label: "off" },
};

interface CountItem {
  n: number | null; // null = a label row, no number column
  label: string;
}

export function Activity({
  connection,
  today,
}: {
  connection: ConnectionState;
  today: TodaySummary | null;
}) {
  const kinds = today?.kinds ?? {};
  const pages = kinds.browser_visit ?? 0;
  const searches = kinds.browser_search ?? 0;
  const chats = kinds.chat_session ?? 0;
  const dwells = kinds.browser_focus ?? 0;
  const appFocus = kinds.desktop_window ?? 0;
  const fileOpens = (kinds.open ?? 0) + (kinds.reveal ?? 0);

  const off = connection !== "connected";
  const browserKind: ActivityKind = off
    ? "disconnected"
    : pages + searches + chats + dwells > 0
      ? "capturing"
      : "idle";
  const desktopKind: ActivityKind = off
    ? "disconnected"
    : appFocus + fileOpens > 0
      ? "capturing"
      : "off";

  const browserItems: CountItem[] = [
    { n: pages, label: pages === 1 ? "page" : "pages" },
    { n: searches, label: searches === 1 ? "search" : "searches" },
    { n: chats, label: chats === 1 ? "chat" : "chats" },
    { n: dwells, label: dwells === 1 ? "dwell" : "dwells" },
  ];
  const desktopItems: CountItem[] =
    desktopKind === "capturing"
      ? [
          { n: appFocus, label: "app focus" },
          { n: fileOpens, label: fileOpens === 1 ? "file open" : "file opens" },
        ]
      : [
          { n: null, label: "app focus · opt-in" },
          { n: null, label: "VS Code companion" },
          { n: null, label: "enable in the Recall app" },
        ];

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
          items={browserItems}
          index={0}
        />
        <ActivityCard
          title="Desktop"
          kind={desktopKind}
          items={desktopItems}
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
  items: CountItem[];
  index: number;
}) {
  const dim = kind === "off" || kind === "disconnected";
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
            key={it.label}
            style={{
              display: "flex",
              alignItems: "baseline",
              gap: 7,
              fontSize: 11.5,
              color: dim ? "var(--ink-3)" : "var(--ink-2)",
            }}
          >
            {it.n === null ? (
              <span
                aria-hidden
                style={{
                  width: 4,
                  height: 4,
                  borderRadius: 2,
                  background: "var(--ink-4)",
                  opacity: 0.55,
                  flexShrink: 0,
                  alignSelf: "center",
                }}
              />
            ) : (
              <span
                style={{
                  minWidth: 22,
                  textAlign: "right",
                  fontFamily:
                    "ui-monospace, SFMono-Regular, Menlo, Consolas, monospace",
                  fontSize: 11,
                  fontWeight: 600,
                  color:
                    it.n > 0 && !dim ? "var(--ink)" : "var(--ink-4)",
                  fontVariantNumeric: "tabular-nums",
                }}
              >
                {it.n}
              </span>
            )}
            {it.label}
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
