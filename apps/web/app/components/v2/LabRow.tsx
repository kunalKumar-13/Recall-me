import { Section } from "../../lib/reveal";

/**
 * The lab row — three columns under the hero, the way a research
 * group states itself: what we work on, what we believe, what just
 * shipped. Every word checkable against the repo.
 */

const FOCUS = [
  { t: "Capture", h: "#extension" },
  { t: "Reconstruction", h: "#how" },
  { t: "Resurfacing", h: "#features" },
  { t: "Recovery", h: "#features" },
];

const PRINCIPLES = [
  { n: "01", t: "Local-first", d: "nothing leaves your machine" },
  { n: "02", t: "Deterministic", d: "same events in, same memory out" },
  { n: "03", t: "Inspectable", d: "plain files — cat, grep, rm" },
  { n: "04", t: "Budgeted", d: "speed enforced by the test suite" },
  { n: "05", t: "Calm", d: "no badges, no feed, no noise" },
];

/* a deterministic little scatter — the loop's day-shape, drawn */
const DOTS = [
  [8, 30], [14, 24], [20, 27], [26, 16], [32, 20], [38, 10],
  [44, 14], [50, 7], [56, 12], [62, 5], [68, 9], [74, 4],
] as const;

export function LabRow() {
  return (
    <Section className="labrow" as="div">
      <div className="lab-inner">
        <div className="lab-col rise">
          <div className="lab-label mono">· our focus</div>
          <ul className="lab-focus">
            {FOCUS.map((f) => (
              <li key={f.t}>
                <a href={f.h} className="mono">
                  {f.t} <span className="ar">→</span>
                </a>
              </li>
            ))}
          </ul>
        </div>
        <div className="lab-col rise">
          <div className="lab-label mono">· principles</div>
          <ul className="lab-prin">
            {PRINCIPLES.map((p) => (
              <li key={p.n}>
                <span className="n mono">{p.n}</span>
                <span className="t">{p.t}</span>
                <span className="d">— {p.d}</span>
              </li>
            ))}
          </ul>
        </div>
        <div className="lab-col rise">
          <div className="lab-label mono">· latest from the engine</div>
          <a className="lab-card" href="/console">
            <svg viewBox="0 0 82 36" className="lab-scatter" aria-hidden>
              {DOTS.map(([x, y], i) => (
                <circle
                  key={i}
                  cx={x}
                  cy={y}
                  r={1.6}
                  className={i % 4 === 1 ? "hot" : ""}
                />
              ))}
              <line x1="4" y1="33" x2="78" y2="33" className="axis" />
              <line x1="4" y1="33" x2="4" y2="3" className="axis" />
            </svg>
            <span className="lab-card-t">The daily continuity loop</span>
            <span className="lab-card-d">
              Recall grades itself — returns, resumes, verdicts. Counts
              only, never content.
            </span>
            <span className="lab-card-g mono">open the console →</span>
          </a>
        </div>
      </div>
    </Section>
  );
}
