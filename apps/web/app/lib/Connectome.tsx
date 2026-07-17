"use client";

/**
 * The connectome — a brain drawn the way Recall sees one: moments as
 * nodes, continuity as the threads between them. Not a picture — an
 * instrument:
 *
 *   · the anatomy draws in, then the red thread stitches through it
 *   · signals keep firing along the fibres afterwards (deterministic
 *     stagger, no randomness)
 *   · three callouts pin real moments to the figure, lab-style
 *   · run the cursor across it and every node reveals the memory it
 *     holds — the brain is explorable, not decorative
 *
 * Honours prefers-reduced-motion (final state, no theatre).
 */

import { useCallback, useRef, useState } from "react";

// viewBox 0 0 520 460 · side profile, front at the left.
const N = {
  f1: [126, 178], f2: [158, 118], f3: [214, 82], f4: [284, 64],
  f5: [352, 72], f6: [408, 102], f7: [442, 158], f8: [450, 218],
  nc: [414, 250],
  cb1: [444, 286], cb2: [424, 332], cb3: [372, 354], cb4: [324, 344],
  st1: [304, 366], st2: [322, 414],
  u1: [260, 332], u2: [204, 322], u3: [164, 310],
  b2: [148, 296], b1: [120, 240],
  s1: [178, 262], s2: [230, 276], s3: [284, 286],
  i1: [196, 168], i2: [268, 128], i3: [344, 148], i4: [396, 206],
  i5: [300, 208], i6: [228, 220], i7: [352, 280], i8: [318, 316],
  hub: [282, 250],
} as const;

type NodeKey = keyof typeof N;

/* every node holds a moment — the figure is made of a real day */
const SPECIMEN: Record<NodeKey, string> = {
  f1: "9:41 · the first tab of the day",
  f2: "gmail — the inbox attempt",
  f3: "chat · retry logic — claude.ai",
  f4: "docs.rs/tokio — time::interval",
  f5: "webhooks.py · half-written",
  f6: "pr #214 — review pass",
  f7: "stripe docs — retries",
  f8: "search · exponential backoff jitter",
  nc: "linear — REC-142",
  cb1: "figma — seed deck, narrative pass",
  cb2: "wb-1750 · 22-min block",
  cb3: "terminal · cargo test",
  cb4: "spec.md — the api sketch",
  st1: "localhost:4545/docs",
  st2: "git — branch switched",
  u1: "notion — roadmap page",
  u2: "chat · schema design",
  u3: "search · rust lifetimes",
  b2: "calendar — the standup that ran long",
  b1: "readme.md",
  s1: "slack thread — the deploy question",
  s2: "wb-1751 · 47-min block",
  s3: "vercel — deploy log",
  i1: "chat · the websocket bug",
  i2: "reconnect.rs — left mid-edit",
  i3: "mdn — network information api",
  i4: "github issue #88",
  i5: "dwell 4m 12s on the fix",
  i6: "notes.md — the morning plan",
  i7: "test_retry.py — 3 runs",
  i8: "changelog draft",
  hub: "now — the live node",
};

const RING: NodeKey[] = [
  "f1", "f2", "f3", "f4", "f5", "f6", "f7", "f8",
  "nc", "cb1", "cb2", "cb3", "cb4", "st1", "st2",
  "u1", "u2", "u3", "b2", "b1",
];

const WEB: Array<[NodeKey, NodeKey]> = [
  ["s1", "s2"], ["s2", "s3"], ["s3", "i8"], ["s1", "b1"], ["s1", "u3"],
  ["f2", "i1"], ["f3", "i2"], ["f4", "i2"], ["f5", "i3"], ["f6", "i3"],
  ["f7", "i4"], ["f8", "i4"], ["nc", "i7"], ["cb4", "i8"], ["u1", "i8"],
  ["u2", "s2"], ["b2", "s1"], ["b1", "i1"],
  ["i1", "i2"], ["i2", "i3"], ["i3", "i4"], ["i4", "i7"], ["i7", "i8"],
  ["i1", "i6"], ["i2", "i5"], ["i3", "i5"], ["i6", "s1"],
  ["i5", "hub"], ["i6", "hub"], ["hub", "s2"], ["hub", "s3"], ["hub", "i7"],
];

/* fibres that keep firing after the draw — indices into WEB */
const FIRING = [5, 8, 12, 18, 20, 23, 27, 28, 30] as const;

/* lab callouts: node → elbow point → caption */
const CALLOUTS: Array<{
  node: NodeKey;
  elbow: [number, number];
  text: string;
  anchor: "start" | "end";
  tx: number;
}> = [
  { node: "i2", elbow: [150, 66], text: "reconnect.rs · left mid-edit", anchor: "start", tx: 26 },
  { node: "i4", elbow: [462, 116], text: "issue #88", anchor: "end", tx: 500 },
  { node: "i8", elbow: [448, 402], text: "wb-1751 · 47-min block", anchor: "end", tx: 502 },
];

