import { loadAlpha } from "../../lib/loaders";
import { AlphaPanel } from "../../components/panels/AlphaPanel";

export const dynamic = "force-dynamic";

/**
 * `/alpha` — the cohort deep-dive. Renders the full
 * `AlphaPanel` (non-compact) which adds the per-cohort table
 * and the drop-reasons aggregation.
 */
export default async function AlphaPage() {
  const data = await loadAlpha();
  return (
    <div className="page">
      <header className="page-header">
        <div>
          <h1 className="page-title">Alpha</h1>
          <div className="page-subtitle">
            five-signal live read from <code>alpha/users/</code>
          </div>
        </div>
      </header>
      <section className="section">
        <AlphaPanel data={data} />
      </section>
    </div>
  );
}
