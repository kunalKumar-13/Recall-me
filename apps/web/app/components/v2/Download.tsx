import { LINKS } from "../../lib/links";
import { Section, SectionHead, Words } from "../../lib/reveal";

/** The closer — one chapter, one promise, the ways in. */
export function Download() {
  return (
    <Section id="download" className="sec">
      <div className="wrap sechead c">
        <SectionHead index="08" eyebrow="Get Recall">
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
