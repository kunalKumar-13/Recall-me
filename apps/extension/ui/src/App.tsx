import { useCallback, useEffect, useState } from "react";
import { AnimatePresence, motion } from "framer-motion";
import {
  fetchHealth,
  fetchInvestigations,
  fetchMemory,
  fetchRecovery,
  isOnline,
  loadSettings,
  markConnected,
  openTab,
  saveSettings,
  wasEverConnected,
} from "./lib/api";
import { bodyState, calm, calmFast, slideView } from "./lib/motion";
import {
  DEFAULT_SETTINGS,
  type ConnectionState,
  type Health,
  type Investigation,
  type MemoryItem,
  type PopupState,
  type Recovery,
  type Settings,
} from "./lib/types";
import { ContinueCard } from "./components/ContinueCard";
import { DebugStrip } from "./components/DebugStrip";
import { Icon } from "./components/icons";
import { InvestigationCard } from "./components/InvestigationCard";
import { MemoryList } from "./components/MemoryList";
import { Section } from "./components/Section";
import { SettingsPanel } from "./components/SettingsPanel";
import {
  CapturingState,
  DisconnectedState,
  EmptyState,
  LoadingState,
  OfflineState,
  ReconnectingState,
} from "./components/states";
import { TrustSurface } from "./components/TrustSurface";

type View = "main" | "settings";

/**
 * The popup. One mounted tree, one fresh read of the local daemon
 * per open. Two views — the memory surface and Settings — that slide
 * past each other; never a stacked modal. Everything below the
 * header is driven by one `PopupState` value, derived in
 * `derivePopupState`. The popup always shows exactly one honest
 * thing.
 */
const DEBUG_PREF_KEY = "recall.debugStripVisible";

