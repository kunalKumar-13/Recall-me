"use client";

/**
 * The demo film — 22 seconds, zero video files. The interface itself
 * acts out a working day on a loop: work builds up, an interruption
 * wipes it, ⌃space summons Recall, ↵ restores everything in order.
 *
 * The timeline is an imperative engine (sorted steps against a
 * millisecond clock) driving DOM inside this component's container —
 * scrub-safe because any jump replays the prefix deterministically.
 */

import { useEffect, useRef } from "react";
import { Section, Words } from "../../lib/reveal";

const TOTAL = 22500;
const SCENES = [
  { t: 0, label: "Work" },
  { t: 9200, label: "Interrupt" },
  { t: 12800, label: "Return" },
  { t: 16200, label: "Restore" },
];

const CODE =
  "fn reconnect(&mut self) {\n  let delay = backoff(self.attempts);\n  self.attempts += 1;\n  sleep(delay).await;\n  match self.dial().await {\n    Ok(s)  => self.on_open(s),\n    Err(_) => self.reconnect(),\n  }\n}";

export function Film() {
  const root = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const container = root.current;
    if (!container) return;
    const $ = <T extends HTMLElement>(sel: string) =>
      container.querySelector(sel) as T | null;

    const stage = $("[data-stage]");
    const sbox = $("[data-stagebox]");
    if (!stage || !sbox) return;

    const els = {
      winEd: $(".winEd"),
      winBr: $(".winBr"),
      winCh: $(".winCh"),
      edCode: $("[data-edcode]"),
      edCaret: $("[data-edcaret]"),
      brTabs: $("[data-brtabs]"),
      brPage: $("[data-brpage]"),
      bubQ: $("[data-bubq]"),
      bubA: $("[data-buba]"),
      chQ: $("[data-chq]"),
      chA: $("[data-cha]"),
      notif: $("[data-notif]"),
      tcard: $("[data-tcard]"),
      keys: $("[data-keys]"),
      kCtrl: $("[data-kctrl]"),
      kSpace: $("[data-kspace]"),
      keyEnter: $("[data-keyenter]"),
      kRet: $("[data-kret]"),
      rpanel: $("[data-rpanel]"),
      lb1: $("[data-lb1]"),
      lb2: $("[data-lb2]"),
      lb3: $("[data-lb3]"),
      toast: $("[data-toast]"),
      endcard: $("[data-endcard]"),
      flies: $("[data-flies]"),
      mclock: $("[data-mclock]"),
      pfill: $("[data-pfill]"),
      ptime: $("[data-ptime]"),
      ppBtn: $("[data-pp]"),
      ptrack: $("[data-ptrack]"),
    };
    if (Object.values(els).some((e) => !e)) return;
    const E = els as { [K in keyof typeof els]: HTMLElement };
    const sceneBtns = Array.from(
      container.querySelectorAll<HTMLElement>("[data-scene]"),
    );

    /* stage scaler: fixed 960×540 canvas scaled to its box */
    const scale = () => {
      const w = sbox.clientWidth;
      const s = w / 960;
      sbox.style.height = `${540 * s}px`;
      stage.style.transform = `scale(${s})`;
    };
    scale();
    addEventListener("resize", scale);

    /* ---------- timeline ---------- */
    type Step = { t: number; fn: () => void };
    const TL: Step[] = [];
    let INSTANT = false;
    const at = (t: number, fn: () => void) => TL.push({ t, fn });
    const typeInto = (
      el: HTMLElement,
      text: string,
      t0: number,
      ms: number,
      chunk: number,
    ) => {
      let end = t0;
      for (let i = chunk; i < text.length + chunk; i += chunk) {
        const slice = text.slice(0, Math.min(i, text.length));
        at(end, () => {
          el.textContent = slice;
        });
        end += ms;
      }
      return end;
    };
    const fly = (text: string, x: number, y: number, t: number) => {
      at(t, () => {
        if (INSTANT) return;
        const d = document.createElement("div");
        d.className = "flyev";
        d.textContent = text;
        d.style.left = `${x}px`;
        d.style.top = `${y}px`;
        E.flies.appendChild(d);
        requestAnimationFrame(() =>
          requestAnimationFrame(() => {
            d.style.transform = `translate(${842 - x}px, ${496 - y}px) scale(0.4)`;
            d.style.opacity = "0";
          }),
        );
        setTimeout(() => d.remove(), 980);
      });
    };
    const addTab = (label: string, t: number) => {
      at(t, () => {
        E.brTabs
          .querySelectorAll(".btab")
          .forEach((x) => x.classList.remove("act"));
        const s = document.createElement("span");
        s.className = "btab act";
        s.textContent = label;
        E.brTabs.appendChild(s);
      });
    };
    const on = (el: HTMLElement, cls = "on") => () => el.classList.add(cls);
    const off = (el: HTMLElement, cls = "on") => () =>
      el.classList.remove(cls);

    /* scene 01 — work */
    at(150, on(E.winEd));
    at(520, on(E.edCaret));
    fly("open  socket.rs", 60, 84, 560);
    typeInto(E.edCode, CODE, 620, 46, 3);
    at(1900, on(E.winBr));
    addTab("docs.rs/tokio", 2120);
    at(2160, () => {
      E.brPage.textContent = "tokio::time — sleep, interval, backoff";
    });
    fly("visit  docs.rs/tokio", 500, 130, 2200);
    addTab("MDN — WebSocket", 3080);
    at(3120, () => {
      E.brPage.textContent = "WebSocket.close() — close codes and reconnects";
    });
    fly("visit  developer.mozilla.org", 560, 130, 3140);
    at(4600, on(E.winCh));
    at(4820, on(E.bubQ, "show"));
    typeInto(
      E.chQ,
      "best websocket reconnect strategy — exponential backoff with jitter?",
      4860,
      40,
      2,
    );
    fly("chat  chatgpt.com", 300, 300, 5100);
    at(6480, on(E.bubA, "show"));
    typeInto(
      E.chA,
      "Use full-jitter backoff: delay = rand(0, base x 2^n), cap at 30s. Reset the counter after one stable minute. Reconnect on close codes 1006 and 1012.",
      6520,
      34,
      3,
    );
    fly("search  google — backoff jitter", 520, 120, 8700);

    /* scene 02 — interrupt */
    at(9200, on(E.notif));
    at(10050, off(E.notif));
    at(10150, on(E.winCh, "min"));
    at(10320, on(E.winBr, "min"));
    at(10500, () => {
      E.winEd.classList.add("min");
      E.edCaret.classList.remove("on");
    });
    at(11050, on(E.tcard));
    at(11900, () => {
      E.mclock.textContent = "3:12 PM";
    });
    at(12400, off(E.tcard));

    /* scene 03 — return */
    at(12800, on(E.keys));
    at(13320, on(E.kCtrl, "press"));
    at(13440, on(E.kSpace, "press"));
    at(13680, () => {
      E.kCtrl.classList.remove("press");
      E.kSpace.classList.remove("press");
    });
    at(13760, on(E.rpanel));
    at(13980, off(E.keys));
    at(15000, on(E.keyEnter));
    at(15560, on(E.kRet, "press"));
    at(15780, off(E.kRet, "press"));
    at(16060, off(E.keyEnter));
    at(16150, off(E.rpanel));

    /* scene 04 — restore */
    at(16220, () => {
      E.winEd.classList.remove("min");
      E.lb1.classList.add("on");
    });
    at(16380, on(E.edCaret));
    at(16950, () => {
      E.winCh.classList.remove("min");
      E.lb2.classList.add("on");
    });
    at(17150, off(E.lb1));
    at(17700, () => {
      E.winBr.classList.remove("min");
      E.lb3.classList.add("on");
    });
    at(17900, off(E.lb2));
    at(18500, () => {
      E.toast.classList.add("on");
      E.lb3.classList.remove("on");
    });
    at(19900, on(E.endcard));
    at(20400, off(E.toast));
    at(21950, off(E.endcard));

    TL.sort((a, b) => a.t - b.t);

    const resetStage = () => {
      [E.winEd, E.winBr, E.winCh].forEach((w) =>
        w.classList.remove("on", "min"),
      );
      [
        E.notif,
        E.tcard,
        E.keys,
        E.keyEnter,
        E.rpanel,
        E.toast,
        E.endcard,
        E.lb1,
        E.lb2,
        E.lb3,
      ].forEach((x) => x.classList.remove("on"));
      [E.kCtrl, E.kSpace, E.kRet].forEach((k) => k.classList.remove("press"));
      E.edCaret.classList.remove("on");
      E.edCode.textContent = "";
      E.chQ.textContent = "";
      E.chA.textContent = "";
      E.bubQ.classList.remove("show");
      E.bubA.classList.remove("show");
      E.brTabs.innerHTML = "";
      E.brPage.textContent = "";
      E.flies.innerHTML = "";
      E.mclock.textContent = "9:41 AM";
    };

    let clock = 0;
    let idx = 0;
    let playing = true;
    let vis = true;
    let raf = 0;
    const runSteps = () => {
      while (idx < TL.length && TL[idx].t <= clock) {
        TL[idx].fn();
        idx += 1;
      }
    };
    const jump = (t: number) => {
      INSTANT = true;
      resetStage();
      idx = 0;
      clock = t;
      runSteps();
      INSTANT = false;
    };
    const fmt = (ms: number) => {
      const s = Math.floor(ms / 1000);
      return `00:${s < 10 ? "0" : ""}${s}`;
    };
    const syncScenes = () => {
      let cur = 0;
      SCENES.forEach((s, i) => {
        if (clock >= s.t) cur = i;
      });
      sceneBtns.forEach((b, i) => b.classList.toggle("act", i === cur));
    };
    const setPlaying = (p: boolean) => {
      playing = p;
      E.ppBtn.textContent = p ? "❚❚" : "▶";
    };

    if (matchMedia("(prefers-reduced-motion: reduce)").matches) {
      jump(18700);
      return () => removeEventListener("resize", scale);
    }

    const io = new IntersectionObserver((es) => {
      vis = es[0].isIntersecting;
    });
    io.observe(sbox);

    const onPP = () => setPlaying(!playing);
    const onBox = () => setPlaying(!playing);
    const onTrack = (e: Event) => {
      const me = e as unknown as { clientX: number };
      const r = E.ptrack.getBoundingClientRect();
      jump(
        Math.min(0.999, Math.max(0, (me.clientX - r.left) / r.width)) * TOTAL,
      );
    };
    E.ppBtn.addEventListener("click", onPP);
    sbox.addEventListener("click", onBox);
    E.ptrack.addEventListener("click", onTrack);
    const sceneHandlers = sceneBtns.map((b, i) => {
      const h = () => jump(SCENES[i].t);
      b.addEventListener("click", h);
      return h;
    });

    let last: number | null = null;
    const tick = (ts: number) => {
      raf = requestAnimationFrame(tick);
      if (last === null) {
        last = ts;
        return;
      }
      const dt = ts - last;
      last = ts;
      if (playing && vis && !document.hidden) {
        clock += dt;
        runSteps();
        if (clock >= TOTAL) jump(0);
      }
      E.pfill.style.width = `${((clock / TOTAL) * 100).toFixed(2)}%`;
      E.ptime.textContent = `${fmt(clock)} / ${fmt(TOTAL)}`;
      syncScenes();
    };
    raf = requestAnimationFrame(tick);

    return () => {
      cancelAnimationFrame(raf);
      io.disconnect();
      removeEventListener("resize", scale);
      E.ppBtn.removeEventListener("click", onPP);
      sbox.removeEventListener("click", onBox);
      E.ptrack.removeEventListener("click", onTrack);
      sceneBtns.forEach((b, i) =>
        b.removeEventListener("click", sceneHandlers[i]),
      );
    };
  }, []);

  return (
    <Section id="film" className="sec">
      <div className="wrap sechead" ref={root}>
        <span className="smeta">
          <b>02</b> / 09
        </span>
        <span className="eyebrow rise">The demo — twenty-two seconds</span>
        <h2>
          <Words>Watch a thread break, </Words>
          <br />
          <em>
            <Words>and come back.</Words>
          </em>
        </h2>
        <p className="body rise">
          Not a screen recording — the interface itself, acting out a working
          day on a loop. Scrub it, pause it, let it run.
        </p>
        <div className="player rise">
          <div className="filmbox">
            <div data-stagebox className="stagebox">
              <div data-stage className="stage" aria-label="Recall product demo">
                <div className="mbar">
                  <span className="msq" />
                  <span>recall — demo workspace</span>
                  <span className="mck" data-mclock>
                    9:41 AM
                  </span>
                </div>
                <div className="fwin winEd">
                  <div className="tb">
                    <span className="td" />
                    <span className="td" />
                    socket.rs — ~/dev/relay
                  </div>
                  <div className="codebox">
                    <span data-edcode />
                    <span className="ecaret" data-edcaret />
                  </div>
                </div>
                <div className="fwin winBr">
                  <div className="tb">
                    <span className="td" />
                    <span className="td" />
                    browser
                  </div>
                  <div className="brTabs" data-brtabs />
                  <div className="brPage" data-brpage />
                </div>
                <div className="fwin winCh">
                  <div className="tb">
                    <span className="td" />
                    <span className="td" />
                    chatgpt.com
                  </div>
                  <div className="chbody">
                    <div className="bub user" data-bubq>
                      <span data-chq />
                    </div>
                    <div className="bub" data-buba>
                      <span data-cha />
                    </div>
                  </div>
                </div>
                <div className="notif" data-notif>
                  <div className="nt">Calendar</div>
                  <div className="nb">Standup — now</div>
                </div>
                <div className="tcard" data-tcard>
                  <div>
                    <em>Six hours later.</em>
                  </div>
                </div>
                <div className="keys" data-keys>
                  <span className="kcap" data-kctrl>
                    ⌃
                  </span>
                  <span className="plus">+</span>
                  <span className="kcap" data-kspace>
                    space
                  </span>
                </div>
                <div className="keyEnter" data-keyenter>
                  <span className="kcap" data-kret>
                    ↵
                  </span>
                </div>
                <div className="rpanel" data-rpanel>
                  <div className="rp-h">Continue where you left off</div>
                  <div className="rp-row">
                    <div>
                      <div className="rp-t">WebSocket reconnect bug</div>
                      <div className="rp-c">
                        1 file · 1 chat · 2 tabs · left mid-implementation
                      </div>
                    </div>
                    <span className="rp-hint">↵ resume</span>
                  </div>
                  <div className="rp-f">
                    <span>↑↓ move</span>
                    <span>↵ resume</span>
                    <span>esc close</span>
                  </div>
                </div>
                <span className="olabel lb1" data-lb1>
                  1 · files
                </span>
                <span className="olabel lb2" data-lb2>
                  2 · chats
                </span>
                <span className="olabel lb3" data-lb3>
                  3 · tabs
                </span>
                <div className="toast" data-toast>
                  Restored — 1 file · 1 chat · 2 tabs
                </div>
                <div className="endcard" data-endcard>
                  <div>
                    Never lose
                    <br />
                    the thread.
                  </div>
                </div>
                <div className="chip">
                  <i />
                  recall — capturing
                </div>
                <div data-flies />
              </div>
            </div>
          </div>
          <div className="pbar">
            <button className="pp" data-pp aria-label="Play or pause the demo">
              ❚❚
            </button>
            <div className="ptrack" data-ptrack>
              <div className="pfill" data-pfill />
              <span className="pmark" style={{ left: "41%" }} />
              <span className="pmark" style={{ left: "57%" }} />
              <span className="pmark" style={{ left: "72%" }} />
            </div>
            <span className="ptime" data-ptime>
              00:00 / 00:22
            </span>
          </div>
          <div className="pscenes">
            {SCENES.map((s, i) => (
              <button
                key={s.label}
                className={`pscene${i === 0 ? " act" : ""}`}
                data-scene
              >
                {s.label}
              </button>
            ))}
          </div>
        </div>
        <p className="fcap rise">
          Live interface, not a video — every window above is real page DOM.
        </p>
      </div>
    </Section>
  );
}
