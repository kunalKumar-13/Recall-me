import { useEffect, useState } from "react";
import { AnimatePresence, motion } from "framer-motion";
import { calm, calmFast } from "../lib/motion";
import {
  getActiveTabDomain,
  getExcludedDomains,
  openRecall,
  openTab,
  setExcludedDomains,
} from "../lib/api";
import type {
  ConnectionState,
  Health,
  Settings,
  TodaySummary,
} from "../lib/types";
import { Icon } from "./icons";

const DOCS_URL = "https://github.com/kunalKumar-13/Recall-me#readme";

/**
 * Settings is a full-popup view, reached from the header gear and
 * left by the back arrow — a slide, never a modal stacked on top.
 * The labels say *what* and *where*, never "enable AI memory": a
 * capture toggle names the surface it captures and the loopback
 * address it writes to.
 *
 * Every control here is real. The capture toggles map to per-kind
 * gates the worker checks before enqueuing; Pause is the same
 * `pauseUntil` epoch the header glyph flips; Private sites edits the
 * `excludedDomains` list the worker filters on live.
 */
export function SettingsPanel({
  settings,
  onChange,
  onBack,
  connection,
  health,
  today,
  pausedUntil,
  onTogglePause,
  onRetry,
}: {
  settings: Settings;
  onChange: (next: Settings) => void;
  onBack: () => void;
  connection: ConnectionState;
  health: Health | null;
  today: TodaySummary | null;
  pausedUntil: number;
  onTogglePause: () => void;
  onRetry: () => void;
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
        <GroupLabel>Connection</GroupLabel>
        <ConnectionDrawer
          connection={connection}
          health={health}
          today={today}
          onRetry={onRetry}
        />

        <div style={{ height: 18 }} />

        <GroupLabel>Capture</GroupLabel>
        <div className="card" style={{ overflow: "hidden" }}>
          <ToggleRow
            label="Capture browsing"
            hint="Pages you visit + how long you stay → 127.0.0.1:4545"
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

        <GroupLabel>Pause</GroupLabel>
        <PauseCard pausedUntil={pausedUntil} onToggle={onTogglePause} />

        <div style={{ height: 18 }} />

        <GroupLabel>Private sites</GroupLabel>
        <PrivateSites />

        <div style={{ height: 18 }} />

        <GroupLabel>Open</GroupLabel>
        <div className="card" style={{ overflow: "hidden" }}>
          <LinkRow
            label="Open Recall"
            hint="The desktop launcher"
            onClick={() => {
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

/**
 * One pause mechanism for the whole extension: the `pauseUntil`
 * epoch. The row says what is true right now and what one click
 * does — resumes at a named time, not a vague "later".
 */
function PauseCard({
  pausedUntil,
  onToggle,
}: {
  pausedUntil: number;
  onToggle: () => void;
}) {
  const paused = pausedUntil > Date.now();
  const resumeAt = new Date(pausedUntil).toLocaleTimeString([], {
    hour: "2-digit",
    minute: "2-digit",
  });
  return (
    <div
      className="card"
      style={{
        display: "flex",
        alignItems: "center",
        gap: 12,
        padding: "12px 14px",
      }}
    >
      <span style={{ flex: 1, minWidth: 0 }}>
        <span style={{ display: "block", fontSize: 13, color: "var(--ink)" }}>
          {paused ? `Paused — resumes at ${resumeAt}` : "Capture is on"}
        </span>
        <span
          style={{ display: "block", fontSize: 10.5, color: "var(--ink-4)" }}
        >
          {paused
            ? "Nothing is being recorded right now"
            : "Pause everything for one hour, no restart needed"}
        </span>
      </span>
      <motion.button
        whileHover={{ y: -1 }}
        transition={calmFast}
        onClick={onToggle}
        style={{
          flexShrink: 0,
          height: 28,
          padding: "0 12px",
          borderRadius: 7,
          background: paused ? "var(--accent)" : "var(--surface-2)",
          color: paused ? "#fff" : "var(--ink-2)",
          fontSize: 12,
          fontWeight: paused ? 600 : 500,
        }}
      >
        {paused ? "Resume now" : "Pause 1 hour"}
      </motion.button>
    </div>
  );
}

/**
 * The excluded-domains editor, plus a one-click "never capture the
 * site I was just on". Exclusion is forward-only: it stops new
 * capture on the domain, it does not rewrite what is already in
 * ~/.recall (clear history from the Recall app).
 */
function PrivateSites() {
  const [domains, setDomains] = useState<string[]>([]);
  const [activeDomain, setActiveDomain] = useState<string | null>(null);
  const [loaded, setLoaded] = useState(false);

  useEffect(() => {
    void Promise.all([getExcludedDomains(), getActiveTabDomain()]).then(
      ([list, active]) => {
        setDomains(list);
        setActiveDomain(active);
        setLoaded(true);
      },
    );
  }, []);

  const save = (next: string[]) => {
    setDomains(next);
    void setExcludedDomains(next);
  };
  const exclude = (d: string) => {
    if (!domains.includes(d)) save([...domains, d].sort());
  };
  const remove = (d: string) => save(domains.filter((x) => x !== d));

  const canExcludeActive =
    activeDomain !== null && !domains.includes(activeDomain);

  return (
    <>
      <div className="card" style={{ overflow: "hidden" }}>
        {canExcludeActive && (
          <div
            style={{
              display: "flex",
              alignItems: "center",
              gap: 12,
              padding: "12px 14px",
              borderBottom:
                domains.length > 0 ? "1px solid var(--line)" : "none",
            }}
          >
            <span style={{ flex: 1, minWidth: 0 }}>
              <span
                style={{
                  display: "block",
                  fontSize: 13,
                  color: "var(--ink)",
                  overflow: "hidden",
                  textOverflow: "ellipsis",
                  whiteSpace: "nowrap",
                }}
              >
                {activeDomain}
              </span>
              <span
                style={{
                  display: "block",
                  fontSize: 10.5,
                  color: "var(--ink-4)",
                }}
              >
                The site you were just on
              </span>
            </span>
            <motion.button
              whileHover={{ y: -1 }}
              transition={calmFast}
              onClick={() => exclude(activeDomain)}
              style={{
                flexShrink: 0,
                height: 28,
                padding: "0 12px",
                borderRadius: 7,
                background: "var(--surface-2)",
                color: "var(--ink-2)",
                fontSize: 12,
                fontWeight: 500,
              }}
            >
              Never capture
            </motion.button>
          </div>
        )}

        <AnimatePresence initial={false}>
          {domains.map((d, i) => (
            <motion.div
              key={d}
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: "auto" }}
              exit={{ opacity: 0, height: 0 }}
              transition={calm}
              style={{ overflow: "hidden" }}
            >
              <div
                style={{
                  display: "flex",
                  alignItems: "center",
                  gap: 12,
                  padding: "10px 14px",
                  borderBottom:
                    i === domains.length - 1 ? "none" : "1px solid var(--line)",
                }}
              >
                <span
                  style={{
                    flex: 1,
                    minWidth: 0,
                    fontSize: 12.5,
                    color: "var(--ink-2)",
                    fontFamily:
                      '"Geist Mono", ui-monospace, SFMono-Regular, Menlo, Consolas, monospace',
                    overflow: "hidden",
                    textOverflow: "ellipsis",
                    whiteSpace: "nowrap",
                  }}
                >
                  {d}
                </span>
                <motion.button
                  whileHover={{ scale: 1.08 }}
                  transition={calmFast}
                  onClick={() => remove(d)}
                  aria-label={`Capture ${d} again`}
                  title="Capture this site again"
                  style={{
                    flexShrink: 0,
                    width: 22,
                    height: 22,
                    borderRadius: 6,
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "center",
                    background: "var(--surface-2)",
                    color: "var(--ink-3)",
                    fontSize: 12,
                    lineHeight: 1,
                  }}
                >
                  ×
                </motion.button>
              </div>
            </motion.div>
          ))}
        </AnimatePresence>

        {loaded && domains.length === 0 && !canExcludeActive && (
          <div
            style={{
              padding: "12px 14px",
              fontSize: 11.5,
              color: "var(--ink-4)",
            }}
          >
            No excluded sites yet.
          </div>
        )}
      </div>
      <p
        style={{
          marginTop: 8,
          fontSize: 10.5,
          lineHeight: 1.55,
          color: "var(--ink-4)",
        }}
      >
        Excluded sites are never captured from now on. Anything saved
        earlier stays in ~/.recall — clear history from the Recall app.
      </p>
    </>
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


/**
 * Repair drawer. A real-data card that sits at the top of Settings
 * and answers *is the daemon alive?* without navigating back to the
 * popup body. Two numbers, both labelled for what they are: today's
 * count from the day file (survives restarts) and the since-start
 * counter from /v1/health.
 */
function ConnectionDrawer({
  connection,
  health,
  today,
  onRetry,
}: {
  connection: ConnectionState;
  health: Health | null;
  today: TodaySummary | null;
  onRetry: () => void;
}) {
  // Collapsible. Default expanded when something is *off* (the
  // drawer is informational then), collapsed when the daemon is
  // healthy (one calm row, click to expand).
  const isUp = connection === "connected" && health !== null;
  const [expanded, setExpanded] = useState(!isUp);

  const dotColor = isUp
    ? "var(--ok)"
    : connection === "offline" || connection === "loading"
      ? "var(--ink-4)"
      : "var(--warn)";

  const statusLine = isUp
    ? "Daemon listening on 127.0.0.1:4545"
    : connection === "offline"
      ? "Browser is offline; daemon state unknown"
      : connection === "loading" || connection === "reconnecting"
        ? "Checking the daemon…"
        : "Daemon not responding";

  return (
    <div className="card" style={{ overflow: "hidden" }}>
      <motion.button
        whileHover={{ background: "var(--surface-2)" }}
        transition={calmFast}
        onClick={() => setExpanded((v) => !v)}
        aria-expanded={expanded}
        aria-label={expanded ? "Collapse connection drawer" : "Expand connection drawer"}
        style={{
          display: "flex",
          alignItems: "center",
          gap: 11,
          width: "100%",
          padding: "12px 14px",
          textAlign: "left",
          borderBottom: expanded ? "1px solid var(--line)" : "none",
        }}
      >
        <motion.span
          animate={isUp ? { opacity: [0.55, 1, 0.55] } : { opacity: 1 }}
          transition={
            isUp
              ? { duration: 1.6, repeat: Infinity, ease: "easeInOut" }
              : { duration: 0 }
          }
          style={{
            width: 8,
            height: 8,
            borderRadius: 4,
            background: dotColor,
            flexShrink: 0,
          }}
        />
        <span style={{ minWidth: 0, flex: 1 }}>
          <span style={{ display: "block", fontSize: 13, color: "var(--ink)" }}>
            {statusLine}
          </span>
          {isUp && (
            <span
              style={{
                display: "block",
                fontSize: 10.5,
                color: "var(--ink-4)",
                fontFamily:
                  '"Geist Mono", ui-monospace, SFMono-Regular, Menlo, Consolas, monospace',
              }}
            >
              {today
                ? `${today.count.toLocaleString()} events today`
                : "today's count unavailable"}
              {health
                ? ` · ${health.ingestedTotal.toLocaleString()} since start`
                : ""}
            </span>
          )}
        </span>
        <motion.span
          animate={{ rotate: expanded ? 90 : 0 }}
          transition={calmFast}
          style={{
            color: "var(--ink-4)",
            fontSize: 11,
            lineHeight: 1,
            flexShrink: 0,
            display: "inline-block",
          }}
        >
          ›
        </motion.span>
      </motion.button>
      <AnimatePresence initial={false}>
        {expanded && (
          <motion.div
            key="drawer-body"
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: "auto" }}
            exit={{ opacity: 0, height: 0 }}
            transition={calmFast}
            style={{ overflow: "hidden" }}
          >
            <div
              style={{
                display: "flex",
                gap: 8,
                padding: "10px 14px",
              }}
            >
              <motion.button
                whileHover={{ y: -1 }}
                transition={calmFast}
                onClick={onRetry}
                style={{
                  height: 28,
                  padding: "0 12px",
                  borderRadius: 7,
                  background: "var(--surface-2)",
                  color: "var(--ink-2)",
                  fontSize: 12,
                  fontWeight: 500,
                }}
              >
                Re-probe
              </motion.button>
              {!isUp && (
                <motion.button
                  whileHover={{ y: -1 }}
                  transition={calmFast}
                  onClick={() => {
                    void openRecall();
                  }}
                  style={{
                    height: 28,
                    padding: "0 12px",
                    borderRadius: 7,
                    background: "var(--accent)",
                    color: "#fff",
                    fontSize: 12,
                    fontWeight: 600,
                  }}
                >
                  Open Recall
                </motion.button>
              )}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
