import { motion } from "framer-motion";
import { calmFast } from "../lib/motion";
import type { Recovery } from "../lib/types";
import { Icon } from "./icons";

/**
 * The popup's hero. One card, one investigation — the single
 * strongest interrupted thread the daemon found. Not a list, not a
 * feed: the answer to "what was I doing?" the moment the popup opens.
 *
 * The card is accent-tinted so it reads as *the* thing to act on,
 * but it stays calm — soft fill, one button, no glow.
 */
export function ContinueCard({
  recovery,
  onResume,
}: {
  recovery: Recovery;
  onResume: () => void;
}) {
  // The caption chips that describe *return intent* (a gap, a
  // revisit) — the trust cue for "why this surfaced".
  const reason = recovery.chips.find(
    (c) => /gap|revisit|interrupt/i.test(c),
  );

  return (
    <div
      className="card"
      style={{
        background: "var(--accent-soft)",
        borderColor: "var(--accent-line)",
        padding: "16px 16px 14px",
      }}
    >
      <div
        style={{
          display: "flex",
          alignItems: "center",
          gap: 7,
          fontSize: 10,
          fontWeight: 600,
          letterSpacing: "0.9px",
          textTransform: "uppercase",
          color: "var(--accent)",
        }}
      >
        <span
          style={{
            width: 6,
            height: 6,
            borderRadius: 3,
            background: "var(--accent)",
          }}
        />
        Continue
      </div>

      <div
        style={{
          marginTop: 9,
          fontSize: 15,
          fontWeight: 600,
          lineHeight: 1.3,
          color: "var(--ink)",
        }}
      >
        {recovery.title}
      </div>

      <div
        style={{
          display: "flex",
          flexWrap: "wrap",
          gap: 6,
          marginTop: 11,
        }}
      >
        {recovery.tabCount > 0 && (
          <span className="chip">
            <Icon.tab size={12} />
            <span style={{ marginLeft: 5 }}>
              {recovery.tabCount} tab{recovery.tabCount === 1 ? "" : "s"}
            </span>
          </span>
        )}
        {recovery.fileCount > 0 && (
          <span className="chip">
            <Icon.file size={12} />
            <span style={{ marginLeft: 5 }}>
              {recovery.fileCount} file{recovery.fileCount === 1 ? "" : "s"}
            </span>
          </span>
        )}
        {reason && <span className="chip accent">{reason}</span>}
      </div>

      <div
        style={{
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
          gap: 12,
          marginTop: 14,
        }}
      >
        <span
          style={{
            fontSize: 11,
            color: "var(--ink-3)",
            lineHeight: 1.45,
          }}
        >
          Surfaced because you left this mid-flow.
        </span>
        <motion.button
          whileHover={{ y: -1 }}
          whileTap={{ y: 0 }}
          transition={calmFast}
          onClick={onResume}
          style={{
            display: "inline-flex",
            alignItems: "center",
            gap: 6,
            flexShrink: 0,
            height: 34,
            padding: "0 16px",
            borderRadius: 9,
            background: "var(--accent)",
            color: "#fff",
            fontSize: 13,
            fontWeight: 600,
          }}
        >
          <Icon.resume size={15} />
          Resume
        </motion.button>
      </div>
    </div>
  );
}
