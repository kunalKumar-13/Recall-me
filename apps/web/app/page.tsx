import { Download } from "./components/v2/Download";
import { Engine } from "./components/v2/Engine";
import { Extension } from "./components/v2/Extension";
import { Faq } from "./components/v2/Faq";
import { Features } from "./components/v2/Features";
import { Finale } from "./components/v2/Finale";
import { Pipeline } from "./components/v2/Pipeline";
import { Stats } from "./components/v2/Stats";
import { Story } from "./components/v2/Story";
import { Terminal } from "./components/v2/Terminal";
import { Hero } from "./components/v2/Hero";
import { Privacy } from "./components/v2/Privacy";
import { ReadingThread } from "./components/v2/ReadingThread";
import { Rule } from "./lib/reveal";
import { SiteNav } from "./components/v2/SiteNav";
import { SiteFooter } from "./components/v2/SiteFooter";

/**
 * v3 landing — porcelain, ink, one red thread, drawn on a drafting
 * frame. Chapters rule across the page rails:
 *
 *   Hero → Stats band → [01] Film → [02] Capabilities bento →
 *   [03] Architecture beams → [04] Extension → [05] Engine table →
 *   [06] Privacy (+ live log) → FAQ → Download → Finale
 */
export default function Page() {
  return (
    <>
      <SiteNav />
      <ReadingThread />
      <main>
        <Hero />
        <Stats />
        <Story />
        <Rule />
        <Features />
        <Rule />
        <Pipeline />
        <Rule />
        <Extension />
        <Rule />
        <Engine />
        <Rule />
        <Terminal />
        <Privacy />
        <Rule />
        <Faq />
        <Download />
        <Finale />
      </main>
      <SiteFooter />
    </>
  );
}
