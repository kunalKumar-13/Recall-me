import { loadScreenshots, SCREENSHOTS_DIR } from "../../lib/loaders";
import { VerdictPill } from "../../components/panels/Verdict";

export const dynamic = "force-dynamic";

/**
 * `/screenshots` — the screenshot manager.
 *
 * One section per bucket (launcher-v2 / launcher-v3 / extension-v2 /
 * demo / alpha / legacy flat). Each section: per-bucket verdict
 * (green / yellow / red / mute), thumbnails, and a *missing markers*
 * list for any directive-named PNG the bucket doesn't have yet.
 *
 * Thumbnails are served from `apps/admin/web/public/screens/<subdir>/`
 * — the live admin runs locally on the founder's laptop, so the
 * deepest path the page has to handle is the static asset pipeline
 * Next already provides.
 */
export default async function ScreenshotsPage() {
  const buckets = await loadScreenshots();
  const total = buckets.reduce((a, b) => a + b.count, 0);
  return (
    <div className="page">
      <header className="page-header">
        <div>
          <h1 className="page-title">Screenshot manager</h1>
          <div className="page-subtitle">
            {total} capture(s) across {buckets.filter((b) => b.exists).length} bucket(s) · source <code>{SCREENSHOTS_DIR}</code>
          </div>
        </div>
      </header>

      {buckets.map((b) => (
        <section key={b.id} className="section">
          <div className="section-header">
            <span className="section-title">{b.label}</span>
            <span className="section-aside">
              — {b.count} present {b.missing.length > 0 && <> · {b.missing.length} missing</>}
              {b.mtime ? <> · {new Date(b.mtime).toLocaleString()}</> : null}
            </span>
            <span style={{ marginLeft: "auto" }}><VerdictPill value={b.verdict} /></span>
          </div>
          {!b.exists ? (
            <div className="card empty-note">
              <code>{b.dir}</code> doesn&apos;t exist yet.
            </div>
          ) : b.count === 0 ? (
            <div className="card empty-note">
              Bucket is empty.
            </div>
          ) : (
            <div className="grid grid-3">
              {b.files.map((f) => (
                <figure key={f} className="card" style={{ overflow: "hidden" }}>
                  {/* eslint-disable-next-line @next/next/no-img-element */}
                  <img
                    src={publicPathFor(b.id, f)}
                    alt={f}
                    loading="lazy"
                    style={{ width: "100%", height: "auto", display: "block" }}
                  />
                  <figcaption className="panel-row" style={{ borderTop: "1px solid var(--line)" }}>
                    <span className="panel-row-label" style={{ fontFamily: "ui-monospace, monospace" }}>{f}</span>
                    <span className="panel-row-detail" />
                    <span className="tag">{b.id}</span>
                  </figcaption>
                </figure>
              ))}
            </div>
          )}
          {b.missing.length > 0 && (
            <div className="card" style={{ marginTop: 10, padding: 12 }}>
              <div className="section-title" style={{ marginBottom: 4 }}>missing markers</div>
              <div style={{ display: "flex", flexWrap: "wrap", gap: 6 }}>
                {b.missing.map((m) => (
                  <span key={m} className="tag" style={{
                    color: "var(--warn)", borderColor: "var(--warn)", background: "var(--warn-soft)",
                  }}>{m}</span>
                ))}
              </div>
            </div>
          )}
        </section>
      ))}
    </div>
  );
}

function publicPathFor(bucketId: string, filename: string): string {
  // The admin web app's public/ has subdirectories mirroring
  // `assets/screenshots/<bucket>/`. The legacy flat bucket
  // lands at /screens/<filename> directly.
  if (bucketId === "extension-flat") {
    // These live at assets/screenshots/*.png; not copied into
    // admin public/, so render a small placeholder instead.
    return "/screens/extension-v2/extension-empty.png";
  }
  return `/screens/${bucketId}/${filename}`;
}
