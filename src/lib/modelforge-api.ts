// Client for the ModelForge backend (model_forge_v2/backend).
//
// Requests go to relative "/api/v1/..." paths, which next.config.ts rewrites
// to the FastAPI service (see MODELFORGE_BACKEND_URL there). This mirrors
// the request shape used by model_forge_v2/frontend/src/services/api.ts so
// the two frontends talk to the backend the same way.

const BASE = "/api/v1";

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const resp = await fetch(`${BASE}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  if (!resp.ok) {
    const detail = await resp.json().catch(() => ({}));
    throw new Error(detail.detail || `Request failed: ${resp.status}`);
  }
  if (resp.status === 204) return undefined as T;
  return resp.json();
}

export interface AttemptSummary {
  attempt_number: number;
  provider_id: string;
  model_id: string;
  status: string;
  error_code: string | null;
}

export interface CompleteResponse {
  succeeded: boolean;
  answer: string | null;
  provider_id: string | null;
  model_id: string | null;
  task_type: string;
  routing_id: string | null;
  attempts: AttemptSummary[];
  decision_reasons: string[];
}

export interface ModelSpec {
  model_id: string;
  provider_id: string;
  display_name: string;
  enabled: boolean;
  context_window: number;
  capabilities: string[];
  [key: string]: unknown;
}

export interface SystemStatus {
  provider_count: number;
  enabled_provider_count: number;
  model_count: number;
  enabled_model_count: number;
  resource_snapshot: Record<string, unknown>;
}

export const modelforgeApi = {
  // The "just answer this" endpoint: fully automatic model selection +
  // fallback. This is what the chat UI calls for a freeform prompt.
  complete: (prompt: string, privacy = "INTERNAL", policyId?: string, maxTokens?: number) =>
    request<CompleteResponse>("/complete", {
      method: "POST",
      body: JSON.stringify({
        prompt,
        privacy_classification: privacy,
        policy_id: policyId || null,
        max_tokens: maxTokens || null,
      }),
    }),

  listModels: () => request<ModelSpec[]>("/models"),

  status: () => request<SystemStatus>("/system/status"),
};
