import { motion } from "framer-motion";
import type { Recovery } from "../../lib/types";
import { calm, calmFast } from "../../lib/motion";

/**
 * Phase 7A Continue hero. Full-width, white card, 20-px radius,
 * 6-px lavender accent rail on the left, soft `0 12 32 .06`
 * shadow. Layout:
 *
 *    +------------------------------------------------+
 *    | | CONTINUE                               HIGH  |
 *    | | WebSocket retry debugging                    |
 *    | | 2 tabs - 2 files - reopened after 2d         |
 *    | |                                  [ Resume ]  |
 *    +------------------------------------------------+
 *      ^- 6-px accent rail
 *
 * Capped at 110 px tall per the directive. Only ever one hero —
 * the launcher's HIGH-only gate is enforced upstream.
 */
export function Hero({
  recovery,
  onResume,
}: {
  recovery: Recovery;
  onResume: () => void;
}) {
  const chips = recovery.chips.slice(0, 3);
  return (
    <motion.section
      initial={{ opacity: 0, y: 6 }}
      animate={{ opacity: 1, y: 0 }}
      transition={calm}
      style={{
        position: "relative",
        margin: "0 var(--pad-edge)",
        background: "var(--surface-1)",
        border: "1px solid var(--line)",
        borderRadius: "var(--radius-card)",
        boxShadow: "var(--shadow-soft)",
        padding: "14px 16px 14px 22px",
        maxHeight: 110,
        overflow: "hidden",
      }}
    >
      {/* Accent rail. */}
      <span
        aria-hidden
        style={{
          position: "absolute",
          left: 0,
          top: 10,
          bottom: 10,
          width: 6,
          borderRadius: 4,
          background: "var(--accent)",
        }}
      />

      <div
        style={{
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
          marginBottom: 4,
        }}
      >
        <span
          style={{
            fontSize: 9,
            fontWeight: 700,
            color: "var(--ink-3)",
            letterSpacing: "1.4px",
            textTransform: "uppercase",
          }}
        >
          Continue
        </span>
        <HighBadge />
      </div>

      <div
        style={{
          fontSize: 14,
          fontWeight: 600,
          color: "var(--ink)",
          letterSpacing: "-0.1px",
          whiteSpace: "nowrap",
          overflow: "hidden",
          textOverflow: "ellipsis",
        }}
      >
        {recovery.title}
      </div>

      <div
        style={{
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
          gap: 10,
          marginTop: 8,
        }}
      >
        <div
          style={{
            display: "flex",
            gap: 6,
            flexWrap: "nowrap",
            overflow: "hidden",
          }}
        >
          {chips.map((c) => (
            <span
              key={c}
              style={{
                display: "inline-flex",
                alignItems: "center",
                height: 20,
                padding: "0 8px",
                borderRadius: 7,
                background: "var(--surface-0)",
                color: "var(--ink-3)",
                border: "1px solid var(--line)",
                fontSize: 10.5,
                fontWeight: 600,
                letterSpacing: "0.2px",
                whiteSpace: "nowrap",
              }}
            >
              {c}
            </span>
          ))}
        </div>
        <ResumeButton onClick={onResume} />
      </div>
    </motion.section>
  );
}

function HighBadge() {
  return (
    <span
      aria-label="High-confidence recovery"
      style={{
        display: "inline-flex",
        alignItems: "center",
        height: 16,
        padding: "0 7px",
        borderRadius: 6,
        background: "var(--accent-soft)",
        color: "var(--accent)",
        fontSize: 9,
        fontWeight: 700,
        letterSpacing: "1px",
      }}
    >
      HIGH
    </span>
  );
}

function ResumeButton({ onClick }: { onClick: () => void }) {
  return (
    <motion.button
      whileHover={{ y: -1 }}
      whileTap={{ scale: 0.985 }}
      transition={calmFast}
      onClick={onClick}
      style={{
        display: "inline-flex",
        alignItems: "center",
        gap: 6,
        height: 30,
        padding: "0 14px",
        borderRadius: 9,
        background: "var(--accent)",
        color: "white",
        fontSize: 12,
        fontWeight: 600,
        letterSpacing: "0.1px",
        boxShadow: "0 4px 12px rgba(191, 59, 43, 0.28)",
      }}
    >
      Resume
      <span
        aria-hidden
        style={{
          fontFamily:
            '"Geist Mono", ui-monospace, SFMono-Regular, Menlo, Consolas, monospace',
          background: "rgba(255, 255, 255, 0.22)",
          color: "white",
          fontSize: 9.5,
          fontWeight: 700,
          padding: "1px 5px",
          borderRadius: 4,
          letterSpacing: 0,
        }}
      >
        1
      </span>
    </motion.button>
  );
}
