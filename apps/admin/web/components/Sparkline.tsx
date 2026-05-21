import type { SparkPoint } from "../lib/types";

/**
 * A tiny SVG sparkline. No chart library — startup-chart explosions
 * are exactly what the directive said not to build. One line, one
 * soft fill underneath, no axes, no grid, no tooltip.
 */
export function Sparkline({
  values,
  width = 120,
  height = 30,
}: {
  values: SparkPoint[];
  width?: number;
  height?: number;
}) {
  if (values.length < 2) {
    return (
      <svg className="spark-svg" viewBox={`0 0 ${width} ${height}`} aria-hidden />
    );
  }
  const xs = values.map((_, i) => (i / (values.length - 1)) * width);
  const max = Math.max(...values.map((p) => p.v));
  const min = Math.min(...values.map((p) => p.v));
  const range = max - min || 1;
  const ys = values.map((p) => height - ((p.v - min) / range) * (height - 4) - 2);

  const linePts = xs.map((x, i) => `${x.toFixed(1)},${ys[i].toFixed(1)}`).join(" ");
  const fillPts =
    `0,${height} ` +
    xs.map((x, i) => `${x.toFixed(1)},${ys[i].toFixed(1)}`).join(" ") +
    ` ${width},${height}`;

  return (
    <svg
      className="spark-svg"
      viewBox={`0 0 ${width} ${height}`}
      preserveAspectRatio="none"
      aria-hidden
    >
      <polygon className="spark-fill" points={fillPts} />
      <polyline className="spark-path" points={linePts} />
    </svg>
  );
}
