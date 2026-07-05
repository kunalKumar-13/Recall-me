import { Section, SectionHead, Words } from "../../lib/reveal";

/** The extension chapter — the popup, the capture table, the four
 *  nevers, the durable pipeline, and the three-step install. */
export function Extension() {
  return (
    <Section id="extension" className="sec">
      <div className="wrap sechead">
        <SectionHead index="05" eyebrow="The browser extension">
          <h2>
            <Words>A quiet witness, </Words>
            <br />
            <em>
              <Words>with a perfect memory.</Words>
            </em>
          </h2>
        </SectionHead>
        <p className="body rise">
          The extension is how Recall sees your browsing — and it is
          deliberately small. It reads the URL and title of pages you visit,
          recognises searches and AI conversations, and hands them to the
          daemon on your machine. It cannot read page contents, and it cannot
          talk to any other server.
        </p>

        <div className="ext rise">
          <div className="pmock" aria-label="The extension popup">
            <div className="pm-h">
              <span className="d" />
              <span className="b">Recall</span>
              <span className="s">daemon ok</span>
            </div>
            <div className="pm-sec">Continue</div>
            <div className="pm-row sel">
              <div>
                <div className="pm-t">WebSocket reconnect bug</div>
                <div className="pm-c">1 file · 1 chat · 2 tabs · resume</div>
              </div>
              <span className="pm-a">open →</span>
            </div>
            <div className="pm-sec">Active threads</div>
            <div className="pm-row">
              <div>
                <div className="pm-t">Seed deck — narrative pass</div>
                <div className="pm-c">yesterday · 6 events</div>
              </div>
            </div>
            <div className="pm-row">
              <div>
                <div className="pm-t">Hiring — staff designer</div>
                <div className="pm-c">2 weeks · 11 events</div>
              </div>
            </div>
            <div className="pm-sec">Today</div>
            <div className="pm-tl">
              <span className="t">14:12</span>
              <span className="k">chat</span>
              <span>WebSocket reconnect strategy</span>
            </div>
            <div className="pm-tl">
              <span className="t">14:03</span>
              <span className="k">search</span>
              <span>exponential backoff jitter</span>
            </div>
            <div className="pm-tl">
              <span className="t">13:41</span>
              <span className="k">visit</span>
              <span>docs.rs/tokio — time::interval</span>
            </div>
            <div className="pm-f">
              <span className="pill">local only</span>
              <span className="pill">no cloud</span>
              <span className="pill">0 uploads</span>
              <span className="pill">daemon ok</span>
              <span className="pill q">3 queued</span>
            </div>
          </div>
          <div>
            <div className="cap-table stagger">
              <div className="cap-tr">
                <span className="a">Any page you visit</span>
                <span className="b">→ visit · url + title</span>
              </div>
              <div className="cap-tr">
                <span className="a">
                  Google, DuckDuckGo, Bing, Kagi, Perplexity
                </span>
                <span className="b">→ search · the query</span>
              </div>
              <div className="cap-tr">
                <span className="a">ChatGPT, Claude, Gemini, Copilot, Grok…</span>
                <span className="b">→ chat · conversation title</span>
              </div>
              <div className="cap-tr">
                <span className="a">Single-page apps changing routes</span>
                <span className="b">→ captured · no reload needed</span>
              </div>
            </div>
            <ul className="never stagger">
              <li>
                <span className="x">✕</span>
                <span>Never page contents — the DOM is never read.</span>
              </li>
              <li>
                <span className="x">✕</span>
                <span>Never incognito windows, ever.</span>
              </li>
              <li>
                <span className="x">✕</span>
                <span>Never sites on your exclude list.</span>
              </li>
              <li>
                <span className="x">✕</span>
                <span>
                  Never any server except{" "}
                  <span className="mono">127.0.0.1:4545</span> — the browser
                  physically refuses.
                </span>
              </li>
            </ul>
          </div>
        </div>

        <div className="pipe rise">
          {"tabs · SPA routes · chats  →  "}
          <span className="k">normalize</span>
          {"  →  "}
          <span className="k">durable outbox</span>
          {"  →  batched POST /v1/events/batch  →  "}
          <span className="k">engine</span>
          {"\n"}
          <span className="hot">daemon asleep or laptop offline?</span>
          {" events wait in the outbox and sync the moment it returns — nothing is lost."}
        </div>

        <div className="rows stagger">
          <div className="rown">
            <span className="i">01</span>
            <h3>Install the app</h3>
            <p>
              Download Recall for macOS or Windows — the daemon starts with
              your machine and holds your memory.
            </p>
          </div>
          <div className="rown">
            <span className="i">02</span>
            <h3>Add the extension</h3>
            <p>
              Chrome, Edge, Brave or Arc — one click, two permissions, one
              loopback origin.
            </p>
          </div>
          <div className="rown">
            <span className="i">03</span>
            <h3>Forget about it</h3>
            <p>
              The toolbar icon is a glance surface: your strongest thread,
              today&apos;s trail, and proof that everything stayed local.
            </p>
          </div>
        </div>

        <p className="body rise" style={{ marginTop: "clamp(30px, 4vw, 52px)" }}>
          And the browser is only the first source. Memory has one door —
          a loopback API — so anything you work in can feed it.
        </p>
        <div className="cap-table stagger">
          <div className="cap-tr">
            <span className="a">Browser — visits, searches, AI chats</span>
            <span className="b">built in</span>
          </div>
          <div className="cap-tr">
            <span className="a">VS Code — the files you settle on and save</span>
            <span className="b">companion extension</span>
          </div>
          <div className="cap-tr">
            <span className="a">Git — commits and branch switches</span>
            <span className="b">one-line hook</span>
          </div>
          <div className="cap-tr">
            <span className="a">Anything else — scripts, notebooks, window managers</span>
            <span className="b">POST /v1/events/batch</span>
          </div>
        </div>
      </div>
    </Section>
  );
}
