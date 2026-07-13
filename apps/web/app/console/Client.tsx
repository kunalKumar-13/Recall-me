"use client";

/**
 * The engine room — a power-user console over the LOCAL daemon.
 *
 * Every request on this page goes browser → 127.0.0.1:4545. Nothing
 * is proxied through the site; deployed or not, your data never
 * leaves your machine. If no daemon answers, the room renders with
 * deterministic demo data and says so plainly.
 *
 * Read-only on purpose: the charter forbids dashboards as product
 * surfaces, but *inspectability is a product promise* — this is the
 * trust ledger with the lights on, not a feed to watch.
 */

import { useCallback, useEffect, useRef, useState } from "react";
import { LINKS } from "../lib/links";
import { Mark } from "../lib/Mark";
import { ThemeToggle } from "../lib/theme";

const DAEMON = "http://127.0.0.1:4545";
const LAYERS = [
  "events",
  "sessions",
  "contexts",
  "resurfacing",
  "threads",
  "evolution",
  "recovery",
];

type Kinds = Record<string, number>;
interface TailEvent {
  ts: string;
  kind: string;
  title: string;
  url: string;
  domain: string;
}
interface Snapshot {
  demo: boolean;
  ingestedTotal: number;
  eventsDir: string;
  today: { count: number; kinds: Kinds };
  recovery: Array<{ title: string; caption: string }>;
  threads: Array<{ title: string; events: number }>;
  radar: string[];
  perf: Array<{ path: string; budget: string; ms: number | null }>;
  tail: TailEvent[];
}

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
  recovery: [
    {
      title: "WebSocket reconnect bug",
      caption: "1 file · 1 chat · 2 tabs · returned 3×",
    },
    { title: "Seed deck — narrative pass", caption: "yesterday · 6 events" },
  ],
  threads: [
    { title: "WebSocket reconnect bug", events: 24 },
    { title: "Rust async runtime research", events: 18 },
    { title: "Hiring — staff designer", events: 11 },
  ],
  radar: ["tokio timeouts deep-dive", "billing migration notes"],
  perf: [
    { path: "/v1/health", budget: "<1 ms server", ms: 0.9 },
    { path: "/v1/events/today", budget: "<10 ms server", ms: 1.4 },
    { path: "/v1/threads/recent", budget: "<50 ms server", ms: 9.2 },
    { path: "/v1/search?q=…", budget: "<60 ms server", ms: 21.7 },
  ],
  tail: [
    { ts: "", kind: "browser_visit", title: "Stripe webhooks — retries", url: "", domain: "stripe.com" },
    { ts: "", kind: "browser_focus", title: "dwell 4m 12s · wb-1751", url: "", domain: "stripe.com" },
    { ts: "", kind: "chat_session", title: "retry logic — claude.ai", url: "", domain: "claude.ai" },
  ],
};

async function j<T>(path: string, timeoutMs = 1800): Promise<T | null> {
  try {
    const c = new AbortController();
    const t = setTimeout(() => c.abort(), timeoutMs);
    const r = await fetch(`${DAEMON}${path}`, {
      cache: "no-store",
      signal: c.signal,
    });
    clearTimeout(t);
    if (!r.ok) return null;
    return (await r.json()) as T;
  } catch {
    return null;
  }
}

async function median(path: string, n = 5): Promise<number> {
  const xs: number[] = [];
  for (let i = 0; i < n; i++) {
    const t0 = performance.now();
    await j(path, 2500);
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
    url: String(e.url ?? ""),
    domain: String(e.domain ?? ""),
  }));
}

