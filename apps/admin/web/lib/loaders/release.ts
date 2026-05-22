import path from "node:path";
import { ADMIN_DATA_DIR, RELEASE_STATE } from "./paths";
import { fileMtime, readJSON, type Verdict } from "./fsx";

/**
 * Release-state reader. The dashboard's *Release Center* panel
 * pulls from two files:
 *
 *   - `apps/admin/release_state.json`        — long-lived per-gate state
 *     (installer ready / signed / mac / screenshots / alpha packet /
 *     go-no-go verdict).
 *   - `apps/admin/data/release.json`         — baked summary the founder
 *     CLI consumes too; backup source.
 *
 * Both shapes are tolerated; the loader normalises them onto a
 * single `ReleaseStatus` envelope.
 */

export interface ReleaseStatus {
  current_version: string;
  next_milestone: string;
  installer: "ready" | "blocked" | "partial" | "unknown";
  mac: "supported" | "preview" | "source-only" | "unknown";
  signing: "signed" | "unsigned" | "unknown";
  screenshots: "complete" | "partial" | "missing" | "unknown";
  alpha_packet: "ready" | "partial" | "missing" | "unknown";
  go_no_go: "GO" | "PARTIAL" | "NO-GO" | "UNKNOWN";
  blocked: string[];
  progress?: { label: string; pct: number; verdict: Verdict }[];
  source_mtime: string | null;
}

function _normalise(raw: Partial<ReleaseStatus> | null): Partial<ReleaseStatus> {
  if (!raw || typeof raw !== "object") return {};
  return raw;
}

function _verdictForGate(value: string | undefined): Verdict {
  if (!value || value === "unknown") return "yellow";
  if (["ready", "signed", "complete", "supported", "GO"].includes(value)) return "green";
  if (["partial", "preview", "PARTIAL"].includes(value)) return "yellow";
  return "red";
}

export async function loadRelease(): Promise<ReleaseStatus> {
  const stateRaw = await readJSON<Partial<ReleaseStatus>>(RELEASE_STATE, {});
  const bakedPath = path.join(ADMIN_DATA_DIR, "release.json");
  const baked = await readJSON<Partial<ReleaseStatus>>(bakedPath, {});

  // State file wins where it has a value; baked fills the gaps.
  const merged: Partial<ReleaseStatus> = {
    ..._normalise(baked),
    ..._normalise(stateRaw),
  };

  const out: ReleaseStatus = {
    current_version: merged.current_version || "unreleased",
    next_milestone: merged.next_milestone || "—",
    installer: (merged.installer as ReleaseStatus["installer"]) || "unknown",
    mac: (merged.mac as ReleaseStatus["mac"]) || "unknown",
    signing: (merged.signing as ReleaseStatus["signing"]) || "unknown",
    screenshots: (merged.screenshots as ReleaseStatus["screenshots"]) || "unknown",
    alpha_packet: (merged.alpha_packet as ReleaseStatus["alpha_packet"]) || "unknown",
    go_no_go: (merged.go_no_go as ReleaseStatus["go_no_go"]) || "UNKNOWN",
    blocked: Array.isArray(merged.blocked) ? merged.blocked : [],
    source_mtime: null,
  };

  // Derive a per-gate progress strip if the source didn't ship one.
  out.progress = [
    { label: "installer", value: out.installer },
    { label: "signing", value: out.signing },
    { label: "mac", value: out.mac },
    { label: "screenshots", value: out.screenshots },
    { label: "alpha packet", value: out.alpha_packet },
  ].map(({ label, value }) => ({
    label,
    verdict: _verdictForGate(value),
    pct:
      value === "ready" || value === "complete" || value === "signed" || value === "supported"
        ? 100
        : value === "partial" || value === "preview" ? 60 : value === "unknown" ? 0 : 20,
  }));

  out.source_mtime = await fileMtime(RELEASE_STATE);
  return out;
}
