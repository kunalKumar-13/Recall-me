import { Logo } from "./Logo";

/**
 * LauncherMockup — a static, pixel-faithful recreation of the Recall
 * launcher: sidebar, search bar, ranked results, and a preview pane.
 *
 * This is *not* a screenshot. It is hand-built markup so the website
 * and the desktop app stay in visual lockstep without shipping a
 * binary image. Nothing here animates; it paints once.
 */

type Result = {
  title: string;
  file: string;
  seen: string;
  score: number;
  active?: boolean;
};

const RESULTS: Result[] = [
  {
    title: "Healthcare Startup Pitch",
    file: "pitch_healthcare_v3.pdf",
    seen: "Last seen Jan 12, 2024",
    score: 98,
    active: true,
  },
  {
    title: "User Research Notes",
    file: "research_interviews.md",
    seen: "Last seen Jan 10, 2024",
    score: 92,
  },
  {
    title: "MVP Technical Plan",
    file: "technical_plan_v2.md",
    seen: "Last seen Jan 8, 2024",
    score: 91,
  },
  {
    title: "Competitor Analysis",
    file: "analysis_competitors.xlsx",
    seen: "Last seen Dec 28, 2023",
    score: 87,
  },
];

const RELATED = [
  "Patient triage flow notes",
  "Care-team routing diagram",
  "Insurance verification logic",
];

function SidebarIcon({ kind }: { kind: string }) {
  const common = {
    fill: "none",
    stroke: "currentColor",
    strokeWidth: 1.6,
    strokeLinecap: "round" as const,
    strokeLinejoin: "round" as const,
  };
  switch (kind) {
    case "search":
      return (
        <svg viewBox="0 0 24 24" {...common}>
          <circle cx="10.5" cy="10.5" r="6.5" />
          <path d="M20 20l-4.5-4.5" />
        </svg>
      );
    case "memories":
      return (
        <svg viewBox="0 0 24 24" {...common}>
          <path d="M4 6.5A2.5 2.5 0 0 1 6.5 4H20v13H6.5A2.5 2.5 0 0 0 4 19.5z" />
          <path d="M4 6.5v13" />
        </svg>
      );
    case "threads":
      return (
        <svg viewBox="0 0 24 24" {...common}>
          <circle cx="6" cy="7" r="2.2" />
          <circle cx="18" cy="17" r="2.2" />
          <path d="M6 9.2v3.3A4 4 0 0 0 10 16.5h5.8" />
        </svg>
      );
    case "settings":
      return (
        <svg viewBox="0 0 24 24" {...common}>
          <circle cx="12" cy="12" r="3" />
          <path d="M12 2.5v2.5M12 19v2.5M4.6 4.6l1.8 1.8M17.6 17.6l1.8 1.8M2.5 12H5M19 12h2.5M4.6 19.4l1.8-1.8M17.6 6.4l1.8-1.8" />
        </svg>
      );
    default:
      return null;
  }
}

const SIDEBAR: { kind: string; label: string; active?: boolean }[] = [
  { kind: "search", label: "Search", active: true },
  { kind: "memories", label: "Memories" },
  { kind: "threads", label: "Threads" },
  { kind: "settings", label: "Settings" },
];

