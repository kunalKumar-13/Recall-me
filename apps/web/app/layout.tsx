import type { Metadata } from "next";
import { Caveat, Fraunces, Inter } from "next/font/google";
import "./globals.css";

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
      <body className="font-sans antialiased text-ink-bright bg-bg-page">
        {children}
      </body>
    </html>
  );
}
