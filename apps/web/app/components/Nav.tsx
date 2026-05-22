"use client";

import { motion, useScroll, useTransform } from "framer-motion";
import { useState } from "react";
import { ANCHORS, LINKS } from "../lib/links";
import { Logo } from "./Logo";
import { WindowsGlyph } from "./WindowsGlyph";

type NavItem = {
  href: string;
  label: string;
  external?: boolean;
};

const NAV_LINKS: NavItem[] = [
  // Phase 6G — narrative-order links, matching the page sections.
  { href: "#problem", label: "The problem" },
  { href: ANCHORS.how, label: "How it works" },
  { href: "#story", label: "Stories" },
  { href: "#screens", label: "Screens" },
  { href: ANCHORS.privacy, label: "Trust" },
  { href: ANCHORS.download, label: "Download" },
  { href: LINKS.github, label: "GitHub", external: true },
];

/**
 * Top nav.
 *
 * Three groups, left → right:
 *   • Logo + wordmark
 *   • Section nav (collapses behind a hamburger on small screens)
 *   • Sign-in (text link, deferred to GitHub) + Download CTA
 *
 * The fill fades in on scroll (0 → 80 px) using `useTransform` over
 * a single rgba layer — no backdrop-filter, no blur, no paint cost
 * during scroll.
 */
export function Nav() {
  const { scrollY } = useScroll();
  const bg = useTransform(
    scrollY,
    [0, 80],
    ["rgba(251, 247, 244, 0)", "rgba(251, 247, 244, 0.92)"]
  );
  const borderOpacity = useTransform(scrollY, [0, 80], [0, 1]);

  const [open, setOpen] = useState(false);

  return (
    <motion.nav
      style={{ backgroundColor: bg }}
      className="fixed top-0 inset-x-0 z-50"
    >
      <motion.div
        aria-hidden
        style={{ opacity: borderOpacity }}
        className="absolute inset-x-0 bottom-0 h-px bg-hairline"
      />

      <div className="max-w-[1280px] mx-auto px-5 md:px-8 h-16 flex items-center justify-between gap-4">
        {/* Logo */}
        <a
          href={ANCHORS.top}
          className="flex items-center gap-2.5 shrink-0 group"
          aria-label="Recall.me — home"
        >
          <Logo className="w-7 h-7" />
          <span className="text-ink-bright font-semibold tracking-tight text-[16px]">
            Recall<span className="text-ink-dim font-normal">.me</span>
          </span>
        </a>

        {/* Center: section links */}
        <div className="hidden lg:flex items-center gap-1 absolute left-1/2 -translate-x-1/2">
          {NAV_LINKS.map((link) => (
            <NavLink key={link.label} {...link} />
          ))}
        </div>

        {/* Right cluster — sign-in + CTA */}
        <div className="flex items-center gap-3 shrink-0">
          <a
            href={LINKS.github}
            target="_blank"
            rel="noopener noreferrer"
            className="
              hidden md:inline-flex text-[13.5px] text-ink
              hover:text-ink-bright transition-colors duration-300
              px-2 py-1.5
            "
          >
            Sign in
          </a>

          <a
            href={ANCHORS.download}
            className="
              hidden sm:inline-flex items-center gap-2
              h-9 px-3.5 rounded-lg
              bg-lavender-gradient text-white text-[13px] font-medium
              shadow-lift
              hover:bg-lavender-gradient-hover
              transition-[background] duration-300
            "
          >
            <WindowsGlyph className="w-3.5 h-3.5" />
            Download alpha
          </a>

          {/* Mobile hamburger */}
          <button
            type="button"
            onClick={() => setOpen((v) => !v)}
            aria-label="Toggle navigation"
            aria-expanded={open}
            className="
              lg:hidden inline-flex items-center justify-center
              w-9 h-9 rounded-md
              border border-hairline bg-bg-base
              text-ink-bright
            "
          >
            <span className="sr-only">Menu</span>
            <svg viewBox="0 0 24 24" className="w-4 h-4" fill="none" stroke="currentColor" strokeWidth="1.8">
              {open ? (
                <path strokeLinecap="round" d="M6 6l12 12M6 18L18 6" />
              ) : (
                <path strokeLinecap="round" d="M4 7h16M4 12h16M4 17h16" />
              )}
            </svg>
          </button>
        </div>
      </div>

      {/* Mobile drawer */}
      {open && (
        <div className="lg:hidden border-t border-hairline bg-bg-page/95">
          <div className="px-5 py-4 flex flex-col gap-1">
            {NAV_LINKS.map((link) => (
              <a
                key={link.label}
                href={link.href}
                target={link.external ? "_blank" : undefined}
                rel={link.external ? "noopener noreferrer" : undefined}
                onClick={() => setOpen(false)}
                className="
                  px-3 py-2 rounded-md text-[14px] text-ink-bright
                  hover:bg-lavender-soft/40 transition-colors
                "
              >
                {link.label}
              </a>
            ))}
            <a
              href={LINKS.github}
              target="_blank"
              rel="noopener noreferrer"
              onClick={() => setOpen(false)}
              className="
                px-3 py-2 rounded-md text-[14px] text-ink
                hover:bg-lavender-soft/40 transition-colors
              "
            >
              Sign in
            </a>
            <a
              href={ANCHORS.download}
              onClick={() => setOpen(false)}
              className="
                mt-2 inline-flex items-center justify-center gap-2
                h-10 rounded-lg
                bg-lavender-gradient text-white text-[14px] font-medium
                shadow-lift
              "
            >
              <WindowsGlyph className="w-3.5 h-3.5" />
              Download alpha
            </a>
          </div>
        </div>
      )}
    </motion.nav>
  );
}

function NavLink({
  href,
  label,
  external,
}: {
  href: string;
  label: string;
  external?: boolean;
}) {
  return (
    <a
      href={href}
      target={external ? "_blank" : undefined}
      rel={external ? "noopener noreferrer" : undefined}
      className="
        text-[13.5px] text-ink hover:text-ink-bright
        transition-colors duration-300
        px-3 py-1.5 rounded-md
      "
    >
      {label}
    </a>
  );
}
