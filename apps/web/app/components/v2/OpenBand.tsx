import { LINKS } from "../../lib/links";
import { Section } from "../../lib/reveal";

/**
 * Built in the open — the roadmap as shipped truth, not promises.
 * Ticks are things you can run today; circles are said out loud so
 * they can be checked later.
 */
const ITEMS = [
  { done: true, label: "launcher · ⌃space resume" },
  { done: true, label: "browser + editor + desktop capture" },
  { done: true, label: "attention signal (work-blocks)" },
  { done: true, label: "semantic file search" },
  { done: true, label: "macOS .dmg" },
  { done: false, label: "notarized public release" },
  { done: false, label: "behavioural session engine" },
  { done: false, label: "windows + linux" },
] as const;

export function OpenBand() {
  return (
    <Section className="openband" as="div">
      <div className="ob-inner">
        <div className="ob-left rise">
          <div className="ob-title">Built in the open.</div>
          <p className="ob-sub">
            Every layer, every budget, every decision — public. Read the
            code, run the smoke tests, file the issue.
          </p>
          <a
            className="ob-link mono"
            href={LINKS.github}
            target="_blank"
            rel="noreferrer"
          >
            github.com/kunalKumar-13/Recall-me ↗
          </a>
        </div>
        <div className="ob-items">
          {ITEMS.map((it) => (
            <span
              key={it.label}
              className={`ob-item mono${it.done ? " done" : ""}`}
            >
              <i>{it.done ? "✓" : "○"}</i> {it.label}
            </span>
          ))}
        </div>
      </div>
    </Section>
  );
}
