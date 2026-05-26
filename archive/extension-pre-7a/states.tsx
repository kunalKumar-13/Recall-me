import { useState } from "react";
import { motion } from "framer-motion";
import { activateDemo, dismissDemo, openRecall, openTab } from "../lib/api";
import { calm, fade } from "../lib/motion";
import type { MemoryItem } from "../lib/types";
import { MemoryList } from "./MemoryList";

const DOWNLOADS_URL =
  "https://github.com/kunalKumar-13/Recall-me/releases/latest";

/**
 * Every non-normal state of the popup, each a calm full-body screen.
 * A memory surface is most fragile exactly here — when it has
 * nothing, or can't reach the daemon — so these states are written
 * to reassure, never to alarm. No red, no error iconography, no
 * "something went wrong". Just a quiet, honest sentence.
 *
 * Exported individually so they can be previewed in isolation
 * (storybook-style) — see `App.tsx`'s `?state=` switch.
 */

function Shell({
  badge,
  title,
  body,
  action,
}: {
  badge: React.ReactNode;
  title: string;
  body: string;
  action?: React.ReactNode;
}) {
  return (
    <motion.div
      variants={fade}
      initial="hidden"
      animate="show"
      transition={calm}
      style={{
        flex: 1,
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        justifyContent: "center",
        textAlign: "center",
        padding: "44px 36px",
        gap: 4,
      }}
    >
      {badge}
      <div
        style={{
          marginTop: 14,
          fontSize: 14,
          fontWeight: 600,
          color: "var(--ink)",
        }}
      >
        {title}
      </div>
      <div
        style={{
          fontSize: 12,
          lineHeight: 1.55,
          color: "var(--ink-3)",
          maxWidth: 280,
        }}
      >
        {body}
      </div>
      {action && <div style={{ marginTop: 16 }}>{action}</div>}
    </motion.div>
  );
}

function Badge({
  color = "var(--accent)",
  pulse = false,
}: {
  color?: string;
  pulse?: boolean;
}) {
  return (
    <motion.span
      animate={pulse ? { opacity: [0.4, 1, 0.4] } : { opacity: 1 }}
      transition={
        pulse
          ? { duration: 1.6, repeat: Infinity, ease: "easeInOut" }
          : calm
      }
      style={{
        width: 38,
        height: 38,
        borderRadius: 12,
        background: "var(--accent-soft)",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
      }}
    >
      <span
        style={{
          width: 10,
          height: 10,
          borderRadius: 5,
          background: color,
        }}
      />
    </motion.span>
  );
}

function PrimaryButton({
  label,
  onClick,
  disabled = false,
}: {
  label: string;
  onClick: () => void;
  disabled?: boolean;
}) {
  return (
    <motion.button
      whileHover={disabled ? undefined : { y: -1 }}
      whileTap={disabled ? undefined : { y: 0 }}
      transition={calm}
      onClick={disabled ? undefined : onClick}
      disabled={disabled}
      style={{
        height: 34,
        padding: "0 18px",
        borderRadius: 9,
        background: disabled ? "var(--ink-4)" : "var(--accent)",
        color: "#fff",
        fontSize: 13,
        fontWeight: 600,
        cursor: disabled ? "default" : "pointer",
        opacity: disabled ? 0.7 : 1,
      }}
    >
      {label}
    </motion.button>
  );
}

function SecondaryButton({
  label,
  onClick,
}: {
  label: string;
  onClick: () => void;
}) {
  return (
    <button
      onClick={onClick}
      style={{
        fontSize: 11.5,
        color: "var(--ink-3)",
        padding: "4px 6px",
      }}
    >
      {label}
    </button>
  );
}

/** A primary action over an optional quiet secondary one. */
function Actions({ children }: { children: React.ReactNode }) {
  return (
    <div
      style={{
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        gap: 4,
      }}
    >
      {children}
    </div>
  );
}

export function LoadingState() {
  return (
    <Shell
      badge={<Badge pulse />}
      title="Picking up where you were"
      body="Reading the local daemon…"
    />
  );
}

export function ReconnectingState() {
  return (
    <Shell
      badge={<Badge pulse color="var(--warn)" />}
      title="Reconnecting"
      body="Looking for the Recall daemon on this machine…"
    />
  );
}

/**
 * The "Open Recall" CTA used by the disconnected screen. Wraps
 * `openRecall()` (the three-rung ladder in `lib/api.ts`) with
 * visible feedback - the label changes for the duration of the
 * launch attempt and surfaces the repair path if the dispatch
 * could not even reach the OS. The "never dead click" rule lives
 * here: every click changes pixels.
 */
