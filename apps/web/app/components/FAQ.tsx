"use client";

import { AnimatePresence, motion } from "framer-motion";
import { useState } from "react";
import { LINKS } from "../lib/links";

const ease = [0.32, 0.72, 0, 1] as const;

type QA = {
  q: string;
  a: React.ReactNode;
};

const FAQS: QA[] = [
  {
    q: "Is my data stored locally?",
    a: (
      <>
        Yes, completely. Every memory Recall captures is stored in{" "}
        <code className="font-mono text-[12.5px]">~/.recall/</code> on
        your machine. The folder is plain JSONL + a local SQLite-backed
        vector index — both human-inspectable, both deletable.
      </>
    ),
  },
  {
    q: "Does Recall use the cloud?",
    a: (
      <>
        No. The only network call Recall ever makes is the one-time
        download of the embedding model on first run. After that the
        loader runs in <code className="font-mono text-[12.5px]">local_files_only=True</code>{" "}
        mode and the app cannot reach the internet.
      </>
    ),
  },
  {
    q: "Does it work offline?",
    a: (
      <>
        After the first-run model download, fully. Searching, indexing,
        and opening files all run on your CPU, with zero network
        required.
      </>
    ),
  },
  {
    q: "Is it open source?",
    a: (
      <>
        Yes. Recall is open source under MIT —{" "}
        <a
          href={LINKS.github}
          target="_blank"
          rel="noopener noreferrer"
          className="text-lavender-deep hover:underline underline-offset-4"
        >
          github.com/kunalKumar-13/Recall-me
        </a>
        . Read the source, audit the network code, send a PR.
      </>
    ),
  },
  {
    q: "What file types work?",
    a: (
      <>
        Plain text (md, txt, rst), 30+ code formats (py, js, ts, go,
        rs, java, …), PDFs via pypdf, JSON / YAML / TOML config files,
        and CSV. Image OCR is opt-in (requires Tesseract). Anything
        not understood is silently skipped.
      </>
    ),
  },
];

function FaqRow({
  qa,
  open,
  onToggle,
}: {
  qa: QA;
  open: boolean;
  onToggle: () => void;
}) {
  return (
    <div className="border-b border-hairline last:border-b-0">
      <button
        type="button"
        onClick={onToggle}
        aria-expanded={open}
        className="
          w-full flex items-start gap-4 justify-between text-left
          py-4 group
        "
      >
        <span className="text-[14.5px] md:text-[15.5px] font-medium text-ink-bright leading-snug">
          {qa.q}
        </span>
        <span
          className={`
            shrink-0 mt-0.5 w-6 h-6 rounded-full
            border border-hairline-strong
            flex items-center justify-center
            text-ink-dim group-hover:text-lavender-deep
            transition-transform duration-300
            ${open ? "rotate-45 bg-lavender-soft text-lavender-deep border-lavender/30" : ""}
          `}
          aria-hidden
        >
          <svg viewBox="0 0 24 24" className="w-3 h-3" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round">
            <path d="M12 5v14M5 12h14" />
          </svg>
        </span>
      </button>

      <AnimatePresence initial={false}>
        {open && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: "auto", opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.32, ease }}
            className="overflow-hidden"
          >
            <div className="pb-5 pr-10 text-[13.5px] text-ink leading-relaxed">
              {qa.a}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}

function StillHaveQuestionsCard() {
  return (
    <motion.aside
      initial={{ opacity: 0, y: 8 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true, margin: "-80px" }}
      transition={{ duration: 0.55, ease, delay: 0.15 }}
      className="
        rounded-2xl
        bg-bg-base border border-hairline shadow-card
        p-7
      "
    >
      <h3 className="font-editorial text-[20px] md:text-[22px] font-medium tracking-editorial text-ink-bright leading-snug">
        Still have <span className="italic">questions?</span>
      </h3>
      <p className="mt-3 text-[13.5px] text-ink leading-relaxed">
        Join our community or open an issue on GitHub — we read every one.
      </p>
      <a
        href={LINKS.issues}
        target="_blank"
        rel="noopener noreferrer"
        className="
          mt-6 inline-flex items-center justify-center gap-2
          h-10 px-4 rounded-lg
          border border-hairline-strong text-ink-bright text-[13.5px] font-medium
          bg-bg-base hover:bg-bg-raised
          transition-colors duration-300
        "
      >
        <svg viewBox="0 0 24 24" className="w-4 h-4" fill="currentColor" aria-hidden>
          <path d="M12 .5C5.65.5.5 5.65.5 12c0 5.08 3.29 9.39 7.86 10.91.58.11.79-.25.79-.56v-2c-3.2.7-3.88-1.36-3.88-1.36-.53-1.34-1.29-1.7-1.29-1.7-1.05-.72.08-.7.08-.7 1.16.08 1.77 1.19 1.77 1.19 1.03 1.77 2.7 1.26 3.36.97.1-.75.4-1.27.74-1.56-2.55-.29-5.24-1.28-5.24-5.7 0-1.26.45-2.29 1.19-3.1-.12-.3-.52-1.47.11-3.07 0 0 .97-.31 3.18 1.18a11 11 0 0 1 5.78 0c2.21-1.49 3.18-1.18 3.18-1.18.63 1.6.23 2.77.12 3.07.74.81 1.19 1.84 1.19 3.1 0 4.43-2.69 5.4-5.26 5.69.41.36.78 1.06.78 2.14v3.17c0 .31.21.68.79.56C20.21 21.39 23.5 17.08 23.5 12c0-6.35-5.15-11.5-11.5-11.5z" />
        </svg>
        Visit GitHub
      </a>
    </motion.aside>
  );
}

/**
 * FAQ — single-open accordion on the left, "Still have questions?"
 * card on the right. Mirrors the reference layout exactly. Mobile
 * stacks: accordion first, side card below.
 */
export function FAQ() {
  const [openIdx, setOpenIdx] = useState<number | null>(0);

  return (
    <section id="faq" className="relative py-24 md:py-28 px-5 md:px-8">
      <div className="max-w-[1280px] mx-auto">
        <motion.div
          initial={{ opacity: 0, y: 8 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, margin: "-100px" }}
          transition={{ duration: 0.55, ease }}
          className="text-center max-w-2xl mx-auto mb-12"
        >
          <div className="text-[10.5px] font-semibold tracking-[0.20em] text-lavender-deep uppercase">
            FAQ
          </div>
          <h2 className="font-editorial mt-3 text-[32px] md:text-[44px] font-medium tracking-editorial text-ink-bright leading-[1.05]">
            Everything you need to{" "}
            <span className="italic">know.</span>
          </h2>
        </motion.div>

        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 lg:gap-8 items-start">
          <div className="lg:col-span-8">
            <div className="rounded-2xl border border-hairline bg-bg-base shadow-card px-5 md:px-7">
              {FAQS.map((qa, i) => (
                <FaqRow
                  key={qa.q}
                  qa={qa}
                  open={openIdx === i}
                  onToggle={() => setOpenIdx(openIdx === i ? null : i)}
                />
              ))}
            </div>
          </div>

          <div className="lg:col-span-4">
            <StillHaveQuestionsCard />
          </div>
        </div>
      </div>
    </section>
  );
}
