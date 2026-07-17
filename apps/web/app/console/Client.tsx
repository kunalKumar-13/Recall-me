"use client";

/**
 * The engine room, rebuilt as one instrument.
 *
 * A single hairline-gridded cockpit: rail (layer meter + vitals),
 * stage (command search over your whole memory + today's rhythm as a
 * 24-hour histogram), side (continue with the real restoration plan,
 * threads, radar), and a live tail + perf pulse along the footer.
 *
 * Every request goes browser → 127.0.0.1:4545. Nothing is proxied
 * through the site; your data never leaves your machine. No daemon →
 * deterministic demo data, said plainly. Read-only by design: this
 * is the trust ledger with the lights on, not a feed.
 */

import {
  useCallback,
  useEffect,
  useMemo,
  useRef,
  useState,
} from "react";
import { LINKS } from "../lib/links";
import { Mark } from "../lib/Mark";
import { ThemeToggle } from "../lib/theme";

const DAEMON = "http://127.0.0.1:4545";

type Kinds = Record<string, number>;
interface TailEvent {
  ts: string;
  kind: string;
  title: string;
  domain: string;
}
interface PlanStep {
  kind: string;
  target: string;
  group: string;
}
interface Candidate {
  id: string;
  title: string;
  caption: string;
}
interface Loop {
  returns: number;
  shown: number;
  used: number;
  verdicts: Record<string, string>; // GREEN | YELLOW | RED
}
interface Snapshot {
  demo: boolean;
  ingestedTotal: number;
  eventsDir: string;
  today: { count: number; kinds: Kinds };
  hours: number[]; // 24 buckets, local time
  recovery: Candidate[];
  threads: Array<{ title: string; events: number }>;
  radar: string[];
  perf: Array<{ label: string; ms: number | null; budget: string }>;
  tail: TailEvent[];
  loop: Loop | null;
}

const KIND_LABELS: Record<string, string> = {
  browser_visit: "pages",
  browser_focus: "dwells",
  browser_search: "searches",
  chat_session: "chats",
  desktop_window: "app focus",
  open: "file opens",
  reveal: "reveals",
};

const DEMO: Snapshot = {
  demo: true,
  ingestedTotal: 412,
  eventsDir: "~/.recall/events",
  today: {
    count: 88,
    kinds: {
      browser_visit: 61,
      browser_focus: 12,
      chat_session: 7,
      browser_search: 5,
      desktop_window: 2,
      open: 1,
    },
  },
  hours: [0, 0, 0, 0, 0, 0, 0, 1, 3, 9, 12, 8, 4, 6, 11, 13, 9, 6, 4, 2, 0, 0, 0, 0],
  recovery: [
    {
      id: "demo",
      title: "WebSocket reconnect bug",
      caption: "1 file · 1 chat · 2 tabs · returned 3×",
    },
  ],
  threads: [
    { title: "WebSocket reconnect bug", events: 24 },
    { title: "Rust async runtime research", events: 18 },
    { title: "Hiring — staff designer", events: 11 },
  ],
  radar: ["tokio timeouts deep-dive", "billing migration notes"],
  perf: [
    { label: "health", ms: 0.9, budget: "<1" },
    { label: "today", ms: 1.4, budget: "<10" },
    { label: "search", ms: 21.7, budget: "<60" },
  ],
  tail: [
    { ts: "", kind: "browser_visit", title: "Stripe webhooks — retries", domain: "stripe.com" },
    { ts: "", kind: "browser_focus", title: "dwell 4m 12s · wb-1751", domain: "stripe.com" },
    { ts: "", kind: "chat_session", title: "retry logic — claude.ai", domain: "claude.ai" },
    { ts: "", kind: "browser_search", title: "exponential backoff jitter", domain: "google.com" },
  ],
  loop: {
    returns: 62,
    shown: 13,
    used: 4,
    verdicts: {
      return_rate: "GREEN",
      continuity_restored: "YELLOW",
      resume_quality: "GREEN",
    },
  },
};

async function j<T>(path: string, init?: RequestInit, timeoutMs = 2200): Promise<T | null> {
  try {
    const c = new AbortController();
    const t = setTimeout(() => c.abort(), timeoutMs);
    const r = await fetch(`${DAEMON}${path}`, {
      cache: "no-store",
      signal: c.signal,
      ...init,
    });
    clearTimeout(t);
    if (!r.ok) return null;
    return (await r.json()) as T;
  } catch {
    return null;
  }
}

