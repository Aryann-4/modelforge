import { NextResponse } from "next/server";

export async function GET() {
  return NextResponse.json([
    {
      model_id: "mock-cloud-large",
      provider_id: "mock-cloud",
      display_name: "Mock Cloud Large",
      enabled: true,
      context_window: 128000,
      capabilities: ["REASONING", "CODING", "LONG_CONTEXT", "STRUCTURED_OUTPUT"],
    },
    {
      model_id: "mock-cloud-vision",
      provider_id: "mock-cloud",
      display_name: "Mock Cloud Vision",
      enabled: true,
      context_window: 64000,
      capabilities: ["VISION", "REASONING"],
    },
    {
      model_id: "mock-local-small",
      provider_id: "mock-local",
      display_name: "Mock Local Small",
      enabled: true,
      context_window: 32000,
      capabilities: ["CODING", "REASONING"],
    },
    {
      model_id: "mock-local-large",
      provider_id: "mock-local",
      display_name: "Mock Local Large",
      enabled: true,
      context_window: 100000,
      capabilities: ["CODING", "REASONING", "LONG_CONTEXT"],
    },
    {
      model_id: "mock-flaky-model",
      provider_id: "mock-flaky",
      display_name: "Mock Flaky Model",
      enabled: true,
      context_window: 16000,
      capabilities: ["CODING"],
    },
  ]);
}
