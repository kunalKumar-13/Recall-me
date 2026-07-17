import { LINKS } from "../../lib/links";
import { Section, SectionHead, Words } from "../../lib/reveal";

/** The closer — one chapter, one promise, the ways in. */
export function Download() {
  return (
    <Section id="download" className="sec">
      <div className="wrap sechead c">
        <SectionHead index="09" eyebrow="Get Recall">
          <h2>
            <Words>Your mind, </Words>
            <em className="thread-mark">
              <Words>rethreaded</Words>
            </em>
            <Words>.</Words>
          </h2>
          <p className="lead rise">
            Install once, leave it running for years. Plain files, one
            folder, zero cloud — and one keystroke back to the work.
          </p>
        </SectionHead>
        <div className="btns rise" style={{ justifyContent: "center" }}>
          <a className="btn solid" href={LINKS.release}>
            Download for macOS <span className="ar">→</span>
          </a>
          <a className="btn line" href="#top">
            Summon anywhere <span className="k">⌃Space</span>
          </a>
        </div>
        <div className="quick stagger">
          <div className="qstep">
            <span className="qn mono">step 01</span>
            <span className="qt">Open the .dmg</span>
            <span className="qd">
              Drag Recall to Applications. It sits in the menu bar and
              starts the local engine.
            </span>
          </div>
          <div className="qstep">
            <span className="qn mono">step 02</span>
            <span className="qt">Add the extension</span>
            <span className="qd">
              Chrome, Edge, Brave or Arc — capture starts quietly, with an
              exclusion list you control.
            </span>
          </div>
          <div className="qstep">
            <span className="qn mono">step 03</span>
            <span className="qt">Press ⌃Space</span>
            <span className="qd">
              Work normally. Next interruption, one keystroke hands the
              thread back.
            </span>
          </div>
        </div>
        <div className="dlrows stagger">
          <a className="dlrow" href={LINKS.release}>
            <span className="p">macOS</span>
            <span className="m">Apple Silicon · .dmg</span>
            <span className="g">Download →</span>
          </a>
          <a className="dlrow" href={LINKS.release}>
            <span className="p">Windows</span>
            <span className="m">x64 · installer</span>
            <span className="g">Download →</span>
          </a>
          <a className="dlrow" href={LINKS.github}>
            <span className="p">Browser extension</span>
            <span className="m">Chrome · Edge · Brave · Arc</span>
            <span className="g">Add →</span>
          </a>
        </div>
      </div>
    </Section>
  );
}
