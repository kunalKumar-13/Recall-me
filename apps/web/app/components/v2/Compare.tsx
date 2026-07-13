import { Section, SectionHead, Words } from "../../lib/reveal";

/**
 * The honest comparison. Every cell is checkable: cloud recall tools
 * record your screen to their servers on a subscription; browser
 * history keeps URLs with no context; Recall keeps the shape of your
 * work in plain files on your disk.
 */

const ROWS: Array<{ q: string; recall: string; cloud: string; history: string; win?: boolean }> = [
  {
    q: "Where your data lives",
    recall: "your disk — ~/.recall, plain text",
    cloud: "their servers",
    history: "your disk",
    win: true,
  },
  {
    q: "What gets captured",
    recall: "titles, URLs, attention — never content",
    cloud: "continuous screen recordings",
    history: "URLs only, no context",
    win: true,
  },
  {
    q: "Can it resume your work?",
    recall: "one keystroke, in order",
    cloud: "search, then reopen by hand",
    history: "scroll and guess",
    win: true,
  },
  {
    q: "Works with the daemon off",
    recall: "capture queues, nothing lost",
    cloud: "needs their uptime",
    history: "yes",
  },
  {
    q: "Cost + source",
    recall: "free · open source",
    cloud: "subscription · closed",
    history: "free · built in",
    win: true,
  },
];

export function Compare() {
  return (
    <Section id="compare" className="sec">
      <div className="wrap sechead c">
        <SectionHead index="08" eyebrow="The honest table">
          <h2>
            <Words>Total recall, </Words>
            <em>
              <Words>without the surveillance.</Words>
            </em>
          </h2>
          <p className="lead rise">
            The other way to remember everything is to record everything and
            upload it. We think that&apos;s the wrong trade.
          </p>
        </SectionHead>
      </div>

      <div className="cmp rise">
        <div className="cmp-head">
          <span />
          <span className="cmp-us">
            Recall
          </span>
          <span>Cloud recall apps</span>
          <span>Browser history</span>
        </div>
        {ROWS.map((r) => (
          <div className="cmp-row" key={r.q}>
            <span className="cmp-q">{r.q}</span>
            <span className={`cmp-us${r.win ? " win" : ""}`}>{r.recall}</span>
            <span className="cmp-o">{r.cloud}</span>
            <span className="cmp-o">{r.history}</span>
          </div>
        ))}
        <div className="cmp-foot mono">
          every claim above is checkable — the code is public and the files
          are yours
        </div>
      </div>
    </Section>
  );
}
