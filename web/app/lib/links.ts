/**
 * Centralized destinations.
 *
 * Every external URL on the page lives here so a single edit updates
 * Nav + Hero + FinalCTA + Footer + FAQ in lockstep. Internal anchors
 * (those starting with `#`) are also collected here so renaming a
 * section id propagates without grep-hunting.
 */
export const LINKS = {
  // External — canonical repo + release.
  github: "https://github.com/kunalKumar-13/Recall-me",
  release: "https://github.com/kunalKumar-13/Recall-me/releases/latest",
  // Watch-the-demo target. Internal scroll to the How It Works
  // section until a real Loom/YouTube URL exists. When the recording
  // is ready, swap this to the public video URL — every CTA picks
  // it up automatically.
  demoVideo: "#how",
  // Docs link in the nav. Falls back to the README on GitHub.
  docs: "https://github.com/kunalKumar-13/Recall-me#readme",
  // Public issues queue — used by the FAQ side card.
  issues: "https://github.com/kunalKumar-13/Recall-me/issues",
  // Email contact for the footer.
  contact: "mailto:admin@recall.me",
} as const;

/**
 * Section anchor ids — change them here, not at the call site.
 * The nav links use these to scroll-jump.
 */
export const ANCHORS = {
  top: "#top",
  how: "#how",
  features: "#features",
  privacy: "#privacy",
  faq: "#faq",
  download: "#download",
} as const;
