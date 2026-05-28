"use client";

// Phase 11B — /docs route. Single long-scroll page, 8 sections,
// same v2 design language as the landing. Sticky sidebar nav on
// the left; content column on the right. No new aesthetic.

import * as React from "react";
import Link from "next/link";
import { Nav } from "../components/v2/Nav";
import { Footer } from "../components/v2/Footer";
import { Mark } from "../components/v2/icons";

type SectionDef = {
  id: string;
  number: string;
  title: string;
};

const SECTIONS: SectionDef[] = [
  { id: "what",         number: "01", title: "What is Recall" },
  { id: "capture",      number: "02", title: "How capture works" },
  { id: "investigations", number: "03", title: "Investigations" },
  { id: "recovery",     number: "04", title: "Recovery" },
  { id: "resume",       number: "05", title: "Resume" },
  { id: "local-first",  number: "06", title: "Local-first" },
  { id: "extension",    number: "07", title: "Extension" },
  { id: "cli",          number: "08", title: "CLI" },
];

export default function DocsPage() {
  const [active, setActive] = React.useState<string>(SECTIONS[0].id);

  React.useEffect(() => {
    const io = new IntersectionObserver(
      (entries) => {
        for (const e of entries) {
          if (e.isIntersecting) setActive(e.target.id);
        }
      },
      { rootMargin: "-30% 0px -60% 0px", threshold: [0, 0.5, 1] },
    );
    SECTIONS.forEach((s) => {
      const el = document.getElementById(s.id);
      if (el) io.observe(el);
    });
    return () => io.disconnect();
  }, []);

  return (
    <div className="v2-root" style={{ position: "relative", minHeight: "100vh" }}>
      <Nav />
      <main>
        <div
          style={{
            position: "relative",
            paddingTop: 140,
            paddingBottom: 80,
          }}
        >
          {/* atmospheric bloom */}
          <div
            style={{
              position: "absolute",
              inset: 0,
              pointerEvents: "none",
              background:
                "radial-gradient(ellipse 50% 40% at 50% 0%, rgba(139,127,227,0.16), transparent 60%)",
            }}
          />

          <div
            style={{
              position: "relative",
              maxWidth: 1320,
              margin: "0 auto",
              padding: "0 32px 40px",
              textAlign: "center",
            }}
          >
            <div
              className="v2-eyebrow"
              style={{ justifyContent: "center", marginBottom: 18 }}
            >
              Documentation · v0.1 alpha
            </div>
            <h1
              style={{
                fontSize: "clamp(40px, 6vw, 72px)",
                fontWeight: 500,
                letterSpacing: "-0.032em",
                lineHeight: 1.02,
                margin: "0 auto 18px",
                maxWidth: 880,
              }}
            >
              How Recall <span className="v2-serif-italic">remembers</span> for you.
            </h1>
            <p
              className="v2-section-sub"
              style={{ margin: "0 auto", maxWidth: 600 }}
            >
              Eight short reads, top to bottom. Skim with the rail
              on the left; jump in anywhere. Everything Recall sees
              lives on your machine.
            </p>
          </div>

          <div
            style={{
              maxWidth: 1320,
              margin: "0 auto",
              padding: "32px 32px 0",
              display: "grid",
              gridTemplateColumns: "240px minmax(0, 1fr)",
              gap: 56,
              alignItems: "start",
            }}
            className="v2-docs-grid"
          >
            {/* sidebar */}
            <aside
              className="v2-docs-rail"
              style={{
                position: "sticky",
                top: 100,
                alignSelf: "start",
              }}
            >
              <div
                style={{
                  fontFamily: "var(--font-mono)",
                  fontSize: 10.5,
                  letterSpacing: "0.18em",
                  textTransform: "uppercase",
                  color: "var(--faint)",
                  marginBottom: 14,
                  padding: "0 6px",
                }}
              >
                Contents
              </div>
              <ul style={{ listStyle: "none", padding: 0, margin: 0 }}>
                {SECTIONS.map((s) => {
                  const isActive = s.id === active;
                  return (
                    <li key={s.id}>
                      <a
                        href={`#${s.id}`}
                        onClick={(e) => {
                          e.preventDefault();
                          document
                            .getElementById(s.id)
                            ?.scrollIntoView({ behavior: "smooth", block: "start" });
                        }}
                        style={{
                          display: "flex",
                          alignItems: "center",
                          gap: 12,
                          padding: "8px 12px",
                          borderRadius: 8,
                          textDecoration: "none",
                          color: isActive ? "var(--text)" : "var(--muted)",
                          background: isActive
                            ? "rgba(139,127,227,0.10)"
                            : "transparent",
                          border: "1px solid " + (isActive ? "rgba(139,127,227,0.22)" : "transparent"),
                          transition: "color 180ms ease, background 180ms ease, border-color 180ms ease",
                          fontSize: 13.5,
                          letterSpacing: "-0.005em",
                        }}
                      >
                        <span
                          style={{
                            fontFamily: "var(--font-mono)",
                            fontSize: 10.5,
                            color: isActive ? "var(--accent)" : "var(--dim)",
                            letterSpacing: "0.06em",
                          }}
                        >
                          {s.number}
                        </span>
                        <span>{s.title}</span>
                      </a>
                    </li>
                  );
                })}
              </ul>

              <div
                style={{
                  marginTop: 28,
                  padding: "14px 14px",
                  border: "1px solid var(--hairline)",
                  borderRadius: 12,
                  background: "rgba(255,255,255,0.02)",
                }}
              >
                <div
                  style={{
                    fontFamily: "var(--font-mono)",
                    fontSize: 10.5,
                    letterSpacing: "0.14em",
                    textTransform: "uppercase",
                    color: "var(--faint)",
                    marginBottom: 8,
                  }}
                >
                  Repo
                </div>
                <a
                  href="https://github.com/kunalKumar-13/Recall-me"
                  target="_blank"
                  rel="noopener noreferrer"
                  style={{
                    display: "inline-flex",
                    alignItems: "center",
                    gap: 8,
                    color: "var(--text-2)",
                    textDecoration: "none",
                    fontSize: 13,
                  }}
                >
                  <Mark size={16} />
                  Recall on GitHub
                </a>
              </div>
            </aside>

            {/* content */}
            <article
              style={{
                position: "relative",
                color: "var(--text-2)",
                fontSize: 15,
                lineHeight: 1.7,
                letterSpacing: "-0.003em",
              }}
            >
              <DocsSection id="what" number="01" title="What is Recall">
                <p>
                  Recall is a <strong style={{ color: "var(--text)" }}>local-first continuity operating system</strong>{" "}
                  — a small daemon that reconstructs what you were mentally working on across your files, browser tabs, chat tools, and time.
                </p>
                <p>
                  It is not an AI memory assistant, not semantic search, not a productivity dashboard, not a chatbot, and not an agent framework. The product makes exactly one claim:
                </p>
                <Pullquote>
                  A continuity layer for your own thinking is only useful if it stays on your machine.
                </Pullquote>
                <p>
                  Every architectural decision serves that claim. Captured events live in plain JSONL under <Code>~/.recall/</Code>, the loopback API binds to <Code>127.0.0.1:4545</Code> only, and there is no cloud, no telemetry, no model-update ping after the first-boot embedding-model download.
                </p>
              </DocsSection>

              <DocsSection id="capture" number="02" title="How capture works">
                <p>
                  Two capture surfaces, both local:
                </p>
                <ul style={{ paddingLeft: 22, margin: "10px 0 18px" }}>
                  <li><strong style={{ color: "var(--text)" }}>Browser extension</strong> — fires on tab completion, posts a tiny JSON envelope to the loopback API.</li>
                  <li><strong style={{ color: "var(--text)" }}>Desktop watcher</strong> — observes focused-window changes on the OS. No screenshots, no OCR, no pixel data — only the active app name and window title.</li>
                </ul>
                <p>
                  Each surface emits one of a small set of <strong style={{ color: "var(--text)" }}>event kinds</strong>:
                </p>
                <CodeBlock>
{`browser_visit       tab loaded
browser_search      a query against Google / DDG / Bing / etc.
chat_session        a session on ChatGPT / Claude / Gemini / …
open                a local file was opened
query               a Recall search ran
desktop_window      a foreground-window switch`}
                </CodeBlock>
                <p>
                  Events land at <Code>~/.recall/events/YYYY-MM-DD.jsonl</Code> in append-only mode. Every row is hand-readable. Delete the folder, Recall is gone.
                </p>
              </DocsSection>

              <DocsSection id="investigations" number="03" title="Investigations">
                <p>
                  Raw events are noisy. Investigations are the layer that turns them into something a human recognises.
                </p>
                <p>
                  An investigation is a coherent topic-coherent slice across multiple sessions. The engine groups events by topic-key (URL host, file path, search-query fragments) and trims by recency. A thread crosses the investigation threshold when it has ≥ 4 events on the same topic-key within a 14-day window.
                </p>
                <p>
                  Each investigation carries a <Code>strength</Code> signal — high / med / low — derived from event count, surface diversity (files + tabs + chats counts more than one of any single kind), and dwell time. The launcher renders the top three under <em>OTHER WORK</em>.
                </p>
              </DocsSection>

              <DocsSection id="recovery" number="04" title="Recovery">
                <p>
                  Recovery is the moment Recall earns its keep. When you return after an absence, the engine asks: <em>is there a coherent thread the user was mid-work on, that hasn&apos;t been closed?</em>
                </p>
                <p>
                  A candidate becomes a recovery if it clears three gates:
                </p>
                <ul style={{ paddingLeft: 22, margin: "10px 0 18px" }}>
                  <li>At least 4 distinct targets (files + tabs + chats).</li>
                  <li>Trust score ≥ 0.55 (calibrated in Phase 4E).</li>
                  <li>Not currently flagged in <Code>~/.recall/bad_recoveries.jsonl</Code> (the dismissal ledger that suppresses cards a user has rejected).</li>
                </ul>
                <p>
                  At most one Continue card surfaces at a time. <em>An inbox is forbidden.</em>
                </p>
              </DocsSection>

              <DocsSection id="resume" number="05" title="Resume">
                <p>
                  Click Resume (or press <Kbdish>⏎</Kbdish>) and the launcher hands the recovery&apos;s ordered target list to the OS:
                </p>
                <ul style={{ paddingLeft: 22, margin: "10px 0 18px" }}>
                  <li>Files open in your default editor.</li>
                  <li>Tabs reopen in the browser, in original order.</li>
                  <li>Chat sessions resume at the conversation URL.</li>
                </ul>
                <p>
                  The launcher then transitions to the <em>Restored</em> state — a check disc, the title, and a per-target list with <Code>OPENED</Code> / <Code>RESTORED</Code> status pills. <Kbdish>Undo</Kbdish> reverses the open; <Kbdish>Done</Kbdish> dismisses and returns control to you.
                </p>
                <p>
                  Median plan execution: under 500 ms on a 10K-event store. Per the budgets in <Code>CLAUDE.md</Code>.
                </p>
              </DocsSection>

              <DocsSection id="local-first" number="06" title="Local-first">
                <p>
                  Everything Recall sees stays on your disk, in plain text. Four guarantees:
                </p>
                <ul style={{ paddingLeft: 22, margin: "10px 0 18px" }}>
                  <li><strong style={{ color: "var(--text)" }}>Local only</strong> — every event, embedding, and index lives in <Code>~/.recall/</Code>. Auditable with <Code>cat</Code>.</li>
                  <li><strong style={{ color: "var(--text)" }}>No cloud</strong> — the HTTP API binds to <Code>127.0.0.1:4545</Code>. Verify with <Code>lsof -i :4545</Code>.</li>
                  <li><strong style={{ color: "var(--text)" }}>No telemetry</strong> — no analytics, no error reporting, no model-update pings. ChromaDB telemetry is disabled at boot.</li>
                  <li><strong style={{ color: "var(--text)" }}>Export anytime</strong> — JSONL is the export. Delete the folder and Recall is gone.</li>
                </ul>
                <p>
                  The only outbound network call in Recall&apos;s lifetime is the first-boot embedding-model download (~80 MB from Hugging Face). After that, every byte stays local.
                </p>
              </DocsSection>

              <DocsSection id="extension" number="07" title="Extension">
                <p>
                  The browser extension is the second capture surface. MV3, ~200 lines of JavaScript, no content scripts. It watches <Code>tabs.onUpdated</Code>, classifies each completed load (chat / search / generic visit), and POSTs a small envelope to the loopback API.
                </p>
                <p>
                  Capture is universal — every visit fires — and classification is opt-in per host. Phase 8F-A (Track A) added a title-settle defer so SPA titles like ChatGPT&apos;s conversation header are captured after they finalize, not before:
                </p>
                <CodeBlock>
{`SETTLE_MS    = 1500    // wait this long after the last update
MAX_WAIT_MS  = 4000    // ceiling so a title-poking tab still fires`}
                </CodeBlock>
                <p>
                  Modern AI chat platforms recognized as <Code>chat_session</Code> (rather than generic <Code>browser_visit</Code>): ChatGPT, Claude, Gemini (incl. AI Studio), Copilot, Mistral chat, DeepSeek, Grok, Poe, t3.chat.
                </p>
                <p>
                  Install the unpacked extension via <Code>chrome://extensions → Developer mode → Load unpacked → apps/extension/</Code>.
                </p>
              </DocsSection>

              <DocsSection id="cli" number="08" title="CLI">
                <p>
                  Nine operator commands, all read-only or sandboxed, all stdlib-only:
                </p>
                <CodeBlock>
{`recall doctor              5 GREEN / N YELLOW health check
recall stats               counts report (read-only)
recall capture status      events today + kind breakdown
recall capture tail [N]    last N events as JSONL
recall inspect <id>        why a candidate did or didn't surface
recall trust review        bad-recovery ledger + resume rates
recall demo run/reset      seed/clear the deterministic demo log
recall alpha review        Phase 8E evidence-board (cohort)
recall founder status      operator overview`}
                </CodeBlock>
                <p>
                  All nine work without booting the launcher. The demo CLI in particular writes only to <Code>~/.recall/events-demo/</Code>, never the real event log — boundary enforced by the seed module.
                </p>
                <p>
                  Full reference: see <Code>recall.py --help</Code> on a working install, or browse the source at{" "}
                  <a
                    href="https://github.com/kunalKumar-13/Recall-me/tree/main/app/core"
                    target="_blank"
                    rel="noopener noreferrer"
                    style={{ color: "var(--accent)", textDecoration: "none" }}
                  >
                    app/core/
                  </a>
                  .
                </p>
              </DocsSection>

              <div
                style={{
                  marginTop: 40,
                  padding: "26px 28px",
                  border: "1px solid var(--hairline)",
                  borderRadius: 14,
                  background:
                    "linear-gradient(180deg, rgba(139,127,227,0.06), rgba(139,127,227,0.02))",
                }}
              >
                <div className="v2-eyebrow" style={{ marginBottom: 10 }}>
                  Next
                </div>
                <div style={{ fontSize: 19, fontWeight: 500, letterSpacing: "-0.014em", marginBottom: 10 }}>
                  Pick up the alpha cohort docs in the repo.
                </div>
                <p style={{ margin: 0, color: "var(--muted)", fontSize: 14, lineHeight: 1.65 }}>
                  The on-disk handbook lives under <Code>alpha/pack/</Code> in the repo —{" "}
                  <a
                    href="https://github.com/kunalKumar-13/Recall-me/tree/main/alpha/pack"
                    target="_blank"
                    rel="noopener noreferrer"
                    style={{ color: "var(--accent)", textDecoration: "none" }}
                  >
                    WELCOME · INSTALL · DAY0 · DAY1 · DAY3 · FEEDBACK · UNINSTALL
                  </a>
                  . That set is the source of truth; this page is the public mirror.
                </p>
                <div style={{ marginTop: 20, display: "flex", gap: 10, flexWrap: "wrap" }}>
                  <Link href="/" className="v2-btn-ghost">
                    ← Back to landing
                  </Link>
                  <a
                    href="https://github.com/kunalKumar-13/Recall-me"
                    target="_blank"
                    rel="noopener noreferrer"
                    className="v2-btn-primary"
                    style={{ height: 40, fontSize: 13.5 }}
                  >
                    Open the repo →
                  </a>
                </div>
              </div>
            </article>
          </div>
        </div>
      </main>
      <Footer />

      <style jsx>{`
        @media (max-width: 1000px) {
          .v2-docs-grid {
            grid-template-columns: 1fr !important;
            gap: 32px !important;
          }
          .v2-docs-rail {
            position: relative !important;
            top: auto !important;
          }
        }
      `}</style>
    </div>
  );
}

