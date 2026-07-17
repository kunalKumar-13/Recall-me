import { Section, SectionHead, Words } from "../../lib/reveal";

export function Privacy() {
  return (
    <Section id="trust" className="sec">
      <div className="wrap sechead c">
        <SectionHead index="06" eyebrow="Local-first is the point">
          <h2>
            <Words>It stays on </Words>
            <em className="thread-mark">
              <Words>your machine</Words>
            </em>
            <Words>.</Words>
          </h2>
        </SectionHead>
        <div className="pv stagger">
          <div>
            <h3>Nothing leaves</h3>
            <p>
              No cloud, no sync, no remote inference. The only outbound call
              is a one-time model download on first run.
            </p>
          </div>
          <div>
            <h3>Everything readable</h3>
            <p>
              Every memory is plain JSONL on disk. Open it, grep it, diff it —
              there is no opaque database.
            </p>
          </div>
          <div>
            <h3>Delete is a full reset</h3>
            <p>
              All state lives in one folder. Remove it and Recall forgets
              completely, with nothing left on a server.
            </p>
          </div>
        </div>
        <div className="filetree rise">
          {"~/.recall/\n├── "}
          <span className="c">events/2026-06-25.jsonl</span>
          {"   "}
          <span className="cm"># every captured moment, one per line</span>
          {"\n├── "}
          <span className="c">threads.json</span>
          {"              "}
          <span className="cm"># topic identity — safe to delete, re-derives</span>
          {"\n└── "}
          <span className="c">config.json</span>
          {"               "}
          <span className="cm"># your folders and toggles</span>
        </div>
        <div className="refuse stagger">
          <div>
            <h3>Built, deliberately</h3>
            <ul>
              <li>
                <span className="y">→</span>
                <span>Deterministic engine — same events in, same memory out</span>
              </li>
              <li>
                <span className="y">→</span>
                <span>Plain-text artifacts you can open, grep and diff</span>
              </li>
              <li>
                <span className="y">→</span>
                <span>Performance budgets enforced in tests, per endpoint</span>
              </li>
              <li>
                <span className="y">→</span>
                <span>A durable capture queue — offline means delayed, never lost</span>
              </li>
              <li>
                <span className="y">→</span>
                <span>One keystroke from anywhere — ⌃Space</span>
              </li>
            </ul>
          </div>
          <div>
            <h3>Refused, deliberately</h3>
            <ul>
              <li>
                <span className="n">✕</span>
                <span>No cloud sync, no accounts, no telemetry</span>
              </li>
              <li>
                <span className="n">✕</span>
                <span>No notifications, badges or streaks</span>
              </li>
              <li>
                <span className="n">✕</span>
                <span>No recommendation feed</span>
              </li>
              <li>
                <span className="n">✕</span>
                <span>No LLM chat over your files</span>
              </li>
              <li>
                <span className="n">✕</span>
                <span>No learned weights guessing what you meant</span>
              </li>
            </ul>
          </div>
        </div>
      </div>
    </Section>
  );
}
