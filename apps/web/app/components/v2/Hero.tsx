"use client";

import {
  useCallback,
  useEffect,
  useRef,
  useState,
  type MouseEvent,
} from "react";
import { LINKS } from "../../lib/links";
import { Section, Words } from "../../lib/reveal";

const THREADS = [
  {
    title: "WebSocket reconnect bug",
    cap: "3 tabs · 2 files · left mid-implementation",
    key: "websocket reconnect bug",
    hint: "↵",
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

/** Gentle magnetism for the primary CTAs — precision, not gimmick. */
function useMagnetic() {
  const onMove = useCallback((e: MouseEvent<HTMLElement>) => {
    const el = e.currentTarget;
    const r = el.getBoundingClientRect();
    el.style.translate = `${((e.clientX - (r.left + r.width / 2)) * 0.14).toFixed(1)}px ${((e.clientY - (r.top + r.height / 2)) * 0.14).toFixed(1)}px`;
  }, []);
  const onLeave = useCallback((e: MouseEvent<HTMLElement>) => {
    e.currentTarget.style.translate = "";
  }, []);
  return { onMouseMove: onMove, onMouseLeave: onLeave };
}

export function Hero() {
  const [query, setQuery] = useState("");
  const [userDrove, setUserDrove] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);
  const launcherRef = useRef<HTMLDivElement>(null);
  const stop = useRef(false);
  const magnetic = useMagnetic();

  const q = query.trim().toLowerCase();
  const visible = THREADS.filter((t) => !q || t.key.includes(q));

  /* self-driving demo: types queries until the visitor touches it */
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

  /* subtle 3D tilt on the launcher panel */
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
    <Section id="top" className="sec hero hero2">
      <div className="glow" aria-hidden="true" />
      {/* the field: drafting dots + one thread finding its way
          left → right across the spread, breathing once drawn */}
      <div className="hfield" aria-hidden="true">
        <svg
          className="hthread"
          viewBox="0 0 1440 640"
          preserveAspectRatio="none"
        >
          <path
            className="ht"
            pathLength={1}
            d="M -24 468 C 200 440, 260 250, 470 268 S 800 452, 1000 342 S 1240 170, 1358 186"
          />
          <circle className="hnode n1" cx="470" cy="268" r="3.6" />
          <circle className="hnode n2" cx="836" cy="420" r="3.6" />
          <circle className="hnode n3" cx="1092" cy="290" r="3.6" />
          <circle className="hend" cx="1360" cy="186" r="5.5" />
        </svg>
      </div>

      <div className="wrap hwrap2">
        <h1 className="spread">
          <span className="l1">
            <Words>Never lose</Words>
          </span>
          <span className="l2">
            <em>
              <Words>the thread.</Words>
            </em>
          </span>
        </h1>

        <div className="hgrid2">
          <div className="hleft">
            <p className="lead rise">
              Recall quietly reconstructs what you were working on — the tabs,
              the files, the half-finished chat — and hands it back the moment
              you return. 100% on your machine.
            </p>
            <div className="btns rise">
              <a className="btn solid" href={LINKS.release} {...magnetic}>
                Download for macOS <span className="ar">→</span>
              </a>
              <a className="btn line" href={LINKS.github} {...magnetic}>
                View on GitHub
              </a>
            </div>
            <p className="quiet rise">
              <span className="live" />
              100% local · no cloud · no telemetry · plain files you can read
              and delete
            </p>
          </div>

          <div className="hpanel rise">
            <div className="kbd-row">
              <span className="kbd">⌃</span>
              <span className="kbd">space</span>
              <span>summons it anywhere — try it</span>
            </div>
            <div
              className="launcher"
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
                  ? `${visible.length} result${visible.length === 1 ? "" : "s"}`
                  : "Continue where you left off"}
              </div>
              {visible.length === 0 && (
                <div className="lc-empty">No matches — try another word</div>
              )}
              {visible.map((t, i) => (
                <div key={t.key} className={`lc-row${i === 0 ? " sel" : ""}`}>
                  <div>
                    <div className="lc-title">{t.title}</div>
                    <div className="lc-cap">{t.cap}</div>
                  </div>
                  {i === 0 && <span className="lc-hint">↵ resume</span>}
                </div>
              ))}
              <div className="lc-foot">
                <span>↑↓ move</span>
                <span>↵ open</span>
                <span>esc close</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </Section>
  );
}
