"use client";

import { motion } from "framer-motion";
import { ANCHORS } from "../lib/links";

const ease = [0.32, 0.72, 0, 1] as const;

type Role = {
  label: string;
  icon: React.ReactNode;
};

const ROLE_ICON = {
  Search: (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round">
      <circle cx="10.5" cy="10.5" r="6.5" />
      <path d="M20 20l-4.5-4.5" />
    </svg>
  ),
  Code: (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round">
      <path d="M9 7l-5 5 5 5M15 7l5 5-5 5" />
    </svg>
  ),
  Bolt: (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.6" strokeLinejoin="round" strokeLinecap="round">
      <path d="M13 2L3 14h7l-1 8 10-12h-7l1-8z" />
    </svg>
  ),
  Book: (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round">
      <path d="M4 4h12a3 3 0 0 1 3 3v13H7a3 3 0 0 1-3-3V4z" />
      <path d="M4 17a3 3 0 0 1 3-3h12" />
    </svg>
  ),
  Sparkle: (
    <svg viewBox="0 0 24 24" fill="currentColor">
      <path d="M12 1.5l1.7 6.3a4 4 0 0 0 2.5 2.5l6.3 1.7-6.3 1.7a4 4 0 0 0-2.5 2.5l-1.7 6.3-1.7-6.3a4 4 0 0 0-2.5-2.5L1.5 12l6.3-1.7a4 4 0 0 0 2.5-2.5L12 1.5z" />
    </svg>
  ),
};

const roles: Role[] = [
  { label: "Researchers", icon: ROLE_ICON.Search },
  { label: "Developers", icon: ROLE_ICON.Code },
  { label: "Founders", icon: ROLE_ICON.Bolt },
  { label: "Students", icon: ROLE_ICON.Book },
  { label: "Creators", icon: ROLE_ICON.Sparkle },
];

/**
 * "TRUSTED BY THINKERS & BUILDERS" strip with five role glyphs.
 * Reads as a quiet acknowledgment, not a logo wall — the icons
 * speak for the kinds of people Recall is for, not for marquee
 * customer logos we don't have.
 *
 * Below the strip, a soft "HOW IT WORKS ↓" anchor link points the
 * eye into the body of the page.
 */
export function BuiltForThinkers() {
  return (
    <section className="relative pt-6 pb-14 md:pb-16 px-5 md:px-8">
      <div className="max-w-[1280px] mx-auto">
        <motion.div
          initial={{ opacity: 0, y: 8 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, margin: "-80px" }}
          transition={{ duration: 0.5, ease }}
          className="text-center"
        >
          <div className="text-[10.5px] font-semibold tracking-[0.20em] text-ink-dim uppercase">
            Trusted by thinkers &amp; builders
          </div>

          <div className="mt-5 flex items-center justify-center gap-5 md:gap-10 flex-wrap text-ink-dim">
            {roles.map((r, i) => (
              <motion.div
                key={r.label}
                initial={{ opacity: 0, y: 6 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true, margin: "-60px" }}
                transition={{ duration: 0.4, ease, delay: 0.05 + i * 0.04 }}
                className="
                  flex items-center gap-2
                  text-[12.5px] font-medium
                  hover:text-ink-bright transition-colors duration-300
                "
              >
                <div className="w-4 h-4">{r.icon}</div>
                {r.label}
              </motion.div>
            ))}
          </div>

          <a
            href={ANCHORS.how}
            className="
              mt-9 inline-flex items-center gap-2
              text-[10.5px] font-semibold tracking-[0.18em] text-lavender-deep uppercase
              hover:opacity-80 transition-opacity duration-300
            "
          >
            How it works
            <svg viewBox="0 0 24 24" className="w-3 h-3" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <path d="M12 4v16M5 13l7 7 7-7" />
            </svg>
          </a>
        </motion.div>
      </div>
    </section>
  );
}
