"use client";

import { useCallback, useEffect, useState } from "react";

/**
 * Theme switch — sun/moon, persisted to localStorage, defaulting to
 * the OS preference (the inline script in layout.tsx applies it
 * before first paint so there is no flash).
 */
export function ThemeToggle() {
  const [theme, setTheme] = useState<string | null>(null);

  useEffect(() => {
    setTheme(document.documentElement.dataset.theme || "light");
  }, []);

  const flip = useCallback(() => {
    const next =
      document.documentElement.dataset.theme === "dark" ? "light" : "dark";
    document.documentElement.dataset.theme = next;
    try {
      localStorage.setItem("recall-theme", next);
    } catch {
      /* private mode — the choice just doesn't persist */
    }
    setTheme(next);
  }, []);

  const dark = theme === "dark";
  return (
    <button
      className="themebtn"
      onClick={flip}
      aria-label={dark ? "Switch to light" : "Switch to dark"}
      title={dark ? "Lamp on" : "Lamp off"}
    >
      {dark ? (
        <svg viewBox="0 0 16 16" width="15" height="15" aria-hidden>
          <circle cx="8" cy="8" r="3.4" fill="none" stroke="currentColor" strokeWidth="1.3" />
          <path
            d="M8 1.2v1.8M8 13v1.8M1.2 8H3M13 8h1.8M3.2 3.2l1.3 1.3M11.5 11.5l1.3 1.3M12.8 3.2l-1.3 1.3M4.5 11.5l-1.3 1.3"
            stroke="currentColor"
            strokeWidth="1.3"
            strokeLinecap="round"
          />
        </svg>
      ) : (
        <svg viewBox="0 0 16 16" width="15" height="15" aria-hidden>
          <path
            d="M13.4 9.6A5.8 5.8 0 0 1 6.4 2.6a5.8 5.8 0 1 0 7 7Z"
            fill="none"
            stroke="currentColor"
            strokeWidth="1.3"
            strokeLinejoin="round"
          />
        </svg>
      )}
    </button>
  );
}
