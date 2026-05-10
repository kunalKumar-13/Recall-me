import { AmbientBackground } from "./components/AmbientBackground";
import { BuiltForThinkers } from "./components/BuiltForThinkers";
import { FAQ } from "./components/FAQ";
import { Features } from "./components/Features";
import { FinalCTA } from "./components/FinalCTA";
import { Footer } from "./components/Footer";
import { Hero } from "./components/Hero";
import { HowItWorks } from "./components/HowItWorks";
import { MemoryVisualization } from "./components/MemoryVisualization";
import { Nav } from "./components/Nav";
import { Privacy } from "./components/Privacy";

/**
 * Page narrative arc — matches the canonical reference exactly:
 *
 *   Hero                  — relationship named, dashboard glimpsed
 *   BuiltForThinkers      — TRUSTED BY THINKERS & BUILDERS strip
 *   HowItWorks            — 4 quiet steps + the small memory diagram
 *   MemoryVisualization   — single dark moment: the connected memory core
 *   Features              — six what-it-does tiles
 *   Privacy               — yours-alone pledge + shield card
 *   FAQ                   — common questions + "still have questions?"
 *   FinalCTA              — short, centered close
 *   Footer                — brand + three columns + socials
 */
export default function Page() {
  return (
    <>
      <AmbientBackground />
      <Nav />
      <main className="relative">
        <Hero />
        <BuiltForThinkers />
        <HowItWorks />
        <MemoryVisualization />
        <Features />
        <Privacy />
        <FAQ />
        <FinalCTA />
      </main>
      <Footer />
    </>
  );
}
