"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";

/**
 * Phase 6J — System Console copy button.
 *
 * Puts the pre-rendered diagnostics blob on the clipboard. Same
 * fallback ladder as the ActionsBar buttons. No server roundtrip.
 */
export function CopyDiagnostics({ blob }: { blob: string }) {
  const [copied, setCopied] = useState(false);
  const router = useRouter();

  async function onCopy() {
    try {
      await navigator.clipboard.writeText(blob);
    } catch {
      const t = document.createElement("textarea");
      t.value = blob;
      document.body.appendChild(t);
      t.select();
      document.execCommand("copy");
      document.body.removeChild(t);
    }
    setCopied(true);
    setTimeout(() => setCopied(false), 1400);
  }

  return (
    <div style={{ display: "flex", gap: 8 }}>
      <button
        type="button"
        onClick={onCopy}
        className="actions-btn"
        style={{ padding: "8px 14px", maxWidth: 200 }}
      >
        <span className="actions-btn-label">{copied ? "Copied" : "Copy diagnostics"}</span>
        <span className="actions-btn-hint">markdown · clipboard</span>
      </button>
      <button
        type="button"
        onClick={() => router.refresh()}
        className="actions-btn"
        style={{ padding: "8px 14px", maxWidth: 160 }}
      >
        <span className="actions-btn-label">Live refresh</span>
        <span className="actions-btn-hint">re-read filesystem</span>
      </button>
    </div>
  );
}
