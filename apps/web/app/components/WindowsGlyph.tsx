/**
 * Windows logo — four-pane glyph used inside the Download CTA.
 * Pure SVG, no font dependency, sized via className.
 */
export function WindowsGlyph({ className }: { className?: string }) {
  return (
    <svg
      viewBox="0 0 16 16"
      className={className}
      fill="currentColor"
      aria-hidden
    >
      <path d="M0 2.5L6.5 1.6V7.5H0V2.5Z" />
      <path d="M7.5 1.45L16 0.25V7.5H7.5V1.45Z" />
      <path d="M0 8.5H6.5V14.4L0 13.5V8.5Z" />
      <path d="M7.5 8.5H16V15.75L7.5 14.55V8.5Z" />
    </svg>
  );
}
