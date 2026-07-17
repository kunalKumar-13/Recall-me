import { useCallback, useEffect, useState } from "react";
import { AnimatePresence, motion } from "framer-motion";
import {
  dismissDemo,
  fetchDemoState,
  fetchHealth,
  fetchInvestigations,
  fetchMemory,
  fetchHours,
  fetchRecovery,
  fetchToday,
  getQueuedCount,
  isOnline,
  loadSettings,
  markConnected,
  openTab,
  saveSettings,
  wasEverConnected,
} from "./lib/api";
import { calm, slideView } from "./lib/motion";
import { getPauseUntil, restoreRecovery, setPauseUntil } from "./lib/api";
import type { Recovery as RecoveryT } from "./lib/types";

/** Resume through the engine's choreographed plan; fall back to the
 *  candidate's raw suggested URLs when the daemon can't answer. */
async function resumeRecovery(recovery: RecoveryT): Promise<void> {
  const plan = await restoreRecovery(recovery.id);
  if (!plan) recovery.urls.forEach(openTab);
}
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
  type TodaySummary,
} from "./lib/types";
import { SettingsPanel } from "./components/SettingsPanel";
import { Header } from "./components/v2/Header";
import { SearchOverlay } from "./components/v2/SearchOverlay";
import {
  DisconnectedPlate,
  EmptyPlate,
  LoadingPlate,
  OfflinePlate,
  ReconnectingPlate,
} from "./components/v2/States";
import { MainV3 } from "./components/v3/Main";

/**
 * Phase 7A — the premium extension surface. Six fixed-position
 * regions in a single 440×640 popup:
 *
 *   1. Header        — mark + daemon dot + Search/Settings buttons
 *   2. Continue hero — full-width recovery card when one exists
 *   3. Investigations— stacked rows (max 4 visible)
 *   4. Today timeline— event rail
 *   5. Activity      — Browser + Desktop status cards
 *   6. Trust strip   — collapsed footer
 *
 *   + Search overlay (Cmd/Ctrl+K, slide-in from the top)
 *   + Settings view  (slides in from the right)
 *
 * The directive is explicit: *open extension → immediately
 * understand: Recall remembered work · Recall can continue it ·
 * Recall is running.*
 */

type View = "main" | "settings";

