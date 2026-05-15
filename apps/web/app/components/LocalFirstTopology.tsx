"use client";

import { motion } from "framer-motion";

const ease = [0.32, 0.72, 0, 1] as const;

/**
 * Local-first section — terminal / topology aesthetic.
 *
 * The previous Privacy section used pledge cards + a shield
 * illustration. The brief now asks for "terminal-like topology
 * diagrams, localhost references, JSONL/state visualizations,
 * loopback language" — and explicitly no security-marketing
 * clichés.
 *
 * This component delivers two pieces in one calm grid:
 *
 *   1. **Topology panel** — a dark `.topology-card` showing the
 *      loopback diagram in monospace. Six labelled boxes arranged
 *      as the data flow that actually exists in the codebase:
 *      Chrome extension + launcher + folder watcher → loopback API
 *      → ~/.recall.
 *   2. **State excerpt** — a small JSONL preview of what `events/
 *      2026-05-14.jsonl` actually looks like on disk. Same shape
 *      the EventLogger writes; this isn't a mockup.
 *
 * Tonal palette: graphite ink on near-black ivory inside the card,
 * lavender accents for the active connection lines, mint dots for
 * the loopback bind marker. No bloom, no glow, no animated
 * particles.
 */

export function LocalFirstTopology() {
  return (
    <section
      id="privacy"
      className="relative py-24 md:py-28 px-5 md:px-8"
    >
      <div className="max-w-[1280px] mx-auto">
        {/* ── Header ────────────────────────────────────────────── */}
        <div className="max-w-2xl">
          <motion.div
            initial={{ opacity: 0, y: 8 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true, margin: "-100px" }}
            transition={{ duration: 0.55, ease }}
            className="text-[10.5px] font-semibold tracking-[0.20em] text-lavender-deep uppercase"
          >
            Local-first
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
            The boundary
            <br />
            <span className="italic">is the bind.</span>
          </motion.h2>
          <motion.p
            initial={{ opacity: 0, y: 8 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true, margin: "-100px" }}
            transition={{ duration: 0.5, ease, delay: 0.12 }}
            className="mt-5 text-ink leading-relaxed text-[15px] max-w-lg"
          >
            Recall does not ship with a way to send your data anywhere.
            The HTTP API binds to <code className="font-mono text-ink-bright text-[13px]">127.0.0.1</code> and
            nothing else. The Chrome extension&apos;s
            {" "}<code className="font-mono text-ink-bright text-[13px]">host_permissions</code> are locked to
            the same address.
          </motion.p>
        </div>

        {/* ── Topology grid ─────────────────────────────────────── */}
        <div className="mt-14 md:mt-16 grid grid-cols-1 lg:grid-cols-12 gap-6 lg:gap-8 items-stretch">
          {/* Loopback topology panel */}
          <motion.div
            initial={{ opacity: 0, y: 14 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true, margin: "-80px" }}
            transition={{ duration: 0.7, ease }}
            className="lg:col-span-7 rounded-2xl topology-card p-6 md:p-7 font-mono"
          >
            <div className="flex items-center justify-between mb-5">
              <span
                className="text-[10.5px] tracking-[0.20em] uppercase"
                style={{ color: "rgba(232, 226, 251, 0.55)" }}
              >
                topology &mdash; 127.0.0.1:4545
              </span>
              <span
                className="flex items-center gap-1.5 text-[10.5px]"
                style={{ color: "rgba(232, 226, 251, 0.65)" }}
              >
                <span
                  aria-hidden
                  className="w-1.5 h-1.5 rounded-full"
                  style={{ background: "rgba(135, 222, 183, 0.85)" }}
                />
                bind: loopback only
              </span>
            </div>

            {/* The diagram. Three writer boxes on the left feed into
                the API box in the centre, which writes the disk
                layer on the right. Connecting hairlines are drawn
                once on view. */}
            <div className="relative">
              <TopologyDiagram />
            </div>

            <div
              className="mt-7 grid grid-cols-3 gap-3 text-[10.5px]"
              style={{ color: "rgba(232, 226, 251, 0.55)" }}
            >
              <div>
                <div className="text-[9.5px] tracking-[0.16em] uppercase mb-1 opacity-70">
                  outbound
                </div>
                <div>
                  one model download
                  <br />
                  on first run only
                </div>
              </div>
              <div>
                <div className="text-[9.5px] tracking-[0.16em] uppercase mb-1 opacity-70">
                  telemetry
                </div>
                <div>
                  none
                  <br />
                  hf + chroma off
                </div>
              </div>
              <div>
                <div className="text-[9.5px] tracking-[0.16em] uppercase mb-1 opacity-70">
                  auth
                </div>
                <div>
                  none
                  <br />
                  the bind is the boundary
                </div>
              </div>
            </div>
          </motion.div>

          {/* JSONL state excerpt */}
          <motion.div
            initial={{ opacity: 0, y: 14 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true, margin: "-80px" }}
            transition={{ duration: 0.7, ease, delay: 0.08 }}
            className="
              lg:col-span-5
              rounded-2xl bg-white edge-highlight
              p-6 md:p-7
            "
          >
            <div className="flex items-center justify-between mb-5">
              <code className="font-mono text-[11px] text-ink-bright tracking-tight">
                ~/.recall/events/2026-05-14.jsonl
              </code>
              <span className="font-mono text-[10px] text-ink-dim tracking-[0.05em] uppercase">
                jsonl
              </span>
            </div>

            <pre
              className="
                font-mono text-[10.5px] leading-[1.7]
                text-ink overflow-x-auto whitespace-pre
              "
            >
{`{"ts":"2026-05-14T09:14:02Z","kind":"browser_visit",
 "payload":{"url":"https://stackoverflow.com/q/ws-retry",
            "title":"WebSocket retry on disconnect",
            "domain":"stackoverflow.com"}}
{"ts":"2026-05-14T09:14:48Z","kind":"open",
 "payload":{"path":"~/code/ws-retry/client.py",
            "title":"client.py"}}
{"ts":"2026-05-14T09:15:11Z","kind":"chat_session",
 "payload":{"url":"https://claude.ai/chat/...",
            "title":"backoff strategy",
            "platform":"claude"}}`}
            </pre>

            <div className="mt-5 pt-5 border-t border-hairline">
              <div className="text-[10.5px] text-ink-dim leading-relaxed">
                <span className="font-mono text-ink-bright">$ cat</span> the
                file — it&apos;s plain text. Delete a line, remove a day,
                forget a week. The retrieval engine reads whatever is
                on disk.
              </div>
            </div>
          </motion.div>
        </div>
      </div>
    </section>
  );
}

