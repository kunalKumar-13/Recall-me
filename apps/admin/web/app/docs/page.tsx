export const dynamic = "force-dynamic";

/**
 * `/docs` — a static index of the canonical docs the founder reaches
 * for from the control room. Every link is a `docs/` path the
 * dashboard does not host itself; it is a *map*, not a viewer.
 */
const DOCS = [
  {
    group: "product",
    rows: [
      ["docs/product/TRUST.md", "Public trust statement"],
      ["docs/product/DAILY_LOOP.md", "Daily loop — six bins, three signals"],
      ["docs/product/RETURN_BEHAVIOR.md", "Return detector semantics"],
      ["docs/product/CONTINUITY_LANGUAGE.md", "Canonical vocabulary"],
      ["docs/product/SURFACE_MAP.md", "One job per surface"],
      ["docs/product/MOTION.md", "Cross-surface motion contract"],
      ["docs/product/FIRST_MAGIC.md", "Demo overlay story"],
    ],
  },
  {
    group: "alpha",
    rows: [
      ["docs/alpha/PLAYBOOK.md", "Cohort operations playbook"],
      ["docs/alpha/STATUS.md", "Live cohort board"],
      ["docs/alpha/KNOWN_FAILURES.md", "Failure catalogue"],
      ["docs/alpha/MOMENTS.md", "Seven first-time moments per tester"],
    ],
  },
  {
    group: "release",
    rows: [
      ["docs/release/RELEASE.md", "Release ladder"],
      ["docs/release/DOWNLOAD_GUIDE.md", "Alpha download paths"],
      ["docs/release/DEMO_VIDEO_SCRIPT.md", "60-second demo storyboard"],
      ["docs/release/MAC_OWNER_NEEDED.md", "Mac maintainer note"],
      ["docs/release/CHANGELOG.md", "Changelog"],
    ],
  },
  {
    group: "engineering",
    rows: [
      ["docs/engineering/PHASE_6H_STATUS.md", "Phase 6H — Control Room OS receipt"],
      ["docs/engineering/PHASE_6G_STATUS.md", "Phase 6G — Public Alpha Surface"],
      ["docs/engineering/PHASE_6F_STATUS.md", "Phase 6F — Daily Loop Validation"],
      ["docs/engineering/PHASE_6E_STATUS.md", "Phase 6E — Alpha Reality"],
      ["docs/engineering/TRUST_LEDGER.md", "Trust boundary spec"],
      ["docs/engineering/PERF.md", "Performance budgets"],
      ["docs/engineering/STABILITY.md", "Failure philosophy"],
      ["docs/engineering/AUDIT_REPORT.md", "Standing engineering debt"],
    ],
  },
  {
    group: "founder",
    rows: [
      ["docs/founder/PHASE_TRACKER.md", "Where the build is"],
      ["docs/founder/ROADMAP_LIVE.md", "Now / next / later / never"],
      ["docs/founder/PUBLIC_ALPHA.md", "Public-alpha readiness"],
      ["docs/founder/FOUNDER_OPERATIONS.md", "Daily founder runbook"],
    ],
  },
] as const;

export default function DocsPage() {
  return (
    <div className="page">
      <header className="page-header">
        <div>
          <h1 className="page-title">Docs</h1>
          <div className="page-subtitle">
            map of the canonical docs · opens locally in your editor
          </div>
        </div>
      </header>

      {DOCS.map(({ group, rows }) => (
        <section key={group} className="section">
          <div className="section-header">
            <span className="section-title">{group}</span>
          </div>
          <div className="card" style={{ overflow: "hidden" }}>
            {rows.map(([path, label]) => (
              <div key={path} className="panel-row">
                <span className="panel-row-label">{label}</span>
                <span className="panel-row-detail">
                  <code>{path}</code>
                </span>
                <span className="tag">md</span>
              </div>
            ))}
          </div>
        </section>
      ))}
    </div>
  );
}
