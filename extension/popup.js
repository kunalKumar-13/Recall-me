const HEALTH = "http://127.0.0.1:49827/health";

const enabledEl = document.getElementById("enabled");
const dotEl = document.getElementById("status-dot");
const textEl = document.getElementById("status-text");

// Initial state.
chrome.storage.local.get(["enabled"], (r) => {
  enabledEl.checked = r.enabled !== false;
});

enabledEl.addEventListener("change", () => {
  chrome.storage.local.set({ enabled: enabledEl.checked });
});

// Health check the local daemon.
(async () => {
  try {
    const r = await fetch(HEALTH, { method: "GET", cache: "no-store" });
    if (!r.ok) throw new Error(`status ${r.status}`);
    const data = await r.json();
    const ingested =
      typeof data.ingested_total === "number" ? data.ingested_total : 0;
    dotEl.classList.add("ok");
    textEl.textContent = `Connected · ${ingested.toLocaleString()} captured`;
  } catch (e) {
    dotEl.classList.add("warn");
    textEl.textContent =
      "Recall daemon not responding. Start the desktop app.";
  }
})();
