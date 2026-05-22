import { loadSystemSnapshot } from "../../lib/loaders";
import { SystemPanel } from "../../components/panels/SystemPanel";

export const dynamic = "force-dynamic";

/**
 * `/system` — System Room. What `recall doctor` would report on
 * this machine, derived from the local filesystem.
 */
export default async function SystemPage() {
  const snapshot = await loadSystemSnapshot();
  return (
    <div className="page">
      <header className="page-header">
        <div>
          <h1 className="page-title">System</h1>
          <div className="page-subtitle">
            live read from <code>{snapshot.recall_home}</code>
          </div>
        </div>
      </header>
      <section className="section">
        <SystemPanel snapshot={snapshot} />
      </section>
    </div>
  );
}
