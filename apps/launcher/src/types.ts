// Mirrors the engine's real wire shapes (api/schemas.py).

export interface OpenableTarget {
  kind: "url" | "path";
  target: string;
}

export interface EventOut {
  ts: string;
  session_id: string;
  kind: string;
  title: string;
  url: string;
  domain: string;
  payload: Record<string, unknown>;
}

export interface RecoveryCandidate {
  id: string;
  thread_id: string;
  title: string;
  last_active_at: number;
  continuity_score: number;
  recovery_confidence: number;
  representative_events: EventOut[];
  suggested_targets: OpenableTarget[];
  related_sessions: string[];
  related_contexts: number;
  unresolved_signals: string[];
  signals: Record<string, unknown>;
  why: string[];
  preview_caption: string;
  last_phase_title: string;
  last_phase_transition: string;
}

export interface RecoveryRecentResponse {
  candidates: RecoveryCandidate[];
  elapsed_ms: number;
}

export interface HealthResponse {
  status: string;
  events_dir: string;
}

// ---- search surface (mirrors api/schemas.py SearchResponse) ----

export interface EpisodicResult {
  kind: string;
  title: string;
  subtitle: string;
  url: string;
  ts_epoch: number;
  score: number;
  session_id: string;
}

export interface SessionResult {
  session_id: string;
  topic: string;
  label: string;
  time_label: string;
  score: number;
  event_count: number;
  // Capture C5 — behavioural attention shape from the dwell signal.
  // `behavioural_label` is "" when there's no signal worth adding.
  work_blocks: number;
  behavioural_label: string;
  kinds: string[];
  preview_events: EventOut[];
  openable_targets: OpenableTarget[];
}

export interface MicroContextResult {
  topic: string;
  label: string;
  time_label: string;
  event_count: number;
  kinds: string[];
  match_count: number;
  preview_events: EventOut[];
  openable_targets: OpenableTarget[];
}

export interface SearchResponse {
  query: string;
  episodic: EpisodicResult[];
  contexts: MicroContextResult[];
  sessions: SessionResult[];
  elapsed_ms: number;
}

// ---- file search (mirrors api/schemas.py FileSearchResponse) ----

export interface FileHit {
  path: string;
  name: string;
  snippet: string;
  score: number;
  ext: string;
}

export interface FileSearchResponse {
  query: string;
  results: FileHit[];
  enabled: boolean;
  elapsed_ms: number;
}

// ---- restoration (mirrors api/schemas.py restore plan) ----

export interface RestorationStep {
  kind: "url" | "path";
  target: string;
  group: "files" | "chats" | "tabs" | "searches";
  reason: string;
}

export interface RestorationPlan {
  id: string;
  thread_id: string;
  title: string;
  preview_caption: string;
  steps: RestorationStep[];
  // Annotated by the Rust command after execution — the tally of
  // what actually opened vs what the plan asked for.
  requested?: number;
  opened?: number;
}

// ---- launcher settings (mirrors lib.rs settings_get) ----

export interface LauncherSettings {
  hotkey: string;
  autostart: boolean;
  folders: number;
  config_path: string;
}

// ---- resurfacing (mirrors api/schemas.py ResurfacedContextOut) ----

export interface ResurfacedContext {
  topic: string;
  label: string;
  time_label: string;
  score: number;
  confidence: number;
  event_count: number;
  kinds: string[];
  preview_events: EventOut[];
  openable_targets: OpenableTarget[];
  why: string[];
  signals: Record<string, unknown>;
}

export interface ResurfaceIdleResponse {
  contexts: ResurfacedContext[];
  enabled: boolean;
  elapsed_ms: number;
}

// ---- threads & evolution (mirrors api/schemas.py) ----

export interface Thread {
  id: string;
  topic_key: string;
  title: string;
  confidence: number;
  created_at: number;
  updated_at: number;
  event_count: number;
  session_count: number;
  surface_types: string[];
  representative_queries: string[];
  representative_targets: OpenableTarget[];
  timeline_summary: string;
  signals: Record<string, unknown>;
  why: string[];
}

export interface ThreadsRecentResponse {
  threads: Thread[];
  elapsed_ms: number;
}

export interface EvolutionPhase {
  id: string;
  thread_id: string;
  title: string;
  start_at: number;
  end_at: number;
  event_count: number;
  dominant_surface: string;
  representative_queries: string[];
  representative_targets: OpenableTarget[];
  momentum_score: number;
  revisit_score: number;
  transition: string;
  signals: Record<string, unknown>;
  why: string[];
}

export interface ThreadEvolutionResponse {
  thread_id: string;
  phases: EvolutionPhase[];
  span_start: number;
  span_end: number;
  elapsed_ms: number;
}
