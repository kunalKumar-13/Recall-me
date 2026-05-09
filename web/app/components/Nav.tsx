"use client";

import { motion, useScroll, useTransform } from "framer-motion";
import { Logo } from "./Logo";

/**
 * Sticky top nav. Transparent at the top of the page, gently fades to a
 * blurred glass slab as the user scrolls. No solid color slab — depth
 * comes from translucency over the atmospheric background.
 */
export function Nav() {
  const { scrollY } = useScroll();
  const bg = useTransform(
    scrollY,
    [0, 80],
    ["rgba(8, 17, 31, 0)", "rgba(8, 17, 31, 0.72)"]
  );
  const borderColor = useTransform(
    scrollY,
    [0, 80],
    ["rgba(124, 155, 255, 0)", "rgba(124, 155, 255, 0.10)"]
  );

  return (
    <motion.nav
      style={{ backgroundColor: bg, borderBottomColor: borderColor }}
      className="fixed top-0 left-0 right-0 z-50 border-b backdrop-blur-md"
    >
      <div className="max-w-6xl mx-auto px-6 h-14 flex items-center justify-between">
        <a href="#top" className="flex items-center gap-2.5">
          <Logo className="w-7 h-7" />
          <span className="text-ink-bright font-semibold tracking-tight">
            Recall
          </span>
        </a>
        <div className="flex items-center gap-1">
          <a
            href="#how"
            className="hidden md:inline-flex text-sm text-ink-dim hover:text-ink-bright transition-colors px-3 py-1.5 rounded-md"
          >
            How it works
          </a>
          <a
            href="#features"
            className="hidden md:inline-flex text-sm text-ink-dim hover:text-ink-bright transition-colors px-3 py-1.5 rounded-md"
          >
            Features
          </a>
          <a
            href="#privacy"
            className="hidden md:inline-flex text-sm text-ink-dim hover:text-ink-bright transition-colors px-3 py-1.5 rounded-md"
          >
            Privacy
          </a>
          <a
            href="https://github.com"
            className="hidden md:inline-flex text-sm text-ink-dim hover:text-ink-bright transition-colors px-3 py-1.5 rounded-md"
          >
            GitHub
          </a>
          <a
            href="#download"
            className="ml-2 text-sm bg-ink-bright text-bg-deepest px-3.5 py-1.5 rounded-md font-medium hover:bg-white transition-colors"
          >
            Download
          </a>
        </div>
      </div>
    </motion.nav>
  );
}
