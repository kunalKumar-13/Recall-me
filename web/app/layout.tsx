import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";

const inter = Inter({
  subsets: ["latin"],
  display: "swap",
  variable: "--font-inter",
});

export const metadata: Metadata = {
  title: "Recall — Ask your computer what you forgot.",
  description:
    "An AI memory layer for your laptop. Recall instantly resurfaces forgotten ideas, notes, PDFs, and code — privately and offline.",
  openGraph: {
    title: "Recall — Ask your computer what you forgot.",
    description:
      "An AI memory layer for your laptop. Local-first, private, instant.",
    type: "website",
  },
  twitter: {
    card: "summary_large_image",
    title: "Recall — Ask your computer what you forgot.",
    description:
      "An AI memory layer for your laptop. Local-first, private, instant.",
  },
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className={inter.variable}>
      <body className="font-sans">{children}</body>
    </html>
  );
}
