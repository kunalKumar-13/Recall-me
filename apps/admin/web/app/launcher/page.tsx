import path from "node:path";
import { LAUNCHER_V3_DIR, SCREENSHOTS_DIR } from "../../lib/loaders/paths";
import { exists, fileMtime, listDir } from "../../lib/loaders/fsx";
import { PanelMeta } from "../../components/panels/HealthPanel";
import { VerdictPill } from "../../components/panels/Verdict";

export const dynamic = "force-dynamic";

/**
 * `/launcher` — launcher v2 vs v3 surface comparison + promotion
 * checklist.
 *
 * Reads:
 *   - `assets/screenshots/launcher-v2/` (Phase 6B)
 *   - `assets/screenshots/launcher-v3/` (Phase 6I)
 *   - `app/ui/launcher_v3/` (the v3 package — used to confirm it's
 *      on disk)
 *
 * Renders three sections: a v3 gallery, a v3-vs-v2 diff strip (side
 * by side), and a promotion checklist (the deferred wire-in items
 * from PHASE_6I_STATUS.md).
 */
export default async function LauncherPage() {
  const v3Exists = await exists(LAUNCHER_V3_DIR);
  const v3Dir = path.join(SCREENSHOTS_DIR, "launcher-v3");
  const v2Dir = path.join(SCREENSHOTS_DIR, "launcher-v2");
  const v3Files = (await listDir(v3Dir)).filter((f) => f.endsWith(".png"));
  const v2Files = (await listDir(v2Dir)).filter((f) => f.endsWith(".png"));
  const [v3Mtime, v2Mtime] = await Promise.all([fileMtime(v3Dir), fileMtime(v2Dir)]);

  // Build the diff pairs by best-effort name match: digest↔launcher-digest,
  // empty↔launcher-empty, etc.
  const DIFF = [
    { v3: "digest.png", v2: "launcher-digest.png", label: "Digest" },
    { v3: "empty.png",  v2: "launcher-empty.png",  label: "Empty"  },
    { v3: "continue.png", v2: "recovery-card.png", label: "Continue / Recovery card" },
    { v3: "focused.png",  v2: "recovery-card-focused.png", label: "Focused recovery" },
  ];

  const promotion: { label: string; state: "green" | "yellow" | "red"; detail: string }[] = [
    {
      label: "v3 package present",
      state: v3Exists ? "green" : "red",
      detail: v3Exists ? "app/ui/launcher_v3/ on disk" : "missing — run Phase 6I",
    },
    {
      label: "v3 captures present",
      state: v3Files.length >= 5 ? "green" : "yellow",
      detail: `${v3Files.length} / 5 PNGs in launcher-v3/`,
    },
    {
      label: "v2 captures present (baseline)",
      state: v2Files.length >= 5 ? "green" : "yellow",
      detail: `${v2Files.length} / 5+ PNGs in launcher-v2/`,
    },
    {
      label: "Live launcher untouched",
      state: "green",
      detail: "app/ui/launcher.py still owns Launcher",
    },
    {
      label: "Wire-in pending",
      state: "yellow",
      detail: "follow-up phase — swap empty_widget + digest_panel onto v3 widget tree",
    },
    {
      label: "QA matrix for live wire-in",
      state: "yellow",
      detail: "all 4 launcher states (empty/digest/results/demo) need a v3 capture diff",
    },
  ];

  return (
    <div className="page">
      <header className="page-header">
        <div>
          <h1 className="page-title">Launcher</h1>
          <div className="page-subtitle">
            v3 captures · v2 baseline · promotion checklist
          </div>
        </div>
      </header>

      <section className="section">
        <PanelMeta
          title="v3 gallery"
          live={path.join(SCREENSHOTS_DIR, "launcher-v3")}
          mtime={v3Mtime}
          extra={`${v3Files.length} capture(s)`}
        />
        {v3Files.length === 0 ? (
          <div className="card empty-note">
            No v3 captures yet. Run{" "}
            <code>python infra/scripts/capture/capture_launcher_v3.py</code>.
          </div>
        ) : (
          <div className="grid grid-2">
            {v3Files.map((f) => (
              <figure key={f} className="card" style={{ overflow: "hidden" }}>
                {/* eslint-disable-next-line @next/next/no-img-element */}
                <img
                  src={`/screens/launcher-v3/${f}`}
                  alt={f}
                  loading="lazy"
                  style={{ width: "100%", height: "auto", display: "block" }}
                />
                <figcaption className="panel-row" style={{ borderTop: "1px solid var(--line)" }}>
                  <span className="panel-row-label" style={{ fontFamily: "ui-monospace, monospace" }}>{f}</span>
                  <span className="panel-row-detail" />
                  <span className="tag">v3</span>
                </figcaption>
              </figure>
            ))}
          </div>
        )}
      </section>

      <section className="section">
        <PanelMeta
          title="v3 vs v2"
          live="diff strip · best-effort name match"
          mtime={v2Mtime}
        />
        <div className="grid grid-2" style={{ gap: 24 }}>
          {DIFF.map((d) => (
            <div key={d.label} className="card" style={{ overflow: "hidden" }}>
              <div className="panel-row" style={{ background: "var(--surface-sunken)" }}>
                <span className="panel-row-label">{d.label}</span>
                <span className="panel-row-detail" />
                <span className="tag">diff</span>
              </div>
              <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 0 }}>
                <DiffSide src={`/screens/launcher-v3/${d.v3}`} label={`v3 · ${d.v3}`} />
                <DiffSide src={`/screens/launcher-v2/${d.v2}`} label={`v2 · ${d.v2}`} />
              </div>
            </div>
          ))}
        </div>
      </section>

      <section className="section">
        <div className="section-header">
          <span className="section-title">Promotion checklist</span>
          <span className="section-aside">— what blocks the live wire-in</span>
        </div>
        <div className="card" style={{ overflow: "hidden" }}>
          {promotion.map((p) => (
            <div key={p.label} className="panel-row">
              <span className="panel-row-label">{p.label}</span>
              <span className="panel-row-detail">{p.detail}</span>
              <VerdictPill value={p.state} />
            </div>
          ))}
        </div>
      </section>
    </div>
  );
}

function DiffSide({ src, label }: { src: string; label: string }) {
  return (
    <div style={{ borderLeft: "1px solid var(--line)" }}>
      {/* eslint-disable-next-line @next/next/no-img-element */}
      <img src={src} alt={label} loading="lazy"
           style={{ width: "100%", height: "auto", display: "block", background: "var(--surface-sunken)" }} />
      <div style={{
        padding: "6px 10px", borderTop: "1px solid var(--line)",
        fontSize: 10.5, color: "var(--ink-3)",
        fontFamily: "ui-monospace, SFMono-Regular, Menlo, Consolas, monospace",
      }}>{label}</div>
    </div>
  );
}
