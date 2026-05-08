import { AmbientBackground } from "./components/AmbientBackground";
import { BuiltForThinkers } from "./components/BuiltForThinkers";
import { Features } from "./components/Features";
import { FinalCTA } from "./components/FinalCTA";
import { Footer } from "./components/Footer";
import { Hero } from "./components/Hero";
import { Nav } from "./components/Nav";
import { Privacy } from "./components/Privacy";
import { Problem } from "./components/Problem";

export default function Page() {
  return (
    <>
      <AmbientBackground />
      <Nav />
      <main className="relative">
        <Hero />
        <Problem />
        <Features />
        <Privacy />
        <BuiltForThinkers />
        <FinalCTA />
      </main>
      <Footer />
    </>
  );
}
