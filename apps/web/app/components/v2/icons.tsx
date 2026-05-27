// Recall landing v2 — glyph set + Recall mark.
// Single-stroke SVG icons used across nav, hero cards, sections.

import * as React from "react";

const sx = {
  stroke: "currentColor",
  strokeWidth: 1.4,
  strokeLinecap: "round" as const,
  strokeLinejoin: "round" as const,
  fill: "none",
};

type IconProps = { size?: number };

export const Arrow = ({ size = 14 }: IconProps) => (
  <svg width={size} height={size} viewBox="0 0 16 16" fill="none">
    <path d="M3 8h10M9 4l4 4-4 4" {...sx} strokeWidth={1.6} />
  </svg>
);

export const ArrowUp = ({ size = 12 }: IconProps) => (
  <svg width={size} height={size} viewBox="0 0 12 12" fill="none">
    <path d="M3 9l5-5M4 4h4v4" {...sx} />
  </svg>
);

export const Play = ({ size = 12 }: IconProps) => (
  <svg width={size} height={size} viewBox="0 0 12 12" fill="none">
    <path d="M3.5 2.5l6 3.5-6 3.5V2.5z" fill="currentColor" />
  </svg>
);

export const Pause = ({ size = 12 }: IconProps) => (
  <svg width={size} height={size} viewBox="0 0 12 12" fill="none">
    <rect x="3" y="2.5" width="2" height="7" rx="0.5" fill="currentColor" />
    <rect x="7" y="2.5" width="2" height="7" rx="0.5" fill="currentColor" />
  </svg>
);

export const Download = ({ size = 14 }: IconProps) => (
  <svg width={size} height={size} viewBox="0 0 16 16" fill="none">
    <path d="M8 2v8m0 0l3-3m-3 3L5 7M3 13h10" {...sx} strokeWidth={1.5} />
  </svg>
);

export const Close = ({ size = 16 }: IconProps) => (
  <svg width={size} height={size} viewBox="0 0 16 16" fill="none">
    <path d="M4 4l8 8M12 4l-8 8" {...sx} strokeWidth={1.5} />
  </svg>
);

export const Search = ({ size = 15 }: IconProps) => (
  <svg width={size} height={size} viewBox="0 0 16 16" fill="none">
    <circle cx="7" cy="7" r="4.5" {...sx} />
    <path d="M10.5 10.5L14 14" {...sx} />
  </svg>
);

export const FileIcon = ({ size = 13 }: IconProps) => (
  <svg width={size} height={size} viewBox="0 0 14 14" fill="none">
    <path d="M3 1.5h5l3 3V12a.5.5 0 01-.5.5h-7A.5.5 0 013 12V2a.5.5 0 01.5-.5z" {...sx} />
    <path d="M8 1.5V4a.5.5 0 00.5.5H11" {...sx} />
  </svg>
);

export const DocIcon = FileIcon;

export const Research = ({ size = 13 }: IconProps) => (
  <svg width={size} height={size} viewBox="0 0 14 14" fill="none">
    <circle cx="6" cy="6" r="3.4" {...sx} />
    <path d="M8.5 8.5L12 12" {...sx} />
  </svg>
);

export const Chat = ({ size = 13 }: IconProps) => (
  <svg width={size} height={size} viewBox="0 0 14 14" fill="none">
    <path d="M2 4a2 2 0 012-2h6a2 2 0 012 2v3.5a2 2 0 01-2 2H5.5L3 12V9.5A2 2 0 012 7.5V4z" {...sx} />
  </svg>
);

export const Code = ({ size = 13 }: IconProps) => (
  <svg width={size} height={size} viewBox="0 0 14 14" fill="none">
    <path d="M5 4L2 7l3 3M9 4l3 3-3 3M8 3l-2 8" {...sx} />
  </svg>
);

export const Tab = ({ size = 13 }: IconProps) => (
  <svg width={size} height={size} viewBox="0 0 14 14" fill="none">
    <rect x="1.5" y="3.5" width="11" height="8" rx="1.2" {...sx} />
    <path d="M1.5 6h11" {...sx} />
  </svg>
);

