/**
 * The cinematic hero centerpiece — a static recreation of the Recall
 * launcher rendered with HTML/CSS so it scales crisply, animates, and
 * matches the actual app's visual language exactly.
 *
 * The data tells one coherent story: the user typed a vague memory, and
 * Recall surfaced a months-old healthcare-startup thread that spans a
 * pitch deck, code, notes, and a draft.
 */

type Memory = {
  ext: { label: string; color: string };
  title: string;
  why: string;
  pill: { text: string; color: string };
  cluster?: number;
  resurfaced?: string;
  selected?: boolean;
};

const memories: Memory[] = [
  {
    ext: { label: "PDF", color: "#ef4444" },
    title: "Healthcare agents pitch deck",
    why: "Covers healthcare, agents, and triage.",
    pill: { text: "Highly relevant", color: "#10b981" },
    cluster: 2,
    resurfaced: "resurfaced from Jan 2024",
    selected: true,
  },
  {
    ext: { label: "PY", color: "#3b82f6" },
    title: "def TriageAgent",
    why: "Discusses agent and triage.",
    pill: { text: "Relevant", color: "#8b9bff" },
  },
  {
    ext: { label: "MD", color: "#8b5cf6" },
    title: "Onboarding flow notes",
    why: "Mentions onboarding and intake.",
    pill: { text: "Relevant", color: "#8b9bff" },
  },
  {
    ext: { label: "TXT", color: "#9ca3af" },
    title: "Market sizing draft",
    why: "Mentions healthcare.",
    pill: { text: "Possible match", color: "#9ca3af" },
  },
];

function ExtTag({ label, color }: { label: string; color: string }) {
  return (
    <div
      className="w-10 h-10 rounded-lg flex items-center justify-center text-[10px] font-bold tracking-widest shrink-0"
      style={{
        background: `${color}22`,
        color,
        border: `1px solid ${color}55`,
      }}
    >
      {label}
    </div>
  );
}

function Pill({ text, color }: { text: string; color: string }) {
  return (
    <span
      className="inline-flex items-center h-5 px-2.5 text-[10px] font-semibold tracking-wide rounded-[10px]"
      style={{
        background: `${color}22`,
        color,
        border: `1px solid ${color}40`,
      }}
    >
      {text}
    </span>
  );
}

function ClusterBadge({ n }: { n: number }) {
  return (
    <span
      className="inline-flex items-center h-5 px-2 text-[10px] font-semibold rounded-[10px]"
      style={{
        background: "rgba(139, 155, 255, 0.12)",
        color: "#a4b3ff",
        border: "1px solid rgba(139, 155, 255, 0.32)",
      }}
    >
      +{n}
    </span>
  );
}

function MemoryRow({ memory }: { memory: Memory }) {
  return (
    <div
      className="flex items-start gap-3 px-3 py-2.5 mx-1 my-0.5 rounded-xl transition-colors"
      style={{
        background: memory.selected
          ? "rgba(50, 56, 78, 0.55)"
          : "transparent",
      }}
    >
      <ExtTag label={memory.ext.label} color={memory.ext.color} />
      <div className="flex-1 min-w-0">
        <div className="text-[13px] font-semibold text-white/95 truncate">
          {memory.title}
        </div>
        <div className="flex items-center gap-2 mt-1">
          <div className="text-[11px] text-white/50 truncate flex-1">
            {memory.why}
            {memory.resurfaced && (
              <span className="text-white/40">
                {" · "}
                {memory.resurfaced}
              </span>
            )}
          </div>
          {memory.cluster ? <ClusterBadge n={memory.cluster} /> : null}
          <Pill text={memory.pill.text} color={memory.pill.color} />
        </div>
      </div>
    </div>
  );
}

function SectionLabel({ children }: { children: React.ReactNode }) {
  return (
    <div className="text-[11px] font-semibold tracking-wide text-white/40">
      {children}
    </div>
  );
}

function Divider() {
  return <div className="h-px w-full bg-white/[0.06] my-3" />;
}

