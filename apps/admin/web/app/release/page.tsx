import { loadRelease } from "../../lib/loaders";
import { ReleasePanel } from "../../components/panels/ReleasePanel";

export const dynamic = "force-dynamic";

/**
 * `/release` — release-center deep-dive. Per-gate progress bars +
 * the GO/PARTIAL/NO-GO verdict + the blockers list.
 */
export default async function ReleasePage() {
  const release = await loadRelease();
  return (
    <div className="page">
      <header className="page-header">
        <div>
          <h1 className="page-title">Release</h1>
          <div className="page-subtitle">
            live read from <code>apps/admin/release_state.json</code>
          </div>
        </div>
      </header>
      <section className="section">
        <ReleasePanel release={release} />
      </section>
    </div>
  );
}
