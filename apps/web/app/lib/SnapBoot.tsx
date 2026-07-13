"use client";

import { useEffect } from "react";

/**
 * Headless-verification harness. With `?snap=1` in the URL every
 * reveal-gated section is forced into its settled (`.in`) state and
 * the page jumps to the hash target, so a screenshot tool that can't
 * scroll or wait for IntersectionObserver still sees real pixels.
 * No-op without the query param; ships inert.
 */
export function SnapBoot() {
  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    if (!params.has("snap")) return;
    const settle = () => {
      document
        .querySelectorAll("section, .sec, .statsband, footer")
        .forEach((el) => el.classList.add("in"));
    };
    settle();
    // late-mounting sections (client components) get a second pass
    const t = setTimeout(() => {
      settle();
      const hash = window.location.hash;
      if (hash) {
        document.querySelector(hash)?.scrollIntoView({ behavior: "instant" as ScrollBehavior });
      }
      // ?probe=1 — report layout overflow through the title so a
      // dump-dom run can read it (headless can't eval JS directly).
      if (params.has("probe")) {
        const vw = document.documentElement.clientWidth;
        const wide: string[] = [];
        document.querySelectorAll("body *").forEach((el) => {
          const r = el.getBoundingClientRect();
          if (r.width > vw + 1 && wide.length < 8) {
            wide.push(
              `${el.tagName}.${String((el as HTMLElement).className).slice(0, 30)}=${Math.round(r.width)}`,
            );
          }
        });
        document.title = `PROBE vw=${vw} sw=${document.scrollingElement?.scrollWidth} :: ${wide.join(" | ") || "clean"}`;
      }
    }, 300);
    return () => clearTimeout(t);
  }, []);
  return null;
}
