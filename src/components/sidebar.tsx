"use client";

import type { ModelInfo } from "@/hooks/use-modelforge";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";

interface SidebarProps {
  activeModel: string | null;
  models: Record<string, ModelInfo>;
  onRunDemo: (type: "inspection" | "coding" | "handoff" | "multimodal") => void;
  isRunning: boolean;
}

const DEMOS = [
  { type: "inspection" as const, icon: "📄", label: "Scanned Inspection → Approval Note" },
  { type: "coding" as const, icon: "💻", label: "Code Task + Sandbox Verify" },
  { type: "handoff" as const, icon: "🔄", label: "Long Context → Model Switch" },
  { type: "multimodal" as const, icon: "🖼️", label: "Engineering Drawing Analysis" },
];

const MODEL_KEYS = ["coder", "reason", "vision"] as const;

export function Sidebar({ activeModel, models, onRunDemo, isRunning }: SidebarProps) {
  return (
    <aside className="w-full h-full bg-[#13161c] border-r border-[#2a3140] flex flex-col overflow-hidden">
      <div className="px-3 pt-3.5 pb-2 text-[10px] font-semibold uppercase tracking-[0.08em] text-[#6b7385]">
        Model Pool
      </div>
      {MODEL_KEYS.map((key) => {
        const m = models[key];
        const isActive = activeModel === key;
        const isSwitching = m.status === "switching";
        const pct = m.ctx;
        return (
          <div
            key={key}
            className={cn(
              "mx-2.5 my-1 px-3 py-2.5 rounded-lg border transition-all duration-200",
              isActive
                ? "border-[#3b82f6] bg-[rgba(59,130,246,0.15)] shadow-[0_0_0_1px_var(--primary)]"
                : isSwitching
                ? "border-[#f59e0b] bg-[rgba(245,158,11,0.12)] animate-switch-flash"
                : "border-[#222833] bg-[#181c24]"
            )}
          >
            <div className="flex items-center justify-between text-[13px] font-semibold">
              <span>{m.name}</span>
              <span className="text-[10px] font-medium px-1.5 py-[2px] rounded bg-[#1e2430] text-[#9aa3b2]">
                {m.tag}
              </span>
            </div>
            <div className="text-[11px] text-[#6b7385] mt-1 font-mono">
              {m.max}K ctx · {pct}% used
            </div>
            <div className="h-[3px] mt-2 bg-[#2a3140] rounded-full overflow-hidden">
              <div
                className={cn(
                  "h-full rounded-full transition-all duration-400",
                  pct > 85 ? "bg-[#ef4444]" : pct > 60 ? "bg-[#f59e0b]" : "bg-[#3b82f6]"
                )}
                style={{ width: `${pct}%` }}
              />
            </div>
          </div>
        );
      })}

      <div className="px-3 pt-5 pb-2 text-[10px] font-semibold uppercase tracking-[0.08em] text-[#6b7385]">
        Demo Scenarios
      </div>
      {DEMOS.map((d) => (
        <Button
          key={d.type}
          variant="ghost"
          className="mx-2.5 my-1 h-auto justify-start gap-2 text-[12px] font-medium text-[#e8eaed] hover:bg-[#1e2430] hover:border-[#3b82f6] border border-[#2a3140] bg-[#181c24] rounded-lg px-3 py-2.5"
          onClick={() => onRunDemo(d.type)}
          disabled={isRunning}
        >
          <span className="text-base">{d.icon}</span>
          <span className="truncate">{d.label}</span>
        </Button>
      ))}

      <div className="flex-1" />
      <div className="p-3 border-t border-[#2a3140] text-[11px] text-[#6b7385] text-center">
        SIH26117 · MRPL
        <br />
        <span className="text-[#22c55e]">● Local Ollama/vLLM</span>
      </div>
    </aside>
  );
}
