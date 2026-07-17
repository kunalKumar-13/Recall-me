"use client";

import { useEffect, useRef, useState, type MouseEvent } from "react";
import { Section } from "../../lib/reveal";

const THREADS = [
  {
    title: "WebSocket reconnect bug",
    cap: "3 tabs · 2 files · left mid-implementation",
    key: "websocket reconnect bug",
  },
  {
    title: "Seed deck — narrative pass",
    cap: "yesterday 4:12pm · 6 events",
    key: "seed deck narrative pass",
  },
  {
    title: "Rust async runtime research",
    cap: "research → implementation · 3 days",
    key: "rust async runtime research tokio",
  },
];

const DEMO_QUERIES = ["websocket", "seed deck", "rust async"];

/**
 * The try-it band — a real, driveable launcher. Types by itself
 * until touched; filtering dims rows instead of removing them so the
 * panel never changes height under your cursor.
 */
export function TryIt() {
  const [query, setQuery] = useState("");
  const [userDrove, setUserDrove] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);
  const launcherRef = useRef<HTMLDivElement>(null);
  const stop = useRef(false);

  const q = query.trim().toLowerCase();
  const matches = THREADS.map((t) => !q || t.key.includes(q));
  const matchCount = matches.filter(Boolean).length;
  const firstMatch = matches.indexOf(true);

  useEffect(() => {
    if (userDrove) return;
    if (matchMedia("(prefers-reduced-motion: reduce)").matches) return;
    stop.current = false;
    let qi = 0;
    let timer: ReturnType<typeof setTimeout>;
    const type = (word: string, done: () => void) => {
      let i = 0;
      const step = () => {
        if (stop.current) return;
        if (i <= word.length) {
          setQuery(word.slice(0, i));
          i += 1;
          timer = setTimeout(step, 95 + Math.random() * 70);
        } else timer = setTimeout(done, 1500);
      };
      step();
    };
    const erase = (done: () => void) => {
      const step = () => {
        if (stop.current) return;
        setQuery((prev) => {
          if (prev.length === 0) {
            timer = setTimeout(done, 650);
            return prev;
          }
          timer = setTimeout(step, 42);
          return prev.slice(0, -1);
        });
      };
      step();
    };
    const loop = () => {
      if (stop.current) return;
      type(DEMO_QUERIES[qi % DEMO_QUERIES.length], () =>
        erase(() => {
          qi += 1;
          loop();
        }),
      );
    };
    timer = setTimeout(loop, 2400);
    return () => {
      stop.current = true;
      clearTimeout(timer);
    };
  }, [userDrove]);

  const takeOver = () => {
    stop.current = true;
    setUserDrove(true);
  };

  const onTilt = (e: MouseEvent<HTMLDivElement>) => {
    const el = launcherRef.current;
    if (!el || matchMedia("(prefers-reduced-motion: reduce)").matches) return;
    const r = el.getBoundingClientRect();
    const px = (e.clientX - r.left) / r.width - 0.5;
    const py = (e.clientY - r.top) / r.height - 0.5;
    el.style.transform = `perspective(1100px) rotateY(${(px * 3).toFixed(2)}deg) rotateX(${(-py * 3).toFixed(2)}deg)`;
  };
  const offTilt = () => {
    if (launcherRef.current) launcherRef.current.style.transform = "";
  };

  return (
    <Section className="trybar" as="div">
      <div className="try-inner">
        <div className="kbd-row rise">
          <span className="kbd">⌃</span>
          <span className="kbd">space</span>
          <span>summons it anywhere — try it</span>
        </div>
        <div
          className="launcher rise"
          ref={launcherRef}
          onMouseMove={onTilt}
          onMouseLeave={offTilt}
          aria-label="The Recall launcher"
        >
          <div className="lc-search">
            <span aria-hidden>⌕</span>
            <input
              ref={inputRef}
              className="lc-input"
              value={query}
              placeholder="Search your memory…"
              aria-label="Search your memory"
              spellCheck={false}
              autoComplete="off"
              onFocus={takeOver}
              onPointerDown={takeOver}
              onChange={(e) => {
                takeOver();
                setQuery(e.target.value);
              }}
            />
            <span className="lc-live" aria-hidden>
              <i /> local
            </span>
          </div>
          <div className="lc-head">
            {q
              ? matchCount === 0
                ? "no matches — try another word"
                : `${matchCount} result${matchCount === 1 ? "" : "s"}`
              : "Continue where you left off"}
          </div>
          {THREADS.map((t, i) => {
            const hit = matches[i];
            const sel = hit && i === firstMatch;
            return (
              <div
                key={t.key}
                className={`lc-row${sel ? " sel" : ""}${q && !hit ? " dim" : ""}`}
              >
                <div>
                  <div className="lc-title">{t.title}</div>
                  <div className="lc-cap">{t.cap}</div>
                </div>
                {sel && <span className="lc-hint">↵ resume</span>}
              </div>
            );
          })}
          <div className="lc-foot">
            <span>↑↓ move</span>
            <span>↵ open</span>
            <span>esc close</span>
          </div>
        </div>
      </div>
    </Section>
  );
}
