"use client";

/**
 * The popup, as an instrument. Same language as the site's console
 * cockpit: hairline-separated regions, bracket labels, mono
 * provenance, one accent. No floating cards, no stagger theatre —
 * the popup is a gauge you glance at, then act from.
 *
 *   [ continue ]   top candidate + resume + the real plan
 *   [ today ]      count + 24-hour rhythm + kind chips
 *   [ threads ]    what's alive this week
 *   [ tail ]       the last moments, timestamped
 *   foot           the trust line, in numbers
 */

import { useState } from "react";
import { fetchPlan, openTab } from "../../lib/api";
import type {
  ConnectionState,
  Investigation,
  MemoryItem,
  Recovery,
  TodaySummary,
} from "../../lib/types";

const KIND_LABELS: Record<string, string> = {
  browser_visit: "pages",
  browser_focus: "dwells",
  browser_search: "searches",
  chat_session: "chats",
  desktop_window: "app focus",
  open: "file opens",
  reveal: "reveals",
};

function Label({ text, right }: { text: string; right?: React.ReactNode }) {
  return (
    <div className="v3-label">
      <span className="v3-brk">[ </span>
      {text}
      <span className="v3-brk"> ]</span>
      {right != null && <span className="v3-labelright">{right}</span>}
    </div>
  );
}

function fmtTime(ts?: number): string {
  if (!ts) return "--:--";
  const d = new Date(ts * 1000);
  return `${String(d.getHours()).padStart(2, "0")}:${String(d.getMinutes()).padStart(2, "0")}`;
}

interface PlanStep {
  kind: string;
  target: string;
  group: string;
}

export function MainV3({
  connection,
  recovery,
  threads,
  tail,
  today,
  hours,
  queued,
  onResume,
}: {
  connection: ConnectionState;
  recovery: Recovery | null;
  threads: Investigation[];
  tail: MemoryItem[];
  today: TodaySummary | null;
  hours: number[] | null;
  queued: number;
  onResume: () => void;
}) {
  const [plan, setPlan] = useState<PlanStep[] | null>(null);
  const [planOpen, setPlanOpen] = useState(false);

  const togglePlan = async () => {
    if (planOpen) {
      setPlanOpen(false);
      return;
    }
    if (!plan && recovery) setPlan(await fetchPlan(recovery.id));
    setPlanOpen(true);
  };

  const hourMax = hours ? Math.max(1, ...hours) : 1;
  const nowHour = new Date().getHours();
  const kinds = Object.entries(today?.kinds ?? {}).sort((a, b) => b[1] - a[1]);
  const kindMax = Math.max(1, ...kinds.map(([, v]) => v));

  return (
    <div className="v3">
      {/* continue */}
      {recovery && (
        <section className="v3-sec">
          <Label text="continue" />
          <div className="v3-cand">
            <div className="v3-cand-t">{recovery.title}</div>
            <div className="v3-cand-c">{recovery.caption}</div>
          </div>
          <div className="v3-actions">
            <button className="v3-resume" onClick={onResume}>
              Resume <span className="v3-kbd">↵</span>
            </button>
            <button className="v3-ghost" onClick={() => void togglePlan()}>
              {planOpen ? "hide plan" : "show plan"}
            </button>
          </div>
          {planOpen && plan && (
            <div className="v3-plan">
              {plan.length === 0 && (
                <div className="v3-empty">plan unavailable</div>
              )}
              {plan.map((st, i) => (
                <div className="v3-step" key={`${st.target}-${i}`}>
                  <i>{i + 1}</i>
                  <span className="g">{st.group}</span>
                  {st.kind === "url" ? (
                    <button
                      className="t link"
                      onClick={() => openTab(st.target)}
                      title={st.target}
                    >
                      {st.target.replace(/^https?:\/\//, "")}
                    </button>
                  ) : (
                    <span className="t" title="opens via the Recall app">
                      {st.target.replace(/^\/Users\/[^/]+/, "~")}
                    </span>
                  )}
                </div>
              ))}
            </div>
          )}
        </section>
      )}

      {/* today */}
      <section className="v3-sec">
        <Label
          text="today"
          right={
            <span className="v3-count">
              {today ? today.count : "—"}
              <i> events</i>
            </span>
          }
        />
        {hours && (
          <>
            <div className="v3-hist" role="img" aria-label="Events per hour today">
              {hours.map((v, h) => (
                <i
                  key={h}
                  className={h === nowHour ? "now" : v > 0 ? "on" : ""}
                  style={{ height: `${Math.max(6, (v / hourMax) * 100)}%` }}
                  title={`${String(h).padStart(2, "0")}:00 — ${v}`}
                />
              ))}
            </div>
            <div className="v3-axis">
              <span>00</span>
              <span>06</span>
              <span>12</span>
              <span>18</span>
              <span>23</span>
            </div>
          </>
        )}
        <div className="v3-chips">
          {kinds.slice(0, 4).map(([k, v]) => (
            <span className="v3-chip" key={k}>
              <i style={{ opacity: 0.35 + 0.65 * (v / kindMax) }} />
              {v} {KIND_LABELS[k] ?? k}
            </span>
          ))}
          {today && today.count === 0 && (
            <span className="v3-empty">quiet so far — work normally</span>
          )}
        </div>
      </section>

      {/* threads */}
      {threads.length > 0 && (
        <section className="v3-sec">
          <Label text="threads" right={<span>{threads.length}</span>} />
          {threads.slice(0, 4).map((t) => (
            <div className="v3-row" key={t.id}>
              <span className="t">{t.title}</span>
              <span className="d">{t.summary}</span>
            </div>
          ))}
        </section>
      )}

      {/* tail */}
      {tail.length > 0 && (
        <section className="v3-sec">
          <Label text="tail" right={<i className="v3-live" />} />
          {tail.slice(0, 4).map((m, i) => (
            <button
              className="v3-tailrow"
              key={`${m.label}-${i}`}
              onClick={m.url ? () => openTab(m.url as string) : undefined}
              disabled={!m.url}
            >
              <span className="ts">{fmtTime(m.ts)}</span>
              <span className="k">{m.kind}</span>
              <span className="t">{m.label}</span>
            </button>
          ))}
        </section>
      )}

      {/* foot */}
      <footer className="v3-foot">
        <span>
          local only · 0 uploads
          {queued > 0 ? ` · ${queued} queued` : ""}
        </span>
        <span className={connection === "connected" ? "ok" : "warn"}>
          {connection === "connected" ? "daemon ok" : connection}
        </span>
      </footer>
    </div>
  );
}