export const Github = ({ size = 16 }: IconProps) => (
  <svg width={size} height={size} viewBox="0 0 20 20" fill="none">
    <path
      d="M10 2C5.6 2 2 5.6 2 10c0 3.5 2.3 6.5 5.5 7.6.4.1.6-.2.6-.4v-1.4c-2.2.5-2.7-1.1-2.7-1.1-.4-.9-.9-1.2-.9-1.2-.7-.5.1-.5.1-.5.8.1 1.2.8 1.2.8.7 1.2 1.9.9 2.4.7.1-.5.3-.9.5-1.1-1.8-.2-3.6-.9-3.6-4 0-.9.3-1.6.8-2.1-.1-.2-.4-1 .1-2.2 0 0 .7-.2 2.2.8.6-.2 1.3-.3 2-.3s1.4.1 2 .3c1.5-1 2.2-.8 2.2-.8.4 1.1.2 2 .1 2.2.5.5.8 1.2.8 2.1 0 3.1-1.9 3.7-3.6 3.9.3.3.6.8.6 1.6v2.3c0 .2.2.5.6.4 3.2-1.1 5.5-4.1 5.5-7.6 0-4.4-3.6-8-8-8z"
      fill="currentColor"
    />
  </svg>
);

export const Ext = ({ size = 14 }: IconProps) => (
  <svg width={size} height={size} viewBox="0 0 14 14" fill="none">
    <rect x="2" y="2" width="4" height="4" rx="0.8" {...sx} />
    <rect x="8" y="2" width="4" height="4" rx="0.8" {...sx} />
    <rect x="2" y="8" width="4" height="4" rx="0.8" {...sx} />
    <circle cx="10" cy="10" r="2.4" {...sx} />
  </svg>
);

export const Shield = ({ size = 18 }: IconProps) => (
  <svg width={size} height={size} viewBox="0 0 20 20" fill="none">
    <path d="M10 2L3.5 4.5v5.6c0 4 3 6.6 6.5 7.9 3.5-1.3 6.5-3.9 6.5-7.9V4.5L10 2z" {...sx} />
  </svg>
);

export const CloudOff = ({ size = 18 }: IconProps) => (
  <svg width={size} height={size} viewBox="0 0 20 20" fill="none">
    <path d="M5.5 14h9a3 3 0 100-6 4.5 4.5 0 00-8.7-1.2A3.5 3.5 0 005.5 14z" {...sx} />
    <path d="M3 4L17 18" stroke="currentColor" strokeWidth={1.4} strokeLinecap="round" />
  </svg>
);

export const EyeOff = ({ size = 18 }: IconProps) => (
  <svg width={size} height={size} viewBox="0 0 20 20" fill="none">
    <path d="M2 10s2.7-4 7-4 7 4 7 4-2.7 4-7 4-7-4-7-4z" {...sx} />
    <circle cx="9" cy="10" r="2.2" {...sx} />
    <path d="M3 3L17 17" stroke="currentColor" strokeWidth={1.4} strokeLinecap="round" />
  </svg>
);

export const Export = ({ size = 18 }: IconProps) => (
  <svg width={size} height={size} viewBox="0 0 20 20" fill="none">
    <path d="M11 4h5v5M16 4l-7 7M5 7v8h8" {...sx} />
  </svg>
);

export const Check = ({ size = 14 }: IconProps) => (
  <svg width={size} height={size} viewBox="0 0 16 16" fill="none">
    <path
      d="M3.5 8.5l3 3 6-7"
      stroke="currentColor"
      strokeWidth={1.7}
      strokeLinecap="round"
      strokeLinejoin="round"
    />
  </svg>
);

export function Mark({ size = 22 }: IconProps) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none">
      <defs>
        <linearGradient id="v2-mark-g" x1="0" y1="0" x2="1" y2="1">
          <stop offset="0%" stopColor="#D7D1FF" />
          <stop offset="100%" stopColor="#8B7FE3" />
        </linearGradient>
      </defs>
      <circle cx="12" cy="12" r="9" stroke="rgba(255,255,255,0.30)" strokeWidth={1.3} />
      <path d="M12 3a9 9 0 017.7 4.4" stroke="url(#v2-mark-g)" strokeWidth={1.7} strokeLinecap="round" />
      <circle cx="12" cy="3" r="1.8" fill="#D7D1FF" />
      <circle cx="12" cy="12" r="1.7" fill="#8B7FE3" />
    </svg>
  );
}

export function Kbd({ children }: { children: React.ReactNode }) {
  return (
    <span
      style={{
        fontFamily: "var(--font-mono)",
        fontSize: 10.5,
        fontWeight: 500,
        color: "var(--muted)",
        background: "rgba(255,255,255,0.04)",
        border: "1px solid var(--hairline)",
        padding: "2px 6px",
        borderRadius: 5,
        letterSpacing: "0.02em",
        lineHeight: 1,
        display: "inline-flex",
        alignItems: "center",
        justifyContent: "center",
        minWidth: 18,
      }}
    >
      {children}
    </span>
  );
}
