"use client";

// Demo modal — opens when user clicks "Watch demo" anywhere on the
// page. Cycles a 4-stage mini-launcher poster every 2.2s. Escape
// closes; clicking the scrim closes; body scroll locked while open.

import * as React from "react";
import { Check, Close, Pause, Play, Search } from "./icons";

const LABELS = ["search", "detect", "recover", "resume"];

export function ModalHost({ open, onClose }: { open: boolean; onClose: () => void }) {
  React.useEffect(() => {
    if (!open) return;
    const onKey = (e: KeyboardEvent) => {
      if (e.key === "Escape") onClose();
    };
    document.body.style.overflow = "hidden";
    window.addEventListener("keydown", onKey);
    return () => {
      document.body.style.overflow = "";
      window.removeEventListener("keydown", onKey);
    };
  }, [open, onClose]);

  if (!open) return null;

  return (
    <div style={{ position: "fixed", inset: 0, zIndex: 999, animation: "v2-modal-in 240ms ease" }}>
      <div
        onClick={onClose}
        style={{
          position: "absolute",
          inset: 0,
          background: "rgba(7,7,10,0.78)",
          backdropFilter: "blur(10px) saturate(140%)",
          WebkitBackdropFilter: "blur(10px) saturate(140%)",
        }}
      />
      <div
        style={{
          position: "absolute",
          inset: 0,
          pointerEvents: "none",
          background:
            "radial-gradient(ellipse 60% 50% at 50% 40%, rgba(139,127,227,0.22), transparent 60%)",
        }}
      />
      <div
        style={{
          position: "absolute",
          top: "50%",
          left: "50%",
          transform: "translate(-50%, -50%)",
          width: "min(1080px, calc(100vw - 48px))",
          maxHeight: "calc(100vh - 64px)",
          overflow: "auto",
          background: "linear-gradient(180deg, #14141C 0%, #0A0A10 100%)",
          border: "1px solid rgba(139,127,227,0.22)",
          borderRadius: 20,
          boxShadow:
            "0 1px 0 rgba(255,255,255,0.05) inset, " +
            "0 60px 120px -40px rgba(0,0,0,0.8), " +
            "0 0 120px -20px rgba(139,127,227,0.40)",
          animation: "v2-modal-pop 320ms cubic-bezier(.2,.7,.2,1)",
        }}
      >
        <ModalContent onClose={onClose} />
      </div>
    </div>
  );
}

function ModalContent({ onClose }: { onClose: () => void }) {
  return (
    <>
      <div
        style={{
          display: "flex",
          alignItems: "flex-start",
          justifyContent: "space-between",
          padding: "24px 28px 20px",
          borderBottom: "1px solid var(--hairline)",
          gap: 16,
        }}
      >
        <div>
          <div className="v2-eyebrow" style={{ marginBottom: 10 }}>Watch demo</div>
          <div
            style={{
              fontSize: 22,
              fontWeight: 500,
              letterSpacing: "-0.022em",
              color: "var(--white)",
            }}
          >
            Two minutes of Recall on a real machine.
          </div>
        </div>
        <button
          onClick={onClose}
          aria-label="Close"
          style={{
            width: 36,
            height: 36,
            borderRadius: 10,
            border: "1px solid var(--hairline)",
            background: "rgba(255,255,255,0.02)",
            color: "var(--muted)",
            cursor: "pointer",
            display: "inline-flex",
            alignItems: "center",
            justifyContent: "center",
          }}
        >
          <Close size={16} />
        </button>
      </div>
      <div style={{ padding: "24px 28px 32px" }}>
        <ModalPlayer />
      </div>
    </>
  );
}

