"use client";

import { MaterialIcon } from "@/components/ui/material-icon";

interface FileExplorerProps {
  activeFile: string;
  onSelectFile: (file: string) => void;
}

const FILES = {
  src: {
    expanded: true,
    items: [
      { key: "lora", name: "lora_kernel.cu", icon: "memory", iconColor: "text-emerald-400", status: "M", statusColor: "text-dusk-peach" },
      { key: "infer", name: "infer_engine.rs", icon: "construction", iconColor: "text-orange-400", status: "A", statusColor: "text-emerald-400" },
      { key: "quant", name: "quant_awq.py", icon: "terminal", iconColor: "text-sky-400", status: "4.2k", statusColor: "text-text-muted/60" },
    ],
  },
  configs: {
    expanded: true,
    items: [
      { key: "policy", name: "airgap_policy.yaml", icon: "shield_lock", iconColor: "text-dusk-crimson", status: "M", statusColor: "text-dusk-crimson" },
      { key: "weights", name: "model_weights.json", icon: "data_object", iconColor: "text-amber-400", status: "U", statusColor: "text-text-muted/50" },
    ],
  },
  benchmarks: {
    expanded: false,
    items: [],
  },
};

export function FileExplorer({ activeFile, onSelectFile }: FileExplorerProps) {
  return (
    <aside className="w-64 md:w-72 bg-dusk-navy/95 backdrop-blur-2xl border-r border-dusk-card-border/80 flex flex-col h-full z-20 flex-shrink-0 select-none">
      {/* Title bar */}
      <div className="h-10 px-3.5 border-b border-dusk-card-border/70 flex items-center justify-between">
        <span className="font-mono text-[11px] font-bold uppercase tracking-wider text-text-muted flex items-center gap-1.5">
          <MaterialIcon name="folder_copy" className="text-sm text-dusk-peach" />
          Explorer
        </span>
        <div className="flex items-center gap-1 text-text-muted">
          <button className="p-1 hover:text-dusk-peach hover:bg-white/[0.04] rounded transition-colors" title="New Kernel File">
            <MaterialIcon name="note_add" className="text-[15px]" />
          </button>
          <button className="p-1 hover:text-dusk-peach hover:bg-white/[0.04] rounded transition-colors" title="New Directory">
            <MaterialIcon name="create_new_folder" className="text-[15px]" />
          </button>
          <button className="p-1 hover:text-dusk-peach hover:bg-white/[0.04] rounded transition-colors" title="Refresh Tree">
            <MaterialIcon name="refresh" className="text-[15px]" />
          </button>
          <button className="p-1 hover:text-dusk-peach hover:bg-white/[0.04] rounded transition-colors" title="Collapse All">
            <MaterialIcon name="unfold_less" className="text-[15px]" />
          </button>
        </div>
      </div>

      {/* Project header */}
      <div className="px-3 py-2 bg-[#1c253b]/60 border-b border-dusk-card-border/40 flex items-center justify-between">
        <div className="flex items-center gap-1.5 text-xs font-mono font-semibold text-text-main truncate">
          <MaterialIcon name="keyboard_arrow_down" className="text-sm text-dusk-peach" />
          <span className="truncate">modelforge-airgap-pipeline</span>
        </div>
        <span className="text-[9px] font-mono text-dusk-peach bg-dusk-peach/10 border border-dusk-peach/30 px-1.5 py-0.5 rounded">
          Enclave
        </span>
      </div>

      {/* File tree */}
      <div className="flex-1 overflow-y-auto py-2 text-xs font-mono space-y-0.5">
        {Object.entries(FILES).map(([folder, data]) => (
          <div key={folder} className={folder === "configs" || folder === "benchmarks" ? "pt-1" : ""}>
            <div className="flex items-center justify-between px-3 py-1 text-text-muted hover:text-text-main hover:bg-dusk-card/40 cursor-pointer group">
              <div className="flex items-center gap-1.5">
                <MaterialIcon
                  name={data.expanded ? "keyboard_arrow_down" : "chevron_right"}
                  className="text-sm"
                />
                <MaterialIcon name="folder" className="text-sm text-amber-300" />
                <span className="font-medium text-text-secondary">{folder}</span>
              </div>
              {data.items.length > 0 && (
                <span className="text-[10px] text-text-muted group-hover:text-dusk-peach">
                  {data.items.length} files
                </span>
              )}
            </div>
            {data.expanded && (
              <div className="pl-6 space-y-0.5">
                {data.items.map((file) => {
                  const isActive = activeFile === file.key;
                  return (
                    <div
                      key={file.key}
                      onClick={() => onSelectFile(file.key)}
                      className={`flex items-center justify-between pr-3 pl-2 py-1.5 rounded-lg cursor-pointer transition-colors ${
                        isActive
                          ? "bg-dusk-plum/30 border-l-2 border-dusk-peach text-text-main hover:bg-dusk-plum/40"
                          : "text-text-muted hover:text-text-main hover:bg-dusk-card/40"
                      }`}
                    >
                      <div className="flex items-center gap-2 truncate">
                        <MaterialIcon name={file.icon} className={`text-[15px] ${file.iconColor}`} />
                        <span className={`truncate ${isActive ? "font-semibold text-dusk-peach" : ""}`}>
                          {file.name}
                        </span>
                      </div>
                      <div className="flex items-center gap-1.5">
                        {isActive && (
                          <span className="w-1.5 h-1.5 rounded-full bg-dusk-peach shadow-[0_0_6px_#FFA586]" />
                        )}
                        <span className={`text-[10px] font-bold font-mono ${file.statusColor}`}>
                          {file.status}
                        </span>
                      </div>
                    </div>
                  );
                })}
              </div>
            )}
          </div>
        ))}

        {/* PR Review Box */}
        <div className="mt-4 mx-2.5 p-3 rounded-xl bg-dusk-card/70 border border-dusk-card-border/90">
          <div className="flex items-center justify-between mb-2">
            <span className="font-mono text-[10px] uppercase font-bold text-dusk-peach tracking-wider flex items-center gap-1">
              <MaterialIcon name="rule" className="text-xs" />
              Staged PR Review
            </span>
            <span className="text-[9px] font-mono bg-dusk-crimson/80 text-white px-1.5 py-0.2 rounded font-semibold">
              AIR-VERIFIED
            </span>
          </div>
          <p className="text-[11px] text-text-secondary mb-2 font-mono">
            Branch: <span className="text-text-main font-semibold">feature/fp8-airgap</span>
          </p>
          <div className="text-[10px] text-text-muted space-y-1">
            <div className="flex items-center justify-between">
              <span>Lines Changed:</span>
              <span className="text-emerald-400 font-mono">
                +142 <span className="text-dusk-crimson">-18</span>
              </span>
            </div>
            <div className="flex items-center justify-between">
              <span>Security Sign-off:</span>
              <span className="text-dusk-peach font-mono">Hardware Enclave</span>
            </div>
          </div>
        </div>
      </div>

      {/* Sidebar bottom */}
      <div className="p-2.5 border-t border-dusk-card-border/70 bg-[#121927]/60 text-[11px] font-mono text-text-muted flex items-center justify-between">
        <span className="flex items-center gap-1.5">
          <span className="w-2 h-2 rounded-full bg-emerald-400 shadow-[0_0_6px_rgba(52,211,153,0.6)]" />
          CUDA 12.4 Enclave
        </span>
        <span className="text-dusk-peach cursor-pointer hover:underline">vLLM daemon</span>
      </div>
    </aside>
  );
}
