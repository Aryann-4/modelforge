"use client";

import { useState } from "react";
import { MaterialIcon } from "@/components/ui/material-icon";

const BOTTOM_TABS = [
  { id: "review", icon: "rate_review", label: "Review Notes" },
  { id: "term", icon: "terminal", label: "Terminal" },
  { id: "output", icon: "data_array", label: "Model Output" },
  { id: "linter", icon: "warning", label: "Diagnostics (0 errors, 1 warning)", iconColor: "text-amber-400" },
];

const TERMINAL_LINES = [
  {
    type: "command",
    text: "nvcc -O3 -arch=sm_89 --use_fast_math -c src/lora_kernel.cu -o build/lora_kernel.o",
  },
  {
    type: "output",
    text: "[NVCC] Compiled 1,280 PTX instructions. Register pressure: 38 registers/thread. Shared memory: 4,096 bytes.",
  },
  {
    type: "success",
    text: "Compilation successful -> build/lora_kernel.o (Execution latency: 0.84ms, zero egress drop confirmed).",
  },
];

export function TerminalPanel() {
  const [activeTab, setActiveTab] = useState("term");

  return (
    <div className="h-44 bg-[#141b2c]/95 border-t border-dusk-card-border/80 flex flex-col flex-shrink-0">
      {/* Tab bar */}
      <div className="h-8 px-3 bg-[#101726] border-b border-dusk-card-border/60 flex items-center justify-between text-xs font-mono select-none">
        <div className="flex items-center gap-4 h-full">
          {BOTTOM_TABS.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`h-full flex items-center gap-1.5 transition-colors ${
                activeTab === tab.id
                  ? "text-dusk-peach border-b-2 border-dusk-peach font-semibold"
                  : "text-text-muted hover:text-text-main border-b-2 border-transparent"
              }`}
            >
              <MaterialIcon name={tab.icon} className={`text-sm ${tab.iconColor || ""}`} />
              <span>{tab.label}</span>
            </button>
          ))}
        </div>
        <div className="flex items-center gap-2 text-text-muted">
          <button className="hover:text-dusk-peach" title="Clear Console">
            <MaterialIcon name="block" className="text-sm" />
          </button>
          <button className="hover:text-dusk-peach" title="Maximize Panel">
            <MaterialIcon name="expand_less" className="text-sm" />
          </button>
          <button className="hover:text-dusk-peach" title="Close Panel">
            <MaterialIcon name="close" className="text-sm" />
          </button>
        </div>
      </div>

      {/* Terminal output */}
      <div className="flex-1 p-3 overflow-y-auto font-mono text-[11px] space-y-1 bg-[#0d1322]">
        {TERMINAL_LINES.map((line, i) => (
          <div key={i} className={line.type === "command" ? "text-text-muted flex items-center gap-2" : line.type === "success" ? "text-emerald-400 pl-4 font-semibold flex items-center gap-2" : "text-text-secondary pl-4"}>
            {line.type === "command" && (
              <span className="text-emerald-400 font-bold">modelforge-node@ada-6000:~/pipeline$</span>
            )}
            {line.type === "success" && (
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 shadow-[0_0_6px_#34D399]" />
            )}
            <span>{line.text}</span>
          </div>
        ))}
        <div className="text-text-muted flex items-center gap-2 pt-1">
          <span className="text-emerald-400 font-bold">modelforge-node@ada-6000:~/pipeline$</span>
          <span className="animate-pulse inline-block w-2 h-3.5 bg-dusk-peach" />
        </div>
      </div>
    </div>
  );
}
