import { Hero } from "./components/v2/Hero";
import { ReadingThread } from "./components/v2/ReadingThread";
import { SiteNav } from "./components/v2/SiteNav";
import { SiteFooter } from "./components/v2/SiteFooter";

/**
 * v2 landing — porcelain, ink, one red thread.
 *
 * Assembled section by section:
 *   Hero → Stats → Film → How → Screens → Terminal → Extension →
 *   Engine → Privacy → FAQ → Download → Finale
 */
export default function Page() {
  return (
    <>
      <SiteNav />
      <ReadingThread />
      <main>
        <Hero />
      </main>
      <SiteFooter />
    </>
  );
}
