import { DEMO_FILE, CONFIG_FILE } from "../../lib/loaders/paths";
import { fileMtime, readJSON } from "../../lib/loaders/fsx";
import { loadAlpha, loadDailyLoop } from "../../lib/loaders";
import { VerdictPill } from "../../components/panels/Verdict";

export const dynamic = "force-dynamic";

/**
 * `/experiments` — the Phase 6J Product Lab.
 *
 * Reads the live state of every feature flag / opt-in the founder
 * has any visibility into:
 *
 *   - demo overlay state         ~/.recall/demo.json
 *   - alpha gates                alpha cohort signals (loadAlpha)
 *   - daily-loop flag            $env:RECALL_DAILY_LOOP (best-effort)
 *   - episodic capture flag      `episodic_enabled` in config.json
 *   - browser-ingest flag        `browser_ingest_enabled` in config.json
 *   - resurfacing flag           `resurfacing_enabled` in config.json
 *   - threads flag               `threads_enabled` in config.json
 *
 * Every row carries the *flip command* in a clipboard chip — the
 * dashboard never mutates the flag itself (same *no server endpoint*
 * rule as the rest of the room).
 */
export default async function ExperimentsPage() {
  const [demo, config, alpha, daily] = await Promise.all([
    readJSON<Record<string, unknown>>(DEMO_FILE, {}),
    readJSON<Record<string, unknown>>(CONFIG_FILE, {}),
    loadAlpha(),
    loadDailyLoop(7),
  ]);
  const demoMtime = await fileMtime(DEMO_FILE);

  const demoState = String(demo.state || "available");
  const dailyLoopOff = (process.env.RECALL_DAILY_LOOP || "on").toLowerCase() === "off";

  const flags: { label: string; value: string; verdict: "green" | "yellow" | "red" | "mute"; detail: string; flip: string }[] = [
    {
      label: "demo overlay",
      value: demoState,
      verdict: demoState === "active" ? "yellow" : "green",
      detail: demoMtime ? `last changed ${new Date(demoMtime).toLocaleString()}` : "default `available`",
      flip: 'curl -s -X POST http://127.0.0.1:4545/v1/demo/dismiss',
    },
    {
      label: "episodic capture",
      value: config.episodic_enabled === false ? "off" : "on",
      verdict: config.episodic_enabled === false ? "red" : "green",
      detail: `~/.recall/config.json · episodic_enabled`,
      flip: "Edit ~/.recall/config.json: episodic_enabled",
    },
    {
      label: "browser ingest",
      value: config.browser_ingest_enabled === false ? "off" : "on",
      verdict: config.browser_ingest_enabled === false ? "red" : "green",
      detail: `loopback port 4545 · ~/.recall/config.json`,
      flip: "Edit ~/.recall/config.json: browser_ingest_enabled",
    },
    {
      label: "resurfacing",
      value: config.resurfacing_enabled === false ? "off" : "on",
      verdict: config.resurfacing_enabled === false ? "yellow" : "green",
      detail: "passive 'on your radar' surface",
      flip: "Edit ~/.recall/config.json: resurfacing_enabled",
    },
    {
      label: "threads",
      value: config.threads_enabled === false ? "off" : "on",
      verdict: config.threads_enabled === false ? "yellow" : "green",
      detail: "persistent topic identity",
      flip: "Edit ~/.recall/config.json: threads_enabled",
    },
    {
      label: "daily loop layer",
      value: dailyLoopOff ? "off" : "on",
      verdict: dailyLoopOff ? "yellow" : "green",
      detail: "$env:RECALL_DAILY_LOOP",
      flip: '$env:RECALL_DAILY_LOOP="on"',
    },
    {
      label: "evolution",
      value: config.evolution_enabled === false ? "off" : "on",
      verdict: config.evolution_enabled === false ? "yellow" : "green",
      detail: "thread phase reconstruction",
      flip: "Edit ~/.recall/config.json: evolution_enabled",
    },
    {
      label: "recovery",
      value: config.recovery_enabled === false ? "off" : "on",
      verdict: config.recovery_enabled === false ? "red" : "green",
      detail: "the entire continuity surface",
      flip: "Edit ~/.recall/config.json: recovery_enabled",
    },
  ];

  return (
    <div className="page">
      <header className="page-header">
        <div>
          <h1 className="page-title">Experiments</h1>
          <div className="page-subtitle">
            feature flags · demo mode · alpha gates
          </div>
        </div>
      </header>

      <section className="section">
        <div className="section-header">
          <span className="section-title">Feature flags</span>
          <span className="section-aside">— live read · clipboard flip</span>
        </div>
        <div className="card" style={{ overflow: "hidden" }}>
          {flags.map((f) => (
            <div key={f.label} className="panel-row">
              <span className="panel-row-label">{f.label}</span>
              <span className="panel-row-detail">
                {f.detail}{" "}
                · <code style={{ fontSize: 11 }}>{f.flip}</code>
              </span>
              <span style={{ display: "inline-flex", gap: 4 }}>
                <span className="tag">{f.value}</span>
                <VerdictPill value={f.verdict} />
              </span>
            </div>
          ))}
        </div>
      </section>

      <section className="section">
        <div className="section-header">
          <span className="section-title">Alpha gates</span>
          <span className="section-aside">— directive numbers · alpha-001</span>
        </div>
        <div className="grid grid-4">
          <Gate label="5 humans" actual={alpha.installs} target={5} />
          <Gate label="3 recoveries" actual={alpha.recoveries} target={3} />
          <Gate label="1 wow" actual={alpha.testers.filter((t) => t.wow_moment).length} target={1} />
          <Gate label="1 failure story" actual={Object.values(alpha.drop_reasons).reduce((a, b) => a + b, 0) + alpha.install_fails} target={1} />
        </div>
      </section>

      <section className="section">
        <div className="section-header">
          <span className="section-title">Trust + daily-loop experiments</span>
          <span className="section-aside">— GREEN floor thresholds</span>
        </div>
        <div className="grid grid-3">
          <ThresholdCard
            label="continuity restored"
            actual={daily.signals.continuity_restored}
            green={60} yellow={25}
          />
          <ThresholdCard
            label="return rate"
            actual={daily.signals.return_rate}
            green={30} yellow={10}
          />
          <ThresholdCard
            label="resume quality"
            actual={daily.signals.resume_quality}
            green={80} yellow={50}
          />
        </div>
      </section>
    </div>
  );
}

