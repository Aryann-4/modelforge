"use client";

import { useState } from "react";
import { MaterialIcon } from "@/components/ui/material-icon";

const SCENARIOS = [
  {
    icon: "build_circle",
    title: "Defect Inspection Log",
    tag: "Active",
    tagColor: "bg-dusk-peach/15 text-dusk-peach border-dusk-peach/40",
    description: "Multi-modal defect segmentation and ISO quality control report synthesis.",
    active: true,
  },
  {
    icon: "code_blocks",
    title: "Sandbox Code Task",
    tag: "Qwen2.5",
    tagColor: "",
    description: "High-concurrency Rust kernel optimization & zero-dependency parser.",
  },
  {
    icon: "draw",
    title: "CAD / Drawing Analysis",
    tag: "Vision",
    tagColor: "",
    description: "P&ID schematics extraction to structured JSON schema specification.",
  },
  {
    icon: "policy",
    title: "Regulatory Policy Compliance",
    tag: "RAG",
    tagColor: "",
    description: "Air-gapped verification against classified standard operating protocols.",
  },
];

export function ScenarioSidebar({ onNewSession }: { onNewSession?: () => void }) {
  const [temp, setTemp] = useState(35);

  return (
    <aside className="w-full md:w-72 lg:w-80 bg-dusk-navy/85 backdrop-blur-2xl border-r border-dusk-card-border/80 flex flex-col h-full z-20 flex-shrink-0">
      <div className="p-4 border-b border-dusk-card-border/80">
        <div className="flex items-center justify-between mb-3">
          <span className="font-mono text-xs text-dusk-peach font-semibold uppercase tracking-wider flex items-center gap-1.5">
            <MaterialIcon name="psychology" className="text-sm" />
            Scenario Sandbox
          </span>
          <span className="text-[10px] font-mono text-white bg-dusk-crimson/80 px-1.5 py-0.5 rounded">
            AIR-GAPPED
          </span>
        </div>
        <button
          onClick={onNewSession}
          className="w-full bg-dusk-peach hover:bg-[#ffb59c] text-dusk-navy font-bold py-2.5 px-4 rounded-xl hover:shadow-[0_0_22px_rgba(255,165,134,0.4)] transition-all transform active:scale-[0.98] text-xs font-mono tracking-wider flex items-center justify-center gap-2 cursor-pointer"
        >
          <MaterialIcon name="add" className="text-base font-bold" />
          New Session Run
        </button>
      </div>

      <div className="p-3 flex-1 overflow-y-auto space-y-2">
        <div className="text-[11px] font-mono uppercase text-text-muted px-2 py-1 tracking-wider">
          Fast Presets
        </div>

        {SCENARIOS.map((s, i) => (
          <button
            key={i}
            className={`w-full text-left p-3 rounded-xl border transition-all group cursor-pointer ${
              s.active
                ? "bg-dusk-plum/30 border-dusk-peach/40 hover:border-dusk-peach"
                : "bg-dusk-card/40 border-dusk-card-border hover:border-dusk-peach/40"
            }`}
          >
            <div className="flex items-center justify-between mb-1">
              <div
                className={`flex items-center gap-2 font-medium text-xs transition-colors ${
                  s.active
                    ? "text-text-main group-hover:text-dusk-peach"
                    : "text-text-main group-hover:text-dusk-peach"
                }`}
              >
                <MaterialIcon
                  name={s.icon}
                  className={`text-sm ${s.active ? "text-dusk-peach" : "text-text-muted group-hover:text-dusk-peach"}`}
                />
                {s.title}
              </div>
              <span
                className={`text-[9px] font-mono px-1.5 py-0.5 rounded ${
                  s.active
                    ? "text-dusk-peach bg-dusk-peach/15"
                    : "text-text-muted"
                }`}
              >
                {s.tag}
              </span>
            </div>
            <p className="text-[11px] text-text-muted line-clamp-2">{s.description}</p>
          </button>
        ))}

        {/* Generation Controls */}
        <div className="pt-3 border-t border-dusk-card-border/60 mt-3 px-1">
          <div className="text-[11px] font-mono uppercase text-text-muted mb-2 tracking-wider flex items-center justify-between">
            <span>Runtime Control</span>
            <span className="text-dusk-peach font-bold">Local Host</span>
          </div>
          <div className="space-y-2.5 text-xs font-mono">
            <div>
              <div className="flex justify-between text-[11px] text-text-muted mb-1">
                <span>Creativity (Temp)</span>
                <span className="text-dusk-peach">{(temp / 100).toFixed(2)}</span>
              </div>
              <input
                type="range"
                min="0"
                max="100"
                value={temp}
                onChange={(e) => setTemp(Number(e.target.value))}
                className="w-full h-1 bg-[#101726] rounded-lg appearance-none cursor-pointer accent-dusk-peach"
              />
            </div>
            <div>
              <div className="flex justify-between text-[11px] text-text-muted mb-1">
                <span>Max Generation Tokens</span>
                <span className="text-text-main">4,096</span>
              </div>
              <div className="grid grid-cols-3 gap-1.5">
                <button className="py-1 text-[10px] rounded bg-dusk-card/80 border border-dusk-card-border hover:border-dusk-peach text-text-muted hover:text-text-main">
                  1k
                </button>
                <button className="py-1 text-[10px] rounded bg-dusk-plum/40 border border-dusk-peach/40 text-dusk-peach font-bold">
                  4k
                </button>
                <button className="py-1 text-[10px] rounded bg-dusk-card/80 border border-dusk-card-border hover:border-dusk-peach text-text-muted hover:text-text-main">
                  8k
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Footer */}
      <div className="p-3 border-t border-dusk-card-border/80 text-[11px] font-mono text-text-muted flex items-center justify-between">
        <span className="flex items-center gap-1.5">
          <span className="w-2 h-2 rounded-full bg-emerald-400" /> 3 Local Models Hot
        </span>
        <span className="text-dusk-peach hover:underline cursor-pointer">Logs</span>
      </div>
    </aside>
  );
}
