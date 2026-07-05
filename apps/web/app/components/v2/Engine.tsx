import { Section, SectionHead, Words } from "../../lib/reveal";

const LAYERS = [
  ["L1", "Events", "raw capture — the append-only log of what happened", "<2ms / write"],
  ["L2", "Sessions", "30-minute temporal groupings of related activity", "30-min windows"],
  ["L3", "Contexts", "topic-coherent slices inside a session", "topic-coherent"],
  ["L4", "Resurfacing", "idle-time surfacing of unfinished work", "<25ms"],
  ["L5", "Threads", "persistent topic identity across days and weeks", "<50ms"],
  ["L6", "Evolution", "the phases a thread moves through over time", "<70ms"],
  ["L7", "Recovery", "resumable work and one-keystroke restoration", "<80ms"],
] as const;

export function Engine() {
  return (
    <Section id="engine" className="sec">
      <div className="wrap sechead">
        <SectionHead index="07" eyebrow="The engine">
          <h2>
            <Words>Seven layers, strictly upward.</Words>
          </h2>
        </SectionHead>
        <p className="body rise">
          Each layer reads only from the one below. Deterministic — the same
          events in always produce the same memory out. Every artifact is
          plain text you can audit.
        </p>
        <div className="layers stagger">
          {LAYERS.map(([i, n, d, b]) => (
            <div className="layer" key={i}>
              <span className="i">{i}</span>
              <span className="n">{n}</span>
              <span className="d">{d}</span>
              <span className="b">{b}</span>
            </div>
          ))}
        </div>
      </div>
    </Section>
  );
}
