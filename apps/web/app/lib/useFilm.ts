"use client";

/**
 * The film engine as a hook. Builds the deterministic timeline
 * against a Stage container and exposes `seek(ms)` — jumping replays
 * the step prefix from a clean reset, so any scroll position maps to
 * exactly one frame of the story. `mode: "loop"` self-plays instead
 * (the reduced-motion / touch fallback).
 */

import { useEffect, useRef, type RefObject } from "react";

export const FILM_TOTAL = 22500;
/** scene starts: work / interrupt / return / restore */
export const FILM_SCENES = [0, 9200, 12800, 16200, FILM_TOTAL];

const CODE =
  "fn reconnect(&mut self) {\n  let delay = backoff(self.attempts);\n  self.attempts += 1;\n  sleep(delay).await;\n  match self.dial().await {\n    Ok(s)  => self.on_open(s),\n    Err(_) => self.reconnect(),\n  }\n}";

export function useFilm(
  root: RefObject<HTMLElement | null>,
  mode: "scrub" | "loop",
) {
  const seekRef = useRef<(ms: number) => void>(() => {});

  useEffect(() => {
    const container = root.current;
    if (!container) return;
    const $ = (sel: string) =>
      container.querySelector(sel) as HTMLElement | null;
    const stage = $("[data-stage]");
    const sbox = $("[data-stagebox]");
    if (!stage || !sbox) return;

    const q = {
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
    };
    if (Object.values(q).some((e) => !e)) return;
    const E = q as { [K in keyof typeof q]: HTMLElement };

    const scale = () => {
      const w = sbox.clientWidth;
      const s = w / 960;
      sbox.style.height = `${540 * s}px`;
      stage.style.transform = `scale(${s})`;
    };
    scale();
    addEventListener("resize", scale);

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

    /* work */
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

    /* interrupt */
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

    /* return */
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

    /* restore */
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

    let clock = -1;
    let idx = 0;
    const runSteps = () => {
      while (idx < TL.length && TL[idx].t <= clock) {
        TL[idx].fn();
        idx += 1;
      }
    };
    const seek = (ms: number) => {
      const t = Math.max(0, Math.min(FILM_TOTAL - 1, ms));
      if (Math.abs(t - clock) < 12) return;
      if (t >= clock && clock >= 0) {
        /* forward: just run the new prefix */
        clock = t;
        runSteps();
        return;
      }
      /* backward (or first frame): deterministic replay */
      INSTANT = true;
      resetStage();
      idx = 0;
      clock = t;
      runSteps();
      INSTANT = false;
    };
    seekRef.current = seek;

    let raf = 0;
    let cleanupLoop = () => {};
    if (mode === "loop") {
      let playing = true;
      let vis = true;
      const io = new IntersectionObserver((es) => {
        vis = es[0].isIntersecting;
      });
      io.observe(sbox);
      const onClick = () => {
        playing = !playing;
      };
      sbox.addEventListener("click", onClick);
      let last: number | null = null;
      let t = 0;
      const tick = (ts: number) => {
        raf = requestAnimationFrame(tick);
        if (last === null) {
          last = ts;
          return;
        }
        const dt = ts - last;
        last = ts;
        if (!playing || !vis || document.hidden) return;
        t += dt;
        if (t >= FILM_TOTAL) t = 0;
        seek(t);
      };
      raf = requestAnimationFrame(tick);
      cleanupLoop = () => {
        cancelAnimationFrame(raf);
        io.disconnect();
        sbox.removeEventListener("click", onClick);
      };
    } else {
      seek(0);
    }

    return () => {
      cleanupLoop();
      removeEventListener("resize", scale);
    };
  }, [root, mode]);

  return seekRef;
}
