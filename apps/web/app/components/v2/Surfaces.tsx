import { Section, SectionHead, Words } from "../../lib/reveal";

/**
 * The surfaces — actual renders of the shipped product (captured
 * from the real builds in demo mode, no mockup fiction), now shown
 * in the hardware they live in: the console on a laptop, the popup
 * dropping from a browser toolbar. The console render swaps
 * light/dark with the site theme; the popup ships dark — that's the
 * HUD.
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
            Real renders of the shipped builds — the engine room on your
            desk, the instrument in your toolbar, the launcher over
            everything.
          </p>
        </SectionHead>
      </div>

      <div className="surf">
        {/* the console, on a laptop */}
        <figure className="surf-main rise">
          <div className="laptop">
            <div className="laptop-lid">
              <div className="laptop-bezel">
                <div className="laptop-cam" aria-hidden />
                <div className="laptop-screen">
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
              </div>
            </div>
            <div className="laptop-base" aria-hidden>
              <div className="laptop-notch" />
            </div>
          </div>
          <figcaption className="surfcap mono">
            the console — talks to <b>127.0.0.1:4545</b> from your own
            browser · zero proxying
          </figcaption>
        </figure>

        {/* the popup, dropping from the browser toolbar */}
        <figure className="surf-side rise">
          <div className="extctx">
            <div className="ext-toolbar" aria-hidden>
              <span className="ext-dot r" />
              <span className="ext-dot y" />
              <span className="ext-dot g" />
              <span className="ext-omni">recall — never lose the thread</span>
              <span className="ext-ico puzzle">
                <svg viewBox="0 0 16 16" width="13" height="13">
                  <path
                    d="M6 2h4v2a1.5 1.5 0 0 0 3 0V2h1v4h-2a1.5 1.5 0 0 0 0 3h2v4h-4v-2a1.5 1.5 0 0 0-3 0v2H2V9h2a1.5 1.5 0 0 0 0-3H2V2h4Z"
                    fill="none"
                    stroke="currentColor"
                    strokeWidth="1.1"
                  />
                </svg>
              </span>
              <span className="ext-ico live">
                <svg viewBox="0 0 28 28" width="15" height="15">
                  <path
                    d="M3 20.5 C 9 4.5, 13.5 25, 19.5 12.5 S 24.5 8.5, 24.6 8.4"
                    stroke="var(--red)"
                    strokeWidth="2.6"
                    fill="none"
                    strokeLinecap="round"
                  />
                  <circle cx="24.4" cy="8.2" r="3.4" fill="var(--red)" />
                </svg>
              </span>
            </div>
            <div className="ext-caret" aria-hidden />
            <div className="ext-pop">
              <img
                src="/shots/popup-dark.png"
                alt="The Recall extension popup — continue, today's rhythm, threads, live tail"
              />
            </div>
          </div>
          <figcaption className="surfcap mono">
            the popup — glance and act, ⌘K to search
          </figcaption>
        </figure>
      </div>
    </Section>
  );
}