function PreviewContent() {
  return (
    <div>
      <SectionLabel>Memory</SectionLabel>
      <div className="text-[16px] font-semibold text-white mt-1.5 tracking-[-0.01em]">
        Healthcare agents pitch deck
      </div>
      <div className="text-[11px] text-white/35 mt-1 truncate">
        ~/Documents/healthcare-v3/pitch_deck.pdf
      </div>
      <div className="text-[11px] italic text-white/40 mt-1">
        Last seen Jan 2024
      </div>

      <Divider />

      <SectionLabel>About</SectionLabel>
      <div className="text-[12px] text-white/85 mt-1.5 leading-relaxed">
        You explored a healthcare agent triage system last winter — an
        onboarding flow that routed pediatric patients via natural-language
        intake.
      </div>

      <Divider />

      <SectionLabel>Excerpt</SectionLabel>
      <div className="text-[12px] italic text-white/60 mt-1.5 leading-[1.65]">
        …routing{" "}
        <b style={{ color: "#cdd2e0" }}>pediatric</b> patients via
        natural-language intake, with the{" "}
        <b style={{ color: "#cdd2e0" }}>agent</b> classifying urgency and
        matching to specialists. The team explored{" "}
        <b style={{ color: "#cdd2e0" }}>healthcare</b>-specific evaluation
        rubrics for triage accuracy…
      </div>

      <Divider />

      <SectionLabel>Sources</SectionLabel>
      <div
        className="text-[11px] mt-1.5"
        style={{ color: "#8b9bff", fontWeight: 500 }}
      >
        Spans PDF, MD, TXT — same idea across formats.
      </div>
      <div className="mt-2 space-y-1 text-[12px] text-white/55">
        <div>·&nbsp; pitch_deck.pdf</div>
        <div>·&nbsp; founders.md</div>
        <div>·&nbsp; market.txt</div>
      </div>

      <Divider />

      <SectionLabel>Related</SectionLabel>
      <div className="mt-2 space-y-1 text-[12px] text-white/55">
        <div>·&nbsp; agent-evaluation.md</div>
        <div>·&nbsp; triage-rubric.py</div>
      </div>
    </div>
  );
}

export function LauncherMockup() {
  return (
    <div
      className="
        w-full max-w-[860px] mx-auto rounded-2xl overflow-hidden
        backdrop-blur-2xl
        border border-white/[0.08]
        shadow-cinematic
      "
      style={{ background: "rgba(15, 17, 21, 0.92)" }}
    >
      {/* Search input row */}
      <div className="flex items-center gap-3 px-6 h-[60px] border-b border-white/[0.06]">
        <input
          defaultValue="that healthcare startup idea from last winter"
          readOnly
          className="bg-transparent text-white text-[17px] flex-1 outline-none placeholder:text-white/30 caret-white"
          aria-label="Search your memory"
        />
        <kbd className="text-[11px] text-white/40 px-2 py-1 rounded border border-white/10 bg-white/[0.03] font-sans tracking-wide">
          Ctrl + Space
        </kbd>
      </div>

      {/* Body — results list (left) + preview pane (right) */}
      <div className="flex" style={{ minHeight: 480 }}>
        {/* Results list */}
        <div className="w-[320px] py-2">
          {memories.map((m, i) => (
            <MemoryRow key={i} memory={m} />
          ))}
        </div>

        {/* Preview pane */}
        <div
          className="flex-1 px-5 py-4 border-l border-white/[0.06] hidden md:block"
          style={{ background: "rgba(22, 25, 34, 0.35)" }}
        >
          <PreviewContent />
        </div>
      </div>

      {/* Footer */}
      <div
        className="px-5 h-[34px] flex items-center justify-center border-t border-white/[0.06]"
        style={{ background: "rgba(22, 25, 34, 0.55)" }}
      >
        <span className="text-[11px] text-white/35 tracking-wide">
          ↑↓ navigate&nbsp;&nbsp;·&nbsp;&nbsp;↵ open
          &nbsp;&nbsp;·&nbsp;&nbsp;Ctrl + ↵ reveal
          &nbsp;&nbsp;·&nbsp;&nbsp;Ctrl + M copy memory
          &nbsp;&nbsp;·&nbsp;&nbsp;Esc close
        </span>
      </div>
    </div>
  );
}
