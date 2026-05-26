import { motion } from "framer-motion";
import { calm } from "../../lib/motion";

/**
 * Phase 7A connection states. Used when there is no live data to
 * render the populated body — the popup still has a Header above
 * + a Trust strip below, so these widgets only need to fill the
 * middle.
 */

export function LoadingPlate() {
  return (
    <Centered>
      <motion.div
        animate={{ opacity: [0.4, 1, 0.4] }}
        transition={{ duration: 1.6, repeat: Infinity, ease: "easeInOut" }}
        style={{
          width: 18,
          height: 18,
          borderRadius: 6,
          background: "var(--accent-soft)",
          border: "2px solid var(--accent-line)",
        }}
      />
      <Headline>Connecting to the daemon…</Headline>
      <Sub>One quick check on 127.0.0.1:4545.</Sub>
    </Centered>
  );
}

export function ReconnectingPlate() {
  return (
    <Centered>
      <Headline>Reconnecting</Headline>
      <Sub>Waiting for the daemon to answer.</Sub>
    </Centered>
  );
}

export function OfflinePlate({ onRetry }: { onRetry: () => void }) {
  return (
    <Centered>
      <Headline>You are offline</Headline>
      <Sub>Recall still works locally — the daemon never needs the internet.</Sub>
      <RetryButton onClick={onRetry} />
    </Centered>
  );
}

export function DisconnectedPlate({
  everConnected,
  onRetry,
}: {
  everConnected: boolean;
  onRetry: () => void;
}) {
  return (
    <Centered>
      <Headline>{everConnected ? "Recall isn't running" : "Recall isn't installed"}</Headline>
      <Sub>
        {everConnected
          ? "Open the desktop app to resume capture."
          : "Install the Recall desktop app to begin."}
      </Sub>
      <RetryButton onClick={onRetry} />
    </Centered>
  );
}

export function EmptyPlate({
  onShowExample,
  onStartWorking,
}: {
  onShowExample: () => void;
  onStartWorking: () => void;
}) {
  return (
    <Centered>
      <motion.div
        initial={{ scale: 0.85, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        transition={calm}
        style={{
          width: 22,
          height: 22,
          borderRadius: 6,
          background: "var(--accent)",
          boxShadow: "0 6px 18px rgba(139, 127, 227, 0.35)",
        }}
      />
      <Headline>Recall notices unfinished work</Headline>
      <Sub>Work normally. Return later. Continue instantly.</Sub>
      <div style={{ display: "flex", flexDirection: "column", gap: 8, alignItems: "stretch", width: 200 }}>
        <PrimaryButton onClick={onShowExample}>Show example</PrimaryButton>
        <SecondaryButton onClick={onStartWorking}>Start working</SecondaryButton>
      </div>
    </Centered>
  );
}

// ── primitives ───────────────────────────────────────────────────

function Centered({ children }: { children: React.ReactNode }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 4 }}
      animate={{ opacity: 1, y: 0 }}
      transition={calm}
      style={{
        flex: 1,
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        justifyContent: "center",
        gap: 12,
        padding: "32px 26px",
        textAlign: "center",
      }}
    >
      {children}
    </motion.div>
  );
}

function Headline({ children }: { children: React.ReactNode }) {
  return (
    <h2
      style={{
        margin: 0,
        fontSize: 15,
        fontWeight: 600,
        color: "var(--ink)",
        letterSpacing: "-0.1px",
      }}
    >
      {children}
    </h2>
  );
}

function Sub({ children }: { children: React.ReactNode }) {
  return (
    <p
      style={{
        margin: 0,
        fontSize: 12,
        color: "var(--ink-3)",
        lineHeight: 1.5,
        maxWidth: 280,
      }}
    >
      {children}
    </p>
  );
}

function RetryButton({ onClick }: { onClick: () => void }) {
  return (
    <button
      onClick={onClick}
      style={{
        marginTop: 4,
        height: 32,
        padding: "0 18px",
        borderRadius: 10,
        background: "var(--surface-1)",
        color: "var(--ink-2)",
        border: "1px solid var(--line)",
        fontSize: 12,
        fontWeight: 500,
        cursor: "pointer",
        transition: "background var(--motion-fast) var(--motion-ease)",
      }}
      onMouseEnter={(e) => ((e.currentTarget.style.background = "var(--surface-2)"))}
      onMouseLeave={(e) => ((e.currentTarget.style.background = "var(--surface-1)"))}
    >
      Retry
    </button>
  );
}

function PrimaryButton({
  onClick,
  children,
}: {
  onClick: () => void;
  children: React.ReactNode;
}) {
  return (
    <button
      onClick={onClick}
      style={{
        height: 36,
        padding: "0 18px",
        borderRadius: 10,
        background: "var(--accent)",
        color: "white",
        fontSize: 12.5,
        fontWeight: 600,
        cursor: "pointer",
        boxShadow: "0 4px 12px rgba(139, 127, 227, 0.30)",
        transition: "background var(--motion-fast) var(--motion-ease)",
      }}
      onMouseEnter={(e) => ((e.currentTarget.style.background = "var(--accent-hover)"))}
      onMouseLeave={(e) => ((e.currentTarget.style.background = "var(--accent)"))}
    >
      {children}
    </button>
  );
}

function SecondaryButton({
  onClick,
  children,
}: {
  onClick: () => void;
  children: React.ReactNode;
}) {
  return (
    <button
      onClick={onClick}
      style={{
        height: 36,
        padding: "0 18px",
        borderRadius: 10,
        background: "var(--surface-1)",
        color: "var(--ink-2)",
        border: "1px solid var(--line)",
        fontSize: 12.5,
        fontWeight: 500,
        cursor: "pointer",
        transition: "background var(--motion-fast) var(--motion-ease)",
      }}
      onMouseEnter={(e) => ((e.currentTarget.style.background = "var(--surface-2)"))}
      onMouseLeave={(e) => ((e.currentTarget.style.background = "var(--surface-1)"))}
    >
      {children}
    </button>
  );
}
