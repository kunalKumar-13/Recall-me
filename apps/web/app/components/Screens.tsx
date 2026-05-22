"use client";

import { motion } from "framer-motion";

const ease = [0.32, 0.72, 0, 1] as const;

/**
 * Phase 6G — the *Screens* gallery.
 *
 * Four real captures from the deterministic offscreen pipeline,
 * shown at low chrome so the visuals carry the section. Same warm
 * white + lavender palette across both surfaces (launcher + popup)
 * — the gallery's job is to show that the two read as one product.
 *
 * Every screenshot is sourced from `assets/screenshots/`, copied
 * into `apps/web/public/screens/` at build time. Deleting any
 * source PNG removes that tile silently rather than 404-ing — the
 * gallery is *cosmetic*, not load-bearing.
 */

type Screen = {
  src: string;
  alt: string;
  caption: string;
  surface: "Launcher" | "Extension" | "Demo" | "Alpha";
};

const SCREENS: Screen[] = [
  {
    src: "/screens/launcher/launcher-digest.png",
    alt: "The launcher's idle digest with a recovery card and active investigations",
    caption: "Idle digest — a recovery, active investigations, the day's trust line.",
    surface: "Launcher",
  },
  {
    src: "/screens/extension/extension-home.png",
    alt: "The extension popup with a continue card, investigation pills, and a today rail",
    caption: "Popup home — the continue card is the hero; investigations are quiet pills.",
    surface: "Extension",
  },
  {
    src: "/screens/demo/demo-extension.png",
    alt: "The demo overlay with a trust banner and the canonical WebSocket recovery",
    caption: "Demo overlay — fresh install, canonical three threads, with a trust banner.",
    surface: "Demo",
  },
  {
    src: "/screens/launcher/launcher-empty.png",
    alt: "The launcher's first-run empty surface with the Show example pill",
    caption: "First-run empty — *Recall notices unfinished work.* with a Show example pill.",
    surface: "Launcher",
  },
];

export function Screens() {
  return (
    <section
      id="screens"
      className="relative py-24 md:py-28 px-5 md:px-8 bg-bg-raised"
    >
      <div className="max-w-[1280px] mx-auto">
        <motion.div
          initial={{ opacity: 0, y: 8 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, margin: "-100px" }}
          transition={{ duration: 0.55, ease }}
          className="max-w-2xl"
        >
          <div className="text-[10.5px] font-semibold tracking-[0.2em] text-lavender-deep uppercase">
            Screens
          </div>
          <h2 className="font-editorial mt-3 text-[32px] md:text-[44px] font-medium tracking-editorial text-ink-bright leading-[1.05]">
            One product,
            <br />
            <span className="italic">two surfaces.</span>
          </h2>
          <p className="mt-5 text-[15px] text-ink leading-[1.7] max-w-[560px]">
            The launcher and the browser popup share a single visual
            language — warm white, lavender, hairlines. Every shot below
            is a real capture from the deterministic screenshot
            pipeline, not a render.
          </p>
        </motion.div>

        <div className="mt-12 md:mt-14 grid grid-cols-1 md:grid-cols-2 gap-6 lg:gap-8">
          {SCREENS.map((s, i) => (
            <motion.figure
              key={s.src}
              initial={{ opacity: 0, y: 10 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true, margin: "-60px" }}
              transition={{ duration: 0.55, ease, delay: i * 0.06 }}
              className="
                rounded-3xl overflow-hidden
                border border-hairline bg-bg-base shadow-card
              "
            >
              <div className="aspect-[4/3] overflow-hidden bg-bg-base flex items-center justify-center">
                {/* eslint-disable-next-line @next/next/no-img-element */}
                <img
                  src={s.src}
                  alt={s.alt}
                  loading="lazy"
                  className="w-full h-full object-contain"
                />
              </div>
              <figcaption className="
                px-5 py-4 flex items-center gap-3
                border-t border-hairline
              ">
                <span className="
                  text-[10.5px] font-semibold tracking-[0.18em]
                  text-lavender-deep uppercase
                ">
                  {s.surface}
                </span>
                <span className="text-[13.5px] text-ink leading-snug">
                  {s.caption}
                </span>
              </figcaption>
            </motion.figure>
          ))}
        </div>
      </div>
    </section>
  );
}
