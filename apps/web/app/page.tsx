import { Download } from "./components/v2/Download";
import { Engine } from "./components/v2/Engine";
import { Extension } from "./components/v2/Extension";
import { Faq } from "./components/v2/Faq";
import { Film } from "./components/v2/Film";
import { Finale } from "./components/v2/Finale";
import { How } from "./components/v2/How";
import { ScreensTrio } from "./components/v2/ScreensTrio";
import { Stats } from "./components/v2/Stats";
import { Terminal } from "./components/v2/Terminal";
import { Hero } from "./components/v2/Hero";
import { Privacy } from "./components/v2/Privacy";
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
        <Stats />
        <Film />
        <How />
        <ScreensTrio />
        <Terminal />
        <Extension />
        <Engine />
        <Privacy />
        <Faq />
        <Download />
        <Finale />
      </main>
      <SiteFooter />
    </>
  );
}
