import { useCallback, useEffect, useState } from "react";
import { AnimatePresence, motion } from "framer-motion";
import {
  dismissDemo,
  fetchDemoState,
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
import { bodyState, calm, calmFast, fadeExpand, slideView, staggered } from "./lib/motion";
import {
  DEFAULT_SETTINGS,
  type ConnectionState,
  type DemoState,
  type Health,
  type Investigation,
  type MemoryItem,
  type PopupState,
  type Recovery,
  type Settings,
} from "./lib/types";
import { ContinueCard } from "./components/ContinueCard";
import { DebugStrip } from "./components/DebugStrip";
import { DemoBanner } from "./components/DemoBanner";
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
  // Phase 6D — demo overlay state. `null` while in flight; otherwise
  // the daemon's current view of `~/.recall/demo.json`. Re-fetched on
  // each `load()` so the auto-dismiss-on-real-ingest transition lands
  // smoothly on the next popup open.
  const [demo, setDemo] = useState<DemoState | null>(null);

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
    const [rec, inv, mem, dem] = await Promise.all([
      fetchRecovery(),
      fetchInvestigations(),
      fetchMemory(),
      fetchDemoState(),
    ]);
    setRecovery(rec);
    setInvestigations(inv);
    setMemory(mem);
    setDemo(dem);
    setConnection("connected");
  }, []);

  // Phase 6D — refresh just the demo slice. Called by the EmptyState's
  // *Show example* button so the overlay appears without a full
  // reload that would refetch health / recovery / threads.
  const reloadDemo = useCallback(async () => {
    setDemo(await fetchDemoState());
  }, []);

  const onDemoDismiss = useCallback(async () => {
    await dismissDemo();
    setDemo(await fetchDemoState());
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

  // Alt+D toggles the DebugStrip. The "1" hotkey fires Resume on the
  // visible recovery card (Phase 5I quick-resume). Both captured at
  // the window level so they work no matter where focus is inside the
  // popup; both cleaned up on unmount.
  useEffect(() => {
    function onKey(e: KeyboardEvent) {
      // Alt+D — toggle debug strip.
      if (e.altKey && (e.code === "KeyD" || e.key.toLowerCase() === "d")) {
        e.preventDefault();
        setDebugVisible((v) => {
          const next = !v;
          if (typeof chrome !== "undefined" && chrome.storage?.local) {
            chrome.storage.local.set({ [DEBUG_PREF_KEY]: next });
          }
          return next;
        });
        return;
      }
      // "1" — quick-resume the recovery card if one is showing.
      // Modifier-less; skipped when the user is typing in a real
      // input (the popup currently has none, but the guard is cheap).
      if (
        !e.altKey && !e.ctrlKey && !e.metaKey && !e.shiftKey &&
        e.key === "1" &&
        !(e.target instanceof HTMLInputElement) &&
        !(e.target instanceof HTMLTextAreaElement)
      ) {
        if (recovery) {
          e.preventDefault();
          recovery.urls.forEach(openTab);
        }
      }
    }
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [recovery]);

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
            connection={connection}
            health={health}
            onRetry={() => load(true)}
          />
        </motion.div>
      </AnimatePresence>
    );
  }

  const state: PopupState = previewMissing
    ? "disconnected"
    : (forced as PopupState | null) ??
      derivePopupState(connection, health, recovery, investigations, memory, demo);

  return (
    <motion.div
      key="main"
      variants={slideView}
      initial="center"
      animate="center"
      transition={calm}
      style={{ display: "flex", flexDirection: "column", flex: 1 }}
    >
      <Header
        connection={connection}
        todayCount={health?.eventsToday ?? 0}
        onSettings={() => setView("settings")}
      />
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
            demo={demo}
            onResume={onResume}
            onRetry={() => load(true)}
            onDemoActivate={reloadDemo}
            onDemoDismiss={onDemoDismiss}
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
  demo: DemoState | null = null,
): PopupState {
  if (connection === "offline") return "offline";
  if (connection === "loading") return "loading";
  if (connection === "reconnecting") return "reconnecting";
  if (connection === "disconnected" || !health) return "disconnected";
  if (recovery) return "recovery";
  if (investigations.length > 0) return "investigations";
  if (health.ingestedTotal > 0 || memory.length > 0) return "capturing";
  // Phase 6D — at this point the engine is empty. The demo overlay
  // wins only when the user clicked Show example AND the daemon
  // has not already auto-dismissed it on a real ingest.
  if (demo?.state === "active" && demo.payload) return "demo";
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

/**
 * A 6 px dot next to the wordmark. When the daemon is connected it
 * breathes (opacity 0.5 → 1 → 0.5 over 1.6 s, looping) so the user
 * has a passive live-signal that capture is on. When disconnected /
 * reconnecting / offline / loading it stops pulsing - a still dot
 * is the correct visual for "not flowing right now".
 */
function DaemonPulse({
  connection,
  color,
}: {
  connection: ConnectionState;
  color: string;
}) {
  const alive = connection === "connected";
  return (
    <motion.span
      title={connection}
      role="status"
      aria-label={`daemon ${connection}`}
      animate={alive ? { opacity: [0.5, 1, 0.5] } : { opacity: 1 }}
      transition={
        alive
          ? { duration: 1.6, repeat: Infinity, ease: "easeInOut" }
          : { duration: 0 }
      }
      style={{
        width: 6,
        height: 6,
        borderRadius: 3,
        background: color,
        marginLeft: 2,
      }}
    />
  );
}


function Header({
  connection,
  todayCount,
  onSettings,
}: {
  connection: ConnectionState;
  todayCount: number;
  onSettings: () => void;
}) {
  const dot =
    connection === "connected"
      ? "var(--ok)"
      : connection === "disconnected" || connection === "reconnecting"
        ? "var(--warn)"
        : "var(--ink-4)";

  const showCount = connection === "connected" && todayCount > 0;

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
      <DaemonPulse connection={connection} color={dot} />
      {/* Phase 6C - small "N today" count next to the pulse. Real data:
          health.eventsToday from /v1/health. Shown only when daemon is
          connected and the count is non-zero; otherwise the slot is
          quiet. */}
      {showCount && (
        <motion.span
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.18, ease: "easeOut" }}
          aria-label={`${todayCount} events today`}
          style={{
            marginLeft: 4,
            fontSize: 10.5,
            color: "var(--ink-4)",
            fontFamily:
              "ui-monospace, SFMono-Regular, Menlo, Consolas, monospace",
            letterSpacing: "0.2px",
          }}
        >
          {todayCount.toLocaleString()} today
        </motion.span>
      )}
      <span style={{ flex: 1 }} />
      {/* Phase 6C repair icon. Opens Settings (which holds the Phase
          5K Connection drawer + repair affordances). The icon is the
          left of the two icon-buttons. */}
      <motion.button
        whileHover={{ y: -1 }}
        transition={calm}
        onClick={onSettings}
        aria-label="Repair"
        title="Connection + repair"
        style={{ display: "flex", color: "var(--ink-3)", padding: 2 }}
      >
        <Icon.wrench size={16} />
      </motion.button>
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
  demo,
  onResume,
  onRetry,
  onDemoActivate,
  onDemoDismiss,
}: {
  state: PopupState;
  health: Health | null;
  recovery: Recovery | null;
  investigations: Investigation[];
  memory: MemoryItem[];
  paused: boolean;
  everConnected: boolean;
  demo: DemoState | null;
  onResume: () => void;
  onRetry: () => void;
  onDemoActivate: () => void;
  onDemoDismiss: () => void;
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
      return (
        <EmptyState
          onDemoStarted={onDemoActivate}
          onDemoDeclined={onDemoActivate}
        />
      );
    case "demo":
      /* Phase 6D — render the demo overlay using the same connected
         body as a real populated popup. The payload's `recovery`,
         `investigations`, and `timeline` plug into the existing
         render path; the only addition is the DemoBanner up top
         (trust statement + Dismiss). */
      return (
        <ConnectedBody
          recovery={demo?.payload?.recovery ?? null}
          investigations={demo?.payload?.investigations ?? []}
          memory={demo?.payload?.timeline ?? []}
          paused={paused}
          eventsToday={0}
          onResume={() => {
            demo?.payload?.recovery.urls.forEach(openTab);
          }}
          banner={
            demo?.payload?.trust ? (
              <DemoBanner
                title={demo.payload.trust.bannerTitle}
                body={demo.payload.trust.bannerBody}
                onDismiss={onDemoDismiss}
              />
            ) : null
          }
        />
      );
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
  banner,
}: {
  recovery: Recovery | null;
  investigations: Investigation[];
  memory: MemoryItem[];
  paused: boolean;
  eventsToday: number;
  onResume: () => void;
  /* Phase 6D — optional trust banner rendered above the Continue
     card. Used by the demo overlay to declare "Example data —
     Nothing here came from your device." */
  banner?: React.ReactNode;
}) {
  let index = 0;
  return (
    <div className="scroll-area" style={{ flex: 1, padding: "20px 0 8px" }}>
      {banner}
      {recovery && (
        /* Phase 6C: the Continue card is the popup's hero, so we drop
           the outer Section's "CONTINUE" label — the card already
           owns that header with its own accent dot. Animation matches
           a normal Section so the entry stagger is unchanged. */
        <motion.section
          variants={fadeExpand}
          initial="hidden"
          animate="show"
          transition={staggered(index++)}
          className="section"
          style={{ marginBottom: "var(--gap-section)" }}
        >
          <ContinueCard recovery={recovery} onResume={onResume} />
        </motion.section>
      )}

      {investigations.length > 0 && (
        <Section
          label="Active investigations"
          count={`${investigations.length}`}
          index={index++}
        >
          {/* Phase 6C: horizontal pill strip — max four pills, never
              a full feed. Wraps cleanly inside the 360 px popup. */}
          <div
            style={{
              display: "flex",
              flexWrap: "wrap",
              gap: 7,
              padding: "2px 0",
            }}
          >
            {investigations.slice(0, 4).map((inv, i) => (
              <InvestigationCard
                key={inv.id}
                investigation={inv}
                index={i}
              />
            ))}
          </div>
        </Section>
      )}

      {memory.length > 0 && (
        <Section label="Today" index={index++}>
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
