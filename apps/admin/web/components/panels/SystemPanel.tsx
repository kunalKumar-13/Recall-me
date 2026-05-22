import type { SystemSnapshot } from "../../lib/loaders";
import { PanelMeta } from "./HealthPanel";
import { VerdictPill } from "./Verdict";

/**
 * SystemPanel — what `recall doctor` would report on this same
 * machine, derived from the filesystem.
 *
 * The dashboard runs on the founder's laptop, so every check here
 * is a local read: `~/.recall/` presence, `events/` mtime,
 * `instance.lock` health, `config.json` indexed-folders count,
 * `demo.json` overlay state. No daemon ping; the goal is "what
 * does the disk say right now".
 */
export function SystemPanel({ snapshot }: { snapshot: SystemSnapshot }) {
  return (
    <div>
      <PanelMeta
        title="System"
        live={snapshot.recall_home}
        mtime={snapshot.generated_at}
        extra={snapshot.recall_home_exists ? "~/.recall present" : "no ~/.recall yet"}
      />
      <div className="card" style={{ overflow: "hidden" }}>
        {snapshot.checks.map((c) => (
          <div key={c.id} className="panel-row">
            <span className="panel-row-label">{c.label}</span>
            <span className="panel-row-detail">{c.detail}</span>
            <VerdictPill value={c.state} />
          </div>
        ))}
      </div>
    </div>
  );
}
