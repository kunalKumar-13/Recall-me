/**
 * Dashboard mockup — the hero device.
 *
 * Composition (left to right):
 *   1. Sidebar         — five nav slots, a "Search" pill highlighted
 *   2. Top bar         — the recovered query, kbd hint, view toggle
 *   3. Top Results     — four file cards with relevance scores
 *   4. Preview         — file header, excerpt with highlights,
 *                        related memories, primary "Open in File" CTA
 *
 * The data tells one coherent story: a healthcare-startup memory
 * recovered from a vague query. That single thread should make the
 * mockup read as a real moment of remembering, not a UI screenshot.
 *
 * Accessibility notes:
 *   - The whole mockup is `aria-hidden` because it's a static visual
 *     prop, not an interactive surface. Screen readers announce the
 *     hero copy + CTAs instead.
 *   - Width is responsive (clamped between mobile-readable and
 *     desktop-comfortable); the preview pane collapses on narrow
 *     viewports rather than horizontally scrolling.
 */

import { Logo } from "./Logo";

// ----------------------------------------------------------- file icons

type FileTint = "lavender" | "cyan" | "mint" | "rose" | "amber";

const TINTS: Record<FileTint, { fg: string; bg: string }> = {
  lavender: { fg: "#8B7FE3", bg: "rgba(169, 156, 247, 0.12)" },
  cyan: { fg: "#3FB1C9", bg: "rgba(125, 216, 232, 0.16)" },
  mint: { fg: "#42B384", bg: "rgba(135, 222, 183, 0.16)" },
  rose: { fg: "#D67896", bg: "rgba(244, 168, 201, 0.18)" },
  amber: { fg: "#C7973C", bg: "rgba(245, 198, 109, 0.18)" },
};

function FileBadge({
  ext,
  tint,
  size = 36,
}: {
  ext: string;
  tint: FileTint;
  size?: number;
}) {
  const t = TINTS[tint];
  return (
    <div
      className="rounded-md flex items-center justify-center font-semibold"
      style={{
        width: size,
        height: size,
        background: t.bg,
        color: t.fg,
        fontSize: size * 0.28,
        letterSpacing: "0.05em",
      }}
    >
      {ext}
    </div>
  );
}

// ----------------------------------------------------------- sidebar

type NavItem = {
  key: string;
  label: string;
  icon: React.ReactNode;
  active?: boolean;
};

const NAV_ICON = {
  Search: (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round">
      <circle cx="10.5" cy="10.5" r="6.5" />
      <path d="M20 20l-4.5-4.5" />
    </svg>
  ),
  Memories: (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round">
      <path d="M5 4h11l3 3v13a1 1 0 0 1-1 1H5a1 1 0 0 1-1-1V5a1 1 0 0 1 1-1z" />
      <path d="M16 4v3h3" />
      <path d="M8 12h8M8 16h6" />
    </svg>
  ),
  Digest: (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round">
      <path d="M4 19V9M10 19V5M16 19v-7M22 19H2" />
    </svg>
  ),
  Graph: (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round">
      <circle cx="6" cy="7" r="2.2" />
      <circle cx="18" cy="6" r="2.2" />
      <circle cx="12" cy="17" r="2.2" />
      <circle cx="19" cy="18" r="1.6" />
      <path d="M7.7 8.5l3.2 6.7M16.5 7.6l-3.4 7.5M14 17l3-1" />
    </svg>
  ),
  Settings: (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round">
      <circle cx="12" cy="12" r="3" />
      <path d="M19.4 15a1.6 1.6 0 0 0 .3 1.7l.1.1a2 2 0 1 1-2.8 2.8l-.1-.1a1.6 1.6 0 0 0-1.7-.3 1.6 1.6 0 0 0-1 1.5V21a2 2 0 1 1-4 0v-.1a1.6 1.6 0 0 0-1-1.5 1.6 1.6 0 0 0-1.7.3l-.1.1a2 2 0 1 1-2.8-2.8l.1-.1a1.6 1.6 0 0 0 .3-1.7 1.6 1.6 0 0 0-1.5-1H3a2 2 0 1 1 0-4h.1a1.6 1.6 0 0 0 1.5-1 1.6 1.6 0 0 0-.3-1.7l-.1-.1a2 2 0 1 1 2.8-2.8l.1.1a1.6 1.6 0 0 0 1.7.3H9a1.6 1.6 0 0 0 1-1.5V3a2 2 0 1 1 4 0v.1a1.6 1.6 0 0 0 1 1.5 1.6 1.6 0 0 0 1.7-.3l.1-.1a2 2 0 1 1 2.8 2.8l-.1.1a1.6 1.6 0 0 0-.3 1.7V9a1.6 1.6 0 0 0 1.5 1H21a2 2 0 1 1 0 4h-.1a1.6 1.6 0 0 0-1.5 1z" />
    </svg>
  ),
};

