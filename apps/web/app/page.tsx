import { AmbientBackground } from "./components/AmbientBackground";
import { Architecture } from "./components/Architecture";
import { ContinueWorking } from "./components/ContinueWorking";
import { EvolutionTimeline } from "./components/EvolutionTimeline";
import { FAQ } from "./components/FAQ";
import { Features } from "./components/Features";
import { FinalCTA } from "./components/FinalCTA";
import { Footer } from "./components/Footer";
import { Hero } from "./components/Hero";
import { LocalFirstTopology } from "./components/LocalFirstTopology";
import { Nav } from "./components/Nav";

/**
 * Page narrative — one cinematic arc:
 *
 *     Hero                  fragmentary memory → continuity core
 *     Architecture          the six-layer stack stabilizes upward
 *     EvolutionTimeline     one thread, gaining structure
 *     ContinueWorking       the emotional payoff
 *     Features              what the system actually exposes
 *     LocalFirstTopology    the bind is the boundary
 *     FAQ                   the open questions
 *     FinalCTA              calm certainty
 *
 * Each section is its own act. The page does not loop animations,
 * does not parallax, does not glow. Motion exists where it earns
 * its weight — entrance staggers on view, the continuity-core
 * convergence on first paint, the evolution trace's one-shot draw.
 *
 * The HowItWorks + MemoryVisualization + BuiltForThinkers sections
 * have been retired. Their roles are now covered by:
 *
 *   • Hero's ContinuityCore (replaces the abstract memory orb)
 *   • Architecture (replaces "how it works" with the actual layer
 *     hierarchy)
 *   • ContinueWorking (replaces the role-marketing strip with the
 *     real launcher digest surface)
 */
export default function Page() {
  return (
    <>
      <AmbientBackground />
      <Nav />
      <main className="relative">
        <Hero />
        <Architecture />
        <EvolutionTimeline />
        <ContinueWorking />
        <Features />
        <LocalFirstTopology />
        <FAQ />
        <FinalCTA />
      </main>
      <Footer />
    </>
  );
}