function DocsSection({
  id,
  number,
  title,
  children,
}: {
  id: string;
  number: string;
  title: string;
  children: React.ReactNode;
}) {
  return (
    <section
      id={id}
      style={{
        scrollMarginTop: 90,
        padding: "44px 0 28px",
        borderTop: "1px solid var(--hairline)",
      }}
    >
      <div
        style={{
          fontFamily: "var(--font-mono)",
          fontSize: 10.5,
          letterSpacing: "0.18em",
          textTransform: "uppercase",
          color: "var(--primary)",
          marginBottom: 10,
        }}
      >
        {number} · doc
      </div>
      <h2
        style={{
          fontSize: 32,
          fontWeight: 500,
          letterSpacing: "-0.022em",
          lineHeight: 1.1,
          color: "var(--text)",
          margin: "0 0 22px",
        }}
      >
        {title}
      </h2>
      <div style={{ display: "flex", flexDirection: "column", gap: 14 }}>
        {children}
      </div>
    </section>
  );
}

function Code({ children }: { children: React.ReactNode }) {
  return (
    <code
      style={{
        fontFamily: "var(--font-mono)",
        fontSize: 13,
        color: "var(--accent)",
        background: "rgba(139,127,227,0.10)",
        padding: "1px 6px",
        borderRadius: 4,
      }}
    >
      {children}
    </code>
  );
}

