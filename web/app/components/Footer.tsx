import { ANCHORS, LINKS } from "../lib/links";
import { Logo } from "./Logo";

type Col = {
  heading: string;
  links: { label: string; href: string; external?: boolean }[];
};

const COLUMNS: Col[] = [
  {
    heading: "Product",
    links: [
      { label: "Features", href: ANCHORS.features },
      { label: "How it works", href: ANCHORS.how },
      { label: "Download", href: LINKS.release, external: true },
    ],
  },
  {
    heading: "Resources",
    links: [
      { label: "Docs", href: LINKS.docs, external: true },
      { label: "Changelog", href: LINKS.github, external: true },
      { label: "Roadmap", href: LINKS.issues, external: true },
    ],
  },
  {
    heading: "Company",
    links: [
      { label: "Privacy", href: ANCHORS.privacy },
      { label: "Security", href: ANCHORS.privacy },
      { label: "Contact", href: LINKS.contact },
    ],
  },
];

function GitHubGlyph() {
  return (
    <svg viewBox="0 0 24 24" className="w-4 h-4" fill="currentColor" aria-hidden>
      <path d="M12 .5C5.65.5.5 5.65.5 12c0 5.08 3.29 9.39 7.86 10.91.58.11.79-.25.79-.56v-2c-3.2.7-3.88-1.36-3.88-1.36-.53-1.34-1.29-1.7-1.29-1.7-1.05-.72.08-.7.08-.7 1.16.08 1.77 1.19 1.77 1.19 1.03 1.77 2.7 1.26 3.36.97.1-.75.4-1.27.74-1.56-2.55-.29-5.24-1.28-5.24-5.7 0-1.26.45-2.29 1.19-3.1-.12-.3-.52-1.47.11-3.07 0 0 .97-.31 3.18 1.18a11 11 0 0 1 5.78 0c2.21-1.49 3.18-1.18 3.18-1.18.63 1.6.23 2.77.12 3.07.74.81 1.19 1.84 1.19 3.1 0 4.43-2.69 5.4-5.26 5.69.41.36.78 1.06.78 2.14v3.17c0 .31.21.68.79.56C20.21 21.39 23.5 17.08 23.5 12c0-6.35-5.15-11.5-11.5-11.5z" />
    </svg>
  );
}

function TwitterGlyph() {
  return (
    <svg viewBox="0 0 24 24" className="w-4 h-4" fill="currentColor" aria-hidden>
      <path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231 5.45-6.231zm-1.161 17.52h1.833L7.084 4.126H5.117l11.966 15.643z" />
    </svg>
  );
}

function DiscordGlyph() {
  return (
    <svg viewBox="0 0 24 24" className="w-4 h-4" fill="currentColor" aria-hidden>
      <path d="M20.317 4.37A19.79 19.79 0 0 0 16.885 3.3a.07.07 0 0 0-.073.035 13.5 13.5 0 0 0-.61 1.252 18.27 18.27 0 0 0-5.487 0 12.6 12.6 0 0 0-.62-1.252.08.08 0 0 0-.073-.035 19.74 19.74 0 0 0-3.432 1.07.06.06 0 0 0-.03.025C2.91 9.05 2.06 13.58 2.5 18.06a.08.08 0 0 0 .03.054 19.9 19.9 0 0 0 5.99 3.03.08.08 0 0 0 .085-.028 14.16 14.16 0 0 0 1.225-1.99.075.075 0 0 0-.04-.105 13.1 13.1 0 0 1-1.872-.892.075.075 0 0 1-.008-.125c.126-.094.252-.192.372-.291a.07.07 0 0 1 .075-.01c3.927 1.793 8.18 1.793 12.061 0a.07.07 0 0 1 .076.009c.12.099.246.198.373.292a.075.075 0 0 1-.006.125 12.3 12.3 0 0 1-1.873.891.075.075 0 0 0-.04.106 15.85 15.85 0 0 0 1.225 1.99.075.075 0 0 0 .084.028 19.84 19.84 0 0 0 6.002-3.03.077.077 0 0 0 .03-.054c.5-5.177-.838-9.674-3.548-13.661a.06.06 0 0 0-.031-.026zM8.02 15.33c-1.183 0-2.157-1.085-2.157-2.42 0-1.333.955-2.42 2.157-2.42 1.21 0 2.176 1.097 2.157 2.42 0 1.335-.956 2.42-2.157 2.42zm7.974 0c-1.182 0-2.157-1.085-2.157-2.42 0-1.333.955-2.42 2.157-2.42 1.211 0 2.176 1.097 2.157 2.42 0 1.335-.946 2.42-2.157 2.42z" />
    </svg>
  );
}

