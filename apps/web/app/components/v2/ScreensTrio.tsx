import { Section, SectionHead, Words } from "../../lib/reveal";

/** Three real launcher states, drawn as quiet panels. */
export function ScreensTrio() {
  return (
    <Section id="screens" className="sec">
      <div className="wrap sechead">
        <SectionHead index="04" eyebrow="One panel · Ctrl-Space">
          <h2>
            <Words>Three states, </Words>
            <em>
              <Words>one thread.</Words>
            </em>
          </h2>
        </SectionHead>
        <div className="trio stagger">
          <div className="shot">
            <div className="launcher">
              <div className="lc-search">
                <span>⌕</span>
                <span className="ph">Search your memory…</span>
              </div>
              <div className="lc-head">Continue where you left off</div>
              <div className="lc-row sel">
                <div>
                  <div className="lc-title">WebSocket reconnect bug</div>
                  <div className="lc-cap">3 tabs · 2 files</div>
                </div>
                <span className="lc-hint">↵</span>
              </div>
              <div className="lc-row">
                <div>
                  <div className="lc-title">Seed deck — narrative</div>
                  <div className="lc-cap">yesterday · 6 events</div>
                </div>
              </div>
              <div className="lc-foot">
                <span>↵ resume</span>
              </div>
            </div>
            <div className="cap">
              <span className="t">Recover</span>
              <span className="s">
                The resting state — your strongest interrupted thread, one
                keystroke away.
              </span>
            </div>
          </div>
          <div className="shot">
            <div className="launcher">
              <div className="lc-search">
                <span>⌕</span>
                <span className="ty">reconnect</span>
              </div>
              <div className="lc-head">3 results</div>
              <div className="lc-row sel">
                <div>
                  <div className="lc-title">WebSocket.close() — MDN</div>
                  <div className="lc-cap">moment · mozilla.org</div>
                </div>
                <span className="lc-hint">↵</span>
              </div>
              <div className="lc-row">
                <div>
                  <div className="lc-title">Reconnect strategy</div>
                  <div className="lc-cap">session · 14 events</div>
                </div>
              </div>
              <div className="lc-foot">
                <span>↵ open</span>
              </div>
            </div>
            <div className="cap">
              <span className="t">Search</span>
              <span className="s">
                Type, and your memory answers — moments, sessions, contexts.
              </span>
            </div>
          </div>
          <div className="shot">
            <div className="launcher">
              <div className="lc-head" style={{ paddingTop: 15 }}>
                ← Rust async research
              </div>
              <div className="lc-row sel">
                <div>
                  <div className="lc-title">Research</div>
                  <div className="lc-cap">reading · days 1–2</div>
                </div>
              </div>
              <div className="lc-row">
                <div>
                  <div className="lc-title">Implementation</div>
                  <div className="lc-cap">building · days 2–4</div>
                </div>
              </div>
              <div className="lc-row">
                <div>
                  <div className="lc-title">Revisit</div>
                  <div className="lc-cap">debugging · today</div>
                </div>
              </div>
              <div className="lc-foot">
                <span>← back</span>
              </div>
            </div>
            <div className="cap">
              <span className="t">Evolve</span>
              <span className="s">
                Open any thread to see the phases it moved through.
              </span>
            </div>
          </div>
        </div>
      </div>
    </Section>
  );
}
