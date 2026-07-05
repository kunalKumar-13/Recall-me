import { LINKS } from "../../lib/links";
import { Section, Words } from "../../lib/reveal";

export function Finale() {
  return (
    <Section className="sec final">
      <div className="wrap">
        <h2>
          <Words>Your mind, </Words>
          <em className="thread-mark">
            <Words>rethreaded</Words>
          </em>
          <Words>.</Words>
        </h2>
        <div className="btns rise">
          <a className="btn solid" href={LINKS.release}>
            Download for macOS
          </a>
          <a className="btn line" href="#top">
            Summon anywhere <span className="k">⌃Space</span>
          </a>
        </div>
      </div>
    </Section>
  );
}
