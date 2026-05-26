import { motion } from "framer-motion";
import type { ConnectionState } from "../../lib/types";
import { calm } from "../../lib/motion";
import { Icon } from "../icons";

/**
 * Phase 7A header. Left side: lavender Recall mark + small daemon
 * dot + two-line wordmark/subtitle. Right side: Search + Settings
 * icon buttons. No empty whitespace, no badge clutter, no event
 * count next to the wordmark.
 *
 * The daemon dot uses the same palette as the page footer so a
 * user glancing at the top of the popup gets the same trust signal
 * the bottom carries.
 */
export function Header({
  connection,
  onSearch,
  onSettings,
}: {
  connection: ConnectionState;
  onSearch: () => void;
  onSettings: () => void;
}) {
  const alive = connection === "connected";
  const dotColor = alive
    ? "var(--ok)"
    : connection === "disconnected" || connection === "reconnecting"
      ? "var(--warn)"
      : "var(--ink-4)";
  const subtitle =
    connection === "connected"
      ? "Connected locally"
      : connection === "reconnecting"
        ? "Reconnecting…"
        : connection === "disconnected"
          ? "Daemon not running"
          : connection === "offline"
            ? "Browser is offline"
            : "Connecting…";

  return (
    <header
      style={{
        display: "flex",
        alignItems: "center",
        gap: 12,
        padding: "16px 18px 14px",
        borderBottom: "1px solid var(--line)",
        background: "var(--surface-0)",
      }}
    >
      <span
        aria-hidden
        style={{
          width: 26,
          height: 26,
          borderRadius: 8,
          background: "linear-gradient(135deg, #b5a8ff, #8b7fe3)",
          flexShrink: 0,
          boxShadow: "0 4px 10px rgba(139, 127, 227, 0.30)",
        }}
      />
      <div
        style={{
          display: "flex",
          flexDirection: "column",
          gap: 1,
          minWidth: 0,
        }}
      >
        <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
          <span
            style={{
              fontSize: 14,
              fontWeight: 600,
              color: "var(--ink)",
              letterSpacing: "-0.1px",
            }}
          >
            Recall
          </span>
          <motion.span
            role="status"
            aria-label={`daemon ${connection}`}
            animate={alive ? { opacity: [0.45, 1, 0.45] } : { opacity: 1 }}
            transition={
              alive
                ? { duration: 1.6, repeat: Infinity, ease: "easeInOut" }
                : { duration: 0 }
            }
            style={{
              width: 7,
              height: 7,
              borderRadius: 4,
              background: dotColor,
              boxShadow: alive
                ? "0 0 0 3px rgba(79, 167, 132, 0.18)"
                : "none",
            }}
          />
        </div>
        <span
          style={{
            fontSize: 11,
            color: "var(--ink-3)",
            letterSpacing: "0.1px",
          }}
        >
          {subtitle}
        </span>
      </div>
      <span style={{ flex: 1 }} />
      <IconButton
        label="Search"
        title="Search (Ctrl+K)"
        onClick={onSearch}
        icon={<Icon.search size={16} />}
      />
      <IconButton
        label="Settings"
        onClick={onSettings}
        icon={<Icon.gear size={17} />}
      />
    </header>
  );
}

function IconButton({
  icon,
  label,
  title,
  onClick,
}: {
  icon: React.ReactNode;
  label: string;
  title?: string;
  onClick: () => void;
}) {
  return (
    <motion.button
      whileHover={{ y: -1, background: "var(--surface-2)" }}
      transition={calm}
      onClick={onClick}
      aria-label={label}
      title={title ?? label}
      style={{
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        width: 30,
        height: 30,
        borderRadius: 9,
        color: "var(--ink-2)",
      }}
    >
      {icon}
    </motion.button>
  );
}
