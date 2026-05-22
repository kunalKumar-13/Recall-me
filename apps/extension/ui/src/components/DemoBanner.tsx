import { motion } from "framer-motion";
import { calmFast } from "../lib/motion";


/**
 * Phase 6D — trust banner shown atop the demo overlay. Calm
 * lavender-tinted strip with a hairline border, a two-line message
 * (*Example data* / *Nothing here came from your device.*), and a
 * Dismiss action that flips the overlay off via
 * `lib/api.ts → dismissDemo()`.
 *
 * Visual rules:
 *   - never red, never alarming — the demo is a trust statement,
 *     not a warning
 *   - height matches a regular section header so the banner reads
 *     as part of the popup rhythm
 *   - the Dismiss link is right-aligned so the eye lands on the
 *     trust statement first
 */
export function DemoBanner({
  title,
  body,
  onDismiss,
}: {
  title: string;
  body: string;
  onDismiss: () => void;
}) {
  return (
    <motion.div
      initial={{ opacity: 0, y: -4 }}
      animate={{ opacity: 1, y: 0 }}
      transition={calmFast}
      style={{
        display: "flex",
        alignItems: "center",
        gap: 12,
        margin: "0 20px 14px",
        padding: "10px 12px",
        background: "var(--accent-soft)",
        border: "1px solid var(--accent-line)",
        borderRadius: 10,
      }}
    >
      <span
        aria-hidden
        style={{
          flexShrink: 0,
          width: 8,
          height: 8,
          borderRadius: 4,
          background: "var(--accent)",
        }}
      />
      <span style={{ minWidth: 0, flex: 1, lineHeight: 1.35 }}>
        <span
          style={{
            display: "inline",
            color: "var(--ink)",
            fontSize: 11.5,
            fontWeight: 600,
            marginRight: 6,
          }}
        >
          {title}
        </span>
        <span
          style={{
            display: "inline",
            color: "var(--ink-3)",
            fontSize: 11.5,
          }}
        >
          {body}
        </span>
      </span>
      <motion.button
        whileHover={{ y: -1 }}
        whileTap={{ y: 0 }}
        transition={calmFast}
        onClick={onDismiss}
        aria-label="Dismiss demo overlay"
        style={{
          flexShrink: 0,
          background: "transparent",
          color: "var(--accent)",
          fontSize: 11.5,
          fontWeight: 600,
          padding: "2px 4px",
          border: "none",
          cursor: "pointer",
        }}
      >
        Dismiss
      </motion.button>
    </motion.div>
  );
}
