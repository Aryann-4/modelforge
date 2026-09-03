"use client";

import { MaterialIcon } from "@/components/ui/material-icon";

export function StatusBar() {
  return (
    <footer className="h-6.5 bg-[#0e1424] border-t border-dusk-card-border/80 px-3 flex items-center justify-between text-[11px] font-mono select-none z-30 flex-shrink-0 text-text-muted">
      <div className="flex items-center gap-3">
        <a className="flex items-center gap-1 text-dusk-peach hover:text-white transition-colors" href="#">
          <MaterialIcon name="fork_right" className="text-[14px]" />
          <span>feature/fp8-airgap*</span>
        </a>
        <div className="flex items-center gap-1 text-text-muted">
          <MaterialIcon name="sync_alt" className="text-[13px]" />
          <span>0↓ 2↑</span>
        </div>
        <div className="flex items-center gap-1.5 text-emerald-400 bg-emerald-950/40 px-2 py-0.2 rounded border border-emerald-800/40">
          <MaterialIcon name="lock" className="text-[13px]" />
          <span>Air-Gapped (Enclave Locked)</span>
        </div>
        <div className="hidden sm:flex items-center gap-2">
          <span className="flex items-center gap-0.5 text-text-muted">
            <MaterialIcon name="cancel" className="text-[13px]" /> 0
          </span>
          <span className="flex items-center gap-0.5 text-amber-400">
            <MaterialIcon name="warning" className="text-[13px]" /> 1
          </span>
        </div>
      </div>
      <div className="flex items-center gap-4">
        <span className="hidden md:inline">Ln 42, Col 18</span>
        <span className="hidden md:inline">Spaces: 4</span>
        <span>UTF-8</span>
        <span className="text-text-secondary flex items-center gap-1">
          <MaterialIcon name="code" className="text-[13px] text-emerald-400" />
          CUDA C++
        </span>
        <span className="text-dusk-peach bg-dusk-peach/10 px-1.5 py-0.2 rounded border border-dusk-peach/20">
          RTX 6000 Ada
        </span>
      </div>
    </footer>
  );
}