async function med(path: string, n: number): Promise<number> {
  const xs: number[] = [];
  for (let i = 0; i < n; i++) {
    const t0 = performance.now();
    await j(path);
    xs.push(performance.now() - t0);
  }
  xs.sort((a, b) => a - b);
  return Math.round(xs[Math.floor(xs.length / 2)] * 10) / 10;
}

function mapTail(events: Array<Record<string, unknown>>): TailEvent[] {
  return events.map((e) => ({
    ts: String(e.ts ?? ""),
    kind: String(e.kind ?? ""),
    title:
      String(e.title ?? "") ||
      String((e.payload as Record<string, unknown>)?.query ?? "") ||
      String(e.domain ?? ""),
    domain: String(e.domain ?? ""),
  }));
}

function bucketHours(events: Array<Record<string, unknown>>): number[] {
  const hours = new Array(24).fill(0);
  const dayStart = new Date();
  dayStart.setHours(0, 0, 0, 0);
  for (const e of events) {
    const ms = Date.parse(String(e.ts ?? ""));
    if (!Number.isFinite(ms) || ms < dayStart.getTime()) continue;
    hours[new Date(ms).getHours()] += 1;
  }
  return hours;
}

async function probe(): Promise<Snapshot | null> {
  const health = await j<Record<string, unknown>>("/v1/health");
  if (!health) return null;
  const [today, rec, thr, rad, recent, loop] = await Promise.all([
    j<{ count: number; kinds: Kinds }>("/v1/events/today"),
    j<{ candidates: Array<Record<string, unknown>> }>("/v1/recovery/recent?n=2"),
    j<{ threads: Array<Record<string, unknown>> }>("/v1/threads/recent?n=5"),
    j<{ contexts: Array<Record<string, unknown>>; enabled: boolean }>("/v1/resurface/idle?n=3"),
    j<{ events: Array<Record<string, unknown>> }>("/v1/events/recent?n=200&days=1"),
    j<Record<string, unknown>>("/v1/loop/summary"),
  ]);
  const perf = [
    { label: "health", ms: await med("/v1/health", 5), budget: "<1" },
    { label: "today", ms: await med("/v1/events/today", 3), budget: "<10" },
    { label: "search", ms: await med("/v1/search?q=console", 3), budget: "<60" },
  ];
  const recentEvents = recent?.events ?? [];
  return {
    demo: false,
    ingestedTotal: Number(health.ingested_total ?? 0),
    eventsDir: String(health.events_dir ?? "~/.recall/events"),
    today: { count: today?.count ?? 0, kinds: today?.kinds ?? {} },
    hours: bucketHours(recentEvents),
    recovery: (rec?.candidates ?? []).map((c) => ({
      id: String(c.id ?? ""),
      title: String(c.title ?? "Untitled"),
      caption: String(c.preview_caption ?? ""),
    })),
    threads: (thr?.threads ?? []).map((t) => ({
      title: String(t.title ?? "Untitled"),
      events: Number(t.event_count ?? 0),
    })),
    radar: (rad?.enabled ? rad.contexts ?? [] : []).map((c) =>
      String(c.label || c.topic || ""),
    ),
    perf,
    tail: mapTail(recentEvents.slice(0, 4)),
    loop: loop
      ? {
          returns: Number((loop.window as Record<string, unknown>)?.returns ?? 0),
          shown: Number(
            (loop.window as Record<string, unknown>)?.recoveries_shown ?? 0,
          ),
          used: Number(
            (loop.window as Record<string, unknown>)?.recoveries_used ?? 0,
          ),
          verdicts: (loop.green_yellow_red ?? {}) as Record<string, string>,
        }
      : null,
  };
}

function tailTime(ts: string): string {
  const ms = Date.parse(ts);
  if (!Number.isFinite(ms)) return "--:--";
  const d = new Date(ms);
  return `${String(d.getHours()).padStart(2, "0")}:${String(d.getMinutes()).padStart(2, "0")}`;
}

interface Hit {
  label: string;
  detail: string;
  url?: string;
}

