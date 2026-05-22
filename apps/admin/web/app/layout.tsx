import "./globals.css";
import type { Metadata } from "next";
import { ActionsBar } from "../components/ActionsBar";
import { Nav } from "../components/Nav";

export const metadata: Metadata = {
  title: "Recall — control room",
  description:
    "Founder control room. Local-first. No server, no auth, no telemetry.",
  // The page never lives at a public origin; robots is belt-and-braces.
  robots: { index: false, follow: false },
};

/**
 * Phase 6H — three-column operator shell.
 *
 *   ┌────────────┬──────────────────────────┬───────────────┐
 *   │  Left rail │   Main route content      │   Actions    │
 *   │  (sticky)  │   (server-rendered)       │   (sticky)   │
 *   └────────────┴──────────────────────────┴───────────────┘
 *
 * Rail + actions are client components (Nav reads the path,
 * ActionsBar runs the clipboard fallback). Every route page is a
 * server component that reads from the live loaders. Nothing in the
 * shell hits the network.
 */
export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>
        <div className="shell">
          <Nav />
          <main className="shell-main">{children}</main>
          <ActionsBar />
        </div>
      </body>
    </html>
  );
}
