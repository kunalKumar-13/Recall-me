import type { CohortCard } from "../lib/types";

const DOT: Record<CohortCard["health"], string> = {
  green: "dot dot-green",
  yellow: "dot dot-yellow",
  red: "dot dot-red",
  mute: "dot dot-mute",
};

const STATUS_PILL: Record<CohortCard["status"], string> = {
  forming: "pill pill-accent",
  active: "pill pill-green",
  planned: "pill pill-mute",
  paused: "pill pill-yellow",
};

export function AlphaCohorts({ cohorts }: { cohorts: CohortCard[] }) {
  if (cohorts.length === 0) {
    return <div className="card empty">no cohorts.json yet</div>;
  }
  return (
    <div className="grid grid-3">
      {cohorts.map((c) => {
        const returnPct = c.devices > 0
          ? Math.round((c.returning / c.devices) * 100)
          : null;
        return (
          <div key={c.id} className="card health">
            <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
              <span className={DOT[c.health]} />
              <span className="health-label" style={{ letterSpacing: 0.5 }}>
                {c.id}
              </span>
              <span style={{ marginLeft: "auto" }} className={STATUS_PILL[c.status]}>
                {c.status}
              </span>
            </div>
            <div style={{ marginTop: 8, fontSize: 13, fontWeight: 600 }}>
              {c.label}
            </div>
            <div style={{ display: "flex", gap: 16, marginTop: 10 }}>
              <Stat label="devices"   value={c.devices} />
              <Stat label="returning" value={
                returnPct !== null ? `${c.returning} (${returnPct}%)` : "—"
              } />
              <Stat label="feedback"  value={c.feedback_count} />
            </div>
            {c.notes ? (
              <div className="health-foot" style={{ marginTop: 8 }}>{c.notes}</div>
            ) : null}
          </div>
        );
      })}
    </div>
  );
}

function Stat({ label, value }: { label: string; value: number | string }) {
  return (
    <div>
      <div className="health-label" style={{ fontSize: 9.5 }}>{label}</div>
      <div style={{ fontSize: 15, fontWeight: 600, marginTop: 2 }}>{value}</div>
    </div>
  );
}
