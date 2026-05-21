import "./globals.css";
import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Recall — control room",
  description:
    "Founder control room. Local-first. No server, no auth, no telemetry.",
  // The page never lives at a public origin; robots is belt-and-braces.
  robots: { index: false, follow: false },
};

/**
 * Root layout for the admin UI. Plain HTML shell, system fonts, calm
 * defaults. The page composes its sections directly — no shell chrome,
 * no nav (a one-page surface is the whole product).
 */
export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