/* ───────────────────────────────────────────────────────────
 *  Topology diagram — inline SVG, no animation past the
 *  draw-on enter. Drawn light-on-dark so it sits inside the
 *  `.topology-card` surface above.
 * ─────────────────────────────────────────────────────────── */

function TopologyDiagram() {
  // ViewBox dimensions. Internal coordinates are arbitrary; the
  // SVG scales to its container's width via `preserveAspectRatio`.
  const W = 720;
  const H = 240;

  // Six nodes — three writers (Chrome, Launcher, Watcher), one API
  // hub, one disk root, one disk subdir.
  const nodes = {
    chrome:   { x: 80,  y: 40,  w: 150, h: 36, label: "chrome ext.",   sub: "MV3 host=loopback" },
    launcher: { x: 80,  y: 102, w: 150, h: 36, label: "launcher",      sub: "PyQt6 (Ctrl+Space)" },
    watcher:  { x: 80,  y: 164, w: 150, h: 36, label: "watchdog",      sub: "folder events" },
    api:      { x: 295, y: 88,  w: 150, h: 62, label: "127.0.0.1:4545", sub: "uvicorn · /v1/*" },
    events:   { x: 510, y: 50,  w: 170, h: 36, label: "~/.recall/events", sub: "jsonl · per-day" },
    threads:  { x: 510, y: 110, w: 170, h: 36, label: "~/.recall/threads.json", sub: "thread identity cache" },
    chroma:   { x: 510, y: 170, w: 170, h: 36, label: "~/.recall/chroma", sub: "vector store" },
  };

  // Connection segments — left side: each writer reaches the API
  // hub. Right side: the API writes three disk paths.
  const edges: { from: keyof typeof nodes; to: keyof typeof nodes }[] = [
    { from: "chrome",   to: "api" },
    { from: "launcher", to: "api" },
    { from: "watcher",  to: "api" },
    { from: "api",      to: "events" },
    { from: "api",      to: "threads" },
    { from: "api",      to: "chroma" },
  ];

  function nodeCenter(n: keyof typeof nodes) {
    const node = nodes[n];
    return { x: node.x + node.w / 2, y: node.y + node.h / 2 };
  }

  function edgePath(from: keyof typeof nodes, to: keyof typeof nodes) {
    const f = nodes[from];
    const t = nodes[to];
    // Anchor at the right edge of `from` and left edge of `to`.
    const x1 = f.x + f.w;
    const y1 = f.y + f.h / 2;
    const x2 = t.x;
    const y2 = t.y + t.h / 2;
    // Two-segment elbow — horizontal out, then vertical to land.
    const midX = x1 + (x2 - x1) / 2;
    return `M ${x1} ${y1} L ${midX} ${y1} L ${midX} ${y2} L ${x2} ${y2}`;
  }

  return (
    <svg
      viewBox={`0 0 ${W} ${H}`}
      className="w-full"
      style={{ height: "auto" }}
      aria-hidden
    >
      {/* Edges — drawn first so nodes overlay them */}
      {edges.map((e, i) => (
        <motion.path
          key={`edge-${i}`}
          d={edgePath(e.from, e.to)}
          fill="none"
          stroke="rgba(169, 156, 247, 0.55)"
          strokeWidth={1.2}
          strokeLinecap="round"
          initial={{ pathLength: 0, opacity: 0 }}
          whileInView={{ pathLength: 1, opacity: 1 }}
          viewport={{ once: true, margin: "-60px" }}
          transition={{
            duration: 0.9,
            ease: [0.32, 0.72, 0, 1],
            delay: 0.2 + i * 0.08,
          }}
        />
      ))}

      {/* Nodes */}
      {(Object.keys(nodes) as (keyof typeof nodes)[]).map((key, i) => {
        const n = nodes[key];
        const isHub = key === "api";
        return (
          <motion.g
            key={key}
            initial={{ opacity: 0, y: 4 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true, margin: "-60px" }}
            transition={{
              duration: 0.5,
              ease: [0.32, 0.72, 0, 1],
              delay: 0.1 + i * 0.05,
            }}
          >
            <rect
              x={n.x}
              y={n.y}
              width={n.w}
              height={n.h}
              rx={6}
              ry={6}
              fill={isHub ? "rgba(169, 156, 247, 0.12)" : "rgba(255, 255, 255, 0.04)"}
              stroke={isHub ? "rgba(169, 156, 247, 0.55)" : "rgba(255, 255, 255, 0.10)"}
              strokeWidth={isHub ? 1.2 : 1}
            />
            {/* Hub gets a mint dot — same loopback-bind indicator
                used in the panel header. */}
            {isHub && (
              <circle
                cx={n.x + 12}
                cy={n.y + 12}
                r={3}
                fill="rgba(135, 222, 183, 0.85)"
              />
            )}
            <text
              x={n.x + (isHub ? 22 : 12)}
              y={n.y + 16}
              fontSize={10.5}
              fontFamily="ui-monospace, monospace"
              fontWeight={600}
              fill="rgba(232, 226, 251, 0.92)"
            >
              {n.label}
            </text>
            <text
              x={n.x + (isHub ? 22 : 12)}
              y={n.y + 28}
              fontSize={9}
              fontFamily="ui-monospace, monospace"
              fill="rgba(232, 226, 251, 0.50)"
            >
              {n.sub}
            </text>
          </motion.g>
        );
      })}
    </svg>
  );
}
