"use client";

/**
 * The story chapter. Four narrated beats of a working day; the
 * workspace stage stays pinned beside them and *scroll is the
 * playhead* — each beat scrubs its scene of the film. On touch,
 * narrow viewports or reduced motion the stage simply plays on a
 * loop below the words.
 */

import { useEffect, useRef, useState } from "react";
import { Section, SectionHead, Words } from "../../lib/reveal";
import { FILM_SCENES, useFilm } from "../../lib/useFilm";
import { Stage } from "./Stage";

const BEATS = [
  {
    time: "9:41 AM",
    h: "You're deep in it.",
    p: "Three tabs, a file half-written, one good question in a chat. The shape of the thing is finally forming.",
  },
  {
    time: "11:00 AM",
    h: "Then the day happens.",
    p: "A standup. A customer call. Someone's quick question that wasn't. The windows close, one by one.",
  },
  {
    time: "3:12 PM",
    h: "You come back to nothing.",
    p: "Clean desk, empty head. The work is somewhere — in history, in downloads, in a chat you can't name. The thread is gone.",
  },
  {
    time: "3:13 PM",
    h: "One keystroke. All of it, back.",
    p: "⌃ space. The file opens, the chat returns, the tabs line up in the order you need them. Recall kept the thread.",
  },
];

export function Story() {
  const [mode, setMode] = useState<"scrub" | "loop">("scrub");
  const gridRef = useRef<HTMLDivElement>(null);
  const stageCol = useRef<HTMLDivElement>(null);
  const progRef = useRef<HTMLDivElement>(null);
  const timeRef = useRef<HTMLSpanElement>(null);
  const seek = useFilm(stageCol, mode);

  useEffect(() => {
    const narrow = matchMedia("(max-width: 940px)");
    const reduce = matchMedia("(prefers-reduced-motion: reduce)");
    const pick = () => setMode(narrow.matches || reduce.matches ? "loop" : "scrub");
    pick();
    narrow.addEventListener("change", pick);
    reduce.addEventListener("change", pick);
    return () => {
      narrow.removeEventListener("change", pick);
      reduce.removeEventListener("change", pick);
    };
  }, []);

  /* scroll = playhead */
  useEffect(() => {
    if (mode !== "scrub") return;
    const grid = gridRef.current;
    if (!grid) return;
    const beats = Array.from(grid.querySelectorAll<HTMLElement>("[data-beat]"));
    let raf = 0;
    const onScroll = () => {
      cancelAnimationFrame(raf);
      raf = requestAnimationFrame(() => {
        const r = grid.getBoundingClientRect();
        const span = r.height - innerHeight;
        const p = Math.min(1, Math.max(0, span > 0 ? -r.top / span : 0));
        const i = Math.min(3, Math.floor(p * 4));
        const local = Math.min(1, Math.max(0, p * 4 - i));
        const t =
          FILM_SCENES[i] + (FILM_SCENES[i + 1] - FILM_SCENES[i]) * local;
        seek.current(t);
        beats.forEach((b, bi) => b.classList.toggle("active", bi === i));
        if (progRef.current)
          progRef.current.style.width = `${(p * 100).toFixed(2)}%`;
        if (timeRef.current) {
          const s = Math.floor(t / 1000);
          timeRef.current.textContent = `00:${s < 10 ? "0" : ""}${s} / 00:22`;
        }
      });
    };
    addEventListener("scroll", onScroll, { passive: true });
    onScroll();
    return () => {
      removeEventListener("scroll", onScroll);
      cancelAnimationFrame(raf);
    };
  }, [mode, seek]);

  return (
    <Section id="film" className="sec story">
      <div className="wrap sechead" style={{ paddingBottom: 0 }}>
        <SectionHead index="01" eyebrow="A day, in twenty-two seconds">
          <h2>
            <Words>Watch the thread break, </Words>
            <em>
              <Words>then come back.</Words>
            </em>
          </h2>
        </SectionHead>
        <p className="body rise">
          Not a video — the interface itself, acting it out.{" "}
          {mode === "scrub" ? "Your scroll is the playhead." : "It plays on a loop."}
        </p>
      </div>
      <div className={`sgrid ${mode}`} ref={gridRef}>
        <div className="sbeats">
          {BEATS.map((b, i) => (
            <div className={`beat${i === 0 ? " active" : ""}`} data-beat key={b.time}>
              <span className="tlab">{b.time}</span>
              <h3>{b.h}</h3>
              <p>{b.p}</p>
            </div>
          ))}
        </div>
        <div className="ssticky" ref={stageCol}>
          <Stage />
          <div className="sfoot">
            <div className="sprog">
              <div className="sfill" ref={progRef} />
            </div>
            <span className="stime" ref={timeRef}>
              00:00 / 00:22
            </span>
          </div>
        </div>
      </div>
    </Section>
  );
}