export function App() {
  const [connection, setConnection] = useState<ConnectionState>("loading");
  const [health, setHealth] = useState<Health | null>(null);
  const [recovery, setRecovery] = useState<Recovery | null>(null);
  const [investigations, setInvestigations] = useState<Investigation[]>([]);
  const [memory, setMemory] = useState<MemoryItem[]>([]);
  const [settings, setSettings] = useState<Settings>(DEFAULT_SETTINGS);
  const [view, setView] = useState<View>("main");
  // Default true: a returning user with a momentarily-down daemon
  // should see "not running", never a wrong "not installed" flash.
  const [everConnected, setEverConnected] = useState(true);
  // Phase 5I: DebugStrip is hidden by default and toggled with Alt+D.
  // Persisted in chrome.storage so power-users keep it on across opens.
  const [debugVisible, setDebugVisible] = useState(false);

  const load = useCallback(async (reconnect = false) => {
    if (!isOnline()) {
      setConnection("offline");
      return;
    }
    setConnection(reconnect ? "reconnecting" : "loading");
    const h = await fetchHealth();
    if (!h) {
      setConnection("disconnected");
      return;
    }
    setHealth(h);
    markConnected();
    setEverConnected(true);
    const [rec, inv, mem] = await Promise.all([
      fetchRecovery(),
      fetchInvestigations(),
      fetchMemory(),
    ]);
    setRecovery(rec);
    setInvestigations(inv);
    setMemory(mem);
    setConnection("connected");
  }, []);

  useEffect(() => {
    loadSettings().then(setSettings);
    wasEverConnected().then(setEverConnected);
    load();
    // Restore the DebugStrip toggle. Chrome only - dev preview keeps
    // it off (the default).
    if (typeof chrome !== "undefined" && chrome.storage?.local) {
      chrome.storage.local.get([DEBUG_PREF_KEY], (r) => {
        setDebugVisible(!!r?.[DEBUG_PREF_KEY]);
      });
    }
  }, [load]);

  // Alt+D toggles the DebugStrip. Captured at the window level so the
  // shortcut works no matter where focus is inside the popup. Listener
  // is cleaned up on unmount (popup close).
  useEffect(() => {
    function onKey(e: KeyboardEvent) {
      // altKey is the platform-correct modifier on Win/Linux; on
      // macOS the same physical key is `Option`, which also reports
      // altKey true. `code === "KeyD"` is layout-independent.
      if (e.altKey && (e.code === "KeyD" || e.key.toLowerCase() === "d")) {
        e.preventDefault();
        setDebugVisible((v) => {
          const next = !v;
          if (typeof chrome !== "undefined" && chrome.storage?.local) {
            chrome.storage.local.set({ [DEBUG_PREF_KEY]: next });
          }
          return next;
        });
      }
    }
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, []);

  const onSettingsChange = useCallback((next: Settings) => {
    setSettings(next);
    void saveSettings(next);
  }, []);

  const onResume = useCallback(() => {
    if (recovery) recovery.urls.forEach(openTab);
  }, [recovery]);

  // Storybook-style state preview: `popup.html?state=disconnected`.
  // `?state=missing` previews the never-installed screen.
  // `?state=capturing` previews the watching-with-events screen.
  const forced = readForcedState();
  const previewMissing = forced === "missing";
  const effEverConnected = previewMissing ? false : everConnected;

  if (view === "settings") {
    return (
      <AnimatePresence mode="wait">
        <motion.div
          key="settings"
          variants={slideView}
          initial="fromRight"
          animate="center"
          exit="fromRight"
          transition={calm}
          style={{ display: "flex", flexDirection: "column", flex: 1 }}
        >
          <SettingsPanel
            settings={settings}
            onChange={onSettingsChange}
            onBack={() => setView("main")}
          />
        </motion.div>
      </AnimatePresence>
    );
  }

  const state: PopupState = previewMissing
    ? "disconnected"
    : (forced as PopupState | null) ??
      derivePopupState(connection, health, recovery, investigations, memory);

  return (
    <motion.div
      key="main"
      variants={slideView}
      initial="center"
      animate="center"
      transition={calm}
      style={{ display: "flex", flexDirection: "column", flex: 1 }}
    >
      <Header connection={connection} onSettings={() => setView("settings")} />
      <AnimatePresence mode="wait" initial={false}>
        <motion.div
          key={state}
          variants={bodyState}
          initial="enter"
          animate="show"
          exit="exit"
          transition={calmFast}
          style={{ display: "flex", flexDirection: "column", flex: 1 }}
        >
          <Body
            state={state}
            health={health}
            recovery={recovery}
            investigations={investigations}
            memory={memory}
            paused={settings.paused}
            everConnected={effEverConnected}
            onResume={onResume}
            onRetry={() => load(true)}
          />
        </motion.div>
      </AnimatePresence>
      <AnimatePresence initial={false}>
        {showsDebugStrip(state) && debugVisible && (
          <motion.div
            key="debug"
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: "auto" }}
            exit={{ opacity: 0, height: 0 }}
            transition={calmFast}
            style={{ overflow: "hidden" }}
          >
            <DebugStrip
              captured={health?.ingestedTotal ?? 0}
              browser={memory.length}
              investigations={investigations.length}
              recovery={recovery ? 1 : 0}
            />
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  );
}

// ── state machine ───────────────────────────────────────────────────

/**
 * The body's state is a pure function of the connection lifecycle
 * + the daemon response. The order of the branches encodes the
 * priority (offline > disconnected > recovery > investigations >
 * capturing > empty).
 *
 * Invariant: if the daemon is connected AND any event has been
 * ingested OR any memory row is visible, the `empty` state is
 * forbidden. The `?? "capturing"` at the bottom of the ladder is
 * how we enforce it - the only path that lands on `empty` requires
 * `ingestedTotal === 0 && memory.length === 0`.
 */
export function derivePopupState(
  connection: ConnectionState,
  health: Health | null,
  recovery: Recovery | null,
  investigations: Investigation[],
  memory: MemoryItem[],
): PopupState {
  if (connection === "offline") return "offline";
  if (connection === "loading") return "loading";
  if (connection === "reconnecting") return "reconnecting";
  if (connection === "disconnected" || !health) return "disconnected";
  if (recovery) return "recovery";
  if (investigations.length > 0) return "investigations";
  if (health.ingestedTotal > 0 || memory.length > 0) return "capturing";
  return "empty";
}

function showsDebugStrip(state: PopupState): boolean {
  return (
    state === "capturing" ||
    state === "investigations" ||
    state === "recovery"
  );
}

function readForcedState(): string | null {
  if (typeof location === "undefined") return null;
  const v = new URLSearchParams(location.search).get("state");
  return v;
}

// ── header ──────────────────────────────────────────────────────────

function Header({
  connection,
  onSettings,
}: {
  connection: ConnectionState;
  onSettings: () => void;
}) {
  const dot =
    connection === "connected"
      ? "var(--ok)"
      : connection === "disconnected" || connection === "reconnecting"
        ? "var(--warn)"
        : "var(--ink-4)";

  return (
    <header
      style={{
        display: "flex",
        alignItems: "center",
        gap: 9,
        padding: "14px 16px",
        borderBottom: "1px solid var(--line)",
      }}
    >
      <span
        style={{
          width: 9,
          height: 9,
          borderRadius: 3,
          background: "linear-gradient(135deg, #b5a8ff, #8b7fe3)",
        }}
      />
      <span style={{ fontSize: 14, fontWeight: 600, letterSpacing: "-0.1px" }}>
        Recall
      </span>
      <span
        title={connection}
        style={{
          width: 6,
          height: 6,
          borderRadius: 3,
          background: dot,
          marginLeft: 2,
        }}
      />
      <span style={{ flex: 1 }} />
      <motion.button
        whileHover={{ rotate: 35 }}
        transition={calm}
        onClick={onSettings}
        aria-label="Settings"
        style={{ display: "flex", color: "var(--ink-3)", padding: 2 }}
      >
        <Icon.gear size={17} />
      </motion.button>
    </header>
  );
}

// ── body ────────────────────────────────────────────────────────────

function Body({
  state,
  health,
  recovery,
  investigations,
  memory,
  paused,
  everConnected,
  onResume,
  onRetry,
}: {
  state: PopupState;
  health: Health | null;
  recovery: Recovery | null;
  investigations: Investigation[];
  memory: MemoryItem[];
  paused: boolean;
  everConnected: boolean;
  onResume: () => void;
  onRetry: () => void;
}) {
  switch (state) {
    case "loading":
      return <LoadingState />;
    case "reconnecting":
      return <ReconnectingState />;
    case "offline":
      return <OfflineState onRetry={onRetry} />;
    case "disconnected":
      return (
        <DisconnectedState everConnected={everConnected} onRetry={onRetry} />
      );
    case "empty":
      return <EmptyState />;
    case "capturing":
      return (
        <CapturingState
          ingestedTotal={health?.ingestedTotal ?? 0}
          memory={memory}
        />
      );
    case "investigations":
    case "recovery":
      return (
        <ConnectedBody
          recovery={recovery}
          investigations={investigations}
          memory={memory}
          paused={paused}
          eventsToday={health?.eventsToday ?? 0}
          onResume={onResume}
        />
      );
  }
}

/**
 * The fully-populated popup: a recovery (if any), the active
 * investigations, the most recent browser memory, and the Trust
 * summary - in that order. Reached only from the `investigations`
 * and `recovery` popup states.
 */
function ConnectedBody({
  recovery,
  investigations,
  memory,
  paused,
  eventsToday,
  onResume,
}: {
  recovery: Recovery | null;
  investigations: Investigation[];
  memory: MemoryItem[];
  paused: boolean;
  eventsToday: number;
  onResume: () => void;
}) {
  let index = 0;
  return (
    <div className="scroll-area" style={{ flex: 1, padding: "20px 0 8px" }}>
      {recovery && (
        <Section label="Continue" index={index++}>
          <ContinueCard recovery={recovery} onResume={onResume} />
        </Section>
      )}

      {investigations.length > 0 && (
        <Section
          label="Active investigations"
          count={`${investigations.length}`}
          index={index++}
        >
          <div className="card" style={{ overflow: "hidden" }}>
            {investigations.map((inv, i) => (
              <InvestigationCard
                key={inv.id}
                investigation={inv}
                last={i === investigations.length - 1}
              />
            ))}
          </div>
        </Section>
      )}

      {memory.length > 0 && (
        <Section label="Browser memory" index={index++}>
          <MemoryList items={memory} />
        </Section>
      )}

      <Section label="Trust" index={index++}>
        <TrustSurface
          connection="connected"
          eventsToday={eventsToday}
          paused={paused}
        />
      </Section>
    </div>
  );
}
