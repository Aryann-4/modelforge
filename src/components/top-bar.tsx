"use client";

interface TopBarProps {
  gpuUsage: string;
  vramUsage: string;
  onToggleSidebar: () => void;
  onTogglePanel: () => void;
}

export function TopBar({ gpuUsage, vramUsage, onToggleSidebar, onTogglePanel }: TopBarProps) {
  return (
    <header className="h-[52px] bg-[#13161c] border-b border-[#2a3140] flex items-center px-3 sm:px-4 gap-2 sm:gap-4 shrink-0 z-30">
      {/* Mobile hamburger */}
      <button
        onClick={onToggleSidebar}
        className="lg:hidden w-8 h-8 grid place-items-center rounded-lg border border-[#2a3140] bg-[#181c24] text-[#9aa3b2] hover:text-[#e8eaed] hover:border-[#3b82f6] transition-colors shrink-0"
        aria-label="Toggle sidebar"
      >
        <svg width="16" height="16" viewBox="0 0 16 16" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round">
          <line x1="2" y1="4" x2="14" y2="4" />
          <line x1="2" y1="8" x2="14" y2="8" />
          <line x1="2" y1="12" x2="14" y2="12" />
        </svg>
      </button>

      <div className="flex items-center gap-2.5 font-bold text-[15px] tracking-tight">
        <div className="w-7 h-7 bg-gradient-to-br from-[#3b82f6] to-[#8b5cf6] rounded-[7px] grid place-items-center text-sm">
          ⬡
        </div>
        <span className="hidden sm:inline">ModelForge</span>
      </div>

      <div className="hidden sm:flex items-center gap-2 bg-[rgba(34,197,94,0.12)] border border-[rgba(34,197,94,0.35)] text-[#22c55e] text-[11px] font-semibold px-3 py-[5px] rounded-full tracking-wide uppercase">
        <div className="w-[7px] h-[7px] bg-[#22c55e] rounded-full animate-pulse-glow" />
        Air-Gapped · Zero External Calls
      </div>

      {/* Mobile sovereignty dot */}
      <div className="sm:hidden flex items-center gap-1.5">
        <div className="w-[7px] h-[7px] bg-[#22c55e] rounded-full animate-pulse-glow" />
        <span className="text-[#22c55e] text-[10px] font-semibold uppercase">Sovereign</span>
      </div>

      <div className="ml-auto flex items-center gap-2 sm:gap-3">
        {/* HW stats — hidden on very small screens, shown on sm+ */}
        <div className="hidden sm:flex gap-3.5 font-mono text-[11px] text-[#9aa3b2]">
          <div>
            <span className="text-[#6b7385]">GPU </span>
            <strong className="text-[#22d3ee] font-medium">{gpuUsage}</strong>
          </div>
          <div className="hidden md:block">
            <span className="text-[#6b7385]">VRAM </span>
            <strong className="text-[#22d3ee] font-medium">{vramUsage}</strong>
          </div>
          <div className="hidden md:block">
            <span className="text-[#6b7385]">Models </span>
            <strong className="text-[#22d3ee] font-medium">3 loaded</strong>
          </div>
        </div>

        {/* Mobile panel toggle */}
        <button
          onClick={onTogglePanel}
          className="xl:hidden w-8 h-8 grid place-items-center rounded-lg border border-[#2a3140] bg-[#181c24] text-[#9aa3b2] hover:text-[#e8eaed] hover:border-[#3b82f6] transition-colors shrink-0"
          aria-label="Toggle panel"
        >
          <svg width="16" height="16" viewBox="0 0 16 16" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round">
            <rect x="1" y="2" width="14" height="12" rx="2" />
            <line x1="10" y1="2" x2="10" y2="14" />
          </svg>
        </button>
      </div>
    </header>
  );
}
