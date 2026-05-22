import { AmbientBackground } from "./components/AmbientBackground";
import { Download } from "./components/Download";
import { FAQ } from "./components/FAQ";
import { Features } from "./components/Features";
import { FinalCTA } from "./components/FinalCTA";
import { Footer } from "./components/Footer";
import { Hero } from "./components/Hero";
import { HowItWorks } from "./components/HowItWorks";
import { Nav } from "./components/Nav";
import { Privacy } from "./components/Privacy";
import { Problem } from "./components/Problem";
import { Screens } from "./components/Screens";
import { Story } from "./components/Story";
import { ThreadConstellation } from "./components/ThreadConstellation";

/**
 * Page narrative — one calm scroll, Phase 6G alpha-public order:
 *
 *     Hero                  the launcher + the promise
 *     Problem               the context-loss tax this fixes
 *     HowItWorks            capture → group → ask → restore
 *     Story                 three real-shape investigations
 *                           (WebSocket / Proposal / Research)
 *     Features              what the system actually exposes
 *     ThreadConstellation   threads, connected — no metaphor
 *     Screens               launcher + extension v2 captures
 *     Privacy               trust — local / no cloud / no telemetry /
 *                           counts only / export only
 *     Download              four artifacts, one calm grid
 *     FAQ                   the open questions
 *     FinalCTA              calm close
 *
 * Each section is its own act. The page does not loop animations,
 * does not parallax, does not glow. Motion exists only on entrance.
 */
export default function Page() {
  return (
    <>
      <AmbientBackground />
      <Nav />
      <main className="relative">
        <Hero />
        <Problem />
        <HowItWorks />
        <Story />
        <Features />
        <ThreadConstellation />
        <Screens />
        <Privacy />
        <Download />
        <FAQ />
        <FinalCTA />
      </main>
      <Footer />
    </>
  );
}
