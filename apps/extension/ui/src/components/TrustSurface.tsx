import type { ConnectionState } from "../lib/types";
import { Icon } from "./icons";

/**
 * The trust strip. Every memory product lives or dies on whether the
 * user believes it about where their data goes — so the popup states
 * it plainly, every time it opens: local only, daemon status, what
 * was captured today. Facts, not reassurance theatre.
 */
export function TrustSurface({
  connection,
  eventsToday,
  paused,
}: {
  connection: ConnectionState;
  eventsToday: number;
  paused: boolean;
}) {
  const connected = connection === "connected";

  return (
    <div
      className="card"
      style={{ padding: "12px 14px", display: "grid", gap: 9 }}
    >
      <Row>
        <Dot
          color={connected ? "var(--ok)" : "var(--warn)"}
        />
        <Label>
          {connected ? "Daemon connected" : "Daemon not reachable"}
        </Label>
        <Value>127.0.0.1:4545</Value>
      </Row>

      <Divider />

      <Row>
        <span style={{ color: "var(--ink-3)", display: "flex" }}>
          <Icon.lock size={14} />
        </span>
        <Label>Local only</Label>
        <Value>{paused ? "paused" : "no cloud · no telemetry"}</Value>
      </Row>

      <Divider />

      <Row>
        <Dot color="var(--ink-4)" />
        <Label>Captured today</Label>
        <Value>
          {connected ? `${eventsToday.toLocaleString()} events` : "—"}
        </Value>
      </Row>
    </div>
  );
}

function Row({ children }: { children: React.ReactNode }) {
  return (
    <div style={{ display: "flex", alignItems: "center", gap: 9 }}>
      {children}
    </div>
  );
}

function Dot({ color }: { color: string }) {
  return (
    <span
      style={{
        width: 7,
        height: 7,
        borderRadius: 4,
        background: color,
        flexShrink: 0,
      }}
    />
  );
}

function Label({ children }: { children: React.ReactNode }) {
  return (
    <span style={{ fontSize: 12, color: "var(--ink-2)" }}>{children}</span>
  );
}

function Value({ children }: { children: React.ReactNode }) {
  return (
    <span
      style={{
        marginLeft: "auto",
        fontSize: 10.5,
        fontFamily: "ui-monospace, SFMono-Regular, Menlo, Consolas, monospace",
        color: "var(--ink-4)",
      }}
    >
      {children}
    </span>
  );
}

function Divider() {
  return <div style={{ height: 1, background: "var(--line)" }} />;
}
