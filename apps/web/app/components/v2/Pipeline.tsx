import { Section, SectionHead, Words } from "../../lib/reveal";

/**
 * The architecture, alive: everything you do (browser, editor,
 * desktop, git) rides into one local engine as a labelled event;
 * the engine's seven layers ripple as they derive; and results ride
 * back out to every surface. The true dependency graph — drawn as
 * the flow it actually is, not a static box diagram.
 *
 * All motion is SVG <animateMotion> along the wire paths, so it
 * scales with the viewBox and needs no JS. Deterministic by
 * construction — same frame every load.
 */

const CORE_IN = { x: 400, y: 230 };
const CORE_OUT = { x: 560, y: 230 };

const SRC = [
  { y: 96, label: "Chrome · Edge · Arc", event: "stripe.com", icon: "globe" },
  { y: 188, label: "VS Code", event: "reconnect.rs", icon: "code" },
  { y: 272, label: "Desktop focus", event: "⌥ 4m 12s", icon: "window" },
  { y: 356, label: "Git · CLI", event: "git commit", icon: "term" },
] as const;

const OUT = [
  { y: 120, label: "Launcher — ⌃space", result: "↵ resume" },
  { y: 214, label: "Extension popup", result: "88 today" },
  { y: 308, label: "Console · API", result: "GET /v1/search" },
] as const;

function wire(x1: number, y1: number, x2: number, y2: number) {
  const mx = (x1 + x2) / 2;
  return `M ${x1} ${y1} C ${mx} ${y1}, ${mx} ${y2}, ${x2} ${y2}`;
}

const ICONS: Record<string, JSX.Element> = {
  globe: (
    <>
      <circle cx="0" cy="0" r="7" />
      <path d="M-7 0h14M0-7c3.5 3 3.5 11 0 14M0-7c-3.5 3-3.5 11 0 14" fill="none" />
    </>
  ),
  code: <path d="M-3-5-8 0l5 5M3-5 8 0l-5 5M1-6-1 6" fill="none" />,
  window: (
    <>
      <rect x="-7" y="-6" width="14" height="12" rx="1.5" fill="none" />
      <path d="M-7-2h14" fill="none" />
    </>
  ),
  term: (
    <>
      <rect x="-7" y="-6" width="14" height="12" rx="1.5" fill="none" />
      <path d="M-4-2l2.5 2-2.5 2M0 2h4" fill="none" />
    </>
  ),
};

