/**
 * The Recall mark: a mind in miniature — memory nodes joined by
 * threads, one of them alive. Same connectome the hero draws, at
 * glyph size. Edges take the surrounding ink; the live node is the
 * one spend of red.
 */
export function Mark({ size = 22 }: { size?: number }) {
  const nodes: Array<[number, number]> = [
    [5.5, 16.5], // front-low
    [8, 8],      // front-top
    [15, 4.5],   // crown
    [21.5, 8],   // rear-top
    [23.5, 15],  // occipital
    [18.5, 21.5],// cerebellum
    [11, 21],    // temporal
  ];
  const hub: [number, number] = [14.5, 13.5];
  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 28 28"
      fill="none"
      aria-hidden
      className="mark"
    >
      {/* ring */}
      {nodes.map((a, i) => {
        const b = nodes[(i + 1) % nodes.length];
        return (
          <line
            key={`r${i}`}
            x1={a[0]} y1={a[1]} x2={b[0]} y2={b[1]}
            stroke="currentColor"
            strokeOpacity="0.35"
            strokeWidth="1.2"
          />
        );
      })}
      {/* spokes into the hub */}
      {[0, 1, 3, 4, 6].map((i) => (
        <line
          key={`s${i}`}
          x1={nodes[i][0]} y1={nodes[i][1]} x2={hub[0]} y2={hub[1]}
          stroke="currentColor"
          strokeOpacity="0.22"
          strokeWidth="1"
        />
      ))}
      {nodes.map((a, i) => (
        <circle key={`n${i}`} cx={a[0]} cy={a[1]} r="1.6" fill="currentColor" fillOpacity="0.75" />
      ))}
      <circle cx={hub[0]} cy={hub[1]} r="2.8" fill="var(--red)" />
    </svg>
  );
}
