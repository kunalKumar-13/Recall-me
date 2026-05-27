"use client";

// Section 8 — Demo poster band. Click opens the demo modal.

import * as React from "react";
import { useReveal } from "./hooks";
import { Play, Search } from "./icons";

export function DemoBand({ onOpen }: { onOpen: () => void }) {
  const headRef = useReveal<HTMLDivElement>();
  const posterRef = useReveal<HTMLDivElement>(0.15);
  return (
    <section id="v2-demo" className="v2-section" style={{ position: "relative" }}>
      <div className="v2-section-wrap">
        <div
          ref={headRef}
          className="reveal"
          style={{
            textAlign: "center",
            marginBottom: 50,
            maxWidth: 820,
            marginLeft: "auto",
            marginRight: "auto",
          }}
        >
          <div className="v2-eyebrow" style={{ justifyContent: "center", marginBottom: 18 }}>
            08 — Demo
          </div>
          <h2 className="v2-section-title">
            Two minutes<br />
            <span className="v2-serif-italic">on a real machine.</span>
          </h2>
        </div>

        <div
          ref={posterRef}
          className="reveal"
          style={{ ["--delay" as never]: "120ms", maxWidth: 1100, margin: "0 auto" }}
        >
          <button
            type="button"
            onClick={onOpen}
            style={{
              width: "100%",
              padding: 0,
              border: "none",
              background: "transparent",
              cursor: "pointer",
              borderRadius: 20,
              position: "relative",
              overflow: "hidden",
              display: "block",
              boxShadow:
                "0 1px 0 rgba(255,255,255,0.04) inset, " +
                "0 50px 100px -40px rgba(0,0,0,0.8), " +
                "0 0 100px -20px rgba(139,127,227,0.35)",
            }}
          >
            <div
              style={{
                height: 540,
                background:
                  "radial-gradient(ellipse 60% 50% at 50% 50%, #1A1525 0%, #07070A 70%)",
                border: "1px solid var(--hairline-strong)",
                borderRadius: 20,
                position: "relative",
                overflow: "hidden",
              }}
            >
              <div
                style={{
                  position: "absolute",
                  left: "50%",
                  top: "50%",
                  transform: "translate(-50%, -50%)",
                }}
              >
                <DemoPoster />
              </div>

              <div
                className="v2-demo-overlay"
                style={{
                  position: "absolute",
                  inset: 0,
                  background: "rgba(7,7,10,0.55)",
                  transition: "background 240ms ease",
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                }}
              >
                <div
                  className="v2-demo-play"
                  style={{
                    width: 86,
                    height: 86,
                    borderRadius: "50%",
                    background: "linear-gradient(180deg, #A597F0, #8B7FE3)",
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "center",
                    color: "var(--white)",
                    boxShadow:
                      "0 1px 0 rgba(255,255,255,0.30) inset, " +
                      "0 0 0 1px rgba(139,127,227,0.5), " +
                      "0 20px 50px -10px rgba(115,95,214,0.6), " +
                      "0 0 80px -10px rgba(139,127,227,0.6)",
                    transition: "transform 240ms cubic-bezier(.2,.7,.2,1)",
                    marginLeft: 6,
                  }}
                >
                  <Play size={28} />
                </div>
              </div>

              <div
                style={{
                  position: "absolute",
                  bottom: 22,
                  left: 24,
                  right: 24,
                  display: "flex",
                  justifyContent: "space-between",
                  alignItems: "flex-end",
                  color: "var(--white)",
                }}
              >
                <div>
                  <div
                    style={{
                      fontFamily: "var(--font-mono)",
                      fontSize: 11,
                      color: "var(--accent)",
                      letterSpacing: "0.18em",
                      textTransform: "uppercase",
                      marginBottom: 6,
                    }}
                  >
                    full demo · 0:44
                  </div>
                  <div
                    style={{
                      fontSize: 24,
                      fontWeight: 500,
                      letterSpacing: "-0.022em",
                    }}
                  >
                    The launcher, the extension, the recovery flow.
                  </div>
                </div>
                <span
                  style={{
                    fontFamily: "var(--font-mono)",
                    fontSize: 10.5,
                    color: "var(--text-2)",
                    letterSpacing: "0.18em",
                    padding: "4px 10px",
                    border: "1px solid rgba(255,255,255,0.18)",
                    borderRadius: 6,
                  }}
                >
                  1080p
                </span>
              </div>
            </div>
          </button>
        </div>
      </div>

      <style jsx>{`
        button:hover :global(.v2-demo-overlay) { background: rgba(7,7,10,0.30); }
        button:hover :global(.v2-demo-play)    { transform: scale(1.06); }
      `}</style>
    </section>
  );
}

function DemoPoster() {
  return (
    <div
      style={{
        width: 580,
        height: 360,
        background: "#FFFFFF",
        borderRadius: 18,
        border: "1px solid rgba(0,0,0,0.06)",
        overflow: "hidden",
        boxShadow: "0 30px 80px -20px rgba(0,0,0,0.5)",
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
        <span style={{ color: "#A1A1AA", display: "flex" }}>
          <Search size={15} />
        </span>
        <span style={{ fontSize: 14, color: "#A1A1AA", flex: 1 }}>
          Start typing to recover…
        </span>
      </div>
      <div
        style={{
          flex: 1,
          padding: 18,
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
        }}
      >
        <div
          style={{
            background: "#FAF8F4",
            border: "1px solid #E6DED4",
            borderRadius: 14,
            padding: "14px 16px",
            position: "relative",
            width: "100%",
          }}
        >
          <div
            style={{
              position: "absolute",
              left: 0,
              top: 14,
              bottom: 14,
              width: 2,
              background: "#8B7FE3",
            }}
          />
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
      </div>
    </div>
  );
}
