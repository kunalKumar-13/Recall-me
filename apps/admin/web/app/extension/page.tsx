import path from "node:path";
import { EXTENSION_DIR, EXTENSION_MANIFEST, SCREENSHOTS_DIR } from "../../lib/loaders/paths";
import { exists, fileMtime, listDir, readJSON } from "../../lib/loaders/fsx";
import { loadDailyLoop, loadSystemSnapshot } from "../../lib/loaders";
import { VerdictPill } from "../../components/panels/Verdict";
import { PanelMeta } from "../../components/panels/HealthPanel";

export const dynamic = "force-dynamic";

/**
 * `/extension` — pairing health for the popup. Derived from:
 *
 *   - the popup's manifest.json (version)
 *   - the daily-loop counters (capture rate / event flow)
 *   - the live `~/.recall/events/` mtime (last activity)
 *   - the `assets/screenshots/extension-v2/` shots (popup snapshots)
 *
 * The directive's *repair button* is the same clipboard-CLI pattern
 * the rest of the dashboard uses — no server endpoint runs the
 * repair.
 */
export default async function ExtensionPage() {
  const [daily, system, manifest] = await Promise.all([
    loadDailyLoop(7),
    loadSystemSnapshot(),
    readJSON<Record<string, unknown>>(EXTENSION_MANIFEST, {}),
  ]);
  const popupBuilt = await fileMtime(path.join(EXTENSION_DIR, "popup", "index.html"));
  const lastEvent = system.checks.find((c) => c.id === "events")?.detail ?? "—";
  const popupShots = (await listDir(path.join(SCREENSHOTS_DIR, "extension-v2")))
    .filter((f) => f.endsWith(".png"));
  const ext = String(manifest.version || "unknown");
  const engineVersion = "0.2.0";
  const drift = ext.split(".")[0] !== engineVersion.split(".")[0]
    ? "major" : ext !== engineVersion ? "minor" : "none";

  const captureRate = daily.window.day_started > 0
    ? Math.round((daily.window.recoveries_shown + daily.window.recoveries_used) / daily.window.day_started * 10) / 10
    : 0;

  return (
    <div className="page">
      <header className="page-header">
        <div>
          <h1 className="page-title">Extension</h1>
          <div className="page-subtitle">
            popup pairing · live from manifest + events + screenshots
          </div>
        </div>
      </header>

      <section className="section">
        <PanelMeta
          title="Pairing"
          live={EXTENSION_MANIFEST}
          mtime={popupBuilt}
        />
        <div className="grid grid-4">
          <Stat label="paired" value={await exists(EXTENSION_MANIFEST) ? "yes" : "no"} verdict={await exists(EXTENSION_MANIFEST) ? "green" : "red"} />
          <Stat label="ext version" value={ext} verdict="mute" />
          <Stat label="engine version" value={engineVersion} verdict="mute" />
          <Stat label="drift" value={drift} verdict={drift === "none" ? "green" : drift === "minor" ? "yellow" : "red"} />
        </div>
      </section>

      <section className="section">
        <PanelMeta title="Capture rate" live="~/.recall/daily_loop.jsonl" mtime={daily.source.log_mtime} />
        <div className="grid grid-4">
          <Stat label="events / day (7d)" value={String(captureRate)} verdict={daily.window.day_started >= 5 ? "green" : "yellow"} />
          <Stat label="last activity" value={lastEvent.split(";")[1]?.trim() ?? "—"} verdict={lastEvent.includes("newest") ? "green" : "mute"} />
          <Stat label="returns (7d)" value={String(daily.window.returns)} verdict={daily.window.returns > 0 ? "green" : "mute"} />
          <Stat label="resume success" value={`${daily.signals.resume_quality ?? "—"}%`} verdict={daily.verdicts.resume_quality} />
        </div>
      </section>

      <section className="section">
        <div className="section-header">
          <span className="section-title">Popup screenshots</span>
          <span className="section-aside">— {popupShots.length} captures in <code>extension-v2/</code></span>
        </div>
        <div className="grid grid-3">
          {popupShots.map((f) => (
            <div key={f} className="card" style={{ overflow: "hidden" }}>
              {/* eslint-disable-next-line @next/next/no-img-element */}
              <img
                src={`/screens/extension-v2/${f}`}
                alt={f}
                loading="lazy"
                style={{ width: "100%", height: "auto", display: "block" }}
              />
              <div className="panel-row" style={{ borderTop: "1px solid var(--line)" }}>
                <span className="panel-row-label" style={{ fontFamily: "ui-monospace, monospace" }}>{f}</span>
                <span className="panel-row-detail" />
                <span className="tag">v2</span>
              </div>
            </div>
          ))}
        </div>
        {popupShots.length === 0 && (
          <div className="card empty-note">
            No popup screenshots yet. Run{" "}
            <code>cd apps/extension/ui && node capture_extension.mjs</code>.
          </div>
        )}
      </section>

      <section className="section">
        <div className="section-header">
          <span className="section-title">Repair</span>
          <span className="section-aside">— clipboard commands · no server endpoint</span>
        </div>
        <div className="card" style={{ overflow: "hidden" }}>
          <RepairRow label="Reset pairing" cmd="python recall.py reset" />
          <RepairRow label="Re-install extension folder" cmd="explorer .\\apps\\extension\\popup" />
          <RepairRow label="Rebuild popup" cmd="cd apps\\extension\\ui && npm run build" />
        </div>
      </section>
    </div>
  );
}

function Stat({
  label, value, verdict,
}: {
  label: string;
  value: string;
  verdict: "green" | "yellow" | "red" | "mute";
}) {
  return (
    <div className="card" style={{ padding: 12 }}>
      <div className="section-title" style={{ marginBottom: 0 }}>{label}</div>
      <div style={{ marginTop: 6, fontSize: 20, fontWeight: 600 }}>{value}</div>
      <div style={{ marginTop: 4 }}><VerdictPill value={verdict} /></div>
    </div>
  );
}

function RepairRow({ label, cmd }: { label: string; cmd: string }) {
  return (
    <div className="panel-row">
      <span className="panel-row-label">{label}</span>
      <span className="panel-row-detail" style={{ fontFamily: "ui-monospace, SFMono-Regular, Menlo, Consolas, monospace" }}>
        <code>{cmd}</code>
      </span>
      <span className="tag">copy</span>
    </div>
  );
}