function OpenRecallButton({
  onAttemptComplete,
}: {
  onAttemptComplete: () => void;
}) {
  type Phase = "idle" | "trying" | "repair" | "hint";
  const [phase, setPhase] = useState<Phase>("idle");

  async function click() {
    setPhase("trying");
    const outcome = await openRecall();
    if (outcome === "repair") {
      setPhase("repair");
      return;
    }
    // Dispatch fired; the OS may or may not have a handler. Re-probe
    // after a short delay so the caller can flip to "connected" if
    // Recall actually came up.
    setTimeout(() => {
      onAttemptComplete();
      // If we are still in `trying` 2 s later, the protocol almost
      // certainly silently dropped. Show the hint, never a dead click.
      setPhase((p) => (p === "trying" ? "hint" : p));
    }, 2000);
  }

  if (phase === "repair") {
    return (
      <Actions>
        <PrimaryButton
          label="Open the downloads page"
          onClick={() => openTab(DOWNLOADS_URL)}
        />
        <span style={{ fontSize: 11, color: "var(--ink-3)", maxWidth: 260 }}>
          Your browser does not have the recall:// handler. Reinstalling
          Recall (or opening the desktop app once) registers it.
        </span>
      </Actions>
    );
  }
  if (phase === "hint") {
    return (
      <Actions>
        <PrimaryButton label="Try again" onClick={click} />
        <span style={{ fontSize: 11, color: "var(--ink-3)", maxWidth: 260 }}>
          Recall did not respond. If it is installed, try opening it
          from your desktop shortcut; if not,{" "}
          <a
            onClick={() => openTab(DOWNLOADS_URL)}
            style={{ color: "var(--accent)", cursor: "pointer" }}
          >
            install it here
          </a>
          .
        </span>
      </Actions>
    );
  }
  return (
    <PrimaryButton
      label={phase === "trying" ? "Opening Recall…" : "Open Recall"}
      onClick={click}
      disabled={phase === "trying"}
    />
  );
}

/**
 * The disconnected screen, pairing-aware. If the daemon has never
 * answered on this profile, Recall is probably not installed — lead
 * with **Install Recall**. If it has answered before, Recall is
 * installed but not running — lead with **Open Recall**, with
 * **Repair connection** as the quiet fallback.
 */
export function DisconnectedState({
  everConnected,
  onRetry,
}: {
  everConnected: boolean;
  onRetry: () => void;
}) {
  if (!everConnected) {
    return (
      <Shell
        badge={<Badge color="var(--accent)" />}
        title="Recall isn't installed yet"
        body="Recall is a small desktop app that runs entirely on your machine. Install it once, and this popup comes alive."
        action={
          <Actions>
            <PrimaryButton
              label="Install Recall"
              onClick={() => openTab(DOWNLOADS_URL)}
            />
            <SecondaryButton
              label="Already installed it — try again"
              onClick={onRetry}
            />
          </Actions>
        }
      />
    );
  }
  return (
    <Shell
      badge={<Badge color="var(--warn)" />}
      title="Recall isn't running"
      body="Capture continues in the background — your memory is safe. Open the desktop app to see it here."
      action={
        <Actions>
          <OpenRecallButton onAttemptComplete={onRetry} />
          <SecondaryButton label="Repair connection" onClick={onRetry} />
        </Actions>
      }
    />
  );
}

export function OfflineState({ onRetry }: { onRetry: () => void }) {
  return (
    <Shell
      badge={<Badge color="var(--ink-4)" />}
      title="You're offline"
      body="That's fine — Recall is local-first and never needed the network. This popup will reconnect to the daemon on its own."
      action={
        <Actions>
          <PrimaryButton label="Try again" onClick={onRetry} />
        </Actions>
      }
    />
  );
}

/**
 * Empty state — the popup's *honest zero*. Phase 6C carried the
 * launcher's headline / body across; Phase 6D pairs the *Show
 * example* pill with a quieter *Start normally* secondary so the
 * empty surface mirrors the launcher's two-button choice exactly.
 *
 * Behaviour:
 *   - *Show example* → `activateDemo()` (POST `/v1/demo/activate`).
 *     The parent re-fetches demo state and swaps the popup into
 *     the demo overlay; the engine itself never sees a synthetic
 *     event.
 *   - *Start normally* → `dismissDemo()` so the choice persists,
 *     and the popup stays on this empty state until real events
 *     arrive.
 *
 * Reachable only when daemon=ok AND ingestedTotal=0 AND memory=∅
 * AND demo state ≠ "active". The state machine in `App.tsx` enforces
 * this invariant.
 */
