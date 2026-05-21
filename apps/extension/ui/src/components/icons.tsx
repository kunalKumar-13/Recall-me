/**
 * A small, quiet icon set — stroked, 1.6px, `currentColor`. No
 * filled glyphs, no brand marks, nothing that reads as decoration.
 * Each icon names a surface the popup actually shows.
 */
type IconProps = { size?: number; className?: string };

function svg(path: React.ReactNode, size = 16, className?: string) {
  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth={1.6}
      strokeLinecap="round"
      strokeLinejoin="round"
      className={className}
      aria-hidden
    >
      {path}
    </svg>
  );
}

export const Icon = {
  search: ({ size, className }: IconProps) =>
    svg(
      <>
        <circle cx="10.5" cy="10.5" r="6.5" />
        <path d="M20 20l-4.5-4.5" />
      </>,
      size,
      className,
    ),
  tab: ({ size, className }: IconProps) =>
    svg(
      <>
        <rect x="3" y="5" width="18" height="14" rx="2.5" />
        <path d="M3 9h18" />
      </>,
      size,
      className,
    ),
  chat: ({ size, className }: IconProps) =>
    svg(
      <>
        <path d="M4 5h16v11H9l-5 4z" />
        <path d="M8 9h8M8 12h5" />
      </>,
      size,
      className,
    ),
  file: ({ size, className }: IconProps) =>
    svg(
      <>
        <path d="M7 3h8l4 4v14H7z" />
        <path d="M14 3v5h5" />
      </>,
      size,
      className,
    ),
  resume: ({ size, className }: IconProps) =>
    svg(
      <>
        <circle cx="12" cy="12" r="9" />
        <path d="M10 9l5 3-5 3z" fill="currentColor" />
      </>,
      size,
      className,
    ),
  thread: ({ size, className }: IconProps) =>
    svg(
      <>
        <circle cx="6" cy="7" r="2.2" />
        <circle cx="18" cy="17" r="2.2" />
        <path d="M6 9.2v3.3A4 4 0 0 0 10 16.5h5.8" />
      </>,
      size,
      className,
    ),
  lock: ({ size, className }: IconProps) =>
    svg(
      <>
        <rect x="4" y="10" width="16" height="11" rx="2" />
        <path d="M8 10V7a4 4 0 0 1 8 0v3" />
      </>,
      size,
      className,
    ),
  gear: ({ size, className }: IconProps) =>
    svg(
      <>
        <circle cx="12" cy="12" r="3.2" />
        <path d="M12 2.5v3M12 18.5v3M4.6 4.6l2.1 2.1M17.3 17.3l2.1 2.1M2.5 12h3M18.5 12h3M4.6 19.4l2.1-2.1M17.3 6.7l2.1-2.1" />
      </>,
      size,
      className,
    ),
  back: ({ size, className }: IconProps) =>
    svg(<path d="M15 5l-7 7 7 7" />, size, className),
  open: ({ size, className }: IconProps) =>
    svg(
      <>
        <path d="M14 4h6v6" />
        <path d="M20 4l-9 9" />
        <path d="M18 14v5a1 1 0 0 1-1 1H5a1 1 0 0 1-1-1V7a1 1 0 0 1 1-1h5" />
      </>,
      size,
      className,
    ),
};
