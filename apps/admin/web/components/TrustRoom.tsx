import type { TrustCard } from "../lib/types";

const PILL: Record<TrustCard["state"], string> = {
  green: "pill pill-green",
  yellow: "pill pill-yellow",
  red: "pill pill-red",
};

export function TrustRoom({ cards }: { cards: TrustCard[] }) {
  if (cards.length === 0) {
    return <div className="card empty">no trust.json yet</div>;
  }
  return (
    <div className="grid grid-3">
      {cards.map((c) => (
        <div key={c.id} className="card health">
          <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
            <div className="health-label">{c.label}</div>
            <span style={{ marginLeft: "auto" }} className={PILL[c.state]}>
              {c.state}
            </span>
          </div>
          <div className="health-value">{c.count}</div>
          <div className="health-foot">{c.detail}</div>
        </div>
      ))}
    </div>
  );
}