function CodeBlock({ children }: { children: React.ReactNode }) {
  return (
    <pre
      style={{
        margin: "8px 0 4px",
        padding: "16px 18px",
        background: "rgba(0,0,0,0.40)",
        border: "1px solid var(--hairline)",
        borderRadius: 10,
        fontFamily: "var(--font-mono)",
        fontSize: 12.5,
        lineHeight: 1.6,
        color: "var(--text-2)",
        letterSpacing: "0.01em",
        whiteSpace: "pre",
        overflowX: "auto",
      }}
    >
      {children}
    </pre>
  );
}

function Kbdish({ children }: { children: React.ReactNode }) {
  return (
    <span
      style={{
        fontFamily: "var(--font-mono)",
        fontSize: 11.5,
        color: "var(--muted)",
        background: "rgba(255,255,255,0.04)",
        border: "1px solid var(--hairline)",
        padding: "1px 6px",
        borderRadius: 4,
        margin: "0 2px",
        letterSpacing: "0.02em",
      }}
    >
      {children}
    </span>
  );
}

function Pullquote({ children }: { children: React.ReactNode }) {
  return (
    <blockquote
      style={{
        margin: "20px 0",
        padding: "16px 22px",
        borderLeft: "2px solid var(--primary)",
        background: "rgba(139,127,227,0.06)",
        borderRadius: "0 10px 10px 0",
        fontSize: 16.5,
        fontWeight: 500,
        color: "var(--text)",
        letterSpacing: "-0.008em",
        lineHeight: 1.5,
      }}
    >
      {children}
    </blockquote>
  );
}
