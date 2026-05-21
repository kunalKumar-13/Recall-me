import { AmbientBackground } from "./components/AmbientBackground";
import { FAQ } from "./components/FAQ";
import { Features } from "./components/Features";
import { FinalCTA } from "./components/FinalCTA";
import { Footer } from "./components/Footer";
import { Hero } from "./components/Hero";
import { HowItWorks } from "./components/HowItWorks";
import { Nav } from "./components/Nav";
import { Privacy } from "./components/Privacy";
import { ThreadConstellation } from "./components/ThreadConstellation";
import { TrustedBy } from "./components/TrustedBy";

/**
 * Page narrative — one calm scroll:
 *
 *     Hero                  the launcher + the promise
 *     TrustedBy             who the continuity layer is for
 *     HowItWorks            capture → group → ask → restore
 *     Features              what the system actually exposes
 *     ThreadConstellation   threads, connected — no metaphor
 *     Privacy               the bind is the boundary
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
        <TrustedBy />
        <HowItWorks />
        <Features />
        <ThreadConstellation />
        <Privacy />
        <FAQ />
        <FinalCTA />
      </main>
      <Footer />
    </>
  );
}
