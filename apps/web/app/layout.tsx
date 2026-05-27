import type { Metadata } from "next";
import { Caveat, Fraunces, Inter } from "next/font/google";
import "./globals.css";
import "./v2.css";

// Phase 11A — Recall landing v2 fonts.
//
// Geist, Geist Mono, and Instrument Serif are loaded via a raw
// <link> to Google Fonts in <head> below. `next/font/google` only
// supports `Geist` from Next 15+, but this project pins 14.2.x;
// the raw <link> matches the design pack's original HTML and keeps
// the v2.css family chain (`var(--font-sans)` → "Geist", -apple-system, …)
// resolving correctly.

// Inter — every body, every UI element, every caption.
const inter = Inter({
  subsets: ["latin"],
  display: "swap",
  variable: "--font-inter",
  weight: ["300", "400", "500", "600", "700"],
});

// Fraunces — the editorial serif. Used for display moments only:
// hero headline, section titles, the FinalCTA close. Restraint is
// what makes it feel deliberate.
const fraunces = Fraunces({
  subsets: ["latin"],
  display: "swap",
  variable: "--font-fraunces",
  weight: ["400", "500", "600"],
  style: ["normal", "italic"],
});

// Caveat — the script font. Reserved for the peripheral handwritten
// annotations ("Not filenames. Thoughts.", "Try the launcher in your
// browser"). Two or three uses across the page, never inside body
// text.
const caveat = Caveat({
  subsets: ["latin"],
  display: "swap",
  variable: "--font-caveat",
  weight: ["400", "500", "600", "700"],
});

export const metadata: Metadata = {
  title: "Recall — A local-first continuity operating system",
  description:
    "Open Ctrl + Space, type a half-thought, get back the tabs, files, and chats you were working with — in a coherent sequence. Local-first, deterministic, no cloud, no telemetry.",
  openGraph: {
    title: "Recall — A local-first continuity operating system",
    description:
      "Cognitive restart, one keystroke. Local-first. Deterministic. No cloud, no telemetry.",
    type: "website",
  },
  twitter: {
    card: "summary_large_image",
    title: "Recall — A local-first continuity operating system",
    description:
      "Cognitive restart, one keystroke. Local-first. Deterministic. No cloud, no telemetry.",
  },
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html
      lang="en"
      className={`${inter.variable} ${fraunces.variable} ${caveat.variable}`}
    >
      <head>
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="anonymous" />
        <link
          href="https://fonts.googleapis.com/css2?family=Geist:wght@300;400;450;500;600&family=Geist+Mono:wght@400;500;600&family=Instrument+Serif:ital@0;1&display=swap"
          rel="stylesheet"
        />
      </head>
      <body className="font-sans antialiased text-ink-bright bg-bg-page">
        {children}
      </body>
    </html>
  );
}
