"use client";

import { motion } from "framer-motion";
import { LINKS } from "../lib/links";

const ease = [0.32, 0.72, 0, 1] as const;

/**
 * Phase 6G — the *Download* section.
 *
 * Four artifacts, one calm grid:
 *
 *   - Windows Lite installer    (~216 MB)   — the default
 *   - Windows Full installer    (~261 MB)   — same product, larger bundle
 *   - macOS preview             unsigned    — gated by MAC_OWNER_NEEDED
 *   - Chrome extension          unpacked    — pairs with either desktop build
 *
 * Each card carries: artifact name · platform tag · short size /
 * status line · download link. The visual hierarchy puts the Lite
 * installer first because that is the path 95 % of cohort testers
 * will walk.
 *
 * The page does NOT host the installers itself. Every link routes
 * to the GitHub releases page so the artifact source of truth stays
 * one place; if a tester ends up on a stale page, the latest binary
 * is one click away.
 */

type Artifact = {
  eyebrow: string;
  title: string;
  meta: string;
  body: string;
  cta: string;
  href: string;
  recommended?: boolean;
};

const ARTIFACTS: Artifact[] = [
  {
    eyebrow: "Windows · default",
    title: "Recall — Lite installer",
    meta: "≈ 216 MB · signed once · Win 10 + Win 11",
    body:
      "The smaller of the two Windows builds. Same product, same engine; PyQt6 deps trimmed via the Phase 5J shrink. Recommended for almost everyone.",
    cta: "Download lite",
    href: LINKS.release,
    recommended: true,
  },
  {
    eyebrow: "Windows · full",
    title: "Recall — Full installer",
    meta: "≈ 261 MB · same code · Win 10 + Win 11",
    body:
      "The unmodified PyInstaller bundle. Identical behaviour to lite. Pick this if your environment forbids on-startup dependency pruning.",
    cta: "Download full",
    href: LINKS.release,
  },
  {
    eyebrow: "macOS · preview",
    title: "Recall — macOS preview",
    meta: "unsigned · Intel + Apple Silicon · ad-hoc dmg",
    body:
      "The Mac path is gated by a maintainer with the right hardware. Use the preview at your own risk; Gatekeeper warning expected until the developer-ID signing path lands.",
    cta: "Read the Mac note",
    href: "https://github.com/kunalKumar-13/Recall-me/blob/main/docs/release/MAC_OWNER_NEEDED.md",
  },
  {
    eyebrow: "Chrome / Edge / Arc",
    title: "Browser extension",
    meta: "MV3 · loopback only · pairs with either desktop build",
    body:
      "The popup that lives in your browser. Bundled inside the installer; the extension folder is also shipped unpacked for sideload.",
    cta: "Open releases",
    href: LINKS.release,
  },
];

export function Download() {
  return (
    <section
      id="download"
      className="relative py-24 md:py-28 px-5 md:px-8"
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
            Download alpha
          </div>
          <h2 className="font-editorial mt-3 text-[32px] md:text-[44px] font-medium tracking-editorial text-ink-bright leading-[1.05]">
            Four artifacts.
            <br />
            <span className="italic">Pick one, install it once.</span>
          </h2>
          <p className="mt-5 text-[15px] text-ink leading-[1.7] max-w-[560px]">
            Recall is an installable desktop app + a browser extension.
            Both stay entirely on your machine. The full alpha install
            takes &lt; 30 seconds on a normal laptop.
          </p>
        </motion.div>

        <div className="mt-12 md:mt-14 grid grid-cols-1 md:grid-cols-2 gap-5 lg:gap-6">
          {ARTIFACTS.map((a, i) => (
            <motion.div
              key={a.title}
              initial={{ opacity: 0, y: 10 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true, margin: "-60px" }}
              transition={{ duration: 0.55, ease, delay: i * 0.06 }}
              className={`
                relative rounded-3xl border bg-bg-base shadow-card
                px-6 py-6 flex flex-col gap-4
                ${a.recommended ? "border-lavender-deep/40" : "border-hairline"}
              `}
            >
              {a.recommended && (
                <span className="
                  absolute top-4 right-4
                  text-[9.5px] font-semibold tracking-[0.16em] uppercase
                  text-lavender-deep bg-lavender-wash
                  rounded-full px-2.5 py-0.5
                  border border-lavender/30
                ">
                  Recommended
                </span>
              )}
              <div>
                <div className="text-[10.5px] font-semibold tracking-[0.18em] text-lavender-deep uppercase">
                  {a.eyebrow}
                </div>
                <h3 className="font-editorial mt-2 text-[22px] font-medium text-ink-bright leading-[1.15]">
                  {a.title}
                </h3>
                <p className="mt-1.5 text-[12px] text-ink-dim font-mono">
                  {a.meta}
                </p>
              </div>
              <p className="text-[13.5px] text-ink leading-[1.6] flex-1">
                {a.body}
              </p>
              <a
                href={a.href}
                target="_blank"
                rel="noopener noreferrer"
                className={`
                  mt-auto inline-flex items-center gap-2
                  h-10 px-4 rounded-lg
                  text-[13px] font-medium
                  transition-[transform,background] duration-300
                  hover:-translate-y-px
                  ${a.recommended
                    ? "bg-ink-bright text-white hover:bg-black"
                    : "bg-bg-raised text-ink-bright border border-hairline hover:border-lavender/40"
                  }
                `}
              >
                {a.cta} →
              </a>
            </motion.div>
          ))}
        </div>

        {/* Trust strip — restates the boundary at the moment of
            download so the user installs with eyes open. */}
        <motion.div
          initial={{ opacity: 0, y: 8 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, margin: "-60px" }}
          transition={{ duration: 0.5, ease, delay: 0.1 }}
          className="
            mt-10 rounded-2xl border border-lavender/30 bg-lavender-wash
            px-5 py-4 text-center
          "
        >
          <p className="text-[13px] text-ink-bright leading-[1.55]">
            <span className="font-semibold">Local-first.</span> No cloud,
            no telemetry, no account. The installer is the only thing
            that touches the network — once, on first run, to download
            the embedding model.
          </p>
        </motion.div>
      </div>
    </section>
  );
}
