// Recall landing v2 — wired destinations.
// One edit propagates to every CTA, footer link, modal trigger.

// Phase 11B — repointed download + extension to the placeholder
// files under apps/web/public/downloads/. The real .dmg / .zip
// artifacts replace these placeholder names when the production
// release pipeline ships.
export const V2_LINKS = {
  github:    "https://github.com/kunalKumar-13/Recall-me",
  docs:      "/docs",
  download:  "/downloads/recall-0.1.0-alpha-placeholder.txt",
  extension: "/downloads/recall-extension-placeholder.txt",
  windowsLite: "/downloads/recall-0.1.0-alpha-placeholder.txt",
  windowsFull: "/downloads/recall-0.1.0-alpha-placeholder.txt",
  macos:     "/downloads/recall-0.1.0-alpha-placeholder.txt",
} as const;

export const V2_ANCHORS = {
  hero:       "#v2-hero",
  window:     "#v2-window",
  continuity: "#v2-continuity",
  privacy:    "#v2-privacy",
  timeline:   "#v2-timeline",
  search:     "#v2-search-surface",
  demo:       "#v2-demo",
  final:      "#v2-final",
} as const;
