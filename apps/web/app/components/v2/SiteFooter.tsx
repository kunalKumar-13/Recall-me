"use client";

import { useEffect, useState } from "react";
import { LINKS } from "../../lib/links";

/** Giant outlined wordmark + a live local clock — the site keeps
 *  time the way the product keeps memory: quietly, on your machine. */
export function SiteFooter() {
  const [time, setTime] = useState("");
  useEffect(() => {
    const fmt = () =>
      new Date().toLocaleTimeString([], {
        hour: "2-digit",
        minute: "2-digit",
      });
    setTime(fmt());
    const t = setInterval(() => setTime(fmt()), 30_000);
    return () => clearInterval(t);
  }, []);
  return (
    <footer>
      <div className="fmark" aria-hidden="true">
        <div className="word">
          Recall<i>.</i>
        </div>
      </div>
      <div className="frow">
        <span>
          Recall — a continuity OS for unfinished thought
          {time ? ` · your time ${time}` : ""}
        </span>
        <nav className="fnav">
          <a href="#how">How</a>
          <a href="#trust">Privacy</a>
          <a href={LINKS.github} target="_blank" rel="noreferrer">
            GitHub
          </a>
          <a href="#download">Download</a>
        </nav>
      </div>
    </footer>
  );
}