export function App() {
  const [connection, setConnection] = useState<ConnectionState>("loading");
  const [health, setHealth] = useState<Health | null>(null);
  const [recovery, setRecovery] = useState<Recovery | null>(null);
  const [investigations, setInvestigations] = useState<Investigation[]>([]);
  const [memory, setMemory] = useState<MemoryItem[]>([]);
  const [settings, setSettings] = useState<Settings>(DEFAULT_SETTINGS);
  const [view, setView] = useState<View>("main");
  const [everConnected, setEverConnected] = useState(true);
  const [demo, setDemo] = useState<DemoState | null>(null);
  const [searchOpen, setSearchOpen] = useState(false);
  const [queued, setQueued] = useState(0);
  const [today, setToday] = useState<TodaySummary | null>(null);
  const [hours, setHours] = useState<number[] | null>(null);

  const load = useCallback(async (reconnect = false) => {
    // Outbox depth matters most when the daemon is unreachable, so
    // read it before any early return below.
    void getQueuedCount().then(setQueued);
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
    // Capture self-check — engine-side ground truth, never a guess.
    void fetchToday().then(setToday);
    void fetchHours().then(setHours);
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
    // chrome://extensions → Extension options opens this same app in
    // a tab, deep-linked straight to Settings.
    if (window.location.hash === "#settings") {
      setView("settings");
      document.body.classList.add("options-tab");
    }
  }, [load]);

  // Cmd/Ctrl+K opens the search overlay. `1` resumes the visible
  // recovery card. Both captured at the window level so they
  // survive focus changes.
  useEffect(() => {
    function onKey(e: KeyboardEvent) {
      const cmd = e.ctrlKey || e.metaKey;
      if (cmd && (e.key === "k" || e.key === "K")) {
        e.preventDefault();
        setSearchOpen((open) => !open);
        return;
      }
      if (
        !e.altKey &&
        !e.ctrlKey &&
        !e.metaKey &&
        !e.shiftKey &&
        e.key === "1" &&
        !(e.target instanceof HTMLInputElement) &&
        !(e.target instanceof HTMLTextAreaElement)
      ) {
        if (recovery) {
          e.preventDefault();
          void resumeRecovery(recovery);
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
    if (recovery) void resumeRecovery(recovery);
  }, [recovery]);

  /* capture pause — one hour, or resume immediately */
  const [pausedUntil, setPausedUntil] = useState(0);
  useEffect(() => {
    void getPauseUntil().then(setPausedUntil);
  }, []);
  const togglePause = useCallback(() => {
    setPausedUntil((prev) => {
      const next = prev > Date.now() ? 0 : Date.now() + 60 * 60 * 1000;
      void setPauseUntil(next);
      return next;
    });
  }, []);

  const forced = readForcedState();
  const previewMissing = forced === "missing";
  const effEverConnected = previewMissing ? false : everConnected;

  // ?state=demolocal — a fully canned popup with zero daemon and
  // zero personal data. Exists for docs and marketing screenshots;
  // every value below is the same fictional day the site's demos use.
  const demoLocal = forced === "demolocal";
  const dlRecovery: Recovery | null = demoLocal
    ? {
        id: "demo",
        title: "WebSocket reconnect bug",
        caption: "2 tabs · 1 file · reopened after a 2-day gap",
        chips: ["2 tabs", "1 file", "2-day gap"],
        tabCount: 2,
        fileCount: 1,
        urls: [],
      }
    : null;
  const dlThreads: Investigation[] = demoLocal
    ? [
        { id: "t1", title: "WebSocket reconnect bug", summary: "started 3d ago · 5 sessions · 24 events", surfaces: [] },
        { id: "t2", title: "Rust async runtime research", summary: "started 1w ago · 4 sessions · 18 events", surfaces: [] },
        { id: "t3", title: "Seed deck — narrative pass", summary: "started 2w ago · 3 sessions · 11 events", surfaces: [] },
      ]
    : [];
  const dlTail: MemoryItem[] = demoLocal
    ? [
        { kind: "tab", label: "Stripe webhooks — retries", detail: "stripe.com", ts: Math.floor(Date.now() / 1000) - 240 },
        { kind: "chat", label: "retry logic — claude.ai", detail: "claude", ts: Math.floor(Date.now() / 1000) - 900 },
        { kind: "search", label: "exponential backoff jitter", detail: "google", ts: Math.floor(Date.now() / 1000) - 1500 },
        { kind: "tab", label: "docs.rs/tokio — time::interval", detail: "docs.rs", ts: Math.floor(Date.now() / 1000) - 2400 },
      ]
    : [];
  const dlToday: TodaySummary | null = demoLocal
    ? { count: 88, kinds: { browser_visit: 61, browser_focus: 12, chat_session: 7, browser_search: 5, open: 3 } }
    : null;
  const dlHours: number[] | null = demoLocal
    ? [0, 0, 0, 0, 0, 0, 0, 1, 3, 9, 12, 8, 4, 6, 11, 13, 9, 6, 4, 2, 0, 0, 0, 0]
    : null;

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
            today={today}
            pausedUntil={pausedUntil}
            onTogglePause={togglePause}
            onRetry={() => load(true)}
          />
        </motion.div>
      </AnimatePresence>
    );
  }

  const state: PopupState = previewMissing
    ? "disconnected"
    : demoLocal
      ? "recovery"
      : (forced as PopupState | null) ??
        derivePopupState(connection, health, recovery, investigations, memory, demo);
  const effConnection = demoLocal ? "connected" : connection;

  // The demo overlay reuses the live render path with the demo's
  // synthesised data — exactly like the launcher's demo branch.
  const effRecovery = demoLocal
    ? dlRecovery
    : state === "demo"
      ? demo?.payload?.recovery ?? null
      : recovery;
  const effInvestigations = demoLocal
    ? dlThreads
    : state === "demo"
      ? demo?.payload?.investigations ?? []
      : investigations;
  const effMemory = demoLocal
    ? dlTail
    : state === "demo"
      ? demo?.payload?.timeline ?? []
      : memory;
  const effOnResume =
    state === "demo"
      ? () => demo?.payload?.recovery.urls.forEach(openTab)
      : onResume;

  return (
    <div
      style={{
        display: "flex",
        flexDirection: "column",
        flex: 1,
        position: "relative",
      }}
    >
      <Header
        connection={effConnection}
        paused={pausedUntil > Date.now()}
        onPause={togglePause}
        onSearch={() => setSearchOpen(true)}
        onSettings={() => setView("settings")}
      />

      <main
        className="scroll-area"
        style={
          state === "recovery" ||
          state === "investigations" ||
          state === "capturing" ||
          state === "demo"
            ? { flex: 1, display: "flex", flexDirection: "column", overflowY: "auto", overflowX: "hidden" }
            : {
                flex: 1,
                display: "flex",
                flexDirection: "column",
                gap: "var(--gap-section)",
                padding: "16px 0 12px",
                overflowY: "auto",
                overflowX: "hidden",
              }
        }
      >
        {state === "loading" && <LoadingPlate />}
        {state === "reconnecting" && <ReconnectingPlate />}
        {state === "offline" && <OfflinePlate onRetry={() => load(true)} />}
        {state === "disconnected" && (
          <DisconnectedPlate
            everConnected={effEverConnected}
            onRetry={() => load(true)}
          />
        )}
        {state === "empty" && (
          <EmptyPlate
            onShowExample={reloadDemo}
            onStartWorking={reloadDemo}
          />
        )}

        {(state === "recovery" ||
          state === "investigations" ||
          state === "capturing" ||
          state === "demo") && (
          <>
            <MainV3
              connection={effConnection}
              recovery={effRecovery}
              threads={effInvestigations}
              tail={effMemory}
              today={demoLocal ? dlToday : state === "demo" ? null : today}
              hours={demoLocal ? dlHours : state === "demo" ? null : hours}
              queued={demoLocal ? 0 : queued}
              onResume={effOnResume}
            />
            {state === "demo" && demo?.payload?.trust && (
              <DemoBannerInline
                title={demo.payload.trust.bannerTitle}
                body={demo.payload.trust.bannerBody}
                onDismiss={onDemoDismiss}
              />
            )}
          </>
        )}
      </main>

      <SearchOverlay
        open={searchOpen}
        onClose={() => setSearchOpen(false)}
        recovery={effRecovery}
        investigations={effInvestigations}
        memory={effMemory}
      />
    </div>
  );
}

// ── state machine ───────────────────────────────────────────────────

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
  if (demo?.state === "active" && demo.payload) return "demo";
  return "empty";
}