function ModalPlayer() {
  const [stage, setStage] = React.useState(0);
  React.useEffect(() => {
    const id = setInterval(() => setStage((s) => (s + 1) % 4), 2200);
    return () => clearInterval(id);
  }, []);
  return (
    <>
      <div
        style={{
          borderRadius: 14,
          overflow: "hidden",
          border: "1px solid var(--hairline)",
          background: "#06060A",
          boxShadow:
            "0 1px 0 rgba(255,255,255,0.04) inset, 0 30px 80px -30px rgba(0,0,0,0.7), 0 0 60px -20px rgba(139,127,227,0.30)",
        }}
      >
        <div
          style={{
            height: 420,
            background:
              "radial-gradient(ellipse 80% 70% at 50% 50%, #18141F 0%, #06060B 70%)",
            position: "relative",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            overflow: "hidden",
          }}
        >
          <ModalLauncher stage={stage} />
        </div>
        <div
          style={{
            display: "flex",
            alignItems: "center",
            gap: 14,
            padding: "14px 18px",
            borderTop: "1px solid var(--hairline)",
            background: "rgba(255,255,255,0.015)",
            fontFamily: "var(--font-mono)",
            fontSize: 11,
            color: "var(--muted)",
            letterSpacing: "0.04em",
          }}
        >
          <span
            style={{
              width: 28,
              height: 28,
              borderRadius: 8,
              background: "var(--primary)",
              color: "var(--bg)",
              display: "inline-flex",
              alignItems: "center",
              justifyContent: "center",
              boxShadow: "0 0 0 1px rgba(139,127,227,0.45), 0 0 16px rgba(139,127,227,0.5)",
            }}
          >
            <Pause size={11} />
          </span>
          <span style={{ color: "var(--text-2)", minWidth: 50 }}>
            0:{String((stage + 1) * 11).padStart(2, "0")}
          </span>
          <div
            style={{
              flex: 1,
              height: 3,
              background: "var(--hairline)",
              borderRadius: 2,
              position: "relative",
            }}
          >
            <div
              style={{
                position: "absolute",
                left: 0,
                top: 0,
                bottom: 0,
                width: `${((stage + 1) / 4) * 100}%`,
                background: "linear-gradient(90deg, var(--primary), var(--accent))",
                borderRadius: 2,
                transition: "width 220ms ease",
                boxShadow: "0 0 10px var(--primary)",
              }}
            />
          </div>
          <span style={{ minWidth: 50, textAlign: "right" }}>0:44</span>
          <span
            style={{
              padding: "2px 8px",
              border: "1px solid var(--hairline)",
              borderRadius: 5,
              color: "var(--faint)",
              textTransform: "uppercase",
              letterSpacing: "0.14em",
            }}
          >
            1080p
          </span>
        </div>
      </div>
      <div
        style={{
          marginTop: 18,
          display: "grid",
          gridTemplateColumns: "repeat(4, 1fr)",
          gap: 1,
          background: "var(--hairline)",
          border: "1px solid var(--hairline)",
          borderRadius: 12,
          overflow: "hidden",
        }}
      >
        {LABELS.map((l, i) => {
          const active = i === stage;
          return (
            <div
              key={i}
              style={{
                padding: "14px 18px",
                background: active ? "rgba(139,127,227,0.10)" : "#0A0A10",
                fontFamily: "var(--font-mono)",
                fontSize: 10.5,
                fontWeight: 500,
                color: active ? "var(--primary)" : "var(--faint)",
                letterSpacing: "0.16em",
                textTransform: "uppercase",
                transition: "background 240ms ease, color 240ms ease",
              }}
            >
              0{i + 1} · {l}
            </div>
          );
        })}
      </div>
    </>
  );
}

function ModalLauncher({ stage }: { stage: number }) {
  return (
    <div
      style={{
        width: 580,
        height: 360,
        background: "#FFFFFF",
        borderRadius: 18,
        border: "1px solid rgba(0,0,0,0.06)",
        overflow: "hidden",
        boxShadow: "0 30px 80px -20px rgba(0,0,0,0.5), 0 0 80px -10px rgba(139,127,227,0.4)",
        display: "flex",
        flexDirection: "column",
        fontFamily: "var(--font-sans)",
        color: "#161618",
      }}
    >
      <div
        style={{
          height: 50,
          padding: "0 16px",
          display: "flex",
          alignItems: "center",
          gap: 12,
          borderBottom: "1px solid rgba(0,0,0,0.06)",
        }}
      >
        <span style={{ color: "#A1A1AA", display: "flex" }}><Search size={15} /></span>
        <span style={{ fontSize: 14, color: "#161618", flex: 1 }}>
          {stage === 0 ? "chatgpt websock" : stage <= 2 ? "chatgpt websocket" : ""}
          {stage === 3 && <span style={{ color: "#A1A1AA" }}>Start typing to recover…</span>}
          {stage <= 2 && (
            <span
              style={{
                display: "inline-block",
                width: 1.5,
                height: 14,
                background: "#8B7FE3",
                marginLeft: 2,
                animation: "v2-caret 1s steps(2) infinite",
              }}
            />
          )}
        </span>
      </div>
      <div style={{ flex: 1, padding: 12, position: "relative" }}>
        <div
          style={{
            position: "absolute",
            inset: 14,
            opacity: stage <= 1 ? 1 : 0,
            transition: "opacity 240ms ease",
          }}
        >
          <MLRow icon="●" title="WebSocket retry debugging" meta="2 days · 5 events" selected />
          <MLRow icon="◆" title="proposal — websocket fallback.md" meta="~/notes · 2d" />
          <MLRow icon="◇" title="ChatGPT — retry semantics" meta="4 visits · 3d" />
        </div>
        <div
          style={{
            position: "absolute",
            inset: 14,
            opacity: stage === 2 ? 1 : 0,
            transition: "opacity 240ms ease",
          }}
        >
          <MLRecover />
        </div>
        <div
          style={{
            position: "absolute",
            inset: 0,
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            opacity: stage === 3 ? 1 : 0,
            transition: "opacity 240ms ease",
          }}
        >
          <MLRestored />
        </div>
      </div>
    </div>
  );
}

