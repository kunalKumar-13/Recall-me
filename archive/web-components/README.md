# `archive/web-components`

Web components that used to be part of the marketing site's
page narrative but were retired between Phase 3A and Phase 4C
as the landing copy tightened around the *continuity-operating-
system* positioning. Kept here (rather than deleted) so the
PRs that bring them back, if any, can `git mv` them rather
than recreate them.

## Inventory

| File | Retired in | Why |
|---|---|---|
| `BuiltForThinkers.tsx` | Phase 3A | The role-marketing strip ("Trusted by thinkers & builders") didn't earn its weight under the new infrastructure-grade framing. Architecture + EvolutionTimeline took its slot. |
| `Demo.tsx` | Phase 3A | Standalone "demo" section replaced by the launcher-style ContinueWorking card. |
| `HowItWorks.tsx` | Phase 3A | Four-step explainer replaced by the more honest "six layers, composed upward" Architecture section. |
| `LauncherMockup.tsx` | Phase 3A | The Hero's right column used to be a Mac-style launcher mockup; replaced by the ContinuityCore composition. |
| `MemoryReconstruction.tsx` | Phase 3A | Earlier visualization. Superseded by EvolutionTimeline (which is honest about transition colour semantics). |
| `MemoryVisualization.tsx` | Phase 3A | The cinematic "memory core" orb-and-cards section. Hero's ContinuityCore is the singular replacement. |
| `Privacy.tsx` | Phase 3A | Shield-art + pledge cards. Replaced by `LocalFirstTopology` (terminal + JSONL excerpt — *the bind is the boundary*). |
| `Problem.tsx` | Phase 3A | "The problem" framing was AI-startup-shaped. Hero's headline carries the same job in one sentence. |
| `QRBlock.tsx` | Phase 3A | Floating QR card that paired with `LauncherMockup`. |
| `TrustBadges.tsx` | Phase 3A | "Local · No cloud · No telemetry" badges. Replaced by the mono trust line `127.0.0.1:4545 · ~/.recall · MIT` in the Hero. |

## What's still live

The components still imported by `apps/web/app/page.tsx` and
related surfaces — see
[`apps/web/app/components/`](../../apps/web/app/components/)
for the live set.

## Restoration

If a future phase brings any of these back:

1. `git mv archive/web-components/<File>.tsx
   apps/web/app/components/<File>.tsx`
2. Add the import to the appropriate page or component.
3. Update this README's table to remove the row.
4. Update [`CHANGELOG.md`](../../docs/release/CHANGELOG.md) with the
   restore.

No PR should *reference* an archived component from outside
this directory. If you find yourself needing one, restore
it — don't import across the archive boundary.
