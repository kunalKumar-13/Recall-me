import { LINKS } from "../../lib/links";
import { Section, SectionHead, Words } from "../../lib/reveal";

export function Download() {
  return (
    <Section id="download" className="sec">
      <div className="wrap sechead c">
        <SectionHead index="—" eyebrow="Get Recall">
          <h2>
            <Words>Install once, </Words>
            <em>
              <Words>leave it for years.</Words>
            </em>
          </h2>
        </SectionHead>
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
            <span className="m">Chrome · Edge · Brave</span>
            <span className="g">Add →</span>
          </a>
        </div>
      </div>
    </Section>
  );
}
