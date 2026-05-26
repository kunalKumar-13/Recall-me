import { loadDesktop } from "../../lib/loaders";
import { VerdictPill } from "../../components/panels/Verdict";
import { PanelMeta } from "../../components/panels/HealthPanel";

export const dynamic = "force-dynamic";

/**
 * `/desktop` — Phase 6M founder view of the desktop memory layer.
 *
 * Reads `~/.recall/events/YYYY-MM-DD.jsonl` directly (last 7 days),
 * filters for `kind == "desktop_window"`, and aggregates per app.
 * Renders the directive's four signals:
 *
 *   - apps        (unique exe names in the window)
 *   - focus       (total focus seconds across all apps)
 *   - top tools   (per-app row sorted by focus time)
 *   - session time (longest single focus block per app)
 *
 * No screenshots. No content beyond the window titles the OS
 * already exposed.
 */
export default async function DesktopPage() {
  const snapshot = await loadDesktop(7);
  const hours = Math.floor(snapshot.total_seconds / 3600);
  const minutes = Math.round((snapshot.total_seconds % 3600) / 60);

  return (
    <div className="page">
      <header className="page-header">
        <div>
          <h1 className="page-title">Desktop</h1>
          <div className="page-subtitle">
            live read from <code>{snapshot.events_dir}</code> · last {snapshot.window_days} days
          </div>
        </div>
      </header>

      <section className="section">
        <PanelMeta
          title="Today"
          live="~/.recall/events/*.jsonl · desktop_window"
          mtime={snapshot.events_dir_mtime}
          extra={snapshot.total_events ? `${snapshot.total_events} focus blocks` : "no desktop activity yet"}
        />
        <div className="grid grid-4">
          <Stat label="apps" value={String(snapshot.unique_apps)} verdict={snapshot.unique_apps ? "green" : "mute"} />
          <Stat label="focus" value={`${hours}h ${minutes}m`} verdict={snapshot.total_seconds > 0 ? "green" : "mute"} />
          <Stat label="blocks" value={String(snapshot.total_events)} verdict={snapshot.total_events ? "green" : "mute"} />
          <Stat
            label="longest"
            value={snapshot.apps[0] ? _fmtMinutes(snapshot.apps[0].longest_seconds) : "—"}
            verdict={snapshot.apps[0] ? "green" : "mute"}
            hint={snapshot.apps[0]?.app}
          />
        </div>
      </section>

      <section className="section">
        <div className="section-header">
          <span className="section-title">Top tools</span>
          <span className="section-aside">
            — per-app · focus time / blocks / switches
          </span>
        </div>
        {snapshot.apps.length === 0 ? (
          <div className="card empty-note">
            No <code>desktop_window</code> events yet. Start the watcher with{" "}
            <code>start_watcher(event_logger)</code> or set{" "}
            <code>RECALL_DESKTOP=on</code> + opt-in via{" "}
            <code>desktop_capture_enabled</code> in <code>~/.recall/config.json</code>.
          </div>
        ) : (
          <div className="card" style={{ overflow: "hidden" }}>
            {snapshot.apps.map((a) => (
              <div key={a.app} className="panel-row">
                <span className="panel-row-label" style={{ fontFamily: "ui-monospace, monospace" }}>
                  {a.app}
                </span>
                <span className="panel-row-detail">
                  {_fmtMinutes(a.total_seconds)} · {a.events} block(s) · {a.switch_count} switch(es)
                  {a.titles_sampled.length > 0 && (
                    <> · <span style={{ color: "var(--ink-4)" }}>{a.titles_sampled[0]}</span></>
                  )}
                </span>
                <span className="tag">{_fmtMinutes(a.longest_seconds)}</span>
              </div>
            ))}
          </div>
        )}
      </section>

      <section className="section">
        <div className="section-header">
          <span className="section-title">Session log</span>
          <span className="section-aside">
            — newest first · last {snapshot.events.length} block(s)
          </span>
        </div>
        {snapshot.events.length === 0 ? (
          <div className="card empty-note">
            No focus blocks captured in the window.
          </div>
        ) : (
          <div className="card" style={{ overflow: "auto", maxHeight: "60vh" }}>
            {snapshot.events
              .slice()
              .sort((a, b) => (b.focus_start || "").localeCompare(a.focus_start || ""))
              .slice(0, 100)
              .map((e, i) => (
                <div key={`${e.focus_start}-${i}`} className="panel-row">
                  <span className="panel-row-label" style={{ fontFamily: "ui-monospace, monospace" }}>
                    {(e.focus_start || "").replace("T", " ").replace("Z", "")}
                  </span>
                  <span className="panel-row-detail">
                    <span style={{ color: "var(--ink-3)" }}>{e.app}</span>
                    <> · </>{e.title}
                    {e.path && (
                      <> · <span style={{ color: "var(--ink-4)" }}>{e.path}</span></>
                    )}
                  </span>
                  <span className="tag">{_fmtMinutes(e.duration)}</span>
                </div>
              ))}
          </div>
        )}
      </section>

      <section className="section">
        <div className="card" style={{ padding: 14 }}>
          <div className="section-title" style={{ marginBottom: 6 }}>Privacy</div>
          <div style={{ fontSize: 12.5, color: "var(--ink-3)", lineHeight: 1.6 }}>
            Metadata only — app · title · focus duration · switch count · optional path.
            <br />
            No screenshots · no OCR · no audio · no clipboard read.
            Disable with <code>RECALL_DESKTOP=off</code> in the environment, or remove
            the layer entirely by deleting <code>app/core/desktop/</code>.
          </div>
        </div>
      </section>
    </div>
  );
}


function _fmtMinutes(seconds: number): string {
  if (seconds < 60) return `${seconds}s`;
  const m = Math.floor(seconds / 60);
  const s = seconds % 60;
  if (m < 60) return s ? `${m}m ${s}s` : `${m}m`;
  const h = Math.floor(m / 60);
  const rm = m % 60;
  return rm ? `${h}h ${rm}m` : `${h}h`;
}


function Stat({
  label, value, verdict, hint,
}: {
  label: string;
  value: string;
  verdict: "green" | "yellow" | "red" | "mute";
  hint?: string;
}) {
  return (
    <div className="card" style={{ padding: 14 }}>
      <div className="section-title" style={{ marginBottom: 0 }}>{label}</div>
      <div style={{ marginTop: 6, fontSize: 22, fontWeight: 600 }}>{value}</div>
      {hint && <div style={{ marginTop: 2, fontSize: 11, color: "var(--ink-3)" }}>{hint}</div>}
      <div style={{ marginTop: 6 }}><VerdictPill value={verdict} /></div>
    </div>
  );
}
