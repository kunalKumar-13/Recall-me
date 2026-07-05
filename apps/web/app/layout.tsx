import type { Metadata, Viewport } from "next";
import "./globals.css";

/**
 * System type on purpose: SF Pro / New York / SF Mono are the same
 * faces the product itself renders in, load in zero milliseconds,
 * and keep the page feeling native rather than "web font'd".
 */
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
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
