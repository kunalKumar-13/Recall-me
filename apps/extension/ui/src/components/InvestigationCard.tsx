import { motion } from "framer-motion";
import { calmFast } from "../lib/motion";
import type { Investigation } from "../lib/types";
import { Icon } from "./icons";


/**
 * Phase 6C investigation pill. One ongoing investigation rendered as
 * a small horizontal pill, not a full card row. The strip of pills
 * answers "what topics are alive right now?" at a glance — never the
 * single thing to *act on* (that's the Continue card), just the
 * topology of the user's current thinking.
 *
 * Cap of four at the call site so the strip never wraps awkwardly
 * or scrolls horizontally; surplus topics fall off the bottom.
 */
export function InvestigationCard({
  investigation,
  index = 0,
}: {
  investigation: Investigation;
  index?: number;
}) {
  return (
    <motion.div
      initial={{ opacity: 0, x: -6 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ ...calmFast, delay: index * 0.04 }}
      whileHover={{ y: -1 }}
      title={investigation.summary || investigation.title}
      style={{
        display: "inline-flex",
        alignItems: "center",
        gap: 7,
        height: 28,
        padding: "0 12px 0 10px",
        borderRadius: 14,
        background: "var(--surface-1)",
        border: "1px solid var(--line)",
        color: "var(--ink)",
        fontSize: 12,
        fontWeight: 500,
        cursor: "default",
        maxWidth: 180,
      }}
    >
      <span
        style={{
          flexShrink: 0,
          color: "var(--ink-3)",
          display: "inline-flex",
        }}
      >
        <Icon.thread size={12} />
      </span>
      <span
        style={{
          minWidth: 0,
          overflow: "hidden",
          textOverflow: "ellipsis",
          whiteSpace: "nowrap",
        }}
      >
        {investigation.title}
      </span>
    </motion.div>
  );
}