const navItems: NavItem[] = [
  { key: "search", label: "Search", icon: NAV_ICON.Search, active: true },
  { key: "memories", label: "Memories", icon: NAV_ICON.Memories },
  { key: "digest", label: "Digest", icon: NAV_ICON.Digest },
  { key: "graph", label: "Graph", icon: NAV_ICON.Graph },
  { key: "settings", label: "Settings", icon: NAV_ICON.Settings },
];

function Sidebar() {
  return (
    <div className="w-[68px] md:w-[78px] shrink-0 bg-bg-sidebar border-r border-hairline flex flex-col items-center py-4 gap-1">
      <div className="mb-3">
        <Logo className="w-7 h-7" />
      </div>

      {navItems.map((item) => (
        <div
          key={item.key}
          className={`
            w-[52px] md:w-[60px] py-2 rounded-lg
            flex flex-col items-center justify-center gap-1
            transition-colors duration-200
            ${
              item.active
                ? "bg-lavender-soft text-lavender-deep"
                : "text-ink-dim"
            }
          `}
        >
          <div className="w-[18px] h-[18px]">{item.icon}</div>
          <div className="text-[9.5px] font-medium tracking-tight">
            {item.label}
          </div>
        </div>
      ))}
    </div>
  );
}

// ----------------------------------------------------------- top bar

function TopBar() {
  return (
    <div className="flex items-center gap-3 px-5 h-14 border-b border-hairline">
      <div className="w-4 h-4 text-ink-dim shrink-0">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.7" strokeLinecap="round">
          <circle cx="10.5" cy="10.5" r="6.5" />
          <path d="M20 20l-4.5-4.5" />
        </svg>
      </div>
      <div className="flex-1 text-[14px] text-ink-bright tracking-[-0.005em] truncate">
        that healthcare startup idea from last winter
      </div>
      <kbd className="hidden md:inline-flex text-[10px] text-ink-dim px-1.5 py-0.5 rounded border border-hairline bg-bg-page font-sans tracking-wider">
        Ctrl + Space
      </kbd>
      <div className="w-7 h-7 rounded-md border border-hairline flex items-center justify-center text-ink-dim">
        <svg viewBox="0 0 24 24" className="w-3.5 h-3.5" fill="none" stroke="currentColor" strokeWidth="1.6">
          <rect x="4" y="4" width="7" height="7" rx="1" />
          <rect x="13" y="4" width="7" height="7" rx="1" />
          <rect x="4" y="13" width="7" height="7" rx="1" />
          <rect x="13" y="13" width="7" height="7" rx="1" />
        </svg>
      </div>
    </div>
  );
}

// ----------------------------------------------------------- results

type Result = {
  ext: string;
  tint: FileTint;
  title: string;
  filename: string;
  date: string;
  score: number;
};

const results: Result[] = [
  {
    ext: "PDF",
    tint: "rose",
    title: "Healthcare Startup Pitch",
    filename: "pitch_healthcare_v3.pdf",
    date: "Last seen Jan 12, 2024",
    score: 98,
  },
  {
    ext: "MD",
    tint: "lavender",
    title: "User Research Notes",
    filename: "research_interviews.md",
    date: "Last seen Jan 10, 2024",
    score: 92,
  },
  {
    ext: "TXT",
    tint: "amber",
    title: "MVP Technical Plan",
    filename: "technical_plan_v2.md",
    date: "Last seen Jan 8, 2024",
    score: 91,
  },
  {
    ext: "DOC",
    tint: "cyan",
    title: "Competitor Analysis",
    filename: "analysis_competitors.docx",
    date: "Last seen Dec 28, 2023",
    score: 87,
  },
];

