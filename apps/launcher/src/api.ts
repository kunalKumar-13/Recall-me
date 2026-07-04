// Every engine call goes through a Rust command (reqwest → 127.0.0.1:4545).
// The webview never touches the network directly — no fetch, no CORS.

import { invoke } from "@tauri-apps/api/core";
import type {
  HealthResponse,
  RecoveryRecentResponse,
  SearchResponse,
  ThreadsRecentResponse,
  ThreadEvolutionResponse,
} from "./types";

export const engineHealth = () => invoke<HealthResponse>("engine_health");

export const recoveryRecent = (n = 3) =>
  invoke<RecoveryRecentResponse>("recovery_recent", { n });

export const recoveryRestore = (id: string) =>
  invoke<unknown>("recovery_restore", { id });

export const search = (q: string) => invoke<SearchResponse>("search", { q });

export const threadsRecent = (n = 6) =>
  invoke<ThreadsRecentResponse>("threads_recent", { n });

export const threadEvolution = (id: string) =>
  invoke<ThreadEvolutionResponse>("thread_evolution", { id });

export const openTarget = (kind: string, target: string) =>
  invoke<void>("open_target", { kind, target });

export const resizeHeight = (height: number) =>
  invoke<void>("resize_height", { height });
