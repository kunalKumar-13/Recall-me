import { Section, SectionHead, Words } from "../../lib/reveal";

/**
 * The surfaces — actual renders of the shipped product (captured
 * from the real builds in demo mode, no mockup fiction): the console
 * cockpit and the extension popup. The console swaps light/dark with
 * the site theme; the popup ships dark because that's the HUD.
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
            These are real renders of the shipped builds — the engine room
            in your browser, the instrument in your toolbar, the launcher
            over everything.
          </p>
        </SectionHead>
      </div>

      <div className="surf">
        <figure className="surf-main rise">
          <div className="surfframe">
            <div className="surfbar mono">
              <span className="d" />
              <span className="d" />
              <span className="d" />
              <span className="surl">recall · /console — your daemon, your browser</span>
            </div>
            {/* theme-matched: light render in light, dark render in dark */}
            <img
              className="shot-light"
              src="/shots/console-light.png"
              alt="The Recall console — layer meter, today's 24-hour rhythm, continue, threads, live tail"
             
            />
            <img
              className="shot-dark"
              src="/shots/console-dark.png"
              alt="The Recall console in ink night"
             
            />
          </div>
          <figcaption className="surfcap mono">
            the console — connects to <b>127.0.0.1:4545</b> from your own
            browser · zero proxying
          </figcaption>
        </figure>

        <figure className="surf-side rise">
          <div className="surfframe popup">
            <img
              src="/shots/popup-dark.png"
              alt="The Recall extension popup — continue, today's rhythm, threads, live tail"
             
            />
          </div>
          <figcaption className="surfcap mono">
            the popup — glance and act, ⌘K to search
          </figcaption>
        </figure>
      </div>
    </Section>
  );
}
