/**
 * DebugStrip — Phase 5H bottom row.
 *
 * Four tiny muted counters that answer the question the popup's
 * larger sections cannot: *is anything being captured?* The user
 * is meant to glance, not read; the strip sits below the body and
 * never asks for attention.
 *
 * Shown only in the connected states (capturing / investigations /
 * recovery). In the empty / disconnected / offline / loading
 * states the popup is doing other talking; an additional row would
 * be noise.
 */

export function DebugStrip({
  captured,
  browser,
  investigations,
  recovery,
}: {
  captured: number;
  browser: number;
  investigations: number;
  recovery: number;
}) {
  const fmt = (n: number) => (n > 9999 ? `${Math.floor(n / 1000)}k` : `${n}`);
  return (
    <div
      role="status"
      aria-label="capture counters"
      style={{
        display: "flex",
        justifyContent: "center",
        gap: 14,
        padding: "8px 12px 10px",
        borderTop: "1px solid var(--line)",
        fontSize: 10,
        fontFamily:
          "ui-monospace, SFMono-Regular, Menlo, Consolas, monospace",
        color: "var(--ink-4)",
      }}
    >
      <Counter label="captured" value={fmt(captured)} />
      <Sep />
      <Counter label="browser" value={fmt(browser)} />
      <Sep />
      <Counter label="invest" value={fmt(investigations)} />
      <Sep />
      <Counter label="recovery" value={fmt(recovery)} />
    </div>
  );
}

function Counter({ label, value }: { label: string; value: string }) {
  return (
    <span style={{ display: "inline-flex", gap: 4, alignItems: "baseline" }}>
      <span style={{ color: "var(--ink-2)", fontWeight: 600 }}>{value}</span>
      <span>{label}</span>
    </span>
  );
}

function Sep() {
  return <span style={{ opacity: 0.4 }}>·</span>;
}
