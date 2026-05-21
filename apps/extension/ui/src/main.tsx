import React from "react";
import { createRoot } from "react-dom/client";
import { App } from "./App";
import "./styles.css";

/**
 * Popup entry. The popup is a single mounted React tree; there is no
 * router and no persistence beyond `chrome.storage` — when the popup
 * closes the tree is torn down, and it re-fetches on next open. That
 * is the right model for a memory *surface*: always a fresh, honest
 * read of the daemon, never a stale cached dashboard.
 */
const root = document.getElementById("root");
if (root) {
  createRoot(root).render(
    <React.StrictMode>
      <App />
    </React.StrictMode>,
  );
}
