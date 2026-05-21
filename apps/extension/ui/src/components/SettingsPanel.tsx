import { motion } from "framer-motion";
import { calm, calmFast } from "../lib/motion";
import { openRecall, openTab } from "../lib/api";
import type { Settings } from "../lib/types";
import { Icon } from "./icons";

const DOCS_URL = "https://github.com/kunalKumar-13/Recall-me#readme";

/**
 * Settings is a full-popup view, reached from the header gear and
 * left by the back arrow — a slide, never a modal stacked on top.
 * The labels say *what* and *where*, never "enable AI memory": a
 * capture toggle names the surface it captures and the loopback
 * address it writes to.
 */
export function SettingsPanel({
  settings,
  onChange,
  onBack,
}: {
  settings: Settings;
  onChange: (next: Settings) => void;
  onBack: () => void;
}) {
  const set = (patch: Partial<Settings>) =>
    onChange({ ...settings, ...patch });

  return (
    <div style={{ display: "flex", flexDirection: "column", height: "100%" }}>
      <header
        style={{
          display: "flex",
          alignItems: "center",
          gap: 10,
          padding: "14px 16px",
          borderBottom: "1px solid var(--line)",
        }}
      >
        <motion.button
          whileHover={{ x: -1 }}
          transition={calmFast}
          onClick={onBack}
          aria-label="Back"
          style={{
            display: "flex",
            color: "var(--ink-2)",
            padding: 2,
          }}
        >
          <Icon.back size={18} />
        </motion.button>
        <span style={{ fontSize: 14, fontWeight: 600 }}>Settings</span>
      </header>

      <div className="scroll-area" style={{ padding: "18px 16px" }}>
        <GroupLabel>Capture</GroupLabel>
        <div className="card" style={{ overflow: "hidden" }}>
          <ToggleRow
            label="Capture browsing"
            hint="Pages you visit → 127.0.0.1:4545"
            checked={settings.captureBrowsing}
            onChange={(v) => set({ captureBrowsing: v })}
          />
          <ToggleRow
            label="Capture searches"
            hint="Search queries → local event log"
            checked={settings.captureSearches}
            onChange={(v) => set({ captureSearches: v })}
          />
          <ToggleRow
            label="Capture chats"
            hint="AI-chat sessions → local event log"
            checked={settings.captureChats}
            onChange={(v) => set({ captureChats: v })}
            last
          />
        </div>

        <div style={{ height: 18 }} />

        <GroupLabel>Browser memory</GroupLabel>
        <div className="card" style={{ overflow: "hidden" }}>
          <ToggleRow
            label="Pause browser memory"
            hint="Stop all capture until you turn this off"
            checked={settings.paused}
            onChange={(v) => set({ paused: v })}
            last
          />
        </div>

        <div style={{ height: 18 }} />

        <GroupLabel>Open</GroupLabel>
        <div className="card" style={{ overflow: "hidden" }}>
          <LinkRow
            label="Open Recall"
            hint="The desktop launcher"
            onClick={() => {
              // Fire-and-forget; openRecall handles the three-rung
              // ladder internally. The settings panel does not have
              // room for a feedback transition; if the protocol
              // isn't registered the user can fall back to their
              // desktop shortcut. Never throws.
              void openRecall();
            }}
          />
          <LinkRow
            label="Open docs"
            hint="github.com/kunalKumar-13/Recall-me"
            onClick={() => openTab(DOCS_URL)}
            last
          />
        </div>

        <p
          style={{
            marginTop: 18,
            fontSize: 10.5,
            lineHeight: 1.6,
            color: "var(--ink-4)",
          }}
        >
          Everything captured stays on this device, in the local Recall
          daemon. No accounts, no cloud, no telemetry.
        </p>
      </div>
    </div>
  );
}

function GroupLabel({ children }: { children: React.ReactNode }) {
  return (
    <div
      style={{
        fontSize: 10,
        fontWeight: 600,
        letterSpacing: "0.9px",
        textTransform: "uppercase",
        color: "var(--ink-3)",
        marginBottom: 9,
      }}
    >
      {children}
    </div>
  );
}

function ToggleRow({
  label,
  hint,
  checked,
  onChange,
  last,
}: {
  label: string;
  hint: string;
  checked: boolean;
  onChange: (v: boolean) => void;
  last?: boolean;
}) {
  return (
    <div
      style={{
        display: "flex",
        alignItems: "center",
        gap: 12,
        padding: "12px 14px",
        borderBottom: last ? "none" : "1px solid var(--line)",
      }}
    >
      <span style={{ flex: 1, minWidth: 0 }}>
        <span style={{ display: "block", fontSize: 13, color: "var(--ink)" }}>
          {label}
        </span>
        <span
          style={{ display: "block", fontSize: 10.5, color: "var(--ink-4)" }}
        >
          {hint}
        </span>
      </span>
      <Toggle checked={checked} onChange={onChange} />
    </div>
  );
}

function Toggle({
  checked,
  onChange,
}: {
  checked: boolean;
  onChange: (v: boolean) => void;
}) {
  return (
    <button
      role="switch"
      aria-checked={checked}
      onClick={() => onChange(!checked)}
      style={{
        flexShrink: 0,
        width: 38,
        height: 22,
        borderRadius: 11,
        padding: 2,
        background: checked ? "var(--accent)" : "var(--surface-sunken)",
        border: "1px solid",
        borderColor: checked ? "var(--accent)" : "var(--line-strong)",
        transition: "background 0.18s cubic-bezier(0.32,0.72,0,1)",
      }}
    >
      <motion.span
        animate={{ x: checked ? 16 : 0 }}
        transition={calm}
        style={{
          display: "block",
          width: 16,
          height: 16,
          borderRadius: 8,
          background: "#fff",
          boxShadow: "0 1px 3px rgba(24,17,45,0.25)",
        }}
      />
    </button>
  );
}

function LinkRow({
  label,
  hint,
  onClick,
  last,
}: {
  label: string;
  hint: string;
  onClick: () => void;
  last?: boolean;
}) {
  return (
    <motion.button
      className="row-button"
      whileHover={{ x: 1 }}
      transition={calmFast}
      onClick={onClick}
      style={{
        display: "flex",
        alignItems: "center",
        gap: 12,
        padding: "12px 14px",
        borderBottom: last ? "none" : "1px solid var(--line)",
      }}
    >
      <span style={{ flex: 1, minWidth: 0 }}>
        <span style={{ display: "block", fontSize: 13, color: "var(--ink)" }}>
          {label}
        </span>
        <span
          style={{ display: "block", fontSize: 10.5, color: "var(--ink-4)" }}
        >
          {hint}
        </span>
      </span>
      <span style={{ color: "var(--ink-4)", display: "flex" }}>
        <Icon.open size={15} />
      </span>
    </motion.button>
  );
}