function ResultRow({ r }: { r: Result }) {
  return (
    <div className="flex items-center gap-3 px-3 py-2.5 rounded-lg hover:bg-bg-page transition-colors">
      <FileBadge ext={r.ext} tint={r.tint} size={36} />
      <div className="flex-1 min-w-0">
        <div className="text-[12.5px] font-semibold text-ink-bright truncate tracking-tight">
          {r.title}
        </div>
        <div className="text-[10.5px] text-ink-dim truncate">
          {r.filename}
        </div>
        <div className="text-[10px] text-ink-dim/85 truncate mt-0.5">
          {r.date}
        </div>
      </div>
      <div className="text-[12px] font-semibold text-lavender-deep tabular-nums">
        {r.score}%
      </div>
    </div>
  );
}

function ResultsColumn() {
  return (
    <div className="w-full md:w-[44%] py-3 px-2 md:border-r md:border-hairline">
      <div className="px-3 mb-2 text-[10.5px] font-semibold tracking-[0.14em] text-ink-dim uppercase">
        Top Results
      </div>
      <div className="flex flex-col gap-0.5">
        {results.map((r) => (
          <ResultRow key={r.title} r={r} />
        ))}
      </div>
      <div className="mt-2 px-3 text-[11px] text-lavender-deep font-medium hover:underline cursor-default">
        See 24 more results →
      </div>
    </div>
  );
}

// ----------------------------------------------------------- preview

function PreviewPane() {
  return (
    <div className="flex-1 py-3 px-4 flex flex-col gap-3">
      <div className="text-[10.5px] font-semibold tracking-[0.14em] text-ink-dim uppercase">
        Preview
      </div>

      {/* File header */}
      <div className="flex items-center gap-2.5">
        <FileBadge ext="PDF" tint="rose" size={28} />
        <div className="min-w-0">
          <div className="text-[13px] font-semibold text-ink-bright truncate tracking-tight">
            Healthcare Startup Pitch
          </div>
          <div className="text-[10.5px] text-ink-dim truncate">
            pitch_healthcare_v3.pdf
          </div>
        </div>
      </div>

      {/* Excerpt */}
      <div>
        <div className="text-[10.5px] font-semibold tracking-[0.14em] text-ink-dim uppercase mb-1.5">
          Excerpt
        </div>
        <p className="text-[12px] leading-relaxed text-ink-bright/90">
          Our vision is to{" "}
          <span className="term-highlight">build AI agents</span> that
          assist healthcare teams by triaging patient queries,
          summarizing history, and routing to the{" "}
          <span className="term-highlight">right specialist</span>…
        </p>
      </div>

      {/* Related memories */}
      <div>
        <div className="text-[10.5px] font-semibold tracking-[0.14em] text-ink-dim uppercase mb-1.5">
          Related Memories
        </div>
        <ul className="space-y-1 text-[11.5px] text-ink-bright/85">
          <li className="flex items-start gap-2">
            <span className="text-lavender-deep/60">•</span>
            <span>AI agent evaluation metrics</span>
          </li>
          <li className="flex items-start gap-2">
            <span className="text-lavender-deep/60">•</span>
            <span>Patient triage flow discussion</span>
          </li>
          <li className="flex items-start gap-2">
            <span className="text-lavender-deep/60">•</span>
            <span>Insurance verification logic</span>
          </li>
        </ul>
      </div>

      {/* Open in File CTA */}
      <div className="mt-auto pt-2">
        <div
          className="
            inline-flex items-center gap-1.5
            px-3 py-1.5 rounded-md
            bg-lavender-gradient text-white text-[11.5px] font-medium
            shadow-lift
          "
        >
          Open in File
          <svg viewBox="0 0 24 24" className="w-3 h-3" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <path d="M5 12h14M13 5l7 7-7 7" />
          </svg>
        </div>
      </div>
    </div>
  );
}

// ----------------------------------------------------------- shell

export function LauncherMockup() {
  return (
    <div
      aria-hidden
      className="
        w-full max-w-[680px] mx-auto
        rounded-2xl overflow-hidden
        bg-bg-base border border-hairline shadow-dashboard
      "
    >
      <div className="flex" style={{ minHeight: 420 }}>
        <Sidebar />
        <div className="flex-1 min-w-0 flex flex-col">
          <TopBar />
          {/* Body — Results + Preview side-by-side. On very narrow
              screens the preview hides to keep things readable. */}
          <div className="flex-1 flex">
            <ResultsColumn />
            <div className="hidden md:flex flex-1">
              <PreviewPane />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
