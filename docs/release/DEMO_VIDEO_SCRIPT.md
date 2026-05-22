# DEMO_VIDEO_SCRIPT.md — the 60-second alpha demo

The placeholder script the recording will follow when the alpha
demo video is captured. **60 seconds**, six beats, **no narration**.
On-screen captions only — the demo is meant to play unmuted on a
laptop speaker, in a meeting room, on a phone, with nobody asked
to read voice-over copy off a slide. Calm.

Pairs with:

- [`docs/product/SURFACE_MAP.md`](../product/SURFACE_MAP.md) —
  the one-job-per-surface contract every shot honours.
- [`docs/product/MOTION.md`](../product/MOTION.md) — the timings
  the screen-recorder should match.
- [`docs/release/RECORDING_PROTOCOL.md`](RECORDING_PROTOCOL.md) —
  the rigorous capture rules (clock, demo seed, no jitter).
- [`apps/web/app/components/Hero.tsx`](../../apps/web/app/components/Hero.tsx)
  — the *Watch demo* button on the marketing site routes to
  this video once recorded.

---

## Beat sheet — 60 s total

| Beat | Duration | Surface | Caption | Action |
|---|---:|---|---|---|
| 1. Install | 0:00 → 0:08 | `Recall-Setup-lite.exe` running | *"Install once."* | Double-click the lite installer. Inno Setup steps through; installer closes at ~7 s. The setup wizard's progress bar fills calmly, no fast-forward. |
| 2. Capture | 0:08 → 0:20 | Browser + a code editor | *"Work normally."* | Tab through a few real-shape pages (Stack Overflow, MDN, a GitHub issue) and open two files. The browser extension's popup is *closed* — capture is invisible. |
| 3. Leave | 0:20 → 0:28 | Cursor moves to desktop, screen-saver fade | *"Step away."* | Press `Win + L` (lock screen) or quit the browser. Black for ~4 s with the caption on. |
| 4. Return | 0:28 → 0:42 | Launcher open (`Ctrl + Space`) | *"Come back."* | The launcher's empty-input state shows the digest: a recovery card + active investigations + the day's trust line. The recovery card reads *WebSocket retry debugging* — the canonical lead. |
| 5. Resume | 0:42 → 0:55 | Launcher → real tabs/files | *"Resume in one click."* | Click *Resume*. The launcher closes; tabs reopen in order in the browser; the two files open in the editor. The viewer sees the entire working state reappear. |
| 6. Trust line | 0:55 → 1:00 | Closing slate | *"Local only · 127.0.0.1:4545 · no cloud"* | Hold the line for 5 s over a calm warm-white background. End frame. |

Total: **60 seconds**, 5 captions, zero voice-over.

---

## Cuts to never make

- **No zoom-ins.** The default screen recorder framing carries
  every shot. Zooming into the UI reads as "look how much
  detail!" — exactly the opposite of the *calm* the product
  promises.
- **No speed-ups.** If the installer takes 8 seconds, the video
  shows 8 seconds. Speeding the install up reads as "we have
  something to hide about timing."
- **No music.** None. The product is for people who are
  concentrating. Music makes the demo feel like a marketing
  asset, not a tool demo.
- **No mouse cursor highlight effects.** A standard cursor
  arrow is the only on-screen pointer. No glow, no click ripple,
  no callout balloons.
- **No fake content.** Every captured tab / file / chat used
  in the recording is real — the same fixtures the
  `app.core.demo_seed` module ships. The viewer should be able
  to inspect the events later and find exactly what they saw.

---

## Pre-flight checklist

Before the recorder rolls:

1. `rm -rf ~/.recall/` — guarantee a clean install path.
2. `RECALL_DEMO_MODE=1 recall doctor` — confirm zero RED rows.
3. Set the system clock to `09:00:00` local. The launcher's
   timeline labels (`HH:MM`) read deterministically.
4. Close every browser window. Open exactly one Chrome window
   with the extension loaded.
5. Set the desktop wallpaper to a single warm-white solid (the
   product's `#FBF7F4`). The cuts between launcher / browser /
   editor read smoothly when the background is the same tone.
6. Record at 1920 × 1080, 60 fps, MP4 (H.264). The marketing
   site preloads the poster image; the video itself can be
   streamed via the standard `<video>` element.

---

## Caption typography

All captions render in **Fraunces 38 px / italic**, off-white
over a 12 %-opaque ink panel anchored to the bottom-left of the
frame:

```
italic 38px ─ Fraunces
weight 500
color #FBF7F4
panel rgba(22, 17, 43, 0.12)
padding 18px 24px
radius 12px
```

…matching the headline typography on the marketing site Hero so
the demo and the page read as one product.

---

## Where this script eventually lives

- The recording lands as `demo.mp4` at the repo root once the
  founder records it.
- The marketing site's `Watch demo` CTA in
  [`Hero.tsx`](../../apps/web/app/components/Hero.tsx) currently
  routes to `#how` (a scroll target). Once `demo.mp4` exists,
  `apps/web/app/lib/links.ts:demoVideo` flips to the hosted URL
  (or a relative path if hosted on the same domain).
- Until then, this file is the script the founder will follow
  when recording. The marketing site is **ready** for the link
  to flip on; the recording itself is the only thing pending.
