// Every engine call goes through a Rust command (reqwest → 127.0.0.1:4545).
// The webview never touches the network directly — no fetch, no CORS.

import { invoke } from "@tauri-apps/api/core";
import type { HealthResponse, RecoveryRecentResponse } from "./types";

export const engineHealth = () => invoke<HealthResponse>("engine_health");

export const recoveryRecent = (n = 3) =>
  invoke<RecoveryRecentResponse>("recovery_recent", { n });

export const recoveryRestore = (id: string) =>
  invoke<unknown>("recovery_restore", { id });

export const resizeHeight = (height: number) =>
  invoke<void>("resize_height", { height });
