import { motion } from "framer-motion";
import { calmFast } from "../lib/motion";
import type { Recovery } from "../lib/types";
import { Icon } from "./icons";


/**
 * Phase 6C — UI-side mapping from total work count to a confidence
 * band. Mirrors the launcher's `derive_recovery_confidence(n_targets)`
 * exactly: ≥ 4 → high, 2-3 → medium, 0-1 → low.
 * No engine-side trust field; pure display.
 */
function _deriveConfidence(tabCount: number, fileCount: number): string {
  const n = tabCount + fileCount;
  if (n >= 4) return "high";
  if (n >= 2) return "medium";
  return "low";
}


/** Inline pill matching the launcher's `_ConfidenceBadge`. Three
 *  bands with the same colour vocabulary across both surfaces. */
function ConfidencePill({ level }: { level: string }) {
  const palette: Record<string, { fg: string; bg: string; label: string }> = {
    high: { fg: "var(--accent)", bg: "var(--accent-soft)", label: "high" },
    medium: { fg: "var(--warn)", bg: "rgba(201, 138, 94, 0.16)", label: "med" },
    low: { fg: "var(--ink-3)", bg: "var(--surface-2)", label: "low" },
  };
  const p = palette[level] ?? palette.high;
  return (
    <span
      aria-label={`confidence ${level}`}
      style={{
        display: "inline-flex",
        alignItems: "center",
        height: 16,
        padding: "0 7px",
        borderRadius: 4,
        background: p.bg,
        color: p.fg,
        fontSize: 9.5,
        fontWeight: 600,
        letterSpacing: "0.3px",
      }}
    >
      {p.label}
    </span>
  );
}


/** Reduce a URL to its short host, dropping `www.`. */
function _hostOf(url: string): string {
  try {
    const u = new URL(url);
    return u.host.replace(/^www\./, "");
  } catch {
    return url;
  }
}


/**
 * Phase 5J resume preview. Renders up to four unique domains the
 * Resume click is about to reopen, in mono font, plus a "+N more"
 * tail when the candidate has more URLs than fit. Real data only -
 * the popup never invents a domain; if `recovery.urls` is empty
 * (a file-only recovery) the preview renders nothing.
 */
function ResumePreview({ urls }: { urls: string[] }) {
  if (urls.length === 0) return null;
  const hosts = Array.from(new Set(urls.map(_hostOf))).filter(Boolean);
  const head = hosts.slice(0, 4);
  const extra = hosts.length - head.length;
  return (
    <div
      style={{
        marginTop: 10,
        fontSize: 10.5,
        lineHeight: 1.45,
        color: "var(--ink-3)",
        fontFamily:
          "ui-monospace, SFMono-Regular, Menlo, Consolas, monospace",
        wordBreak: "break-all",
      }}
    >
      {head.join("  ·  ")}
      {extra > 0 && (
        <span style={{ color: "var(--ink-4)" }}>{`  ·  +${extra} more`}</span>
      )}
    </div>
  );
}

/**
 * The popup's hero. One card, one investigation — the single
 * strongest interrupted thread the daemon found. Not a list, not a
 * feed: the answer to "what was I doing?" the moment the popup opens.
 *
 * The card is accent-tinted so it reads as *the* thing to act on,
 * but it stays calm — soft fill, one button, no glow.
 */
export function ContinueCard({
  recovery,
  onResume,
}: {
  recovery: Recovery;
  onResume: () => void;
}) {
  // The caption chips that describe *return intent* (a gap, a
  // revisit) — the trust cue for "why this surfaced".
  const reason = recovery.chips.find(
    (c) => /gap|revisit|interrupt/i.test(c),
  );

  return (
    <div
      className="card"
      style={{
        background: "var(--accent-soft)",
        borderColor: "var(--accent-line)",
        padding: "16px 16px 14px",
      }}
    >
      <div
        style={{
          display: "flex",
          alignItems: "center",
          gap: 7,
          fontSize: 10,
          fontWeight: 600,
          letterSpacing: "0.9px",
          textTransform: "uppercase",
          color: "var(--accent)",
        }}
      >
        <span
          style={{
            width: 6,
            height: 6,
            borderRadius: 3,
            background: "var(--accent)",
          }}
        />
        Continue
        <span style={{ marginLeft: "auto" }}>
          <ConfidencePill
            level={_deriveConfidence(recovery.tabCount, recovery.fileCount)}
          />
        </span>
      </div>

      <div
        style={{
          marginTop: 9,
          fontSize: 15,
          fontWeight: 600,
          lineHeight: 1.3,
          color: "var(--ink)",
        }}
      >
        {recovery.title}
      </div>

      <div
        style={{
          display: "flex",
          flexWrap: "wrap",
          gap: 6,
          marginTop: 11,
        }}
      >
        {recovery.tabCount > 0 && (
          <span className="chip">
            <Icon.tab size={12} />
            <span style={{ marginLeft: 5 }}>
              {recovery.tabCount} tab{recovery.tabCount === 1 ? "" : "s"}
            </span>
          </span>
        )}
        {recovery.fileCount > 0 && (
          <span className="chip">
            <Icon.file size={12} />
            <span style={{ marginLeft: 5 }}>
              {recovery.fileCount} file{recovery.fileCount === 1 ? "" : "s"}
            </span>
          </span>
        )}
        {reason && <span className="chip accent">{reason}</span>}
      </div>

      {/* Phase 5J: a small resume preview of the actual domains
          that will reopen. Real data from recovery.urls (no
          placeholders); dropped silently if no URLs are
          attached (file-only recoveries). */}
      <ResumePreview urls={recovery.urls} />

      <div
        style={{
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
          gap: 12,
          marginTop: 14,
        }}
      >
        <span
          style={{
            fontSize: 11,
            color: "var(--ink-3)",
            lineHeight: 1.45,
          }}
        >
          Surfaced because you left this mid-flow.
        </span>
        <motion.button
          whileHover={{ y: -1 }}
          whileTap={{ y: 0 }}
          transition={calmFast}
          onClick={onResume}
          aria-keyshortcuts="1"
          title="Resume (press 1)"
          style={{
            display: "inline-flex",
            alignItems: "center",
            gap: 6,
            flexShrink: 0,
            height: 34,
            padding: "0 14px 0 16px",
            borderRadius: 9,
            background: "var(--accent)",
            color: "#fff",
            fontSize: 13,
            fontWeight: 600,
          }}
        >
          <Icon.resume size={15} />
          Resume
          <span
            aria-hidden
            style={{
              marginLeft: 4,
              padding: "1px 5px",
              borderRadius: 4,
              background: "rgba(255,255,255,0.18)",
              fontSize: 10,
              fontWeight: 600,
              letterSpacing: "0.3px",
            }}
          >
            1
          </span>
        </motion.button>
      </div>
    </div>
  );
}
