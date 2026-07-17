/**
 * The connectome — a brain drawn the way Recall sees one: moments as
 * nodes, continuity as the threads between them. Grey structure
 * draws in first (the anatomy), then the red thread arrives from the
 * left edge and stitches through it (the day being reconnected),
 * ending on the live node.
 *
 * The silhouette is anatomical, facing left: rounded frontal lobe,
 * high parietal crown, occipital curve, a real notch before the
 * cerebellum, a brain-stem drop, and a sylvian-fissure chain across
 * the temporal lobe. Pure SVG + CSS transitions — deterministic,
 * honours prefers-reduced-motion.
 */

// viewBox 0 0 520 460 · side profile, front at the left.
const N = {
  // outline, clockwise from the forehead
  f1: [126, 178], f2: [158, 118], f3: [214, 82], f4: [284, 64],
  f5: [352, 72], f6: [408, 102], f7: [442, 158], f8: [450, 218],
  nc: [414, 250],                     // the cerebrum/cerebellum notch
  cb1: [444, 286], cb2: [424, 332], cb3: [372, 354], cb4: [324, 344],
  st1: [304, 366], st2: [322, 414],   // the stem drops down
  u1: [260, 332], u2: [204, 322], u3: [164, 310],
  b2: [148, 296], b1: [120, 240],
  // sylvian fissure across the temporal lobe
  s1: [178, 262], s2: [230, 276], s3: [284, 286],
  // inner web
  i1: [196, 168], i2: [268, 128], i3: [344, 148], i4: [396, 206],
  i5: [300, 208], i6: [228, 220], i7: [352, 280], i8: [318, 316],
  hub: [282, 250],
} as const;

type NodeKey = keyof typeof N;

const RING: NodeKey[] = [
  "f1", "f2", "f3", "f4", "f5", "f6", "f7", "f8",
  "nc", "cb1", "cb2", "cb3", "cb4", "st1", "st2",
  "u1", "u2", "u3", "b2", "b1",
];

const WEB: Array<[NodeKey, NodeKey]> = [
  // fissure chain
  ["s1", "s2"], ["s2", "s3"], ["s3", "i8"], ["s1", "b1"], ["s1", "u3"],
  // ring → inner
  ["f2", "i1"], ["f3", "i2"], ["f4", "i2"], ["f5", "i3"], ["f6", "i3"],
  ["f7", "i4"], ["f8", "i4"], ["nc", "i7"], ["cb4", "i8"], ["u1", "i8"],
  ["u2", "s2"], ["b2", "s1"], ["b1", "i1"],
  // inner web
  ["i1", "i2"], ["i2", "i3"], ["i3", "i4"], ["i4", "i7"], ["i7", "i8"],
  ["i1", "i6"], ["i2", "i5"], ["i3", "i5"], ["i6", "s1"],
  ["i5", "hub"], ["i6", "hub"], ["hub", "s2"], ["hub", "s3"], ["hub", "i7"],
];

// The red thread: in from the left, up the frontal lobe, along the
// crown's underside, down into the hub.
const THREAD = `M -30 300 C 30 292, 72 266, 120 240
  C 152 222, 170 188, 196 168
  C 224 150, 242 134, 268 128
  C 300 122, 306 170, 300 208
  C 296 230, 290 240, 282 250`;

export function Connectome() {
  return (
    <svg
      className="cnx"
      viewBox="0 0 520 460"
      role="img"
      aria-label="A brain drawn as connected memory nodes, with a red thread reconnecting into it"
    >
      {RING.map((k, i) => {
        const a = N[k];
        const b = N[RING[(i + 1) % RING.length]];
        return (
          <line
            key={`r${k}`}
            className="cnx-edge ring"
            x1={a[0]} y1={a[1]} x2={b[0]} y2={b[1]}
            pathLength={1}
            style={{ transitionDelay: `${0.12 + i * 0.045}s` }}
          />
        );
      })}
      {WEB.map(([ka, kb], i) => {
        const a = N[ka];
        const b = N[kb];
        return (
          <line
            key={`w${ka}${kb}`}
            className="cnx-edge"
            x1={a[0]} y1={a[1]} x2={b[0]} y2={b[1]}
            pathLength={1}
            style={{ transitionDelay: `${0.6 + i * 0.04}s` }}
          />
        );
      })}
      {(Object.keys(N) as NodeKey[]).map((k, i) => (
        <circle
          key={`n${k}`}
          className="cnx-node"
          cx={N[k][0]} cy={N[k][1]}
          r={k === "hub" ? 5 : k.startsWith("i") || k.startsWith("s") ? 3.2 : 2.8}
          style={{ transitionDelay: `${0.3 + i * 0.035}s` }}
        />
      ))}
      <path className="cnx-thread" d={THREAD} pathLength={1} />
      <circle className="cnx-hub" cx={N.hub[0]} cy={N.hub[1]} r={6} />
    </svg>
  );
}
