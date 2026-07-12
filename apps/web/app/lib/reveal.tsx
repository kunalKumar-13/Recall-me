"use client";

/**
 * Reveal primitives. A Section observes itself and gains `.in` once,
 * which the stylesheet turns into the quiet settle: eyebrow ticks
 * draw, words cascade, rows stagger, the red thread underlines sweep.
 */

import {
  createElement,
  useEffect,
  useRef,
  type ElementType,
  type ReactNode,
} from "react";

export function Section({
  id,
  className = "",
  as = "section",
  children,
}: {
  id?: string;
  className?: string;
  as?: ElementType;
  children: ReactNode;
}) {
  const ref = useRef<HTMLElement | null>(null);
  useEffect(() => {
    const el = ref.current;
    if (!el) return;
    if (typeof IntersectionObserver === "undefined") {
      el.classList.add("in");
      return;
    }
    const io = new IntersectionObserver(
      (entries) => {
        entries.forEach((e) => {
          if (e.isIntersecting) {
            e.target.classList.add("in");
            io.unobserve(e.target);
          }
        });
      },
      { rootMargin: "0px 0px -10% 0px", threshold: 0.08 },
    );
    io.observe(el);
    return () => io.disconnect();
  }, []);
  return createElement(as, { id, className, ref }, children);
}

/** Split heading text into word spans for the cascade. `<br/>` and
 *  `<em>` children survive; each word gets an incremental delay. */
export function Words({ children }: { children: ReactNode }) {
  let delay = 0;
  const wrap = (node: ReactNode, key: number): ReactNode => {
    if (typeof node === "string") {
      return node.split(/(\s+)/).map((part, i) => {
        if (!part) return null;
        if (/^\s+$/.test(part)) return part;
        const style = { transitionDelay: `${(0.06 + delay * 0.07).toFixed(2)}s` };
        delay += 1;
        return (
          <span key={`${key}-${i}`} className="w" style={style}>
            {part}
          </span>
        );
      });
    }
    return node;
  };
  const arr = Array.isArray(children) ? children : [children];
  return <>{arr.map((c, i) => wrap(c, i))}</>;
}

/** Editorial section header: a numbered bracket eyebrow in the
 *  drafting-table voice — `[ 03 ] CAPTURE` — then the display
 *  heading. `total` is kept for API compatibility; the bracket
 *  carries the number now. */
export function SectionHead({
  index,
  total: _total = "08",
  eyebrow,
  children,
}: {
  index: string;
  total?: string;
  eyebrow: string;
  children: ReactNode;
}) {
  return (
    <>
      <span className="eyebrow rise">
        <span className="bk">[</span>
        <span className="no">{index}</span>
        <span className="bk">]</span>
        {eyebrow}
      </span>
      {children}
    </>
  );
}

/** Full-bleed hairline between chapters. Where it crosses the page
 *  rails, a small + sits on the intersection. */
export function Rule() {
  return (
    <div className="rule" aria-hidden="true">
      <span className="rx l" />
      <span className="rx r" />
    </div>
  );
}
