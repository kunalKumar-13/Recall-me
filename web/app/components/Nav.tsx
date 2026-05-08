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
    ["rgba(10, 11, 15, 0)", "rgba(10, 11, 15, 0.72)"]
  );
  const borderColor = useTransform(
    scrollY,
    [0, 80],
    ["rgba(255, 255, 255, 0)", "rgba(255, 255, 255, 0.06)"]
  );

  return (
    <motion.nav
      style={{ backgroundColor: bg, borderBottomColor: borderColor }}
      className="fixed top-0 left-0 right-0 z-50 border-b backdrop-blur-md"
    >
      <div className="max-w-6xl mx-auto px-6 h-14 flex items-center justify-between">
        <a href="#top" className="flex items-center gap-2">
          <Logo className="w-7 h-7" />
          <span className="text-white font-semibold tracking-tight">
            Recall
          </span>
        </a>
        <div className="flex items-center gap-1">
          <a
            href="#features"
            className="hidden md:inline-flex text-sm text-white/60 hover:text-white transition-colors px-3 py-1.5 rounded-md"
          >
            Features
          </a>
          <a
            href="#privacy"
            className="hidden md:inline-flex text-sm text-white/60 hover:text-white transition-colors px-3 py-1.5 rounded-md"
          >
            Privacy
          </a>
          <a
            href="https://github.com"
            className="hidden md:inline-flex text-sm text-white/60 hover:text-white transition-colors px-3 py-1.5 rounded-md"
          >
            GitHub
          </a>
          <a
            href="#download"
            className="ml-2 text-sm bg-white text-black px-3.5 py-1.5 rounded-md font-medium hover:bg-white/90 transition-colors"
          >
            Download
          </a>
        </div>
      </div>
    </motion.nav>
  );
}
