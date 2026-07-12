import type { Metadata, Viewport } from "next";
import { GeistSans } from "geist/font/sans";
import { GeistMono } from "geist/font/mono";
import localFont from "next/font/local";
import { SnapBoot } from "./lib/SnapBoot";
import "./globals.css";

/**
 * Type is the product's voice. Geist Sans carries display + body,
 * Geist Mono carries provenance (timestamps, paths, budgets), and
 * Instrument Serif italic carries the one editorial gesture in each
 * headline. All three are bundled woff2 served from this origin —
 * the site makes zero runtime font requests, same rule as the
 * product: nothing leaves the machine that doesn't have to.
 */
const instrument = localFont({
  src: [
    {
      path: "./fonts/instrument-serif-regular.woff2",
      weight: "400",
      style: "normal",
    },
    {
      path: "./fonts/instrument-serif-italic.woff2",
      weight: "400",
      style: "italic",
    },
  ],
  variable: "--font-serif",
  display: "swap",
});

export const metadata: Metadata = {
  title: "Recall — never lose the thread",
  description:
    "Recall quietly reconstructs what you were working on — the tabs, the files, the half-finished chat — and hands it back the moment you return. 100% local, no cloud, no telemetry.",
  openGraph: {
    title: "Recall — never lose the thread",
    description:
      "A local-first continuity OS. One keystroke brings back the exact work you left — files, chats, tabs — in order.",
    type: "website",
  },
  twitter: {
    card: "summary",
    title: "Recall — never lose the thread",
    description:
      "A local-first continuity OS. One keystroke brings back the exact work you left.",
  },
};

export const viewport: Viewport = {
  themeColor: "#fbfbfa",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html
      lang="en"
      className={`${GeistSans.variable} ${GeistMono.variable} ${instrument.variable}`}
    >
      <body>
        {/* The drafting frame: two hairline rails at the content
            edges, running the full height of the page. Sections rule
            across them; the + marks live on the rules. */}
        <div className="rails" aria-hidden="true" />
        <SnapBoot />
        {children}
      </body>
    </html>
  );
}