function readForcedState(): string | null {
  if (typeof location === "undefined") return null;
  return new URLSearchParams(location.search).get("state");
}

// ── inline demo banner ──────────────────────────────────────────────

function DemoBannerInline({
  title,
  body,
  onDismiss,
}: {
  title: string;
  body: string;
  onDismiss: () => void;
}) {
  return (
    <section
      style={{
        margin: "0 var(--pad-edge)",
        padding: "10px 14px",
        background: "var(--accent-soft)",
        border: "1px solid var(--accent-line)",
        borderRadius: "var(--radius-card)",
        display: "flex",
        alignItems: "center",
        gap: 10,
      }}
    >
      <span
        aria-hidden
        style={{
          width: 8,
          height: 8,
          borderRadius: 4,
          background: "var(--accent)",
          flexShrink: 0,
        }}
      />
      <div style={{ flex: 1, minWidth: 0 }}>
        <div
          style={{
            fontSize: 11,
            fontWeight: 600,
            color: "var(--ink-2)",
          }}
        >
          {title}
        </div>
        <div style={{ fontSize: 10.5, color: "var(--ink-3)" }}>{body}</div>
      </div>
      <button
        onClick={onDismiss}
        style={{
          fontSize: 11,
          fontWeight: 600,
          color: "var(--accent)",
          padding: "4px 6px",
          background: "transparent",
          cursor: "pointer",
        }}
      >
        Dismiss
      </button>
    </section>
  );
}
