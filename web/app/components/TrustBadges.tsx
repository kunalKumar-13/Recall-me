"use client";

import { motion } from "framer-motion";

const ease = [0.32, 0.72, 0, 1] as const;

type Badge = {
  icon: React.ReactNode;
  title: string;
  body: string;
  tint: string;
};

/**
 * Inline monoline glyphs at 1.5px stroke. Single-color so each badge
 * can tint them via currentColor, keeping the row as a unified set.
 */
const Icon = {
  Shield: (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
      <path d="M12 3l8 3v6c0 4.5-3.4 8.4-8 9-4.6-.6-8-4.5-8-9V6l8-3z" />
      <path d="M9.5 12l1.7 1.7L15 10.5" />
    </svg>
  ),
  CloudOff: (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
      <path d="M4 4l16 16" />
      <path d="M17.5 17.5h-12a4 4 0 0 1-.5-7.96A6 6 0 0 1 16 8" />
      <path d="M20 14a4 4 0 0 0-1.6-3.2" />
    </svg>
  ),
  EyeOff: (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
      <path d="M3 3l18 18" />
      <path d="M10.6 5.2A11 11 0 0 1 12 5c5 0 9 4 10 7-.5 1.4-1.6 3-3.2 4.3" />
      <path d="M6.2 6.2C4 7.6 2.6 9.6 2 12c1 3 5 7 10 7 1.5 0 2.9-.4 4.2-1" />
      <path d="M9.9 9.9a3 3 0 0 0 4.2 4.2" />
    </svg>
  ),
  Heart: (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
      <path d="M12 20.5l-1.4-1.3C5.4 14.5 2 11.5 2 7.9A4.9 4.9 0 0 1 6.9 3c1.7 0 3.4.8 4.5 2.1H12C13 3.8 14.7 3 16.4 3A4.9 4.9 0 0 1 21.3 7.9c0 3.6-3.4 6.6-8.6 11.3L12 20.5z" />
    </svg>
  ),
};

const badges: Badge[] = [
  {
    icon: Icon.Shield,
    title: "100% Local",
    body: "Your data stays on your device",
    tint: "#A99CF7",
  },
  {
    icon: Icon.CloudOff,
    title: "No Cloud",
    body: "Everything stays local",
    tint: "#7DD8E8",
  },
  {
    icon: Icon.EyeOff,
    title: "No Telemetry",
    body: "Zero tracking. Ever.",
    tint: "#87DEB7",
  },
  {
    icon: Icon.Heart,
    title: "Your Data, Yours",
    body: "You own your memories",
    tint: "#F4A8C9",
  },
];

/**
 * Trust badges — four white cards in a row beneath the hero CTAs.
 *
 * Each card is the same shape (icon, title, body) so the row reads as
 * a single statement rather than four discrete claims. Icons inherit
 * a per-card tint from `currentColor` so the row carries a quiet
 * rainbow without any one element shouting.
 */
export function TrustBadges() {
  return (
    <div
      className="
        grid grid-cols-2 lg:grid-cols-4 gap-3 md:gap-4
        max-w-[640px]
      "
    >
      {badges.map((b, i) => (
        <motion.div
          key={b.title}
          initial={{ opacity: 0, y: 8 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, margin: "-60px" }}
          transition={{ duration: 0.45, ease, delay: 0.32 + i * 0.04 }}
          className="
            flex items-start gap-3
            px-3.5 py-3 rounded-xl
            bg-bg-base border border-hairline shadow-card
          "
        >
          <div
            className="shrink-0 w-7 h-7 flex items-center justify-center rounded-md"
            style={{ background: `${b.tint}1f`, color: b.tint }}
          >
            <div className="w-4 h-4">{b.icon}</div>
          </div>
          <div className="min-w-0">
            <div className="text-[12.5px] font-semibold text-ink-bright leading-tight">
              {b.title}
            </div>
            <div className="text-[11px] text-ink-dim leading-snug mt-0.5">
              {b.body}
            </div>
          </div>
        </motion.div>
      ))}
    </div>
  );
}