export function LauncherMockup() {
  return (
    <div
      className="
        relative w-full rounded-2xl overflow-hidden
        bg-bg-base border border-hairline
        shadow-dashboard
      "
    >
      {/* ── Title strip ─────────────────────────────────────────── */}
      <div className="flex items-center gap-2 px-4 h-9 border-b border-hairline bg-bg-raised/70">
        <span className="w-2.5 h-2.5 rounded-full bg-ink-dimmer/60" />
        <span className="w-2.5 h-2.5 rounded-full bg-ink-dimmer/40" />
        <span className="w-2.5 h-2.5 rounded-full bg-ink-dimmer/30" />
        <span className="ml-2 inline-flex items-center gap-1.5 text-[10px] font-mono text-ink-dim">
          <Logo className="w-3.5 h-3.5" />
          Recall
        </span>
      </div>

      <div className="flex">
        {/* ── Sidebar ──────────────────────────────────────────── */}
        <nav className="w-[124px] shrink-0 border-r border-hairline bg-bg-sidebar/60 py-3 px-2">
          {SIDEBAR.map((item) => (
            <div
              key={item.label}
              className={`
                flex items-center gap-2 px-2.5 py-2 rounded-lg mb-0.5
                text-[11.5px]
                ${
                  item.active
                    ? "bg-lavender-soft/70 text-lavender-deep font-medium"
                    : "text-ink-dim"
                }
              `}
            >
              <span className="w-3.5 h-3.5">
                <SidebarIcon kind={item.kind} />
              </span>
              {item.label}
            </div>
          ))}
        </nav>

        {/* ── Main column ─────────────────────────────────────── */}
        <div className="flex-1 min-w-0">
          {/* Search bar */}
          <div className="px-4 pt-4">
            <div className="flex items-center gap-2.5 h-10 px-3 rounded-xl border border-hairline-strong bg-bg-base">
              <span className="w-4 h-4 text-ink-dim shrink-0">
                <SidebarIcon kind="search" />
              </span>
              <span className="text-[12.5px] text-ink-bright truncate">
                that healthcare startup idea from last winter
              </span>
              <span className="ml-auto shrink-0 text-[9.5px] font-mono text-ink-dim border border-hairline rounded-md px-1.5 py-0.5">
                Ctrl + Space
              </span>
            </div>
          </div>

          {/* Results + preview */}
          <div className="grid grid-cols-1 sm:grid-cols-[1.05fr_0.95fr]">
            {/* Results list */}
            <div className="px-4 py-4">
              <div className="text-[9px] font-semibold tracking-[0.18em] text-ink-dim uppercase mb-2.5">
                Top results
              </div>
              <div className="space-y-1.5">
                {RESULTS.map((r) => (
                  <div
                    key={r.file}
                    className={`
                      flex items-center gap-2.5 p-2 rounded-lg
                      ${r.active ? "bg-lavender-soft/55" : ""}
                    `}
                  >
                    <span
                      className="
                        w-7 h-7 shrink-0 rounded-md
                        flex items-center justify-center
                        bg-bg-raised border border-hairline
                        text-[8px] font-mono font-semibold text-ink-dim
                      "
                    >
                      DOC
                    </span>
                    <span className="min-w-0">
                      <span className="block text-[11.5px] font-medium text-ink-bright truncate">
                        {r.title}
                      </span>
                      <span className="block text-[9.5px] font-mono text-ink-dim truncate">
                        {r.file}
                      </span>
                      <span className="block text-[9px] text-ink-dimmer">
                        {r.seen}
                      </span>
                    </span>
                    <span className="ml-auto shrink-0 text-[10.5px] font-mono font-semibold text-lavender-deep">
                      {r.score}%
                    </span>
                  </div>
                ))}
              </div>
              <div className="mt-3 text-[10px] text-lavender-deep font-medium">
                See 24 more results →
              </div>
            </div>

            {/* Preview pane */}
            <div className="px-4 py-4 border-t sm:border-t-0 sm:border-l border-hairline bg-bg-raised/40">
              <div className="text-[9px] font-semibold tracking-[0.18em] text-ink-dim uppercase mb-2.5">
                Preview
              </div>
              <div className="flex items-center gap-2">
                <span className="w-7 h-7 shrink-0 rounded-md flex items-center justify-center bg-highlight-soft border border-hairline text-[8px] font-mono font-semibold text-ink-dim">
                  PDF
                </span>
                <span className="min-w-0">
                  <span className="block text-[11.5px] font-medium text-ink-bright truncate">
                    Healthcare Startup Pitch
                  </span>
                  <span className="block text-[9.5px] font-mono text-ink-dim truncate">
                    pitch_healthcare_v3.pdf
                  </span>
                </span>
              </div>

              <div className="mt-3 text-[9px] font-semibold tracking-[0.18em] text-ink-dim uppercase">
                Excerpt
              </div>
              <p className="mt-1.5 text-[10.5px] leading-[1.6] text-ink">
                Our vision is to give care teams{" "}
                <span className="term-highlight">a single continuity layer</span>{" "}
                — patient history, triage notes, and routing decisions stay
                connected across every visit.
              </p>

              <div className="mt-3 text-[9px] font-semibold tracking-[0.18em] text-ink-dim uppercase">
                Related memories
              </div>
              <ul className="mt-1.5 space-y-1">
                {RELATED.map((item) => (
                  <li
                    key={item}
                    className="flex items-center gap-1.5 text-[10px] text-ink"
                  >
                    <span className="w-1 h-1 rounded-full bg-lavender-deep shrink-0" />
                    {item}
                  </li>
                ))}
              </ul>

              <div className="mt-3.5 inline-flex items-center justify-center h-7 px-3 rounded-lg bg-ink-bright text-white text-[10px] font-medium">
                Open file
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
