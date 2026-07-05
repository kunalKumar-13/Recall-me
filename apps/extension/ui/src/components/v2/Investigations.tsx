import { motion } from "framer-motion";
import type { Investigation } from "../../lib/types";
import { calm, staggered } from "../../lib/motion";

/**
 * Phase 7A investigations strip. Replaces the 6C horizontal pill
 * cluster with vertical stacked cards. Each row is 48 px tall:
 * title (one line) + last-seen caption + strength dot on the left
 * + quiet right chevron. Max 4 rows; anything past the fourth
 * earns the strip a scroll handle (rather than overflowing the
 * popup).
 */
export function Investigations({
  investigations,
}: {
  investigations: Investigation[];
}) {
  if (investigations.length === 0) return null;
  return (
    <section
      style={{
        margin: "0 var(--pad-edge)",
      }}
    >
      <SectionLabel
        label="Active investigations"
        count={investigations.length}
      />
      <div
        style={{
          background: "var(--surface-1)",
          border: "1px solid var(--line)",
          borderRadius: "var(--radius-card)",
          boxShadow: "var(--shadow-soft)",
          overflow: "hidden",
          maxHeight: 4 * 48,
          overflowY: investigations.length > 4 ? "auto" : "hidden",
        }}
        className={investigations.length > 4 ? "scroll-area" : undefined}
      >
        {investigations.slice(0, 12).map((inv, i) => (
          <motion.button
            key={inv.id || i}
            initial={{ opacity: 0, y: 4 }}
            animate={{ opacity: 1, y: 0 }}
            transition={staggered(i)}
            whileHover={{ background: "var(--surface-2)" }}
            // hover transition rides the global calm curve
            style={{
              display: "flex",
              alignItems: "center",
              gap: 12,
              width: "100%",
              height: 48,
              padding: "0 16px",
              borderBottom:
                i < investigations.length - 1 && i < 11
                  ? "1px solid var(--line)"
                  : "none",
              background: "transparent",
              textAlign: "left",
              transition: "background var(--motion-fast) var(--motion-ease)",
            }}
          >
            <StrengthDot strong={inv.surfaces.length >= 3} />
            <div
              style={{
                flex: 1,
                display: "flex",
                flexDirection: "column",
                gap: 2,
                minWidth: 0,
              }}
            >
              <span
                style={{
                  fontSize: 12.5,
                  fontWeight: 600,
                  color: "var(--ink)",
                  whiteSpace: "nowrap",
                  overflow: "hidden",
                  textOverflow: "ellipsis",
                }}
              >
                {inv.title}
              </span>
              <span
                style={{
                  fontSize: 10.5,
                  color: "var(--ink-3)",
                  whiteSpace: "nowrap",
                  overflow: "hidden",
                  textOverflow: "ellipsis",
                }}
              >
                {inv.summary || surfaceSummary(inv.surfaces)}
              </span>
            </div>
            <Chevron />
          </motion.button>
        ))}
      </div>
    </section>
  );
}

function StrengthDot({ strong }: { strong: boolean }) {
  return (
    <motion.span
      initial={{ scale: 0.7, opacity: 0 }}
      animate={{ scale: 1, opacity: 1 }}
      transition={calm}
      aria-hidden
      style={{
        width: 8,
        height: 8,
        borderRadius: 4,
        background: strong ? "var(--accent)" : "var(--ink-4)",
        boxShadow: strong
          ? "0 0 0 3px rgba(191, 59, 43, 0.16)"
          : "none",
        flexShrink: 0,
      }}
    />
  );
}

function Chevron() {
  return (
    <svg
      width={12}
      height={12}
      viewBox="0 0 12 12"
      fill="none"
      stroke="var(--ink-3)"
      strokeWidth={1.6}
      strokeLinecap="round"
      strokeLinejoin="round"
      aria-hidden
      style={{ flexShrink: 0 }}
    >
      <path d="M4 2l5 4-5 4" />
    </svg>
  );
}

export function SectionLabel({
  label,
  count,
}: {
  label: string;
  count?: number;
}) {
  return (
    <div
      style={{
        display: "flex",
        alignItems: "baseline",
        gap: 8,
        padding: "0 4px 8px",
      }}
    >
      <span
        style={{
          fontSize: 9.5,
          fontWeight: 700,
          letterSpacing: "1.4px",
          textTransform: "uppercase",
          color: "var(--ink-3)",
        }}
      >
        {label}
      </span>
      {typeof count === "number" && (
        <span
          style={{
            fontSize: 9.5,
            fontWeight: 500,
            color: "var(--ink-4)",
            letterSpacing: "0.4px",
          }}
        >
          {count}
        </span>
      )}
    </div>
  );
}

function surfaceSummary(surfaces: string[]): string {
  if (surfaces.length === 0) return "Active";
  return `${surfaces.length} surface${surfaces.length === 1 ? "" : "s"}`;
}
