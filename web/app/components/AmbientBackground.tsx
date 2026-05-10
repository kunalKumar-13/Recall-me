/**
 * Ambient background — entirely static.
 *
 * Light-mode version: the page wash already lives in body's CSS
 * gradient (lavender from above, hints of cyan and mint at the
 * corners). All this component adds is the dot-grid texture, which
 * gives the cream surface a tactile feel without any paint cost
 * beyond first render. No animated layers, no blur filters, nothing
 * that touches scroll performance.
 */
export function AmbientBackground() {
  return (
    <div
      aria-hidden
      className="fixed inset-0 -z-10 overflow-hidden pointer-events-none"
    >
      <div className="absolute inset-0 grid-texture" />
    </div>
  );
}