export function ConsoleClient() {
  const [snap, setSnap] = useState<Snapshot | null>(null);
  const [probing, setProbing] = useState(true);
  const [sq, setSq] = useState("");
  const [hits, setHits] = useState<Hit[] | null>(null);
  const [plan, setPlan] = useState<PlanStep[] | null>(null);
  const [planFor, setPlanFor] = useState<string | null>(null);
  const alive = useRef(true);
  const connected = useRef(false);
  const inputRef = useRef<HTMLInputElement>(null);

  const load = useCallback(async () => {
    setProbing(true);
    const s = await probe();
    if (!alive.current) return;
    connected.current = !!s;
    setSnap(s ?? DEMO);
    setProbing(false);
  }, []);

  useEffect(() => {
    alive.current = true;
    void load();
    return () => {
      alive.current = false;
    };
  }, [load]);

  /* quiet live refresh — today, histogram, tail */
  useEffect(() => {
    const t = setInterval(async () => {
      if (document.hidden || !connected.current) return;
      const [today, recent] = await Promise.all([
        j<{ count: number; kinds: Kinds }>("/v1/events/today"),
        j<{ events: Array<Record<string, unknown>> }>("/v1/events/recent?n=200&days=1"),
      ]);
      if (!alive.current || !today) return;
      setSnap((s) =>
        s && !s.demo
          ? {
              ...s,
              today: { count: today.count, kinds: today.kinds },
              hours: recent ? bucketHours(recent.events) : s.hours,
              tail: recent ? mapTail(recent.events.slice(0, 4)) : s.tail,
            }
          : s,
      );
    }, 8000);
    return () => clearInterval(t);
  }, []);

  /* '/' focuses the command line, esc clears */
  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      if (e.key === "/" && document.activeElement !== inputRef.current) {
        e.preventDefault();
        inputRef.current?.focus();
      } else if (e.key === "Escape") {
        setSq("");
        inputRef.current?.blur();
      }
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, []);

  /* search memory + files, debounced */
  useEffect(() => {
    const q = sq.trim();
    if (!q || !connected.current) {
      setHits(null);
      return;
    }
    let dead = false;
    const t = setTimeout(async () => {
      const [mem, files] = await Promise.all([
        j<{ episodic: Array<Record<string, unknown>> }>(
          `/v1/search?q=${encodeURIComponent(q)}`,
        ),
        j<{ results: Array<Record<string, unknown>>; enabled: boolean }>(
          `/v1/search/files?q=${encodeURIComponent(q)}&n=3`,
        ),
      ]);
      if (dead) return;
      const out: Hit[] = [];
      (mem?.episodic ?? []).slice(0, 6).forEach((e) =>
        out.push({
          label: String(e.title || e.subtitle || "Moment"),
          detail: String(e.subtitle || e.kind || ""),
          url: String(e.url || "") || undefined,
        }),
      );
      (files?.enabled ? files.results : []).forEach((f) =>
        out.push({
          label: String(f.name ?? "file"),
          detail: String(f.path ?? "").replace(/^\/Users\/[^/]+/, "~"),
        }),
      );
      setHits(out);
    }, 200);
    return () => {
      dead = true;
      clearTimeout(t);
    };
  }, [sq]);

  /* the restoration plan for the top candidate — the real order */
  const revealPlan = useCallback(
    async (c: Candidate) => {
      if (planFor === c.id) {
        setPlan(null);
        setPlanFor(null);
        return;
      }
      if (snap?.demo) {
        setPlan([
          { kind: "path", target: "~/dev/api/webhooks.py", group: "files" },
          { kind: "url", target: "https://claude.ai/chat/…", group: "chats" },
          { kind: "url", target: "https://stripe.com/docs/webhooks", group: "tabs" },
        ]);
        setPlanFor(c.id);
        return;
      }
      const p = await j<{ steps: PlanStep[] }>(
        `/v1/recovery/${encodeURIComponent(c.id)}/restore`,
        { method: "POST" },
      );
      setPlan(p?.steps ?? []);
      setPlanFor(c.id);
    },
    [planFor, snap?.demo],
  );

  const s = snap;
  const hourMax = useMemo(() => Math.max(1, ...(s?.hours ?? [1])), [s?.hours]);
  const nowHour = new Date().getHours();
  const kindMax = s ? Math.max(1, ...Object.values(s.today.kinds), 1) : 1;

  /* honest layer signals: a dot means "has material right now" */
  const layerOn: Record<string, boolean> = {
    events: (s?.today.count ?? 0) > 0,
    sessions: (s?.today.count ?? 0) > 0,
    contexts: (s?.today.count ?? 0) > 0,
    resurfacing: (s?.radar.length ?? 0) > 0,
    threads: (s?.threads.length ?? 0) > 0,
    evolution: (s?.threads[0]?.events ?? 0) > 3,
    recovery: (s?.recovery.length ?? 0) > 0,
  };

  return (
    <div className="ck">
      {/* ── bar ─────────────────────────────────────────────── */}
      <header className="ck-bar">
        <a className="brand" href="/">
          <Mark />
          Recall
          <span className="ck-badge mono">console</span>
        </a>
        <div className="ck-status mono">
          {probing ? (
            <>
              <i className="d probing" /> probing 127.0.0.1:4545…
            </>
          ) : s && !s.demo ? (
            <>
              <i className="d ok" /> daemon connected · local only
            </>
          ) : (
            <>
              <i className="d off" /> no daemon · demo data
            </>
          )}
        </div>
        <div className="ck-actions">
          <button className="ck-btn mono" onClick={load} disabled={probing}>
            re-probe
          </button>
          <ThemeToggle />
          <a className="ck-btn mono" href="/">
            ← site
          </a>
        </div>
      </header>

      {/* ── instrument ──────────────────────────────────────── */}
      <div className="ck-grid">
        {/* rail */}
        <aside className="ck-rail">
          <div className="ck-cell">
            <div className="ck-label mono">engine layers</div>
            <div className="ck-meter">
              {Object.entries(layerOn).map(([name, on]) => (
                <div className="ck-layer mono" key={name}>
                  <i className={on ? "on" : ""} />
                  <span>{name}</span>
                </div>
              ))}
            </div>
          </div>
          <div className="ck-cell">
            <div className="ck-label mono">vitals</div>
            <div className="ck-kv mono">
              <span>address</span>
              <b>127.0.0.1:4545</b>
            </div>
            <div className="ck-kv mono">
              <span>since start</span>
              <b>{s ? s.ingestedTotal.toLocaleString() : "—"}</b>
            </div>
            <div className="ck-kv mono">
              <span>store</span>
              <b className="ck-path" title={s?.eventsDir}>
                {s?.eventsDir.replace(/^\/Users\/[^/]+/, "~") ?? "—"}
              </b>
            </div>
            <div className="ck-kv mono">
              <span>uploads</span>
              <b>0 · ever</b>
            </div>
          </div>
          <div className="ck-cell">
            <div className="ck-label mono">
              the loop <span className="ck-loopwin">· 7d</span>
            </div>
            <div className="ck-kv mono">
              <span>returns</span>
              <b>{s?.loop?.returns ?? "—"}</b>
            </div>
            <div className="ck-kv mono">
              <span>surfaced → used</span>
              <b>
                {s?.loop ? `${s.loop.shown} → ${s.loop.used}` : "—"}
              </b>
            </div>
            <div className="ck-verdicts">
              {s?.loop &&
                Object.entries(s.loop.verdicts).map(([k, v]) => (
                  <div className="ck-verdict mono" key={k}>
                    <i className={v.toLowerCase()} />
                    <span>{k.replace(/_/g, " ")}</span>
                  </div>
                ))}
            </div>
            <p className="ck-loopnote mono">
              recall grading itself — counts only, never content
            </p>
          </div>
          <div className="ck-cell ck-railnote mono">
            read-only · zero proxying
            <br />
            this page ↔ your daemon
          </div>
        </aside>

        {/* stage */}
        <section className="ck-stage">
          <div className="ck-cmd">
            <span className="ck-glyph" aria-hidden>
              ⌕
            </span>
            <input
              ref={inputRef}
              className="ck-input"
              value={sq}
              onChange={(e) => setSq(e.target.value)}
              placeholder={
                s?.demo
                  ? "search needs the daemon — start Recall and re-probe"
                  : "ask your memory — pages, chats, files…"
              }
              disabled={!!s?.demo}
              spellCheck={false}
            />
            <span className="ck-keys mono">
              <b>/</b> focus · <b>esc</b> clear
            </span>
          </div>

          {hits ? (
            <div className="ck-results">
              {hits.length === 0 && (
                <div className="ck-empty mono">nothing matched “{sq}”</div>
              )}
              {hits.map((h, i) =>
                h.url ? (
                  <a
                    key={`${h.label}-${i}`}
                    className="ck-hit"
                    href={h.url}
                    target="_blank"
                    rel="noreferrer"
                  >
                    <span className="t">{h.label}</span>
                    <span className="d mono">{h.detail}</span>
                    <span className="g mono">open ↗</span>
                  </a>
                ) : (
                  <div key={`${h.label}-${i}`} className="ck-hit">
                    <span className="t">{h.label}</span>
                    <span className="d mono">{h.detail}</span>
                    <span className="g mono">file</span>
                  </div>
                ),
              )}
            </div>
          ) : (
            <div className="ck-today">
              <div className="ck-today-head">
                <span className="ck-label mono">today</span>
                <span className="ck-count mono">
                  {s ? s.today.count.toLocaleString() : "—"}
                  <i>events</i>
                </span>
              </div>
              <div className="ck-hist" role="img" aria-label="Events per hour today">
                {(s?.hours ?? new Array(24).fill(0)).map((v, h) => (
                  <div className="ck-hcol" key={h}>
                    <i
                      className={h === nowHour ? "now" : v > 0 ? "on" : ""}
                      style={{ height: `${Math.max(3, (v / hourMax) * 100)}%` }}
                      title={`${String(h).padStart(2, "0")}:00 — ${v} events`}
                    />
                  </div>
                ))}
              </div>
              <div className="ck-hxaxis mono">
                <span>00</span>
                <span>06</span>
                <span>12</span>
                <span>18</span>
                <span>23</span>
              </div>
              <div className="ck-chips">
                {s &&
                  Object.entries(s.today.kinds)
                    .sort((a, b) => b[1] - a[1])
                    .map(([k, v]) => (
                      <span className="ck-chip mono" key={k}>
                        <i style={{ opacity: 0.3 + 0.7 * (v / kindMax) }} />
                        {v} {KIND_LABELS[k] ?? k}
                      </span>
                    ))}
                {s && s.today.count === 0 && (
                  <span className="ck-empty mono">
                    quiet so far — work normally
                  </span>
                )}
              </div>
            </div>
          )}
        </section>

        {/* side */}
        <aside className="ck-side">
          <div className="ck-cell">
            <div className="ck-label mono">continue</div>
            {(s?.recovery ?? []).map((c) => (
              <div key={c.id}>
                <button className="ck-cand" onClick={() => void revealPlan(c)}>
                  <span className="t">{c.title}</span>
                  <span className="d mono">{c.caption}</span>
                  <span className="g mono">
                    {planFor === c.id ? "hide plan" : "show plan"}
                  </span>
                </button>
                {planFor === c.id && plan && (
                  <div className="ck-plan">
                    {plan.map((st, i) =>
                      st.kind === "url" ? (
                        <a
                          key={i}
                          className="ck-step mono"
                          href={st.target}
                          target="_blank"
                          rel="noreferrer"
                        >
                          <i>{i + 1}</i>
                          <span>{st.group}</span>
                          <b>{st.target.replace(/^https?:\/\//, "").slice(0, 34)}…</b>
                        </a>
                      ) : (
                        <div key={i} className="ck-step mono">
                          <i>{i + 1}</i>
                          <span>{st.group}</span>
                          <b title="files open via the launcher">
                            {st.target.replace(/^\/Users\/[^/]+/, "~")}
                          </b>
                        </div>
                      ),
                    )}
                  </div>
                )}
              </div>
            ))}
            {s && s.recovery.length === 0 && (
              <div className="ck-empty mono">nothing to resume</div>
            )}
          </div>
          <div className="ck-cell">
            <div className="ck-label mono">active threads</div>
            {(s?.threads ?? []).map((t) => (
              <div className="ck-row" key={t.title}>
                <span className="t">{t.title}</span>
                <span className="d mono">{t.events}</span>
              </div>
            ))}
            {s && s.threads.length === 0 && (
              <div className="ck-empty mono">none yet</div>
            )}
          </div>
          <div className="ck-cell">
            <div className="ck-label mono">on your radar</div>
            {(s?.radar ?? []).map((r) => (
              <div className="ck-row" key={r}>
                <span className="t">{r}</span>
                <span className="d mono">cooled</span>
              </div>
            ))}
            {s && s.radar.length === 0 && (
              <div className="ck-empty mono">clear</div>
            )}
          </div>
        </aside>
      </div>

      {/* ── foot: tail + pulse ──────────────────────────────── */}
      <footer className="ck-foot">
        <div className="ck-tail">
          <span className="ck-label mono">
            tail <i className="ck-tick" />
          </span>
          <div className="ck-tailrows">
            {(s?.tail ?? []).map((e, i) => (
              <div className="ck-tailrow mono" key={`${e.ts}-${i}`}>
                <span className="ts">{tailTime(e.ts)}</span>
                <span className="k">{e.kind.replace("browser_", "")}</span>
                <span className="t">{e.title}</span>
                <span className="d">{e.domain}</span>
              </div>
            ))}
          </div>
        </div>
        <div className="ck-pulse mono">
          {(s?.perf ?? []).map((p) => (
            <span className="ck-pchip" key={p.label}>
              {p.label} <b>{p.ms === null ? "—" : `${p.ms}ms`}</b>
              <i>{p.budget}</i>
            </span>
          ))}
          <a href={LINKS.github} target="_blank" rel="noreferrer">
            source ↗
          </a>
        </div>
      </footer>
    </div>
  );
}
