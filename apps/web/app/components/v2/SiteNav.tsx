import { LINKS } from "../../lib/links";

export function SiteNav() {
  return (
    <div className="topbar">
      <div className="row">
        <a className="brand" href="#top">
          <span className="dot" />
          Recall
        </a>
        <nav className="topnav">
          <a className="hide-sm" href="#film">
            Demo
          </a>
          <a className="hide-sm" href="#how">
            How it works
          </a>
          <a className="hide-sm" href="#extension">
            Extension
          </a>
          <a className="hide-sm" href="#engine">
            Engine
          </a>
          <a className="hide-sm" href="#trust">
            Privacy
          </a>
          <a className="hide-sm" href="#faq">
            FAQ
          </a>
          <a href={LINKS.docs} target="_blank" rel="noreferrer">
            Docs
          </a>
          <a className="cta" href="#download">
            Download
          </a>
        </nav>
      </div>
    </div>
  );
}
