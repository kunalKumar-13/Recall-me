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
