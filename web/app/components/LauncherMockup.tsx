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
    ext: { label: "PDF", color: "#EF4444" },
    title: "Healthcare agents pitch deck",
    why: "Covers healthcare, agents, and triage.",
    pill: { text: "Highly relevant", color: "#10B981" },
    cluster: 2,
    resurfaced: "resurfaced from Jan 2024",
    selected: true,
  },
  {
    ext: { label: "PY", color: "#7C9BFF" },
    title: "def TriageAgent",
    why: "Discusses agent and triage.",
    pill: { text: "Relevant", color: "#8BA5FF" },
  },
  {
    ext: { label: "MD", color: "#A78BFA" },
    title: "Onboarding flow notes",
    why: "Mentions onboarding and intake.",
    pill: { text: "Relevant", color: "#8BA5FF" },
  },
  {
    ext: { label: "TXT", color: "#94A3B8" },
    title: "Market sizing draft",
    why: "Mentions healthcare.",
    pill: { text: "Possible match", color: "#94A3B8" },
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
        background: "rgba(124, 155, 255, 0.14)",
        color: "#AFC2FF",
        border: "1px solid rgba(124, 155, 255, 0.32)",
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
          ? "rgba(50, 60, 92, 0.55)"
          : "transparent",
      }}
    >
      <ExtTag label={memory.ext.label} color={memory.ext.color} />
      <div className="flex-1 min-w-0">
        <div className="text-[13px] font-semibold text-ink-bright truncate">
          {memory.title}
        </div>
        <div className="flex items-center gap-2 mt-1">
          <div className="text-[11px] text-ink-dim truncate flex-1">
            {memory.why}
            {memory.resurfaced && (
              <span className="text-ink-dim/80">
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
    <div className="text-[11px] font-semibold tracking-wide text-ink-dim">
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
      <div className="text-[16px] font-semibold text-ink-bright mt-1.5 tracking-tight">
        Healthcare agents pitch deck
      </div>
      <div className="text-[11px] text-ink-dim mt-1 truncate">
        ~/Documents/healthcare-v3/pitch_deck.pdf
      </div>
      <div className="text-[11px] italic text-ink-dim/85 mt-1">
        Last seen Jan 2024
      </div>

      <Divider />

      <SectionLabel>About</SectionLabel>
      <div className="text-[12px] text-ink mt-1.5 leading-relaxed">
        You explored a healthcare agent triage system last winter — an
        onboarding flow that routed pediatric patients via natural-language
        intake.
      </div>

      <Divider />

      <SectionLabel>Excerpt</SectionLabel>
      <div className="text-[12px] italic text-ink/80 mt-1.5 leading-[1.65]">
        …routing{" "}
        <b className="text-ink-bright not-italic">pediatric</b> patients via
        natural-language intake, with the{" "}
        <b className="text-ink-bright not-italic">agent</b> classifying
        urgency and matching to specialists. The team explored{" "}
        <b className="text-ink-bright not-italic">healthcare</b>-specific
        evaluation rubrics for triage accuracy…
      </div>

      <Divider />

      <SectionLabel>Sources</SectionLabel>
      <div className="text-[11px] mt-1.5 font-medium text-accent">
        Spans PDF, MD, TXT — same idea across formats.
      </div>
      <div className="mt-2 space-y-1 text-[12px] text-ink/80">
        <div>·&nbsp; pitch_deck.pdf</div>
        <div>·&nbsp; founders.md</div>
        <div>·&nbsp; market.txt</div>
      </div>

      <Divider />

      <SectionLabel>Related</SectionLabel>
      <div className="mt-2 space-y-1 text-[12px] text-ink/80">
        <div>·&nbsp; agent-evaluation.md</div>
        <div>·&nbsp; triage-rubric.py</div>
      </div>
    </div>
  );
}

export function LauncherMockup() {
  return (
    <div className="
      w-full max-w-[940px] mx-auto rounded-2xl overflow-hidden
      surface-glass
      border border-white/[0.08]
      shadow-cinematic
    ">
      {/* Search input row */}
      <div className="flex items-center gap-3 px-6 h-[60px] border-b border-white/[0.06]">
        <input
          defaultValue="that healthcare startup idea from last winter"
          readOnly
          className="bg-transparent text-ink-bright text-[17px] flex-1 outline-none placeholder:text-ink-dim/70 caret-accent"
          aria-label="Search your memory"
        />
        <kbd className="text-[11px] text-ink-dim px-2 py-1 rounded border border-white/[0.08] bg-white/[0.03] font-sans tracking-wide">
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
        <div className="flex-1 px-5 py-4 border-l border-white/[0.06] hidden md:block surface-glass-soft">
          <PreviewContent />
        </div>
      </div>

      {/* Footer */}
      <div className="px-5 h-[34px] flex items-center justify-center border-t border-white/[0.06] bg-black/20">
        <span className="text-[11px] text-ink-dim tracking-wide">
          ↑↓ navigate&nbsp;&nbsp;·&nbsp;&nbsp;↵ open
          &nbsp;&nbsp;·&nbsp;&nbsp;Ctrl + ↵ reveal
          &nbsp;&nbsp;·&nbsp;&nbsp;Ctrl + M copy memory
          &nbsp;&nbsp;·&nbsp;&nbsp;Esc close
        </span>
      </div>
    </div>
  );
}