async function probe(): Promise<Snapshot | null> {
  const health = await j<Record<string, unknown>>("/v1/health");
  if (!health) return null;
  const [today, rec, thr, rad, tail] = await Promise.all([
    j<{ count: number; kinds: Kinds }>("/v1/events/today"),
    j<{ candidates: Array<Record<string, unknown>> }>("/v1/recovery/recent?n=3"),
    j<{ threads: Array<Record<string, unknown>> }>("/v1/threads/recent?n=5"),
    j<{ contexts: Array<Record<string, unknown>>; enabled: boolean }>(
      "/v1/resurface/idle?n=3",
    ),
    j<{ events: Array<Record<string, unknown>> }>("/v1/events/recent?n=9&days=2"),
  ]);
  const [pHealth, pToday, pThreads, pSearch] = [
    await median("/v1/health"),
    await median("/v1/events/today", 3),
    await median("/v1/threads/recent?n=5", 3),
    await median("/v1/search?q=console", 3),
  ];
  return {
    demo: false,
    ingestedTotal: Number(health.ingested_total ?? 0),
    eventsDir: String(health.events_dir ?? "~/.recall/events"),
    today: {
      count: today?.count ?? 0,
      kinds: today?.kinds ?? {},
    },
    recovery: (rec?.candidates ?? []).map((c) => ({
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
    perf: [
      { path: "/v1/health", budget: "<1 ms server", ms: pHealth },
      { path: "/v1/events/today", budget: "<10 ms server", ms: pToday },
      { path: "/v1/threads/recent", budget: "<50 ms server", ms: pThreads },
      { path: "/v1/search?q=…", budget: "<60 ms server", ms: pSearch },
    ],
    tail: mapTail(tail?.events ?? []),
  };
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

function tailTime(ts: string): string {
  if (!ts) return "--:--";
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
  const alive = useRef(true);
  const connected = useRef(false);

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

  /* quiet live refresh: today + tail only, light endpoints */
  useEffect(() => {
    const t = setInterval(async () => {
      if (document.hidden || !connected.current) return;
      const [today, tail] = await Promise.all([
        j<{ count: number; kinds: Kinds }>("/v1/events/today"),
        j<{ events: Array<Record<string, unknown>> }>(
          "/v1/events/recent?n=9&days=2",
        ),
      ]);
      if (!alive.current || !today) return;
      setSnap((s) =>
        s && !s.demo
          ? {
              ...s,
              today: { count: today.count, kinds: today.kinds },
              tail: tail ? mapTail(tail.events) : s.tail,
            }
          : s,
      );
    }, 8000);
    return () => clearInterval(t);
  }, []);

  /* search over memory + files, debounced */
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
      (mem?.episodic ?? []).slice(0, 5).forEach((e) =>
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
    }, 220);
    return () => {
      dead = true;
      clearTimeout(t);
    };
  }, [sq]);

  const s = snap;
  const kindMax = s ? Math.max(1, ...Object.values(s.today.kinds)) : 1;

  return (
    <div className="conroot">
      <header className="conbar">
        <a className="brand" href="/">
          <Mark />
          Recall
          <span className="conbadge mono">console</span>
        </a>
        <div className="constatus mono">
          {probing ? (
            <>
              <i className="dot probing" /> probing 127.0.0.1:4545…
            </>
          ) : s && !s.demo ? (
            <>
              <i className="dot ok" /> daemon connected · local only
            </>
          ) : (
            <>
              <i className="dot off" /> no daemon found · demo data
            </>
          )}
        </div>
        <div className="conright">
          <button className="conbtn mono" onClick={load} disabled={probing}>
            re-probe
          </button>
          <ThemeToggle />
          <a className="conbtn mono" href="/">
            ← site
          </a>
        </div>
      </header>

      <div className="constrip mono" aria-hidden="true">
        {LAYERS.map((l, i) => (
          <span key={l}>
            <b>{l}</b>
            {i < LAYERS.length - 1 && <i> → </i>}
          </span>
        ))}
        <span className="constrip-note">seven layers · strictly upward · deterministic</span>
      </div>

      {s?.demo && !probing && (
        <div className="condemo mono">
          showing demo data — start Recall locally and re-probe. this page
          only ever talks to <b>127.0.0.1:4545</b> from your own browser; the
          site never sees your data.
        </div>
      )}

      <main className="congrid">
        {/* search — the whole memory from here */}
        <section className="conpanel span3 consearch">
          <div className="conlabel mono">[ 00 ] search your memory</div>
          <input
            className="coninput mono"
            value={sq}
            onChange={(e) => setSq(e.target.value)}
            placeholder={
              s?.demo
                ? "search works when the daemon is connected…"
                : "type — memory and files, under 100 ms…"
            }
            spellCheck={false}
            disabled={!!s?.demo}
          />
          {hits && (
            <div className="conhits">
              {hits.length === 0 && (
                <div className="conempty mono">nothing matched</div>
              )}
              {hits.map((h, i) =>
                h.url ? (
                  <a
                    className="conhit"
                    key={`${h.label}-${i}`}
                    href={h.url}
                    target="_blank"
                    rel="noreferrer"
                  >
                    <span className="conhit-t">{h.label}</span>
                    <span className="conhit-d mono">{h.detail}</span>
                  </a>
                ) : (
                  <div className="conhit" key={`${h.label}-${i}`}>
                    <span className="conhit-t">{h.label}</span>
                    <span className="conhit-d mono">{h.detail}</span>
                  </div>
                ),
              )}
            </div>
          )}
        </section>

        {/* today */}
        <section className="conpanel span2">
          <div className="conlabel mono">[ 01 ] captured today</div>
          <div className="connum">
            {s ? s.today.count.toLocaleString() : "—"}
            <span className="consub">events</span>
          </div>
          <div className="conbars">
            {s &&
              Object.entries(s.today.kinds)
                .sort((a, b) => b[1] - a[1])
                .map(([k, v]) => (
                  <div className="conbar-row" key={k}>
                    <span className="conbar-k mono">
                      {KIND_LABELS[k] ?? k}
                    </span>
                    <span className="conbar-track">
                      <i
                        style={{
                          width: `${Math.max(2, (v / kindMax) * 100)}%`,
                        }}
                      />
                    </span>
                    <span className="conbar-v mono">{v}</span>
                  </div>
                ))}
            {s && Object.keys(s.today.kinds).length === 0 && (
              <div className="conempty mono">
                nothing yet today — work normally
              </div>
            )}
          </div>
        </section>

        {/* daemon */}
        <section className="conpanel">
          <div className="conlabel mono">[ 02 ] daemon</div>
          <div className="conkv mono">
            <span>address</span>
            <b>127.0.0.1:4545</b>
          </div>
          <div className="conkv mono">
            <span>since start</span>
            <b>{s ? s.ingestedTotal.toLocaleString() : "—"} ingested</b>
          </div>
          <div className="conkv mono">
            <span>store</span>
            <b className="conpath">{s?.eventsDir ?? "—"}</b>
          </div>
          <div className="conkv mono">
            <span>uploads</span>
            <b>0 — loopback is the boundary</b>
          </div>
        </section>

        {/* perf */}
        <section className="conpanel">
          <div className="conlabel mono">[ 03 ] perf pulse</div>
          <div className="conperf mono">
            {(s?.perf ?? []).map((p) => (
              <div className="conperf-row" key={p.path}>
                <span className="conperf-p">{p.path}</span>
                <span className="conperf-m">
                  {p.ms === null ? "—" : `${p.ms} ms`}
                </span>
                <span className="conperf-b">{p.budget}</span>
              </div>
            ))}
          </div>
          <p className="confoot-note">
            wall-clock from this browser, median of repeated calls — budgets
            are the charter&apos;s server-side ceilings.
          </p>
        </section>

        {/* recovery */}
        <section className="conpanel">
          <div className="conlabel mono">[ 04 ] continue</div>
          {(s?.recovery ?? []).map((r) => (
            <div className="conrow" key={r.title}>
              <div className="conrow-t">{r.title}</div>
              <div className="conrow-c mono">{r.caption}</div>
            </div>
          ))}
          {s && s.recovery.length === 0 && (
            <div className="conempty mono">nothing to resume right now</div>
          )}
        </section>

        {/* threads */}
        <section className="conpanel">
          <div className="conlabel mono">[ 05 ] active threads</div>
          {(s?.threads ?? []).map((t) => (
            <div className="conrow" key={t.title}>
              <div className="conrow-t">{t.title}</div>
              <div className="conrow-c mono">{t.events} events</div>
            </div>
          ))}
          {s && s.threads.length === 0 && (
            <div className="conempty mono">no threads yet</div>
          )}
        </section>

        {/* live tail */}
        <section className="conpanel span2">
          <div className="conlabel mono">
            [ 06 ] live tail <i className="contick" />
          </div>
          <div className="contail">
            {(s?.tail ?? []).map((e, i) => (
              <div className="contail-row" key={`${e.ts}-${i}`}>
                <span className="contail-ts mono">{tailTime(e.ts)}</span>
                <span className="contail-k mono">{e.kind}</span>
                <span className="contail-t">{e.title}</span>
                <span className="contail-d mono">{e.domain}</span>
              </div>
            ))}
            {s && s.tail.length === 0 && (
              <div className="conempty mono">no recent events</div>
            )}
          </div>
        </section>

        {/* radar */}
        <section className="conpanel">
          <div className="conlabel mono">[ 07 ] on your radar</div>
          {(s?.radar ?? []).map((r) => (
            <div className="conrow" key={r}>
              <div className="conrow-t">{r}</div>
              <div className="conrow-c mono">set aside · cooled</div>
            </div>
          ))}
          {s && s.radar.length === 0 && (
            <div className="conempty mono">radar is clear</div>
          )}
        </section>
      </main>

      <footer className="confoot mono">
        <span>
          read-only · this page ↔ your daemon · zero proxying, zero analytics
          · refreshes quietly every 8s
        </span>
        <a href={LINKS.github} target="_blank" rel="noreferrer">
          source ↗
        </a>
      </footer>
    </div>
  );
}