/**
 * Footer — three columns of links, brand block on the left with
 * social icons, and a bottom strip with copyright + tagline.
 *
 * Static markup; no JS required at runtime, no interaction state.
 */
export function Footer() {
  return (
    <footer className="relative pt-16 pb-10 px-5 md:px-8 border-t border-hairline">
      <div className="max-w-[1280px] mx-auto">
        <div className="grid grid-cols-1 md:grid-cols-12 gap-10">
          {/* ── Brand block ────────────────────────────────────── */}
          <div className="md:col-span-5">
            <a
              href={ANCHORS.top}
              className="flex items-center gap-2.5 group"
              aria-label="Recall.me — home"
            >
              <Logo className="w-6 h-6" />
              <span className="text-ink-bright font-semibold tracking-tight text-[16px]">
                Recall<span className="text-ink-dim font-normal">.me</span>
              </span>
            </a>
            <p className="mt-3 text-[13.5px] text-ink leading-relaxed max-w-xs">
              The private AI memory layer
              <br />
              for your laptop.
            </p>

            <div className="mt-5 flex items-center gap-2">
              <SocialLink href={LINKS.github} label="GitHub">
                <GitHubGlyph />
              </SocialLink>
              <SocialLink href="https://twitter.com" label="Twitter / X">
                <TwitterGlyph />
              </SocialLink>
              <SocialLink href="https://discord.com" label="Discord">
                <DiscordGlyph />
              </SocialLink>
            </div>
          </div>

          {/* ── Three link columns ────────────────────────────── */}
          {COLUMNS.map((col) => (
            <div key={col.heading} className="md:col-span-2 lg:col-span-2">
              <div className="text-[10.5px] font-semibold tracking-[0.18em] text-ink-dim uppercase">
                {col.heading}
              </div>
              <ul className="mt-4 space-y-3">
                {col.links.map((l) => (
                  <li key={l.label}>
                    <a
                      href={l.href}
                      target={l.external ? "_blank" : undefined}
                      rel={l.external ? "noopener noreferrer" : undefined}
                      className="
                        text-[13.5px] text-ink hover:text-ink-bright
                        transition-colors duration-300
                      "
                    >
                      {l.label}
                    </a>
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>

        <div className="mt-12 pt-6 border-t border-hairline flex items-center justify-between gap-4 flex-wrap">
          <p className="text-[12px] text-ink-dim">
            © {new Date().getFullYear()} Recall.me. All rights reserved.
          </p>
          <p className="text-[12px] text-ink-dim">
            Built with <span className="text-lavender-deep">♡</span> for thinkers.
          </p>
        </div>
      </div>
    </footer>
  );
}

function SocialLink({
  href,
  label,
  children,
}: {
  href: string;
  label: string;
  children: React.ReactNode;
}) {
  return (
    <a
      href={href}
      target="_blank"
      rel="noopener noreferrer"
      aria-label={label}
      className="
        inline-flex items-center justify-center
        w-9 h-9 rounded-lg
        text-ink hover:text-ink-bright
        bg-bg-base hover:bg-bg-raised
        border border-hairline
        transition-colors duration-300
      "
    >
      {children}
    </a>
  );
}
