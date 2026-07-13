import { Section, SectionHead, Words } from "../../lib/reveal";

/**
 * The capability bento — hairline-celled, no cards, every cell led
 * by a small working illustration of the real thing (event rows,
 * dwell blocks, the restore order, the exclusion list). Nothing in
 * here is a stock icon; it's the product drawn at 1:1.
 */
export function Features() {
  return (
    <Section id="features" className="sec">
      <div className="wrap sechead c">
        <SectionHead index="02" eyebrow="Capabilities">
          <h2>
            <Words>Everything you need. </Words>
            <em>
              <Words>Nothing watching you.</Words>
            </em>
          </h2>
          <p className="lead rise">
            Recall captures the shape of your work — never the content of your
            screen — and turns it into something you can return to.
          </p>
        </SectionHead>
      </div>

      <div className="bento">
        <div className="brow">
          {/* capture — the event log, drawn honestly */}
          <div className="bcell wide">
            <div className="bart">
              <div className="evrow"><span className="evk">browser_visit</span><span className="evt">stripe.com/docs/webhooks</span><span className="evtime">19:42</span></div>
              <div className="evrow"><span className="evk">browser_focus</span><span className="evt">dwell 4m 12s · wb-1751</span><span className="evtime">19:46</span></div>
              <div className="evrow"><span className="evk">chat_session</span><span className="evt">claude.ai — retry logic</span><span className="evtime">19:51</span></div>
              <div className="evrow dim"><span className="evk">open</span><span className="evt">~/dev/api/webhooks.py</span><span className="evtime">19:58</span></div>
            </div>
            <h3>Capture that reads like a logbook</h3>
            <p>
              Visits, searches, chats, file opens, attention. Plain JSONL on
              your disk — auditable with <span className="mono">cat</span>,
              deletable with <span className="mono">rm</span>.
            </p>
          </div>
          {/* private sites */}
          <div className="bcell">
            <div className="bart">
              <div className="exrow"><span>linkedin.com</span><span className="exoff">never captured</span></div>
              <div className="exrow"><span>bank-of-anything.com</span><span className="exoff">never captured</span></div>
              <div className="exrow add"><span>+ the site you were just on</span></div>
            </div>
            <h3>Private sites stay private</h3>
            <p>
              One click excludes a domain forever. Pause everything for an
              hour from the toolbar.
            </p>
          </div>
        </div>

        <div className="brow flip">
          {/* work blocks */}
          <div className="bcell">
            <div className="bart">
              <div className="wbtrack">
                <span className="wb" style={{ left: "2%", width: "26%" }} />
                <span className="wb" style={{ left: "31%", width: "14%" }} />
                <span className="wbgap" style={{ left: "47%", width: "10%" }} />
                <span className="wb hot" style={{ left: "59%", width: "37%" }} />
              </div>
              <div className="wblabels mono">
                <span>9:14 research</span>
                <span>break</span>
                <span>10:02 implementation</span>
              </div>
            </div>
            <h3>Work-blocks, not clock windows</h3>
            <p>
              Dwell and focus group your day behaviourally — the way it
              actually happened.
            </p>
          </div>
          {/* restore choreography */}
          <div className="bcell wide">
            <div className="bart">
              <div className="steps">
                <span className="step"><i>1</i> files</span>
                <span className="sline" aria-hidden />
                <span className="step"><i>2</i> chats</span>
                <span className="sline" aria-hidden />
                <span className="step"><i>3</i> tabs, by domain</span>
                <span className="sline" aria-hidden />
                <span className="step"><i>4</i> searches</span>
              </div>
            </div>
            <h3>Restore is choreographed</h3>
            <p>
              Enter doesn&apos;t explode ten tabs at you. Work reopens in
              order, staggered, so you re-enter the room the way you left it.
            </p>
          </div>
        </div>

        <div className="brow">
          {/* file search */}
          <div className="bcell wide">
            <div className="bart">
              <div className="fsq mono">⌕ rlhf reading notes</div>
              <div className="fsr"><span className="fsn">rlhf-notes.md</span><span className="fsp mono">~/Documents/research</span><span className="fss mono">0.81</span></div>
              <div className="fsr dim"><span className="fsn">reward-shaping.pdf</span><span className="fsp mono">~/Documents/papers</span><span className="fss mono">0.74</span></div>
            </div>
            <h3>Search memory and disk together</h3>
            <p>
              One query spans what you saw and what you saved — episodic
              memory plus semantic file search over folders you choose.
            </p>
          </div>
          {/* hotkey */}
          <div className="bcell">
            <div className="bart bkeys">
              <span className="kcap2">⌃</span>
              <span className="bplus">+</span>
              <span className="kcap2">space</span>
            </div>
            <h3>One keystroke away</h3>
            <p>
              Summon it over any app. Re-record the hotkey live in settings —
              it can never end up unreachable.
            </p>
          </div>
        </div>
      </div>
    </Section>
  );
}