const THREAD = `M -30 300 C 30 292, 72 266, 120 240
  C 152 222, 170 188, 196 168
  C 224 150, 242 134, 268 128
  C 300 122, 306 170, 300 208
  C 296 230, 290 240, 282 250`;

const KEYS = Object.keys(N) as NodeKey[];

export function Connectome() {
  const svgRef = useRef<SVGSVGElement>(null);
  const [hot, setHot] = useState<NodeKey | null>(null);

  const onMove = useCallback((e: React.MouseEvent<SVGSVGElement>) => {
    const el = svgRef.current;
    if (!el) return;
    const r = el.getBoundingClientRect();
    const x = ((e.clientX - r.left) / r.width) * 520;
    const y = ((e.clientY - r.top) / r.height) * 460;
    let best: NodeKey | null = null;
    let bd = 42 * 42; // capture radius in viewBox units
    for (const k of KEYS) {
      const dx = N[k][0] - x;
      const dy = N[k][1] - y;
      const d = dx * dx + dy * dy;
      if (d < bd) {
        bd = d;
        best = k;
      }
    }
    setHot(best);
  }, []);

  const hotPos = hot ? N[hot] : null;

  return (
    <div className="cnxwrap">
      <svg
        ref={svgRef}
        className="cnx"
        viewBox="0 0 520 460"
        role="img"
        aria-label="A brain drawn as connected memory nodes — hover to see the moment each node holds"
        onMouseMove={onMove}
        onMouseLeave={() => setHot(null)}
      >
        {RING.map((k, i) => {
          const a = N[k];
          const b = N[RING[(i + 1) % RING.length]];
          const isHot = hot === k || hot === RING[(i + 1) % RING.length];
          return (
            <line
              key={`r${k}`}
              className={`cnx-edge ring${isHot ? " hot" : ""}`}
              x1={a[0]} y1={a[1]} x2={b[0]} y2={b[1]}
              pathLength={1}
              style={{ transitionDelay: `${0.12 + i * 0.045}s` }}
            />
          );
        })}
        {WEB.map(([ka, kb], i) => {
          const a = N[ka];
          const b = N[kb];
          const isHot = hot === ka || hot === kb;
          return (
            <line
              key={`w${ka}${kb}`}
              className={`cnx-edge${isHot ? " hot" : ""}`}
              x1={a[0]} y1={a[1]} x2={b[0]} y2={b[1]}
              pathLength={1}
              style={{ transitionDelay: `${0.6 + i * 0.04}s` }}
            />
          );
        })}

        {/* signals that keep travelling after the anatomy settles */}
        {FIRING.map((wi, i) => {
          const [ka, kb] = WEB[wi];
          const a = N[ka];
          const b = N[kb];
          return (
            <line
              key={`p${wi}`}
              className={`cnx-pulse${i % 3 === 0 ? " red" : ""}`}
              x1={a[0]} y1={a[1]} x2={b[0]} y2={b[1]}
              pathLength={1}
              style={{
                animationDelay: `${4.6 + i * 0.7}s`,
                animationDuration: `${2.4 + (i % 4) * 0.5}s`,
              }}
            />
          );
        })}

        {/* lab callouts */}
        {CALLOUTS.map((c, i) => {
          const a = N[c.node];
          return (
            <g
              key={c.node}
              className="cnx-callout"
              style={{ transitionDelay: `${4.4 + i * 0.35}s` }}
            >
              <line className="lead" x1={a[0]} y1={a[1]} x2={c.elbow[0]} y2={c.elbow[1]} />
              <line
                className="lead"
                x1={c.elbow[0]} y1={c.elbow[1]}
                x2={c.anchor === "start" ? c.tx : c.tx}
                y2={c.elbow[1]}
              />
              <rect
                className="pin"
                x={a[0] - 2.6} y={a[1] - 2.6}
                width={5.2} height={5.2}
              />
              <text
                className="cap"
                x={c.tx}
                y={c.elbow[1] - 6}
                textAnchor={c.anchor}
              >
                {c.text}
              </text>
            </g>
          );
        })}

        {KEYS.map((k, i) => (
          <circle
            key={`n${k}`}
            className={`cnx-node${hot === k ? " hot" : ""}`}
            cx={N[k][0]} cy={N[k][1]}
            r={k === "hub" ? 5 : k.startsWith("i") || k.startsWith("s") ? 3.2 : 2.8}
            style={{ transitionDelay: `${0.3 + i * 0.035}s` }}
          />
        ))}
        <path className="cnx-thread" d={THREAD} pathLength={1} />
        <circle className="cnx-hub" cx={N.hub[0]} cy={N.hub[1]} r={6} />
      </svg>

      {/* the explorer tip — what this node remembers */}
      <div
        className={`cnx-tip mono${hot ? " on" : ""}`}
        style={
          hotPos
            ? {
                left: `${(hotPos[0] / 520) * 100}%`,
                top: `${(hotPos[1] / 460) * 100}%`,
              }
            : undefined
        }
        aria-hidden={!hot}
      >
        <i /> {hot ? SPECIMEN[hot] : ""}
      </div>
    </div>
  );
}
