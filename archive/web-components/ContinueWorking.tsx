"use client";

import { motion } from "framer-motion";

const ease = [0.32, 0.72, 0, 1] as const;

/**
 * Continue where you left off — the emotional payoff.
 *
 * The brief frames this section as "quietly magical": restoring
 * unfinished work across browser, chats, files, and searches in
 * one calm surface. The visual proves it by rendering the actual
 * launcher digest section — the same rows, the same dim time
 * labels, the same hairline rail. Marketing surface and product
 * surface speak the same language.
 *
 * Phase 4A surgical pass:
 *   1. Icon-chip column replaces the lavender-rail-plus-dot
 *      treatment. Reads more like a row in the actual launcher.
 *   2. "Restored" pill on the live row so the reader sees the
 *      product's labelling convention before they install it.
 *   3. Header carries the `Ctrl + Space` kbd chip — same shortcut
 *      the launcher itself binds. The marketing site and the
 *      keyboard contract finally agree on screen.
 *   4. Footer status line: "12 active threads", quiet pulsing
 *      indicator. Honest, infrastructural, no dopamine.
 */

type Row = {
  title: string;
  subtitle: string;
  kind: "browser" | "chat" | "file" | "search";
  /** Phase 4A: the row currently in the restored state.
   *  Mirrors the launcher's `RecoveryRow` after a successful
   *  one-click restore. */
  restored?: boolean;
};

const ROWS: Row[] = [
  {
    title: "WebSocket retry on disconnect — best practices",
    subtitle: "stackoverflow.com  ·  3 days  ·  4 tabs · 2 files · 1 chat",
    kind: "browser",
    restored: true,
  },
  {
    title: "RLHF reward shaping conversation",
    subtitle: "Claude  ·  yesterday  ·  14 messages",
    kind: "chat",
  },
  {
    title: "~/code/websocket-retry/client.py",
    subtitle: "4 opens this week",
    kind: "file",
  },
];

/* ─────────────────────────────────────────────────────────────
 *  Icon-chip column (Phase 4A).
 *  A small rounded square that holds a glyph appropriate to the
 *  row's surface kind. Replaces the rail+dot pattern; reads
 *  closer to the launcher's `RecoveryRow` rendering and to the
 *  cinematic mockup the design pass referenced.
 * ───────────────────────────────────────────────────────────── */

function KindGlyph({ kind }: { kind: Row["kind"] }) {
  // Two-tone treatment: a soft lavender ground, the existing
  // glyph SVGs (kept minimal — stroke-only, 1.4 px).
  const stroke = "currentColor";
  if (kind === "browser") {
    return (
      <svg viewBox="0 0 20 20" fill="none" stroke={stroke} strokeWidth="1.4"
           strokeLinecap="round" strokeLinejoin="round">
        <rect x="3" y="4" width="14" height="12" rx="1.5" />
        <path d="M3 7h14" />
        <path d="M6 5.5h.01M8 5.5h.01" />
      </svg>
    );
  }
  if (kind === "chat") {
    return (
      <svg viewBox="0 0 20 20" fill="none" stroke={stroke} strokeWidth="1.4"
           strokeLinecap="round" strokeLinejoin="round">
        <path d="M4 5h12a1 1 0 0 1 1 1v7a1 1 0 0 1-1 1H9l-3.5 2.5V14H4a1 1 0 0 1-1-1V6a1 1 0 0 1 1-1z" />
      </svg>
    );
  }
  if (kind === "file") {
    return (
      <svg viewBox="0 0 20 20" fill="none" stroke={stroke} strokeWidth="1.4"
           strokeLinecap="round" strokeLinejoin="round">
        <path d="M5 3h7l3 3v10a1 1 0 0 1-1 1H5a1 1 0 0 1-1-1V4a1 1 0 0 1 1-1z" />
        <path d="M12 3v3h3" />
      </svg>
    );
  }
  // search
  return (
    <svg viewBox="0 0 20 20" fill="none" stroke={stroke} strokeWidth="1.4"
         strokeLinecap="round" strokeLinejoin="round">
      <circle cx="9" cy="9" r="5" />
      <path d="M13 13l3 3" />
    </svg>
  );
}

function KindIconChip({ kind }: { kind: Row["kind"] }) {
  return (
    <div
      aria-hidden
      className="
        shrink-0 w-9 h-9 rounded-lg
        flex items-center justify-center
        bg-lavender/[0.10] border border-lavender/[0.18]
        text-lavender-deep
      "
    >
      <div className="w-4 h-4">
        <KindGlyph kind={kind} />
      </div>
    </div>
  );
}