const LAYERS = 7;

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
            loopback — through seven layers, and back out to every surface
            you summon.
          </p>
        </SectionHead>
      </div>

      <div className="pipewrap rise">
        <svg
          className="pipesvg"
          viewBox="0 0 960 460"
          role="img"
          aria-label="Browser, editor, desktop and git events flow into the local Recall engine, which processes them through seven layers and serves the launcher, popup and API"
        >
          <defs>
            <pattern id="pdots" width="26" height="26" patternUnits="userSpaceOnUse">
              <circle cx="1" cy="1" r="1" className="pdot" />
            </pattern>
            {SRC.map((s, i) => (
              <path
                key={`wi${i}`}
                id={`win${i}`}
                d={wire(232, s.y, CORE_IN.x, CORE_IN.y)}
                fill="none"
              />
            ))}
            {OUT.map((o, i) => (
              <path
                key={`wo${i}`}
                id={`wout${i}`}
                d={wire(CORE_OUT.x, CORE_OUT.y, 728, o.y)}
                fill="none"
              />
            ))}
          </defs>

          <rect width="960" height="460" fill="url(#pdots)" />

          {/* wires (static hairlines) */}
          {SRC.map((_, i) => (
            <use key={`uwi${i}`} href={`#win${i}`} className="wire" />
          ))}
          {OUT.map((_, i) => (
            <use key={`uwo${i}`} href={`#wout${i}`} className="wire" />
          ))}

          {/* ingest packets — labelled events riding into the core */}
          {SRC.map((s, i) => (
            <g key={`pi${i}`} className="pkt">
              <g>
                <rect x="-52" y="-11" width="104" height="22" rx="11" className="pkt-bg" />
                <text className="pkt-t">{s.event}</text>
                <animateMotion
                  dur="3.4s"
                  begin={`${-i * 0.85}s`}
                  repeatCount="indefinite"
                  rotate="0"
                  keyPoints="0;1"
                  keyTimes="0;1"
                  calcMode="linear"
                >
                  <mpath href={`#win${i}`} />
                </animateMotion>
                <animate
                  attributeName="opacity"
                  dur="3.4s"
                  begin={`${-i * 0.85}s`}
                  repeatCount="indefinite"
                  values="0;1;1;0"
                  keyTimes="0;0.12;0.8;1"
                />
              </g>
            </g>
          ))}

          {/* serve packets — results riding out to each surface */}
          {OUT.map((o, i) => (
            <g key={`po${i}`} className="pkt out">
              <g>
                <rect x="-56" y="-11" width="112" height="22" rx="11" className="pkt-bg" />
                <text className="pkt-t">{o.result}</text>
                <animateMotion
                  dur="3.4s"
                  begin={`${1.2 - i * 0.85}s`}
                  repeatCount="indefinite"
                  rotate="0"
                >
                  <mpath href={`#wout${i}`} />
                </animateMotion>
                <animate
                  attributeName="opacity"
                  dur="3.4s"
                  begin={`${1.2 - i * 0.85}s`}
                  repeatCount="indefinite"
                  values="0;1;1;0"
                  keyTimes="0;0.14;0.82;1"
                />
              </g>
            </g>
          ))}

          {/* source nodes: icon + label */}
          {SRC.map((s, i) => (
            <g key={`n${i}`} className="pnode-g">
              <rect x="40" y={s.y - 19} width="192" height="38" rx="9" className="pnode" />
              <g transform={`translate(66 ${s.y})`} className="picon">
                {ICONS[s.icon]}
              </g>
              <text x="88" y={s.y + 4} className="plabel src">
                {s.label}
              </text>
            </g>
          ))}

          {/* the core — a processor with seven layers rippling */}
          <g className="pcore-g">
            <rect x="400" y="150" width="160" height="160" rx="20" className="pcore" />
            <text x="480" y="180" textAnchor="middle" className="pcore-title">
              RECALL ENGINE
            </text>
            {Array.from({ length: LAYERS }).map((_, i) => (
              <rect
                key={`L${i}`}
                x={422 + i * 17.5}
                y="200"
                width="10"
                height="44"
                rx="3"
                className="player"
              >
                <animate
                  attributeName="opacity"
                  dur="2.1s"
                  begin={`${i * 0.16}s`}
                  repeatCount="indefinite"
                  values="0.2;1;0.2"
                  keyTimes="0;0.5;1"
                />
                <animate
                  attributeName="height"
                  dur="2.1s"
                  begin={`${i * 0.16}s`}
                  repeatCount="indefinite"
                  values="20;44;20"
                  keyTimes="0;0.5;1"
                />
                <animate
                  attributeName="y"
                  dur="2.1s"
                  begin={`${i * 0.16}s`}
                  repeatCount="indefinite"
                  values="212;200;212"
                  keyTimes="0;0.5;1"
                />
              </rect>
            ))}
            <text x="480" y="272" textAnchor="middle" className="pcore-sub">
              127.0.0.1:4545 · local only
            </text>
            <text x="480" y="340" textAnchor="middle" className="pmuted">
              events → sessions → contexts → resurfacing → threads →
            </text>
            <text x="480" y="356" textAnchor="middle" className="pmuted">
              evolution → recovery
            </text>
          </g>

          {/* output nodes */}
          {OUT.map((o, i) => (
            <g key={`o${i}`} className="pnode-g">
              <rect x="728" y={o.y - 19} width="192" height="38" rx="9" className="pnode" />
              <text x="748" y={o.y + 4} className="plabel out">
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
