/**
 * The connectome — a brain drawn the way Recall sees one: moments as
 * nodes, continuity as the threads between them. Grey structure
 * draws in first (the anatomy), then the red thread arrives from the
 * left edge and stitches through it (the day being reconnected),
 * ending on the live node.
 *
 * Pure SVG + CSS transitions — deterministic, no randomness, honours
 * prefers-reduced-motion (final state, no theatre).
 */

// Hand-placed side-profile brain, facing right. viewBox 0 0 520 460.
const N = {
  // outline, clockwise from the front-top
  f1: [128, 168], f2: [168, 108], f3: [232, 74], f4: [304, 62],
  f5: [368, 78], f6: [418, 118], f7: [448, 176], f8: [452, 240],
  f9: [430, 300], cb1: [388, 348], cb2: [332, 372], st: [296, 408],
  t1: [244, 348], t2: [186, 322], b1: [140, 268], b2: [118, 214],
  // inner web
  i1: [212, 176], i2: [286, 138], i3: [356, 186], i4: [388, 258],
  i5: [304, 232], i6: [232, 252], i7: [318, 312], i8: [256, 300],
  hub: [300, 262],
} as const;

type NodeKey = keyof typeof N;

const RING: NodeKey[] = [
  "f1", "f2", "f3", "f4", "f5", "f6", "f7", "f8", "f9",
  "cb1", "cb2", "st", "t1", "t2", "b1", "b2",
];

const WEB: Array<[NodeKey, NodeKey]> = [
  ["f2", "i1"], ["f3", "i2"], ["f4", "i2"], ["f5", "i3"], ["f6", "i3"],
  ["f7", "i4"], ["f8", "i4"], ["f9", "i7"], ["cb1", "i7"], ["cb2", "i7"],
  ["t1", "i8"], ["t2", "i6"], ["b1", "i6"], ["b2", "i1"],
  ["i1", "i2"], ["i2", "i3"], ["i3", "i4"], ["i1", "i6"], ["i2", "i5"],
  ["i3", "i5"], ["i4", "i7"], ["i6", "i8"], ["i7", "i8"], ["i5", "hub"],
  ["i6", "hub"], ["i8", "hub"], ["i4", "hub"], ["st", "i7"],
];

// The red thread: in from the left edge, through the web, to the hub.
const THREAD = `M -30 306 C 40 296, 70 258, 118 214
  C 150 190, 178 182, 212 176
  C 250 170, 268 150, 286 138
  C 316 148, 296 196, 304 232
  C 306 246, 300 254, 300 262`;

export function Connectome() {
  return (
    <svg
      className="cnx"
      viewBox="0 0 520 460"
      role="img"
      aria-label="A brain drawn as connected memory nodes, with a red thread reconnecting into it"
    >
      {/* anatomy: the outline ring */}
      {RING.map((k, i) => {
        const a = N[k];
        const b = N[RING[(i + 1) % RING.length]];
        return (
          <line
            key={`r${k}`}
            className="cnx-edge"
            x1={a[0]} y1={a[1]} x2={b[0]} y2={b[1]}
            pathLength={1}
            style={{ transitionDelay: `${0.12 + i * 0.05}s` }}
          />
        );
      })}
      {/* anatomy: the inner web */}
      {WEB.map(([ka, kb], i) => {
        const a = N[ka];
        const b = N[kb];
        return (
          <line
            key={`w${ka}${kb}`}
            className="cnx-edge"
            x1={a[0]} y1={a[1]} x2={b[0]} y2={b[1]}
            pathLength={1}
            style={{ transitionDelay: `${0.5 + i * 0.045}s` }}
          />
        );
      })}
      {/* nodes */}
      {(Object.keys(N) as NodeKey[]).map((k, i) => (
        <circle
          key={`n${k}`}
          className="cnx-node"
          cx={N[k][0]} cy={N[k][1]}
          r={k === "hub" ? 5 : k.startsWith("i") ? 3.4 : 2.8}
          style={{ transitionDelay: `${0.3 + i * 0.04}s` }}
        />
      ))}
      {/* the thread finds its way in */}
      <path className="cnx-thread" d={THREAD} pathLength={1} />
      <circle className="cnx-hub" cx={N.hub[0]} cy={N.hub[1]} r={6} />
    </svg>
  );
}
