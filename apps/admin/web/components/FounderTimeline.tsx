import type { TimelinePhase } from "../lib/types";

const CLASS: Record<TimelinePhase["state"], string> = {
  done: "timeline-step done",
  partial: "timeline-step partial",
  now: "timeline-step now",
  next: "timeline-step next",
};

export function FounderTimeline({ phases }: { phases: TimelinePhase[] }) {
  if (phases.length === 0) {
    return <div className="card empty">no timeline.json yet</div>;
  }
  const done = phases.filter((p) => p.state === "done").length;
  const now = phases.find((p) => p.state === "now");
  const next = phases.find((p) => p.state === "next");
  return (
    <div className="card timeline">
      <div className="timeline-track">
        {phases.map((p) => (
          <div key={p.name} className={CLASS[p.state]}>
            <div className="timeline-step-name">{p.name}</div>
            <div className="timeline-step-meta">{p.label}</div>
            <div className="timeline-step-meta">{p.done_pct}%</div>
          </div>
        ))}
      </div>
      <div
        style={{
          marginTop: 14,
          paddingTop: 12,
          borderTop: "1px solid var(--line)",
          display: "flex",
          gap: 24,
          fontSize: 12,
          color: "var(--ink-3)",
          flexWrap: "wrap",
        }}
      >
        <span>
          <strong style={{ color: "var(--ink)" }}>{done}</strong> phases done
        </span>
        {now ? (
          <span>
            now: <strong style={{ color: "var(--accent)" }}>{now.name}</strong>{" "}
            — {now.label} ({now.done_pct}%)
          </span>
        ) : null}
        {next ? (
          <span>
            next: <strong style={{ color: "var(--ink-2)" }}>{next.name}</strong>{" "}
            — {next.label}
          </span>
        ) : null}
      </div>
    </div>
  );
}
