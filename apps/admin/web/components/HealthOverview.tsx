import type { HealthCard } from "../lib/types";

const DOT: Record<HealthCard["health"], string> = {
  green: "dot dot-green",
  yellow: "dot dot-yellow",
  red: "dot dot-red",
  mute: "dot dot-mute",
};

export function HealthOverview({ cards }: { cards: HealthCard[] }) {
  if (cards.length === 0) {
    return (
      <div className="card empty">no health.json yet — drop one in <code>apps/admin/data/</code></div>
    );
  }
  return (
    <div className="grid grid-3">
      {cards.map((c) => (
        <div key={c.id} className="card health">
          <div className="health-label">
            <span className={DOT[c.health]} /> &nbsp;{c.label}
          </div>
          <div className="health-value">
            {c.value}
            {c.unit ? <span className="health-unit">{c.unit}</span> : null}
          </div>
          {c.foot ? <div className="health-foot">{c.foot}</div> : null}
        </div>
      ))}
    </div>
  );
}
