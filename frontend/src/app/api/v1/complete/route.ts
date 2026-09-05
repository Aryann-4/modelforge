import { NextResponse } from "next/server";

const providers = [
  {
    provider_id: "mock-cloud",
    name: "Mock Cloud Provider",
    type: "MOCK",
    enabled: true,
    health: "HEALTHY",
  },
  {
    provider_id: "mock-local",
    name: "Mock Local Provider",
    type: "MOCK",
    enabled: true,
    health: "HEALTHY",
  },
  {
    provider_id: "mock-flaky",
    name: "Mock Flaky Provider",
    type: "MOCK",
    enabled: true,
    health: "HEALTHY",
  },
];

const models = [
  {
    model_id: "mock-cloud-large",
    provider_id: "mock-cloud",
    display_name: "Mock Cloud Large",
    enabled: true,
    context_window: 128000,
    execution_type: "CLOUD",
    capabilities: ["REASONING", "CODING", "LONG_CONTEXT", "STRUCTURED_OUTPUT"],
    cost_metadata: { estimated_input_cost_per_1k: 1.0, estimated_output_cost_per_1k: 3.0 },
    latency_metadata: { estimated_latency_ms: 1200 },
    reliability_metadata: { configured_success_rate: 0.98 },
  },
  {
    model_id: "mock-cloud-vision",
    provider_id: "mock-cloud",
    display_name: "Mock Cloud Vision",
    enabled: true,
    context_window: 64000,
    execution_type: "CLOUD",
    capabilities: ["VISION", "REASONING"],
    cost_metadata: { estimated_input_cost_per_1k: 1.5, estimated_output_cost_per_1k: 4.0 },
    latency_metadata: { estimated_latency_ms: 1500 },
    reliability_metadata: { configured_success_rate: 0.95 },
  },
  {
    model_id: "mock-local-small",
    provider_id: "mock-local",
    display_name: "Mock Local Small",
    enabled: true,
    context_window: 32000,
    execution_type: "LOCAL",
    capabilities: ["CODING", "REASONING"],
    cost_metadata: { estimated_input_cost_per_1k: 0.0, estimated_output_cost_per_1k: 0.0 },
    latency_metadata: { estimated_latency_ms: 400 },
    reliability_metadata: { configured_success_rate: 0.99 },
  },
  {
    model_id: "mock-local-large",
    provider_id: "mock-local",
    display_name: "Mock Local Large",
    enabled: true,
    context_window: 100000,
    execution_type: "LOCAL",
    capabilities: ["CODING", "REASONING", "LONG_CONTEXT"],
    cost_metadata: { estimated_input_cost_per_1k: 0.0, estimated_output_cost_per_1k: 0.0 },
    latency_metadata: { estimated_latency_ms: 900 },
    reliability_metadata: { configured_success_rate: 0.97 },
  },
  {
    model_id: "mock-flaky-model",
    provider_id: "mock-flaky",
    display_name: "Mock Flaky Model",
    enabled: true,
    context_window: 16000,
    execution_type: "CLOUD",
    capabilities: ["CODING"],
    cost_metadata: { estimated_input_cost_per_1k: 0.5, estimated_output_cost_per_1k: 1.0 },
    latency_metadata: { estimated_latency_ms: 500 },
    reliability_metadata: { configured_success_rate: 0.6 },
  },
];

let routeCounter = 0;

function classifyTask(prompt: string): string {
  const lower = prompt.toLowerCase();
  if (/\b(code|python|function|script|debug|compile|class|api)\b/.test(lower)) return "CODING";
  if (/\b(image|scan|drawing|pdf|photo|ocr|diagram|p&id|visual)\b/.test(lower)) return "VISION";
  if (/\b(reason|think|explain|analyze|plan|strategy|logic)\b/.test(lower)) return "REASONING";
  return "GENERAL";
}

function selectModel(taskType: string) {
  const eligible = models.filter((m) => m.enabled);
  if (taskType === "VISION") {
    return eligible.find((m) => m.capabilities.includes("VISION")) || eligible[0];
  }
  if (taskType === "CODING") {
    return (
      eligible
        .filter((m) => m.capabilities.includes("CODING"))
        .sort((a, b) => a.latency_metadata.estimated_latency_ms - b.latency_metadata.estimated_latency_ms)[0] || eligible[0]
    );
  }
  return (
    eligible.sort((a, b) => b.reliability_metadata.configured_success_rate - a.reliability_metadata.configured_success_rate)[0] ||
    eligible[0]
  );
}

export async function POST(request: Request) {
  const body = await request.json();
  const { prompt, privacy_classification = "INTERNAL" } = body;

  const taskType = classifyTask(prompt);
  const selected = selectModel(taskType);
  const routingId = `route_${(routeCounter++).toString(16).padStart(12, "0")}`;

  const attempts: Array<{
    attempt_number: number;
    provider_id: string;
    model_id: string;
    status: string;
    error_code: string | null;
  }> = [];

  // Simulate: flaky model fails on first attempt if selected
  if (selected.provider_id === "mock-flaky") {
    attempts.push({
      attempt_number: 1,
      provider_id: "mock-flaky",
      model_id: "mock-flaky-model",
      status: "FAILED",
      error_code: "MODEL_ERROR",
    });
    // Fallback to cloud
    const fallback = models.find((m) => m.model_id === "mock-cloud-large")!;
    attempts.push({
      attempt_number: 2,
      provider_id: "mock-cloud",
      model_id: "mock-cloud-large",
      status: "SUCCEEDED",
      error_code: null,
    });
    return NextResponse.json({
      succeeded: true,
      answer: `[mock:${fallback.model_id}] simulated response to: '${prompt.slice(0, 120)}'`,
      provider_id: "mock-cloud",
      model_id: fallback.model_id,
      task_type: taskType,
      routing_id: routingId,
      attempts,
      decision_reasons: [`Selected ${selected.model_id}: Provider permitted; Privacy policy satisfied; Hardware sufficient`],
    });
  }

  attempts.push({
    attempt_number: 1,
    provider_id: selected.provider_id,
    model_id: selected.model_id,
    status: "SUCCEEDED",
    error_code: null,
  });

  return NextResponse.json({
    succeeded: true,
    answer: `[mock:${selected.model_id}] simulated response to: '${prompt.slice(0, 120)}'`,
    provider_id: selected.provider_id,
    model_id: selected.model_id,
    task_type: taskType,
    routing_id: routingId,
    attempts,
    decision_reasons: [`Selected ${selected.model_id}: Provider permitted; Privacy policy satisfied; Lower estimated latency`],
  });
}
