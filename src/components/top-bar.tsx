"use client";

interface TopBarProps {
  gpuUsage: string;
  vramUsage: string;
}

export function TopBar({ gpuUsage, vramUsage }: TopBarProps) {
  return (
    <header className="h-[52px] bg-[#13161c] border-b border-[#2a3140] flex items-center px-4 gap-4 shrink-0 z-50">
      <div className="flex items-center gap-2.5 font-bold text-[15px] tracking-tight">
        <div className="w-7 h-7 bg-gradient-to-br from-[#3b82f6] to-[#8b5cf6] rounded-[7px] grid place-items-center text-sm">
          ⬡
        </div>
        ModelForge
      </div>
      <div className="flex items-center gap-2 bg-[rgba(34,197,94,0.12)] border border-[rgba(34,197,94,0.35)] text-[#22c55e] text-[11px] font-semibold px-3 py-[5px] rounded-full tracking-wide uppercase">
        <div className="w-[7px] h-[7px] bg-[#22c55e] rounded-full animate-pulse-glow" />
        Air-Gapped · Zero External Calls
      </div>
      <div className="ml-auto flex items-center gap-3">
        <div className="flex gap-3.5 font-mono text-[11px] text-[#9aa3b2]">
          <div>
            <span className="text-[#6b7385]">GPU </span>
            <strong className="text-[#22d3ee] font-medium">{gpuUsage}</strong>
          </div>
          <div>
            <span className="text-[#6b7385]">VRAM </span>
            <strong className="text-[#22d3ee] font-medium">{vramUsage}</strong>
          </div>
          <div>
            <span className="text-[#6b7385]">Models </span>
            <strong className="text-[#22d3ee] font-medium">3 loaded</strong>
          </div>
        </div>
      </div>
    </header>
  );
}
