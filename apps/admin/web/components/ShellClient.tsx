"use client";

import { useState } from "react";

import { CommandPalette } from "./CommandPalette";
import { TopBar, type TopBarStats } from "./TopBar";

/**
 * Phase 6J — client wrapper around the TopBar + CommandPalette.
 *
 * The layout passes server-computed `TopBarStats` in; this client
 * component owns the palette-open state and bridges the keyboard
 * shortcut to the modal. Keeps the rest of the shell server-rendered.
 */

export function ShellClient({ stats }: { stats: TopBarStats }) {
  const [open, setOpen] = useState(false);
  return (
    <>
      <TopBar stats={stats} onOpenPalette={() => setOpen(true)} />
      <CommandPalette open={open} onClose={() => setOpen(false)} />
    </>
  );
}
