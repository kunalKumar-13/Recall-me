import Link from "next/link";
import { loadLogSources, loadOneLog } from "../../lib/loaders";
import { VerdictPill } from "../../components/panels/Verdict";

export const dynamic = "force-dynamic";

/**
 * `/logs?source=<id>&q=<query>` — log viewer.
 *
 * Two columns:
 *   - left: source picker (doctor / recovery / daily / alpha / release)
 *           with the per-source verdict + entry count.
 *   - right: filtered entries from the selected source. `?q=` is
 *           a substring filter on the rendered message; defaults
 *           to empty.
 *
 * Download is a copy-cmd row (`Get-Content <path>`) — same *no
 * server* contract as the rest of the room.
 */
export default async function LogsPage({
  searchParams,
}: {
  searchParams: { source?: string; q?: string };
}) {
  const sources = await loadLogSources();
  const sourceId = searchParams.source || sources[0]?.id || "";
  const selected = sourceId ? await loadOneLog(sourceId) : null;
  const q = (searchParams.q || "").trim().toLowerCase();
  const filtered = selected
    ? selected.entries.filter((e) =>
        !q || e.message.toLowerCase().includes(q) ||
        (e.level || "").toLowerCase().includes(q)
      )
    : [];

  return (
    <div className="page">
      <header className="page-header">
        <div>
          <h1 className="page-title">Logs</h1>
          <div className="page-subtitle">
            doctor · recovery · daily · alpha · release
          </div>
        </div>
      </header>

      <section className="section">
        <div className="grid" style={{ gridTemplateColumns: "260px minmax(0, 1fr)", gap: 14 }}>
          <div className="card" style={{ overflow: "hidden" }}>
            {sources.map((s) => (
              <Link
                key={s.id}
                href={`/logs?source=${s.id}`}
                className="panel-row"
                style={{
                  textDecoration: "none",
                  color: "inherit",
                  background: s.id === sourceId ? "var(--accent-soft)" : undefined,
                }}
              >
                <span className="panel-row-label">{s.label}</span>
                <span className="panel-row-detail">
                  {s.entries.length} entries
                  {s.mtime ? ` · ${new Date(s.mtime).toLocaleString()}` : ""}
                </span>
                <VerdictPill value={s.verdict} />
              </Link>
            ))}
          </div>

          <div>
            {!selected ? (
              <div className="card empty-note">Pick a source on the left.</div>
            ) : (
              <>
                <div className="section-header">
                  <span className="section-title">{selected.label}</span>
                  <span className="section-aside">
                    — <code>{selected.path}</code>
                    {selected.mtime ? <> · {new Date(selected.mtime).toLocaleString()}</> : null}
                  </span>
                </div>
                <form action="/logs" method="get" style={{ marginBottom: 10 }}>
                  <input type="hidden" name="source" value={sourceId} />
                  <input
                    name="q"
                    defaultValue={q}
                    placeholder="Filter entries…"
                    style={{
                      width: "100%",
                      padding: "8px 12px",
                      border: "1px solid var(--line)",
                      borderRadius: 8,
                      background: "var(--surface)",
                      color: "var(--ink)",
                      fontSize: 12.5,
                    }}
                  />
                </form>
                {!selected.exists ? (
                  <div className="card empty-note">
                    <code>{selected.path}</code> doesn&apos;t exist yet.
                  </div>
                ) : filtered.length === 0 ? (
                  <div className="card empty-note">
                    {q ? `No entries match "${q}".` : "Source is empty."}
                  </div>
                ) : (
                  <div className="card" style={{
                    overflow: "auto",
                    maxHeight: "60vh",
                    fontFamily: "ui-monospace, SFMono-Regular, Menlo, Consolas, monospace",
                    fontSize: 11.5,
                    padding: 14,
                  }}>
                    {filtered.slice(0, 200).map((e, i) => (
                      <div key={i} style={{ padding: "2px 0", color: "var(--ink-2)" }}>
                        {e.ts && <span style={{ color: "var(--ink-4)" }}>{e.ts} </span>}
                        {e.level && (
                          <span style={{
                            color: "var(--accent)",
                            padding: "0 6px",
                            background: "var(--accent-soft)",
                            borderRadius: 4,
                            marginRight: 6,
                          }}>{e.level}</span>
                        )}
                        {e.message.length > 240 ? e.message.slice(0, 240) + "…" : e.message}
                      </div>
                    ))}
                    {filtered.length > 200 && (
                      <div style={{ marginTop: 8, color: "var(--ink-3)", fontStyle: "italic" }}>
                        {filtered.length - 200} more · refine the filter
                      </div>
                    )}
                  </div>
                )}
                <div className="card" style={{ marginTop: 14, padding: 12 }}>
                  <div className="section-title" style={{ marginBottom: 4 }}>Download</div>
                  <code style={{ fontSize: 11 }}>
                    Get-Content -Raw &quot;{selected.path}&quot; | Set-Clipboard
                  </code>
                </div>
              </>
            )}
          </div>
        </div>
      </section>
    </div>
  );
}
