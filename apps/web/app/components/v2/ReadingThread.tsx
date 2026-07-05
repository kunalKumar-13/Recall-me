"use client";

import { useEffect, useRef } from "react";

/** The fixed red thread down the left edge: scroll progress plus a
 *  traveling node — the page's bookmark. */
export function ReadingThread() {
  const bar = useRef<HTMLDivElement>(null);
  const node = useRef<HTMLDivElement>(null);
  useEffect(() => {
    if (matchMedia("(prefers-reduced-motion: reduce)").matches) return;
    const onScroll = () => {
      const h = document.documentElement.scrollHeight - innerHeight;
      const p = h > 0 ? scrollY / h : 0;
      if (bar.current) bar.current.style.transform = `scaleY(${p})`;
      if (node.current) {
        node.current.style.top = `${p * (innerHeight - 8)}px`;
        node.current.style.opacity = p > 0.005 ? "1" : "0";
      }
    };
    addEventListener("scroll", onScroll, { passive: true });
    onScroll();
    return () => removeEventListener("scroll", onScroll);
  }, []);
  return (
    <>
      <div className="progress" ref={bar} aria-hidden />
      <div id="prognode" ref={node} aria-hidden />
    </>
  );
}
