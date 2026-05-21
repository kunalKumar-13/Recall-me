import { motion } from "framer-motion";
import { fadeExpand, staggered } from "../lib/motion";

/**
 * A titled zone of the popup. Sections enter with a small top-down
 * stagger (fade + a few px of expand) so the popup *settles* into
 * place rather than appearing all at once — the visual equivalent
 * of the room coming back into focus.
 */
export function Section({
  label,
  count,
  index = 0,
  children,
}: {
  label: string;
  count?: string;
  index?: number;
  children: React.ReactNode;
}) {
  return (
    <motion.section
      className="section"
      variants={fadeExpand}
      initial="hidden"
      animate="show"
      transition={staggered(index)}
      style={{ marginBottom: "var(--gap-section)" }}
    >
      <div className="section-label">
        <span>{label}</span>
        {count ? <span className="count">{count}</span> : null}
      </div>
      {children}
    </motion.section>
  );
}
