"use client";

import { useCallback, type MouseEvent } from "react";
import { Connectome } from "../../lib/Connectome";
import { LINKS } from "../../lib/links";
import { Section, Words } from "../../lib/reveal";

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

/**
 * The lab hero: statement left, specimen right. The specimen is the
 * connectome — your day as a brain of connected moments, with the
 * red thread finding its way back in. Plot furniture (axis ticks,
 * a graph label, the derivation line) because Recall is an
 * instrument, not an app with a mascot.
 */
export function Hero() {
  const magnetic = useMagnetic();
  return (
    <Section id="top" className="sec hero hero3">
      <div className="glow" aria-hidden="true" />
      <div className="wrap h3wrap">
        <div className="h3left">
          <span className="h3over mono rise">
            An instrument for unfinished thought
          </span>
          <h1>
            <Words>Never lose</Words>
            <br />
            <em>
              <Words>the thread.</Words>
            </em>
          </h1>
          <p className="lead rise">
            Recall reconstructs what you were working on — the tabs, the
            files, the half-finished chat — and hands it back the moment you
            return. One keystroke. 100% on your machine.
          </p>
          <div className="btns rise">
            <a className="btn solid" href={LINKS.release} {...magnetic}>
              Download for macOS <span className="ar">→</span>
            </a>
            <a className="btn line" href={LINKS.github} {...magnetic}>
              View source <span className="ar">→</span>
            </a>
          </div>
          <p className="quiet rise">
            <span className="live" />
            no cloud · no telemetry · plain files you can read and delete
          </p>
        </div>

        <figure className="h3plot rise" aria-label="The memory graph">
          <figcaption className="plotlabel mono">
            <span>memory graph</span>
            <span className="dim">~/.recall · deterministic</span>
          </figcaption>
          <div className="plotbox">
            <Connectome />
            {/* axis furniture */}
            <span className="ax ax-y mono" aria-hidden>
              <i>t₀</i>
              <i>t₁</i>
              <i>t₂</i>
            </span>
            <span className="ax ax-x mono" aria-hidden>
              <i>events</i>
              <i>sessions</i>
              <i>threads</i>
            </span>
          </div>
          <div className="plotderiv mono">
            recovery = f(events, gaps, returns) — no weights, no guessing
          </div>
        </figure>
      </div>
    </Section>
  );
}
