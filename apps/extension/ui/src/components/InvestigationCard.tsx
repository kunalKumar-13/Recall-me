import { motion } from "framer-motion";
import { calmFast } from "../lib/motion";
import type { Investigation } from "../lib/types";
import { Icon } from "./icons";

const SURFACE_LABEL: Record<string, string> = {
  browser_visit: "tabs",
  browser_search: "searches",
  chat_session: "chats",
  open: "files",
  reveal: "files",
  query: "lookups",
};

/**
 * One ongoing investigation — a topic still alive but not the single
 * thing to resume right now. Rendered as a quiet row inside a shared
 * card; the list is capped at four so this never becomes a feed.
 */
export function InvestigationCard({
  investigation,
  last,
}: {
  investigation: Investigation;
  last: boolean;
}) {
  const surfaces = Array.from(
    new Set(
      investigation.surfaces
        .map((s) => SURFACE_LABEL[s])
        .filter(Boolean),
    ),
  );

  return (
    <motion.div
      className="row-button"
      whileHover={{ x: 1 }}
      transition={calmFast}
      style={{
        display: "flex",
        gap: 11,
        padding: "11px 13px",
        borderBottom: last ? "none" : "1px solid var(--line)",
      }}
    >
      <span
        style={{
          flexShrink: 0,
          width: 28,
          height: 28,
          borderRadius: 8,
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          background: "var(--surface-sunken)",
          color: "var(--ink-3)",
        }}
      >
        <Icon.thread size={15} />
      </span>
      <span style={{ minWidth: 0, flex: 1 }}>
        <span
          style={{
            display: "block",
            fontSize: 13,
            fontWeight: 600,
            color: "var(--ink)",
            whiteSpace: "nowrap",
            overflow: "hidden",
            textOverflow: "ellipsis",
          }}
        >
          {investigation.title}
        </span>
        <span
          style={{
            display: "block",
            marginTop: 2,
            fontSize: 11,
            color: "var(--ink-3)",
          }}
        >
          {investigation.summary || surfaces.join(" · ") || "Active"}
        </span>
      </span>
    </motion.div>
  );
}
