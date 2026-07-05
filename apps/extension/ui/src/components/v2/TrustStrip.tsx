import type { ConnectionState } from "../../lib/types";

/**
 * Phase 7A collapsed trust strip. One row, tiny pills, pinned to
 * the bottom of the popup:
 *
 *    LOCAL ONLY    NO CLOUD    0 uploads    daemon OK
 *
 * Replaces the old `TrustSurface` section. The directive is
 * explicit: *Remove giant section.*
 */
export function TrustStrip({
  connection,
  queued = 0,
}: {
  connection: ConnectionState;
  /** Durable-outbox depth — events captured but not yet delivered. */
  queued?: number;
}) {
  const daemon =
    connection === "connected"
      ? { label: "daemon OK", tone: "ok" as const }
      : connection === "reconnecting"
        ? { label: "reconnecting", tone: "warn" as const }
        : connection === "disconnected"
          ? { label: "daemon off", tone: "warn" as const }
          : connection === "offline"
            ? { label: "offline", tone: "warn" as const }
            : { label: "connecting", tone: "muted" as const };
  return (
    <footer
      style={{
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        flexWrap: "wrap",
        gap: 6,
        padding: "10px 14px 12px",
        background: "var(--surface-0)",
        borderTop: "1px solid var(--line)",
      }}
    >
      <TrustPill label="local only" tone="muted" />
      <TrustPill label="no cloud" tone="muted" />
      <TrustPill label="0 uploads" tone="muted" />
      <TrustPill label={daemon.label} tone={daemon.tone} />
      {queued > 0 && (
        <TrustPill
          label={`${queued} queued`}
          tone={connection === "connected" ? "muted" : "warn"}
        />
      )}
    </footer>
  );
}

function TrustPill({
  label,
  tone,
}: {
  label: string;
  tone: "ok" | "warn" | "muted";
}) {
  const colours =
    tone === "ok"
      ? { fg: "var(--ok)", bg: "var(--ok-soft)" }
      : tone === "warn"
        ? { fg: "var(--warn)", bg: "var(--warn-soft)" }
        : { fg: "var(--ink-3)", bg: "var(--surface-2)" };
  return (
    <span
      style={{
        display: "inline-flex",
        alignItems: "center",
        height: 18,
        padding: "0 8px",
        borderRadius: 999,
        background: colours.bg,
        color: colours.fg,
        fontSize: 9.5,
        fontWeight: 700,
        letterSpacing: "1px",
        textTransform: "uppercase",
        whiteSpace: "nowrap",
      }}
    >
      {label}
    </span>
  );
}
