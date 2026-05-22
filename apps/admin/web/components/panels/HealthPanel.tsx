import { HealthOverview } from "../HealthOverview";
import type { HealthSnapshot } from "../../lib/loaders";

/**
 * HealthPanel — wraps the existing `HealthOverview` cards with a
 * thin "live" header that names the data source + freshness.
 * Every card value is read by `loadHealthSnapshot()`; nothing is
 * hardcoded in this file.
 */
export function HealthPanel({ snapshot }: { snapshot: HealthSnapshot }) {
  return (
    <div>
      <PanelMeta
        title="Engine health"
        live="apps/admin/data/health.json"
        mtime={snapshot.baked_mtime}
        extra={
          snapshot.live.recall_home_exists
            ? `~/.recall present · ${snapshot.live.events_files} day-files`
            : "~/.recall not created yet"
        }
      />
      {snapshot.baked.length === 0 ? (
        <div className="card empty-note">
          No baked health.json yet — run <code>recall founder bake</code>.
        </div>
      ) : (
        <HealthOverview cards={snapshot.baked} />
      )}
    </div>
  );
}

export function PanelMeta({
  title,
  live,
  mtime,
  extra,
}: {
  title: string;
  live: string;
  mtime: string | null;
  extra?: string;
}) {
  return (
    <div className="section-header">
      <span className="section-title">{title}</span>
      <span className="section-aside">
        — derived from <code>{live}</code>
        {mtime ? <> · updated {new Date(mtime).toLocaleString()}</> : null}
        {extra ? <> · {extra}</> : null}
      </span>
    </div>
  );
}