/* ─────────────────────────────────────────────────────────────
 *  Time label — right-aligned mono, deliberately quiet.
 * ───────────────────────────────────────────────────────────── */

function TimeLabel({ value }: { value: string }) {
  return (
    <span className="
      shrink-0 font-mono text-[10px] tracking-[0.05em] uppercase
      text-ink-dim
    ">
      {value}
    </span>
  );
}

const ROW_TIMES = ["2m ago", "45m ago", "yesterday"];

export function ContinueWorking() {
  return (
    <section
      id="continue"
      className="relative py-24 md:py-28 px-5 md:px-8 overflow-hidden"
    >
      <div className="max-w-[1280px] mx-auto">
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-12 lg:gap-16 items-start">
          {/* ── Left: copy ───────────────────────────────────────── */}
          <div className="lg:col-span-5">
            <motion.div
              initial={{ opacity: 0, y: 8 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true, margin: "-100px" }}
              transition={{ duration: 0.55, ease }}
              className="text-[10.5px] font-semibold tracking-[0.20em] text-lavender-deep uppercase"
            >
              Continue where you left off
            </motion.div>

            <motion.h2
              initial={{ opacity: 0, y: 12 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true, margin: "-100px" }}
              transition={{ duration: 0.6, ease, delay: 0.06 }}
              className="
                font-editorial mt-3
                text-[32px] md:text-[44px]
                font-medium tracking-editorial leading-[1.05]
                text-ink-bright
              "
            >
              Open the launcher.
              <br />
              <span className="italic">Find yourself.</span>
            </motion.h2>

            <motion.p
              initial={{ opacity: 0, y: 6 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true, margin: "-100px" }}
              transition={{ duration: 0.5, ease, delay: 0.12 }}
              className="mt-5 text-ink leading-relaxed text-[15px] max-w-md"
            >
              An empty query brings a quiet digest: the threads you
              keep coming back to, the moment you closed yesterday,
              the file you almost finished. Nothing arrives at random.
              Every row is something you already started.
            </motion.p>

            {/* Kbd chip (Phase 4A — matches the chip in the
                launcher mockup's header so the keyboard contract
                reads identically on both surfaces). */}
            <motion.div
              initial={{ opacity: 0 }}
              whileInView={{ opacity: 1 }}
              viewport={{ once: true, margin: "-100px" }}
              transition={{ duration: 0.5, ease, delay: 0.2 }}
              className="
                mt-7 flex items-center gap-2
                text-[11px] font-mono text-ink-dim tracking-[0.05em]
              "
            >
              <span
                className="
                  min-w-[28px] h-7 px-2 flex items-center justify-center
                  rounded-md border border-hairline bg-white
                  text-ink-bright font-semibold
                "
              >
                Ctrl
              </span>
              <span className="opacity-50 text-ink-dim">+</span>
              <span
                className="
                  min-w-[28px] h-7 px-2 flex items-center justify-center
                  rounded-md border border-hairline bg-white
                  text-ink-bright font-semibold
                "
              >
                Space
              </span>
              <span className="ml-2 opacity-70">
                — opens the launcher anywhere
              </span>
            </motion.div>
          </div>

          {/* ── Right: launcher-style digest panel ──────────────── */}
          <div className="lg:col-span-7">
            <motion.div
              initial={{ opacity: 0, y: 18 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true, margin: "-80px" }}
              transition={{ duration: 0.7, ease, delay: 0.1 }}
              className="
                relative rounded-2xl bg-white edge-highlight
                overflow-hidden
              "
            >
              {/* Faux command-bar header. Phase 4A: the right side
                  now carries a Ctrl + Space kbd chip — same
                  binding the launcher actually uses. */}
              <div className="border-b border-hairline px-5 py-3 flex items-center gap-3">
                <div className="flex items-center gap-1.5">
                  <span
                    className="w-2 h-2 rounded-full"
                    style={{ background: "rgba(214, 120, 150, 0.55)" }}
                  />
                  <span
                    className="w-2 h-2 rounded-full"
                    style={{ background: "rgba(199, 151, 60, 0.55)" }}
                  />
                  <span
                    className="w-2 h-2 rounded-full"
                    style={{ background: "rgba(135, 222, 183, 0.65)" }}
                  />
                </div>
                <div
                  className="
                    flex-1 h-7 rounded-md border border-hairline
                    bg-[#FBF8F4]/80 flex items-center px-3
                  "
                >
                  <span className="font-mono text-[11.5px] text-ink-dim">
                    Recall &mdash; <span className="text-ink-bright">empty query</span>
                  </span>
                </div>
                <div className="flex items-center gap-1">
                  <span
                    className="
                      min-w-[22px] h-5 px-1.5 flex items-center justify-center
                      rounded border border-hairline bg-[#FBF8F4]/80
                      font-mono text-[9px] text-ink-bright font-semibold uppercase
                      tracking-[0.05em]
                    "
                  >
                    Ctrl
                  </span>
                  <span
                    className="
                      min-w-[22px] h-5 px-1.5 flex items-center justify-center
                      rounded border border-hairline bg-[#FBF8F4]/80
                      font-mono text-[9px] text-ink-bright font-semibold uppercase
                      tracking-[0.05em]
                    "
                  >
                    Space
                  </span>
                </div>
              </div>

              {/* Section label */}
              <div className="px-5 pt-5 pb-3 flex items-center justify-between">
                <span className="text-[10.5px] font-semibold tracking-[0.18em] text-lavender-deep uppercase">
                  Continue where you left off
                </span>
                <span className="font-mono text-[9.5px] text-ink-dim tracking-[0.05em] uppercase">
                  3 candidates
                </span>
              </div>

              {/* The three rows. Phase 4A treatment: icon chip on
                  the left, two-line title block, a small RESTORED
                  pill on the live row, right-aligned time label. */}
              <div className="divide-y divide-hairline">
                {ROWS.map((row, i) => (
                  <motion.div
                    key={row.title}
                    initial={{ opacity: 0, y: 4 }}
                    whileInView={{ opacity: 1, y: 0 }}
                    viewport={{ once: true, margin: "-40px" }}
                    transition={{
                      duration: 0.45,
                      ease,
                      delay: 0.25 + i * 0.07,
                    }}
                    className="
                      relative px-5 py-3
                      flex items-center gap-4
                      transition-colors duration-200
                      hover:bg-[#FBF8F4]/40
                    "
                  >
                    <KindIconChip kind={row.kind} />

                    <div className="min-w-0 flex-1">
                      <div className="flex items-center gap-2 flex-wrap">
                        <span className="text-[13px] font-medium text-ink-bright truncate tracking-tight max-w-full">
                          {row.title}
                        </span>
                        {row.restored && (
                          <span
                            className="
                              shrink-0
                              text-[8.5px] font-bold tracking-[0.1em]
                              text-lavender-deep
                              bg-lavender/[0.08] border border-lavender/[0.20]
                              px-2 py-0.5 rounded-full uppercase
                            "
                          >
                            Restored
                          </span>
                        )}
                      </div>
                      <div className="text-[11px] text-ink-dim mt-0.5 truncate">
                        {row.subtitle}
                      </div>
                    </div>

                    <TimeLabel value={ROW_TIMES[i] || ""} />
                  </motion.div>
                ))}
              </div>

              {/* Footer — Phase 4A: now mirrors the launcher's own
                  "X active threads" indicator (the same /v1/threads
                  count, surfaced under the digest in calmest mono).
                  The pulsing dot is the only animated element in
                  the card, and it's barely-there. */}
              <motion.div
                initial={{ opacity: 0 }}
                whileInView={{ opacity: 1 }}
                viewport={{ once: true, margin: "-40px" }}
                transition={{ duration: 0.5, ease, delay: 0.7 }}
                className="
                  border-t border-hairline px-5 py-3
                  flex items-center justify-between
                  text-[10.5px] text-ink-dim
                "
              >
                <span className="font-mono tracking-tight">
                  /v1/recovery/recent  ·  /v1/threads/recent
                </span>
                <span className="flex items-center gap-2">
                  <span
                    aria-hidden
                    className="w-1.5 h-1.5 rounded-full bg-lavender-deep animate-pulse"
                    style={{ animationDuration: "2.4s" }}
                  />
                  <span className="font-mono tracking-[0.08em] uppercase font-semibold text-lavender-deep">
                    12 active threads
                  </span>
                </span>
              </motion.div>
            </motion.div>
          </div>
        </div>
      </div>
    </section>
  );
}
