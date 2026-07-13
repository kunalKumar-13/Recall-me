import type { Metadata } from "next";
import { ConsoleClient } from "./Client";

export const metadata: Metadata = {
  title: "Console — Recall",
  description:
    "The engine room. Talks to your local Recall daemon on 127.0.0.1:4545 from your own browser — the site never sees your data.",
  robots: { index: false },
};

export default function ConsolePage() {
  return <ConsoleClient />;
}
