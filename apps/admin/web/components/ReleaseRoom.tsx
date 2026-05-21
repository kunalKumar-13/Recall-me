import type { ReleaseStatus } from "../lib/types";

const PILL: Record<string, string> = {
  GO: "pill pill-green",
  PARTIAL: "pill pill-yellow",
  "NO-GO": "pill pill-red",
  ready: "pill pill-green",
  partial: "pill pill-yellow",
  blocked: "pill pill-red",
  supported: "pill pill-green",
  preview: "pill pill-yellow",
  "source-only": "pill pill-mute",
  signed: "pill pill-green",
  unsigned: "pill pill-yellow",
  complete: "pill pill-green",
  missing: "pill pill-red",
};

export function ReleaseRoom({ release }: { release: ReleaseStatus | null }) {
  if (!release) {
    return <div className="card empty">no release.json yet</div>;
  }
  return (
    <div className="grid grid-2">
      <div className="card">
        <div className="kv">
          <span className="kv-k">Current version</span>
          <span className="kv-v kv-mono">{release.current_version}</span>
        </div>
        <div className="kv">
          <span className="kv-k">Next milestone</span>
          <span className="kv-v">{release.next_milestone}</span>
        </div>
        <div className="kv">
          <span className="kv-k">GO / NO-GO</span>
          <span className={PILL[release.go_no_go] ?? "pill pill-mute"}>
            {release.go_no_go}
          </span>
        </div>
        <div className="kv">
          <span className="kv-k">Installer</span>
          <span className={PILL[release.installer] ?? "pill pill-mute"}>
            {release.installer}
          </span>
        </div>
        <div className="kv">
          <span className="kv-k">macOS</span>
          <span className={PILL[release.mac] ?? "pill pill-mute"}>
            {release.mac}
          </span>
        </div>
        <div className="kv">
          <span className="kv-k">Code signing</span>
          <span className={PILL[release.signing] ?? "pill pill-mute"}>
            {release.signing}
          </span>
        </div>
        <div className="kv">
          <span className="kv-k">Screenshots</span>
          <span className={PILL[release.screenshots] ?? "pill pill-mute"}>
            {release.screenshots}
          </span>
        </div>
      </div>
      <div className="card">
        <div style={{ padding: "12px 14px 8px" }}>
          <div className="health-label">Blocked items</div>
        </div>
        {release.blocked.length === 0 ? (
          <div className="row">
            <div className="row-detail">no blockers — ready to tag</div>
          </div>
        ) : (
          release.blocked.map((b, i) => (
            <div key={i} className="row">
              <span className="dot dot-red" />
              <span className="row-title" style={{ fontSize: 12.5, fontWeight: 500 }}>
                {b}
              </span>
            </div>
          ))
        )}
      </div>
    </div>
  );
}
