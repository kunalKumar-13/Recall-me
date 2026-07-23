import { Section, SectionHead, Words } from "../../lib/reveal";

/**
 * The surfaces — real renders of the shipped builds (captured in demo
 * mode, no mockup fiction). No faux hardware: each render sits in a
 * clean hairline panel with a deep soft shadow, the way premium
 * product sites show their own UI. The console swaps light/dark with
 * the site theme; the popup ships dark — that's the HUD.
 */
export function Surfaces() {
  return (
    <Section id="surfaces" className="sec">
      <div className="wrap sechead c">
        <SectionHead index="05" eyebrow="The surfaces">
          <h2>
            <Words>One memory, </Words>
            <em>
              <Words>every screen.</Words>
            </em>
          </h2>
          <p className="lead rise">
            Real renders of the shipped builds — the console on your desk,
            the popup in your toolbar, the launcher over everything.
          </p>
        </SectionHead>
      </div>

      <div className="surf rise">
        <div className="surf-glow" aria-hidden />

        <figure className="surf-fig console">
          <div className="panel panel-console">
            <img
              className="shot-light"
              src="/shots/console-light.png"
              alt="The Recall console — engine layers, today's 24-hour rhythm, continue, active threads and the live tail"
            />
            <img
              className="shot-dark"
              src="/shots/console-dark.png"
              alt="The Recall console in ink night"
            />
          </div>
          <figcaption className="panelcap">
            the console — <b>127.0.0.1:4545</b>, your own browser · zero
            proxying
          </figcaption>
        </figure>

        <figure className="surf-fig popup">
          <div className="panel panel-popup">
            <img
              src="/shots/popup-dark.png"
              alt="The Recall extension popup — continue, today's rhythm, threads and the live tail"
            />
          </div>
          <figcaption className="panelcap">
            the popup — glance and act, <b>⌘K</b> to search
          </figcaption>
        </figure>
      </div>
    </Section>
  );
}
