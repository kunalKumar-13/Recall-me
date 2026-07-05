import { Section, SectionHead, Words } from "../../lib/reveal";

const MOVES = [
  {
    n: "01",
    t: "Capture",
    p: "File opens, searches, and chat sessions are logged locally as you work — URL and title only, never page contents.",
  },
  {
    n: "02",
    t: "Group",
    p: "Raw events become sessions, then topic-coherent contexts, then threads that persist across days.",
  },
  {
    n: "03",
    t: "Resurface",
    p: "When you go idle, the thread you set aside surfaces quietly. Never a badge, never a notification.",
  },
  {
    n: "04",
    t: "Recover",
    p: "One keystroke reopens the work in order — files, then chats, then tabs by domain, then searches.",
  },
];

export function How() {
  return (
    <Section id="how" className="sec">
      <div className="wrap sechead">
        <SectionHead index="03" eyebrow="How it works">
          <h2>
            <Words>Four quiet moves.</Words>
          </h2>
        </SectionHead>
        <div className="rows stagger">
          {MOVES.map((m) => (
            <div className="rown" key={m.n}>
              <span className="i">{m.n}</span>
              <h3>{m.t}</h3>
              <p>{m.p}</p>
            </div>
          ))}
        </div>
      </div>
    </Section>
  );
}