export function EmptyState({
  onDemoStarted,
  onDemoDeclined,
}: {
  onDemoStarted?: () => void;
  onDemoDeclined?: () => void;
} = {}) {
  const [busy, setBusy] = useState<null | "demo" | "decline">(null);

  async function handleShowExample() {
    setBusy("demo");
    await activateDemo();
    setBusy(null);
    onDemoStarted?.();
  }

  async function handleStartNormally() {
    setBusy("decline");
    await dismissDemo();
    setBusy(null);
    onDemoDeclined?.();
  }

  return (
    <motion.div
      variants={fade}
      initial="hidden"
      animate="show"
      transition={calm}
      style={{
        flex: 1,
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        textAlign: "center",
        padding: "48px 28px 26px",
        gap: 12,
      }}
    >
      <Badge />
      <div
        style={{
          marginTop: 6,
          fontSize: 15,
          fontWeight: 600,
          color: "var(--ink)",
          lineHeight: 1.3,
        }}
      >
        Recall notices unfinished work.
      </div>
      <div
        style={{
          fontSize: 12.5,
          lineHeight: 1.6,
          color: "var(--ink-3)",
          maxWidth: 280,
        }}
      >
        Work normally. Return later.
        <br />
        Recall fills itself.
      </div>
      <div
        style={{
          marginTop: 14,
          display: "flex",
          gap: 8,
          alignItems: "center",
          justifyContent: "center",
        }}
      >
        <motion.button
          whileHover={busy ? undefined : { y: -1 }}
          whileTap={busy ? undefined : { y: 0 }}
          transition={calm}
          onClick={busy ? undefined : handleShowExample}
          disabled={busy !== null}
          style={{
            height: 32,
            padding: "0 16px",
            borderRadius: 16,
            background: "var(--accent-soft)",
            color: "var(--accent)",
            fontSize: 12,
            fontWeight: 600,
            border: "1px solid var(--accent-line)",
            cursor: busy ? "default" : "pointer",
            opacity: busy === "decline" ? 0.55 : 1,
          }}
        >
          {busy === "demo" ? "Loading…" : "Show example"}
        </motion.button>
        <motion.button
          whileHover={busy ? undefined : { y: -1 }}
          whileTap={busy ? undefined : { y: 0 }}
          transition={calm}
          onClick={busy ? undefined : handleStartNormally}
          disabled={busy !== null}
          style={{
            height: 32,
            padding: "0 14px",
            borderRadius: 16,
            background: "transparent",
            color: "var(--ink-3)",
            fontSize: 12,
            fontWeight: 500,
            border: "1px solid var(--border-soft)",
            cursor: busy ? "default" : "pointer",
            opacity: busy === "demo" ? 0.55 : 1,
          }}
        >
          Start normally
        </motion.button>
      </div>
      <div
        style={{
          marginTop: 12,
          fontSize: 10.5,
          color: "var(--ink-4)",
          fontFamily:
            "ui-monospace, SFMono-Regular, Menlo, Consolas, monospace",
        }}
      >
        local only · 127.0.0.1:4545 · no cloud
      </div>
    </motion.div>
  );
}

/**
 * Capturing state — daemon healthy, events flowing in, no
 * investigation yet. Phase 5H surface; replaces the prior "everything
 * empty" fallback that read as broken.
 *
 * Three layers:
 *   1. Reassurance line ("Recall is watching locally" + event count).
 *   2. A real recent-activity preview from the event store, up to
 *      five rows. Reuses `MemoryList` so the row visual is exactly
 *      the same one the user sees later in the INVESTIGATIONS / RECOVERY
 *      states - one rendering, one truth.
 *   3. Fallback copy if the recent-activity list is empty (the
 *      daemon counts events but the popup's /v1/events/recent
 *      returned nothing - cache, ordering, or a stale read).
 *
 * No CTA. The user is mid-flow; the popup's job here is *not to
 * interrupt*.
 */
export function CapturingState({
  ingestedTotal,
  memory,
}: {
  ingestedTotal: number;
  memory: MemoryItem[];
}) {
  const eventLine =
    ingestedTotal === 1
      ? "1 event captured"
      : `${ingestedTotal.toLocaleString()} events captured`;
  return (
    <motion.div
      variants={fade}
      initial="hidden"
      animate="show"
      transition={calm}
      style={{
        flex: 1,
        display: "flex",
        flexDirection: "column",
        padding: "26px 18px 14px",
        gap: 14,
      }}
    >
      <div
        style={{
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          gap: 8,
        }}
      >
        <Badge color="var(--ok)" />
        <div style={{ fontSize: 14, fontWeight: 600, color: "var(--ink)" }}>
          Recall is watching locally
        </div>
        <div style={{ fontSize: 12, color: "var(--ink-3)" }}>{eventLine}</div>
      </div>

      <div
        style={{
          fontSize: 10,
          fontWeight: 600,
          letterSpacing: "0.9px",
          textTransform: "uppercase",
          color: "var(--ink-3)",
          padding: "0 6px",
        }}
      >
        Recent activity
      </div>

      {memory.length > 0 ? (
        <MemoryList items={memory.slice(0, 5)} />
      ) : (
        <div
          style={{
            background: "var(--surface)",
            border: "1px dashed var(--line-strong)",
            borderRadius: 12,
            padding: "12px 14px",
            color: "var(--ink-3)",
            fontSize: 11.5,
            lineHeight: 1.55,
          }}
        >
          Counters are moving but the activity stream hasn't refreshed
          yet. Recall is capturing in the background; this list fills
          on the next read.
        </div>
      )}
    </motion.div>
  );
}
