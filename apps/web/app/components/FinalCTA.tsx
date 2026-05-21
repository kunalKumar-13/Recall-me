"use client";

import { motion } from "framer-motion";
import { LINKS } from "../lib/links";
import { WindowsGlyph } from "./WindowsGlyph";

const ease = [0.32, 0.72, 0, 1] as const;

/**
 * FinalCTA — calmer, more compact than the prior pass. Editorial
 * serif headline (italic on "never"), single lavender Download CTA,
 * three-line trust caption beneath. The lavender halo behind the
 * headline is static (a single radial-gradient, no animation, paint-
 * once on mount).
 */
export function FinalCTA() {
  return (
    <section
      id="download"
      className="relative pt-24 md:pt-32 pb-24 md:pb-32 px-5 md:px-8 overflow-hidden"
    >
      {/* Static lavender halo. Lighter than the previous pass
          (alpha 0.18 → 0.10) so the headline carries the moment
          via type weight, not via background heat. */}
      <div
        aria-hidden
        className="
          absolute left-1/2 -translate-x-1/2 -top-16
          w-[600px] h-[500px] pointer-events-none
        "
        style={{
          background:
            "radial-gradient(circle, rgba(169,156,247,0.10) 0%, transparent 60%)",
        }}
      />

      <div className="relative max-w-2xl mx-auto text-center">
        <motion.h2
          initial={{ opacity: 0, y: 10 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, margin: "-100px" }}
          transition={{ duration: 0.6, ease }}
          className="
            font-editorial
            text-[34px] md:text-[44px] lg:text-[52px]
            font-medium tracking-editorial leading-[1.05]
            text-ink-bright
          "
        >
          Ready to pick up
          <br />
          <span className="italic">where you left off?</span>
        </motion.h2>

        <motion.div
          initial={{ opacity: 0, y: 6 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, margin: "-100px" }}
          transition={{ duration: 0.55, ease, delay: 0.08 }}
          className="mt-9 flex items-center justify-center"
        >
          <a
            href={LINKS.release}
            target="_blank"
            rel="noopener noreferrer"
            className="
              inline-flex items-center gap-2
              h-12 px-6 rounded-lg
              bg-lavender-gradient text-white text-[14.5px] font-medium
              shadow-lift
              hover:bg-lavender-gradient-hover
              transition-[background,transform] duration-300
              hover:-translate-y-px
            "
          >
            <WindowsGlyph className="w-4 h-4" />
            Download for Windows
          </a>
        </motion.div>

        <motion.p
          initial={{ opacity: 0 }}
          whileInView={{ opacity: 1 }}
          viewport={{ once: true, margin: "-100px" }}
          transition={{ duration: 0.7, ease, delay: 0.18 }}
          className="mt-6 text-[12.5px] text-ink-dim"
        >
          It&apos;s free. It&apos;s private. It&apos;s yours.
        </motion.p>
      </div>
    </section>
  );
}
