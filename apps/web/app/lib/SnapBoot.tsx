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
    }, 300);
    return () => clearTimeout(t);
  }, []);
  return null;
}