function MLRow({
  icon,
  title,
  meta,
  selected,
}: { icon: string; title: string; meta: string; selected?: boolean }) {
  return (
    <div
      style={{
        display: "flex",
        alignItems: "center",
        gap: 12,
        padding: "10px 12px",
        borderRadius: 9,
        marginBottom: 4,
        background: selected ? "rgba(139,127,227,0.10)" : "transparent",
        position: "relative",
      }}
    >
      {selected && (
        <span
          style={{
            position: "absolute",
            left: 0,
            top: 8,
            bottom: 8,
            width: 2.5,
            borderRadius: 2,
            background: "#8B7FE3",
          }}
        />
      )}
      <span
        style={{
          color: selected ? "#8B7FE3" : "#71717A",
          fontSize: 11,
          width: 14,
          textAlign: "center",
        }}
      >
        {icon}
      </span>
      <span style={{ flex: 1, fontSize: 13.5, color: "#161618", fontWeight: selected ? 500 : 400 }}>
        {title}
      </span>
      <span style={{ fontFamily: "var(--font-mono)", fontSize: 11, color: "#A1A1AA" }}>{meta}</span>
    </div>
  );
}

function MLRecover() {
  return (
    <div
      style={{
        background: "#FAF8F4",
        border: "1px solid #E6DED4",
        borderRadius: 14,
        padding: "14px 16px",
        position: "relative",
      }}
    >
      <div style={{ position: "absolute", left: 0, top: 14, bottom: 14, width: 2, background: "#8B7FE3" }} />
      <div
        style={{
          fontFamily: "var(--font-mono)",
          fontSize: 10.5,
          color: "#71717A",
          letterSpacing: "0.09em",
          textTransform: "uppercase",
          marginBottom: 8,
        }}
      >
        Continue · Returned after 2 days
      </div>
      <div
        style={{
          fontSize: 20,
          fontWeight: 500,
          color: "#161618",
          letterSpacing: "-0.02em",
          marginBottom: 12,
        }}
      >
        WebSocket retry debugging
      </div>
      <div style={{ display: "flex", gap: 6, marginBottom: 14 }}>
        {["2 files", "2 tabs", "1 search"].map((l) => (
          <span
            key={l}
            style={{
              display: "inline-flex",
              alignItems: "center",
              height: 24,
              padding: "0 10px",
              borderRadius: 7,
              background: "#fff",
              border: "1px solid #E6DED4",
              fontSize: 12,
              color: "#161618",
            }}
          >
            {l}
          </span>
        ))}
      </div>
      <div style={{ display: "flex", gap: 8 }}>
        <span
          style={{
            height: 32,
            padding: "0 14px",
            borderRadius: 9,
            background: "#8B7FE3",
            color: "#fff",
            display: "inline-flex",
            alignItems: "center",
            gap: 7,
            fontSize: 13,
            fontWeight: 500,
          }}
        >
          Resume{" "}
          <span
            style={{
              fontFamily: "var(--font-mono)",
              fontSize: 10.5,
              background: "rgba(255,255,255,0.2)",
              padding: "1px 5px",
              borderRadius: 4,
            }}
          >
            ↵
          </span>
        </span>
        <span
          style={{
            height: 32,
            padding: "0 14px",
            borderRadius: 9,
            background: "#fff",
            border: "1px solid #E6DED4",
            color: "#161618",
            display: "inline-flex",
            alignItems: "center",
            fontSize: 13,
            fontWeight: 500,
          }}
        >
          Review
        </span>
      </div>
    </div>
  );
}

function MLRestored() {
  return (
    <div style={{ textAlign: "center" }}>
      <div
        style={{
          width: 56,
          height: 56,
          margin: "0 auto 16px",
          borderRadius: "50%",
          background: "linear-gradient(135deg, #B79EFF, #8B7FE3)",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          boxShadow: "0 0 40px rgba(139,127,227,0.6)",
          color: "#fff",
        }}
      >
        <Check size={22} />
      </div>
      <div style={{ fontSize: 18, fontWeight: 500, color: "#161618", marginBottom: 6 }}>
        Restored — 2 files · 2 tabs · 1 chat
      </div>
      <div style={{ fontFamily: "var(--font-mono)", fontSize: 12, color: "#71717A" }}>
        opened in order
      </div>
    </div>
  );
}
