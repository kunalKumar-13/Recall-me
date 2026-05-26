import "./globals.css";
import type { Metadata } from "next";
import { ActionsBar } from "../components/ActionsBar";
import { BottomBar, type BottomBarStats } from "../components/BottomBar";
import { Nav } from "../components/Nav";
import { ShellClient } from "../components/ShellClient";
import type { TopBarStats } from "../components/TopBar";
import { loadAlpha, loadRelease, loadSystemSnapshot } from "../lib/loaders";

export const metadata: Metadata = {
  title: "Recall — control room",
  description:
    "Founder control room. Local-first. No server, no auth, no telemetry.",
  // The page never lives at a public origin; robots is belt-and-braces.
  robots: { index: false, follow: false },
};

/**
 * Phase 6J — full operator shell.
 *
 *   ┌──────────────────────────────────────────────────────────────┐
 *   │ TopBar  (Recall · health · readiness · installs · Ctrl+K)    │
 *   ├────────────┬────────────────────────────┬────────────────────┤
 *   │  Left rail │   Main route content        │   Actions sidebar │
 *   │  (sticky)  │   (server-rendered)         │   (sticky)        │
 *   ├────────────┴────────────────────────────┴────────────────────┤
 *   │ BottomBar (version · doctor · build)                          │
 *   └──────────────────────────────────────────────────────────────┘
 *
 * Stats for the top + bottom bars are loaded *here* so every page
 * inherits them without a per-page fetch. The CommandPalette is
 * mounted once via the ShellClient client component.
 */
export default async function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const [alpha, release, system] = await Promise.all([
    loadAlpha(),
    loadRelease(),
    loadSystemSnapshot(),
  ]);

  const daemonCheck = system.checks.find((c) => c.id === "events");
  const top: TopBarStats = {
    installs: alpha.installs,
    daemon_state: daemonCheck?.state ?? "yellow",
    daemon_label: daemonCheck?.state === "green" ? "online" : daemonCheck?.state === "yellow" ? "idle" : "—",
    readiness_state:
      release.go_no_go === "GO" ? "green" :
      release.go_no_go === "PARTIAL" ? "yellow" :
      release.go_no_go === "NO-GO" ? "red" : "yellow",
    readiness_label: `readiness ${release.go_no_go}`,
    version: release.current_version,
  };

  const launcherCheck = system.checks.find((c) => c.id === "launcher");
  const bottom: BottomBarStats = {
    version: release.current_version,
    build_label: "phase-6J · local · no server",
    doctor_state: launcherCheck?.state ?? "yellow",
    doctor_label:
      launcherCheck?.state === "green"
        ? "GREEN"
        : launcherCheck?.state === "yellow"
          ? "YELLOW"
          : launcherCheck?.state === "red"
            ? "RED"
            : "—",
    baked_mtime: null,
  };

  return (
    <html lang="en">
      <body>
        <ShellClient stats={top} />
        <div className="shell">
          <Nav />
          <main className="shell-main">{children}</main>
          <ActionsBar />
        </div>
        <BottomBar stats={bottom} />
      </body>
    </html>
  );
}
