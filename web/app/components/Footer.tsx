import { Logo } from "./Logo";

export function Footer() {
  return (
    <footer className="relative py-12 px-6 border-t border-white/[0.06]">
      <div className="max-w-6xl mx-auto flex items-center justify-between gap-6 flex-wrap">
        <div className="flex items-center gap-2.5">
          <Logo className="w-6 h-6" />
          <span className="text-white/85 font-semibold tracking-tight">
            Recall
          </span>
          <span className="text-white/35 text-sm hidden md:inline">
            — ask your computer what you forgot
          </span>
        </div>
        <div className="flex items-center gap-5 text-sm text-white/45">
          <a
            href="https://github.com"
            className="hover:text-white/85 transition-colors"
          >
            GitHub
          </a>
          <a href="#privacy" className="hover:text-white/85 transition-colors">
            Privacy
          </a>
          <a href="#" className="hover:text-white/85 transition-colors">
            Contact
          </a>
        </div>
      </div>
      <div className="max-w-6xl mx-auto mt-8 text-xs text-white/25">
        © {new Date().getFullYear()} Recall. Local-first. Yours alone.
      </div>
    </footer>
  );
}
