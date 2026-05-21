# FIRST_WEEK.md — what a stranger experiences

The success condition of Phase 5C, written out day by day. A
stranger installs Recall, uses it for a week, returns. The founder
is not in the room. This file is the audit of what they *should*
go through — every friction moment, every confusion point, every
trust moment named and addressed.

Pairs with [`TRUST_MOMENTS.md`](../product/TRUST_MOMENTS.md) (the specific
beats), [`KNOWN_LIMITATIONS.md`](../product/KNOWN_LIMITATIONS.md) (what they
will hit that we own honestly), and
[`PUBLIC_ALPHA_CHECKLIST.md`](../release/PUBLIC_ALPHA_CHECKLIST.md) (what must
be true before they meet this file).

---

## Day 0 — install

| | What happens | Trust moment | Friction risk | Mitigation |
|---|---|---|---|---|
| step | download `Recall-Setup.exe` from GitHub releases | the SHA-256 on the page; the open repo | SmartScreen *"Windows protected your PC"* warning | `INSTALL.md` names this; the installer is per-user, no admin |
| step | double-click installer | first contact — does it feel professional? | the unsigned `.exe` reads as risky | signing is the GO_NO_GO gate-7 blocker, on the public-alpha path |
| step | wizard finishes, Recall launches | first-launch onboarding (one screen) | onboarding might be skipped without folder pick | the empty-launcher state guides ("press Ctrl + , to choose folders") |
| step | optional — install the browser extension | the popup explains itself before pairing | pairing is two clicks the user did not expect | the extension's *Install Recall / Open / Repair* CTAs (Phase 5A) |

**End of Day 0:** Recall is running in the tray. The launcher
opens empty with *"Recall is ready. Work a little, then come back
later."* That message is the whole Day-0 ask.

## Day 1 — browser memory active

| | What happens | Trust moment | Friction risk | Mitigation |
|---|---|---|---|---|
| user works normally | browsing, file opens; the extension captures URLs + titles | the popup says *"local only · 127.0.0.1:4545 · no cloud"* | user wonders if anything is being captured | the popup's trust line, plus `recall stats` shows events accumulating |
| evening — launcher opened | empty digest still | "is this thing working?" | nothing yet to surface | the calm copy + `recall doctor` answers the question honestly |

**End of Day 1:** events are flowing; nothing crystallises yet.
Correct, by the engine's design — recovery does not fabricate.

## Day 2 — first investigation

| | What happens | Trust moment | Friction risk | Mitigation |
|---|---|---|---|---|
| user returns to a topic | a thread crystallises (`>= 3` seeding events, multi-session) | the launcher's *"Active investigations"* surface appears | the word *investigation* is unfamiliar | `CONTINUITY_LANGUAGE.md` defines it once, calmly |
| user opens launcher empty | digest now shows one row under *Active investigations* | "Recall noticed what I am working on" | none significant | — |

**End of Day 2:** there is a thing on the page that names what the
user is doing.

## Day 3 — first recovery

| | What happens | Trust moment | Friction risk | Mitigation |
|---|---|---|---|---|
| user gets interrupted mid-flow | momentum signals high, abandonment fires | *the* moment Recall exists for | a wrong card would destroy trust here | the Phase 4E gates (`_MIN_RESUME_INTENT`, depth filter) — *missed > weak* |
| next morning, launcher opens | *"Continue today"* header + one recovery card with evidence chip | the **first-recovery ceremony** (Phase 5C) flashes once: *"Recall noticed unfinished work. Pick a card to resume."* | the ceremony only fires once — never repeats | tracked in `~/.recall/ceremonies.json` |
| user clicks Resume | files + tabs reopen in the prescribed order | the room is back — *"wait, it remembered that?"* | a restored target may have moved | the launcher footer summarises (`Restored 4 of 5`) without alarm |

**End of Day 3:** the milestone moment. If this happens cleanly
once, the next four days take care of themselves.

## Day 4+ — repeat use

| | What happens | Trust moment | Friction risk | Mitigation |
|---|---|---|---|---|
| morning open | *"Continue today"* header | the time-of-day swap (Phase 5B) | feels like a notification system to a sceptical user | it isn't — there are no pushes, no badges, no streaks |
| evening open | *"You paused here"* header | the same calm tool, different question | over-rotation if recoveries keep coming | recovery stays selective by design |
| `recall stats --today` | the local-only daily score | the user sees the loop is working, on their machine, for them | nothing is shared | enforced by `TRUST_LEDGER.md` — `build_export()` cannot include today's data |

**End of Week 1:** the user reopened Recall voluntarily on at
least three of the seven days. That is the success criterion.

---

## The recurring patterns

Three patterns dominate first-user friction (also in
[`FIRST_USE_AUDIT.md`](FIRST_USE_AUDIT.md)):

1. **First-week silence.** Days 0–1 look empty by design; the
   product cannot lie about that. Calm copy carries those days.
2. **Hidden extension install.** The most common reason the
   browser-memory section stays empty. The popup's pairing CTAs
   address it; `recall doctor` flags it explicitly.
3. **Restoration choreography pacing.** When a Resume opens five
   targets fast, the user can lose orientation. Mitigated by the
   prescribed order (files → chats → tabs → searches) and the
   single footer line summarising the outcome.

## What this file is for

A first-public-alpha user runs into all of the above with no
founder nearby. This file is the founder's audit that every row
has a designed answer — and the link back to the code or copy that
delivers it. When a row has no answer, that is the next thing to
build.
