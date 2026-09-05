import { NextResponse } from "next/server";

export const dynamic = "force-dynamic";

export async function GET() {
  return NextResponse.json({
    provider_count: 3,
    enabled_provider_count: 3,
    model_count: 5,
    enabled_model_count: 5,
    resource_snapshot: {
      cpu_count: 2,
      cpu_utilization_pct: 15.0,
      ram_total_gb: 8.0,
      ram_available_gb: 6.0,
      vram_total_gb: 0.0,
      vram_available_gb: 0.0,
      gpu_available: false,
      active_workloads: 0,
      source: "simulated",
      taken_at: new Date().toISOString(),
    },
  });
}
