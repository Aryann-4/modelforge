import { NextResponse } from "next/server";

const OPENAI_API_KEY = process.env.OPENAI_API_KEY;

const models = [
  {
    model_id: "gpt-4o",
    provider_id: "openai",
    display_name: "GPT-4o",
    enabled: true,
    context_window: 128000,
    capabilities: ["REASONING", "CODING", "LONG_CONTEXT", "STRUCTURED_OUTPUT"],
  },
  {
    model_id: "gpt-4o-mini",
    provider_id: "openai",
    display_name: "GPT-4o Mini",
    enabled: true,
    context_window: 128000,
    capabilities: ["CODING", "REASONING"],
  },
  {
    model_id: "gpt-3.5-turbo",
    provider_id: "openai",
    display_name: "GPT-3.5 Turbo",
    enabled: true,
    context_window: 16000,
    capabilities: ["CODING"],
  },
];

function classifyTask(prompt: string): string {
  const lower = prompt.toLowerCase();
  if (/\b(code|python|function|script|debug|compile|class|api|bug)\b/.test(lower)) return "CODING";
  if (/\b(image|scan|drawing|pdf|photo|ocr|diagram|visual)\b/.test(lower)) return "VISION";
  if (/\b(reason|think|explain|analyze|plan|strategy|logic)\b/.test(lower)) return "REASONING";
  return "GENERAL";
}

function selectModel(taskType: string) {
  if (taskType === "CODING") return models.find((m) => m.model_id === "gpt-4o")!;
  if (taskType === "VISION") return models.find((m) => m.model_id === "gpt-4o")!;
  if (taskType === "REASONING") return models.find((m) => m.model_id === "gpt-4o")!;
  return models.find((m) => m.model_id === "gpt-4o-mini")!;
}

export async function POST(request: Request) {
  if (!OPENAI_API_KEY) {
    return NextResponse.json(
      { succeeded: false, answer: null, provider_id: null, model_id: null, task_type: "GENERAL", routing_id: null, attempts: [], decision_reasons: ["OPENAI_API_KEY not configured. Set it in Vercel → Settings → Environment Variables."] },
      { status: 500 }
    );
  }

  const body = await request.json();
  const { prompt } = body;

  const taskType = classifyTask(prompt);
  const selected = selectModel(taskType);
  const routingId = `route_${Date.now().toString(16)}`;

  try {
    const res = await fetch("https://api.openai.com/v1/chat/completions", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${OPENAI_API_KEY}`,
      },
      body: JSON.stringify({
        model: selected.model_id,
        messages: [{ role: "user", content: prompt }],
        max_tokens: 1024,
      }),
    });

    const data = await res.json();

    if (!res.ok) {
      return NextResponse.json({
        succeeded: false,
        answer: null,
        provider_id: "openai",
        model_id: selected.model_id,
        task_type: taskType,
        routing_id: routingId,
        attempts: [{ attempt_number: 1, provider_id: "openai", model_id: selected.model_id, status: "FAILED", error_code: data.error?.message || "UNKNOWN_ERROR" }],
        decision_reasons: [`Selected ${selected.model_id} but OpenAI returned an error: ${data.error?.message || res.status}`],
      });
    }

    const answer = data.choices?.[0]?.message?.content || "No response generated.";

    return NextResponse.json({
      succeeded: true,
      answer,
      provider_id: "openai",
      model_id: selected.model_id,
      task_type: taskType,
      routing_id: routingId,
      attempts: [{ attempt_number: 1, provider_id: "openai", model_id: selected.model_id, status: "SUCCEEDED", error_code: null }],
      decision_reasons: [`Routed to ${selected.model_id} for ${taskType} task`],
    });
  } catch (err) {
    const message = err instanceof Error ? err.message : "Unknown error";
    return NextResponse.json({
      succeeded: false,
      answer: null,
      provider_id: "openai",
      model_id: selected.model_id,
      task_type: taskType,
      routing_id: routingId,
      attempts: [{ attempt_number: 1, provider_id: "openai", model_id: selected.model_id, status: "FAILED", error_code: message }],
      decision_reasons: [`Request to OpenAI failed: ${message}`],
    });
  }
}