function Gate({ label, actual, target }: { label: string; actual: number; target: number }) {
  const v = actual >= target ? "green" : actual >= 1 ? "yellow" : "red";
  return (
    <div className="card" style={{ padding: 12 }}>
      <div className="section-title" style={{ marginBottom: 0 }}>{label}</div>
      <div style={{ marginTop: 6, fontSize: 24, fontWeight: 600 }}>
        {actual} <span style={{ fontSize: 12, color: "var(--ink-3)" }}>/ {target}</span>
      </div>
      <div style={{ marginTop: 4 }}><VerdictPill value={v} /></div>
    </div>
  );
}

function ThresholdCard({
  label, actual, green, yellow,
}: {
  label: string;
  actual: number | null;
  green: number;
  yellow: number;
}) {
  const v: "green" | "yellow" | "red" | "mute" =
    actual === null ? "mute"
    : actual >= green ? "green"
    : actual >= yellow ? "yellow"
    : "red";
  return (
    <div className="card" style={{ padding: 14 }}>
      <div className="section-title" style={{ marginBottom: 0 }}>{label}</div>
      <div style={{ marginTop: 6, fontSize: 22, fontWeight: 600 }}>
        {actual === null ? "—" : `${actual}%`}
      </div>
      <div style={{ marginTop: 4, fontSize: 11, color: "var(--ink-3)" }}>
        green ≥ {green}% · yellow ≥ {yellow}%
      </div>
      <div style={{ marginTop: 6 }}><VerdictPill value={v} /></div>
    </div>
  );
}
