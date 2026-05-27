"use client";

// Recall landing v2 — page composition.
// Nav + 9 sections + Footer + Watch-demo modal.
// Anchors: #v2-hero, #v2-window, #v2-continuity, #v2-privacy,
// #v2-timeline, #v2-search-surface, #v2-demo, #v2-final.

import * as React from "react";
import { Nav } from "./components/v2/Nav";
import { Hero } from "./components/v2/Hero";
import { MemoryOSWindow } from "./components/v2/MemoryOSWindow";
import { ContinuityAnimation } from "./components/v2/ContinuityAnimation";
import { RecoveryFlow } from "./components/v2/RecoveryFlow";
import { BrowserCapture } from "./components/v2/BrowserCapture";
import { PrivacyGrid } from "./components/v2/PrivacyGrid";
import { ResumeTimeline } from "./components/v2/ResumeTimeline";
import { SearchSurface } from "./components/v2/SearchSurface";
import { DemoBand } from "./components/v2/DemoBand";
import { FinalCTA } from "./components/v2/FinalCTA";
import { Footer } from "./components/v2/Footer";
import { ModalHost } from "./components/v2/ModalHost";

export default function Page() {
  const [demoOpen, setDemoOpen] = React.useState(false);
  return (
    <div className="v2-root" style={{ position: "relative" }}>
      <Nav />
      <main>
        <Hero onOpenDemo={() => setDemoOpen(true)} />
        <MemoryOSWindow />
        <ContinuityAnimation />
        <RecoveryFlow />
        <BrowserCapture />
        <PrivacyGrid />
        <ResumeTimeline />
        <SearchSurface />
        <DemoBand onOpen={() => setDemoOpen(true)} />
        <FinalCTA />
      </main>
      <Footer />
      <ModalHost open={demoOpen} onClose={() => setDemoOpen(false)} />
    </div>
  );
}
