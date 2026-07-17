import { Compare } from "./components/v2/Compare";
import { Download } from "./components/v2/Download";
import { Extension } from "./components/v2/Extension";
import { Faq } from "./components/v2/Faq";
import { Features } from "./components/v2/Features";
import { OpenBand } from "./components/v2/OpenBand";
import { Pipeline } from "./components/v2/Pipeline";
import { Stats } from "./components/v2/Stats";
import { Story } from "./components/v2/Story";
import { Surfaces } from "./components/v2/Surfaces";
import { Hero } from "./components/v2/Hero";
import { LabRow } from "./components/v2/LabRow";
import { Privacy } from "./components/v2/Privacy";
import { TryIt } from "./components/v2/TryIt";
import { ReadingThread } from "./components/v2/ReadingThread";
import { Rule } from "./lib/reveal";
import { SiteNav } from "./components/v2/SiteNav";
import { SiteFooter } from "./components/v2/SiteFooter";

/**
 * The landing — porcelain, ink, one red thread, drawn on a drafting
 * frame. Eight chapters, one arc, no repeats:
 *
 *   Hero → Stats band → [01] Film → [02] Capabilities →
 *   [03] Architecture → [04] Extension → [05] Local-first →
 *   [06] The honest table → open band → [07] FAQ → [08] Get Recall
 */
export default function Page() {
  return (
    <>
      <SiteNav />
      <ReadingThread />
      <main>
        <Hero />
        <LabRow />
        <TryIt />
        <Stats />
        <Story />
        <Rule />
        <Features />
        <Rule />
        <Pipeline />
        <Rule />
        <Extension />
        <Rule />
        <Surfaces />
        <Rule />
        <Privacy />
        <Rule />
        <Compare />
        <OpenBand />
        <Faq />
        <Download />
      </main>
      <SiteFooter />
    </>
  );
}
