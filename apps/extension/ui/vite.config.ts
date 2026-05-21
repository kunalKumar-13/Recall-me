import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

/**
 * The popup is built into `apps/extension/popup/` and the MV3
 * `manifest.json` points its `default_popup` there. Chrome loads
 * `apps/extension/` as the unpacked extension; `manifest.json` and
 * `background.js` stay hand-written at that root, and only the popup
 * UI is a build artifact.
 *
 * `base: "./"` makes every asset URL relative — an extension page is
 * loaded from a `chrome-extension://` origin, not a web server root.
 */
export default defineConfig({
  plugins: [react()],
  base: "./",
  build: {
    outDir: "../popup",
    emptyOutDir: true,
    // One small popup — no need to split chunks across files.
    rollupOptions: {
      output: {
        entryFileNames: "assets/[name].js",
        chunkFileNames: "assets/[name].js",
        assetFileNames: "assets/[name].[ext]",
      },
    },
  },
});
