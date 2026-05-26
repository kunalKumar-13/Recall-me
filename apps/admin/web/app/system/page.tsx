import { loadSystemSnapshot } from "../../lib/loaders";
import { SystemPanel } from "../../components/panels/SystemPanel";
import { CopyDiagnostics } from "../../components/CopyDiagnostics";

export const dynamic = "force-dynamic";

/**
 * `/system` — System Console.
 *
 * Phase 6H built the filesystem-derived checks; Phase 6J adds a
 * *copy diagnostics* button that hands the founder a single
 * markdown blob to paste into a bug report (handles, mtimes, the
 * doctor verdicts, no PII).
 */
export default async function SystemPage() {
  const snapshot = await loadSystemSnapshot();
  // Build a redacted diagnostics blob — no URLs, no filenames from
  // the user's actual events, no chat content. The directive's
  // trust-ledger contract applies here too.
  const diagnostics = [
    `# Recall — System diagnostics`,
    `_generated ${snapshot.generated_at}_`,
    ``,
    `**~/.recall path** \`${snapshot.recall_home}\` _exists_ ${snapshot.recall_home_exists ? "yes" : "no"}`,
    ``,
    `## Checks`,
    ``,
    ...snapshot.checks.map((c) =>
      `- **${c.label}** \`${c.state.toUpperCase()}\` — ${c.detail}`,
    ),
    ``,
    `## Trust contract`,
    `- counts only · no URLs · no filenames · no queries · no chat content`,
    `- generated locally · never uploaded · share at your own discretion`,
  ].join("\n");

  return (
    <div className="page">
      <header className="page-header">
        <div>
          <h1 className="page-title">System</h1>
          <div className="page-subtitle">
            live read from <code>{snapshot.recall_home}</code>
          </div>
        </div>
        <CopyDiagnostics blob={diagnostics} />
      </header>
      <section className="section">
        <SystemPanel snapshot={snapshot} />
      </section>
      <section className="section">
        <div className="section-header">
          <span className="section-title">Diagnostics preview</span>
          <span className="section-aside">— exactly what the copy button puts on your clipboard</span>
        </div>
        <pre style={{
          padding: 14,
          background: "var(--surface)",
          border: "1px solid var(--line)",
          borderRadius: 12,
          fontSize: 11.5,
          fontFamily: "ui-monospace, SFMono-Regular, Menlo, Consolas, monospace",
          color: "var(--ink-2)",
          overflow: "auto",
        }}>{diagnostics}</pre>
      </section>
    </div>
  );
}
