import { NextResponse } from "next/server";

export async function GET() {
  return NextResponse.json([
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
  ]);
}
