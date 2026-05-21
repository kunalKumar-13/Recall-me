import type { FeedbackItem, FeedbackTag } from "../lib/types";

const TAG_PILL: Record<FeedbackTag, string> = {
  pain: "pill pill-red",
  bug: "pill pill-yellow",
  confusion: "pill pill-yellow",
  trust: "pill pill-accent",
  feature: "pill pill-mute",
};

export function FeedbackRoom({ items }: { items: FeedbackItem[] }) {
  if (items.length === 0) {
    return <div className="card empty">no feedback.json yet</div>;
  }
  const sorted = [...items].sort((a, b) => b.date.localeCompare(a.date));
  return (
    <div className="card" style={{ overflow: "hidden" }}>
      {sorted.map((f) => (
        <div key={f.id} className="row" style={{ alignItems: "flex-start" }}>
          <span className={TAG_PILL[f.tag]}>{f.tag}</span>
          <span style={{ minWidth: 0, flex: 1 }}>
            <span
              className="row-title"
              style={{ display: "block", fontWeight: 500 }}
            >
              &ldquo;{f.quote}&rdquo;
            </span>
            {f.note ? (
              <span className="row-detail" style={{ display: "block", marginTop: 4 }}>
                — {f.note}
              </span>
            ) : null}
          </span>
          <span className="row-meta">
            <span style={{ display: "block" }}>{f.cohort}</span>
            <span className="kv-mono" style={{ display: "block", opacity: 0.7 }}>
              {f.date}
            </span>
          </span>
        </div>
      ))}
    </div>
  );
}
