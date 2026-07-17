import { Section, SectionHead, Words } from "../../lib/reveal";

const QA = [
  [
    "Can it read what's on a page?",
    "No. The extension uses the browser's tabs API — URL and title only. There are no content scripts and the DOM is never touched. You can read the whole capture worker in a few minutes; it's plain JavaScript in the repo.",
  ],
  [
    "Where does my data live?",
    "In one folder — ~/.recall/ — as plain JSONL text files. Open them in any editor. Deleting the folder is a complete, immediate reset. Nothing exists anywhere else.",
  ],
  [
    "What if the app isn't running?",
    'The extension keeps capturing into a durable queue inside the browser and delivers everything the moment the daemon is back. A "queued" pill in the popup tells you exactly how many events are waiting. Nothing is dropped.',
  ],
  [
    "Is this AI? Does it learn about me?",
    "No models make decisions about your memory. The engine is deterministic heuristics — the same events always produce the same threads. The only model on your machine is a small local embedding model for file search, downloaded once.",
  ],
  [
    "Does it slow anything down?",
    "Capture writes take under 2 milliseconds. Recalling your work is budgeted under 100 milliseconds — the budgets are enforced by the test suite, and a miss is treated as a bug.",
  ],
  [
    "Which browsers work?",
    "Chrome, Edge, Brave, Arc — anything Chromium with Manifest V3. Incognito is never captured, and you can exclude any domain in settings.",
  ],
] as const;

export function Faq() {
  return (
    <Section id="faq" className="sec">
      <div className="wrap sechead">
        <SectionHead index="07" eyebrow="Questions, answered plainly">
          <h2>
            <Words>Everything you&apos;d want to ask.</Words>
          </h2>
        </SectionHead>
        <div className="faq stagger">
          {QA.map(([q, a]) => (
            <div className="qa" key={q}>
              <h3>{q}</h3>
              <p>{a}</p>
            </div>
          ))}
        </div>
      </div>
    </Section>
  );
}
