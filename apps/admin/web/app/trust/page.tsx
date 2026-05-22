import { loadTrustSnapshot } from "../../lib/loaders";
import { TrustPanel } from "../../components/panels/TrustPanel";

export const dynamic = "force-dynamic";

/**
 * `/trust` — the recovery-ledger deep-dive. Six outcomes + derived
 * signals + the baked operator cards (when present).
 */
export default async function TrustPage() {
  const snapshot = await loadTrustSnapshot();
  return (
    <div className="page">
      <header className="page-header">
        <div>
          <h1 className="page-title">Trust</h1>
          <div className="page-subtitle">
            live read from <code>alpha/recovery_journal.json</code>
          </div>
        </div>
      </header>
      <section className="section">
        <TrustPanel snapshot={snapshot} />
      </section>
    </div>
  );
}
