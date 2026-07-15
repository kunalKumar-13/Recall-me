import { Section, SectionHead, Words } from "../../lib/reveal";

/**
 * The architecture, drawn: sources on the left, the engine core in
 * the middle, surfaces on the right, with capture flowing along
 * animated beams. It's the true dependency graph — browser / editor /
 * desktop feed 127.0.0.1:4545, the seven layers derive, and the
 * launcher + popup + API read back out.
 */

const SRC = [
  { y: 90, label: "CHROME · EDGE · ARC" },
  { y: 170, label: "VS CODE" },
  { y: 250, label: "DESKTOP FOCUS" },
  { y: 330, label: "GIT HOOKS · CLI" },
] as const;

const OUT = [
  { y: 110, label: "LAUNCHER — ⌃SPACE" },
  { y: 210, label: "EXTENSION POPUP" },
  { y: 310, label: "API · 127.0.0.1:4545" },
] as const;

function beam(x1: number, y1: number, x2: number, y2: number) {
  const mx = (x1 + x2) / 2;
  return `M ${x1} ${y1} C ${mx} ${y1}, ${mx} ${y2}, ${x2} ${y2}`;
}

export function Pipeline() {
  return (
    <Section id="engine" className="sec">
      <div className="wrap sechead c">
        <SectionHead index="03" eyebrow="Architecture">
          <h2>
            <Words>One engine, </Words>
            <em>
              <Words>every surface.</Words>
            </em>
          </h2>
          <p className="lead rise">
            Everything you do flows into one deterministic engine on
            loopback — and back out to every surface you summon.
          </p>
        </SectionHead>
      </div>

      <div className="pipewrap rise">
        <svg
          className="pipesvg"
          viewBox="0 0 960 420"
          role="img"
          aria-label="Sources flow into the local Recall engine, which serves the launcher, popup and API"
        >
          <defs>
            <pattern id="pdots" width="24" height="24" patternUnits="userSpaceOnUse">
              <circle cx="1" cy="1" r="1" fill="rgba(23,22,19,0.10)" />
            </pattern>
            <linearGradient id="pbeam" x1="0" y1="0" x2="1" y2="0">
              <stop offset="0" stopColor="rgba(191,59,43,0)" />
              <stop offset="0.5" stopColor="rgba(191,59,43,0.85)" />
              <stop offset="1" stopColor="rgba(191,59,43,0)" />
            </linearGradient>
          </defs>
          <rect width="960" height="420" fill="url(#pdots)" />

          {/* static wires */}
          {SRC.map((s) => (
            <path key={s.y} d={beam(238, s.y, 442, 210)} className="wire" />
          ))}
          {OUT.map((o) => (
            <path key={o.y} d={beam(518, 210, 722, o.y)} className="wire" />
          ))}
          {/* travelling light on each wire */}
          {SRC.map((s, i) => (
            <path
              key={`b${s.y}`}
              d={beam(238, s.y, 442, 210)}
              className="beam"
              style={{ animationDelay: `${i * 0.9}s` }}
            />
          ))}
          {OUT.map((o, i) => (
            <path
              key={`b${o.y}`}
              d={beam(518, 210, 722, o.y)}
              className="beam out"
              style={{ animationDelay: `${1.2 + i * 0.9}s` }}
            />
          ))}

          {/* source nodes */}
          {SRC.map((s) => (
            <g key={`n${s.y}`}>
              <rect x="66" y={s.y - 17} width="172" height="34" rx="8" className="pnode" />
              <text x="152" y={s.y + 4} textAnchor="middle" className="plabel">
                {s.label}
              </text>
            </g>
          ))}

          {/* the core */}
          <g>
            <rect x="442" y="172" width="76" height="76" rx="16" className="pcore" />
            <circle cx="480" cy="210" r="7" fill="#bf3b2b" />
            <text x="480" y="272" textAnchor="middle" className="plabel core">
              RECALL ENGINE
            </text>
            <text x="480" y="290" textAnchor="middle" className="pmuted">
              events → sessions → contexts → threads → recovery
            </text>
          </g>

          {/* output nodes */}
          {OUT.map((o) => (
            <g key={`o${o.y}`}>
              <rect x="722" y={o.y - 17} width="168" height="34" rx="8" className="pnode" />
              <text x="806" y={o.y + 4} textAnchor="middle" className="plabel">
                {o.label}
              </text>
            </g>
          ))}
        </svg>
        <div className="pipecmd mono rise">
          <span className="dollar">$</span> everything stays in{" "}
          <b>~/.recall/</b> — delete the folder, it never happened
        </div>
        <div className="pipebudgets mono rise">
          budgets, enforced by the test suite: writes &lt;2 ms · search
          &lt;60 ms · resurfacing &lt;25 ms · recovery &lt;80 ms
        </div>
      </div>
    </Section>
  );
}
